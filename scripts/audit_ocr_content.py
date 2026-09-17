from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median
from typing import Any

import audit_pdf_mvp as audit
import ocr_raster_pilot as pilot


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "audit"
CACHE_DIR = ROOT / "outputs" / "audit" / "ocr"
SUMMARY_JSON = ROOT / "outputs" / "audit" / "ocr-content-pilot.json"
SUMMARY_MD = ROOT / "outputs" / "audit" / "ocr-content-pilot.md"

LOW_CONFIDENCE = 0.75
DUBIOUS_CHARS = set("\ufffd~|[]{}^\\@#*¤±")

# Keys must match audit.COMPONENTS (singular: table/formula).
OCR_CAPABILITIES: dict[str, bool] = {
  "text": True,
  "alternatives": True,
  "punctuation": True,
  "capitalization": True,
  "inlineFormatting": False,
  "table": False,
  "formula": False,
  "media": False,
}
OBSERVABLE_COMPONENTS = ["text", "punctuation", "capitalization", "alternatives"]

PILOT_CASES = [
  {"school": "CMB", "year": 2019, "slug": "cmb-6ano-2019-2020-mat", "questions": [1, 6, 11]},
  {"school": "CMBH", "year": 2017, "slug": "cmbh-6ano-2017-2018-mat", "questions": [2, 5, 19]},
  {"school": "CMBel", "year": 2021, "slug": "cmbel-6ano-2021-2022", "questions": [2, 5, 9]},
  {"school": "CMB", "year": 2016, "slug": "cmb-6ano-2016-2017-mat", "questions": [1, 4, 9]},
  {"school": "CMC", "year": 2011, "slug": "cmc-6ano-2011-2012-mat", "questions": [13, 14, 15]},
]
NON_ELIGIBLE_CONTROL = {"school": "CMC", "year": 2011, "slug": "cmc-6ano-2011-2012-mat", "question": 13}


@dataclass
class OcrAuditWord:
  text: str
  page: int
  bbox: tuple[float, float, float, float]
  ocrConfidence: float | None
  reconstructionConfidence: float | None
  isReconstructed: bool
  dubiousCharacterEvidence: list[str] = field(default_factory=list)
  role: str = "stem"

  def to_dict(self) -> dict[str, Any]:
    return {
      "text": self.text,
      "page": self.page,
      "bbox": [round(value, 2) for value in self.bbox],
      "ocrConfidence": self.ocrConfidence,
      "reconstructionConfidence": self.reconstructionConfidence,
      "isReconstructed": self.isReconstructed,
      "dubiousCharacterEvidence": self.dubiousCharacterEvidence,
      "role": self.role,
    }


def load_payload(slug: str) -> dict[str, Any]:
  path = CACHE_DIR / slug / "tesseract" / "ocr.json"
  return json.loads(path.read_text(encoding="utf-8"))


def percentile(values: list[float], fraction: float) -> float | None:
  if not values:
    return None
  ordered = sorted(values)
  index = max(0, min(len(ordered) - 1, int(round(fraction * (len(ordered) - 1)))))
  return round(ordered[index], 4)


def dubious_evidence(text: str, confidence: float | None) -> list[str]:
  evidence = [f"char:{char}" for char in text if char in DUBIOUS_CHARS]
  if confidence is not None and confidence < 0.5:
    evidence.append("very_low_conf_token")
  return evidence


def normalize_ocr_marker_case(text: str) -> str:
  # OCR sometimes reads option markers as lowercase "(a)". The auditor's
  # parse_alternatives only recognises uppercase in parentheses. This is an
  # OCR-only case normalization of the marker glyph; it never touches content.
  text = re.sub(
    r"(?m)^(\s*)\(([a-e])\)",
    lambda match: f"{match.group(1)}({match.group(2).upper()})",
    text,
  )
  text = re.sub(
    r"(?m)^(\s*)([a-e])([).:\-–—])",
    lambda match: f"{match.group(1)}{match.group(2).upper()}{match.group(3)}",
    text,
  )
  return text


