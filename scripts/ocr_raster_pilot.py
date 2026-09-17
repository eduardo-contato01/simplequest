from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
  sys.path.insert(0, str(SCRIPTS))

import audit_pdf_mvp as audit
from ocr_pdf_layer import DEFAULT_TESSERACT, DEFAULT_TESSDATA, file_fingerprint, run_ocr, slugify


DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "audit" / "ocr"
SUMMARY_MD = ROOT / "outputs" / "audit" / "ocr-raster-pilot-summary.md"
SUMMARY_JSON = ROOT / "outputs" / "audit" / "ocr-raster-pilot-summary.json"
SUMMARY_CSV = ROOT / "outputs" / "audit" / "ocr-raster-pilot-summary.csv"

PILOT_PROOFS = [
  {
    "school": "CMB",
    "year": 2016,
    "pdf": r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS\CMB\6º Ano\CMB - 6ANO - 2016_2017 (mat).pdf",
    "reason": "Controle raster do piloto anterior; prova de 17 paginas com 20 questoes.",
  },
  {
    "school": "CMB",
    "year": 2024,
    "pdf": r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS\CMB\6º Ano\CMB - 6ANO - 2024_2025.pdf",
    "reason": "Controle raster recente; documento longo de 31 paginas.",
  },
  {
    "school": "CMBel",
    "year": 2022,
    "pdf": r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS\CMBel\6º Ano\CMBel - 6ANO - 2022_2023.pdf",
    "reason": "Controle raster de outra instituicao; 21 paginas e intervalo menor de questoes.",
  },
  {
    "school": "CMC",
    "year": 2009,
    "pdf": r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS\CMC\6º Ano\CMC - 6ANO - 2009_2010 (mat).pdf",
    "reason": "Controle raster antigo; 12 paginas, 30 questoes e provavel multiplas questoes por pagina.",
  },
  {
    "school": "CMBH",
    "year": 2017,
    "pdf": r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS\CMBH\6º Ano\CMBH - 6ANO - 2017_2018 (mat).pdf",
    "reason": "Raster adicional fora dos controles principais; outra instituicao, 12 paginas, 20 questoes.",
  },
]


def load_effective_catalog() -> list[dict[str, Any]]:
  base = json.loads(audit.CATALOG.read_text(encoding="utf-8"))
  revisions, _ = audit.load_revisions_from_d1(None)
  return audit.effective_catalog(base, revisions)


def catalog_questions(catalog: list[dict[str, Any]], school: str, year: int) -> list[dict[str, Any]]:
  questions = [
    question for question in catalog
    if question.get("school") == school and int(question.get("year", 0)) == year
  ]
  return sorted(questions, key=lambda item: int(item.get("number", 0)))


def line_to_audit_shape(page: dict[str, Any], line: dict[str, Any]) -> dict[str, Any]:
  x0, top, x1, bottom = line["bbox"]
  scale_x = float(page.get("pdfWidth") or page.get("width") or 1) / float(page.get("width") or 1)
  scale_y = float(page.get("pdfHeight") or page.get("height") or 1) / float(page.get("height") or 1)
  shape = {
    "text": line.get("text", ""),
    "x0": float(x0) * scale_x,
    "x1": float(x1) * scale_x,
    "top": float(top) * scale_y,
    "bottom": float(bottom) * scale_y,
    "page": int(page["page"]) - 1,
    "pageHeight": float(page.get("pdfHeight") or page.get("height") or 0),
    "confidence": line.get("confidence"),
  }
  if line.get("isReconstructed"):
    shape["isReconstructed"] = True
    shape["reconstructionConfidence"] = line.get("reconstructionConfidence")
    shape["sourceLine"] = line.get("sourceLine")
  return shape


def ocr_word_to_audit_shape(page: dict[str, Any], word: dict[str, Any]) -> dict[str, Any]:
  x0, top, x1, bottom = word["bbox"]
  scale_x = float(page.get("pdfWidth") or page.get("width") or 1) / float(page.get("width") or 1)
  scale_y = float(page.get("pdfHeight") or page.get("height") or 1) / float(page.get("height") or 1)
  return {
    "text": word.get("text", ""),
    "x0": float(x0) * scale_x,
    "x1": float(x1) * scale_x,
    "top": float(top) * scale_y,
    "bottom": float(bottom) * scale_y,
    "confidence": word.get("confidence"),
  }


def line_words(page: dict[str, Any], line: dict[str, Any]) -> list[dict[str, Any]]:
  indexes = set(line.get("wordIndexes") or [])
  return [word for word in page.get("words") or [] if word.get("index") in indexes]


def median_value(values: list[float], default: float = 0.0) -> float:
  clean = [float(value) for value in values if value is not None]
  return float(median(clean)) if clean else default


def reconstructed_line_candidate(page: dict[str, Any], line: dict[str, Any]) -> tuple[bool, str | None]:
  words = line_words(page, line)
  if len(words) < 18:
    return False, None
  line_shape = line_to_audit_shape(page, line)
  page_height = max(1.0, float(page.get("pdfHeight") or page.get("height") or 1))
  word_shapes = [ocr_word_to_audit_shape(page, word) for word in words]
  heights = [shape["bottom"] - shape["top"] for shape in word_shapes if shape["bottom"] > shape["top"]]
  median_height = median_value(heights, 0.0)
  if median_height <= 0:
    return False, None
  line_height = line_shape["bottom"] - line_shape["top"]
  centers = [((shape["top"] + shape["bottom"]) / 2) for shape in word_shapes]
  vertical_spread = max(centers) - min(centers) if centers else 0.0
  tall_relative_to_page = line_height >= page_height * 0.07
  tall_relative_to_words = line_height >= median_height * 5.0
  spread_relative_to_words = vertical_spread >= median_height * 4.0
  substantial_page_region = (line_shape["bottom"] - line_shape["top"]) >= page_height * 0.12 or len(words) >= 45
  if tall_relative_to_page and tall_relative_to_words and spread_relative_to_words and substantial_page_region:
    return True, "tall_multiband_block"
  return False, None


