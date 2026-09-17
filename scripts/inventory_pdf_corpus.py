from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import unicodedata
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pdfplumber


DEFAULT_OUTPUT_DIR = Path("outputs/audit")
DEFAULT_PDF_ROOT = Path(r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS")


def strip_accents(value: str) -> str:
  return "".join(
    char for char in unicodedata.normalize("NFD", value)
    if unicodedata.category(char) != "Mn"
  )


def collapse_spaces(value: str) -> str:
  return re.sub(r"\s+", " ", value).strip()


def compact_key(value: str) -> str:
  value = strip_accents(value).upper()
  value = re.sub(r"\d+", "", value)
  value = re.sub(r"[^A-Z]+", " ", value)
  return collapse_spaces(value)


def normalize_for_marker(value: str) -> str:
  value = strip_accents(value).upper()
  value = value.replace("º", "O").replace("°", "O")
  value = re.sub(r"\s+", " ", value)
  return value.strip()


def relative_path(path: Path, root: Path) -> str:
  try:
    return str(path.relative_to(root))
  except ValueError:
    return str(path)


def identify_institution(path: Path, root: Path) -> str | None:
  rel = path.relative_to(root) if path.is_relative_to(root) else path
  if rel.parts:
    first = rel.parts[0]
    if first and first != path.name:
      return first
  match = re.match(r"([A-Za-z]+)", path.stem)
  return match.group(1) if match else None


def identify_year(path: Path) -> int | None:
  text = str(path)
  matches = re.findall(r"(?:19|20)\d{2}", text)
  if not matches:
    return None
  years = [int(item) for item in matches]
  preferred = [year for year in years if 1990 <= year <= 2035]
  return preferred[0] if preferred else years[0]


def identify_series(path: Path) -> str | None:
  text = strip_accents(str(path)).upper()
  match = re.search(r"(\d+)\s*(?:O|º|°)?\s*ANO", text)
  if match:
    return f"{match.group(1)}º Ano"
  match = re.search(r"(\d+)\s*(?:A|ª)?\s*SERIE", text)
  if match:
    return f"{match.group(1)}ª Série"
  return None


def text_lines(page: pdfplumber.page.Page) -> list[str]:
  words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=False) or []
  grouped: list[tuple[float, list[dict[str, Any]]]] = []
  for word in words:
    top = float(word.get("top", 0))
    for index, (group_top, items) in enumerate(grouped):
      if abs(group_top - top) <= 3:
        items.append(word)
        break
    else:
      grouped.append((top, [word]))
  lines: list[str] = []
  for _, items in sorted(grouped, key=lambda item: item[0]):
    items.sort(key=lambda item: float(item.get("x0", 0)))
    line = collapse_spaces(" ".join(str(item.get("text", "")) for item in items))
    if line:
      lines.append(line)
  return lines


def marker_patterns(lines: list[str]) -> Counter[str]:
  patterns: Counter[str] = Counter()
  for line in lines:
    normalized = normalize_for_marker(line)
    compact = re.sub(r"[^A-Z0-9]+", "", normalized)
    if re.search(r"\bQUESTAO\s*\d{1,3}\b", normalized) or re.search(r"\bQ\s*UESTAO\s*\d{1,3}\b", normalized) or re.search(r"QUESTAO\d{1,3}", compact):
      patterns["questao"] += 1
    elif re.match(r"^\s*\d{1,2}\s*[.)]\s+\S+", line):
      patterns["numeric-dot"] += 1
    elif re.match(r"^\s*\d{1,2}\s*[-–—]\s+\S+", line):
      patterns["numeric-dash"] += 1
  return patterns


def subject_flags(text_sample: str) -> dict[str, bool]:
  normalized = strip_accents(text_sample).upper()
  return {
    "matematica": "MATEMATICA" in normalized,
    "portugues": "PORTUGUES" in normalized or "LINGUA PORTUGUESA" in normalized,
    "redacao": "REDACAO" in normalized,
    "prova_objetiva": "PROVA OBJETIVA" in normalized,
  }