def build_pilot_context(payload: dict[str, Any], expected_numbers: list[int]) -> dict[str, Any]:
  base_preflight = pilot.ocr_preflight(payload, expected_numbers, use_marker_scorer=False)
  shadow = pilot.extract_marker_candidates_shadow(payload, expected_numbers, base_preflight)
  scope = shadow["pageRoleDiscovery"]
  in_scope_pages = {feature["pageNumber"] for feature in scope["pages"] if feature["questionScope"] == "question_scope"}
  scope_roles = {feature["pageNumber"]: feature["pageRole"] for feature in scope["pages"]}
  marker_preflight = pilot.ocr_preflight(payload, expected_numbers, use_marker_scorer=True)
  markers = sorted(
    marker_preflight["selectedQuestionMarkers"],
    key=lambda item: (int(item["page"]), float(item.get("top") or 0)),
  )
  pages, _ = pilot.pages_with_reconstructed_lines(payload)
  return {
    "pages": {int(page["page"]): page for page in pages},
    "markers": markers,
    "in_scope_pages": in_scope_pages,
    "scope": scope,
    "scope_roles": scope_roles,
    "marker_preflight": marker_preflight,
  }


def find_question_marker(markers: list[dict[str, Any]], in_scope_pages: set[int], number: int) -> dict[str, Any] | None:
  for marker in markers:
    if int(marker["number"]) != number:
      continue
    if int(marker["page"]) not in in_scope_pages:
      continue
    if marker.get("contentAuditEligibility"):
      return marker
  return None


def find_region_end(markers: list[dict[str, Any]], start_index: int, in_scope_pages: set[int]) -> dict[str, Any] | None:
  for marker in markers[start_index + 1:]:
    if int(marker["page"]) not in in_scope_pages:
      continue
    association = (marker.get("questionAssociationConfidence") or {}).get("level")
    if marker.get("contentAuditEligibility") or association == "high":
      return marker
  return None


ALTERNATIVE_MARKER_RE = re.compile(
  r"^\s*(?:[A-E]\s*(?:\(\s*\)|[).:\-–—])|\(\s*[A-E]\s*\))",
  re.IGNORECASE,
)


def collect_region(
  context: dict[str, Any],
  start_page: int,
  start_top: float,
  end_page: int,
  end_top: float | None,
  recurring: dict[str, int],
) -> dict[str, Any]:
  pages = context["pages"]
  in_scope_pages = context["in_scope_pages"]
  text_parts: list[str] = []
  words: list[OcrAuditWord] = []
  line_confidences: list[float] = []
  in_alternatives = False
  stem_end_delimited = False
  for page_number in range(start_page, end_page + 1):
    if page_number not in in_scope_pages:
      continue
    page = pages.get(page_number)
    if not page:
      continue
    for line in page.get("lines") or []:
      shape = pilot.line_to_audit_shape(page, line)
      top = float(shape["top"])
      if page_number == start_page and top < start_top - 1:
        continue
      if end_top is not None and page_number == end_page and top >= end_top - 1:
        continue
      key = pilot.normalized_line_key(str(line.get("text") or ""))
      region = pilot.structural_region(page, shape)
      if region in {"header", "footer"} and recurring.get(key, 0) >= 3:
        continue
      text = str(line.get("text") or "")
      if not in_alternatives and ALTERNATIVE_MARKER_RE.match(text):
        in_alternatives = True
        stem_end_delimited = True
      text_parts.append(text)
      if line.get("confidence") is not None:
        line_confidences.append(float(line["confidence"]))
      role = "alternative" if in_alternatives else "stem"
      for word in pilot.line_words(page, line):
        confidence = word.get("confidence")
        words.append(OcrAuditWord(
          text=str(word.get("text") or ""),
          page=page_number,
          bbox=tuple(float(value) for value in word.get("bbox") or (0, 0, 0, 0)),
          ocrConfidence=float(confidence) if confidence is not None else None,
          reconstructionConfidence=line.get("reconstructionConfidence"),
          isReconstructed=bool(line.get("isReconstructed")),
          dubiousCharacterEvidence=dubious_evidence(str(word.get("text") or ""), confidence),
          role=role,
        ))
  return {
    "text": "\n".join(text_parts).strip(),
    "words": words,
    "lineConfidences": line_confidences,
    "stemEndDelimited": stem_end_delimited,
  }


