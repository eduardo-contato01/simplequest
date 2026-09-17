from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_pdf_mvp as audit  # noqa: E402
import audit_ocr_content as ocr  # noqa: E402
import ocr_raster_pilot as pilot  # noqa: E402


FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def catalog_question(image: bool = False) -> dict:
  blocks = [{"type": "text", "text": "Pergunta sintetica de teste"}]
  if image:
    blocks.append({"type": "image", "urls": ["x.webp"]})
  return {
    "id": "q1",
    "number": 1,
    "contentBlocks": blocks,
    "alternativeBlocks": [[{"type": "text", "text": value}] for value in ["um", "dois", "tres", "quatro", "cinco"]],
    "answerType": "ABCDE",
  }


def pdf_question(text: str, capabilities: dict | None = None) -> audit.PdfQuestion:
  return audit.PdfQuestion(
    number=1,
    text=text,
    pages=[1],
    image_count=0,
    bold_word_count=0,
    italic_word_count=0,
    font_samples=[],
    words=[],
    tables=[],
    formulas=[],
    structure={"question_boundary": 0.99, "header_footer_cleaning": 0.9},
    capabilities=capabilities,
  )


OCR_CAPS = dict(ocr.OCR_CAPABILITIES)


def words_for(tokens: list[str], role: str, confidence: float = 0.97) -> list[ocr.OcrAuditWord]:
  return [
    ocr.OcrAuditWord(text=token, page=1, bbox=(0, 0, 0, 0), ocrConfidence=confidence,
                     reconstructionConfidence=None, isReconstructed=False, role=role)
    for token in tokens
  ]


def test_capability() -> None:
  text = "A." + " Pergunta sintetica de teste " + "B um C dois D tres E quatro E cinco"
  without = audit.compare_question(catalog_question(), pdf_question(text), preflight={"status": "ready_for_audit"})
  with_caps = audit.compare_question(catalog_question(), pdf_question(text, OCR_CAPS), preflight={"status": "ready_for_audit"})
  check("capability_none_preserves_native_media", without["componentStatus"]["media"]["status"] == "not_applicable",
        str(without["componentStatus"]["media"]["status"]))
  check("capability_false_media_unverified", with_caps["componentStatus"]["media"]["status"] == "unverified",
        str(with_caps["componentStatus"]["media"]["status"]))
  check("capability_false_table_unverified", with_caps["componentStatus"]["table"]["status"] == "unverified",
        str(with_caps["componentStatus"]["table"]["status"]))
  check("capability_false_formula_unverified", with_caps["componentStatus"]["formula"]["status"] == "unverified",
        str(with_caps["componentStatus"]["formula"]["status"]))
  check("capability_false_inlineFormatting_unverified", with_caps["componentStatus"]["inlineFormatting"]["status"] == "unverified",
        str(with_caps["componentStatus"]["inlineFormatting"]["status"]))


def test_eligibility() -> None:
  text = "A." + " Pergunta sintetica de teste " + "B um C dois D tres E quatro E cinco"
  ineligible = audit.compare_question(catalog_question(), pdf_question(text, OCR_CAPS),
                                      preflight={"status": "segmentation_uncertain"}, question_eligible=False)
  eligible = audit.compare_question(catalog_question(), pdf_question(text, OCR_CAPS),
                                    preflight={"status": "segmentation_uncertain"}, question_eligible=True)
  check("eligible_false_ocr_ineligible", ineligible["status"] == "ocr-ineligible", ineligible["status"])
  check("eligible_false_no_verified", all(v["status"] != "verified" for v in ineligible["componentStatus"].values()))
  check("eligible_true_not_global_gate", eligible.get("status") != "preflight-not-ready", eligible.get("status", "compared"))


def test_difference_and_evidence() -> None:
  catalog = catalog_question()
  ocr_text = "Pergunta sintetica DIFERENTE de teste\nA) um\nB) dois\nC) tres\nD) quatro\nE) cinco"
  ocr_q = pdf_question(ocr_text, OCR_CAPS)
  words = (
    words_for(["Pergunta", "sintetica", "DIFERENTE", "de", "teste"], "stem")
    + words_for(["A", "um", "B", "dois", "C", "tres", "D", "quatro", "E", "cinco"], "alternative")
  )
  metrics = ocr.word_metrics(words)
  result = ocr.compare_question_ocr(catalog, ocr_q, {"status": "ready_for_audit"}, True, metrics, words,
                                    "contexto", boundary_ok=True)
  check("no_difference_status", all(v["status"] != "difference" for v in result["componentStatus"].values()))
  check("public_differences_empty", result["differences"] == [])
  check("evidence_preserved", len(result["ocrDifferenceEvidence"]) >= 1, str(len(result["ocrDifferenceEvidence"])))
  check("native_text_conservative", result["componentStatus"]["text"]["status"] == "uncertain",
        result["componentStatus"]["text"]["status"])


