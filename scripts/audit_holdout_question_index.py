from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import median
from typing import Any

import pdfplumber
from PIL import Image

from ocr_pdf_layer import DEFAULT_TESSERACT, DEFAULT_TESSDATA, group_words_into_lines, tesseract_page

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "audit" / "holdout" / "manifest-v2.json"
PROTOCOL_PATH = ROOT / "audit" / "holdout" / "protocol-v2.json"
INDEX_PATH = ROOT / "audit" / "holdout" / "question-index-v2.json"
OCR_CACHE_DIR = ROOT / "outputs" / "audit" / "holdout" / "ocr"

INDEX_METHOD_VERSION = "neutral-question-index-v1"
FROZEN_OCR = {"engine": "tesseract", "dpi": 160, "psm": 11, "lang": "por+eng"}

QUESTAO_RE = re.compile(r"^\s*QUEST[ÃA]O\s*0*(\d{1,3})\b", re.IGNORECASE)
ITEM_RE = re.compile(r"^\s*ITEM\s*0*(\d{1,3})\b", re.IGNORECASE)
PARENT_CHILD_RE = re.compile(r"^\s*\d{1,3}\s*[-–—]\s*[A-Ea-e]\b")
NUMERIC_RE = re.compile(r"^\s*0*(\d{1,3})\s*[.)\-–—]\s*(?!\s*[A-Ea-e]\b)")
BARE_NUMERIC_RE = re.compile(r"^\s*0*(\d{1,3})\s+(?=\S)")
ITEM_UPPERCASE_RE = re.compile(r"\bITEM\s*0*(\d{1,3})\b")
ROMAN_RE = re.compile(r"^\s*\(?\s*(I{1,3}|IV|V)\s*[).\-–—]?\s+\S")
MAX_QUESTION_NUMBER = 150
REPEATED_PAGE_THRESHOLD = 3
MIN_KEYWORD_MARKERS = 3
MIN_GRAMMAR_CANDIDATES = 3
MIN_MONOTONIC_RATIO = 0.6
MAX_DUPLICATE_RATIO = 0.34


def _line_key(text: str) -> str:
  # Collapse digits so repeated headers/footers that only differ by page number
  # map to the same key.
  import unicodedata
  value = unicodedata.normalize("NFKD", str(text or ""))
  value = "".join(char for char in value if not unicodedata.combining(char)).casefold()
  return re.sub(r"\d+", "#", value).strip()


def _repeated_line_keys(lines: list[dict[str, Any]]) -> set[str]:
  pages_by_key: dict[str, set[int]] = {}
  for line in lines:
    key = _line_key(line.get("text"))
    if not key:
      continue
    pages_by_key.setdefault(key, set()).add(int(line.get("page") or 0))
  return {key for key, pages in pages_by_key.items() if len(pages) >= REPEATED_PAGE_THRESHOLD}


def _candidate(line: dict[str, Any], number: int, kind: str) -> dict[str, Any]:
  bbox = line.get("bbox") or [0, 0, 0, 0]
  return {
    "number": number,
    "page": int(line["page"]),
    "top": float(bbox[1]),
    "x0": float(bbox[0]),
    "kind": kind,
    "text": str(line.get("text") or "").strip(),
  }