def region_metrics(words: list[OcrAuditWord], line_confidences: list[float]) -> dict[str, Any]:
  confidences = [word.ocrConfidence for word in words if word.ocrConfidence is not None]
  total = len(words)
  reconstructed = sum(1 for word in words if word.isReconstructed)
  dubious = sum(1 for word in words if word.dubiousCharacterEvidence)
  characters = sum(len(word.text) for word in words)
  dubious_characters = sum(len(word.dubiousCharacterEvidence) for word in words if word.dubiousCharacterEvidence)
  return {
    "tokenCount": total,
    "meanWordConfidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
    "medianWordConfidence": round(median(confidences), 4) if confidences else None,
    "p10WordConfidence": percentile(confidences, 0.1),
    "lowConfidenceTokenShare": round(sum(1 for c in confidences if c < LOW_CONFIDENCE) / len(confidences), 4) if confidences else None,
    "reconstructedTokenShare": round(reconstructed / total, 4) if total else 0.0,
    "dubiousCharacterCount": dubious_characters,
    "dubiousCharacterShare": round(dubious_characters / characters, 4) if characters else 0.0,
    "lineConfidence": round(sum(line_confidences) / len(line_confidences), 4) if line_confidences else None,
  }


def build_ocr_extracted_question(
  number: int,
  text: str,
  pages_used: list[int],
  start: dict[str, Any],
) -> audit.PdfQuestion:
  boundary = start.get("boundaryConfidence") or {}
  boundary_score = float(boundary.get("score") or (0.95 if boundary.get("level") == "high" else 0.55))
  structure = {
    "question_boundary": boundary_score,
    "header_footer_cleaning": 0.85,
    "markerPattern": start.get("pattern"),
  }
  return audit.PdfQuestion(
    number=number,
    text=text,
    pages=pages_used,
    image_count=0,
    bold_word_count=0,
    italic_word_count=0,
    font_samples=[],
    words=[],
    tables=[],
    formulas=[],
    structure=structure,
    capabilities=dict(OCR_CAPABILITIES),
  )


def word_metrics(words: list[OcrAuditWord]) -> dict[str, Any]:
  confidences = [word.ocrConfidence for word in words if word.ocrConfidence is not None]
  total = len(words)
  reconstructed = sum(1 for word in words if word.isReconstructed)
  characters = sum(len(word.text) for word in words)
  dubious_characters = sum(len(word.dubiousCharacterEvidence) for word in words if word.dubiousCharacterEvidence)
  return {
    "tokenCount": total,
    "meanWordConfidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
    "medianWordConfidence": round(median(confidences), 4) if confidences else None,
    "p10WordConfidence": percentile(confidences, 0.1),
    "lowConfidenceTokenShare": round(sum(1 for c in confidences if c < LOW_CONFIDENCE) / len(confidences), 4) if confidences else None,
    "reconstructedTokenShare": round(reconstructed / total, 4) if total else 0.0,
    "dubiousCharacterCount": dubious_characters,
    "dubiousCharacterShare": round(dubious_characters / characters, 4) if characters else 0.0,
  }


def stem_metrics_of(words: list[OcrAuditWord]) -> dict[str, Any]:
  stem = [word for word in words if word.role == "stem"]
  metrics = word_metrics(stem)
  metrics["stemTokenCount"] = len(stem)
  return metrics


def alternative_metrics_of(words: list[OcrAuditWord]) -> dict[str, Any]:
  alternative = [word for word in words if word.role == "alternative"]
  metrics = word_metrics(alternative)
  metrics["alternativeTokenCount"] = len(alternative)
  return metrics


def confidence_band(metrics: dict[str, Any]) -> str:
  # Descriptive, experimental bands. Not a definitive threshold.
  p10 = metrics.get("p10WordConfidence")
  median = metrics.get("medianWordConfidence")
  low_share = metrics.get("lowConfidenceTokenShare")
  if p10 is None or median is None:
    return "descriptive_low"
  if p10 >= 0.90 and median >= 0.93 and (low_share or 0) <= 0.05 and (metrics.get("dubiousCharacterShare") or 0) <= 0.01:
    return "descriptive_high"
  if p10 >= 0.70 and (low_share or 0) <= 0.20:
    return "descriptive_medium"
  return "descriptive_low"


def band_level(band: str) -> str:
  return {"descriptive_high": "high", "descriptive_medium": "medium", "descriptive_low": "low"}.get(band, "low")


def intrinsic_alternatives(text: str) -> tuple[str, dict[str, str], str]:
  # Observation-only split: explicit uppercase A-E markers (case normalization
  # already applied). No catalog involvement.
  explicit = audit.parse_alternatives(text)
  if explicit:
    match = re.search(r"(?m)^\s*(?:[A-E]\s*(?:\(\s*\)|[).:\-–—])|\(\s*[A-E]\s*\))\s*", text)
    stem = text[:match.start()] if match else text
    return "explicit", explicit, stem
  return "none", {}, text


