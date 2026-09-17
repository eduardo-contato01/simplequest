from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pdfplumber

from inventory_pdf_corpus import inspect_pdf


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "public" / "data" / "questions.json"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "audit"
LOCAL_CONFIG = ROOT / ".simplequest-audit.local.json"
DEFAULT_D1_DIR = ROOT / ".wrangler" / "state" / "v3" / "d1" / "miniflare-D1DatabaseObject"

QUESTION_RE = re.compile(r"QUEST(?:ÃO|AO)\s*0*(\d{1,3})\s*[.\-–—]?", re.IGNORECASE)
ALT_RE = re.compile(r"(?m)^\s*(?:([A-E])\s*(?:\(\s*\)|[).:\-–—])|\(\s*([A-E])\s*\))\s*(.+?)(?=\n\s*(?:[A-E]\s*(?:\(\s*\)|[).:\-–—])|\(\s*[A-E]\s*\))|\Z)", re.DOTALL)
NUMBER_RE = re.compile(r"\b\d+(?:[ .]\d{3})+(?:,\d+)?\b|\b\d+(?:,\d+)?\b")
ENUMERATION_RE = re.compile(r"\b(?:(?:I|II|III|IV|V|VI|VII|VIII|IX|X)|\d+[ªº])\s*[.)-]", re.IGNORECASE)
PUNCTUATION = ".,:;!?()[]{}"
SUPERSCRIPT_DIGITS = {
  "0": "⁰",
  "1": "¹",
  "2": "²",
  "3": "³",
  "4": "⁴",
  "5": "⁵",
  "6": "⁶",
  "7": "⁷",
  "8": "⁸",
  "9": "⁹",
}
COMPONENTS = ["text", "punctuation", "capitalization", "inlineFormatting", "alternatives", "table", "formula", "media"]
COMPONENT_LABELS = {
  "text": "Texto",
  "punctuation": "Pontuacao",
  "capitalization": "Capitalizacao",
  "inlineFormatting": "Formatacao inline",
  "alternatives": "Alternativas",
  "table": "Tabela",
  "formula": "Formula",
  "media": "Midia",
}

ADMISSION_ALLOWED_CLASSIFICATIONS = {"text_native", "hybrid"}


def admission_decision(inventory: dict[str, Any]) -> dict[str, Any]:
  classification = inventory.get("classification") or "unknown"
  if classification in ADMISSION_ALLOWED_CLASSIFICATIONS:
    state = "admitted"
    reason = "PDF possui texto extraivel suficiente para preflight estrutural."
  elif classification == "text_low_quality":
    state = "needs_structural_recovery"
    reason = "PDF possui texto extraivel baixo/fraco; auditoria automatica ainda nao e segura."
  elif classification == "raster":
    state = "needs_ocr"
    reason = "PDF sem texto extraivel suficiente; exige futura camada OCR antes da auditoria."
  else:
    state = "admission_uncertain"
    reason = "Classificacao estrutural do PDF nao foi conclusiva."
  return {
    "state": state,
    "classification": classification,
    "allowedToPreflight": state == "admitted",
    "reason": reason,
    "pageCount": inventory.get("pageCount"),
    "averageCharsPerPage": inventory.get("averageCharsPerPage"),
    "medianCharsPerPage": inventory.get("medianCharsPerPage"),
    "pagesWithoutText": inventory.get("pagesWithoutText"),
    "pagesWithoutTextRatio": inventory.get("pagesWithoutTextRatio"),
    "imagePageRatio": inventory.get("imagePageRatio"),
    "dominantImages": inventory.get("dominantImages"),
  }


def normalize_pdf_text(value: str) -> str:
  replacements = {
    "\uf02d": "-",
    "\uf0b7": "•",
    "\u00ad": "",
    "−": "-",
    "–": "-",
    "—": "-",
    "×": "x",
  }
  for source, target in replacements.items():
    value = value.replace(source, target)
  return value.replace("\r\n", "\n").replace("\r", "\n")


def collapse_spaces(value: str) -> str:
  return re.sub(r"\s+", " ", normalize_pdf_text(value)).strip()


