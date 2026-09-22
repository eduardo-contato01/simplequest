from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_observations as observations  # noqa: E402
import audit_question_boundary as question_boundary  # noqa: E402
import audit_response_fusion as fusion  # noqa: E402
import audit_response_holdout as runner  # noqa: E402
import audit_response_regions as regions  # noqa: E402
import audit_response_structure as response_structure  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def line(page: int, top: float, text: str) -> observations.ObservedLine:
  return observations.ObservedLine(page=page, text=text, bbox=(50.0, top, 500.0, top + 12.0), source="synthetic")


def make_bundle(pages, height: float = 800.0) -> observations.ObservationBundle:
  lines: list[observations.ObservedLine] = []
  for page in sorted(pages):
    for top, text in pages[page]:
      lines.append(line(page, top, text))
  for index, item in enumerate(lines):
    item.line_index = index
  geometry = {page: {"pdfHeight": height, "pdfWidth": 600.0} for page in pages}
  return observations.ObservationBundle(words=[], lines=lines, visual_components=[], page_geometry=geometry, source="synthetic")


def visual(page: int, top: float, left: float = 60.0, size: float = 14.0) -> observations.ObservedVisualComponent:
  bbox = (left, top, left + size, top + size)
  return observations.ObservedVisualComponent(page=page, bbox=bbox, area=size * size, width=size, height=size, fill=0.0)


def option_count(bundle: observations.ObservationBundle, boundary: dict) -> int | None:
  lines = bundle.lines_as_region_input()
  markers = observations.extract_text_markers(lines)
  discovered = regions.discover_response_regions(
    boundary=boundary, lines=lines, words=[], strong_markers=markers, visual_markers=[], raster_components=[],
  )
  structure = response_structure.discover_response_structure(runner._observed_lines(lines))
  result = fusion.fuse_response_evidence(boundary, structure, {}, discovered)
  return result.get("optionCountHypothesis")


def entry(qid: str, number: int, start: int, end: int, run: int = 1) -> dict:
  return {"questionId": qid, "questionNumber": number, "pageStart": start, "pageEnd": end, "sequenceRun": run}


def data(doc_id: str, questions: list[dict]) -> dict:
  return {"documentId": doc_id, "contentFingerprint": "fp", "questions": questions}


def run_question(bundle, index_doc, qid, gt_pages=None):
  questions = question_boundary.index_questions(index_doc)
  current = question_boundary.find_question(questions, qid)
  nxt = question_boundary.next_question_in_order(questions, qid)
  pages = question_boundary.expected_pages(current) if current else (gt_pages or [1])
  boundary = question_boundary.compute_question_boundary(bundle, current or {"questionId": qid, "questionNumber": -1, "pageStart": -1, "pageEnd": -1}, nxt, pages)
  filtered = question_boundary.filter_bundle(bundle, boundary)
  return boundary, filtered


def test_same_page_two_questions_ae() -> None:
  pages = {1: [
    (100, "1. Enunciado um"), (120, "(A) a1"), (134, "(B) b1"), (148, "(C) c1"), (162, "(D) d1"), (176, "(E) e1"),
    (300, "2. Enunciado dois"), (320, "(A) a2"), (334, "(B) b2"), (348, "(C) c2"), (362, "(D) d2"), (376, "(E) e2"),
  ]}
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q1", 1, 1, 1), entry("d:q2", 2, 1, 1)])
  unfiltered = option_count(bundle, {"reliable": True, "pages": [1]})
  b1, f1 = run_question(bundle, index, "d:q1")
  b2, f2 = run_question(bundle, index, "d:q2")
  check("two_ae.bug_unfiltered_10", unfiltered == 10, unfiltered)
  check("two_ae.q1_reliable", b1["reliable"] is True, b1)
  check("two_ae.q1_count_5", option_count(f1, b1) == 5, option_count(f1, b1))
  check("two_ae.q2_count_5", option_count(f2, b2) == 5, option_count(f2, b2))


def test_same_page_five_questions_ae() -> None:
  lines = []
  for question in range(1, 6):
    base = 50 + (question - 1) * 140
    lines.append((base, f"{question}. Enunciado {question}"))
    for offset, letter in enumerate("ABCDE"):
      lines.append((base + 14 + offset * 14, f"({letter}) alt {question}{letter}"))
  bundle = make_bundle({1: lines})
  questions = [entry(f"d:q{n}", n, 1, 1) for n in range(1, 6)]
  index = data("d", questions)
  unfiltered = option_count(bundle, {"reliable": True, "pages": [1]})
  boundary, filtered = run_question(bundle, index, "d:q3")
  check("five_ae.bug_unfiltered_25", unfiltered == 25, unfiltered)
  check("five_ae.q3_count_5", option_count(filtered, boundary) == 5, option_count(filtered, boundary))