SHARED_STRONG = [
  "responder as quest", "responda as quest", "questoes de", "questoes 0",
  "leia o texto", "com base no texto", "de acordo com o texto",
  "no texto", "texto acima", "segundo o texto", "texto i", "texto 1",
]
SHARED_POSSIBLE = [
  "observe a figura", "figura abaixo", "figura a seguir", "imagem a seguir",
  "observe o grafico", "tabela abaixo",
]


def shared_context_risk(context_text: str, region_text: str) -> tuple[str, dict[str, Any]]:
  # Intrinsic only: looks at OCR text before the marker and inside the region.
  haystack = audit.strip_accents(f"{context_text}\n{region_text}").lower()
  strong = sorted({pattern for pattern in SHARED_STRONG if pattern in haystack})
  possible = sorted({pattern for pattern in SHARED_POSSIBLE if pattern in haystack})
  if strong:
    return "strong", {"strong": strong, "possible": possible}
  if possible:
    return "possible", {"strong": [], "possible": possible}
  return "none", {"strong": [], "possible": []}


def _confidence(level: str, evidence: list[str], blockers: list[str], metrics: dict[str, Any], observed: int | None = None) -> dict[str, Any]:
  payload = {
    "level": level,
    "evidence": evidence,
    "blockers": blockers,
    "metrics": {
      "meanWordConfidence": metrics.get("meanWordConfidence"),
      "medianWordConfidence": metrics.get("medianWordConfidence"),
      "p10WordConfidence": metrics.get("p10WordConfidence"),
      "lowConfidenceTokenShare": metrics.get("lowConfidenceTokenShare"),
      "reconstructedTokenShare": metrics.get("reconstructedTokenShare"),
      "dubiousCharacterShare": metrics.get("dubiousCharacterShare"),
    },
  }
  if observed is not None:
    payload["observedTokenCount"] = observed
  return payload


def stem_confidence(band: str, boundary_ok: bool, stem_end_delimited: bool, risk: str, metrics: dict[str, Any]) -> dict[str, Any]:
  level = band_level(band)
  evidence = [
    f"stem_band:{band}",
    f"boundary:{'high' if boundary_ok else 'low'}",
    f"stem_end_delimited:{stem_end_delimited}",
    f"shared_context:{risk}",
  ]
  blockers: list[str] = []
  if not boundary_ok:
    blockers.append("boundary_nao_confiavel")
    level = "low"
  if not stem_end_delimited:
    # Without a reliable end the stem cannot be isolated from alternatives.
    blockers.append("stem_end_not_delimited")
    level = "low"
  if (metrics.get("reconstructedTokenShare") or 0) > 0.5:
    blockers.append("reconstrucao_dominante")
    if level == "high":
      level = "medium"
  if risk in {"strong", "possible"}:
    # Structural blocker only; it does not mean the OCR read poorly.
    blockers.append(f"shared_context_{risk}")
  return _confidence(level, evidence, blockers, metrics, observed=metrics.get("stemTokenCount"))


def alternatives_confidence(band: str, boundary_ok: bool, method: str, alternatives: dict[str, str], metrics: dict[str, Any]) -> dict[str, Any]:
  evidence = [f"alternative_band:{band}", f"method:{method}", f"detected:{len(alternatives)}"]
  observed = metrics.get("alternativeTokenCount")
  blockers: list[str] = []
  if method != "explicit":
    blockers.append("metodo_nao_explicito")
    return _confidence("low", evidence, blockers, metrics, observed=observed)
  if len(alternatives) < 2:
    blockers.append("poucas_alternativas")
    return _confidence("low", evidence, blockers, metrics, observed=observed)
  empty = [option for option, value in alternatives.items() if not value.strip()]
  if empty:
    blockers.append("alternativa_sem_texto")
  level = band_level(band)
  if not boundary_ok:
    blockers.append("boundary_nao_confiavel")
    level = "low"
  elif empty and level == "high":
    level = "medium"
  return _confidence(level, evidence, blockers, metrics, observed=observed)