def strip_accents(value: str) -> str:
  return "".join(ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn")


def loose_text(value: str) -> str:
  value = strip_accents(collapse_spaces(value)).lower()
  value = re.sub(rf"[{re.escape(PUNCTUATION)}]", " ", value)
  return re.sub(r"\s+", " ", value).strip()


def comparable_text(value: str) -> str:
  value = collapse_spaces(value)
  value = re.sub(r"(\d+)\s*[º°]\s*C\b", r"\1°C", value)
  value = re.sub(r"([º°])\s*C\.", r"\1C§", value)
  value = re.sub(r"^\s*0*\d{1,3}\s*[.)\-–—]\s*", "", value)
  value = re.sub(r"^\([^)]*\)\s*", "", value)
  value = re.sub(r"QUEST(?:ÃO|AO)\s*0*\d{1,3}\s*[.\-–—]?\s*", "", value, flags=re.IGNORECASE)
  value = re.sub(r"\b[A-E]\s*\(\s*\)\s*", "", value)
  value = re.sub(r"\b[A-E]\s*[).:\-–—]\s*", "", value)
  value = value.replace("§", ".")
  return collapse_spaces(value)


def similarity(left: str, right: str) -> float:
  if not left and not right:
    return 1.0
  if not left or not right:
    return 0.0
  return SequenceMatcher(None, left, right).ratio()


def confidence(score: float) -> str:
  if score >= 0.92:
    return "alta"
  if score >= 0.78:
    return "media"
  return "baixa"


def load_local_config(config_path: Path) -> dict[str, Any]:
  if not config_path.exists():
    return {}
  return json.loads(config_path.read_text(encoding="utf-8"))


def default_d1_db_path() -> Path | None:
  if not DEFAULT_D1_DIR.exists():
    return None
  candidates = [
    path for path in DEFAULT_D1_DIR.glob("*.sqlite")
    if path.name != "metadata.sqlite"
  ]
  if not candidates:
    return None
  return max(candidates, key=lambda path: path.stat().st_mtime)


def parse_json_field(value: Any, fallback: Any) -> Any:
  if value is None or value == "":
    return fallback
  try:
    return json.loads(value)
  except Exception:
    return fallback


def revision_row_to_question(row: sqlite3.Row) -> dict[str, Any]:
  return {
    "id": row["id"],
    "sourceRow": row["source_row"],
    "school": row["school"],
    "year": row["year"],
    "number": row["number"],
    "subjects": parse_json_field(row["subjects"], []),
    "answer": row["answer"],
    "answerType": row["answer_type"],
    "difficulty": row["difficulty"],
    "content": row["content"],
    "preview": row["preview"],
    "sourceDocument": row["source_document"],
    "sourceBookmark": row["source_bookmark"],
    "hasTable": bool(row["has_table"]),
    "hasMedia": bool(row["has_media"]),
    "hasMath": bool(row["has_math"]),
    "status": row["status"],
    "isCustom": bool(row["is_custom"]),
    "stem": row["stem"],
    "alternatives": parse_json_field(row["alternatives"], []),
    "formula": row["formula"],
    "tableData": row["table_data"],
    "imageUrls": parse_json_field(row["image_urls"], []),
    "contentBlocks": parse_json_field(row["content_blocks"], []),
    "alternativeBlocks": parse_json_field(row["alternative_blocks"], []),
    "authenticatedAt": row["authenticated_at"],
    "authenticatedBy": row["authenticated_by"],
    "isLocked": bool(row["is_locked"]),
    "lockedAt": row["locked_at"],
    "lockedBy": row["locked_by"],
    "lastUnlockReason": row["last_unlock_reason"],
    "auditTrail": parse_json_field(row["audit_trail"], []),
    "updatedAt": row["updated_at"],
  }


def load_revisions_from_d1(d1_db: Path | None) -> tuple[list[dict[str, Any]], str | None]:
  path = d1_db or default_d1_db_path()
  if not path:
    return [], None
  connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
  connection.row_factory = sqlite3.Row
  try:
    rows = connection.execute("select * from question_revisions").fetchall()
  finally:
    connection.close()
  return [revision_row_to_question(row) for row in rows], str(path)


def effective_catalog(base: list[dict[str, Any]], revisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
  by_id = {question["id"]: dict(question) for question in base}
  for revision in revisions:
    merged = dict(by_id.get(revision["id"], {}))
    merged.update(revision)
    by_id[revision["id"]] = merged
  return list(by_id.values())


def configured_pdf_root(args: argparse.Namespace) -> Path:
  if args.pdf_root:
    return Path(args.pdf_root)
  env_root = os.environ.get("SIMPLEQUEST_PDF_ROOT")
  if env_root:
    return Path(env_root)
  config = load_local_config(Path(args.config))
  if config.get("pdfRoot"):
    return Path(config["pdfRoot"])
  raise SystemExit(
    "Informe a raiz externa dos PDFs com --pdf-root, SIMPLEQUEST_PDF_ROOT "
    "ou .simplequest-audit.local.json ({\"pdfRoot\":\"...\"})."
  )


def question_slug(text: str) -> str:
  text = strip_accents(text).lower()
  return re.sub(r"[^a-z0-9]+", " ", text).strip()


def find_pdf(pdf_root: Path, school: str, year: int, explicit_pdf: str | None) -> tuple[Path, str, list[dict[str, Any]]]:
  if explicit_pdf:
    path = Path(explicit_pdf)
    if not path.exists():
      raise SystemExit(f"PDF informado nao encontrado: {path}")
    return path, "alta", []

  candidates: list[dict[str, Any]] = []
  school_slug = question_slug(school)
  year_tokens = {str(year), f"{year}_{year + 1}", f"{year}-{year + 1}"}
  for path in pdf_root.rglob("*.pdf"):
    name = path.name
    name_slug = question_slug(name)
    if name_slug.startswith("gab "):
      continue
    if " port " in f" {name_slug} " or "portugues" in name_slug:
      continue
    if school_slug not in name_slug:
      continue
    score = 0
    reasons = []
    if f"{year}_{year + 1}" in name or f"{year}-{year + 1}" in name:
      score += 80
      reasons.append("ciclo-ano-ano-seguinte")
    elif str(year) in name:
      score += 35
      reasons.append("ano")
    if "mat" in name_slug or "matematica" in name_slug:
      score += 20
      reasons.append("matematica")
    if "6ano" in name_slug or "6 ano" in name_slug or "6o ano" in name_slug:
      score += 20
      reasons.append("6ano")
    if school_slug == question_slug(path.parent.parent.name) or school_slug == question_slug(path.parent.name):
      score += 10
      reasons.append("pasta")
    if score and any(token in name for token in year_tokens):
      candidates.append({"path": str(path), "score": score, "reasons": reasons})

  candidates.sort(key=lambda item: item["score"], reverse=True)
  if not candidates:
    raise SystemExit(f"Nenhum PDF candidato encontrado para {school} {year} em {pdf_root}")
  top = candidates[0]
  level = "alta" if top["score"] >= 80 else "media" if top["score"] >= 60 else "baixa"
  return Path(top["path"]), level, candidates[:10]


@dataclass
class PdfWord:
  text: str
  page: int
  x0: float
  x1: float
  top: float
  bottom: float
  font: str
  bold: bool
  italic: bool
  underline: bool


@dataclass
class PdfQuestion:
  number: int
  text: str
  pages: list[int]
  image_count: int
  bold_word_count: int
  italic_word_count: int
  font_samples: list[str]
  words: list[PdfWord]
  tables: list[SemanticTable]
  formulas: list[dict[str, Any]]
  structure: dict[str, Any]
  capabilities: dict[str, bool] | None = None


@dataclass
class AuditToken:
  text: str
  normalized: str
  role: str
  option: str | None
  bold: bool = False
  italic: bool = False
  underline: bool = False


@dataclass
class SemanticTableCell:
  row: int
  column: int
  row_span: int
  col_span: int
  merged: bool
  ghost: bool
  text: str
  blocks: list[dict[str, Any]]
  formulas: list[str]
  formula_structures: list[dict[str, Any]]
  bbox: tuple[float, float, float, float] | None = None


@dataclass
class SemanticTable:
  source: str
  page: int | None
  rows: int
  columns: int
  cells: list[SemanticTableCell]
  confidence: str


def style_from_font(font: str) -> tuple[bool, bool]:
  lowered = font.lower()
  return ("bold" in lowered or "black" in lowered), ("italic" in lowered or "oblique" in lowered)


def structural_key(value: str) -> str:
  value = strip_accents(normalize_pdf_text(value)).upper()
  value = re.sub(r"\d+", "#", value)
  value = re.sub(r"[_\W]+", " ", value, flags=re.UNICODE)
  return collapse_spaces(value)


def compact_structure(value: str) -> str:
  return re.sub(r"[^A-Z0-9]", "", strip_accents(normalize_pdf_text(value)).upper())


def page_lines(page: pdfplumber.page.Page) -> list[dict[str, Any]]:
  words = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False, use_text_flow=False) or []
  lines: list[dict[str, Any]] = []
  for word in words:
    top = float(word["top"])
    bucket = round(top / 3)
    current = next((line for line in lines if line["bucket"] == bucket and abs(line["top"] - top) < 3.0), None)
    if current is None:
      current = {"bucket": bucket, "top": top, "bottom": float(word["bottom"]), "x0": float(word["x0"]), "x1": float(word["x1"]), "words": []}
      lines.append(current)
    current["words"].append(word)
    current["top"] = min(current["top"], float(word["top"]))
    current["bottom"] = max(current["bottom"], float(word["bottom"]))
    current["x0"] = min(current["x0"], float(word["x0"]))
    current["x1"] = max(current["x1"], float(word["x1"]))
  for line in lines:
    line["words"].sort(key=lambda item: float(item["x0"]))
    line["text"] = normalize_pdf_text(" ".join(str(word.get("text", "")) for word in line["words"]))
    line["key"] = structural_key(line["text"])
  return sorted(lines, key=lambda item: (item["top"], item["x0"]))


def question_marker_from_line(line: dict[str, Any], expected_numbers: set[int] | None = None) -> dict[str, Any] | None:
  text = normalize_pdf_text(line.get("text", ""))
  normalized = strip_accents(text).upper()
  normalized = re.sub(r"\s+", " ", normalized).strip()
  match = re.search(r"\b(?:Q\s*)?UESTAO\s*0*(\d{1,3})\b", normalized)
  if match:
    return {"number": int(match.group(1)), "pattern": "questao"}
  # Some PDFs mark questions only as "01.", "02.", ... at the left margin.
  if float(line.get("x0", 999)) <= 85:
    numeric = re.match(r"\s*0*(\d{1,3})\s*(?:[.)](?!\d)|[-–—])(?:\s|$)", text)
    if numeric:
      number = int(numeric.group(1))
      if expected_numbers is None or number in expected_numbers:
        return {"number": number, "pattern": "numeric-dot"}
  return None


def marker_candidate_score(start: dict[str, Any], expected_numbers: set[int]) -> float:
  text = str(start.get("text", ""))
  normalized = strip_accents(text).upper()
  score = 0.0
  if start.get("number") in expected_numbers:
    score += 20
  if start.get("pattern") == "questao":
    score += 12
  elif start.get("pattern") == "numeric-dot":
    score += 5
  if float(start.get("page", 0)) == 0:
    score -= 8
  if re.fullmatch(r"\s*\d{1,3}\s*[.)\-–—]?\s*", text):
    score -= 4
  if any(marker in normalized for marker in ["PROVA", "CADERNO", "INSTRU", "CARTAO", "RESPOSTA"]):
    score -= 6
  if len(text) > 25:
    score += 3
  return score


def detect_recurring_structure(pdf: pdfplumber.PDF) -> dict[str, Any]:
  all_lines: list[dict[str, Any]] = []
  page_count = len(pdf.pages)
  for page_index, page in enumerate(pdf.pages):
    for line in page_lines(page):
      if not line.get("key"):
        continue
      all_lines.append({**line, "page": page_index + 1, "pageHeight": float(page.height)})
  grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
  for line in all_lines:
    band = "top" if line["top"] < 95 else "bottom" if line["bottom"] > line["pageHeight"] - 95 else "middle"
    if band == "middle":
      continue
    grouped.setdefault((band, line["key"]), []).append(line)
  recurring: list[dict[str, Any]] = []
  threshold = max(2, int(page_count * 0.25))
  for (band, key), items in grouped.items():
    pages = sorted({item["page"] for item in items})
    if len(pages) < threshold:
      continue
    sample = items[0]
    recurring.append({
      "band": band,
      "key": key,
      "sample": sample["text"],
      "pages": pages[:12],
      "count": len(pages),
      "top": round(sum(float(item["top"]) for item in items) / len(items), 2),
      "bottom": round(sum(float(item["bottom"]) for item in items) / len(items), 2),
      "x0": round(min(float(item["x0"]) for item in items), 2),
      "x1": round(max(float(item["x1"]) for item in items), 2),
    })
  confidence = 0.95 if recurring else 0.65
  return {"regions": recurring, "confidence": confidence}


def line_is_structural(line: dict[str, Any], structure: dict[str, Any] | None) -> bool:
  if not structure:
    return False
  key = structural_key(line.get("text", ""))
  for region in structure.get("regions") or []:
    if key != region.get("key"):
      continue
    if abs(float(line.get("top", 0)) - float(region.get("top", 0))) <= 8:
      return True
  return False


def preflight_pdf(pdf_path: Path, expected_numbers: list[int]) -> dict[str, Any]:
  expected_set = set(expected_numbers)
  with pdfplumber.open(str(pdf_path)) as pdf:
    recurring = detect_recurring_structure(pdf)
    starts: list[dict[str, Any]] = []
    patterns: dict[str, int] = {}
    line_summaries: list[dict[str, Any]] = []
    for page_index, page in enumerate(pdf.pages):
      for line in page_lines(page):
        marker = question_marker_from_line(line, expected_set)
        if not marker:
          continue
        starts.append({
          "number": marker["number"],
          "page": page_index,
          "top": float(line["top"]),
          "pattern": marker["pattern"],
          "text": line["text"],
        })
        patterns[marker["pattern"]] = patterns.get(marker["pattern"], 0) + 1
        line_summaries.append({"page": page_index + 1, "number": marker["number"], "pattern": marker["pattern"], "text": line["text"][:120]})
    dedup: dict[int, dict[str, Any]] = {}
    for start in sorted(starts, key=lambda item: (item["page"], item["top"])):
      if start["number"] not in expected_set:
        continue
      scored = {**start, "markerConfidence": round(marker_candidate_score(start, expected_set), 4)}
      previous = dedup.get(start["number"])
      if previous is None or scored["markerConfidence"] > previous.get("markerConfidence", -999):
        dedup[start["number"]] = scored
    detected = sorted(dedup.values(), key=lambda item: (item["page"], item["top"]))
    expected_count = len(expected_numbers)
    detected_count = len(detected)
    coverage = detected_count / expected_count if expected_count else 0.0
    ordered = [item["number"] for item in detected]
    monotonic = ordered == sorted(ordered)
    if coverage >= 0.95 and monotonic:
      status = "ready_for_audit"
      segmentation_confidence = min(0.99, 0.9 + coverage * 0.09)
    elif coverage >= 0.65:
      status = "segmentation_uncertain"
      segmentation_confidence = coverage * 0.8
    else:
      status = "segmentation_failed"
      segmentation_confidence = coverage * 0.5
    return {
      "pageCount": len(pdf.pages),
      "expectedQuestions": expected_count,
      "detectedQuestions": detected_count,
      "missingQuestions": [number for number in expected_numbers if number not in dedup],
      "extraQuestionMarkers": [item["number"] for item in starts if item["number"] not in expected_set],
      "questionMarkers": line_summaries[:40],
      "selectedQuestionMarkers": [
        {
          "page": item["page"] + 1,
          "number": item["number"],
          "pattern": item.get("pattern"),
          "confidence": item.get("markerConfidence"),
          "text": str(item.get("text", ""))[:120],
        }
        for item in detected[:60]
      ],
      "markerPatterns": patterns,
      "segmentationConfidence": round(segmentation_confidence, 4),
      "status": status,
      "headersFooters": recurring,
      "alternativePattern": "detected_per_question",
      "visualAlternatives": "detected_per_catalog_question",
      "structuralTextRegions": recurring.get("regions", [])[:20],
      "_starts": detected,
    }


def extract_question_starts(pdf: pdfplumber.PDF, expected_numbers: list[int] | None = None, preflight: dict[str, Any] | None = None) -> list[dict[str, Any]]:
  if preflight and preflight.get("_starts"):
    return [
      {"number": item["number"], "page": item["page"], "top": item["top"], "pattern": item.get("pattern")}
      for item in preflight["_starts"]
    ]
  starts: list[dict[str, Any]] = []
  for page_index, page in enumerate(pdf.pages):
    for line in page_lines(page):
      marker = question_marker_from_line(line, set(expected_numbers) if expected_numbers else None)
      if marker:
        starts.append({"number": marker["number"], "page": page_index, "top": float(line["top"]), "pattern": marker["pattern"]})
  dedup: dict[int, dict[str, Any]] = {}
  for start in starts:
    dedup.setdefault(start["number"], start)
  return sorted(dedup.values(), key=lambda item: (item["page"], item["top"]))


def crop_text(page: pdfplumber.page.Page, top: float, bottom: float, structure: dict[str, Any] | None = None) -> str:
  lines = []
  for line in page_lines(page):
    if not (top <= float(line["top"]) <= bottom):
      continue
    if line_is_structural(line, structure):
      continue
    lines.append(line["text"])
  text = normalize_pdf_text("\n".join(lines))
  return apply_detected_superscript_units(page, top, bottom, text)


def count_images(page: pdfplumber.page.Page, top: float, bottom: float) -> int:
  return sum(1 for image in page.images if top <= float(image.get("top", 0)) <= bottom)


def horizontal_overlap(left_x0: float, left_x1: float, right_x0: float, right_x1: float) -> float:
  return max(0.0, min(left_x1, right_x1) - max(left_x0, right_x0))


def apply_detected_superscript_units(page: pdfplumber.page.Page, top: float, bottom: float, text: str) -> str:
  chars = [
    char for char in (getattr(page, "chars", []) or [])
    if top <= float(char.get("top", 0)) <= bottom
  ]
  replacements: list[tuple[str, str]] = []
  for index, char in enumerate(chars):
    digit = str(char.get("text", ""))
    if digit not in SUPERSCRIPT_DIGITS:
      continue
    previous = []
    cursor = index - 1
    while cursor >= 0 and len(previous) < 2:
      candidate = chars[cursor]
      value = str(candidate.get("text", ""))
      if value.strip():
        previous.append(candidate)
      cursor -= 1
    if len(previous) < 2:
      continue
    previous = list(reversed(previous))
    unit = "".join(str(item.get("text", "")) for item in previous).lower()
    if unit not in {"cm", "mm", "m²", "m", "km"} and not unit.endswith("m"):
      continue
    base_size = max(float(item.get("size", 0)) for item in previous)
    digit_size = float(char.get("size", 0))
    if not base_size or digit_size / base_size > 0.82:
      continue
    if float(char.get("top", 0)) >= min(float(item.get("top", 0)) for item in previous) - 0.6:
      continue
    if abs(float(char.get("x0", 0)) - float(previous[-1].get("x1", 0))) > 2.0:
      continue
    plain = f"{unit}{digit}"
    semantic = f"{unit}{SUPERSCRIPT_DIGITS[digit]}"
    replacements.append((plain, semantic))
  for plain, semantic in replacements:
    text = re.sub(rf"\b{re.escape(plain)}\b", semantic, text, count=1, flags=re.IGNORECASE)
  return text


def is_word_underlined(page: pdfplumber.page.Page, word: dict[str, Any]) -> bool:
  word_x0 = float(word["x0"])
  word_x1 = float(word["x1"])
  word_width = max(1.0, word_x1 - word_x0)
  baseline = float(word["bottom"])
  shapes = [*(getattr(page, "rects", []) or []), *(getattr(page, "lines", []) or [])]
  for shape in shapes:
    x0 = float(shape.get("x0", 0))
    x1 = float(shape.get("x1", 0))
    y0 = float(shape.get("top", shape.get("y0", 0)))
    y1 = float(shape.get("bottom", shape.get("y1", y0)))
    height = abs(y1 - y0)
    width = abs(x1 - x0)
    if height > 2.5:
      continue
    if width > max(90.0, word_width * 2.5):
      continue
    if horizontal_overlap(word_x0, word_x1, x0, x1) / word_width < 0.55:
      continue
    if -0.5 <= y0 - baseline <= 1.8 or -0.5 <= y1 - baseline <= 1.8:
      return True
  return False


def inline_block_text(block: dict[str, Any]) -> str:
  kind = block.get("type")
  if kind == "text":
    return block.get("text", "")
  if kind == "formula":
    return f"\\({block.get('latex', '')}\\)"
  if kind == "script":
    return f"{block.get('base', '')}{block.get('value', '')}"
  return ""


def is_marker_cell(blocks: list[dict[str, Any]], marker: str) -> bool:
  return len(blocks) == 1 and blocks[0].get("type") == "text" and blocks[0].get("text", "").strip() == marker


def table_cell_text(blocks: list[dict[str, Any]]) -> str:
  return collapse_spaces("".join(inline_block_text(block) for block in blocks))


def table_cell_formulas(blocks: list[dict[str, Any]]) -> list[str]:
  return [block.get("latex", "") for block in blocks if block.get("type") == "formula" and block.get("latex")]


def parse_latex_fraction(latex: str) -> dict[str, Any] | None:
  normalized = collapse_spaces(latex).replace(" ", "")
  match = re.fullmatch(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", normalized)
  if not match:
    return None
  return {
    "type": "fraction",
    "numerator": match.group(1),
    "denominator": match.group(2),
    "source": "catalog",
  }


def formula_structures_from_latex(formulas: list[str]) -> list[dict[str, Any]]:
  structures: list[dict[str, Any]] = []
  for formula in formulas:
    fraction = parse_latex_fraction(formula)
    if fraction:
      structures.append(fraction)
    else:
      structures.append({"type": "unsupported", "latex": formula, "source": "catalog"})
  return structures


def parse_simplequest_table(block: dict[str, Any]) -> SemanticTable:
  # Python port of app/components/QuestionBlocks.tsx parseTableContent().
  source = block.get("content") if block.get("content") else [{"id": f"{block.get('id', 'table')}-text", "type": "text", "text": block.get("data", "")}]
  rows: list[list[list[dict[str, Any]]]] = [[[]]]
  part = 0
  quoted = False

  def current_cell() -> list[dict[str, Any]]:
    return rows[-1][-1]

  def next_cell() -> None:
    rows[-1].append([])

  def next_row() -> None:
    rows.append([[]])

  def push_text(content: dict[str, Any], segment: dict[str, Any], text: str) -> None:
    nonlocal part
    if not text:
      return
    formatted = bool(segment.get("bold") or segment.get("italic") or segment.get("underline"))
    item = {
      "id": f"{content.get('id', 'text')}-table-{part}",
      "type": "text",
      "text": text,
      "alignment": content.get("alignment"),
    }
    part += 1
    if formatted:
      item["segments"] = [{**segment, "text": text}]
    current_cell().append(item)

  for content in source:
    if content.get("type") != "text":
      current_cell().append(content)
      continue
    segments = content.get("segments") if content.get("segments") else [{"text": content.get("text", "")}]
    for segment in segments:
      buffer = ""
      for character in segment.get("text", "").replace("\r\n", "\n"):
        if character in {"`", "´"}:
          push_text(content, segment, buffer)
          buffer = ""
          quoted = not quoted
        elif not quoted and character == "|":
          push_text(content, segment, buffer)
          buffer = ""
          next_cell()
        elif not quoted and character == "\n":
          push_text(content, segment, buffer)
          buffer = ""
          next_row()
        else:
          buffer += character
      push_text(content, segment, buffer)

  parsed_rows: list[list[dict[str, Any]]] = []
  for row in rows:
    if not any(any(item.get("type") != "text" or item.get("text", "").strip() for item in cell) for cell in row):
      continue
    parsed_rows.append([
      {"blocks": cell, "rowSpan": 1, "colSpan": 1, "merged": False, "ghost": is_marker_cell(cell, "~")}
      for cell in row
    ])

  for row in parsed_rows:
    for cell_index, cell in enumerate(row):
      if not is_marker_cell(cell["blocks"], ">"):
        continue
      for target_index in range(cell_index - 1, -1, -1):
        target = row[target_index]
        if target["merged"]:
          continue
        if target["ghost"]:
          break
        target["colSpan"] += 1
        cell["merged"] = True
        break

  for row_index in range(1, len(parsed_rows)):
    for cell_index, cell in enumerate(parsed_rows[row_index]):
      if not is_marker_cell(cell["blocks"], "^"):
        continue
      for target_row in range(row_index - 1, -1, -1):
        if cell_index >= len(parsed_rows[target_row]):
          continue
        target = parsed_rows[target_row][cell_index]
        if target["merged"]:
          continue
        target["rowSpan"] += 1
        cell["merged"] = True
        break

  cells: list[SemanticTableCell] = []
  for row_index, row in enumerate(parsed_rows):
    for column_index, cell in enumerate(row):
      cells.append(SemanticTableCell(
        row=row_index,
        column=column_index,
        row_span=cell["rowSpan"],
        col_span=cell["colSpan"],
        merged=cell["merged"],
        ghost=cell["ghost"],
        text=table_cell_text(cell["blocks"]),
        blocks=cell["blocks"],
        formulas=table_cell_formulas(cell["blocks"]),
        formula_structures=formula_structures_from_latex(table_cell_formulas(cell["blocks"])),
      ))
  return SemanticTable(
    source="catalog",
    page=None,
    rows=len(parsed_rows),
    columns=max((len(row) for row in parsed_rows), default=0),
    cells=cells,
    confidence="alta",
  )


def normalized_cell_text(value: Any) -> str:
  if value is None:
    return ""
  return collapse_spaces(str(value))


def text_from_words(words: list[dict[str, Any]]) -> str:
  ordered = sorted(words, key=lambda word: (float(word.get("top", 0)), float(word.get("x0", 0))))
  return collapse_spaces(" ".join(normalize_pdf_text(str(word.get("text", ""))) for word in ordered))


def cell_words(page: pdfplumber.page.Page, bbox: tuple[float, float, float, float]) -> list[dict[str, Any]]:
  x0, top, x1, bottom = bbox
  words = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False, use_text_flow=False) or []
  return [
    word for word in words
    if x0 - 1 <= float(word["x0"]) and float(word["x1"]) <= x1 + 1 and top - 1 <= float(word["top"]) and float(word["bottom"]) <= bottom + 1
  ]


def horizontal_shapes(page: pdfplumber.page.Page, bbox: tuple[float, float, float, float]) -> list[dict[str, float]]:
  cell_x0, cell_top, cell_x1, cell_bottom = bbox
  shapes: list[dict[str, float]] = []
  for shape in [*(getattr(page, "rects", []) or []), *(getattr(page, "lines", []) or [])]:
    x0 = float(shape.get("x0", 0))
    x1 = float(shape.get("x1", 0))
    top = float(shape.get("top", shape.get("y0", 0)))
    bottom = float(shape.get("bottom", shape.get("y1", top)))
    width = abs(x1 - x0)
    height = abs(bottom - top)
    if height > 2.0 or width < 4.0:
      continue
    if x0 < cell_x0 - 1 or x1 > cell_x1 + 1 or top < cell_top - 1 or bottom > cell_bottom + 1:
      continue
    shapes.append({"x0": min(x0, x1), "x1": max(x0, x1), "top": min(top, bottom), "bottom": max(top, bottom), "width": width, "height": height})
  return shapes


def detect_fraction_in_bbox(page: pdfplumber.page.Page, bbox: tuple[float, float, float, float], page_number: int) -> list[dict[str, Any]]:
  words = cell_words(page, bbox)
  shapes = horizontal_shapes(page, bbox)
  cell_width = max(1.0, bbox[2] - bbox[0])
  fractions: list[dict[str, Any]] = []
  for shape in shapes:
    # Full-width table borders are not fraction bars. A fraction bar is local and
    # sits between two compact text groups inside the same cell.
    if shape["width"] > cell_width * 0.55 or shape["width"] > 45:
      continue
    if shape["top"] - bbox[1] < 4 or bbox[3] - shape["bottom"] < 4:
      continue
    bar_center = (shape["x0"] + shape["x1"]) / 2
    above = [
      word for word in words
      if float(word["bottom"]) <= shape["top"] + 1.2 and 0 <= shape["top"] - float(word["bottom"]) <= 12
      and horizontal_overlap(float(word["x0"]), float(word["x1"]), shape["x0"] - 3, shape["x1"] + 3) > 0
    ]
    below = [
      word for word in words
      if float(word["top"]) >= shape["bottom"] - 1.2 and 0 <= float(word["top"]) - shape["bottom"] <= 12
      and horizontal_overlap(float(word["x0"]), float(word["x1"]), shape["x0"] - 3, shape["x1"] + 3) > 0
    ]
    numerator = text_from_words(above)
    denominator = text_from_words(below)
    if not numerator or not denominator:
      continue
    if not re.search(r"\d", numerator) or not re.search(r"\d", denominator):
      continue
    if not re.fullmatch(r"[\wÀ-ÿ.,+\-]+(?:\s+[\wÀ-ÿ.,+\-]+)*", numerator, flags=re.UNICODE):
      continue
    if not re.fullmatch(r"[\wÀ-ÿ.,+\-]+(?:\s+[\wÀ-ÿ.,+\-]+)*", denominator, flags=re.UNICODE):
      continue
    numerator_center = (min(float(word["x0"]) for word in above) + max(float(word["x1"]) for word in above)) / 2
    denominator_center = (min(float(word["x0"]) for word in below) + max(float(word["x1"]) for word in below)) / 2
    if abs(numerator_center - bar_center) > max(8.0, shape["width"] * 0.7):
      continue
    if abs(denominator_center - bar_center) > max(8.0, shape["width"] * 0.7):
      continue
    fractions.append({
      "type": "fraction",
      "numerator": numerator,
      "denominator": denominator,
      "source": "pdf",
      "page": page_number,
      "confidence": "alta",
      "bbox": [round(bbox[0], 2), round(bbox[1], 2), round(bbox[2], 2), round(bbox[3], 2)],
      "bar": [round(shape["x0"], 2), round(shape["top"], 2), round(shape["x1"], 2), round(shape["bottom"], 2)],
    })
  dedup: list[dict[str, Any]] = []
  seen: set[tuple[str, str, int, int]] = set()
  for fraction in fractions:
    key = (fraction["numerator"], fraction["denominator"], round(fraction["bar"][0]), round(fraction["bar"][1]))
    if key not in seen:
      seen.add(key)
      dedup.append(fraction)
  return dedup


def detect_pdf_fractions(page: pdfplumber.page.Page, top: float, bottom: float, page_number: int) -> list[dict[str, Any]]:
  return detect_fraction_in_bbox(page, (0.0, max(0, top - 2), float(page.width), min(float(page.height), bottom)), page_number)


def clean_pdf_table_rows(rows: list[list[Any]]) -> list[list[str]]:
  compressed: list[list[str]] = []
  for row in rows:
    values = [normalized_cell_text(cell) for cell in row]
    non_empty = [value for value in values if value]
    if not non_empty:
      continue
    joined = " ".join(non_empty)
    normalized_joined = strip_accents(joined).upper()
    if "PROVA DE MATEMATICA" in normalized_joined or "QUESTAO" in normalized_joined or "QUEST�O" in joined:
      continue
    if len(joined) > 350:
      continue
    compressed.append(non_empty)

  merged: list[list[str]] = []
  for row in compressed:
    if merged and len(row) == max(1, len(merged[-1]) - 1):
      for index, value in enumerate(row, start=len(merged[-1]) - len(row)):
        merged[-1][index] = collapse_spaces(f"{merged[-1][index]} {value}")
      continue
    if merged and len(row) == 1 and len(merged[-1]) > 1:
      merged[-1][-1] = collapse_spaces(f"{merged[-1][-1]} {row[0]}")
      continue
    merged.append(row)
  return merged


def semantic_pdf_table(rows: list[list[Any]], page_number: int, page: pdfplumber.page.Page | None = None, cell_bboxes: list[list[tuple[float, float, float, float] | None]] | None = None) -> SemanticTable | None:
  cleaned = clean_pdf_table_rows(rows)
  if len(cleaned) < 2:
    return None
  columns = max(len(row) for row in cleaned)
  if columns < 2:
    return None
  cells: list[SemanticTableCell] = []
  cleaned_bboxes: list[list[tuple[float, float, float, float] | None]] = []
  if cell_bboxes:
    for raw_row, bbox_row in zip(rows, cell_bboxes):
      row_bboxes = [
        bbox for value, bbox in zip(raw_row, bbox_row)
        if normalized_cell_text(value)
      ]
      if row_bboxes:
        cleaned_bboxes.append(row_bboxes)
  for row_index, row in enumerate(cleaned):
    for column_index in range(columns):
      text = row[column_index] if column_index < len(row) else ""
      bbox = cleaned_bboxes[row_index][column_index] if row_index < len(cleaned_bboxes) and column_index < len(cleaned_bboxes[row_index]) else None
      formula_structures = detect_fraction_in_bbox(page, bbox, page_number) if page and bbox else []
      if formula_structures:
        formula_words = " ".join(f"{item['numerator']} {item['denominator']}" for item in formula_structures)
        if loose_text(text) == loose_text(formula_words):
          text = ""
      cells.append(SemanticTableCell(
        row=row_index,
        column=column_index,
        row_span=1,
        col_span=1,
        merged=False,
        ghost=False,
        text=text,
        blocks=[{"type": "text", "text": text}] if text else [],
        formulas=[],
        formula_structures=formula_structures,
        bbox=bbox,
      ))
  confidence_level = "alta" if all(len(row) == columns for row in cleaned[1:]) else "media"
  return SemanticTable(source="pdf", page=page_number, rows=len(cleaned), columns=columns, cells=cells, confidence=confidence_level)


def extract_pdf_tables(page: pdfplumber.page.Page, top: float, bottom: float, page_number: int) -> list[SemanticTable]:
  crop = page.crop((0, max(0, top - 2), page.width, min(page.height, bottom)))
  tables: list[SemanticTable] = []
  try:
    found_tables = crop.find_tables(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}) or []
  except Exception:
    found_tables = []
  for raw_table in found_tables:
    rows = raw_table.extract()
    cell_bboxes = [list(row.cells) for row in raw_table.rows]
    semantic = semantic_pdf_table(rows, page_number, page, cell_bboxes)
    if semantic:
      tables.append(semantic)
  return tables