def recurring_headers_footers(page_line_samples: list[tuple[int, list[str]]], page_count: int) -> dict[str, Any]:
  counts: Counter[str] = Counter()
  samples: dict[str, str] = {}
  for _, lines in page_line_samples:
    candidates = lines[:3] + lines[-3:]
    for line in candidates:
      key = compact_key(line)
      if len(key) < 6:
        continue
      counts[key] += 1
      samples.setdefault(key, line)
  threshold = max(2, int(page_count * 0.25))
  recurring = [
    {"sample": samples[key], "count": count}
    for key, count in counts.most_common()
    if count >= threshold
  ][:12]
  return {"count": len(recurring), "items": recurring}


def classify_document(
  page_count: int,
  char_counts: list[int],
  image_counts: list[int],
  page_areas: list[float],
) -> str:
  if page_count <= 0:
    return "unknown"
  average = statistics.mean(char_counts) if char_counts else 0
  median = statistics.median(char_counts) if char_counts else 0
  no_text_pages = sum(1 for count in char_counts if count < 20)
  no_text_ratio = no_text_pages / page_count
  image_pages = sum(1 for count in image_counts if count > 0)
  image_ratio = image_pages / page_count

  if no_text_ratio >= 0.8 and average < 50 and image_ratio >= 0.5:
    return "raster"
  if average >= 800 and median >= 500 and no_text_ratio <= 0.1:
    return "text_native"
  if no_text_ratio >= 0.2 and average >= 100:
    return "hybrid"
  if average < 500 or median < 250:
    return "text_low_quality"
  if image_ratio >= 0.35 and no_text_ratio >= 0.1:
    return "hybrid"
  if average >= 500:
    return "text_native"
  return "text_low_quality"