def test_same_page_three_questions_ad() -> None:
  lines = []
  for question in range(1, 4):
    base = 80 + (question - 1) * 200
    lines.append((base, f"{question}. Enunciado {question}"))
    for offset, letter in enumerate("ABCD"):
      lines.append((base + 14 + offset * 14, f"({letter}) alt {question}{letter}"))
  bundle = make_bundle({1: lines})
  index = data("d", [entry("d:q1", 1, 1, 1), entry("d:q2", 2, 1, 1), entry("d:q3", 3, 1, 1)])
  unfiltered = option_count(bundle, {"reliable": True, "pages": [1]})
  boundary, filtered = run_question(bundle, index, "d:q2")
  check("three_ad.bug_unfiltered_12", unfiltered == 12, unfiltered)
  check("three_ad.middle_count_4", option_count(filtered, boundary) == 4, option_count(filtered, boundary))


def test_multi_page_question() -> None:
  pages = {
    1: [(100, "1. Enunciado um"), (120, "(A) a1"), (134, "(B) b1")],
    2: [(60, "(C) c1"), (74, "(D) d1"), (88, "(E) e1"), (300, "2. Enunciado dois"), (320, "(A) a2"), (334, "(B) b2"), (348, "(C) c2"), (362, "(D) d2"), (376, "(E) e2")],
  }
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q1", 1, 1, 2), entry("d:q2", 2, 2, 2)])
  boundary, filtered = run_question(bundle, index, "d:q1")
  check("multi.pages", boundary["pages"] == [1, 2], boundary["pages"])
  check("multi.start_limit", boundary["pageLimits"][1]["top"] == 100.0, boundary["pageLimits"])
  check("multi.end_limit", boundary["pageLimits"][2]["bottom"] == 300.0, boundary["pageLimits"])
  check("multi.count_of_q1", option_count(filtered, boundary) == 5, option_count(filtered, boundary))
  boundary2, filtered2 = run_question(bundle, index, "d:q2")
  check("multi.q2_count", option_count(filtered2, boundary2) == 5, option_count(filtered2, boundary2))


def test_missing_current_marker() -> None:
  pages = {1: [(100, "9. outro item"), (120, "(A) x"), (134, "(B) y"), (148, "(C) z")]}
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q2", 2, 1, 1)])
  boundary, filtered = run_question(bundle, index, "d:q2")
  check("missing.reliable_false", boundary["reliable"] is False, boundary)
  check("missing.reason", boundary["reason"] == "current_marker_not_found", boundary["reason"])
  check("missing.count_blocked", option_count(filtered, boundary) is None, option_count(filtered, boundary))


def test_duplicate_or_reset_numbering() -> None:
  pages = {1: [(100, "1. run um q1"), (140, "(A) a"), (154, "(B) b"), (168, "(C) c"), (182, "(D) d")],
           2: [(100, "1. run dois q1"), (140, "(A) a"), (154, "(B) b"), (168, "(C) c"), (182, "(D) d"), (400, "2. run dois q2")]}
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q1:o1", 1, 1, 1, run=1), entry("d:q1:o2", 1, 2, 2, run=2), entry("d:q2:o2", 2, 2, 2, run=2)])
  boundary, filtered = run_question(bundle, index, "d:q1:o2")
  check("reset.uses_page", boundary["currentMarker"]["page"] == 2, boundary["currentMarker"])
  check("reset.next_marker", boundary["nextMarker"]["number"] == 2, boundary["nextMarker"])
  check("reset.page_limits", boundary["pageLimits"][2]["bottom"] == 400.0, boundary["pageLimits"])
  check("reset.count_4", option_count(filtered, boundary) == 4, option_count(filtered, boundary))


def test_one_question_per_page_regression() -> None:
  pages = {1: [(100, "1. Enunciado"), (120, "(A) a"), (134, "(B) b"), (148, "(C) c"), (162, "(D) d"), (176, "(E) e")]}
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q1", 1, 1, 1)])
  boundary, filtered = run_question(bundle, index, "d:q1")
  check("onepage.reliable", boundary["reliable"] is True, boundary)
  check("onepage.count_5", option_count(filtered, boundary) == 5, option_count(filtered, boundary))