def token_confidence(kind: str, stem_band: str, boundary_ok: bool, stem_end_delimited: bool, words: list[OcrAuditWord]) -> dict[str, Any]:
  # Computed ONLY over stem tokens: alternatives can neither dilute nor improve it.
  pattern = re.compile(r"[.,:;!?()\[\]{}]") if kind == "punctuation" else re.compile(r"[A-Za-zÀ-ÿ]")
  selected = [word for word in words if word.role == "stem" and pattern.search(word.text)]
  observed = len(selected)
  metrics = word_metrics(selected)
  if observed == 0:
    return _confidence(
      "low",
      ["observedTokenCount:0"],
      [f"no_observable_{kind}"],
      metrics,
      observed=0,
    )
  confidences = [word.ocrConfidence for word in selected if word.ocrConfidence is not None]
  low_share = (sum(1 for c in confidences if c < LOW_CONFIDENCE) / len(confidences)) if confidences else None
  dubious = sum(len(word.dubiousCharacterEvidence) for word in selected)
  evidence = [f"observedTokenCount:{observed}", f"lowShare:{round(low_share, 4) if low_share is not None else None}", f"dubious:{dubious}"]
  blockers: list[str] = []
  level = "low"
  if not boundary_ok or not stem_end_delimited:
    blockers.append("stem_end_not_delimited")
  elif band_level(stem_band) == "high" and (low_share or 0) <= 0.05 and dubious == 0:
    level = "high"
  elif band_level(stem_band) in {"high", "medium"} and (low_share or 0) <= 0.20:
    level = "medium"
  else:
    blockers.append("qualidade_ocr_insuficiente")
  return _confidence(level, evidence, blockers, metrics, observed=observed)


def compare_question_ocr(
  catalog_question: dict[str, Any],
  ocr_question: audit.PdfQuestion,
  preflight: dict[str, Any],
  eligible: bool,
  region_metrics: dict[str, Any],
  words: list[OcrAuditWord],
  context_text: str,
  boundary_ok: bool,
) -> dict[str, Any]:
  result = audit.compare_question(catalog_question, ocr_question, preflight=preflight, question_eligible=eligible)
  statuses = result["componentStatus"]
  # Preserve every base difference before any downgrade.
  base_differences = list(result.get("differences") or [])
  for diff in base_differences:
    component = audit.component_for_difference(diff)
    if component in statuses:
      audit.set_component(statuses, component, "uncertain", "ocr-difference (V1: difference proibido; evidencia preservada).")
  result["differences"] = []

  ineligible = (not eligible) or result.get("status") in {"missing-in-pdf", "ocr-ineligible"}
  stem_metrics = stem_metrics_of(words)
  alternative_metrics = alternative_metrics_of(words)
  stem_band = confidence_band(stem_metrics)
  alternative_band = confidence_band(alternative_metrics)
  stem_end_delimited = any(word.role == "alternative" for word in words)
  method, ocr_alternatives, ocr_stem = intrinsic_alternatives(ocr_question.text)
  risk, risk_evidence = shared_context_risk(context_text, ocr_question.text)

  confidences = {
    "stem": stem_confidence(stem_band, boundary_ok, stem_end_delimited, risk, stem_metrics),
    "alternatives": alternatives_confidence(alternative_band, boundary_ok, method, ocr_alternatives, alternative_metrics),
    "punctuation": token_confidence("punctuation", stem_band, boundary_ok, stem_end_delimited, words),
    "capitalization": token_confidence("capitalization", stem_band, boundary_ok, stem_end_delimited, words),
  }

  stem_diffs: list[dict[str, Any]] = []
  if stem_end_delimited:
    catalog_parts = {(part["role"], part["option"]): part["text"] for part in audit.catalog_text_parts(catalog_question)}
    catalog_stem = catalog_parts.get(("stem", None), "")
    stem_diffs = audit.localized_text_differences(catalog_stem, ocr_stem, "stem", None)
  text_diffs = [diff for diff in stem_diffs if diff.get("type") not in {"punctuation-localized", "capitalization-localized"}]
  punctuation_diffs = [diff for diff in stem_diffs if diff.get("type") == "punctuation-localized"]
  capitalization_diffs = [diff for diff in stem_diffs if diff.get("type") == "capitalization-localized"]

  catalog_alternatives = audit.catalog_alternatives(catalog_question)
  alternative_evidence: list[dict[str, Any]] = []
  alternatives_equal = False
  if stem_end_delimited and ocr_alternatives and catalog_alternatives:
    same_keys = list(ocr_alternatives.keys()) == list(catalog_alternatives.keys())
    same_text = all(
      audit.loose_text(ocr_alternatives.get(option, "")) == audit.loose_text(value)
      for option, value in catalog_alternatives.items()
    )
    alternatives_equal = same_keys and same_text
    if not alternatives_equal:
      alternative_evidence.append({
        "type": "alternatives-localized",
        "confidence": "media",
        "catalog": catalog_alternatives,
        "pdf": ocr_alternatives,
      })

  shared_block = risk in {"strong", "possible"}

  def status_of(confidence: dict[str, Any], diffs: list[dict[str, Any]], block_verified: bool = False) -> str:
    if ineligible or block_verified:
      return "uncertain"
    if confidence["level"] == "high" and not diffs:
      return "verified"
    return "uncertain"

  ocr_component_status = {
    "stem": status_of(confidences["stem"], text_diffs, block_verified=shared_block),
    "alternatives": "verified" if (not ineligible and confidences["alternatives"]["level"] == "high" and alternatives_equal) else "uncertain",
    "punctuation": status_of(confidences["punctuation"], punctuation_diffs),
    "capitalization": status_of(confidences["capitalization"], capitalization_diffs),
  }

  # Native componentStatus.text has a broader semantics (stem + alternatives
  # related differences). Keep it conservative in OCR V1 and expose the OCR
  # layer separately.
  audit.set_component(statuses, "text", "uncertain", "OCR V1: semantica nativa ampla; ver ocrComponentStatus.stem.")
  for component in ["alternatives", "punctuation", "capitalization"]:
    if statuses.get(component, {}).get("status") == "verified":
      audit.set_component(statuses, component, "uncertain", "OCR V1: status nativo conservador; ver ocrComponentStatus.")

  result["ocrComponentStatus"] = ocr_component_status
  result["stemConfidence"] = confidences["stem"]
  result["stemComparison"] = {
    "status": ocr_component_status["stem"],
    "differences": text_diffs,
    "sharedContextBlock": shared_block,
  }
  result["ocrComponentConfidence"] = confidences
  result["sharedContextRisk"] = risk
  result["sharedContextEvidence"] = risk_evidence
  result["confidencePolicyVersion"] = "experimental_v1"
  result["ocrRegionBand"] = confidence_band(region_metrics)
  result["ocrRegionBandExperimental"] = True
  result["ocrDifferenceEvidence"] = base_differences + text_diffs + punctuation_diffs + capitalization_diffs + alternative_evidence
  result["globalStatus"] = audit.global_status(statuses, "alta")
  result["needsHumanReview"] = result["globalStatus"] != "verified"
  return result