def inspect_pdf(path: Path, root: Path) -> dict[str, Any]:
  result: dict[str, Any] = {
    "path": str(path),
    "relativePath": relative_path(path, root),
    "institution": identify_institution(path, root),
    "year": identify_year(path),
    "series": identify_series(path),
    "pageCount": 0,
    "averageCharsPerPage": 0,
    "medianCharsPerPage": 0,
    "pagesWithoutText": 0,
    "pagesWithoutTextRatio": 0,
    "imagePages": 0,
    "imagePageRatio": 0,
    "dominantImages": False,
    "classification": "unknown",
    "questionMarkerPatterns": {},
    "approxQuestionMarkers": 0,
    "hasQuestao": False,
    "hasSpacedQuestao": False,
    "hasNumericMarkers": False,
    "combinedDocumentSignals": {},
    "likelyCombinedDocument": "unknown",
    "recurringHeadersFooters": {"count": 0, "items": []},
    "questionsPerPagePattern": "unknown",
    "apparentTablesOrImages": "unknown",
    "error": None,
  }
  try:
    with pdfplumber.open(str(path)) as pdf:
      page_count = len(pdf.pages)
      char_counts: list[int] = []
      image_counts: list[int] = []
      page_areas: list[float] = []
      all_marker_patterns: Counter[str] = Counter()
      lines_for_headers: list[tuple[int, list[str]]] = []
      marker_counts_by_page: list[int] = []
      subject_text_parts: list[str] = []

      for index, page in enumerate(pdf.pages):
        chars = len(getattr(page, "chars", []) or [])
        lines = text_lines(page)
        if chars == 0 and lines:
          chars = len("\n".join(lines))
        images = len(page.images or [])
        page_marker_patterns = marker_patterns(lines)
        all_marker_patterns.update(page_marker_patterns)
        marker_counts_by_page.append(sum(page_marker_patterns.values()))
        char_counts.append(chars)
        image_counts.append(images)
        page_areas.append(float(page.width) * float(page.height))
        lines_for_headers.append((index + 1, lines))
        if index < 5 or index >= max(0, page_count - 3):
          subject_text_parts.extend(lines[:20])

      average = statistics.mean(char_counts) if char_counts else 0
      median = statistics.median(char_counts) if char_counts else 0
      pages_without_text = sum(1 for count in char_counts if count < 20)
      image_pages = sum(1 for count in image_counts if count > 0)
      subject_sample = "\n".join(subject_text_parts)
      subjects = subject_flags(subject_sample)
      combined_score = sum(1 for key in ["matematica", "portugues", "redacao"] if subjects.get(key))
      approx_markers = sum(all_marker_patterns.values())
      nonzero_marker_pages = [count for count in marker_counts_by_page if count > 0]
      if approx_markers == 0:
        qpp = "unknown"
      elif nonzero_marker_pages and max(nonzero_marker_pages) <= 1 and len(nonzero_marker_pages) >= approx_markers * 0.8:
        qpp = "one_question_per_page"
      elif nonzero_marker_pages and statistics.mean(nonzero_marker_pages) > 1.25:
        qpp = "multiple_questions_per_page"
      else:
        qpp = "mixed_or_unknown"

      result.update({
        "pageCount": page_count,
        "averageCharsPerPage": round(average, 2),
        "medianCharsPerPage": round(median, 2),
        "pagesWithoutText": pages_without_text,
        "pagesWithoutTextRatio": round(pages_without_text / page_count, 4) if page_count else 0,
        "imagePages": image_pages,
        "imagePageRatio": round(image_pages / page_count, 4) if page_count else 0,
        "dominantImages": bool(page_count and image_pages / page_count >= 0.5),
        "classification": classify_document(page_count, char_counts, image_counts, page_areas),
        "questionMarkerPatterns": dict(all_marker_patterns),
        "approxQuestionMarkers": approx_markers,
        "hasQuestao": all_marker_patterns["questao"] > 0,
        "hasSpacedQuestao": any("Q UEST" in normalize_for_marker(line) or line.startswith("UEST") for _, lines in lines_for_headers for line in lines),
        "hasNumericMarkers": all_marker_patterns["numeric-dot"] > 0 or all_marker_patterns["numeric-dash"] > 0,
        "combinedDocumentSignals": subjects,
        "likelyCombinedDocument": "yes" if combined_score >= 2 else "no" if combined_score == 1 else "unknown",
        "recurringHeadersFooters": recurring_headers_footers(lines_for_headers, page_count),
        "questionsPerPagePattern": qpp,
        "apparentTablesOrImages": "yes" if image_pages / page_count >= 0.25 else "unknown",
      })
  except Exception as exc:
    result["error"] = f"{type(exc).__name__}: {exc}"
  return result


def inspect_pdf_worker(args: tuple[str, str]) -> dict[str, Any]:
  path_text, root_text = args
  return inspect_pdf(Path(path_text), Path(root_text))