def extract_pdf_words(page: pdfplumber.page.Page, top: float, bottom: float, page_number: int) -> list[PdfWord]:
  words = page.extract_words(extra_attrs=["fontname"], keep_blank_chars=False, use_text_flow=False) or []
  result: list[PdfWord] = []
  for word in words:
    if not (top <= float(word["top"]) <= bottom):
      continue
    text = normalize_pdf_text(word.get("text", ""))
    if not text.strip():
      continue
    font = str(word.get("fontname") or "")
    bold, italic = style_from_font(font)
    result.append(PdfWord(
      text=text,
      page=page_number,
      x0=float(word["x0"]),
      x1=float(word["x1"]),
      top=float(word["top"]),
      bottom=float(word["bottom"]),
      font=font,
      bold=bold,
      italic=italic,
      underline=is_word_underlined(page, word),
    ))
  return result


def word_style_counts(page: pdfplumber.page.Page, top: float, bottom: float) -> tuple[int, int, list[str]]:
  words = page.extract_words(extra_attrs=["fontname"], keep_blank_chars=False, use_text_flow=False) or []
  bold = 0
  italic = 0
  samples: list[str] = []
  for word in words:
    if not (top <= float(word["top"]) <= bottom):
      continue
    font = str(word.get("fontname") or "")
    if font and font not in samples:
      samples.append(font)
    is_bold, is_italic = style_from_font(font)
    if is_bold:
      bold += 1
    if is_italic:
      italic += 1
  return bold, italic, samples[:8]