def collect_context_text(context: dict[str, Any], start_page: int, start_top: float) -> str:
  # OCR text before the marker: previous page tail plus same-page lines above it.
  banner_tokens = ["transcreva", "folha de respostas", "cartao-resposta", "cartao resposta"]

  def usable(page: dict[str, Any], line: dict[str, Any]) -> bool:
    shape = pilot.line_to_audit_shape(page, line)
    # Keep header lines (shared-text references often sit at the top of the
    # page) but drop footer lines and instruction banners.
    if pilot.structural_region(page, shape) == "footer":
      return False
    low = audit.strip_accents(str(line.get("text") or "")).lower()
    return not any(token in low for token in banner_tokens)

  lines: list[str] = []
  previous = context["pages"].get(start_page - 1)
  if previous:
    lines.extend(str(line.get("text") or "") for line in (previous.get("lines") or []) if usable(previous, line))
  current = context["pages"].get(start_page)
  if current:
    for line in current.get("lines") or []:
      shape = pilot.line_to_audit_shape(current, line)
      if float(shape["top"]) < start_top - 1 and usable(current, line):
        lines.append(str(line.get("text") or ""))
  return "\n".join(lines)


def audit_question(
  catalog: list[dict[str, Any]],
  school: str,
  year: int,
  context: dict[str, Any],
  number: int,
  eligible: bool,
) -> dict[str, Any]:
  catalog_question = next(
    (
      question for question in catalog
      if question.get("school") == school
      and int(question.get("year", 0)) == year
      and int(question["number"]) == number
    ),
    None,
  )
  markers = context["markers"]
  in_scope_pages = context["in_scope_pages"]
  start = find_question_marker(markers, in_scope_pages, number)
  if catalog_question is None or start is None:
    return {"number": number, "status": "not_associable", "eligible": eligible}
  start_index = markers.index(start)
  end = find_region_end(markers, start_index, in_scope_pages)
  start_page = int(start["page"])
  start_top = float(start.get("top") or 0)
  scope_end = int(context["scope"]["questionContentEnd"])
  if end:
    end_page = int(end["page"])
    end_top: float | None = float(end.get("top") or 0)
    end_number = end.get("number")
    boundary_method = "next_selected_marker"
    boundary_reliable = True
  else:
    end_page = scope_end
    end_top = None
    end_number = None
    end_role = context["scope_roles"].get(scope_end)
    boundary_reliable = end_role not in {"answer_sheet_or_post_content"}
    boundary_method = "question_scope_end" if boundary_reliable else "question_scope_end_uncertain"
  recurring = pilot.recurring_edge_lines(list(context["pages"].values()))
  region = collect_region(context, start_page, start_top, end_page, end_top, recurring)
  raw_text = region["text"]
  words = region["words"]
  line_confidences = region["lineConfidences"]
  text = normalize_ocr_marker_case(raw_text)
  metrics = region_metrics(words, line_confidences)
  context_text = collect_context_text(context, start_page, start_top)
  pages_used = list(range(start_page, end_page + 1))
  ocr_question = build_ocr_extracted_question(number, text, pages_used, start)
  marker_boundary_score = float((start.get("boundaryConfidence") or {}).get("score") or 0)
  boundary_ok = boundary_reliable and marker_boundary_score >= 0.9
  result = compare_question_ocr(
    catalog_question, ocr_question, context["marker_preflight"], eligible, metrics, words, context_text, boundary_ok
  )
  return {
    "number": number,
    "eligible": eligible,
    "boundary": {
      "startPage": start_page, "startTop": start.get("top"),
      "endPage": end_page, "endNumber": end_number, "endTop": (end or {}).get("top"),
      "boundaryResolutionMethod": boundary_method, "boundaryReliable": boundary_reliable,
      "pages": pages_used,
    },
    "ocrText": text,
    "ocrTextRaw": raw_text,
    "markerCaseNormalizationApplied": text != raw_text,
    "ocrWords": [word.to_dict() for word in words],
    "metrics": metrics,
    "stemMetrics": stem_metrics_of(words),
    "alternativeMetrics": alternative_metrics_of(words),
    "ocrQuestion": {
      "pages": ocr_question.pages,
      "structure": ocr_question.structure,
      "capabilities": ocr_question.capabilities,
      "wordsCount": len(ocr_question.words),
    },
    "catalogText": audit.catalog_text(catalog_question),
    "result": result,
  }