def _extract_families(lines: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
  keyword: list[dict[str, Any]] = []
  separator: list[dict[str, Any]] = []
  bare: list[dict[str, Any]] = []
  repeated = _repeated_line_keys(lines)
  for line in lines:
    text = str(line.get("text") or "").strip()
    if not text:
      continue
    match = QUESTAO_RE.match(text) or ITEM_RE.match(text)
    if match:
      keyword.append(_candidate(line, int(match.group(1)), "keyword"))
      continue
    uppercase_item = ITEM_UPPERCASE_RE.search(text)
    if uppercase_item:
      keyword.append(_candidate(line, int(uppercase_item.group(1)), "keyword"))
      continue
    if PARENT_CHILD_RE.match(text) or ROMAN_RE.match(text):
      continue
    numeric_match = NUMERIC_RE.match(text)
    if numeric_match:
      number = int(numeric_match.group(1))
      rest = text[numeric_match.end(1):]
      # Reject decimal continuations like "9.6 million".
      if rest[:1] == "." and rest[1:2].isdigit():
        continue
      if 1 <= number <= MAX_QUESTION_NUMBER and _line_key(text) not in repeated:
        separator.append(_candidate(line, number, "numeric"))
      continue
    bare_match = BARE_NUMERIC_RE.match(text)
    if bare_match:
      number = int(bare_match.group(1))
      if 1 <= number <= MAX_QUESTION_NUMBER and _line_key(text) not in repeated:
        bare.append(_candidate(line, number, "numeric"))
  return keyword, separator, bare


def evaluate_numbering_grammar(candidates: list[dict[str, Any]]) -> dict[str, Any]:
  if not candidates:
    return {"count": 0, "unique": 0, "monotonicRatio": None, "duplicateRatio": None, "plausible": False, "score": 0.0}
  ordered = sorted(candidates, key=lambda item: (item["page"], item["top"]))
  numbers = [marker["number"] for marker in ordered]
  unique = len(set(numbers))
  pairs = len(numbers) - 1
  increasing = sum(1 for index in range(pairs) if numbers[index] < numbers[index + 1])
  monotonic_ratio = (increasing / pairs) if pairs > 0 else 1.0
  duplicate_ratio = 1 - unique / len(numbers)
  plausible = (
    len(numbers) >= MIN_GRAMMAR_CANDIDATES
    and monotonic_ratio >= MIN_MONOTONIC_RATIO
    and duplicate_ratio <= MAX_DUPLICATE_RATIO
  )
  score = unique + monotonic_ratio * 10 - duplicate_ratio * 5
  return {
    "count": len(numbers),
    "unique": unique,
    "monotonicRatio": round(monotonic_ratio, 4),
    "duplicateRatio": round(duplicate_ratio, 4),
    "plausible": plausible,
    "score": round(score, 4),
  }


def select_primary_markers(lines: list[dict[str, Any]]) -> dict[str, Any]:
  keyword, separator, bare = _extract_families(lines)
  keyword_numbers = {marker["number"] for marker in keyword}
  if len(keyword_numbers) >= MIN_KEYWORD_MARKERS:
    return {"markers": keyword, "primary": "KEYWORD", "ambiguous": False}
  sep_eval = evaluate_numbering_grammar(separator)
  bare_eval = evaluate_numbering_grammar(bare)
  if sep_eval["plausible"] and not bare_eval["plausible"]:
    return {"markers": separator, "primary": "SEP", "ambiguous": False}
  if bare_eval["plausible"] and not sep_eval["plausible"]:
    return {"markers": bare, "primary": "BARE", "ambiguous": False}
  if sep_eval["plausible"] and bare_eval["plausible"]:
    # Case C: both families form a plausible sequence. Following the neutral
    # hierarchy (SEP before BARE), keep the separator family and record the
    # overlap for later review instead of merging both (merging is what produced
    # the false starts) or forcing a score-based winner.
    return {"markers": separator, "primary": "MIXED", "ambiguous": True}
  if separator or bare:
    return {"markers": separator + bare, "primary": "FALLBACK", "ambiguous": False}
  if keyword:
    return {"markers": keyword, "primary": "KEYWORD", "ambiguous": False}
  return {"markers": [], "primary": "NONE", "ambiguous": False}


def detect_markers(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  return select_primary_markers(lines)["markers"]


def build_sequence(markers: list[dict[str, Any]], page_count: int, page_heights: dict[int, float]) -> dict[str, Any]:
  anomalies: list[dict[str, Any]] = []
  ordered = sorted(markers, key=lambda item: (item["page"], item["top"]))
  unique: list[dict[str, Any]] = []
  seen: set[int] = set()
  for marker in ordered:
    if marker["number"] in seen:
      anomalies.append({"type": "duplicate_question_number", "number": marker["number"], "page": marker["page"]})
      continue
    seen.add(marker["number"])
    unique.append(marker)
  if not unique:
    return {"questions": [], "anomalies": anomalies}
  numbers = [marker["number"] for marker in unique]
  for index in range(1, len(numbers)):
    if numbers[index] <= numbers[index - 1]:
      anomalies.append({"type": "non_monotonic_numbering", "from": numbers[index - 1], "to": numbers[index]})
  expected = set(range(numbers[0], numbers[-1] + 1))
  for missing in sorted(expected - set(numbers)):
    anomalies.append({"type": "missing_question_number", "number": missing})
  if numbers[0] != 1:
    anomalies.append({"type": "missing_question_number", "number": 1, "note": "sequence does not start at 1"})
  questions: list[dict[str, Any]] = []
  for index, marker in enumerate(unique):
    if index + 1 < len(unique):
      following = unique[index + 1]
      height = page_heights.get(following["page"], 0.0) or 0.0
      if height and following["top"] <= height * 0.18:
        page_end = following["page"] - 1
      else:
        page_end = following["page"]
    else:
      page_end = page_count
    page_start = marker["page"]
    page_end = max(page_start, min(page_end, page_count))
    if page_end > page_start:
      # multi-page continuation is preserved; no structural info recorded
      pass
    questions.append({
      "questionId": None,
      "questionNumber": marker["number"],
      "pageStart": page_start,
      "pageEnd": page_end,
    })
  return {"questions": questions, "anomalies": anomalies}


def sequence_quality(markers: list[dict[str, Any]]) -> str:
  if not markers:
    return "none"
  if {marker["kind"] for marker in markers} & {"keyword"}:
    return "strong"
  numbers = sorted({marker["number"] for marker in markers})
  if len(numbers) < 2:
    return "weak"
  sequential = sum(1 for index in range(1, len(numbers)) if numbers[index] == numbers[index - 1] + 1)
  ratio = sequential / (len(numbers) - 1)
  coverage = numbers[-1] - numbers[0] + 1
  return "strong" if ratio >= 0.8 and coverage <= 2 * len(numbers) else "weak"


def looks_like_question_sequence(markers: list[dict[str, Any]]) -> bool:
  if not markers:
    return False
  kinds = {marker["kind"] for marker in markers}
  numbers = sorted({marker["number"] for marker in markers})
  if "keyword" in kinds:
    return len(numbers) >= 1
  # Numeric-only detection is a fallback and may include list items; require a
  # mostly sequential run of plausible question numbers.
  if len(numbers) < 5:
    return False
  sequential = sum(1 for index in range(1, len(numbers)) if numbers[index] == numbers[index - 1] + 1)
  return sequential >= max(1, int(len(numbers) * 0.6)) and numbers[-1] <= 150


def _native_pages(pdf_path: str) -> tuple[dict[int, list[dict[str, Any]]], dict[int, float], int]:
  pages: dict[int, list[dict[str, Any]]] = {}
  heights: dict[int, float] = {}
  with pdfplumber.open(str(pdf_path)) as pdf:
    page_count = len(pdf.pages)
    for index, page in enumerate(pdf.pages, start=1):
      words = []
      for word in page.extract_words():
        words.append({
          "index": len(words), "text": str(word.get("text") or ""),
          "bbox": [float(word["x0"]), float(word["top"]), float(word["x1"]), float(word["bottom"])],
          "confidence": None, "source": "native",
        })
      lines = group_words_into_lines(words)
      for line in lines:
        line["page"] = index
      pages[index] = lines
      heights[index] = float(page.height)
  return pages, heights, page_count


def _ocr_pages(pdf_path: str, document_id: str, dpi: int = FROZEN_OCR["dpi"], psm: int = FROZEN_OCR["psm"],
               lang: str = FROZEN_OCR["lang"]) -> tuple[dict[int, list[dict[str, Any]]], dict[int, float], int]:
  cache_dir = OCR_CACHE_DIR / document_id
  cache_file = cache_dir / "ocr.json"
  if cache_file.exists():
    payload = json.loads(cache_file.read_text(encoding="utf-8"))
    pages = {int(page["page"]): page["lines"] for page in payload["pages"]}
    heights = {int(page["page"]): float(page["height"]) for page in payload["pages"]}
    return pages, heights, len(payload["pages"])
  cache_dir.mkdir(parents=True, exist_ok=True)
  pages: dict[int, list[dict[str, Any]]] = {}
  heights: dict[int, float] = {}
  payload_pages: list[dict[str, Any]] = []
  with pdfplumber.open(str(pdf_path)) as pdf:
    page_count = len(pdf.pages)
    for index, page in enumerate(pdf.pages, start=1):
      image_path = cache_dir / f"page-{index:02d}.png"
      rendered = page.to_image(resolution=dpi)
      rendered.original.save(image_path)
      ocr_page = tesseract_page(image_path, index, DEFAULT_TESSERACT, DEFAULT_TESSDATA, lang, psm)
      lines = [dict(line, page=index) for line in ocr_page.lines]
      pages[index] = lines
      heights[index] = float(ocr_page.height)
      payload_pages.append({
        "page": index, "width": ocr_page.width, "height": ocr_page.height,
        "words": ocr_page.words, "lines": lines,
      })
  cache_dir.mkdir(parents=True, exist_ok=True)
  (cache_dir / "ocr.json").write_text(json.dumps({
    "engine": FROZEN_OCR["engine"], "dpi": dpi, "psm": psm, "lang": lang, "pages": payload_pages,
  }, ensure_ascii=False), encoding="utf-8")
  return pages, heights, page_count


def index_document(document: dict[str, Any], allow_ocr: bool = True) -> dict[str, Any]:
  document_id = document["documentId"]
  path = document["canonicalPath"]
  expected = document["contentFingerprint"]
  import hashlib
  actual = hashlib.sha256(Path(path).read_bytes()).hexdigest()
  if actual != expected:
    raise RuntimeError(f"source_fingerprint_mismatch:{document_id}")
  method = "native"
  pages, heights, page_count = _native_pages(path)
  all_lines = [line for page_lines in pages.values() for line in page_lines]
  selection = select_primary_markers(all_lines)
  markers = selection["markers"]
  anomalies: list[dict[str, Any]] = []
  lowered = path.lower()
  if "gabarito" in lowered or "\\gab_" in lowered or "/gab_" in lowered:
    anomalies.append({"type": "other", "note": "answer sheet/gabarito document; question stems not expected"})
  if not looks_like_question_sequence(markers):
    if allow_ocr:
      method = "ocr"
      pages, heights, page_count = _ocr_pages(path, document_id)
      all_lines = [line for page_lines in pages.values() for line in page_lines]
      selection = select_primary_markers(all_lines)
      markers = selection["markers"]
  if selection["ambiguous"]:
    anomalies.append({"type": "requires_neutral_verification", "note": "SEP and BARE both plausible; primary selected by neutral score"})
  if not looks_like_question_sequence(markers):
    anomalies.append({"type": "unresolved_question_start", "note": "no reliable question numbering sequence"})
  sequence = build_sequence(markers, page_count, heights)
  anomalies.extend(sequence["anomalies"])
  if markers and sequence_quality(markers) == "weak":
    anomalies.append({"type": "requires_neutral_verification", "note": "numeric-only sequence not clearly sequential"})
  questions = []
  for question in sequence["questions"]:
    question["questionId"] = f"{document_id}:q{question['questionNumber']}"
    questions.append(question)
  return {
    "documentId": document_id,
    "contentFingerprint": expected,
    "method": method,
    "pageCount": page_count,
    "questions": questions,
    "anomalies": anomalies,
  }


def _load(path: Path) -> Any:
  return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
  parser = argparse.ArgumentParser(description="Neutral question index for the frozen holdout manifest (no response structure).")
  parser.add_argument("--manifest", default=str(MANIFEST_PATH))
  parser.add_argument("--out", default=str(INDEX_PATH))
  parser.add_argument("--only", default=None, help="process a single documentId")
  parser.add_argument("--no-ocr", action="store_true")
  parser.add_argument("--report", default=None)
  args = parser.parse_args()

  manifest = _load(Path(args.manifest))
  documents = manifest["documents"]
  if args.only:
    documents = [document for document in documents if document["documentId"] == args.only]
  results = []
  for document in documents:
    results.append(index_document(document, allow_ocr=not args.no_ocr))
    summary = results[-1]
    print(f"{summary['documentId']} method={summary['method']} questions={len(summary['questions'])} anomalies={len(summary['anomalies'])}", flush=True)

  import hashlib
  if args.report:
    Path(args.report).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

  if args.only:
    return

  manifest_path = Path(args.manifest)
  try:
    created_from = manifest_path.resolve().relative_to(ROOT).as_posix()
  except ValueError:
    created_from = manifest_path.as_posix()
  index = {
    "protocolVersion": manifest["protocolVersion"],
    "indexMethodVersion": INDEX_METHOD_VERSION,
    "createdFromManifest": created_from,
    "manifestFileSha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    "manifestCanonicalJsonSha256": hashlib.sha256(
      json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest(),
    "ocrConfig": FROZEN_OCR,
    "documents": [
      {
        "documentId": result["documentId"],
        "contentFingerprint": result["contentFingerprint"],
        "questions": result["questions"],
      }
      for result in results
    ],
    "indexingAnomalies": [
      {"documentId": result["documentId"], **anomaly}
      for result in results for anomaly in result["anomalies"]
    ],
  }
  Path(args.out).write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
  print(json.dumps({"out": args.out, "documents": len(index["documents"]), "anomalies": len(index["indexingAnomalies"])}, ensure_ascii=False))


if __name__ == "__main__":
  main()