def extract_pdf_questions(pdf_path: Path, expected_numbers: list[int] | None = None, preflight: dict[str, Any] | None = None) -> dict[int, PdfQuestion]:
  with pdfplumber.open(str(pdf_path)) as pdf:
    starts = extract_question_starts(pdf, expected_numbers, preflight)
    expected_last = max(expected_numbers) if expected_numbers else None
    recurring_samples = " ".join(
      compact_structure(str(region.get("sample", "")))
      for region in ((preflight or {}).get("headersFooters") or {}).get("regions", [])
    )
    mixed_subject_pdf = "MATEMATICA" in recurring_samples and "LINGUAPORTUGUESA" in recurring_samples
    result: dict[int, PdfQuestion] = {}
    for index, start in enumerate(starts):
      next_start = starts[index + 1] if index + 1 < len(starts) else None
      pieces: list[str] = []
      pages: list[int] = []
      image_count = 0
      bold_count = 0
      italic_count = 0
      font_samples: list[str] = []
      question_words: list[PdfWord] = []
      question_tables: list[SemanticTable] = []
      question_formulas: list[dict[str, Any]] = []
      if next_start:
        end_page = next_start["page"] if next_start["page"] == start["page"] else next_start["page"] - 1
      elif mixed_subject_pdf and expected_last == start["number"]:
        end_page = start["page"]
      else:
        end_page = len(pdf.pages) - 1
      for page_index in range(start["page"], end_page + 1):
        page = pdf.pages[page_index]
        top = start["top"] if page_index == start["page"] else 0
        bottom = next_start["top"] if next_start and page_index == next_start["page"] else page.height
        text = crop_text(page, top, bottom, (preflight or {}).get("headersFooters"))
        if text.strip():
          pieces.append(text)
          pages.append(page_index + 1)
        image_count += count_images(page, top, bottom)
        bold, italic, fonts = word_style_counts(page, top, bottom)
        bold_count += bold
        italic_count += italic
        question_words.extend(extract_pdf_words(page, top, bottom, page_index + 1))
        question_tables.extend(extract_pdf_tables(page, top, bottom, page_index + 1))
        question_formulas.extend(detect_pdf_fractions(page, top, bottom, page_index + 1))
        for font in fonts:
          if font not in font_samples:
            font_samples.append(font)
      text = trim_pdf_question_text(start["number"], "\n".join(pieces).strip())
      result[start["number"]] = PdfQuestion(
        number=start["number"],
        text=text,
        pages=pages,
        image_count=image_count,
        bold_word_count=bold_count,
        italic_word_count=italic_count,
        font_samples=font_samples[:8],
        words=question_words,
        tables=question_tables,
        formulas=question_formulas,
        structure={
          "question_boundary": (preflight or {}).get("segmentationConfidence", 0.99),
          "header_footer_cleaning": ((preflight or {}).get("headersFooters") or {}).get("confidence", 0.65),
          "markerPattern": start.get("pattern"),
        },
      )
    return result


def trim_pdf_question_text(number: int, text: str) -> str:
  matches = list(QUESTION_RE.finditer(text))
  if not matches:
    return clean_pdf_segment_text(re.sub(rf"^\s*0*{number}\s*[.)\-–—]\s*", "", text.strip()))
  start_index = 0
  for match in matches:
    if int(match.group(1)) == number:
      start_index = match.start()
      break
  end_index = len(text)
  for match in matches:
    if match.start() > start_index and int(match.group(1)) != number:
      end_index = match.start()
      break
  return clean_pdf_segment_text(text[start_index:end_index])


def clean_pdf_segment_text(text: str) -> str:
  lines = []
  for line in text.splitlines():
    stripped = collapse_spaces(line)
    if not stripped:
      continue
    upper = strip_accents(stripped).upper()
    compact = compact_structure(stripped)
    if upper.startswith("(PROVA DE MATEMATICA DO CONCURSO"):
      continue
    if "CONCURSODEADMISSAO" in compact and ("PROVADEMATEMATICA" in compact or "ENSINOFUNDAMENTAL" in compact):
      continue
    if upper.startswith("CONFERIDO POR") or upper.startswith("PÁGINA ") or upper.startswith("PAGINA "):
      continue
    if re.fullmatch(r"_+", stripped):
      continue
    if re.fullmatch(r"Pagina\s+\d+", strip_accents(stripped), re.IGNORECASE):
      continue
    if stripped in {"MÚLTIPLA-ESCOLHA", "MULTIPLA-ESCOLHA"}:
      continue
    lines.append(line)
  return "\n".join(lines).strip()


def block_text(block: dict[str, Any]) -> str:
  kind = block.get("type")
  if kind == "text":
    return block.get("text", "")
  if kind == "formula":
    return f"\\({block.get('latex', '')}\\)"
  if kind == "script":
    return f"{block.get('base', '')}{block.get('value', '')}"
  if kind == "table":
    if block.get("content"):
      return "".join(block_text(item) for item in block["content"])
    return block.get("data", "")
  if kind == "image":
    return "[imagem]"
  if kind == "pending-media":
    return "[midia pendente]"
  return ""


def catalog_text(question: dict[str, Any]) -> str:
  blocks = question.get("contentBlocks") or []
  alt_blocks = question.get("alternativeBlocks") or []
  if blocks:
    parts = [block_text(block) for block in blocks]
    for group in alt_blocks:
      parts.extend(block_text(block) for block in group)
    return "\n".join(part for part in parts if part.strip())
  return question.get("content", "")


def count_catalog_formatting(question: dict[str, Any]) -> dict[str, int]:
  counts = {"bold": 0, "italic": 0, "underline": 0}
  for block in [*(question.get("contentBlocks") or []), *[item for group in (question.get("alternativeBlocks") or []) for item in group]]:
    if block.get("type") != "text":
      continue
    for segment in block.get("segments") or []:
      for key in counts:
        if segment.get(key):
          counts[key] += len(segment.get("text", "").split()) or 1
  return counts


def catalog_media_counts(question: dict[str, Any]) -> dict[str, int]:
  blocks = [*(question.get("contentBlocks") or []), *[item for group in (question.get("alternativeBlocks") or []) for item in group]]
  table_inline_blocks = [item for block in blocks if block.get("type") == "table" for item in (block.get("content") or [])]
  return {
    "images": sum(len(block.get("urls") or []) for block in blocks if block.get("type") == "image"),
    "pendingMedia": sum(1 for block in blocks if block.get("type") == "pending-media"),
    "formulas": sum(1 for block in [*blocks, *table_inline_blocks] if block.get("type") in {"formula", "script"}),
    "tables": sum(1 for block in blocks if block.get("type") == "table"),
  }


def catalog_tables(question: dict[str, Any]) -> list[SemanticTable]:
  blocks = [*(question.get("contentBlocks") or []), *[item for group in (question.get("alternativeBlocks") or []) for item in group]]
  return [parse_simplequest_table(block) for block in blocks if block.get("type") == "table"]


def catalog_formula_structures(question: dict[str, Any]) -> list[dict[str, Any]]:
  formulas: list[dict[str, Any]] = []
  for table_index, table in enumerate(catalog_tables(question)):
    for cell in table_visible_cells(table):
      for formula in cell.formula_structures:
        formulas.append({
          **comparable_formula(formula),
          "context": "table",
          "table": table_index,
          "row": cell.row,
          "column": cell.column,
        })
  for block in question.get("contentBlocks") or []:
    if block.get("type") == "formula":
      parsed = parse_latex_fraction(block.get("latex", ""))
      formulas.append({**comparable_formula(parsed or {"type": "unsupported", "latex": block.get("latex", "")}), "context": "stem"})
  for group_index, group in enumerate(question.get("alternativeBlocks") or []):
    for block in group:
      if block.get("type") == "formula":
        parsed = parse_latex_fraction(block.get("latex", ""))
        formulas.append({**comparable_formula(parsed or {"type": "unsupported", "latex": block.get("latex", "")}), "context": "alternative", "option": chr(ord("A") + group_index)})
  return formulas


def table_visible_cells(table: SemanticTable) -> list[SemanticTableCell]:
  return [cell for cell in table.cells if not cell.merged and not cell.ghost]


def cell_compare_text(cell: SemanticTableCell) -> str:
  if cell.formulas:
    value = cell.text
    for formula in cell.formulas:
      value = value.replace(f"\\({formula}\\)", "").replace(formula, "")
    return collapse_spaces(value)
  if cell.formula_structures and loose_text(cell.text) == loose_text(" ".join(
    f"{item.get('numerator', '')} {item.get('denominator', '')}"
    for item in cell.formula_structures
    if item.get("type") == "fraction"
  )):
    return ""
  return collapse_spaces(cell.text)


def table_text_signature(table: SemanticTable) -> str:
  pieces: list[str] = []
  for cell in table_visible_cells(table):
    pieces.append(cell_compare_text(cell))
    pieces.extend(
      f"{item.get('numerator', '')} {item.get('denominator', '')}"
      for item in cell.formula_structures
      if item.get("type") == "fraction"
    )
  return loose_text(" ".join(piece for piece in pieces if piece))


def table_cell_matrix(table: SemanticTable) -> list[list[str]]:
  matrix = [["" for _ in range(table.columns)] for _ in range(table.rows)]
  for cell in table_visible_cells(table):
    if cell.row < table.rows and cell.column < table.columns:
      matrix[cell.row][cell.column] = cell_compare_text(cell)
  return matrix


def table_formula_matrix(table: SemanticTable) -> list[list[list[dict[str, Any]]]]:
  matrix = [[[] for _ in range(table.columns)] for _ in range(table.rows)]
  for cell in table_visible_cells(table):
    if cell.row < table.rows and cell.column < table.columns:
      matrix[cell.row][cell.column] = cell.formula_structures
  return matrix


def comparable_formula(formula: dict[str, Any]) -> dict[str, Any]:
  if formula.get("type") == "fraction":
    return {
      "type": "fraction",
      "numerator": collapse_spaces(str(formula.get("numerator", ""))),
      "denominator": collapse_spaces(str(formula.get("denominator", ""))),
    }
  return {"type": str(formula.get("type", "unsupported")), "latex": formula.get("latex")}