def run_pilot(output_dir: Path) -> dict[str, Any]:
  catalog = pilot.load_effective_catalog()
  proofs: list[dict[str, Any]] = []
  for case in PILOT_CASES:
    payload = load_payload(case["slug"])
    expected = [
      int(question["number"]) for question in catalog
      if question.get("school") == case["school"] and int(question.get("year", 0)) == case["year"]
    ]
    context = build_pilot_context(payload, expected)
    audited = [
      audit_question(catalog, case["school"], case["year"], context, number, True)
      for number in case["questions"]
    ]
    proofs.append({
      "school": case["school"],
      "year": case["year"],
      "slug": case["slug"],
      "proofStatus": context["marker_preflight"]["status"],
      "segmentationConfidence": context["marker_preflight"]["segmentationConfidence"],
      "questions": audited,
    })

  control_payload = load_payload(NON_ELIGIBLE_CONTROL["slug"])
  control_expected = [
    int(question["number"]) for question in catalog
    if question.get("school") == NON_ELIGIBLE_CONTROL["school"] and int(question.get("year", 0)) == NON_ELIGIBLE_CONTROL["year"]
  ]
  control_context = build_pilot_context(control_payload, control_expected)
  control = audit_question(
    catalog, NON_ELIGIBLE_CONTROL["school"], NON_ELIGIBLE_CONTROL["year"], control_context,
    NON_ELIGIBLE_CONTROL["question"], False,
  )
  summary = {
    "mode": "read-only",
    "engine": "tesseract",
    "capabilities": OCR_CAPABILITIES,
    "pilot": proofs,
    "nonEligibleControl": {"school": NON_ELIGIBLE_CONTROL["school"], "year": NON_ELIGIBLE_CONTROL["year"], "question": control},
  }
  write_outputs(summary, output_dir)
  return summary