def period_bucket(year: int | None) -> str:
  if year is None:
    return "unknown"
  start = (year // 5) * 5
  return f"{start}-{start + 4}"


def summarize(records: list[dict[str, Any]], root: Path) -> dict[str, Any]:
  total_pages = sum(int(item.get("pageCount") or 0) for item in records)
  by_class = Counter(item.get("classification", "unknown") for item in records)
  by_institution = Counter(item.get("institution") or "unknown" for item in records)
  by_period = Counter(period_bucket(item.get("year")) for item in records)
  marker_patterns: Counter[str] = Counter()
  for item in records:
    marker_patterns.update(item.get("questionMarkerPatterns") or {})
  raster_by_institution = Counter(
    item.get("institution") or "unknown"
    for item in records
    if item.get("classification") == "raster"
  )
  raster_by_year = Counter(
    str(item.get("year") or "unknown")
    for item in records
    if item.get("classification") == "raster"
  )
  audit_without_ocr = sum(1 for item in records if item.get("classification") in {"text_native", "hybrid"})
  needs_ocr = sum(1 for item in records if item.get("classification") == "raster")
  low_quality = sum(1 for item in records if item.get("classification") == "text_low_quality")
  families = Counter()
  for item in records:
    cls = item.get("classification")
    markers = item.get("questionMarkerPatterns") or {}
    if cls == "raster":
      family = "raster_or_scanned"
    elif markers.get("questao"):
      family = "text_with_questao_markers"
    elif markers.get("numeric-dot") or markers.get("numeric-dash"):
      family = "text_with_numeric_markers"
    elif cls in {"text_native", "hybrid", "text_low_quality"}:
      family = "text_without_detected_question_markers"
    else:
      family = "unknown"
    if item.get("likelyCombinedDocument") == "yes":
      family += "_combined"
    families[family] += 1
  controls: dict[str, dict[str, list[dict[str, Any]]]] = {
    "expectedRaster": {},
    "expectedText": {},
  }
  raster_controls = {
    ("CMB", 2016),
    ("CMB", 2024),
    ("CMBel", 2017),
    ("CMBel", 2022),
    ("CMC", 2009),
  }
  text_controls = {
    ("CMB", 2014),
    ("CMB", 2015),
  }
  for item in records:
    key = (item.get("institution"), item.get("year"))
    label = f"{key[0]} {key[1]}"
    rel_upper = str(item.get("relativePath", "")).upper()
    if "GABAR" in rel_upper or item.get("series") != "6º Ano":
      continue
    control_item = {
      "relativePath": item.get("relativePath"),
      "classification": item.get("classification"),
      "averageCharsPerPage": item.get("averageCharsPerPage"),
      "medianCharsPerPage": item.get("medianCharsPerPage"),
      "pagesWithoutTextRatio": item.get("pagesWithoutTextRatio"),
    }
    if key in raster_controls:
      controls["expectedRaster"].setdefault(label, []).append(control_item)
    if key in text_controls:
      controls["expectedText"].setdefault(label, []).append(control_item)

  return {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "pdfRoot": str(root),
    "totalPdfs": len(records),
    "totalPages": total_pages,
    "classificationCounts": dict(by_class),
    "classificationPercentages": {
      key: round(value / len(records) * 100, 2) if records else 0
      for key, value in by_class.items()
    },
    "byInstitution": dict(by_institution.most_common()),
    "byPeriod": dict(sorted(by_period.items())),
    "markerPatterns": dict(marker_patterns.most_common()),
    "rasterByInstitution": dict(raster_by_institution.most_common(20)),
    "rasterByYear": dict(raster_by_year.most_common(20)),
    "estimatedAuditableWithoutOcr": audit_without_ocr,
    "estimatedNeedsOcr": needs_ocr,
    "estimatedTextLowQualityNeedsStructuralWork": low_quality,
    "structuralFamilies": dict(families.most_common()),
    "controls": controls,
  }


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
  fieldnames = [
    "relativePath",
    "institution",
    "year",
    "series",
    "pageCount",
    "averageCharsPerPage",
    "medianCharsPerPage",
    "pagesWithoutText",
    "pagesWithoutTextRatio",
    "imagePages",
    "imagePageRatio",
    "dominantImages",
    "classification",
    "approxQuestionMarkers",
    "questionMarkerPatterns",
    "hasQuestao",
    "hasSpacedQuestao",
    "hasNumericMarkers",
    "likelyCombinedDocument",
    "recurringHeaderFooterCount",
    "questionsPerPagePattern",
    "apparentTablesOrImages",
    "error",
  ]
  with path.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for item in records:
      row = {key: item.get(key) for key in fieldnames}
      row["questionMarkerPatterns"] = json.dumps(item.get("questionMarkerPatterns") or {}, ensure_ascii=False)
      row["recurringHeaderFooterCount"] = (item.get("recurringHeadersFooters") or {}).get("count", 0)
      writer.writerow(row)


def markdown_summary(summary: dict[str, Any]) -> str:
  total = summary["totalPdfs"] or 1
  counts = Counter(summary.get("classificationCounts") or {})
  lines = [
    "# Inventário Estrutural do Acervo PDF",
    "",
    "Modo: somente leitura. Sem OCR, sem auditoria de conteúdo e sem comparação questão a questão.",
    "",
    f"- Total de PDFs: {summary['totalPdfs']}",
    f"- Total de páginas: {summary['totalPages']}",
    f"- `text_native`: {counts.get('text_native', 0)} ({counts.get('text_native', 0) / total:.1%})",
    f"- `raster`: {counts.get('raster', 0)} ({counts.get('raster', 0) / total:.1%})",
    f"- `hybrid`: {counts.get('hybrid', 0)} ({counts.get('hybrid', 0) / total:.1%})",
    f"- `text_low_quality`: {counts.get('text_low_quality', 0)} ({counts.get('text_low_quality', 0) / total:.1%})",
    f"- `unknown`: {counts.get('unknown', 0)}",
    f"- Auditáveis hoje sem OCR (estimativa): {summary['estimatedAuditableWithoutOcr']}",
    f"- Exigiriam camada futura de OCR (estimativa): {summary['estimatedNeedsOcr']}",
    "",
    "## Distribuição Por Instituição",
    "",
  ]
  for key, value in summary["byInstitution"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Distribuição Por Período", ""]
  for key, value in summary["byPeriod"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Padrões De Marcadores", ""]
  for key, value in summary["markerPatterns"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Raster Por Instituição", ""]
  for key, value in summary["rasterByInstitution"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Raster Por Ano", ""]
  for key, value in summary["rasterByYear"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Famílias Estruturais Observáveis", ""]
  for key, value in summary["structuralFamilies"].items():
    lines.append(f"- {key}: {value}")
  lines += ["", "## Controles", ""]
  lines.append(f"- Controles esperados como raster: {summary['controls']['expectedRaster']}")
  lines.append(f"- Controles esperados como textuais: {summary['controls']['expectedText']}")
  lines += [
    "",
    "## Leitura Operacional",
    "",
    "- `raster` indica PDF sem texto extraível suficiente; esta etapa não usa OCR.",
    "- `text_low_quality` indica algum texto extraível, mas abaixo do limiar conservador para auditoria confiável.",
    "- `hybrid` indica mistura mensurável de páginas com e sem texto ou presença forte de imagem junto de texto.",
  ]
  return "\n".join(lines)


def main() -> None:
  parser = argparse.ArgumentParser(description="Inventario estrutural leve do acervo PDF do SimpleQuest.")
  parser.add_argument("--pdf-root", default=os.environ.get("SIMPLEQUEST_PDF_ROOT") or str(DEFAULT_PDF_ROOT))
  parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
  parser.add_argument("--limit", type=int, default=None)
  parser.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 2) - 1)))
  args = parser.parse_args()

  root = Path(args.pdf_root)
  output_dir = Path(args.output_dir)
  output_dir.mkdir(parents=True, exist_ok=True)
  if not root.exists():
    raise SystemExit(f"Raiz de PDFs nao encontrada: {root}")

  pdfs = sorted(path for path in root.rglob("*.pdf") if path.is_file())
  if args.limit:
    pdfs = pdfs[:args.limit]

  records_by_path: dict[str, dict[str, Any]] = {}
  worker_args = [(str(path), str(root)) for path in pdfs]
  with ProcessPoolExecutor(max_workers=max(1, args.workers)) as executor:
    futures = {executor.submit(inspect_pdf_worker, item): item[0] for item in worker_args}
    for index, future in enumerate(as_completed(futures), start=1):
      path_text = futures[future]
      if index == 1 or index % 25 == 0 or index == len(futures):
        print(f"[inventory] {index}/{len(futures)} {relative_path(Path(path_text), root)}", file=sys.stderr)
      records_by_path[path_text] = future.result()
  records = [records_by_path[str(path)] for path in pdfs]
  summary = summarize(records, root)
  payload = {"summary": summary, "pdfs": records}

  json_path = output_dir / "corpus-inventory.json"
  csv_path = output_dir / "corpus-inventory.csv"
  md_path = output_dir / "corpus-inventory-summary.md"
  json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
  write_csv(csv_path, records)
  md_path.write_text(markdown_summary(summary), encoding="utf-8")

  print(json.dumps({
    "json": str(json_path),
    "csv": str(csv_path),
    "markdown": str(md_path),
    "totalPdfs": summary["totalPdfs"],
    "totalPages": summary["totalPages"],
    "classificationCounts": summary["classificationCounts"],
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