def test_page_height_prefers_image_for_ocr() -> None:
  pages = {1: [(1000, "1. Enunciado"), (1020, "(A) a"), (1034, "(B) b"), (1048, "(C) c"), (1062, "(D) d"), (1076, "(E) e")]}
  lines = [line(1, top, text) for top, text in pages[1]]
  for index, item in enumerate(lines):
    item.line_index = index
  # OCR payloads can carry both heights; observed bboxes are in image pixels.
  bundle = observations.ObservationBundle(
    words=[], lines=lines, visual_components=[],
    page_geometry={1: {"imageHeight": 1760.0, "pdfHeight": 792.0, "imageWidth": 1240.0, "pdfWidth": 595.0}},
    source="ocr_cache",
  )
  index = data("d", [entry("d:q1", 1, 1, 1)])
  boundary, filtered = run_question(bundle, index, "d:q1")
  limit = boundary["pageLimits"][1]
  check("height.image_wins", limit["bottom"] == 1760.0, limit)
  check("height.not_collapsed", limit["bottom"] > limit["top"], limit)
  check("height.count_5", option_count(filtered, boundary) == 5, option_count(filtered, boundary))


def test_duplicate_number_same_page_is_ambiguous() -> None:
  pages = {1: [
    (100, "1. primeira ocorrencia"), (120, "(A) a"), (134, "(B) b"), (148, "(C) c"), (162, "(D) d"), (176, "(E) e"),
    (300, "1. segunda ocorrencia"), (320, "(A) a"), (334, "(B) b"), (348, "(C) c"), (362, "(D) d"), (376, "(E) e"),
  ]}
  bundle = make_bundle(pages)
  index = data("d", [entry("d:q1", 1, 1, 1)])
  boundary, filtered = run_question(bundle, index, "d:q1")
  check("duppage.reliable_false", boundary["reliable"] is False, boundary)
  check("duppage.reason", boundary["reason"] == "current_marker_ambiguous", boundary["reason"])
  check("duppage.count_blocked", option_count(filtered, boundary) is None, option_count(filtered, boundary))


def test_runner_integration_boundary() -> None:
  pages = {1: [
    (100, "1. Enunciado um"), (120, "(A) a1"), (134, "(B) b1"), (148, "(C) c1"), (162, "(D) d1"), (176, "(E) e1"),
    (300, "2. Enunciado dois"), (320, "(A) a2"), (334, "(B) b2"), (348, "(C) c2"), (362, "(D) d2"), (376, "(E) e2"),
  ]}
  bundle = make_bundle(pages)
  questions = [entry("d:q1", 1, 1, 1), entry("d:q2", 2, 1, 1)]
  index = data("d", questions)
  current, nxt = runner.resolve_index_entries(index, "d:q1")
  # Real runner path: boundary metadata computed and bundle filtered internally.
  result = runner._run_with_boundary(bundle, current, current, nxt, [1], None)
  check("runner.integration_count_5", result.get("optionCountHypothesis") == 5, result.get("optionCountHypothesis"))
  check("runner.integration_not_10", result.get("optionCountHypothesis") != 10, result.get("optionCountHypothesis"))


def test_visual_respects_boundary() -> None:
  pages = {1: [
    (100, "1. Enunciado um"), (120, "(A) a1"), (134, "(B) b1"), (148, "(C) c1"), (162, "(D) d1"), (176, "(E) e1"),
    (300, "2. Enunciado dois"), (320, "(A) a2"), (334, "(B) b2"), (348, "(C) c2"), (362, "(D) d2"), (376, "(E) e2"),
  ]}
  bundle = make_bundle(pages)
  bundle.visual_components = [visual(1, 118), visual(1, 132), visual(1, 146), visual(1, 160), visual(1, 174),
                              visual(1, 318), visual(1, 332), visual(1, 346), visual(1, 360), visual(1, 374)]
  index = data("d", [entry("d:q1", 1, 1, 1), entry("d:q2", 2, 1, 1)])
  boundary, filtered = run_question(bundle, index, "d:q1")
  original_count = len(bundle.visual_components)
  check("visual.original_untouched", len(bundle.visual_components) == original_count)
  check("visual.filtered_5", len(filtered.visual_components) == 5, len(filtered.visual_components))
  check("visual.no_q2", all(component.bbox[1] < 300.0 for component in filtered.visual_components))
  evidence = [{"page": 1, "bbox": list(component.bbox)} for component in bundle.visual_components]
  kept = question_boundary.filter_visual_items(evidence, boundary)
  check("visual.evidence_filtered_5", len(kept) == 5, len(kept))
  check("visual.evidence_no_q2", all(item["bbox"][1] < 300.0 for item in kept))


def main() -> None:
  test_same_page_two_questions_ae()
  test_same_page_five_questions_ae()
  test_same_page_three_questions_ad()
  test_multi_page_question()
  test_missing_current_marker()
  test_duplicate_or_reset_numbering()
  test_duplicate_number_same_page_is_ambiguous()
  test_one_question_per_page_regression()
  test_page_height_prefers_image_for_ocr()
  test_runner_integration_boundary()
  test_visual_respects_boundary()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks do question boundary neutro passaram.")


if __name__ == "__main__":
  main()