def compare_cell_formulas(catalog_table: SemanticTable, pdf_table: SemanticTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
  catalog_formulas = table_formula_matrix(catalog_table)
  pdf_formulas = table_formula_matrix(pdf_table)
  verified: list[dict[str, Any]] = []
  differences: list[dict[str, Any]] = []
  unverified: list[dict[str, Any]] = []
  for row_index in range(catalog_table.rows):
    for column_index in range(catalog_table.columns):
      left = [comparable_formula(item) for item in catalog_formulas[row_index][column_index]]
      right = [comparable_formula(item) for item in pdf_formulas[row_index][column_index]]
      if not left and not right:
        continue
      if any(item.get("type") == "unsupported" for item in left):
        unverified.append({"row": row_index, "column": column_index, "catalog": left, "reason": "unsupported-catalog-formula"})
        continue
      if left == right:
        verified.append({"row": row_index, "column": column_index, "formulas": left})
      elif right:
        differences.append({"row": row_index, "column": column_index, "catalog": left, "pdf": right})
      else:
        unverified.append({"row": row_index, "column": column_index, "catalog": left, "reason": "no-pdf-formula-detected"})
  return verified, differences, unverified


def compare_table_pair(catalog_table: SemanticTable, pdf_table: SemanticTable) -> dict[str, Any]:
  catalog_matrix = table_cell_matrix(catalog_table)
  pdf_matrix = table_cell_matrix(pdf_table)
  if catalog_table.rows != pdf_table.rows or catalog_table.columns != pdf_table.columns:
    return {
      "status": "uncertain",
      "reason": "shape-mismatch",
      "catalogShape": [catalog_table.rows, catalog_table.columns],
      "pdfShape": [pdf_table.rows, pdf_table.columns],
      "confidence": "media",
    }
  cell_diffs: list[dict[str, Any]] = []
  for row_index in range(catalog_table.rows):
    for column_index in range(catalog_table.columns):
      catalog_text = catalog_matrix[row_index][column_index]
      pdf_text = pdf_matrix[row_index][column_index]
      if loose_text(catalog_text) != loose_text(pdf_text):
        cell_diffs.append({
          "row": row_index,
          "column": column_index,
          "catalog": catalog_text,
          "pdf": pdf_text,
        })
  if cell_diffs:
    return {"status": "difference", "reason": "cell-text", "confidence": "alta", "cells": cell_diffs[:8]}
  formulas_verified, formula_diffs, formula_unverified = compare_cell_formulas(catalog_table, pdf_table)
  if formula_diffs:
    return {"status": "difference", "reason": "cell-formula", "confidence": "alta", "formulas": formula_diffs[:8]}
  if formula_unverified:
    return {
      "status": "unverified",
      "reason": "cell-formula-unverified",
      "confidence": "media",
      "formulas": formula_unverified[:8],
      "verifiedFormulas": formulas_verified,
    }
  merged_cells = [cell for cell in table_visible_cells(catalog_table) if cell.row_span > 1 or cell.col_span > 1]
  if merged_cells:
    return {"status": "verified", "confidence": "media", "reason": "text-verified-merge-not-fully-compared", "verifiedFormulas": formulas_verified}
  return {"status": "verified", "confidence": min(catalog_table.confidence, pdf_table.confidence, key={"baixa": 0, "media": 1, "alta": 2}.get), "verifiedFormulas": formulas_verified}


def audit_tables(question: dict[str, Any], pdf_question: PdfQuestion) -> dict[str, Any]:
  catalog_semantic = catalog_tables(question)
  if not catalog_semantic:
    if pdf_question.tables:
      return {
        "status": "uncertain",
        "tables": [],
        "summary": {"catalog": 0, "pdf": len(pdf_question.tables)},
        "reason": "pdf-table-like-geometry-without-catalog-table",
      }
    return {"status": "not_applicable", "tables": [], "summary": {"catalog": 0, "pdf": len(pdf_question.tables)}}
  unmatched_pdf = list(pdf_question.tables)
  results: list[dict[str, Any]] = []
  for index, catalog_table in enumerate(catalog_semantic):
    best_index = -1
    best_score = 0.0
    catalog_signature = table_text_signature(catalog_table)
    for pdf_index, pdf_table in enumerate(unmatched_pdf):
      score = similarity(catalog_signature, table_text_signature(pdf_table))
      if score > best_score:
        best_score = score
        best_index = pdf_index
    if best_index < 0 or best_score < 0.74:
      results.append({
        "index": index,
        "status": "unverified",
        "reason": "no-confident-pdf-table-match",
        "catalogShape": [catalog_table.rows, catalog_table.columns],
        "bestScore": round(best_score, 4),
      })
      continue
    pdf_table = unmatched_pdf.pop(best_index)
    comparison = compare_table_pair(catalog_table, pdf_table)
    results.append({
      "index": index,
      **comparison,
      "catalogShape": comparison.get("catalogShape", [catalog_table.rows, catalog_table.columns]),
      "pdfShape": comparison.get("pdfShape", [pdf_table.rows, pdf_table.columns]),
      "matchScore": round(best_score, 4),
      "pdfPage": pdf_table.page,
    })
  statuses = [result["status"] for result in results]
  if "difference" in statuses:
    status = "difference"
  elif "uncertain" in statuses:
    status = "uncertain"
  elif "unverified" in statuses:
    status = "unverified"
  else:
    status = "verified"
  return {
    "status": status,
    "tables": results,
    "summary": {"catalog": len(catalog_semantic), "pdf": len(pdf_question.tables)},
  }


def audit_formulas(question: dict[str, Any], pdf_question: PdfQuestion, table_audit: dict[str, Any]) -> dict[str, Any]:
  catalog_formulas = catalog_formula_structures(question)
  if not catalog_formulas:
    return {"status": "not_applicable", "summary": {"catalog": 0, "pdfDetected": len(pdf_question.formulas)}, "formulas": []}

  verified: list[dict[str, Any]] = []
  differences: list[dict[str, Any]] = []
  unverified: list[dict[str, Any]] = []
  uncertain: list[dict[str, Any]] = []
  table_verified: list[dict[str, Any]] = []
  table_unverified: list[dict[str, Any]] = []
  table_differences: list[dict[str, Any]] = []

  for table in table_audit.get("tables", []):
    for item in table.get("verifiedFormulas") or []:
      for formula in item.get("formulas") or []:
        table_verified.append({
          **comparable_formula(formula),
          "context": "table",
          "table": table.get("index"),
          "row": item.get("row"),
          "column": item.get("column"),
          "confidence": table.get("confidence", "media"),
        })
    if table.get("reason") == "cell-formula-unverified":
      table_unverified.extend(table.get("formulas") or [])
    if table.get("reason") == "cell-formula":
      table_differences.extend(table.get("formulas") or [])

  for formula in catalog_formulas:
    if formula.get("type") == "unsupported":
      unverified.append({**formula, "reason": "unsupported-catalog-formula"})
      continue
    if formula.get("context") == "table":
      match = next((
        item for item in table_verified
        if item.get("table") == formula.get("table")
        and item.get("row") == formula.get("row")
        and item.get("column") == formula.get("column")
        and comparable_formula(item) == comparable_formula(formula)
      ), None)
      if match:
        verified.append({**formula, "confidence": match.get("confidence", "alta")})
        continue
      diff = next((
        item for item in table_differences
        if item.get("row") == formula.get("row") and item.get("column") == formula.get("column")
      ), None)
      if diff:
        differences.append({**formula, "pdf": diff.get("pdf"), "reason": "table-cell-formula-difference"})
      else:
        unresolved = next((
          item for item in table_unverified
          if item.get("row") == formula.get("row") and item.get("column") == formula.get("column")
        ), None)
        unverified.append({**formula, "reason": (unresolved or {}).get("reason", "table-cell-formula-unverified")})
      continue

    pdf_match = next((
      item for item in pdf_question.formulas
      if comparable_formula(item) == comparable_formula(formula)
    ), None)
    if pdf_match:
      verified.append({**formula, "confidence": pdf_match.get("confidence", "alta"), "page": pdf_match.get("page")})
    else:
      unverified.append({**formula, "reason": "no-pdf-formula-detected"})

  if differences:
    status = "difference"
  elif uncertain:
    status = "uncertain"
  elif unverified:
    status = "unverified"
  else:
    status = "verified"
  return {
    "status": status,
    "summary": {
      "catalog": len(catalog_formulas),
      "pdfDetected": len(pdf_question.formulas),
      "verified": len(verified),
      "difference": len(differences),
      "unverified": len(unverified),
      "uncertain": len(uncertain),
    },
    "formulas": {
      "verified": verified,
      "difference": differences,
      "unverified": unverified,
      "uncertain": uncertain,
    },
  }


def parse_alternatives(text: str) -> dict[str, str]:
  parsed: dict[str, str] = {}
  for match in ALT_RE.finditer(text):
    option = (match.group(1) or match.group(2) or "").upper()
    content = match.group(3) or ""
    if option:
      parsed[option] = collapse_spaces(content)
  return parsed


def compact_question_line(line: str) -> str:
  return re.sub(r"^\s*(?:QUEST[ÃA]O|Q\s*UEST[ÃA]O)\s+\d{1,2}\s*[-–—.]?\s*", "", line, flags=re.IGNORECASE)


def normalized_pdf_lines_for_alternatives(text: str) -> list[str]:
  lines: list[str] = []
  for raw in text.splitlines():
    line = collapse_spaces(compact_question_line(raw))
    if not line:
      continue
    if lines and re.fullmatch(r"[.,;:!?]+", line):
      lines[-1] = collapse_spaces(f"{lines[-1]}{line}")
      continue
    lines.append(line)
  return lines


def infer_unmarked_alternatives(text: str, catalog_alts: dict[str, str]) -> dict[str, Any]:
  expected = len(catalog_alts)
  if expected < 2:
    return {"alternatives": {}, "stem": text, "confidence": 0.0, "method": "none"}
  lines = normalized_pdf_lines_for_alternatives(text)
  if len(lines) <= expected:
    return {"alternatives": {}, "stem": text, "confidence": 0.0, "method": "insufficient-lines"}
  candidate_lines = lines[-expected:]
  options = list(catalog_alts.keys())[:expected]
  scores = [
    similarity(loose_text(comparable_text(catalog_alts.get(option, ""))), loose_text(comparable_text(candidate)))
    for option, candidate in zip(options, candidate_lines)
  ]
  average = sum(scores) / len(scores) if scores else 0.0
  minimum = min(scores) if scores else 0.0
  if average < 0.72 or minimum < 0.45:
    return {
      "alternatives": {},
      "stem": text,
      "confidence": round(average, 4),
      "method": "suffix-lines-rejected",
      "scores": [round(score, 4) for score in scores],
    }
  stem = "\n".join(lines[:-expected])
  return {
    "alternatives": {option: candidate for option, candidate in zip(options, candidate_lines)},
    "stem": stem,
    "confidence": round(min(0.73, average), 4),
    "method": "suffix-lines",
    "scores": [round(score, 4) for score in scores],
  }


def pdf_alternative_structure(text: str, catalog_alts: dict[str, str] | None = None) -> dict[str, Any]:
  explicit = parse_alternatives(text)
  if explicit:
    first_alt = re.search(r"(?m)^\s*(?:[A-E]\s*(?:\(\s*\)|[).:\-–—])|\(\s*[A-E]\s*\))\s*", text)
    stem = text[:first_alt.start()] if first_alt else text
    return {"alternatives": explicit, "stem": stem, "confidence": 0.95, "method": "explicit-marker"}
  if catalog_alts:
    return infer_unmarked_alternatives(text, catalog_alts)
  return {"alternatives": {}, "stem": text, "confidence": 0.0, "method": "none"}


def catalog_alternatives(question: dict[str, Any]) -> dict[str, str]:
  options = ["A", "B", "C", "D", "E"]
  answer_type = question.get("answerType") or "ABCDE"
  if answer_type == "ABCD":
    options = ["A", "B", "C", "D"]
  elif answer_type == "CE":
    options = ["C", "E"]
  groups = question.get("alternativeBlocks") or []
  if groups:
    return {
      option: collapse_spaces(" ".join(block_text(block) for block in groups[index]))
      for index, option in enumerate(options)
      if index < len(groups) and collapse_spaces(" ".join(block_text(block) for block in groups[index]))
    }
  alternatives = question.get("alternatives") or []
  if alternatives:
    return {
      option: collapse_spaces(str(alternatives[index]))
      for index, option in enumerate(options)
      if index < len(alternatives) and str(alternatives[index]).strip()
    }
  return parse_alternatives(question.get("content", ""))


def catalog_alternatives_are_media(question: dict[str, Any]) -> bool:
  groups = question.get("alternativeBlocks") or []
  if not groups:
    return False
  media_groups = 0
  for group in groups:
    meaningful = [block for block in group if block_text(block).strip()]
    if meaningful and all(block.get("type") in {"image", "pending-media"} for block in meaningful):
      media_groups += 1
  return media_groups >= 2 and media_groups == len(groups)


def token_key(value: str) -> str:
  return strip_accents(normalize_pdf_text(value)).lower()


def word_tokens(value: str) -> list[str]:
  return re.findall(r"[\wÀ-ÿ]+(?:[.,]\d+)?%?|[^\w\s]", normalize_pdf_text(value), flags=re.UNICODE)


def catalog_text_parts(question: dict[str, Any]) -> list[dict[str, Any]]:
  parts: list[dict[str, Any]] = []
  blocks = question.get("contentBlocks") or []
  if blocks:
    stem = "\n".join(block_text(block) for block in blocks if block_text(block).strip())
  else:
    stem = question.get("stem") or question.get("content", "")
  parts.append({"role": "stem", "option": None, "text": stem})
  for option, text in catalog_alternatives(question).items():
    parts.append({"role": "alternative", "option": option, "text": text})
  return parts


def pdf_text_parts(pdf_question: PdfQuestion, catalog_alts: dict[str, str] | None = None) -> list[dict[str, Any]]:
  structure = pdf_alternative_structure(pdf_question.text, catalog_alts)
  alternatives = structure["alternatives"]
  stem = structure["stem"]
  parts = [{"role": "stem", "option": None, "text": stem}]
  for option, text in alternatives.items():
    parts.append({"role": "alternative", "option": option, "text": text})
  return parts


def catalog_style_tokens_from_text(text: str, role: str, option: str | None, styles: dict[str, bool]) -> list[AuditToken]:
  result: list[AuditToken] = []
  for raw in word_tokens(text):
    normalized = token_key(raw)
    if not re.search(r"[\wÀ-ÿ]", raw, flags=re.UNICODE):
      continue
    result.append(AuditToken(
      text=raw,
      normalized=normalized,
      role=role,
      option=option,
      bold=bool(styles.get("bold")),
      italic=bool(styles.get("italic")),
      underline=bool(styles.get("underline")),
    ))
  return result


def catalog_style_tokens(question: dict[str, Any]) -> list[AuditToken]:
  tokens: list[AuditToken] = []
  for block in question.get("contentBlocks") or []:
    if block.get("type") != "text":
      continue
    segments = block.get("segments") or [{"text": block.get("text", "")}]
    for segment in segments:
      tokens.extend(catalog_style_tokens_from_text(segment.get("text", ""), "stem", None, segment))
  for index, group in enumerate(question.get("alternativeBlocks") or []):
    option = chr(ord("A") + index)
    for block in group:
      if block.get("type") != "text":
        continue
      segments = block.get("segments") or [{"text": block.get("text", "")}]
      for segment in segments:
        tokens.extend(catalog_style_tokens_from_text(segment.get("text", ""), "alternative", option, segment))
  return tokens


def pdf_style_tokens(pdf_question: PdfQuestion) -> list[AuditToken]:
  return [
    AuditToken(
      text=word.text,
      normalized=token_key(word.text),
      role="unknown",
      option=None,
      bold=word.bold,
      italic=word.italic,
      underline=word.underline,
    )
    for word in pdf_question.words
    if re.search(r"[\wÀ-ÿ]", word.text, flags=re.UNICODE)
  ]


def diff_context(value: str, start: int, end: int, width: int = 46) -> str:
  left = max(0, start - width)
  right = min(len(value), end + width)
  return collapse_spaces(value[left:right])


def artifact_context(value: str) -> bool:
  lowered = strip_accents(value).lower()
  return any(marker in lowered for marker in ["[imagem]", "[midia pendente]", "\\frac", "\\(", "\\)", "figura ilustrativa"])


def table_syntax_context(value: str) -> bool:
  if "|" not in value:
    return False
  before, _, after = value.partition("|")
  return bool(before.strip() or after.strip())


def formula_noise_diff(catalog_piece: str, pdf_piece: str, catalog_context: str, pdf_context: str) -> bool:
  if artifact_context(catalog_context) or artifact_context(pdf_context):
    return True
  if not catalog_piece.strip() and re.fullmatch(r"\d+(?:\s+\d+)?", pdf_piece.strip()):
    return True
  if not catalog_piece.strip() and re.fullmatch(r"\d+\s+[\wÀ-ÿ]\s*\(\s*\)", pdf_piece.strip(), flags=re.UNICODE):
    return True
  return False


def classify_local_text_diff(catalog_piece: str, pdf_piece: str) -> tuple[str, str]:
  catalog_clean = collapse_spaces(catalog_piece)
  pdf_clean = collapse_spaces(pdf_piece)
  if catalog_clean and pdf_clean and compact_number(catalog_clean) == compact_number(pdf_clean) and catalog_clean != pdf_clean:
    return "number-spacing-localized", "alta"
  if catalog_clean and pdf_clean and strip_accents(catalog_clean).lower() == strip_accents(pdf_clean).lower() and catalog_clean != pdf_clean:
    return "capitalization-localized", "alta"
  punctuation = set(PUNCTUATION)
  if catalog_clean and all(char in punctuation for char in catalog_clean) and not pdf_clean:
    return "punctuation-localized", "alta"
  if pdf_clean and all(char in punctuation for char in pdf_clean) and not catalog_clean:
    return "punctuation-localized", "alta"
  if catalog_clean and pdf_clean and all(char in punctuation for char in catalog_clean + pdf_clean):
    return "punctuation-localized", "alta"
  return "text-localized", "media" if len(catalog_clean) + len(pdf_clean) < 80 else "baixa"


def localized_text_differences(catalog: str, pdf: str, role: str, option: str | None, limit: int = 8) -> list[dict[str, Any]]:
  catalog_cmp = comparable_text(catalog)
  pdf_cmp = comparable_text(pdf)
  matcher = SequenceMatcher(None, catalog_cmp, pdf_cmp)
  differences: list[dict[str, Any]] = []
  for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "equal":
      continue
    catalog_piece = catalog_cmp[i1:i2]
    pdf_piece = pdf_cmp[j1:j2]
    if not catalog_piece.strip() and not pdf_piece.strip():
      continue
    if catalog_piece.strip() == pdf_piece.strip():
      continue
    catalog_context = diff_context(catalog_cmp, i1, i2)
    pdf_context = diff_context(pdf_cmp, j1, j2)
    if table_syntax_context(catalog_piece) or table_syntax_context(catalog_context):
      continue
    if artifact_context(catalog_piece) or artifact_context(catalog_context) or artifact_context(pdf_piece):
      continue
    if formula_noise_diff(catalog_piece, pdf_piece, catalog_context, pdf_context):
      continue
    diff_type, level = classify_local_text_diff(catalog_piece, pdf_piece)
    if diff_type == "punctuation-localized" and detect_number_spacing(catalog_context, pdf_context):
      diff_type = "number-spacing-localized"
    differences.append({
      "type": diff_type,
      "confidence": level,
      "role": role,
      "option": option,
      "catalog": catalog_piece.strip(),
      "pdf": pdf_piece.strip(),
      "catalogContext": catalog_context,
      "pdfContext": pdf_context,
    })
    if len(differences) >= limit:
      break
  return differences


def compare_text_by_parts(question: dict[str, Any], pdf_question: PdfQuestion) -> list[dict[str, Any]]:
  differences: list[dict[str, Any]] = []
  catalog_alts = catalog_alternatives(question)
  catalog_parts = {(part["role"], part["option"]): part["text"] for part in catalog_text_parts(question)}
  pdf_parts = {(part["role"], part["option"]): part["text"] for part in pdf_text_parts(pdf_question, catalog_alts)}
  for key, catalog_part in catalog_parts.items():
    pdf_part = pdf_parts.get(key)
    if pdf_part is None:
      continue
    differences.extend(localized_text_differences(catalog_part, pdf_part, key[0], key[1]))
    existing_time_pairs = {
      (diff.get("catalog"), diff.get("pdf"))
      for diff in differences
      if diff.get("type") == "unit-spacing-localized" and diff.get("role") == key[0] and diff.get("option") == key[1]
    }
    for issue in detect_time_unit_spacing(catalog_part, pdf_part):
      pair = (issue["catalog"], issue["pdf"])
      if pair in existing_time_pairs:
        continue
      differences.append({
        "type": "unit-spacing-localized",
        "confidence": issue["confidence"],
        "role": key[0],
        "option": key[1],
        "catalog": issue["catalog"],
        "pdf": issue["pdf"],
        "catalogContext": text_window(catalog_part, issue["catalog"]),
        "pdfContext": text_window(pdf_part, issue["pdf"]),
      })
  return differences


def structural_confidence_for_question(question: dict[str, Any], pdf_question: PdfQuestion) -> dict[str, Any]:
  catalog_alts = catalog_alternatives(question)
  pdf_structure = pdf_alternative_structure(pdf_question.text, catalog_alts)
  pdf_alts = pdf_structure["alternatives"]
  expected_alt_count = len(catalog_alts)
  if expected_alt_count == 0:
    stem_alternatives = 0.9
  elif len(pdf_alts) == expected_alt_count:
    stem_alternatives = float(pdf_structure.get("confidence") or 0.95)
  elif catalog_alternatives_are_media(question):
    stem_alternatives = 0.78
  elif len(pdf_alts) >= max(1, expected_alt_count - 1):
    stem_alternatives = 0.72
  else:
    stem_alternatives = 0.45
  return {
    "question_boundary": float((pdf_question.structure or {}).get("question_boundary", 0.99)),
    "stem_alternatives": round(stem_alternatives, 4),
    "header_footer_cleaning": float((pdf_question.structure or {}).get("header_footer_cleaning", 0.65)),
    "catalog_match": None,
    "pdfAlternativeCount": len(pdf_alts),
    "catalogAlternativeCount": expected_alt_count,
    "alternativeMethod": pdf_structure.get("method"),
    "markerPattern": (pdf_question.structure or {}).get("markerPattern"),
  }


def localized_formatting_differences(question: dict[str, Any], pdf_question: PdfQuestion, limit: int = 20) -> list[dict[str, Any]]:
  catalog_tokens = catalog_style_tokens(question)
  pdf_tokens = pdf_style_tokens(pdf_question)
  matcher = SequenceMatcher(None, [token.normalized for token in catalog_tokens], [token.normalized for token in pdf_tokens])
  raw: list[dict[str, Any]] = []
  for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag != "equal":
      continue
    for offset in range(min(i2 - i1, j2 - j1)):
      catalog_token = catalog_tokens[i1 + offset]
      pdf_token = pdf_tokens[j1 + offset]
      mismatches: list[str] = []
      for style in ["bold", "italic", "underline"]:
        if getattr(catalog_token, style) != getattr(pdf_token, style):
          mismatches.append(style)
      if not mismatches:
        continue
      if "\ufffd" in catalog_token.text or "\ufffd" in pdf_token.text or catalog_token.text in {"□"} or pdf_token.text in {"□"}:
        continue
      if len(catalog_token.text.strip()) == 1 and not catalog_token.text.strip().isupper():
        continue
      if catalog_token.role == "alternative" and len(catalog_token.text.strip()) == 1 and "bold" in mismatches:
        continue
      raw.append({
        "type": "formatting-inline",
        "confidence": "media" if "underline" in mismatches else "alta",
        "role": catalog_token.role,
        "option": catalog_token.option,
        "text": catalog_token.text,
        "_firstIndex": i1 + offset,
        "_lastIndex": i1 + offset,
        "styles": mismatches,
        "catalog": {"bold": catalog_token.bold, "italic": catalog_token.italic, "underline": catalog_token.underline},
        "pdf": {"bold": pdf_token.bold, "italic": pdf_token.italic, "underline": pdf_token.underline},
      })
  merged: list[dict[str, Any]] = []
  for item in raw:
    previous = merged[-1] if merged else None
    if (
      previous
      and previous.get("role") == item.get("role")
      and previous.get("option") == item.get("option")
      and previous.get("styles") == item.get("styles")
      and previous.get("catalog") == item.get("catalog")
      and previous.get("pdf") == item.get("pdf")
      and previous.get("_lastIndex") == item.get("_firstIndex", -2) - 1
      and len(str(previous.get("text", ""))) < 180
    ):
      previous["text"] = f"{previous['text']} {item['text']}"
      previous["_lastIndex"] = item["_lastIndex"]
      continue
    merged.append(item)
    if len(merged) >= limit:
      break
  for item in merged:
    item.pop("_firstIndex", None)
    item.pop("_lastIndex", None)
  return merged


def initial_component_statuses(media: dict[str, int]) -> dict[str, dict[str, Any]]:
  statuses: dict[str, dict[str, Any]] = {}
  for component in COMPONENTS:
    statuses[component] = {"status": "verified", "notes": []}
  if media["tables"]:
    statuses["table"] = {"status": "unverified", "notes": ["Tabela presente; comparacao semantica de celulas ainda nao implementada."]}
  else:
    statuses["table"] = {"status": "not_applicable", "notes": []}
  if media["formulas"]:
    statuses["formula"] = {"status": "unverified", "notes": ["Formula presente; comparacao matematica/visual ainda nao implementada."]}
  else:
    statuses["formula"] = {"status": "not_applicable", "notes": []}
  if media["images"] or media["pendingMedia"]:
    note = "Midia presente; comparacao visual ainda nao implementada."
    if media["pendingMedia"]:
      note = "Midia pendente presente no catalogo."
    statuses["media"] = {"status": "unverified", "notes": [note]}
  else:
    statuses["media"] = {"status": "not_applicable", "notes": []}
  return statuses


def mark_component(statuses: dict[str, dict[str, Any]], component: str, status: str, note: str | None = None) -> None:
  current = statuses[component]["status"]
  priority = {"not_applicable": 0, "verified": 1, "unverified": 2, "uncertain": 3, "difference": 4}
  if priority[status] >= priority[current]:
    statuses[component]["status"] = status
  if note and note not in statuses[component]["notes"]:
    statuses[component]["notes"].append(note)


def set_component(statuses: dict[str, dict[str, Any]], component: str, status: str, note: str | None = None) -> None:
  statuses[component]["status"] = status
  if note and note not in statuses[component]["notes"]:
    statuses[component]["notes"].append(note)


def apply_capability_mask(component_statuses: dict[str, dict[str, Any]], capabilities: dict[str, bool] | None) -> None:
  # A component the extraction layer cannot observe must never end as verified,
  # difference or not_applicable just because the adapter returned [] or 0.
  if not capabilities:
    return
  for component, capability in capabilities.items():
    if capability is False and component in component_statuses:
      set_component(component_statuses, component, "unverified", "Componente nao observavel pela camada de extracao (capability=false).")


def component_for_difference(diff: dict[str, Any]) -> str:
  diff_type = diff.get("type")
  if diff_type == "punctuation-localized":
    return "punctuation"
  if diff_type == "capitalization-localized":
    return "capitalization"
  if diff_type == "formatting-inline":
    return "inlineFormatting"
  if diff_type == "alternatives-count":
    return "alternatives"
  if diff_type == "table-semantic":
    return "table"
  if diff_type == "formula-semantic":
    return "formula"
  if diff.get("role") == "alternative":
    return "alternatives"
  return "text"


def global_status(component_statuses: dict[str, dict[str, Any]], association_confidence: str) -> str:
  if association_confidence != "alta":
    return "uncertain"
  values = [item["status"] for item in component_statuses.values()]
  if "difference" in values:
    return "difference"
  if "uncertain" in values:
    return "uncertain"
  if "unverified" in values:
    return "partially_verified"
  return "verified"


def count_punctuation(value: str) -> dict[str, int]:
  return {char: value.count(char) for char in [".", ":", ";", ",", "?"]}


def number_forms(value: str) -> set[str]:
  return {match.group(0) for match in NUMBER_RE.finditer(value)}


def compact_number(value: str) -> str:
  return re.sub(r"(?<=\d)[ .](?=\d{3}\b)", "", value)


def detect_number_spacing(catalog: str, pdf: str) -> list[dict[str, str]]:
  issues: list[dict[str, str]] = []
  catalog_numbers = number_forms(catalog)
  pdf_numbers = number_forms(pdf)
  by_compact_catalog = {compact_number(number): number for number in catalog_numbers}
  by_compact_pdf = {compact_number(number): number for number in pdf_numbers}
  for compact, left in by_compact_catalog.items():
    right = by_compact_pdf.get(compact)
    if right and left != right:
      issues.append({"catalog": left, "pdf": right, "confidence": "alta"})
  return issues


def time_unit_expressions(value: str) -> dict[str, str]:
  expressions: dict[str, str] = {}
  pattern = re.compile(r"\b\d+\s*h(?:\s*\d+\s*min)?(?:\s*\d+\s*s)?\b", re.IGNORECASE)
  for match in pattern.finditer(value):
    raw = collapse_spaces(match.group(0))
    if len(re.findall(r"(?:h|min|s)", raw, flags=re.IGNORECASE)) < 2:
      continue
    compact = re.sub(r"\s+", "", raw).lower()
    expressions.setdefault(compact, raw)
  return expressions


def detect_time_unit_spacing(catalog: str, pdf: str) -> list[dict[str, str]]:
  issues: list[dict[str, str]] = []
  catalog_times = time_unit_expressions(catalog)
  pdf_times = time_unit_expressions(pdf)
  for compact, catalog_raw in catalog_times.items():
    pdf_raw = pdf_times.get(compact)
    if pdf_raw and catalog_raw != pdf_raw:
      issues.append({"catalog": catalog_raw, "pdf": pdf_raw, "confidence": "alta"})
  return issues


def detect_case_differences(catalog: str, pdf: str, limit: int = 10) -> list[dict[str, str]]:
  issues: list[dict[str, str]] = []
  catalog_words = re.findall(r"\b[\wÀ-ÿ]+\b", catalog)
  pdf_words = re.findall(r"\b[\wÀ-ÿ]+\b", pdf)
  catalog_keys = [strip_accents(word).lower() for word in catalog_words]
  pdf_keys = [strip_accents(word).lower() for word in pdf_words]
  matcher = SequenceMatcher(None, catalog_keys, pdf_keys)
  for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag != "equal":
      continue
    for offset in range(min(i2 - i1, j2 - j1)):
      left = catalog_words[i1 + offset]
      right = pdf_words[j1 + offset]
      if left != right and left.lower() == right.lower():
        issues.append({"catalog": left, "pdf": right, "confidence": "alta"})
        if len(issues) >= limit:
          return issues
  return issues


def text_window(value: str, needle: str, width: int = 80) -> str:
  position = value.find(needle)
  if position < 0:
    return ""
  start = max(0, position - width)
  end = min(len(value), position + len(needle) + width)
  return value[start:end]


def sample_differences(catalog: str, pdf: str, limit: int = 6) -> list[dict[str, str]]:
  matcher = SequenceMatcher(None, catalog, pdf)
  samples: list[dict[str, str]] = []
  for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "equal":
      continue
    left = catalog[i1:i2].strip()
    right = pdf[j1:j2].strip()
    if not left and not right:
      continue
    samples.append({
      "type": tag,
      "catalog": left[:180],
      "pdf": right[:180],
      "confidence": "media" if len(left) + len(right) < 80 else "baixa",
    })
    if len(samples) >= limit:
      break
  return samples


def compare_question(
  question: dict[str, Any],
  pdf_question: PdfQuestion | None,
  preflight: dict[str, Any] | None = None,
  question_eligible: bool | None = None,
) -> dict[str, Any]:
  catalog_raw = catalog_text(question)
  catalog_cmp = comparable_text(catalog_raw)
  media = catalog_media_counts(question)
  component_statuses = initial_component_statuses(media)
  if not pdf_question:
    for component in COMPONENTS:
      mark_component(component_statuses, component, "uncertain", "Questao nao associada ao PDF.")
    return {
      "id": question["id"],
      "number": question["number"],
      "associationConfidence": "baixa",
      "status": "missing-in-pdf",
      "globalStatus": "uncertain",
      "componentStatus": component_statuses,
      "differences": [{"type": "association", "severity": "high", "confidence": "alta", "message": "Marcador da questao nao encontrado no PDF."}],
    }

  if question_eligible is False:
    for component in COMPONENTS:
      mark_component(component_statuses, component, "uncertain", "Questao nao elegivel para auditoria de conteudo na camada OCR.")
    if pdf_question.capabilities:
      apply_capability_mask(component_statuses, pdf_question.capabilities)
    return {
      "id": question["id"],
      "number": question["number"],
      "associationConfidence": "baixa",
      "status": "ocr-ineligible",
      "globalStatus": "uncertain",
      "gate": "individual_eligibility",
      "proofStatus": (preflight or {}).get("status"),
      "componentStatus": component_statuses,
      "differences": [],
      "needsHumanReview": True,
    }

  if question_eligible is None and preflight and preflight.get("status") != "ready_for_audit":
    for component in COMPONENTS:
      mark_component(component_statuses, component, "uncertain", "Preflight estrutural da prova nao atingiu confianca suficiente para diff de conteudo.")
    return {
      "id": question["id"],
      "number": question["number"],
      "associationConfidence": "baixa",
      "status": "preflight-not-ready",
      "globalStatus": "uncertain",
      "componentStatus": component_statuses,
      "structureConfidence": {
        "question_boundary": (preflight or {}).get("segmentationConfidence", 0),
        "stem_alternatives": 0,
        "header_footer_cleaning": ((preflight or {}).get("headersFooters") or {}).get("confidence", 0),
        "catalog_match": 0,
      },
      "differences": [{"type": "association", "severity": "high", "confidence": "alta", "message": "Preflight estrutural da prova bloqueou a comparacao de conteudo."}],
    }

  pdf_cmp = comparable_text(pdf_question.text)
  exact_score = similarity(catalog_cmp, pdf_cmp)
  loose_score = similarity(loose_text(catalog_cmp), loose_text(pdf_cmp))
  structure_confidence = structural_confidence_for_question(question, pdf_question)
  structure_confidence["catalog_match"] = round(loose_score, 4)
  differences: list[dict[str, Any]] = []

  table_audit = audit_tables(question, pdf_question)
  if table_audit["status"] == "verified":
    set_component(component_statuses, "table", "verified", "Tabela verificada por comparacao semantica de celulas.")
  elif table_audit["status"] == "difference":
    mark_component(component_statuses, "table", "difference", "Tabela com divergencia semantica de celula.")
    differences.append({"type": "table-semantic", "confidence": "alta", "tables": table_audit["tables"]})
  elif table_audit["status"] == "uncertain":
    mark_component(component_statuses, "table", "uncertain", "Tabela do PDF reconstruida com baixa confianca.")

  formula_audit = audit_formulas(question, pdf_question, table_audit)
  if formula_audit["status"] == "verified":
    set_component(component_statuses, "formula", "verified", "Formula verificada por estrutura semantica no PDF.")
  elif formula_audit["status"] == "difference":
    mark_component(component_statuses, "formula", "difference", "Formula com divergencia semantica.")
    differences.append({"type": "formula-semantic", "confidence": "alta", "formulas": formula_audit.get("formulas")})
  elif formula_audit["status"] == "uncertain":
    mark_component(component_statuses, "formula", "uncertain", "Formula presente, mas associacao/leitura geometrica esta incerta.")

  localized_diffs: list[dict[str, Any]] = []
  text_structure_ready = structure_confidence["stem_alternatives"] >= 0.74 and structure_confidence["header_footer_cleaning"] >= 0.7
  if text_structure_ready:
    localized_diffs = compare_text_by_parts(question, pdf_question)
    differences.extend(localized_diffs)
  else:
    mark_component(component_statuses, "text", "uncertain", "Separacao estrutural entre enunciado e alternativas ainda nao confiavel.")
    mark_component(component_statuses, "alternatives", "uncertain", "Separacao estrutural entre enunciado e alternativas ainda nao confiavel.")
    mark_component(component_statuses, "inlineFormatting", "uncertain", "Formatacao inline depende de alinhamento textual estruturalmente incerto.")

  if text_structure_ready:
    catalog_enums = ENUMERATION_RE.findall(catalog_cmp)
    pdf_enums = ENUMERATION_RE.findall(pdf_cmp)
    if len(catalog_enums) != len(pdf_enums):
      differences.append({"type": "enumeration-count", "confidence": "alta", "catalog": len(catalog_enums), "pdf": len(pdf_enums)})

  catalog_alts = catalog_alternatives(question)
  pdf_alts = pdf_alternative_structure(pdf_question.text, catalog_alts)["alternatives"]
  media_alternatives = catalog_alternatives_are_media(question)
  if media_alternatives:
    mark_component(component_statuses, "media", "unverified", "Alternativas em midia presentes; conteudo visual ainda nao auditado.")
  if text_structure_ready and len(pdf_alts) and len(catalog_alts) != len(pdf_alts) and not media["tables"] and not media_alternatives:
    differences.append({"type": "alternatives-count", "confidence": "alta", "catalog": len(catalog_alts), "pdf": len(pdf_alts)})

  if media["pendingMedia"]:
    mark_component(component_statuses, "media", "unverified", "Midia pendente exige revisao humana.")

  if text_structure_ready:
    differences.extend(localized_formatting_differences(question, pdf_question))

  if text_structure_ready and exact_score < 0.985 and not localized_diffs and not any(media.values()) and not artifact_context(catalog_cmp) and not artifact_context(pdf_cmp):
    differences.append({"type": "text-samples", "confidence": "media" if loose_score >= 0.94 else "baixa", "samples": sample_differences(catalog_cmp, pdf_cmp)})

  if pdf_question.capabilities:
    differences = [
      diff for diff in differences
      if pdf_question.capabilities.get(component_for_difference(diff), True) is not False
    ]
    apply_capability_mask(component_statuses, pdf_question.capabilities)

  for diff in differences:
    mark_component(component_statuses, component_for_difference(diff), "difference")

  status = global_status(component_statuses, "alta")
  needs_human = status != "verified"
  result = {
    "id": question["id"],
    "number": question["number"],
    "associationConfidence": "alta",
    "pages": pdf_question.pages,
    "scores": {
      "exact": round(exact_score, 4),
      "loose": round(loose_score, 4),
      "textConfidence": confidence(loose_score),
    },
    "globalStatus": status,
    "componentStatus": component_statuses,
    "structureConfidence": structure_confidence,
    "tableAudit": table_audit,
    "formulaAudit": formula_audit,
    "needsHumanReview": needs_human,
    "differences": differences,
  }
  if question_eligible is not None:
    result["gate"] = "individual_eligibility"
    result["proofStatus"] = (preflight or {}).get("status")
  return result


def admission_blocked_question(question: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
  media = catalog_media_counts(question)
  component_statuses = initial_component_statuses(media)
  note = f"Auditoria bloqueada na admissao estrutural: {admission.get('state')}."
  for component in COMPONENTS:
    mark_component(component_statuses, component, "uncertain", note)
  return {
    "id": question["id"],
    "number": question["number"],
    "associationConfidence": "baixa",
    "status": "admission-blocked",
    "globalStatus": "uncertain",
    "componentStatus": component_statuses,
    "structureConfidence": {
      "admission": admission.get("state"),
      "question_boundary": 0,
      "stem_alternatives": 0,
      "header_footer_cleaning": 0,
      "catalog_match": 0,
    },
    "needsHumanReview": True,
    "differences": [],
  }


def markdown_report(result: dict[str, Any]) -> str:
  preflight = result.get("preflight") or {}
  headers = (preflight.get("headersFooters") or {}).get("regions") or []
  admission = result.get("admission") or {}
  lines = [
    f"# Auditoria PDF - {result['school']} {result['year']} ({result.get('catalogState', 'base')})",
    "",
    "Modo: somente leitura. PDF original tratado como fonte canonica; DOCX/catalogo como estrutura auxiliar.",
    "",
    f"- PDF: `{result['pdf']['path']}`",
    f"- Estado do catalogo auditado: {result.get('catalogState', 'base')}",
    f"- Confianca da associacao da prova: {result['pdf']['associationConfidence']}",
    f"- Questoes auditadas: {len(result['questions'])}",
    f"- Questoes para revisao humana: {sum(1 for q in result['questions'] if q.get('needsHumanReview'))}",
    "",
    "## Admissao estrutural",
    "",
    f"- Estado: {admission.get('state', '-')}",
    f"- Classificacao do PDF: {admission.get('classification', '-')}",
    f"- Permitido ao preflight: {admission.get('allowedToPreflight', '-')}",
    f"- Motivo: {admission.get('reason', '-')}",
    f"- Caracteres por pagina: media={admission.get('averageCharsPerPage', '-')} | mediana={admission.get('medianCharsPerPage', '-')}",
    f"- Paginas sem texto: {admission.get('pagesWithoutText', '-')} ({admission.get('pagesWithoutTextRatio', '-')})",
    "",
    "## Preflight estrutural",
    "",
    f"- Status: {preflight.get('status', '-')}",
    f"- Paginas: {preflight.get('pageCount', '-')}",
    f"- Questoes esperadas: {preflight.get('expectedQuestions', '-')}",
    f"- Marcadores detectados: {preflight.get('detectedQuestions', '-')}",
    f"- Confianca de segmentacao: {preflight.get('segmentationConfidence', '-')}",
    f"- Padroes de marcador: {preflight.get('markerPatterns', {})}",
    f"- Questoes ausentes na segmentacao: {preflight.get('missingQuestions', [])}",
    f"- Regioes recorrentes de cabecalho/rodape: {len(headers)}",
    "",
    "## Resumo por questao",
    "",
  ]
  for question in result["questions"]:
    diff_count = len(question.get("differences", []))
    pages = ", ".join(str(page) for page in question.get("pages", [])) or "-"
    score = question.get("scores", {})
    lines.append(f"### Q{question['number']:02d} - `{question['id']}`")
    lines.append(f"- Paginas PDF: {pages}")
    if score:
      lines.append(f"- Similaridade exata: {score['exact']} | flexivel: {score['loose']} | confianca textual: {score['textConfidence']}")
    if question.get("globalStatus"):
      lines.append(f"- Status global: {question.get('globalStatus')}")
    structure = question.get("structureConfidence") or {}
    if structure:
      lines.append(
        "- Confianca estrutural: "
        f"limite={structure.get('question_boundary', '-')} | "
        f"enunciado/alternativas={structure.get('stem_alternatives', '-')} | "
        f"limpeza cabecalho/rodape={structure.get('header_footer_cleaning', '-')} | "
        f"catalogo={structure.get('catalog_match', '-')}"
      )
    components = question.get("componentStatus") or {}
    if components:
      summary = "; ".join(
        f"{COMPONENT_LABELS.get(key, key)}={value.get('status')}"
        for key, value in components.items()
      )
      lines.append(f"- Componentes: {summary}")
    lines.append(f"- Revisao humana: {'sim' if question.get('needsHumanReview') else 'nao'}")
    if not diff_count:
      lines.append("- Divergencias: nenhuma detectada pelo MVP.")
    else:
      lines.append(f"- Divergencias detectadas: {diff_count}")
      for diff in question["differences"][:8]:
        diff_type = diff.get("type", "unknown")
        confidence_level = diff.get("confidence", "-")
        if diff_type == "punctuation-count":
          lines.append(f"  - pontuacao ({confidence_level}): {diff.get('details')}")
        elif diff_type in {"punctuation-localized", "number-spacing-localized", "capitalization-localized", "unit-spacing-localized", "text-localized"}:
          location = diff.get("role", "texto")
          if diff.get("option"):
            location = f"{location} {diff.get('option')}"
          lines.append(
            f"  - {diff_type} ({confidence_level}, {location}): "
            f"catalogo=`{diff.get('catalog')}` pdf=`{diff.get('pdf')}`"
          )
        elif diff_type == "number-spacing":
          lines.append(f"  - espaco em numero ({confidence_level}): {diff.get('details')}")
        elif diff_type == "enumeration-count":
          lines.append(f"  - enumeracoes ({confidence_level}): catalogo={diff.get('catalog')} pdf={diff.get('pdf')}")
        elif diff_type == "capitalization":
          lines.append(f"  - capitalizacao ({confidence_level}): {diff.get('samples')[:3]}")
        elif diff_type == "media-count":
          lines.append(f"  - midia ({confidence_level}): catalogo={diff.get('catalogImages')} pdf={diff.get('pdfImages')}")
        elif diff_type == "formula-review":
          lines.append(f"  - formula ({confidence_level}): {diff.get('catalogFormulaBlocks')} blocos no catalogo; revisar visualmente.")
        elif diff_type == "table-review":
          lines.append(f"  - tabela ({confidence_level}): {diff.get('catalogTableBlocks')} blocos no catalogo; revisar layout.")
        elif diff_type == "text-samples":
          samples = diff.get("samples") or []
          lines.append(f"  - texto ({confidence_level}): {samples[:2]}")
        elif diff_type == "formatting-inline":
          location = diff.get("role", "texto")
          if diff.get("option"):
            location = f"{location} {diff.get('option')}"
          lines.append(
            f"  - formatacao inline ({confidence_level}, {location}): "
            f"`{diff.get('text')}` estilos={diff.get('styles')} catalogo={diff.get('catalog')} pdf={diff.get('pdf')}"
          )
        else:
          lines.append(f"  - {diff_type} ({confidence_level})")
    lines.append("")
  return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
  pdf_root = configured_pdf_root(args)
  if not pdf_root.exists():
    raise SystemExit(f"Raiz externa de PDFs nao encontrada: {pdf_root}")
  base_catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
  revisions: list[dict[str, Any]] = []
  d1_path: str | None = None
  if args.catalog_state == "effective":
    revisions, d1_path = load_revisions_from_d1(Path(args.d1_db) if args.d1_db else None)
    catalog = effective_catalog(base_catalog, revisions)
  else:
    catalog = base_catalog
  questions = [
    question for question in catalog
    if question.get("school") == args.school and int(question.get("year", 0)) == args.year
  ]
  questions.sort(key=lambda item: int(item.get("number", 0)))
  if args.max_questions:
    questions = questions[:args.max_questions]
  if not questions:
    raise SystemExit(f"Nenhuma questao encontrada no catalogo para {args.school} {args.year}")

  pdf_path, pdf_confidence, candidates = find_pdf(pdf_root, args.school, args.year, args.pdf)
  expected_numbers = [int(question["number"]) for question in questions]
  inventory = inspect_pdf(pdf_path, pdf_root)
  admission = admission_decision(inventory)
  if not admission["allowedToPreflight"]:
    audited = [admission_blocked_question(question, admission) for question in questions]
    now = datetime.now(timezone.utc).isoformat()
    return {
      "generatedAt": now,
      "mode": "read-only",
      "catalogState": args.catalog_state,
      "canonicalSource": "PDF original",
      "auxiliarySource": "DOCX/catalogo SimpleQuest",
      "d1": {"path": d1_path, "revisionCount": len(revisions)} if args.catalog_state == "effective" else None,
      "school": args.school,
      "year": args.year,
      "pdfRoot": str(pdf_root),
      "pdf": {
        "path": str(pdf_path),
        "associationConfidence": pdf_confidence,
        "candidates": candidates,
      },
      "admission": admission,
      "preflight": {
        "status": "not_run",
        "reason": f"Bloqueado pela admissao estrutural: {admission['state']}",
        "expectedQuestions": len(expected_numbers),
        "detectedQuestions": 0,
        "segmentationConfidence": 0,
        "markerPatterns": {},
        "missingQuestions": expected_numbers,
      },
      "questions": audited,
    }
  preflight = preflight_pdf(pdf_path, expected_numbers)
  pdf_questions = extract_pdf_questions(pdf_path, expected_numbers, preflight)
  audited = [compare_question(question, pdf_questions.get(int(question["number"])), preflight) for question in questions]
  now = datetime.now(timezone.utc).isoformat()
  return {
    "generatedAt": now,
    "mode": "read-only",
    "catalogState": args.catalog_state,
    "canonicalSource": "PDF original",
    "auxiliarySource": "DOCX/catalogo SimpleQuest",
    "d1": {"path": d1_path, "revisionCount": len(revisions)} if args.catalog_state == "effective" else None,
    "school": args.school,
    "year": args.year,
    "pdfRoot": str(pdf_root),
    "pdf": {
      "path": str(pdf_path),
      "associationConfidence": pdf_confidence,
      "candidates": candidates,
    },
    "admission": admission,
    "preflight": {key: value for key, value in preflight.items() if key != "_starts"},
    "questions": audited,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description="Auditoria MVP somente leitura entre catalogo SimpleQuest e PDF original.")
  parser.add_argument("--school", required=True, help="Instituicao, ex.: CMB")
  parser.add_argument("--year", required=True, type=int, help="Ano da prova no catalogo, ex.: 2014")
  parser.add_argument("--pdf-root", help="Raiz externa dos PDFs. Alternativas: SIMPLEQUEST_PDF_ROOT ou .simplequest-audit.local.json")
  parser.add_argument("--pdf", help="PDF especifico para auditar uma prova.")
  parser.add_argument("--config", default=str(LOCAL_CONFIG), help="Arquivo local ignorado pelo Git com {\"pdfRoot\":\"...\"}.")
  parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Diretorio de saida dos relatorios.")
  parser.add_argument("--catalog-state", choices=["base", "effective"], default="base", help="Audita o JSON base ou o catalogo efetivo base + revisoes D1.")
  parser.add_argument("--d1-db", help="Caminho opcional para SQLite D1 local em modo leitura.")
  parser.add_argument("--max-questions", type=int, default=0, help="Limita a quantidade de questoes para depuracao.")
  args = parser.parse_args()

  result = run(args)
  output_dir = Path(args.output_dir)
  output_dir.mkdir(parents=True, exist_ok=True)
  base = f"{args.school.lower()}-{args.year}-{args.catalog_state}-audit"
  json_path = output_dir / f"{base}.json"
  md_path = output_dir / f"{base}.md"
  json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
  md_path.write_text(markdown_report(result), encoding="utf-8")
  print(json.dumps({
    "json": str(json_path),
    "markdown": str(md_path),
    "questions": len(result["questions"]),
    "needsHumanReview": sum(1 for question in result["questions"] if question.get("needsHumanReview")),
    "pdf": result["pdf"]["path"],
    "associationConfidence": result["pdf"]["associationConfidence"],
    "admission": (result.get("admission") or {}).get("state"),
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