def split_words_into_visual_bands(page: dict[str, Any], line: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
  words = line_words(page, line)
  word_shapes = [{**ocr_word_to_audit_shape(page, word), "word": word} for word in words]
  heights = [shape["bottom"] - shape["top"] for shape in word_shapes if shape["bottom"] > shape["top"]]
  median_height = median_value(heights, 0.0)
  if median_height <= 0:
    return [], {"rejected": True, "reason": "missing_word_height"}
  y_threshold = max(median_height * 0.9, 4.0)
  bands: list[dict[str, Any]] = []
  for shape in sorted(word_shapes, key=lambda item: ((item["top"] + item["bottom"]) / 2, item["x0"])):
    center = (shape["top"] + shape["bottom"]) / 2
    matched = None
    for band in bands:
      if abs(center - band["center"]) <= y_threshold:
        matched = band
        break
    if matched is None:
      matched = {"items": [], "center": center}
      bands.append(matched)
    matched["items"].append(shape)
    matched["center"] = sum((item["top"] + item["bottom"]) / 2 for item in matched["items"]) / len(matched["items"])

  bands = [band for band in bands if band["items"]]
  if len(bands) < 2:
    return [], {"rejected": True, "reason": "single_visual_band"}
  if len(bands) > 35:
    return [], {"rejected": True, "reason": "too_many_visual_bands", "bands": len(bands)}

  page_width = max(1.0, float(page.get("pdfWidth") or page.get("width") or 1))
  text_bands = []
  sparse_bands = 0
  wide_gap_bands = 0
  for band in sorted(bands, key=lambda item: item["center"]):
    items = sorted(band["items"], key=lambda item: item["x0"])
    if len(items) <= 1:
      sparse_bands += 1
    gaps = [items[index + 1]["x0"] - items[index]["x1"] for index in range(len(items) - 1)]
    if any(gap > page_width * 0.28 for gap in gaps) and len(items) >= 5:
      wide_gap_bands += 1
    text_bands.append(items)

  if sparse_bands > max(4, len(text_bands) // 2):
    return [], {"rejected": True, "reason": "too_many_sparse_bands", "bands": len(text_bands)}
  if wide_gap_bands > max(4, len(text_bands) // 2):
    return [], {"rejected": True, "reason": "probable_multicolumn_or_table", "bands": len(text_bands)}

  reconstructed: list[dict[str, Any]] = []
  source_line = line.get("line")
  confidences = [word.get("confidence") for word in words if word.get("confidence") is not None]
  source_confidence = sum(confidences) / len(confidences) if confidences else None
  reconstruction_confidence = 0.88
  if wide_gap_bands:
    reconstruction_confidence -= min(0.12, wide_gap_bands * 0.02)
  if len(text_bands) >= 20:
    reconstruction_confidence -= 0.04
  for index, items in enumerate(text_bands):
    original_words = [item["word"] for item in items]
    xs0 = [item["word"]["bbox"][0] for item in items]
    ys0 = [item["word"]["bbox"][1] for item in items]
    xs1 = [item["word"]["bbox"][2] for item in items]
    ys1 = [item["word"]["bbox"][3] for item in items]
    band_confidences = [word.get("confidence") for word in original_words if word.get("confidence") is not None]
    reconstructed.append({
      "line": f"{source_line}.{index + 1}",
      "text": " ".join(str(word.get("text") or "") for word in original_words).strip(),
      "bbox": [min(xs0), min(ys0), max(xs1), max(ys1)],
      "confidence": round(sum(band_confidences) / len(band_confidences), 4) if band_confidences else source_confidence,
      "wordIndexes": [word["index"] for word in original_words],
      "isReconstructed": True,
      "reconstructionConfidence": round(max(0.0, min(1.0, reconstruction_confidence)), 4),
      "sourceLine": source_line,
      "sourceText": str(line.get("text") or "")[:180],
    })
  return reconstructed, {
    "rejected": False,
    "bands": len(reconstructed),
    "sourceLine": source_line,
    "reconstructionConfidence": round(max(0.0, min(1.0, reconstruction_confidence)), 4),
  }


def pages_with_reconstructed_lines(ocr_payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
  metrics = {
    "suspectBlocks": 0,
    "splitBlocks": 0,
    "reconstructedLines": 0,
    "ambiguousBlocks": 0,
    "rejectedBlocks": [],
  }
  pages: list[dict[str, Any]] = []
  for page in ocr_payload.get("pages") or []:
    updated_lines: list[dict[str, Any]] = []
    for line in page.get("lines") or []:
      suspicious, reason = reconstructed_line_candidate(page, line)
      if not suspicious:
        updated_lines.append(line)
        continue
      metrics["suspectBlocks"] += 1
      reconstructed, detail = split_words_into_visual_bands(page, line)
      if not reconstructed:
        metrics["ambiguousBlocks"] += 1
        metrics["rejectedBlocks"].append({
          "page": page.get("page"),
          "line": line.get("line"),
          "reason": detail.get("reason"),
          "candidateReason": reason,
          "text": str(line.get("text") or "")[:120],
        })
        updated_lines.append(line)
        continue
      metrics["splitBlocks"] += 1
      metrics["reconstructedLines"] += len(reconstructed)
      updated_lines.extend(reconstructed)
    page_copy = {**page, "lines": sorted(updated_lines, key=lambda item: (item["bbox"][1], item["bbox"][0]))}
    pages.append(page_copy)
  return pages, metrics


def normalized_token(value: str) -> str:
  return audit.strip_accents(re.sub(r"\s+", " ", str(value))).upper()


def token_number(value: str) -> int | None:
  match = re.fullmatch(r"0*(\d{1,3})(?:[.)-])?", str(value).strip())
  return int(match.group(1)) if match else None


def token_looks_like_questao(value: str) -> bool:
  normalized = normalized_token(value)
  return normalized in {"QUESTAO", "QUESTAO."} or normalized.startswith("QUEST")


def body_line_below(page: dict[str, Any], line_index: int, marker_bottom: float) -> bool:
  lines = page.get("lines") or []
  for next_line in lines[line_index + 1:line_index + 4]:
    shape = line_to_audit_shape(page, next_line)
    gap = shape["top"] - marker_bottom
    text = str(next_line.get("text") or "")
    if 4 <= gap <= 55 and len(text.strip()) >= 20 and not re.search(r"P[ÁA]GINA|CONCURSO|VISTO", normalized_token(text)):
      return True
  return False


def recover_header_embedded_marker(page: dict[str, Any], line: dict[str, Any], line_index: int, expected_set: set[int]) -> list[dict[str, Any]]:
  line_shape = line_to_audit_shape(page, line)
  line_height = max(1.0, line_shape["bottom"] - line_shape["top"])
  text = str(line.get("text") or "")
  normalized = normalized_token(text)
  if line_shape["top"] > 95:
    return []
  if "QUEST" not in normalized or "PAGINA" not in normalized:
    return []
  words = line_words(page, line)
  candidates: list[dict[str, Any]] = []
  for index, word in enumerate(words):
    if not token_looks_like_questao(str(word.get("text") or "")):
      continue
    quest_shape = ocr_word_to_audit_shape(page, word)
    for next_word in words[index + 1:index + 5]:
      number = token_number(str(next_word.get("text") or ""))
      if number is None or number not in expected_set:
        continue
      number_shape = ocr_word_to_audit_shape(page, next_word)
      same_row = abs(((quest_shape["top"] + quest_shape["bottom"]) / 2) - ((number_shape["top"] + number_shape["bottom"]) / 2)) <= 8
      plausible_x = quest_shape["x0"] <= 90 and number_shape["x0"] <= 130
      lower_band = quest_shape["top"] >= line_shape["top"] + line_height * 0.55
      strong_tokens = (word.get("confidence") or 0) >= 0.85 and (next_word.get("confidence") or 0) >= 0.85
      if same_row and plausible_x and lower_band and strong_tokens and body_line_below(page, line_index, number_shape["bottom"]):
        confidence = round(min(0.93, ((word.get("confidence") or 0) + (next_word.get("confidence") or 0)) / 2), 4)
        candidates.append({
          "number": number,
          "page": int(page["page"]) - 1,
          "top": number_shape["top"],
          "pattern": "recovered_header_marker",
          "text": f"{word.get('text')} {next_word.get('text')}",
          "ocrConfidence": confidence,
          "structuralConfidence": 0.91,
          "recovery": {
            "type": "header_embedded_marker",
            "sourceLine": text[:180],
            "questionToken": word.get("text"),
            "numberToken": next_word.get("text"),
          },
        })
      break
  return candidates


def recover_corrupted_marker(
  page: dict[str, Any],
  line: dict[str, Any],
  line_index: int,
  expected_set: set[int],
  confirmed_positions: list[dict[str, Any]],
  strong_existing_numbers: set[int],
) -> list[dict[str, Any]]:
  line_shape = line_to_audit_shape(page, line)
  if line_shape["x0"] > 95 or line_shape["bottom"] - line_shape["top"] > 45:
    return []
  words = line_words(page, line)
  if len(words) < 3:
    return []
  first = words[0]
  if not token_looks_like_questao(str(first.get("text") or "")) or (first.get("confidence") or 0) < 0.9:
    return []
  second = words[1]
  second_text = str(second.get("text") or "").strip()
  explicit_number = token_number(second_text)
  second_shape = ocr_word_to_audit_shape(page, second)
  first_shape = ocr_word_to_audit_shape(page, first)
  token_is_bad_number_slot = explicit_number is None and len(second_text) <= 3 and (second.get("confidence") or 0) <= 0.7
  token_is_out_of_range_number = explicit_number is not None and explicit_number not in expected_set and len(second_text) <= 3
  slot_ok = first_shape["x1"] <= second_shape["x0"] <= first_shape["x1"] + 24
  plausible_body = body_line_below(page, line_index, line_shape["bottom"]) or len(str(line.get("text") or "")) > 40
  if not ((token_is_bad_number_slot or token_is_out_of_range_number) and slot_ok and plausible_body):
    return []
  before = [
    item for item in confirmed_positions
    if (item["page"], item["top"]) < (line_shape["page"], line_shape["top"])
  ]
  after = [
    item for item in confirmed_positions
    if (item["page"], item["top"]) > (line_shape["page"], line_shape["top"])
  ]
  prev_number = before[-1]["number"] if before else None
  next_number = after[0]["number"] if after else None
  candidates: list[int] = []
  if next_number is not None and next_number - 1 in expected_set:
    candidates.append(next_number - 1)
  if prev_number is not None and prev_number + 1 in expected_set:
    candidates.append(prev_number + 1)
  candidates = [number for number in candidates if number not in strong_existing_numbers]
  inferred = candidates[0] if len(set(candidates)) == 1 else None
  if inferred is None:
    return []
  return [{
    "number": inferred,
    "page": int(page["page"]) - 1,
    "top": line_shape["top"],
    "pattern": "recovered_corrupted_marker",
    "text": f"{first.get('text')} {second.get('text')}",
    "ocrConfidence": second.get("confidence"),
    "structuralConfidence": 0.88,
    "recovery": {
      "type": "corrupted_number_token",
      "sourceLine": str(line.get("text") or "")[:180],
      "questionToken": first.get("text"),
      "corruptedToken": second_text,
      "explicitOcrNumber": explicit_number,
      "previousConfirmed": prev_number,
      "nextConfirmed": next_number,
      "inferredNumber": inferred,
    },
  }]


def normalized_marker_confidence(item: dict[str, Any]) -> float:
  if item.get("scorerConfidence") is not None:
    return round(float(item["scorerConfidence"]), 4)
  if item.get("structuralConfidence") is not None:
    return round(float(item["structuralConfidence"]), 4)
  if item.get("ocrConfidence") is not None:
    return round(float(item["ocrConfidence"]), 4)
  return round(max(0.0, min(1.0, float(item.get("markerScore") or 0) / 35)), 4)


def neighbor_numbers(detected: list[dict[str, Any]], index: int) -> tuple[int | None, int | None]:
  previous_number = detected[index - 1]["number"] if index > 0 else None
  next_number = detected[index + 1]["number"] if index + 1 < len(detected) else None
  return previous_number, next_number


def local_sequence_state(item: dict[str, Any], detected: list[dict[str, Any]], index: int, expected_numbers: list[int]) -> str:
  previous_number, next_number = neighbor_numbers(detected, index)
  number = item["number"]
  expected_first = expected_numbers[0] if expected_numbers else None
  expected_last = expected_numbers[-1] if expected_numbers else None
  previous_ok = number == expected_first or previous_number == number - 1
  next_ok = number == expected_last or next_number == number + 1
  if previous_ok and next_ok:
    return "complete"
  if previous_ok or next_ok:
    return "partial"
  return "broken"


def classify_association(item: dict[str, Any], detected: list[dict[str, Any]], index: int, expected_numbers: list[int], global_status: str) -> dict[str, Any]:
  marker_confidence = normalized_marker_confidence(item)
  pattern = item.get("pattern")
  sequence_state = local_sequence_state(item, detected, index, expected_numbers)
  unique = sum(1 for marker in detected if marker["number"] == item["number"]) == 1
  in_expected_range = item["number"] in set(expected_numbers)
  if not in_expected_range or not unique or global_status == "segmentation_failed":
    level = "low"
  elif pattern in {"questao", "recovered_header_marker", "recovered_corrupted_marker"} and marker_confidence >= 0.84 and sequence_state in {"complete", "partial"}:
    level = "high"
  elif pattern == "reconstructed_line_marker" and marker_confidence >= 0.88 and sequence_state in {"complete", "partial"}:
    level = "high"
  elif pattern == "numeric-dot" and marker_confidence >= 0.84 and sequence_state == "complete":
    level = "high"
  elif marker_confidence >= 0.68 and sequence_state in {"complete", "partial"}:
    level = "medium"
  else:
    level = "uncertain"
  return {
    "level": level,
    "score": marker_confidence,
    "unique": unique,
    "inExpectedRange": in_expected_range,
    "localSequence": sequence_state,
  }


def classify_boundary(item: dict[str, Any], detected: list[dict[str, Any]], index: int, expected_numbers: list[int]) -> dict[str, Any]:
  previous_number, next_number = neighbor_numbers(detected, index)
  number = item["number"]
  expected_first = expected_numbers[0] if expected_numbers else None
  expected_last = expected_numbers[-1] if expected_numbers else None
  start_anchored = number == expected_first or previous_number == number - 1
  end_anchored = number == expected_last or next_number == number + 1
  if start_anchored and end_anchored:
    level = "high"
    score = 0.95
  elif start_anchored or end_anchored:
    level = "uncertain"
    score = 0.55
  else:
    level = "low"
    score = 0.25
  return {
    "level": level,
    "score": score,
    "startAnchored": start_anchored,
    "endAnchored": end_anchored,
    "previousDetected": previous_number,
    "nextDetected": next_number,
  }


def annotate_question_confidences(detected: list[dict[str, Any]], expected_numbers: list[int], global_status: str) -> list[dict[str, Any]]:
  annotated = []
  for index, item in enumerate(detected):
    marker_confidence = normalized_marker_confidence(item)
    association = classify_association(item, detected, index, expected_numbers, global_status)
    boundary = classify_boundary(item, detected, index, expected_numbers)
    content_eligible = association["level"] == "high" and boundary["level"] == "high" and global_status != "segmentation_failed"
    annotated.append({
      **item,
      "markerConfidence": marker_confidence,
      "questionAssociationConfidence": association,
      "boundaryConfidence": boundary,
      "contentAuditEligibility": content_eligible,
    })
  return annotated


def structural_region(page: dict[str, Any], shape: dict[str, Any]) -> str:
  page_height = float(page.get("pdfHeight") or page.get("height") or 1)
  if shape["bottom"] < page_height * 0.13:
    return "header"
  if shape["top"] > page_height * 0.88:
    return "footer"
  return "body"


def normalized_line_key(text: str) -> str:
  return re.sub(r"\s+", " ", normalized_token(text)).strip()[:120]


def recurring_edge_lines(pages: list[dict[str, Any]]) -> Counter[str]:
  recurring: Counter[str] = Counter()
  for page in pages:
    page_height = float(page.get("pdfHeight") or page.get("height") or 1)
    for line in page.get("lines") or []:
      shape = line_to_audit_shape(page, line)
      if shape["bottom"] < page_height * 0.13 or shape["top"] > page_height * 0.88:
        key = normalized_line_key(str(line.get("text") or ""))
        if len(key) >= 12:
          recurring[key] += 1
  return recurring


def candidate_text_pattern(text: str) -> tuple[str | None, int | None, list[str]]:
  normalized = normalized_token(text)
  warnings: list[str] = []
  contextual_reference = re.search(r"\b(?:TEXTO|TEXTOS|LEIA|RESPONDA|PARA)\b.{0,40}\bQUEST(?:AO|OES|ÕES)\s+0*(\d{1,3})", normalized)
  if contextual_reference:
    return "textual_reference", int(contextual_reference.group(1)), ["contextual_question_reference"]
  plural = re.search(r"\bQUEST(?:AO|OES|ÕES)\s+0*(\d{1,3})(?:\s*(?:E|,|-)\s*0*(\d{1,3}))?", normalized)
  if plural and ("QUESTOES" in normalized or "QUESTÕES" in normalized):
    return "textual_reference", int(plural.group(1)), ["plural_question_reference"]
  questao = re.search(r"\bQUEST(?:AO|ÃO|A0|O)\s*[:.-]?\s*0*(\d{1,3})(?:[.:)]|º|ª)?", normalized)
  if questao:
    if re.search(r"\b6\s*[ºO]\s*ANO\b", normalized) or "CONCURSO" in normalized or "PAGINA" in normalized:
      warnings.append("questao_with_header_terms")
    return "questao_number", int(questao.group(1)), warnings
  numeric = re.match(r"^\s*0*(\d{1,3})\s*[.)]\s+\S+", text)
  if numeric:
    return "numeric_dot", int(numeric.group(1)), warnings
  return None, None, warnings


def line_word_median_height(page: dict[str, Any], line: dict[str, Any]) -> float | None:
  heights = []
  for word in line_words(page, line):
    shape = ocr_word_to_audit_shape(page, word)
    height = shape["bottom"] - shape["top"]
    if height > 0:
      heights.append(height)
  return round(median_value(heights), 4) if heights else None


def section_signals(text: str) -> list[str]:
  normalized = normalized_token(text)
  signals = []
  if "MATEMATICA" in normalized:
    signals.append("matematica")
  if "LINGUA PORTUGUESA" in normalized or "PORTUGUESA" in normalized:
    signals.append("lingua_portuguesa")
  if "REDACAO" in normalized:
    signals.append("redacao")
  if "CONCURSO" in normalized:
    signals.append("concurso")
  if "PAGINA" in normalized:
    signals.append("pagina")
  if re.search(r"\b6\s*[ºO]\s*ANO\b", normalized):
    signals.append("serie_6_ano")
  return signals


def negative_text_signals(text: str) -> list[str]:
  normalized = normalized_token(text)
  signals = []
  if re.match(r"^\s*\(?[A-Ea-e]\)?\s*[).]?", text):
    signals.append("alternative")
  if "PAGINA" in normalized or re.search(r"\bp\.\s*\d+\b", text, re.IGNORECASE):
    signals.append("page_number")
  if "ATENCAO" in normalized or "CANDIDATO" in normalized or "CARTAO" in normalized:
    signals.append("instruction_or_list")
  if "CONCURSO" in normalized or re.search(r"\b6\s*[ºO]\s*ANO\b", normalized):
    signals.append("header_terms")
  if re.search(r"\bQUEST(?:AO|OES|ÕES)\s+\d+\s*(?:E|,|-)\s*\d+", normalized):
    signals.append("plural_question_reference")
  if re.search(r"\b(?:R\$|CM|KM|MM|%|H|MIN)\b|\d+[,.]\d+|\d+/\d+", normalized):
    signals.append("math_or_unit_value")
  if "|" in text or text.count("  ") >= 3:
    signals.append("table_like")
  return signals


def instruction_vocab_hits(text: str) -> list[str]:
  normalized = normalized_token(text)
  vocabulary = {
    "ASSINATURA": r"\bASSINATURA\b",
    "CANDIDATO": r"\bCANDIDAT[OA]S?\b",
    "CARTAO": r"\bCARTAO\b",
    "DESCLASSIFICACAO": r"\bDESCLASSIFIC",
    "FISCALIZACAO": r"\bFISCALIZ",
    "INSTRUCOES": r"\bINSTRUCOES\b|\bINSTRUCAO\b",
    "PROVA": r"\bPROVA\b",
    "RESPOSTA": r"\bRESPOSTAS?\b",
    "TEMPO": r"\bTEMPO\b",
  }
  return [name for name, pattern in vocabulary.items() if re.search(pattern, normalized)]


def numeric_instruction_list_evidence(candidate: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
  if candidate.get("textPattern") != "numeric_dot":
    return {"isInstructionListLike": False, "score": 0}

  same_page = [
    item for item in candidates
    if item.get("textPattern") == "numeric_dot"
    and item.get("page") == candidate.get("page")
    and abs(float(item.get("xRel") or 0) - float(candidate.get("xRel") or 0)) <= 0.055
    and abs(float(item.get("top") or 0) - float(candidate.get("top") or 0)) <= 130
  ]
  nearby_numbers = {int(item["number"]) for item in same_page}
  number = int(candidate["number"])
  local_run = [
    value for value in range(number - 2, number + 3)
    if value in nearby_numbers
  ]
  consecutive_neighbors = int(number - 1 in nearby_numbers) + int(number + 1 in nearby_numbers)

  local_text = " ".join(str(item.get("text") or "") for item in same_page)
  vocab_hits = sorted(set(instruction_vocab_hits(local_text)))
  regular_gaps = []
  ordered = sorted(same_page, key=lambda item: float(item.get("top") or 0))
  for previous, current in zip(ordered, ordered[1:]):
    gap = float(current.get("top") or 0) - float(previous.get("top") or 0)
    if 5 <= gap <= 45:
      regular_gaps.append(round(gap, 2))

  margin_delta = candidate.get("marginDelta")
  margin_far = margin_delta is not None and float(margin_delta) >= 0.14
  early_page = int(candidate.get("page") or 0) <= 2 and float(candidate.get("yRel") or 0) <= 0.55
  list_sequence = len(local_run) >= 3 and consecutive_neighbors >= 1
  regular_list_spacing = len(regular_gaps) >= 2

  score = 0
  if list_sequence:
    score += 2
  if regular_list_spacing:
    score += 1
  if len(vocab_hits) >= 2:
    score += 2
  elif len(vocab_hits) == 1:
    score += 1
  if margin_far:
    score += 2
  if early_page:
    score += 1

  return {
    "isInstructionListLike": score >= 5 and list_sequence and len(vocab_hits) >= 1,
    "score": score,
    "nearbyNumericItems": len(same_page),
    "localRun": local_run,
    "consecutiveNeighbors": consecutive_neighbors,
    "regularGaps": regular_gaps[:6],
    "instructionVocabulary": vocab_hits,
    "marginFarFromReference": margin_far,
    "earlyPageRegion": early_page,
  }


def local_sequence_evidence(candidate: dict[str, Any], candidates: list[dict[str, Any]], expected_set: set[int]) -> dict[str, Any]:
  ordered = sorted(candidates, key=lambda item: (item["page"], item["top"], item["xRel"]))
  current_index = next((index for index, item in enumerate(ordered) if item["candidateId"] == candidate["candidateId"]), None)
  if current_index is None:
    return {"state": "unknown", "previous": None, "next": None}
  number = candidate["number"]
  previous_numbers = [
    item["number"] for item in ordered[:current_index]
    if item["number"] in expected_set and item["number"] != number
  ]
  next_numbers = [
    item["number"] for item in ordered[current_index + 1:]
    if item["number"] in expected_set and item["number"] != number
  ]
  previous_number = previous_numbers[-1] if previous_numbers else None
  next_number = next_numbers[0] if next_numbers else None
  previous_ok = number == min(expected_set) or previous_number == number - 1
  next_ok = number == max(expected_set) or next_number == number + 1
  if previous_ok and next_ok:
    state = "complete"
  elif previous_ok or next_ok:
    state = "partial"
  else:
    state = "broken"
  return {"state": state, "previous": previous_number, "next": next_number}


LEADING_MARKER_ARTIFACT_RE = re.compile(r"^[\s|\[\]\{\}()~^+=_\\/•·,;:]+")
NUMERIC_MARKER_MIN_BODY_WORDS = 4
NUMERIC_MARKER_MIN_BODY_CHARS = 20
NUMERIC_MARKER_MIN_RECONSTRUCTION = 0.80


def numeric_marker_variant(
  text: str,
  expected_set: set[int],
  is_reconstructed: bool,
  reconstruction_confidence: float | None,
) -> dict[str, Any] | None:
  # Conservative OCR-variant parser used only to GENERATE candidates. It never
  # accepts a marker: the existing marker scorer remains the final decision.
  raw = str(text or "")
  if not raw.strip():
    return None
  lead = LEADING_MARKER_ARTIFACT_RE.match(raw)
  leading_artifact = bool(lead)
  stripped = raw[lead.end():] if lead else raw
  head = re.match(r"0*(\d{1,3})([.)\,\-–—:]?)", stripped)
  if not head:
    return None
  number = int(head.group(1))
  separator = head.group(2)
  rest = stripped[head.end():]
  evidence: list[str] = []
  if leading_artifact:
    evidence.append("leading_artifact_stripped")

  dot_zero = re.match(r"^\s*0\s+[A-Za-zÀ-ÿ]", rest)
  duplicated = re.match(r"\s+0*(\d{1,3})\b", rest)

  if separator == "." and dot_zero:
    base_variant = "numeric_dot_ocr_o"
    rest = re.sub(r"^\s*0\s+", "", rest, count=1)
    evidence.append("dot_followed_by_standalone_zero_before_text")
  elif duplicated and separator in {"", "."} and int(duplicated.group(1)) == number:
    base_variant = "numeric_duplicated"
    rest = rest[duplicated.end():]
    evidence.append("duplicated_leading_number")
  elif separator == ",":
    base_variant = "numeric_comma"
    evidence.append("comma_separator")
  elif separator == ")":
    base_variant = "numeric_paren"
    evidence.append("paren_separator")
  elif separator == "":
    if not re.match(r"\s+\S", rest):
      return None
    base_variant = "numeric_no_punctuation"
    evidence.append("no_punctuation")
  elif separator in {".", "-", "–", "—", ":"}:
    if not (leading_artifact and re.match(r"\s+\S", rest)):
      return None
    base_variant = "numeric_with_standard_punctuation"
    evidence.append("standard_punctuation_after_leading_artifact")
  else:
    return None

  if number not in expected_set:
    return None
  body_words = re.findall(r"[\wÀ-ÿ]+", rest)
  if len(body_words) < NUMERIC_MARKER_MIN_BODY_WORDS or len(rest.strip()) < NUMERIC_MARKER_MIN_BODY_CHARS:
    return None
  signals = negative_text_signals(raw)
  if "alternative" in signals or "page_number" in signals:
    return None
  if is_reconstructed and (reconstruction_confidence or 0.0) < NUMERIC_MARKER_MIN_RECONSTRUCTION:
    return None

  variant = "numeric_with_leading_artifact" if leading_artifact else base_variant
  if leading_artifact:
    evidence.append(f"base_variant:{base_variant}")
  return {
    "number": number,
    "variant": variant,
    "rawText": raw,
    "normalizedMarkerNumber": number,
    "normalizationEvidence": evidence,
  }


def variant_candidate_allowed(
  shape: dict[str, Any],
  page: dict[str, Any],
  text: str,
  variant: str | None,
  number: int | None,
  margin_reference: float | None,
  anchor_numbers: set[int],
) -> bool:
  # Structural gates applied only to OCR-variant candidates, before they enter
  # the candidate pool. They do not touch the scorer or any accepted marker.
  if variant is None:
    return True
  if structural_region(page, shape) != "body":
    return False
  page_width = float(page.get("pdfWidth") or page.get("width") or 1)
  x_rel = float(shape["x0"]) / page_width
  if margin_reference is not None and abs(x_rel - margin_reference) > 0.05:
    return False
  signals = negative_text_signals(text)
  if "alternative" in signals or "page_number" in signals or "instruction_or_list" in signals:
    return False
  words = len(str(text).split())
  if variant == "numeric_duplicated":
    return words >= 5
  if words < 6:
    return False
  if number is not None and variant in {"numeric_no_punctuation", "numeric_dot_ocr_o"}:
    # Risky variants need a locally anchored sequence: a neighbour number must
    # already be a selected marker of this proof.
    if number - 1 not in anchor_numbers and number + 1 not in anchor_numbers:
      return False
  if variant == "numeric_no_punctuation":
    head = re.match(r"^[\s|\[\]\{\}()~^+=_\\/•·,;:]*0*\d{1,3}\s*", str(text))
    body = str(text)[head.end():].strip() if head else str(text)
    if body and body[0].islower():
      return False
  return True


# --- Marker profile discovery (shadow only) --------------------------------
# These helpers only OBSERVE candidates. They never change candidateScore,
# classification, selection, association, boundary or content eligibility.

PROFILE_MIN_ANCHORS = 4
PROFILE_MIN_HOLDOUT = 2
PROFILE_MIN_PURITY = 0.6
PROFILE_MIN_MARGIN = 0.30
PROFILE_MIN_COVERAGE = 0.20
PROFILE_MARGIN_TOL = 0.06
PROFILE_X_TOL = 0.06
PROFILE_GAP_TOL = 12.0
PROFILE_MAX_PROFILES = 3
SEVERE_NEGATIVE_SIGNALS = {
  "alternative_line",
  "page_number_or_page_header",
  "instruction_or_list",
  "plural_question_reference",
  "numeric_dot_instruction_list_block",
  "recurring_header_footer_line",
  "questao_number_ambiguous_with_header_terms",
}
_SUFFIX_FROM_CHAR = {".": "dot", ")": "paren", "-": "dash", "–": "dash", "—": "dash", ":": "colon", ",": "comma"}


def _descriptor_signature(descriptor: dict[str, Any]) -> tuple:
  # Style signature used for grouping/purity. numberFormat is inferred
  # separately from the 1..9 range so magnitude cannot split a profile.
  return (
    descriptor["keyword"],
    descriptor["prefix"],
    descriptor["suffix"],
  )


def _single_digit_format(raw: str) -> str:
  # Only the 1..9 range discriminates padding: "10" is identical in both styles.
  if raw and raw.isdigit() and 1 <= int(raw) <= 9:
    return "zero_padded_2" if re.fullmatch(r"0\d", raw) else "unpadded"
  return "indeterminate"


def build_marker_descriptor(text: str, variant: str | None = None) -> dict[str, Any]:
  raw = str(text or "")
  lead = LEADING_MARKER_ARTIFACT_RE.match(raw)
  leading_artifact = bool(lead)
  stripped = raw[lead.end():] if lead else raw
  head = stripped[:24]
  keyword = "none"
  keyword_case: str | None = None
  km = re.search(r"(QUEST(?:AO|ÃO|A0)|ITEM)", head, re.IGNORECASE)
  if km:
    keyword = "question" if km.group(0).upper().startswith("QUEST") else "item"
    matched = km.group(0)
    if matched.isupper():
      keyword_case = "upper"
    elif matched[:1].isupper():
      keyword_case = "title"
    else:
      keyword_case = "lower"
  # Ordinal only counts as part of the marker itself ("1ª QUESTÃO", "1º ITEM"),
  # never when it appears in the statement body ("... A 20ª Mostra ...").
  ordinal = None
  if km:
    prefix_region = head[:km.start()]
    ordinal = re.match(r"^\s*0*(\d{1,3})\s*[ºª°]\b", prefix_region)
  prefix = "ordinal" if ordinal else "none"
  number_raw = ""
  separator = "none"
  separator_raw = ""
  nm = re.search(r"(?<!\d)(0*\d{1,3})(?!\d)", stripped)
  if nm:
    number_raw = nm.group(1)
    after = stripped[nm.end():]
    gap = re.match(r"\s*", after).end()
    following = after[gap:gap + 1]
    separator_raw = following
    if following in _SUFFIX_FROM_CHAR:
      separator = _SUFFIX_FROM_CHAR[following]
    elif following and not following.isalnum():
      # Corrupted OCR glyphs (U+FFFD, "~", ...) are unknown, never silently none.
      separator = "unknown"
    else:
      separator = "none"
  elif ordinal:
    number_raw = ordinal.group(1)
  suffix = separator
  if len(number_raw) <= 1:
    width = "one_digit"
  elif len(number_raw) == 2:
    width = "two_digit"
  else:
    width = "variable"
  duplicated = variant == "numeric_duplicated" or bool(
    re.search(r"^\s*0*(\d{1,3})\s+\1\b", re.sub(r"^[\s|\[\]\{\}()~^+=_\\/•·,;:]+", "", raw))
  )
  return {
    "keyword": keyword,
    "keywordCase": keyword_case,
    "prefix": prefix,
    "numberRaw": number_raw,
    "numberInt": int(number_raw) if number_raw.isdigit() else None,
    "numberWidth": width,
    "numberFormat": _single_digit_format(number_raw),
    "separator": separator,
    "separatorRaw": separator_raw,
    "suffix": suffix,
    "leadingArtifact": leading_artifact,
    "duplicatedDigit": duplicated,
    "ocrZeroAfterDot": variant == "numeric_dot_ocr_o",
    "variant": variant,
  }


def _candidate_severe_negatives(candidate: dict[str, Any]) -> set[str]:
  return {item.get("signal") for item in candidate.get("negativeEvidence") or []}


def _region_usable(candidate: dict[str, Any]) -> bool:
  region = candidate.get("structuralRegion")
  if region == "body":
    return True
  if region in {"header", "footer"}:
    return int(candidate.get("headerFooterRecurrence") or 0) == 0
  return False


def _candidate_margin_ok(candidate: dict[str, Any]) -> bool:
  margin_delta = candidate.get("marginDelta")
  if margin_delta is not None:
    return float(margin_delta) <= PROFILE_MARGIN_TOL
  x_rel = candidate.get("xRel")
  return x_rel is not None and float(x_rel) <= 0.25


def _is_primary_anchor(candidate: dict[str, Any]) -> bool:
  descriptor = candidate.get("markerDescriptor") or {}
  if descriptor.get("prefix") == "ordinal":
    return False
  if candidate.get("classification") != "strong_candidate":
    return False
  effective_unique = candidate.get("effectiveUniqueNumber", candidate.get("uniqueNumber"))
  if not effective_unique or not candidate.get("inExpectedRange"):
    return False
  if not _region_usable(candidate):
    return False
  # Keyword markers ("Questão 09 :") often carry the statement on the next
  # line, so the marker line itself can be very short.
  min_words = 2 if descriptor.get("keyword") != "none" else 5
  if int(candidate.get("wordCount") or 0) < min_words:
    return False
  if _candidate_severe_negatives(candidate) & SEVERE_NEGATIVE_SIGNALS:
    return False
  return _candidate_margin_ok(candidate)


def _is_weak_run_member(candidate: dict[str, Any]) -> bool:
  descriptor = candidate.get("markerDescriptor") or {}
  if descriptor.get("keyword") != "none" or descriptor.get("suffix") != "none" or descriptor.get("prefix") != "none":
    return False
  if not candidate.get("uniqueNumber") or not candidate.get("inExpectedRange"):
    return False
  if not _region_usable(candidate):
    return False
  if int(candidate.get("wordCount") or 0) < 6:
    return False
  if _candidate_severe_negatives(candidate) & SEVERE_NEGATIVE_SIGNALS:
    return False
  return _candidate_margin_ok(candidate)


def _sequential_run_anchors(candidates: list[dict[str, Any]], min_run: int) -> set[int]:
  ordered = sorted(candidates, key=lambda item: (item["page"], item["top"]))
  anchors: set[int] = set()
  run: list[dict[str, Any]] = []
  for candidate in ordered:
    if not _is_weak_run_member(candidate):
      run = []
      continue
    if run:
      previous = run[-1]
      same_descriptor = _descriptor_signature(previous["markerDescriptor"]) == _descriptor_signature(candidate["markerDescriptor"])
      consecutive = candidate["number"] == previous["number"] + 1
      same_page = candidate["page"] == previous["page"]
      if not (same_descriptor and consecutive and same_page):
        if len(run) >= min_run:
          anchors.update(id(item) for item in run)
        run = []
    run.append(candidate)
  if len(run) >= min_run:
    anchors.update(id(item) for item in run)
  return anchors


def _profile_group_stats(group: list[dict[str, Any]], expected_count: int, support_extra: int = 0) -> dict[str, Any]:
  # Once a keyword style is established by enough primary anchors, keyword-less
  # anchors (instructions, stray numbers) are not allowed to shape the modal
  # keyword/suffix/format or the purity/entropy. They still count as support and
  # keep the section scope, and remain normal scorer candidates.
  keyword_anchors = [c for c in group if (c.get("markerDescriptor") or {}).get("keyword") != "none"]
  keyword_style_established = len(keyword_anchors) >= PROFILE_MIN_ANCHORS
  style_group = keyword_anchors if keyword_style_established else group
  signatures: dict[tuple, int] = {}
  keyword_counts: dict[str, int] = {}
  suffix_counts: dict[str, int] = {}
  for candidate in style_group:
    descriptor = candidate["markerDescriptor"]
    signature = _descriptor_signature(descriptor)
    signatures[signature] = signatures.get(signature, 0) + 1
    if descriptor["keyword"] != "none":
      keyword_counts[descriptor["keyword"]] = keyword_counts.get(descriptor["keyword"], 0) + 1
    suffix_counts[descriptor["suffix"]] = suffix_counts.get(descriptor["suffix"], 0) + 1
  ranked = sorted(signatures.items(), key=lambda item: (-item[1], item[0]))
  dominant, dominant_count = ranked[0]
  style_total = len(style_group)
  purity = dominant_count / style_total if style_total else 0.0
  runner_up = ranked[1] if len(ranked) > 1 else None
  margin = ((dominant_count - runner_up[1]) / style_total) if runner_up else 1.0
  # numberFormat is inferred only from the 1..9 range of anchors that share the
  # FULL dominant style (keyword/prefix/suffix), so anchors of another style
  # (e.g. question/dot vs question/colon) can never mix their padding.
  format_pool = [c for c in style_group if _descriptor_signature(c["markerDescriptor"]) == dominant]
  one_to_nine = [c["markerDescriptor"]["numberRaw"] for c in format_pool
                 if _single_digit_format(c["markerDescriptor"]["numberRaw"]) != "indeterminate"]
  zero_padded = sum(1 for raw in one_to_nine if re.fullmatch(r"0\d", raw))
  unpadded = sum(1 for raw in one_to_nine if re.fullmatch(r"[1-9]", raw))
  if zero_padded and unpadded:
    number_format = "mixed"
  elif zero_padded:
    number_format = "zero_padded_2"
  elif unpadded:
    number_format = "unpadded"
  else:
    number_format = "indeterminate"
  format_purity = round(max(zero_padded, unpadded) / len(one_to_nine), 4) if one_to_nine else None
  total_support = len(group) + support_extra
  x_values = sorted(float(c["xRel"]) for c in style_group if c.get("xRel") is not None)
  gap_values = sorted(float(c["previousGap"]) for c in style_group if c.get("previousGap") is not None)
  median_x = median_value(x_values, None)
  median_gap = median_value(gap_values, None)
  def iqr(values: list[float]) -> float:
    if len(values) < 4:
      return 0.0
    lower = median_value(values[:len(values) // 2], 0.0)
    upper = median_value(values[len(values) // 2:], 0.0)
    return round(upper - lower, 4)
  entropy = 0.0
  for count in signatures.values():
    share = count / style_total
    if share > 0:
      entropy -= share * math.log(share)
  keyword_acceptable = sorted(k for k, v in keyword_counts.items() if v / style_total >= 0.2)
  # A single minority observation must not create an acceptable alternative.
  # The modal suffix itself does not depend on this minimum.
  suffix_acceptable = sorted(
    k for k, v in suffix_counts.items()
    if v >= 2 and v / style_total >= 0.2
  )
  return {
    "keyword": dominant[0],
    "numberFormat": number_format,
    "prefix": dominant[1],
    "suffix": dominant[2],
    "keywordAcceptable": keyword_acceptable,
    "suffixAcceptable": suffix_acceptable,
    "numberFormatEvidence": {
      "oneToNineAnchors": len(one_to_nine),
      "zeroPadded2": zero_padded,
      "unpadded": unpadded,
      "formatPurity": format_purity,
    },
    "styleAnchors": style_total,
    "styleExcludedAnchors": len(group) - style_total,
    "keywordStyleEstablished": keyword_style_established,
    "xPositionProfile": {"median": round(median_x, 4) if median_x is not None else None, "iqr": iqr(x_values), "tolerance": PROFILE_X_TOL},
    "verticalGapProfile": {"medianPreviousGap": round(median_gap, 4) if median_gap is not None else None, "tolerance": PROFILE_GAP_TOL},
    "support": total_support,
    "coverage": round(total_support / expected_count, 4) if expected_count else 0.0,
    "purity": round(purity, 4),
    "entropy": round(entropy, 4),
    "alternativeProfiles": [
      {"signature": list(signature), "count": count, "share": round(count / style_total, 4)}
      for signature, count in ranked[1:4]
    ],
    "dominantMargin": round(margin, 4),
  }


def _profile_holdout(group: list[dict[str, Any]], dominant: tuple) -> dict[str, Any]:
  odd = [c for c in group if c["number"] % 2 == 1]
  even = [c for c in group if c["number"] % 2 == 0]
  if len(odd) < PROFILE_MIN_HOLDOUT or len(even) < PROFILE_MIN_HOLDOUT:
    return {"status": "insufficient_holdout", "discoveryHalf": None, "validationHalf": None, "purity": None}
  discovery, validation = (odd, even) if len(odd) <= len(even) else (even, odd)
  matches = sum(1 for c in validation if _descriptor_signature(c["markerDescriptor"]) == dominant)
  return {
    "status": "validated",
    "discoveryHalf": "odd" if discovery is odd else "even",
    "validationHalf": "even" if validation is even else "odd",
    "purity": round(matches / len(validation), 4),
  }


def _make_profile(group: list[dict[str, Any]], extra_support: list[dict[str, Any]], expected_count: int, scope: dict[str, Any], index: int) -> dict[str, Any]:
  stats = _profile_group_stats(group, expected_count, support_extra=len(extra_support))
  holdout = _profile_holdout(group, (stats["keyword"], stats["prefix"], stats["suffix"]))
  anchor_ids = {id(c) for c in group} | {id(c) for c in extra_support}
  return {
    "id": f"profile-{index}",
    "scope": scope,
    "keyword": stats["keyword"],
    "numberFormat": stats["numberFormat"],
    "prefix": stats["prefix"],
    "suffix": stats["suffix"],
    "keywordAcceptable": stats["keywordAcceptable"],
    "suffixAcceptable": stats["suffixAcceptable"],
    "numberFormatEvidence": stats["numberFormatEvidence"],
    "xPositionProfile": stats["xPositionProfile"],
    "verticalGapProfile": stats["verticalGapProfile"],
    "support": {"anchors": stats["support"], "modalAnchors": stats["styleAnchors"], "scopeAnchors": len(group), "expectedQuestions": expected_count, "coverage": stats["coverage"]},
    "styleAnchors": stats["styleAnchors"],
    "styleExcludedAnchors": stats["styleExcludedAnchors"],
    "keywordStyleEstablished": stats["keywordStyleEstablished"],
    "purity": stats["purity"],
    "entropy": stats["entropy"],
    "confidence": None,
    "alternativeProfiles": stats["alternativeProfiles"],
    "dominantMargin": stats["dominantMargin"],
    "holdout": holdout,
    "_anchorIds": sorted(anchor_ids),
  }


def discover_marker_profiles(candidates: list[dict[str, Any]], expected_numbers: list[int]) -> dict[str, Any]:
  expected_count = len(expected_numbers)
  primary_ids = {id(c) for c in candidates if _is_primary_anchor(c)}
  weak_ids = _sequential_run_anchors(candidates, PROFILE_MIN_ANCHORS)
  primary_candidates = [c for c in candidates if id(c) in primary_ids]
  weak_candidates = [c for c in candidates if id(c) in weak_ids and id(c) not in primary_ids]
  # When there are enough primary anchors, sequential runs only add support:
  # they must never change the modal keyword/prefix/suffix/numberFormat.
  use_primary_only = len(primary_candidates) >= PROFILE_MIN_ANCHORS
  discovery_candidates = primary_candidates if use_primary_only else primary_candidates + weak_candidates
  # A keyword style established by enough primary anchors is authoritative for
  # the profile style: keyword-less anchors must not shape the modal (handled in
  # _profile_group_stats). They still count as support and keep the section
  # scope, and remain normal scorer candidates. A single keyword anchor is not
  # enough to establish the style.
  keyword_anchors = [c for c in discovery_candidates if (c.get("markerDescriptor") or {}).get("keyword") != "none"]
  keyword_style_established = len(keyword_anchors) >= PROFILE_MIN_ANCHORS
  result: dict[str, Any] = {
    "status": "unavailable",
    "reason": None,
    "anchorRule": {
      "primary": len(primary_ids),
      "sequentialRun": len(weak_ids),
      "usedSequentialFallback": not use_primary_only,
      "keywordStyleEstablished": keyword_style_established,
      "effective": len(discovery_candidates),
    },
    "profiles": [],
  }
  if len(discovery_candidates) < PROFILE_MIN_ANCHORS:
    result["reason"] = "insufficient_anchors"
    return result

  groups: list[tuple[dict[str, Any], list[dict[str, Any]], set[int]]] = []
  disciplines = {signal for c in discovery_candidates for signal in (c.get("sectionSignals") or []) if signal in {"matematica", "lingua_portuguesa", "redacao"}}
  if len(disciplines) >= 2:
    ordered_disciplines = [d for d in ["matematica", "lingua_portuguesa", "redacao"] if d in disciplines]
    split_groups = []
    for discipline in ordered_disciplines:
      members = [c for c in discovery_candidates if discipline in (c.get("sectionSignals") or [])]
      if len(members) >= PROFILE_MIN_ANCHORS:
        split_groups.append(members)
    remaining = [c for c in discovery_candidates if not any(d in (c.get("sectionSignals") or []) for d in disciplines)]
    if len(remaining) >= PROFILE_MIN_ANCHORS:
      split_groups.append(remaining)
    if len(split_groups) >= 2:
      for members in split_groups[:PROFILE_MAX_PROFILES]:
        pages = [c["page"] for c in members]
        scope = {"pageFrom": min(pages), "pageTo": max(pages), "discipline": None}
        groups.append((scope, members, {id(c) for c in members}))
  if not groups:
    ordered = sorted(discovery_candidates, key=lambda item: (item["page"], item["top"]))
    reset_index = None
    for i in range(1, len(ordered)):
      if ordered[i]["number"] < ordered[i - 1]["number"]:
        reset_index = i
        break
    if reset_index and reset_index >= PROFILE_MIN_ANCHORS and (len(ordered) - reset_index) >= PROFILE_MIN_ANCHORS:
      first, second = ordered[:reset_index], ordered[reset_index:]
      for members in (first, second):
        pages = [c["page"] for c in members]
        groups.append(({"pageFrom": min(pages), "pageTo": max(pages), "discipline": None}, members, {id(c) for c in members}))
    else:
      pages = [c["page"] for c in ordered]
      groups.append(({"pageFrom": min(pages), "pageTo": max(pages), "discipline": None}, ordered, {id(c) for c in ordered}))

  profiles: list[dict[str, Any]] = []
  rejected: list[dict[str, Any]] = []
  for index, (scope, members, member_ids) in enumerate(groups, start=1):
    extra_support: list[dict[str, Any]] = []
    if use_primary_only:
      extra_support = [c for c in weak_candidates if scope["pageFrom"] <= c["page"] <= scope["pageTo"]]
    profile = _make_profile(members, extra_support, expected_count, scope, index)
    holdout_purity = profile["holdout"]["purity"]
    confidence_terms = [
      profile["purity"],
      profile["support"]["coverage"],
      min(1.0, profile["support"]["anchors"] / 10),
      min(1.0, profile["dominantMargin"]),
    ]
    if holdout_purity is not None:
      confidence_terms.append(holdout_purity)
    confidence = round(sum(confidence_terms) / len(confidence_terms), 4)
    profile["confidence"] = confidence
    reason = None
    if profile["support"]["anchors"] < PROFILE_MIN_ANCHORS:
      reason = "insufficient_anchors"
    elif profile["purity"] < PROFILE_MIN_PURITY:
      reason = "low_purity"
    elif profile["dominantMargin"] < PROFILE_MIN_MARGIN:
      reason = "low_margin"
    elif profile["support"]["coverage"] < PROFILE_MIN_COVERAGE:
      reason = "low_coverage"
    if reason:
      rejected.append({"scope": scope, "reason": reason, "support": profile["support"], "purity": profile["purity"], "dominantMargin": profile["dominantMargin"]})
    else:
      profiles.append(profile)
  if profiles:
    result["status"] = "available" if len(profiles) == 1 else "multiprofile"
    result["profiles"] = profiles
  else:
    result["reason"] = rejected[0]["reason"] if rejected else "insufficient_anchors"
  result["rejected"] = rejected
  return result


PROFILE_SIGNAL_WEIGHTS = {
  "keyword": 2.0,
  "suffix": 2.0,
  "prefix": 1.5,
  "number_format": 1.0,
  "x_position": 1.0,
  "vertical_gap": 1.0,
  "region": 1.0,
}


def profile_affinity(candidate: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
  descriptor = candidate.get("markerDescriptor") or {}
  matched: list[str] = []
  mismatched: list[str] = []
  neutral: list[str] = []
  def signal(name: str, verdict: bool | None) -> None:
    if verdict is True:
      matched.append(name)
    elif verdict is False:
      mismatched.append(name)
    else:
      neutral.append(name)

  if profile["keyword"] != "none":
    if descriptor.get("keyword") == profile["keyword"] or descriptor.get("keyword") in profile["keywordAcceptable"]:
      signal("keyword", True)
    else:
      signal("keyword", False)
  else:
    signal("keyword", descriptor.get("keyword") == "none")

  if descriptor.get("prefix") == "ordinal" or profile["prefix"] == "ordinal":
    signal("prefix", False)
  else:
    signal("prefix", True)

  candidate_suffix = descriptor.get("suffix")
  if candidate_suffix == "unknown":
    # OCR glyph not recognised: absence of evidence, not evidence against.
    signal("suffix", None)
  else:
    signal("suffix", candidate_suffix == profile["suffix"] or candidate_suffix in profile["suffixAcceptable"])

  candidate_format = descriptor.get("numberFormat")
  profile_format = profile.get("numberFormat")
  if profile_format in {"mixed", "indeterminate"} or candidate_format not in {"unpadded", "zero_padded_2"}:
    signal("number_format", None)
  else:
    signal("number_format", candidate_format == profile_format)

  x_profile = profile["xPositionProfile"]
  if x_profile.get("median") is not None and candidate.get("xRel") is not None:
    signal("x_position", abs(float(candidate["xRel"]) - float(x_profile["median"])) <= PROFILE_X_TOL)
  else:
    signal("x_position", None)

  gap_profile = profile["verticalGapProfile"]
  if gap_profile.get("medianPreviousGap") is not None and candidate.get("previousGap") is not None:
    signal("vertical_gap", abs(float(candidate["previousGap"]) - float(gap_profile["medianPreviousGap"])) <= PROFILE_GAP_TOL)
  else:
    signal("vertical_gap", None)

  region = candidate.get("structuralRegion")
  if region == "body":
    signal("region", True)
  elif region in {"header", "footer"}:
    signal("region", False)
  else:
    signal("region", None)

  applicable_weight = sum(PROFILE_SIGNAL_WEIGHTS[name] for name in matched + mismatched)
  match_weight = sum(PROFILE_SIGNAL_WEIGHTS[name] for name in matched)
  mismatch_weight = sum(PROFILE_SIGNAL_WEIGHTS[name] for name in mismatched)
  match_strength = round(match_weight / applicable_weight, 4) if applicable_weight else None
  mismatch_strength = round(mismatch_weight / applicable_weight, 4) if applicable_weight else None
  checks = len(matched) + len(mismatched)
  affinity = round(len(matched) / checks, 4) if checks else None
  # Strong structural negatives stay visible separately and must never be
  # cancelled by the profile. They only cap the backward-compatible affinity.
  structural_negatives = sorted(_candidate_severe_negatives(candidate) & SEVERE_NEGATIVE_SIGNALS)
  if structural_negatives and affinity is not None:
    affinity = round(min(affinity, 0.5), 4)
  return {
    "affinity": affinity,
    "evidence": matched,
    "mismatch": mismatched,
    "neutral": neutral,
    "match_strength": match_strength,
    "mismatch_strength": mismatch_strength,
    "structural_negatives": structural_negatives,
  }


def attach_marker_profiles(candidates: list[dict[str, Any]], discovery: dict[str, Any]) -> None:
  profiles = discovery.get("profiles") or []
  for candidate in candidates:
    candidate["isProfileAnchor"] = False
    candidate["profileId"] = None
    candidate["profileAffinity"] = None
    candidate["profileEvidence"] = []
    candidate["profileMismatch"] = []
    candidate["profileMatchEvidence"] = []
    candidate["profileMismatchEvidence"] = []
    candidate["profileMatchStrength"] = None
    candidate["profileMismatchStrength"] = None
    candidate["profileStructuralNegatives"] = []
  if not profiles:
    # No profile: absence of evidence, never a negative one.
    return
  anchor_map = {profile["id"]: set(profile.get("_anchorIds") or []) for profile in profiles}
  for candidate in candidates:
    for profile in profiles:
      if id(candidate) in anchor_map.get(profile["id"], set()):
        candidate["isProfileAnchor"] = True
        candidate["profileId"] = profile["id"]
      scope = profile["scope"]
      if scope.get("pageFrom") is not None and not (scope["pageFrom"] <= candidate["page"] <= scope["pageTo"]):
        continue
      if candidate["isProfileAnchor"]:
        continue
      result = profile_affinity(candidate, profile)
      candidate["profileId"] = profile["id"]
      candidate["profileAffinity"] = result["affinity"]
      candidate["profileEvidence"] = result["evidence"]
      candidate["profileMismatch"] = result["mismatch"]
      candidate["profileMatchEvidence"] = result["evidence"]
      candidate["profileMismatchEvidence"] = result["mismatch"]
      candidate["profileMatchStrength"] = result["match_strength"]
      candidate["profileMismatchStrength"] = result["mismatch_strength"]
      candidate["profileStructuralNegatives"] = result["structural_negatives"]
      break


# --- Page role / questionContentScope (shadow only) ------------------------
# Observational: classifies pages and simulates a scoped uniqueness. It never
# changes uniqueNumber, scores, classification, selection or the profile.

PAGE_COVER_ADMIN_VOCAB = (
  "CONCURSO", "ADMISSAO", "PROCESSO SELETIVO", "INSCRICAO", "CONFERENCIA",
  "ASSINATURA", "ENSINO FUNDAMENTAL", "6O ANO", "6 ANO", "CONCURSO DE ADMISSAO",
)
PAGE_POST_VOCAB = (
  "GABARITO", "PADRAO DE RESPOSTA", "FOLHA DE RESPOSTAS", "RASCUNHO", "ANULADA",
)
ALT_LINE_RE = re.compile(r"(?m)^\s*\(?[A-Ea-e]\)?\s*[).:\-–—]")


def _page_text(page: dict[str, Any]) -> str:
  return "\n".join(str(line.get("text") or "") for line in page.get("lines") or [])


def _page_header_footer_evidence(page: dict[str, Any]) -> int:
  height = float(page.get("pdfHeight") or page.get("height") or 1)
  count = 0
  for line in page.get("lines") or []:
    bbox = line.get("bbox") or [0, 0, 0, 0]
    top = float(bbox[1])
    bottom = float(bbox[3])
    if bottom < height * 0.13 or top > height * 0.88:
      count += 1
  return count


def collect_page_features(pages: list[dict[str, Any]], candidates: list[dict[str, Any]], expected_numbers: list[int]) -> list[dict[str, Any]]:
  expected_count = len(expected_numbers)
  by_page: dict[int, list[dict[str, Any]]] = {}
  for candidate in candidates:
    by_page.setdefault(int(candidate["page"]), []).append(candidate)
  features: list[dict[str, Any]] = []
  for page in pages:
    page_number = int(page["page"])
    page_candidates = by_page.get(page_number, [])
    in_range = [c for c in page_candidates if c["inExpectedRange"]]
    keyword_markers = [c for c in in_range if (c["markerDescriptor"] or {}).get("keyword") != "none"]
    numeric_markers = [c for c in in_range if (c["markerDescriptor"] or {}).get("keyword") == "none"]
    out_of_range = [c for c in page_candidates if not c["inExpectedRange"]]
    text = _page_text(page)
    upper = audit.strip_accents(text).upper()
    lines = page.get("lines") or []
    alternatives = sum(1 for line in lines if ALT_LINE_RE.search(str(line.get("text") or "")))
    body = sum(1 for line in lines if len(str(line.get("text") or "").split()) >= 6)
    admin_vocab = sorted({word for word in PAGE_COVER_ADMIN_VOCAB if word in upper})
    post_vocab = sorted({word for word in PAGE_POST_VOCAB if word in upper})
    section = sorted({signal for line in lines for signal in section_signals(str(line.get("text") or ""))})
    features.append({
      "pageNumber": page_number,
      "inRangeCandidateCount": len(in_range),
      "keywordMarkerCount": len(keyword_markers),
      "numericMarkerCount": len(numeric_markers),
      "outOfRangeCandidateCount": len(out_of_range),
      "alternativeEvidence": alternatives,
      "substantialBodyEvidence": body,
      "instructionVocabularyHits": len(instruction_vocab_hits(text)),
      "administrativeVocabularyHits": admin_vocab,
      "postVocabularyHits": post_vocab,
      "headerFooterEvidence": _page_header_footer_evidence(page),
      "candidateDensity": round(len(page_candidates) / max(1, len(lines)), 4),
      "expectedRangeCoverage": round(len(in_range) / expected_count, 4) if expected_count else 0.0,
      "sectionSignals": section,
      "evidence": {
        "keywordNumbers": [c["number"] for c in keyword_markers],
        "numericNumbers": [c["number"] for c in numeric_markers],
        "outOfRangeNumbers": [c["number"] for c in out_of_range],
      },
    })
  return features


def infer_question_scope(features: list[dict[str, Any]], expected_count: int) -> dict[str, Any]:
  for feature in features:
    keyword_marker = feature["keywordMarkerCount"] >= 1
    question_pair = feature["inRangeCandidateCount"] >= 2 and feature["alternativeEvidence"] >= 2 and feature["substantialBodyEvidence"] >= 4
    feature["hasQuestionEvidence"] = keyword_marker or question_pair
    # A numbered list with no keyword markers and (almost) no alternatives is the
    # classic instruction/list signature; it is NOT treated as question content.
    feature["listLike"] = feature["inRangeCandidateCount"] >= 3 and feature["keywordMarkerCount"] == 0 and feature["alternativeEvidence"] <= 1
    feature["hasInstructionEvidence"] = bool(
      feature["listLike"]
      or ((not feature["hasQuestionEvidence"]) and (feature["instructionVocabularyHits"] >= 2 or len(feature["administrativeVocabularyHits"]) >= 2))
    )
    feature["hasPostEvidence"] = bool(
      len(feature["postVocabularyHits"]) >= 1
      or (feature["outOfRangeCandidateCount"] >= 4 and not feature["hasQuestionEvidence"])
    )

  feature_by_page = {f["pageNumber"]: f for f in features}
  question_pages = [f["pageNumber"] for f in features if f["hasQuestionEvidence"]]
  keyword_pages = [f["pageNumber"] for f in features if f["keywordMarkerCount"] >= 1]
  start: int | None = None
  for index in range(len(features) - 1):
    if features[index]["hasQuestionEvidence"] and features[index + 1]["hasQuestionEvidence"]:
      start = features[index]["pageNumber"]
      break
  if start is None:
    start = 1
  # Never exclude a page that carries an in-range keyword marker: pull start back.
  if keyword_pages and min(keyword_pages) < start:
    start = min(keyword_pages)
  end = max(question_pages) if question_pages else features[-1]["pageNumber"]

  for feature in features:
    page_number = feature["pageNumber"]
    if page_number < start:
      if page_number == 1 and not feature["hasQuestionEvidence"]:
        role = "cover"
      elif feature["hasInstructionEvidence"]:
        role = "instructions"
      else:
        role = "unknown"
    elif page_number <= end:
      if feature["hasQuestionEvidence"] and feature["listLike"]:
        role = "mixed"
      elif feature["hasQuestionEvidence"]:
        role = "question_content"
      elif feature["hasInstructionEvidence"]:
        role = "mixed"
      else:
        role = "unknown"
    else:
      role = "answer_sheet_or_post_content" if (feature["hasPostEvidence"] or (feature["outOfRangeCandidateCount"] >= 4 and not feature["hasQuestionEvidence"])) else "unknown"
    feature["pageRole"] = role
    # Conservative scope: only clearly non-question pages without keyword markers
    # leave the scope. mixed/unknown always stay inside.
    excluded = role in {"cover", "instructions", "answer_sheet_or_post_content"} and feature["keywordMarkerCount"] == 0
    feature["questionScope"] = "non_question_scope" if excluded else "question_scope"

  # General, explainable confidence (no per-institution rule, no human truth).
  start_feature = feature_by_page.get(start, {})
  start_by_marker = bool(
    start_feature.get("keywordMarkerCount", 0) >= 1
    or (
      start_feature.get("inRangeCandidateCount", 0) >= 2
      and start_feature.get("alternativeEvidence", 0) >= 2
      and start_feature.get("substantialBodyEvidence", 0) >= 4
    )
  )
  no_keyword_before_start = not any(f["keywordMarkerCount"] >= 1 for f in features if f["pageNumber"] < start)
  next_feature = feature_by_page.get(start + 1)
  # Continuation must not demand that the next page be question_content: a
  # mixed/unknown page without contradictory (cover/instructions/post) role is
  # acceptable.
  continuation_ok = (
    next_feature is None
    or next_feature.get("keywordMarkerCount", 0) >= 1
    or next_feature.get("pageRole") not in {"cover", "instructions", "answer_sheet_or_post_content"}
  )
  enough_question_pages = sum(1 for f in features if f["hasQuestionEvidence"]) >= 2
  end_safe = not any(f["keywordMarkerCount"] >= 1 for f in features if f["pageNumber"] > end)
  unknown_ratio = round(sum(1 for f in features if f["pageRole"] in {"mixed", "unknown"}) / max(1, len(features)), 4)
  # A scope that begins on page 1 without any in-range keyword marker is not
  # trustworthy: page 1 could be a cover/orientations page that mimics question
  # numbering. Require keyword evidence when the start is the first page.
  first_page_keyword_start = not (start == 1 and start_feature.get("keywordMarkerCount", 0) == 0)
  if start_by_marker and no_keyword_before_start and continuation_ok and enough_question_pages and end_safe and unknown_ratio <= 0.5 and first_page_keyword_start:
    confidence = "high"
  elif start_by_marker and no_keyword_before_start and enough_question_pages:
    confidence = "medium"
  else:
    confidence = "low"

  reliable_excluded = [
    f["pageNumber"] for f in features
    if f["questionScope"] == "non_question_scope" and f["pageRole"] in {"cover", "instructions", "answer_sheet_or_post_content"}
  ]
  keyword_outside_scope = [
    f["pageNumber"] for f in features
    if f["questionScope"] == "non_question_scope" and f["keywordMarkerCount"] >= 1
  ]
  start_not_after_keyword = (not keyword_pages) or start <= min(keyword_pages)
  policy_active = bool(
    confidence == "high"
    and first_page_keyword_start
    and reliable_excluded
    and not keyword_outside_scope
    and start_not_after_keyword
  )
  if policy_active:
    policy_reason = "question_scope_high_confidence"
  elif not first_page_keyword_start:
    policy_reason = "fallback_global_first_page_without_keyword"
  elif confidence != "high":
    policy_reason = "fallback_global_low_scope_confidence"
  elif keyword_outside_scope:
    policy_reason = "fallback_global_keyword_outside_scope"
  else:
    policy_reason = "fallback_global_no_reliable_excluded_pages"

  ambiguous = [f["pageNumber"] for f in features if f["pageRole"] in {"mixed", "unknown"}]
  excluded_pages = [f["pageNumber"] for f in features if f["questionScope"] == "non_question_scope"]
  return {
    "questionContentStart": start,
    "questionContentEnd": end,
    "confidence": confidence,
    "confidenceScore": {"high": 1.0, "medium": 0.6, "low": 0.3}[confidence],
    "confidenceEvidence": {
      "startByMarker": start_by_marker,
      "noKeywordBeforeStart": no_keyword_before_start,
      "continuationOk": bool(continuation_ok),
      "enoughQuestionPages": bool(enough_question_pages),
      "endSafe": bool(end_safe),
      "unknownRatio": unknown_ratio,
    },
    "scopeUniquenessPolicyActive": policy_active,
    "scopeUniquenessPolicyReason": policy_reason,
    "pagesExcludedFromQuestionScope": excluded_pages,
    "reliableExcludedPages": reliable_excluded,
    "keywordOutsideQuestionScope": keyword_outside_scope,
    "ambiguousPages": ambiguous,
    "pages": features,
  }


def apply_question_scope_uniqueness(candidates: list[dict[str, Any]], scope: dict[str, Any]) -> None:
  in_scope_pages = {f["pageNumber"] for f in scope["pages"] if f["questionScope"] == "question_scope"}
  counts: dict[int, int] = {}
  for candidate in candidates:
    if int(candidate["page"]) in in_scope_pages:
      counts[int(candidate["number"])] = counts.get(int(candidate["number"]), 0) + 1
  for candidate in candidates:
    in_scope = int(candidate["page"]) in in_scope_pages
    candidate["inQuestionScope"] = in_scope
    candidate["globalUnique"] = bool(candidate.get("uniqueNumber"))
    candidate["questionScopeUnique"] = bool(in_scope and counts.get(int(candidate["number"]), 0) == 1)
    duplicates = []
    if in_scope and not candidate["questionScopeUnique"]:
      for other in candidates:
        if other is candidate or int(other["number"]) != int(candidate["number"]):
          continue
        if int(other["page"]) not in in_scope_pages:
          continue
        duplicates.append({
          "page": int(other["page"]),
          "classification": other.get("classification"),
          "textPattern": other.get("textPattern"),
        })
    candidate["questionScopeDuplicateEvidence"] = duplicates
  policy_active = bool(scope.get("scopeUniquenessPolicyActive"))
  policy_reason = scope.get("scopeUniquenessPolicyReason")
  for candidate in candidates:
    candidate["effectiveUniqueNumber"] = (
      bool(candidate["questionScopeUnique"]) if policy_active else bool(candidate.get("uniqueNumber"))
    )
    candidate["effectiveUniqueReason"] = policy_reason


def extract_marker_candidates_shadow(ocr_payload: dict[str, Any], expected_numbers: list[int], preflight: dict[str, Any]) -> dict[str, Any]:
  pages, reconstruction_metrics = pages_with_reconstructed_lines(ocr_payload)
  expected_set = set(expected_numbers)
  selected_pairs = {
    (int(item["page"]), int(item["number"]))
    for item in preflight.get("selectedQuestionMarkers") or []
  }
  selected_x = [
    float(item.get("marker", item).get("xRel"))
    for item in []
  ]
  selected_shapes = []
  for page in pages:
    for line in page.get("lines") or []:
      shape = line_to_audit_shape(page, line)
      marker = audit.question_marker_from_line(shape, expected_set)
      if marker and (int(page["page"]), int(marker["number"])) in selected_pairs:
        page_width = float(page.get("pdfWidth") or page.get("width") or 1)
        selected_shapes.append(shape["x0"] / page_width)
  margin_reference = median_value(selected_shapes, None) if selected_shapes else None
  recurring = recurring_edge_lines(pages)
  candidates: list[dict[str, Any]] = []
  candidate_id = 0
  broad_expected = set(range(1, 101))

  def build_candidate(page, page_width, page_height, lines, line_index, line, number, pattern, warnings, variant_meta):
    nonlocal candidate_id
    text = str(line.get("text") or "")
    shape = line_to_audit_shape(page, line)
    previous_gap = None
    next_gap = None
    if line_index > 0:
      previous_shape = line_to_audit_shape(page, lines[line_index - 1])
      previous_gap = round(shape["top"] - previous_shape["bottom"], 4)
    if line_index + 1 < len(lines):
      next_shape = line_to_audit_shape(page, lines[line_index + 1])
      next_gap = round(next_shape["top"] - shape["bottom"], 4)
    key = normalized_line_key(text)
    source = "reconstructed_line" if line.get("isReconstructed") else "raw_ocr"
    candidate_id += 1
    return {
      "candidateId": candidate_id,
      "number": int(number),
      "text": text[:220],
      "rawText": text,
      "normalizedMarkerNumber": int(number),
      "markerVariant": variant_meta["variant"] if variant_meta else None,
      "normalizationEvidence": list(variant_meta["normalizationEvidence"]) if variant_meta else [],
      "markerDescriptor": build_marker_descriptor(text, variant_meta["variant"] if variant_meta else None),
      "textPattern": pattern,
      "patternWarnings": warnings,
      "bbox": [round(shape["x0"], 2), round(shape["top"], 2), round(shape["x1"], 2), round(shape["bottom"], 2)],
      "page": int(page["page"]),
      "top": round(shape["top"], 4),
      "lineIndex": line_index,
      "xRel": round(shape["x0"] / page_width, 4),
      "yRel": round(shape["top"] / page_height, 4),
      "widthRel": round((shape["x1"] - shape["x0"]) / page_width, 4),
      "heightRel": round((shape["bottom"] - shape["top"]) / page_height, 4),
      "wordCount": len(text.split()),
      "medianWordHeight": line_word_median_height(page, line),
      "previousGap": previous_gap,
      "nextGap": next_gap,
      "source": source,
      "ocrConfidence": line.get("confidence"),
      "reconstructionConfidence": line.get("reconstructionConfidence"),
      "structuralRegion": structural_region(page, shape),
      "headerFooterRecurrence": recurring.get(key, 0),
      "expectedRange": [min(expected_numbers), max(expected_numbers)] if expected_numbers else None,
      "inExpectedRange": int(number) in expected_set,
      "currentPipelineSelected": (int(page["page"]), int(number)) in selected_pairs,
      "sectionSignals": section_signals(text),
      "negativeTextSignals": negative_text_signals(text),
      "marginReference": round(margin_reference, 4) if margin_reference is not None else None,
      "marginDelta": round(abs((shape["x0"] / page_width) - margin_reference), 4) if margin_reference is not None else None,
    }

  page_anchors: dict[int, set[int]] = {}
  # Pass 1: standard markers only. These build the same-page sequência anchor.
  for page in pages:
    page_width = float(page.get("pdfWidth") or page.get("width") or 1)
    page_height = float(page.get("pdfHeight") or page.get("height") or 1)
    lines = page.get("lines") or []
    for line_index, line in enumerate(lines):
      text = str(line.get("text") or "")
      pattern, number, warnings = candidate_text_pattern(text)
      broad_marker = audit.question_marker_from_line(line_to_audit_shape(page, line), broad_expected)
      if pattern is None and broad_marker:
        pattern = broad_marker["pattern"]
        number = broad_marker["number"]
      if pattern is None or number is None:
        continue
      candidates.append(build_candidate(page, page_width, page_height, lines, line_index, line, number, pattern, warnings, None))
      page_anchors.setdefault(int(page["page"]), set()).add(int(number))

  # Pass 2: OCR variants. Gated before entering the pool; the scorer still decides.
  for page in pages:
    page_width = float(page.get("pdfWidth") or page.get("width") or 1)
    page_height = float(page.get("pdfHeight") or page.get("height") or 1)
    lines = page.get("lines") or []
    anchors = page_anchors.get(int(page["page"]), set())
    for line_index, line in enumerate(lines):
      text = str(line.get("text") or "")
      pattern, number, warnings = candidate_text_pattern(text)
      broad_marker = audit.question_marker_from_line(line_to_audit_shape(page, line), broad_expected)
      if pattern is not None or broad_marker:
        continue
      variant_meta = numeric_marker_variant(
        text,
        expected_set,
        bool(line.get("isReconstructed")),
        line.get("reconstructionConfidence"),
      )
      if variant_meta is None:
        continue
      variant_number = variant_meta["number"]
      if variant_number is None:
        continue
      shape = line_to_audit_shape(page, line)
      if not variant_candidate_allowed(
        shape, page, text, variant_meta["variant"], variant_number, margin_reference, anchors
      ):
        continue
      candidates.append(build_candidate(
        page, page_width, page_height, lines, line_index, line,
        variant_number, variant_meta["variant"], warnings, variant_meta,
      ))
  number_counts = Counter(candidate["number"] for candidate in candidates)
  for candidate in candidates:
    sequence = local_sequence_evidence(candidate, candidates, expected_set)
    candidate["sequence"] = sequence
    candidate["uniqueNumber"] = number_counts[candidate["number"]] == 1
    candidate["numericInstructionListEvidence"] = numeric_instruction_list_evidence(candidate, candidates)
    score, confidence, classification, positive, negative = score_marker_candidate(candidate)
    candidate["candidateScore"] = score
    candidate["candidateConfidence"] = confidence
    candidate["classification"] = classification
    candidate["positiveEvidence"] = positive
    candidate["negativeEvidence"] = negative
  page_features = collect_page_features(pages, candidates, expected_numbers)
  page_role_discovery = infer_question_scope(page_features, len(expected_numbers))
  apply_question_scope_uniqueness(candidates, page_role_discovery)
  profile_discovery = discover_marker_profiles(candidates, expected_numbers)
  attach_marker_profiles(candidates, profile_discovery)
  return {
    "candidates": sorted(candidates, key=lambda item: (-item["candidateScore"], item["page"], item["lineIndex"])),
    "reconstructionMetrics": reconstruction_metrics,
    "marginReference": round(margin_reference, 4) if margin_reference is not None else None,
    "profileDiscovery": profile_discovery,
    "pageRoleDiscovery": page_role_discovery,
  }


def score_marker_candidate(candidate: dict[str, Any]) -> tuple[int, float, str, list[dict[str, Any]], list[dict[str, Any]]]:
  score = 0
  positive: list[dict[str, Any]] = []
  negative: list[dict[str, Any]] = []

  def add_positive(name: str, weight: int, detail: Any = None) -> None:
    nonlocal score
    score += weight
    positive.append({"signal": name, "weight": weight, "detail": detail})

  def add_negative(name: str, weight: int, detail: Any = None) -> None:
    nonlocal score
    score -= weight
    negative.append({"signal": name, "weight": -weight, "detail": detail})

  pattern = candidate["textPattern"]
  if pattern == "questao_number":
    add_positive("text_pattern_questao_number", 34)
  elif pattern == "numeric_dot":
    add_positive("text_pattern_numeric_dot", 16)
  elif pattern in {"recovered_header_marker", "recovered_corrupted_marker"}:
    add_positive("text_pattern_recovered", 24)
  elif pattern == "textual_reference":
    add_negative("textual_question_reference", 34)
  else:
    add_positive("text_pattern_other_marker_like", 6, pattern)

  if candidate["inExpectedRange"]:
    add_positive("inside_expected_catalog_range", 22, candidate["expectedRange"])
  else:
    add_negative("outside_expected_catalog_range", 28, candidate["expectedRange"])

  sequence_state = candidate.get("sequence", {}).get("state")
  if sequence_state == "complete":
    add_positive("local_sequence_complete", 18, candidate.get("sequence"))
  elif sequence_state == "partial":
    add_positive("local_sequence_partial", 9, candidate.get("sequence"))
  elif sequence_state == "broken":
    add_negative("local_sequence_broken", 12, candidate.get("sequence"))

  if candidate.get("uniqueNumber"):
    add_positive("unique_candidate_number", 7)
  else:
    add_negative("duplicate_candidate_number", 8)

  if candidate.get("marginDelta") is not None:
    if candidate["marginDelta"] <= 0.035:
      add_positive("consistent_left_margin", 10, candidate["marginDelta"])
    elif candidate["marginDelta"] >= 0.16:
      add_negative("inconsistent_left_margin", 10, candidate["marginDelta"])

  if candidate["wordCount"] >= 6:
    add_positive("plausible_statement_start", 9, candidate["wordCount"])
  elif candidate["wordCount"] <= 2:
    add_negative("too_little_text_for_statement", 8, candidate["wordCount"])

  if candidate.get("previousGap") is not None and candidate["previousGap"] >= 8:
    add_positive("vertical_gap_before", 5, candidate["previousGap"])
  if candidate.get("nextGap") is not None and -2 <= candidate["nextGap"] <= 12:
    add_positive("near_following_body_text", 5, candidate["nextGap"])

  if candidate["source"] == "reconstructed_line":
    add_positive("from_reconstructed_line", 3, candidate.get("reconstructionConfidence"))
    if (candidate.get("reconstructionConfidence") or 0) < 0.84:
      add_negative("low_reconstruction_confidence", 8, candidate.get("reconstructionConfidence"))

  if candidate["ocrConfidence"] is not None and candidate["ocrConfidence"] >= 0.9:
    add_positive("high_ocr_confidence", 4, candidate["ocrConfidence"])
  elif candidate["ocrConfidence"] is not None and candidate["ocrConfidence"] < 0.75:
    add_negative("low_ocr_confidence", 8, candidate["ocrConfidence"])

  region = candidate.get("structuralRegion")
  if region == "body":
    add_positive("body_region", 4)
  elif region in {"header", "footer"}:
    add_negative("header_or_footer_region", 10, region)

  if candidate.get("headerFooterRecurrence", 0) >= 3:
    add_negative("recurring_header_footer_line", 32, candidate["headerFooterRecurrence"])

  text_negatives = set(candidate.get("negativeTextSignals") or [])
  if "alternative" in text_negatives:
    add_negative("alternative_line", 30)
  if "page_number" in text_negatives:
    add_negative("page_number_or_page_header", 28)
  if "instruction_or_list" in text_negatives:
    add_negative("instruction_or_list", 24)
  if "header_terms" in text_negatives:
    add_negative("header_terms_concurso_serie", 24)
  if "math_or_unit_value" in text_negatives and pattern != "questao_number":
    add_negative("math_or_unit_value", 16)
  if "plural_question_reference" in text_negatives:
    add_negative("plural_question_reference", 28)
  if "table_like" in text_negatives:
    add_negative("table_like_line", 12)
  if "questao_with_header_terms" in (candidate.get("patternWarnings") or []):
    add_negative("questao_number_ambiguous_with_header_terms", 30)

  if pattern == "numeric_dot":
    if not (candidate["inExpectedRange"] and sequence_state in {"complete", "partial"} and candidate["wordCount"] >= 6):
      add_negative("numeric_dot_missing_combined_evidence", 24)
    instruction_list = candidate.get("numericInstructionListEvidence") or {}
    if instruction_list.get("isInstructionListLike"):
      add_negative("numeric_dot_instruction_list_block", 38, instruction_list)

  strong_negative = any(item["signal"] in {
    "recurring_header_footer_line",
    "alternative_line",
    "page_number_or_page_header",
    "instruction_or_list",
    "plural_question_reference",
    "questao_number_ambiguous_with_header_terms",
  } for item in negative)
  if not candidate["inExpectedRange"] and pattern == "questao_number" and score >= 20:
    classification = "valid_marker_outside_current_scope"
  elif strong_negative and score < 45:
    classification = "reject_candidate"
  elif strong_negative:
    classification = "uncertain"
  elif score >= 70:
    classification = "strong_candidate"
  elif score >= 45:
    classification = "possible_candidate"
  elif score >= 20:
    classification = "weak_candidate"
  elif -5 <= score < 20:
    classification = "uncertain"
  else:
    classification = "reject_candidate"
  confidence = round(max(0.0, min(1.0, score / 90)), 4)
  return score, confidence, classification, positive, negative


def scorer_pattern_for_selection(text_pattern: str) -> str:
  if text_pattern == "questao_number":
    return "questao"
  if text_pattern == "numeric_dot":
    return "numeric-dot"
  return f"scorer_{text_pattern}"


def apply_marker_scorer_selection(
  ocr_payload: dict[str, Any],
  expected_numbers: list[int],
  starts: list[dict[str, Any]],
  patterns: dict[str, int],
  line_summaries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
  baseline_preflight = {
    "selectedQuestionMarkers": [
      {"page": item["page"] + 1, "number": item["number"]}
      for item in starts
      if item.get("number") in set(expected_numbers)
    ]
  }
  shadow = extract_marker_candidates_shadow(ocr_payload, expected_numbers, baseline_preflight)
  existing_keys = {
    (int(item["page"]) + 1, int(item["number"]), round(float(item.get("top") or 0), 2))
    for item in starts
  }
  existing_numbers = {int(item["number"]) for item in starts if item.get("number") in set(expected_numbers)}
  promoted: list[dict[str, Any]] = []
  for candidate in sorted(shadow["candidates"], key=lambda item: (item["page"], item["top"], item["xRel"])):
    if candidate.get("classification") != "strong_candidate":
      continue
    if not candidate.get("inExpectedRange"):
      continue
    if int(candidate["number"]) in existing_numbers:
      continue
    key = (int(candidate["page"]), int(candidate["number"]), round(float(candidate.get("top") or 0), 2))
    if key in existing_keys:
      continue
    item = {
      "number": int(candidate["number"]),
      "page": int(candidate["page"]) - 1,
      "top": float(candidate["top"]),
      "pattern": scorer_pattern_for_selection(str(candidate.get("textPattern") or "")),
      "text": candidate.get("text") or "",
      "rawText": candidate.get("rawText"),
      "markerVariant": candidate.get("markerVariant"),
      "normalizationEvidence": candidate.get("normalizationEvidence"),
      "ocrConfidence": candidate.get("ocrConfidence"),
      "structuralConfidence": candidate.get("reconstructionConfidence"),
      "markerScore": candidate.get("candidateScore"),
      "scorerConfidence": candidate.get("candidateConfidence"),
      "selectionMethod": "marker_scorer",
      "scorer": {
        "classification": candidate.get("classification"),
        "score": candidate.get("candidateScore"),
        "confidence": candidate.get("candidateConfidence"),
        "source": candidate.get("source"),
        "textPattern": candidate.get("textPattern"),
        "positiveEvidence": candidate.get("positiveEvidence"),
        "negativeEvidence": candidate.get("negativeEvidence"),
      },
    }
    promoted.append(item)
    starts.append(item)
    existing_numbers.add(item["number"])
    patterns[item["pattern"]] = patterns.get(item["pattern"], 0) + 1
    line_summaries.append({
      "page": item["page"] + 1,
      "number": item["number"],
      "pattern": item["pattern"],
      "text": str(item.get("text") or "")[:140],
      "ocrConfidence": item.get("ocrConfidence"),
      "structuralConfidence": item.get("structuralConfidence"),
      "selectionMethod": item.get("selectionMethod"),
      "scorer": item.get("scorer"),
    })
  return promoted, shadow.get("profileDiscovery")


def ocr_preflight(ocr_payload: dict[str, Any], expected_numbers: list[int], use_marker_scorer: bool = False) -> dict[str, Any]:
  expected_set = set(expected_numbers)
  starts: list[dict[str, Any]] = []
  patterns: dict[str, int] = {}
  line_summaries: list[dict[str, Any]] = []
  pages, reconstruction_metrics = pages_with_reconstructed_lines(ocr_payload)
  for page in pages:
    for line_index, line in enumerate(page.get("lines") or []):
      audit_line = line_to_audit_shape(page, line)
      marker = audit.question_marker_from_line(audit_line, expected_set)
      if marker and audit_line.get("isReconstructed") and marker.get("pattern") != "questao":
        marker = None
      if not marker:
        recovered = recover_header_embedded_marker(page, line, line_index, expected_set)
        for item in recovered:
          starts.append(item)
          patterns[item["pattern"]] = patterns.get(item["pattern"], 0) + 1
          line_summaries.append({
            "page": item["page"] + 1,
            "number": item["number"],
            "pattern": item["pattern"],
            "text": item["text"][:140],
            "ocrConfidence": item.get("ocrConfidence"),
            "structuralConfidence": item.get("structuralConfidence"),
          })
        continue
      item = {
        "number": marker["number"],
        "page": audit_line["page"],
        "top": audit_line["top"],
        "pattern": "reconstructed_line_marker" if audit_line.get("isReconstructed") else marker["pattern"],
        "text": audit_line["text"],
        "ocrConfidence": audit_line.get("confidence"),
        "structuralConfidence": audit_line.get("reconstructionConfidence") if audit_line.get("isReconstructed") else None,
      }
      if audit_line.get("isReconstructed"):
        item["reconstruction"] = {
          "sourceLine": audit_line.get("sourceLine"),
          "reconstructionConfidence": audit_line.get("reconstructionConfidence"),
        }
      starts.append(item)
      patterns[item["pattern"]] = patterns.get(item["pattern"], 0) + 1
      line_summaries.append({
        "page": audit_line["page"] + 1,
        "number": marker["number"],
        "pattern": item["pattern"],
        "text": audit_line["text"][:140],
        "ocrConfidence": audit_line.get("confidence"),
        "structuralConfidence": item.get("structuralConfidence"),
        "reconstruction": item.get("reconstruction"),
      })

  confirmed_positions = sorted(
    [
      {"number": item["number"], "page": item["page"], "top": item["top"]}
      for item in starts
      if item["number"] in expected_set and item.get("pattern") in {"questao", "recovered_header_marker", "reconstructed_line_marker"}
    ],
    key=lambda item: (item["page"], item["top"]),
  )
  strong_existing_numbers = {item["number"] for item in confirmed_positions}
  for page in pages:
    for line_index, line in enumerate(page.get("lines") or []):
      for item in recover_corrupted_marker(page, line, line_index, expected_set, confirmed_positions, strong_existing_numbers):
        if item["number"] in strong_existing_numbers:
          continue
        starts.append(item)
        strong_existing_numbers.add(item["number"])
        confirmed_positions.append({"number": item["number"], "page": item["page"], "top": item["top"]})
        confirmed_positions.sort(key=lambda value: (value["page"], value["top"]))
        patterns[item["pattern"]] = patterns.get(item["pattern"], 0) + 1
        line_summaries.append({
          "page": item["page"] + 1,
          "number": item["number"],
          "pattern": item["pattern"],
          "text": item["text"][:140],
          "ocrConfidence": item.get("ocrConfidence"),
          "structuralConfidence": item.get("structuralConfidence"),
        })

  scorer_promoted = []
  profile_discovery: dict[str, Any] = {"status": "not_computed", "reason": "marker_scorer_disabled"}
  if use_marker_scorer:
    scorer_promoted, profile_discovery = apply_marker_scorer_selection(
      ocr_payload, expected_numbers, starts, patterns, line_summaries
    )

  dedup: dict[int, dict[str, Any]] = {}
  for start in sorted(starts, key=lambda item: (item["page"], item["top"])):
    if start["number"] not in expected_set:
      continue
    if start.get("selectionMethod") == "marker_scorer" and start.get("markerScore") is not None:
      scored = start
    elif str(start.get("pattern", "")).startswith("recovered_") or start.get("pattern") == "reconstructed_line_marker":
      scored = {**start, "markerScore": round(float(start.get("structuralConfidence") or 0) * 35, 4)}
    else:
      scored = {**start, "markerScore": round(audit.marker_candidate_score(start, expected_set), 4)}
    previous = dedup.get(start["number"])
    if previous is None or scored["markerScore"] > previous.get("markerScore", -999):
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
  detected = annotate_question_confidences(detected, expected_numbers, status)
  high_association_count = sum(1 for item in detected if item["questionAssociationConfidence"]["level"] == "high")
  high_boundary_count = sum(1 for item in detected if item["boundaryConfidence"]["level"] == "high")
  content_eligible_count = sum(1 for item in detected if item["contentAuditEligibility"])

  return {
    "status": status,
    "expectedQuestions": expected_count,
    "detectedQuestions": detected_count,
    "highConfidenceAssociations": high_association_count,
    "highBoundaryQuestions": high_boundary_count,
    "contentAuditEligibleQuestions": content_eligible_count,
    "missingQuestions": [number for number in expected_numbers if number not in dedup],
    "extraQuestionMarkers": [item["number"] for item in starts if item["number"] not in expected_set],
    "selectedQuestionMarkers": [
      {
        "page": item["page"] + 1,
        "number": item["number"],
        "top": item.get("top"),
        "bbox": item.get("bbox"),
          "pattern": item["pattern"],
        "markerScore": item.get("markerScore"),
          "markerConfidence": item.get("markerConfidence"),
          "ocrConfidence": item.get("ocrConfidence"),
          "structuralConfidence": item.get("structuralConfidence"),
          "questionAssociationConfidence": item.get("questionAssociationConfidence"),
          "boundaryConfidence": item.get("boundaryConfidence"),
          "contentAuditEligibility": item.get("contentAuditEligibility"),
          "recovery": item.get("recovery"),
          "reconstruction": item.get("reconstruction"),
          "selectionMethod": item.get("selectionMethod"),
          "scorer": item.get("scorer"),
          "markerVariant": item.get("markerVariant"),
          "normalizationEvidence": item.get("normalizationEvidence"),
          "text": str(item.get("text", ""))[:140],
        }
        for item in detected
    ],
    "questionMarkers": line_summaries[:80],
    "markerPatterns": patterns,
    "recoveredMarkers": [
      {
        "page": item["page"] + 1,
        "number": item["number"],
        "pattern": item.get("pattern"),
        "markerScore": item.get("markerScore"),
        "markerConfidence": item.get("markerConfidence"),
        "ocrConfidence": item.get("ocrConfidence"),
        "structuralConfidence": item.get("structuralConfidence"),
        "questionAssociationConfidence": item.get("questionAssociationConfidence"),
        "boundaryConfidence": item.get("boundaryConfidence"),
        "contentAuditEligibility": item.get("contentAuditEligibility"),
        "recovery": item.get("recovery"),
        "selectionMethod": item.get("selectionMethod"),
        "scorer": item.get("scorer"),
      }
      for item in detected
      if str(item.get("pattern", "")).startswith("recovered_")
    ],
    "reconstructedMarkers": [
      {
        "page": item["page"] + 1,
        "number": item["number"],
        "pattern": item.get("pattern"),
        "markerScore": item.get("markerScore"),
        "markerConfidence": item.get("markerConfidence"),
        "ocrConfidence": item.get("ocrConfidence"),
        "structuralConfidence": item.get("structuralConfidence"),
        "questionAssociationConfidence": item.get("questionAssociationConfidence"),
        "boundaryConfidence": item.get("boundaryConfidence"),
        "contentAuditEligibility": item.get("contentAuditEligibility"),
        "reconstruction": item.get("reconstruction"),
        "selectionMethod": item.get("selectionMethod"),
        "scorer": item.get("scorer"),
      }
      for item in detected
      if item.get("pattern") == "reconstructed_line_marker"
    ],
    "scorerPromotedMarkers": [
      {
        "page": item["page"] + 1,
        "number": item["number"],
        "pattern": item.get("pattern"),
        "markerScore": item.get("markerScore"),
        "scorerConfidence": item.get("scorerConfidence"),
        "ocrConfidence": item.get("ocrConfidence"),
        "structuralConfidence": item.get("structuralConfidence"),
        "text": str(item.get("text") or "")[:140],
        "scorer": item.get("scorer"),
      }
      for item in scorer_promoted
    ],
    "markerScorerEnabled": bool(use_marker_scorer),
    "profileDiscovery": profile_discovery,
    "lineReconstruction": reconstruction_metrics,
    "segmentationConfidence": round(segmentation_confidence, 4),
    "monotonic": monotonic,
  }


def component_clues(ocr_payload: dict[str, Any]) -> dict[str, Any]:
  texts = []
  confidences = []
  table_like = 0
  formula_like = 0
  for page in ocr_payload.get("pages") or []:
    for line in page.get("lines") or []:
      text = str(line.get("text") or "")
      texts.append(text)
      if line.get("confidence") is not None:
        confidences.append(float(line["confidence"]))
      if "|" in text or "\t" in text or text.count("  ") >= 3:
        table_like += 1
      if any(symbol in text for symbol in ["=", "+", "−", "-", "×", "÷", "/", "%"]) and any(ch.isdigit() for ch in text):
        formula_like += 1
  joined = "\n".join(texts)
  return {
    "pagesWithText": sum(1 for page in ocr_payload.get("pages") or [] if int(page.get("chars") or 0) > 30),
    "averageLineConfidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
    "tableLikeLines": table_like,
    "formulaLikeLines": formula_like,
    "hasAlternativesClue": bool(__import__("re").search(r"(?m)^\s*[A-E]\s*(?:[).:\-]|[\(\)])", joined)),
  }


def ocr_cache_path(args: argparse.Namespace, proof: dict[str, Any]) -> Path:
  return Path(args.output_dir) / slugify(Path(proof["pdf"]).stem) / args.engine / "ocr.json"


def cache_validation_error(cache: dict[str, Any], args: argparse.Namespace, proof: dict[str, Any], fingerprint: dict[str, Any]) -> str | None:
  pdf_path = Path(proof["pdf"])
  if Path(str(cache.get("pdf") or "")) != pdf_path:
    return f"PDF de origem difere: cache={cache.get('pdf')} esperado={pdf_path}"
  if cache.get("engine") != args.engine:
    return f"engine difere: cache={cache.get('engine')} esperado={args.engine}"
  if int(cache.get("dpi") or 0) != int(args.dpi):
    return f"dpi difere: cache={cache.get('dpi')} esperado={args.dpi}"
  expected_psm = args.psm if args.engine == "tesseract" else None
  if cache.get("psm") != expected_psm:
    return f"psm difere: cache={cache.get('psm')} esperado={expected_psm}"
  expected_lang = args.lang if args.engine == "tesseract" else None
  if cache.get("lang") != expected_lang:
    return f"lang difere: cache={cache.get('lang')} esperado={expected_lang}"
  if cache.get("firstPage") is not None or cache.get("lastPage") is not None:
    return "cache parcial: firstPage/lastPage nao sao nulos"
  pages = cache.get("pages") or []
  if int(cache.get("pagesProcessed") or 0) != len(pages):
    return f"pagesProcessed difere da lista de paginas: {cache.get('pagesProcessed')} vs {len(pages)}"
  if not pages:
    return "cache sem paginas OCR"
  page_numbers = [int(page.get("page") or 0) for page in pages]
  if page_numbers != list(range(1, len(pages) + 1)):
    return f"paginas processadas nao sao contiguas: {page_numbers[:10]}"
  cached_fingerprint = cache.get("pdfFingerprint")
  if cached_fingerprint:
    for key in ["sha256", "sizeBytes"]:
      if cached_fingerprint.get(key) != fingerprint.get(key):
        return f"fingerprint {key} difere: cache={cached_fingerprint.get(key)} esperado={fingerprint.get(key)}"
  return None


def load_cached_ocr(args: argparse.Namespace, proof: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
  path = ocr_cache_path(args, proof)
  if not path.exists():
    raise SystemExit(f"Cache OCR ausente para {proof['school']} {proof['year']}: {path}")
  cache = json.loads(path.read_text(encoding="utf-8"))
  fingerprint = file_fingerprint(Path(proof["pdf"]))
  error = cache_validation_error(cache, args, proof, fingerprint)
  if error:
    raise SystemExit(f"Cache OCR incompativel para {proof['school']} {proof['year']}: {error}")
  metadata_backfilled = False
  if not cache.get("pdfFingerprint"):
    cache["pdfFingerprint"] = fingerprint
    cache["cacheMetadataBackfilled"] = True
    metadata_backfilled = True
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
  engine_version_status = "available" if cache.get("engineVersion") else "not_available_in_cache"
  return cache, {
    "json": str(path),
    "engine": cache.get("engine"),
    "engineVersion": cache.get("engineVersion"),
    "engineVersionStatus": engine_version_status,
    "dpi": cache.get("dpi"),
    "psm": cache.get("psm"),
    "lang": cache.get("lang"),
    "elapsedSeconds": 0,
    "originalElapsedSeconds": cache.get("elapsedSeconds"),
    "pagesProcessed": cache.get("pagesProcessed"),
    "averageConfidence": cache.get("averageConfidence"),
    "totalChars": cache.get("totalChars"),
    "markerCounts": cache.get("markerCounts"),
    "cache": {
      "mode": "reused",
      "validated": True,
      "metadataBackfilled": metadata_backfilled,
      "pdfFingerprint": cache.get("pdfFingerprint"),
    },
  }


def run_pilot(args: argparse.Namespace) -> dict[str, Any]:
  if args.reuse_ocr and args.clean:
    raise SystemExit("--clean nao pode ser usado junto com --reuse-ocr, pois apagaria os caches antes da leitura.")
  catalog = load_effective_catalog()
  results = []
  start_all = time.perf_counter()
  for proof in PILOT_PROOFS:
    questions = catalog_questions(catalog, proof["school"], proof["year"])
    expected_numbers = [int(question["number"]) for question in questions]
    ocr_args = argparse.Namespace(
      pdf=proof["pdf"],
      engine=args.engine,
      output_dir=args.output_dir,
      dpi=args.dpi,
      first_page=None,
      last_page=None,
      tesseract=args.tesseract,
      tessdata=args.tessdata,
      lang=args.lang,
      psm=args.psm,
      clean=args.clean,
    )
    if args.reuse_ocr:
      ocr_payload, ocr_result = load_cached_ocr(args, proof)
    else:
      ocr_result = run_ocr(ocr_args)
      ocr_payload = json.loads(Path(ocr_result["json"]).read_text(encoding="utf-8"))
      ocr_result["cache"] = {"mode": "generated", "validated": False}
    preflight = ocr_preflight(ocr_payload, expected_numbers, use_marker_scorer=bool(args.use_marker_scorer))
    clues = component_clues(ocr_payload)
    results.append({
      **proof,
      "expectedQuestions": len(expected_numbers),
      "ocr": ocr_result,
      "preflight": preflight,
      "clues": clues,
    })
  summary = {
    "mode": "read-only",
    "engine": args.engine,
    "dpi": args.dpi,
    "reuseOcr": bool(args.reuse_ocr),
    "useMarkerScorer": bool(args.use_marker_scorer),
    "elapsedSeconds": round(time.perf_counter() - start_all, 3),
    "proofs": results,
    "aggregate": aggregate(results),
  }
  write_outputs(summary)
  return summary


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
  total_expected = sum(item["expectedQuestions"] for item in results)
  total_detected = sum(item["preflight"]["detectedQuestions"] for item in results)
  total_high = sum(item["preflight"]["highConfidenceAssociations"] for item in results)
  total_high_boundary = sum(item["preflight"].get("highBoundaryQuestions") or 0 for item in results)
  total_content_eligible = sum(item["preflight"].get("contentAuditEligibleQuestions") or 0 for item in results)
  statuses: dict[str, int] = {}
  for item in results:
    status = item["preflight"]["status"]
    statuses[status] = statuses.get(status, 0) + 1
  return {
    "proofCount": len(results),
    "expectedQuestions": total_expected,
    "detectedQuestions": total_detected,
    "segmentationRate": round(total_detected / total_expected, 4) if total_expected else None,
    "highConfidenceAssociations": total_high,
    "highConfidenceAssociationRate": round(total_high / total_expected, 4) if total_expected else None,
    "highBoundaryQuestions": total_high_boundary,
    "contentAuditEligibleQuestions": total_content_eligible,
    "statuses": statuses,
    "averageOcrConfidence": round(sum(item["ocr"].get("averageConfidence") or 0 for item in results) / len(results), 4) if results else None,
    "averageStructuralConfidence": round(sum(item["preflight"].get("segmentationConfidence") or 0 for item in results) / len(results), 4) if results else None,
    "pagesProcessed": sum(item["ocr"].get("pagesProcessed") or 0 for item in results),
    "pagesWithText": sum(item["clues"].get("pagesWithText") or 0 for item in results),
    "elapsedSeconds": round(sum(item["ocr"].get("elapsedSeconds") or 0 for item in results), 3),
    "reusedCaches": sum(1 for item in results if (item["ocr"].get("cache") or {}).get("mode") == "reused"),
    "generatedOcrRuns": sum(1 for item in results if (item["ocr"].get("cache") or {}).get("mode") == "generated"),
  }


def write_outputs(summary: dict[str, Any]) -> None:
  SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
  SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
  with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=[
      "school", "year", "pagesProcessed", "pagesWithText", "expectedQuestions",
      "detectedQuestions", "highConfidenceAssociations", "status", "averageConfidence",
      "structuralConfidence", "highBoundaryQuestions", "contentAuditEligibleQuestions",
      "markerPatterns", "missingQuestions", "elapsedSeconds", "cacheMode",
    ])
    writer.writeheader()
    for item in summary["proofs"]:
      writer.writerow({
        "school": item["school"],
        "year": item["year"],
        "pagesProcessed": item["ocr"].get("pagesProcessed"),
        "pagesWithText": item["clues"].get("pagesWithText"),
        "expectedQuestions": item["expectedQuestions"],
        "detectedQuestions": item["preflight"].get("detectedQuestions"),
        "highConfidenceAssociations": item["preflight"].get("highConfidenceAssociations"),
        "status": item["preflight"].get("status"),
        "averageConfidence": item["ocr"].get("averageConfidence"),
        "structuralConfidence": item["preflight"].get("segmentationConfidence"),
        "highBoundaryQuestions": item["preflight"].get("highBoundaryQuestions"),
        "contentAuditEligibleQuestions": item["preflight"].get("contentAuditEligibleQuestions"),
        "markerPatterns": json.dumps(item["preflight"].get("markerPatterns"), ensure_ascii=False),
        "missingQuestions": json.dumps(item["preflight"].get("missingQuestions"), ensure_ascii=False),
        "elapsedSeconds": item["ocr"].get("elapsedSeconds"),
        "cacheMode": (item["ocr"].get("cache") or {}).get("mode"),
      })
  SUMMARY_MD.write_text(render_markdown(summary), encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
  aggregate_data = summary["aggregate"]
  lines = [
    "# Piloto OCR Raster",
    "",
    "Experimento somente leitura. A camada OCR gera artefatos intermediarios em `outputs/audit/ocr/` e nao altera catalogo, banco, revisoes, locks, autenticacoes, importador ou questoes.",
    "",
    "## Agregado",
    "",
    f"- Engine: `{summary['engine']}`; dpi: `{summary['dpi']}`.",
    f"- Reuso de cache OCR: {summary.get('reuseOcr')}.",
    f"- Provas: {aggregate_data['proofCount']}.",
    f"- Paginas OCR: {aggregate_data['pagesProcessed']}; paginas com texto: {aggregate_data['pagesWithText']}.",
    f"- Questoes esperadas/detectadas: {aggregate_data['expectedQuestions']}/{aggregate_data['detectedQuestions']} ({aggregate_data['segmentationRate']:.1%}).",
    f"- Associacoes de alta confianca: {aggregate_data['highConfidenceAssociations']} ({aggregate_data['highConfidenceAssociationRate']:.1%}).",
    f"- Fronteiras de alta confianca: {aggregate_data['highBoundaryQuestions']}; elegiveis para auditoria de conteudo: {aggregate_data['contentAuditEligibleQuestions']}.",
    f"- Status: {aggregate_data['statuses']}.",
    f"- Confianca OCR media: {aggregate_data['averageOcrConfidence']}; confianca estrutural media: {aggregate_data['averageStructuralConfidence']}.",
    f"- Caches reutilizados: {aggregate_data['reusedCaches']}; OCRs gerados nesta execucao: {aggregate_data['generatedOcrRuns']}.",
    f"- Tempo OCR somado: {aggregate_data['elapsedSeconds']}s.",
    "",
    "## Provas",
    "",
  ]
  for item in summary["proofs"]:
    preflight = item["preflight"]
    ocr = item["ocr"]
    clues = item["clues"]
    lines += [
      f"### {item['school']} {item['year']}",
      "",
      f"- Motivo da escolha: {item['reason']}",
      f"- PDF: `{item['pdf']}`",
      f"- Cache OCR: {(ocr.get('cache') or {}).get('mode')}; engineVersion={ocr.get('engineVersion')}; engineVersionStatus={ocr.get('engineVersionStatus')}.",
      f"- Paginas OCR/texto: {ocr.get('pagesProcessed')}/{clues.get('pagesWithText')}; chars: {ocr.get('totalChars')}; confianca media: {ocr.get('averageConfidence')}.",
      f"- Questoes esperadas/detectadas: {item['expectedQuestions']}/{preflight.get('detectedQuestions')}; associacao alta: {preflight.get('highConfidenceAssociations')}; fronteira alta: {preflight.get('highBoundaryQuestions')}; elegiveis conteudo: {preflight.get('contentAuditEligibleQuestions')}; structuralConfidence={preflight.get('segmentationConfidence')}.",
      f"- Preflight OCR: `{preflight.get('status')}`; monotonic={preflight.get('monotonic')}; padroes={preflight.get('markerPatterns')}.",
      f"- Ausentes: {preflight.get('missingQuestions')[:20]}",
      f"- Linhas tipo tabela: {clues.get('tableLikeLines')}; linhas tipo formula/numerica: {clues.get('formulaLikeLines')}; pistas de alternativas: {clues.get('hasAlternativesClue')}.",
      f"- Artefato: `{ocr.get('json')}`",
      "",
    ]
  return "\n".join(lines)


def main() -> None:
  parser = argparse.ArgumentParser(description="Piloto OCR estrutural para PDFs rasterizados do SimpleQuest.")
  parser.add_argument("--engine", choices=["tesseract", "rapidocr"], default="rapidocr")
  parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
  parser.add_argument("--dpi", type=int, default=160)
  parser.add_argument("--tesseract", default=str(DEFAULT_TESSERACT))
  parser.add_argument("--tessdata", default=str(DEFAULT_TESSDATA))
  parser.add_argument("--lang", default="por+eng")
  parser.add_argument("--psm", type=int, default=6)
  parser.add_argument("--reuse-ocr", action="store_true", help="Reutiliza ocr.json existente e falha se o cache estiver ausente ou incompativel.")
  parser.add_argument("--use-marker-scorer", action="store_true", help="Ativa experimentalmente a promocao de candidatos strong_candidate do marker scorer.")
  parser.add_argument("--clean", action="store_true")
  args = parser.parse_args()
  print(json.dumps(run_pilot(args)["aggregate"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