def test_empty_token_evidence() -> None:
  words = words_for(["Pergunta", "sintetica", "teste"], "stem")
  confidence = ocr.token_confidence("punctuation", "descriptive_high", True, True, words)
  check("no_punctuation_tokens_not_high", confidence["level"] != "high", confidence["level"])
  check("no_punctuation_tokens_reason", any("no_observable_punctuation" in blocker for blocker in confidence["blockers"]),
        str(confidence["blockers"]))
  check("no_punctuation_observed_zero", confidence.get("observedTokenCount") == 0, str(confidence.get("observedTokenCount")))


def test_stem_independence() -> None:
  good_stem = words_for(["Pergunta", "sintetica", "de", "teste"], "stem", 0.97)
  good_alt = words_for(["um", "dois", "tres"], "alternative", 0.97)
  bad_alt = words_for(["um", "dois", "tres"], "alternative", 0.55)
  stem_metrics_good = ocr.stem_metrics_of(good_stem + good_alt)
  stem_metrics_bad = ocr.stem_metrics_of(good_stem + bad_alt)
  check("stem_metrics_ignore_alternatives", stem_metrics_good == stem_metrics_bad,
        f"{stem_metrics_good} vs {stem_metrics_bad}")
  punct_good = ocr.token_confidence("capitalization", "descriptive_high", True, True, good_stem + good_alt)
  punct_bad = ocr.token_confidence("capitalization", "descriptive_high", True, True, good_stem + bad_alt)
  check("stem_token_confidence_ignore_alternatives", punct_good["level"] == punct_bad["level"],
        f"{punct_good['level']} vs {punct_bad['level']}")


def test_pilot_boundaries() -> None:
  summary = ocr.run_pilot(ocr.DEFAULT_OUTPUT_DIR)
  check("pilot_zero_native_difference",
        all(
          data["status"] != "difference"
          for proof in summary["pilot"]
          for question in proof["questions"]
          for data in (question.get("result", {}).get("componentStatus", {}) or {}).values()
        ))
  for proof in summary["pilot"]:
    for question in proof["questions"]:
      result = question.get("result")
      if not result:
        continue
      boundary = question["boundary"]
      start, end = boundary["startPage"], boundary["endPage"]
      check(f"boundary_pages_contiguous_{proof['school']}_{proof['year']}_Q{question['number']}",
            boundary["pages"] == list(range(start, end + 1)), str(boundary["pages"]))
      if boundary["boundaryResolutionMethod"].startswith("question_scope_end"):
        check(f"last_question_scope_end_{proof['school']}_{proof['year']}_Q{question['number']}",
              boundary["boundaryReliable"] is False or boundary["boundaryReliable"] is True)
      if result.get("sharedContextRisk") in {"strong", "possible"}:
        check(f"shared_context_blocks_stem_{proof['school']}_{proof['year']}_Q{question['number']}",
              result["ocrComponentStatus"]["stem"] != "verified",
              result["ocrComponentStatus"]["stem"])


def test_boundary_spans() -> None:
  def page(number: int) -> dict:
    return {
      "page": number,
      "width": 1000,
      "height": 1000,
      "pdfWidth": 500,
      "pdfHeight": 500,
      "lines": [{"line": 1, "text": f"linha {number}", "bbox": [10, 100, 200, 120], "wordIndexes": [0], "confidence": 0.9}],
      "words": [{"index": 0, "text": f"linha{number}", "bbox": [10, 100, 200, 120], "confidence": 0.9}],
    }
  context = {"pages": {number: page(number) for number in (1, 2, 3)}, "in_scope_pages": {1, 2, 3}}
  region = ocr.collect_region(context, 1, 0.0, 3, None, {})
  check("collect_region_spans_three_pages", region["text"].count("linha") == 3, region["text"])

  catalog = pilot.load_effective_catalog()
  payload = ocr.load_payload("cmbh-6ano-2017-2018-mat")
  expected = [int(q["number"]) for q in catalog if q.get("school") == "CMBH" and int(q.get("year", 0)) == 2017]
  context = ocr.build_pilot_context(payload, expected)
  last = ocr.audit_question(catalog, "CMBH", 2017, context, 20, True)
  boundary = last.get("boundary", {})
  check("last_question_without_next_marker_uses_scope_end",
        str(boundary.get("boundaryResolutionMethod", "")).startswith("question_scope_end"), str(boundary))
  check("last_question_pages_contiguous",
        boundary.get("pages") == list(range(boundary.get("startPage", 0), boundary.get("endPage", -1) + 1)),
        str(boundary.get("pages")))


def main() -> int:
  test_capability()
  test_eligibility()
  test_difference_and_evidence()
  test_empty_token_evidence()
  test_stem_independence()
  test_boundary_spans()
  test_pilot_boundaries()
  if FAILURES:
    print(f"\n{len(FAILURES)} FAILURES: {FAILURES}")
    return 1
  print("\nALL CHECKS PASSED")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