def write_outputs(summary: dict[str, Any], output_dir: Path) -> None:
  output_dir.mkdir(parents=True, exist_ok=True)
  SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
  SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
  SUMMARY_MD.write_text(render_markdown(summary), encoding="utf-8")


def render_markdown(summary: dict[str, Any]) -> str:
  lines = [
    "# Piloto OCR -> Auditor de Conteudo (V1, shadow)",
    "",
    "Experimento somente leitura. Nenhum `difference` e emitido pela camada OCR; componentes nao observaveis ficam `unverified`.",
    "",
  ]
  for proof in summary["pilot"]:
    lines.append(f"## {proof['school']} {proof['year']} (status={proof['proofStatus']}, segmentacao={proof['segmentationConfidence']})")
    lines.append("")
    for item in proof["questions"]:
      if item.get("status") == "not_associable":
        lines.append(f"- Q{item['number']}: nao associavel (elegibilidade/limite).")
        continue
      result = item["result"]
      components = ", ".join(
        f"{name}={data['status']}" for name, data in result.get("componentStatus", {}).items()
      )
      lines.append(f"### Q{item['number']} (pages {item['boundary']['startPage']}-{item['boundary']['endPage']})")
      metrics = item["metrics"]
      lines.append(
        f"- metricas: mean={metrics['meanWordConfidence']} median={metrics['medianWordConfidence']} "
        f"p10={metrics['p10WordConfidence']} lowShare={metrics['lowConfidenceTokenShare']} "
        f"reconShare={metrics['reconstructedTokenShare']} dubShare={metrics['dubiousCharacterShare']} "
        f"lineConf={metrics['lineConfidence']}"
      )
      confidence = result.get("ocrComponentConfidence") or {}
      levels = ", ".join(
        f"{name}={value.get('level')}" for name, value in confidence.items()
      )
      ocr_status = result.get("ocrComponentStatus") or {}
      stem_metrics = item.get("stemMetrics") or {}
      lines.append(f"- boundary: start=p{item['boundary']['startPage']} end=p{item['boundary']['endPage']} pages={item['boundary']['pages']} method={item['boundary']['boundaryResolutionMethod']} reliable={item['boundary']['boundaryReliable']}")
      lines.append(
        f"- stemMetrics: p10={stem_metrics.get('p10WordConfidence')} median={stem_metrics.get('medianWordConfidence')} "
        f"lowShare={stem_metrics.get('lowConfidenceTokenShare')} reconShare={stem_metrics.get('reconstructedTokenShare')} "
        f"dubShare={stem_metrics.get('dubiousCharacterShare')}"
      )
      lines.append(
        f"- confianca OCR ({result.get('confidencePolicyVersion')}): {levels} | "
        f"sharedContextRisk={result.get('sharedContextRisk')}"
      )
      lines.append(f"- global={result.get('globalStatus')} gate={result.get('gate')} proofStatus={result.get('proofStatus')}")
      lines.append(f"- componentStatus nativo: {components}")
      lines.append(
        f"- ocrComponentStatus: stem={ocr_status.get('stem')} alternatives={ocr_status.get('alternatives')} "
        f"punctuation={ocr_status.get('punctuation')} capitalization={ocr_status.get('capitalization')}"
      )
      if result.get("ocrDifferenceEvidence"):
        lines.append(f"- ocrDifferenceEvidence: {result['ocrDifferenceEvidence']}")
      lines.append("")
  control = summary["nonEligibleControl"]["question"]
  lines.append(f"## Controle nao elegivel: {summary['nonEligibleControl']['school']} {summary['nonEligibleControl']['year']} Q{control['number']}")
  if control.get("result"):
    result = control["result"]
    components = ", ".join(f"{name}={data['status']}" for name, data in result.get("componentStatus", {}).items())
    lines.append(f"- global={result.get('globalStatus')} status={result.get('status')} gate={result.get('gate')}")
    lines.append(f"- componentes: {components}")
  lines.append("")
  return "\n".join(lines)


def main() -> None:
  parser = argparse.ArgumentParser(description="Piloto OCR -> auditor de conteudo (V1, shadow).")
  parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
  args = parser.parse_args()
  summary = run_pilot(Path(args.output_dir))
  print(json.dumps({
    "json": str(SUMMARY_JSON),
    "markdown": str(SUMMARY_MD),
    "proofs": len(summary["pilot"]),
    "questions": sum(len(p["questions"]) for p in summary["pilot"]),
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
