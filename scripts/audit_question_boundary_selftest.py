from __future__ import annotations

import inspect
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


def line_at(
  page: int,
  top: float,
  text: str,
  x0: float,
  x1: float,
) -> observations.ObservedLine:
  return observations.ObservedLine(
    page=page,
    text=text,
    bbox=(
      x0,
      top,
      x1,
      top + 12.0,
    ),
    source="synthetic",
  )


def make_parallel_columns_bundle() -> observations.ObservationBundle:
  lines = []

  lines.append(
    line_at(
      1,
      100,
      "9. Questao esquerda",
      40,
      250,
    )
  )

  for index, label in enumerate(
    "ABCDE"
  ):
    lines.append(
      line_at(
        1,
        125 + index * 24,
        f"({label}) esquerda {label}",
        50,
        250,
      )
    )

  lines.append(
    line_at(
      1,
      100,
      "10. Questao direita",
      320,
      560,
    )
  )

  for index, label in enumerate(
    "ABCDE"
  ):
    lines.append(
      line_at(
        1,
        125 + index * 24,
        f"({label}) direita {label}",
        330,
        560,
      )
    )

  for index, item in enumerate(lines):
    item.line_index = index

  visuals = []

  for index in range(5):
    visuals.append(
      visual(
        1,
        125 + index * 24,
        left=60,
      )
    )

    visuals.append(
      visual(
        1,
        125 + index * 24,
        left=340,
      )
    )

  return observations.ObservationBundle(
    words=[],
    lines=lines,
    visual_components=visuals,
    page_geometry={
      1: {
        "pdfHeight": 800.0,
        "pdfWidth": 600.0,
      }
    },
    source="synthetic",
  )


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
  structure = response_structure.discover_response_structure(runner._observed_lines(lines))
  markers = runner._markers_with_recovered_geometry(lines, structure)
  discovered = regions.discover_response_regions(
    boundary=boundary, lines=lines, words=[], strong_markers=markers, visual_markers=[], raster_components=[],
    selected_response_set=structure.get("selectedResponseSet"),
  )
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
  context = {"document_questions": questions} if "document_questions" in inspect.signature(question_boundary.compute_question_boundary).parameters else {}
  boundary = question_boundary.compute_question_boundary(bundle, current or {"questionId": qid, "questionNumber": -1, "pageStart": -1, "pageEnd": -1}, nxt, pages, **context)
  filtered = question_boundary.filter_bundle(bundle, boundary)
  return boundary, filtered


def test_parallel_two_column_questions() -> None:
  bundle = make_parallel_columns_bundle()

  index = data(
    "d",
    [
      entry(
        "d:q9",
        9,
        1,
        1,
      ),
      entry(
        "d:q10",
        10,
        1,
        1,
      ),
    ],
  )

  b9, f9 = run_question(
    bundle,
    index,
    "d:q9",
  )

  b10, f10 = run_question(
    bundle,
    index,
    "d:q10",
  )

  q9_limits = (
    b9.get(
      "pageLimits",
      {},
    ).get(
      1,
      {},
    )
  )

  q10_limits = (
    b10.get(
      "pageLimits",
      {},
    ).get(
      1,
      {},
    )
  )

  check(
    "columns2d.q9_mode",
    b9.get(
      "boundaryMode"
    ) == "two_column",
    b9,
  )

  check(
    "columns2d.q9_x1",
    q9_limits.get(
      "x1"
    ) is not None
    and q9_limits[
      "x1"
    ] < 300.0,
    q9_limits,
  )

  check(
    "columns2d.q9_count",
    option_count(
      f9,
      b9,
    ) == 5,
    option_count(
      f9,
      b9,
    ),
  )

  check(
    "columns2d.q9_only_left",
    bool(
      f9.lines
    )
    and all(
      (
        line.bbox[0]
        + line.bbox[2]
      ) / 2.0
      < 300.0
      for line in f9.lines
    ),
    [
      list(
        line.bbox
      )
      for line in f9.lines
    ],
  )

  check(
    "columns2d.q10_mode",
    b10.get(
      "boundaryMode"
    ) == "two_column",
    b10,
  )

  check(
    "columns2d.q10_x0",
    q10_limits.get(
      "x0"
    ) is not None
    and q10_limits[
      "x0"
    ] > 100.0
    and q10_limits[
      "x0"
    ] < 300.0,
    q10_limits,
  )

  check(
    "columns2d.q10_count",
    option_count(
      f10,
      b10,
    ) == 5,
    option_count(
      f10,
      b10,
    ),
  )

  check(
    "columns2d.q10_only_right",
    bool(
      f10.lines
    )
    and all(
      (
        line.bbox[0]
        + line.bbox[2]
      ) / 2.0
      > 300.0
      for line in f10.lines
    ),
    [
      list(
        line.bbox
      )
      for line in f10.lines
    ],
  )

  visual_evidence = [
    {
      "page":
        component.page,

      "bbox":
        list(
          component.bbox
        ),
    }
    for component
    in bundle.visual_components
  ]

  q10_visual = (
    question_boundary
    .filter_visual_items(
      visual_evidence,
      b10,
    )
  )

  check(
    "columns2d.visual_right_only",
    len(
      q10_visual
    ) == 5
    and all(
      (
        item["bbox"][0]
        + item["bbox"][2]
      ) / 2.0
      > 300.0
      for item in q10_visual
    ),
    q10_visual,
  )


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
  check("two_ae.unfiltered_conservative", unfiltered is None, unfiltered)
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
  check("five_ae.unfiltered_conservative", unfiltered is None, unfiltered)
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
  check("three_ad.unfiltered_conservative", unfiltered is None, unfiltered)
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
  # Existing Structure clustering is page-local and selects A-B here, not the
  # C-E continuation. The contract must not silently union rejected clusters.
  # Cross-page completeness is outside this patch; preserve safe abstention.
  selected = response_structure.discover_response_structure(
    runner._observed_lines(filtered.lines_as_region_input()))["selectedResponseSet"]
  check("multi.selected_fragment", selected["labels"] == ["A", "B"], selected)
  check("multi.selected_fragment_conservative", option_count(filtered, boundary) is None, option_count(filtered, boundary))
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


def test_target_identity_and_grammar() -> None:
  def boundary_for(text, canonical=23, printed=None, next_text=None, next_printed=None):
    current = entry("synthetic:q23", canonical, 1, 1)
    if printed is not None:
      current["printedQuestionNumber"] = printed
      current["section"] = "synthetic_section"
    questions = [current]
    rows = [(100, text), (120, "(A) alpha"), (140, "(B) beta"), (160, "(C) gamma")]
    if next_text is not None:
      nxt = entry("synthetic:next", canonical + 1, 1, 1)
      if next_printed is not None:
        nxt["printedQuestionNumber"] = next_printed
      questions.append(nxt)
      rows.append((300, next_text))
    bundle = make_bundle({1: rows})
    return run_question(bundle, data("synthetic", questions), current["questionId"])[0]

  normal = boundary_for("23. Enunciado")
  check("identity.normal_reliable", normal["reliable"], normal)
  check("identity.normal_canonical_source", (normal.get("currentMarker") or {}).get("numberSource") == "canonical", normal)
  check("identity.normal_grammar", (normal.get("currentMarker") or {}).get("matchGrammar") == "numeric_separator", normal)

  printed = boundary_for("07. Enunciado", canonical=27, printed=7, next_text="08. Proxima", next_printed=8)
  check("identity.printed_current_reliable", printed["reliable"], printed)
  marker = printed.get("currentMarker") or {}
  check("identity.printed_number", marker.get("number") == 7, marker)
  check("identity.canonical_unchanged", printed["questionNumber"] == 27 and marker.get("canonicalQuestionNumber") == 27, printed)
  check("identity.printed_provenance", marker.get("observedQuestionNumber") == 7 and marker.get("numberSource") == "printed", marker)
  check("identity.next_printed", (printed.get("nextMarker") or {}).get("number") == 8 and (printed.get("nextMarker") or {}).get("numberSource") == "printed", printed)
  check("identity.next_cut", (printed.get("pageLimits", {}).get(1) or {}).get("bottom") == 300.0, printed)
  for invalid in [0, -1, True, 1.5, "invalid", "7x"]:
    b = boundary_for("23. Enunciado", printed=invalid)
    check(f"identity.invalid_printed_{invalid!r}", b["reliable"] and (b.get("currentMarker") or {}).get("numberSource") == "canonical", b)
  text_printed = boundary_for("07. Enunciado", canonical=27, printed="07")
  check("identity.valid_digit_string", text_printed["reliable"] and (text_printed.get("currentMarker") or {}).get("numberSource") == "printed", text_printed)

  for header in ["QUESTÃO - 20", "QUESTÃO – 20", "QUESTÃO — 20", "QUESTÃO: 20", "questao - 20", "ITEM: 20"]:
    b = boundary_for(header, canonical=20)
    check(f"identity.keyword_{header}", b["reliable"] and (b.get("currentMarker") or {}).get("matchGrammar") == "keyword_separator", b)
  for header, number in [("7º Item", 7), ("19° Item", 19), ("7.º Item", 7), ("19.º item", 19)]:
    b = boundary_for(header, canonical=number)
    check(f"identity.ordinal_{header}", b["reliable"] and (b.get("currentMarker") or {}).get("matchGrammar") == "ordinal_item", b)
  for header in ["Questão 14", "Item 14"]:
    b = boundary_for(header, canonical=14)
    check(f"identity.legacy_{header}", b["reliable"] and (b.get("currentMarker") or {}).get("matchGrammar") == "legacy_keyword", b)

  for prefix in ["\uf0d8 ", "• ", "\ue123\ue124 "]:
    text = prefix + "Questão 14"
    b = boundary_for(text, canonical=14)
    marker = b.get("currentMarker") or {}
    check(f"identity.decoration_{prefix!r}", b["reliable"] and marker.get("leadingDecorationNormalized") is True, b)
    check(f"identity.decoration_original_{prefix!r}", marker.get("text") == text, marker)
  embedded = boundary_for("Questão 14 enunciado \uf0d8")
  check("identity.wrong_number_no_fuzzy", not embedded["reliable"], embedded)
  decorated_next = boundary_for("\uf0d8 Questão 14", canonical=14, next_text="\uf0d8 Questão: 15")
  check("identity.decorated_next", decorated_next["reliable"] and (decorated_next.get("nextMarker") or {}).get("leadingDecorationNormalized") is True, decorated_next)

  for body in ["A partir da figura", "Basta observar", "Como mostrado", "Dado o valor", "Entre os pontos"]:
    b = boundary_for("23. " + body)
    check(f"identity.numeric_letter_{body}", b["reliable"] and (b.get("currentMarker") or {}).get("matchGrammar") == "numeric_separator", b)
  for text in ["23-A alternativa/subitem", "23 – A texto", "23—A texto", "Texto 3 referente aos itens 7 a 9", "considere os itens 7 a 9", "considere ITEM 7", "Questão texto 7", "\uf0d8 Texto Questão 7", "23.6 valor decimal"]:
    target = 7 if "7" in text else 23
    b = boundary_for(text, canonical=target)
    check(f"identity.negative_{text}", not b["reliable"] and b["reason"] == "current_marker_not_found", b)

  duplicate = make_bundle({1: [(100, "QUESTÃO - 20"), (300, "Questão 20")]})
  b, _ = run_question(duplicate, data("d", [entry("d:q20", 20, 1, 1)]), "d:q20")
  check("identity.mixed_grammar_duplicate", not b["reliable"] and b["reason"] == "current_marker_ambiguous", b)
  same_grammar = make_bundle({1: [(100, "7º Item"), (300, "7° Item")]})
  b, _ = run_question(same_grammar, data("d", [entry("d:q7", 7, 1, 1)]), "d:q7")
  check("identity.ordinal_duplicate", not b["reliable"] and b["reason"] == "current_marker_ambiguous", b)
  missing_next = boundary_for("Questão - 20", canonical=20, next_text="Questão - 22")
  check("identity.next_wrong_number", not missing_next["reliable"] and missing_next["reason"] == "next_marker_not_found", missing_next)
  duplicate_next = make_bundle({1: [(100, "Questão - 20"), (300, "21º Item"), (400, "Questão 21")]})
  b, _ = run_question(duplicate_next, data("d", [entry("d:q20", 20, 1, 1), entry("d:q21", 21, 1, 1)]), "d:q20")
  check("identity.next_duplicate", not b["reliable"] and b["reason"] == "next_marker_ambiguous", b)
  reset_index = data("d", [entry("d:q7", 7, 1, 1), {**entry("d:q27", 27, 2, 2), "printedQuestionNumber": 7},
                          {**entry("d:q28", 28, 2, 2), "printedQuestionNumber": 8}])
  reset_bundle = make_bundle({1: [(100, "7º Item")], 2: [(100, "7º Item"), (300, "8º Item")]})
  b, _ = run_question(reset_bundle, reset_index, "d:q27")
  check("identity.reset_page", b["reliable"] and (b.get("currentMarker") or {}).get("page") == 2, b)
  check("identity.reset_next", (b.get("nextMarker") or {}).get("number") == 8, b)
  check("identity.frozen_metadata_not_mutated", reset_index["questions"][1]["questionNumber"] == 27 and reset_index["questions"][1]["printedQuestionNumber"] == 7, reset_index)
  global_before = question_boundary.detect_question_markers(make_bundle({1: [(100, "Questão - 20"), (300, "7º Item")]}).lines_as_region_input())
  check("identity.global_grammar_not_extended", global_before == [], global_before)


def test_index_backed_column_peers() -> None:
  def scope(rows, entries, qid):
    bundle = make_bundle({})
    bundle.lines = [line_at(page, top, text, x0, x1) for page, top, text, x0, x1 in rows]
    for i, observed in enumerate(bundle.lines):
      observed.line_index = i
    bundle.page_geometry = {p: {"pdfWidth": 600.0, "pdfHeight": 800.0} for p, *_ in rows}
    boundary, filtered = run_question(bundle, data("synthetic", entries), qid)
    return boundary, filtered

  def verified(boundary, qid):
    return next((v for v in boundary.get("verifiedQuestionStarts", []) if v.get("questionId") == qid), {})

  real = [(1, 100, "9. Esquerda", 40, 250), (1, 100, "10. Direita", 320, 560)]
  entries = [entry("d:q9", 9, 1, 1), entry("d:q10", 10, 1, 1)]
  for qid, peer_id in [("d:q9", "d:q10"), ("d:q10", "d:q9")]:
    b, _ = scope(real, entries, qid)
    check(f"peers.real_columns_{qid}", b["reliable"] and b["boundaryMode"] == "two_column", b)
    check(f"peers.real_evidence_{qid}", (b.get("columnEvidence") or {}).get("peerQuestionId") == peer_id, b)
    check(f"peers.real_unique_{qid}", verified(b, peer_id).get("status") == "unique", b)
  check("peers.optional_api", "document_questions" in inspect.signature(question_boundary.compute_question_boundary).parameters)

  for fake in ["1 6 8", "77. Numero de conteudo"]:
    b, _ = scope([(1, 100, "20. Questao", 40, 250), (1, 100, fake, 320, 560)], [entry("d:q20", 20, 1, 1)], "d:q20")
    check(f"peers.unindexed_{fake}", b["boundaryMode"] == "vertical" and b["columnLimits"] is None, b)
    check(f"peers.unindexed_evidence_{fake}", b.get("columnEvidence") is None, b)

  reference_rows = [(1, 50, "23. Header real", 40, 250), (1, 200, "24. Header real", 40, 250),
                    (1, 400, "Questão 25", 320, 560), (1, 420, "23). Referencia interna", 40, 250)]
  reference_entries = [entry(f"d:q{n}", n, 1, 1) for n in [23, 24, 25]]
  b, _ = scope(reference_rows, reference_entries, "d:q25")
  check("peers.reference_no_split", b["reliable"] and b["boundaryMode"] == "vertical" and b["columnLimits"] is None, b)
  check("peers.duplicate_status", verified(b, "d:q23").get("status") == "ambiguous" and verified(b, "d:q23").get("matchCount") == 2, b)
  check("peers.duplicate_not_selected", b.get("columnEvidence") is None, b)
  b, _ = scope(real, [entry("d:q9", 9, 1, 1), entry("d:q10", 10, 2, 2)], "d:q9")
  check("peers.other_page_ignored", b["boundaryMode"] == "vertical" and not verified(b, "d:q10"), b)

  for text, canonical, printed, grammar in [("07. Peer", 27, 7, "numeric_separator"),
                                           ("7º Item", 7, None, "ordinal_item"),
                                           ("Questão - 20", 20, None, "keyword_separator")]:
    peer_entry = entry("d:peer", canonical, 1, 1)
    if printed is not None:
      peer_entry["printedQuestionNumber"] = printed
    b, _ = scope([(1, 100, "9. Atual", 40, 250), (1, 100, text, 320, 560)], [entry("d:q9", 9, 1, 1), peer_entry], "d:q9")
    evidence = b.get("columnEvidence") or {}
    check(f"peers.variant_split_{text}", b["boundaryMode"] == "two_column", b)
    check(f"peers.variant_grammar_{text}", evidence.get("peerMatchGrammar") == grammar, evidence)
    check(f"peers.variant_source_{text}", evidence.get("peerNumberSource") == ("printed" if printed else "canonical"), evidence)
    check(f"peers.variant_identity_{text}", evidence.get("peerCanonicalQuestionNumber") == canonical and evidence.get("peerObservedQuestionNumber") == (printed or canonical), evidence)
    check(f"peers.variant_evidence_{text}", set(evidence.get("evidence") or []) == {"frozen_index_same_page", "unique_target_match", "parallel_x_separation", "parallel_y_alignment"}, evidence)

  for rows, name in [([(1, 100, "9. Atual", 40, 250), (1, 350, "10. Abaixo", 320, 560)], "vertical_gap"),
                     ([(1, 100, "9. Atual", 40, 250), (1, 150, "10. Indentada", 70, 280)], "small_x_gap")]:
    b, _ = scope(rows, entries, "d:q9")
    check(f"peers.no_parallel_{name}", b["boundaryMode"] == "vertical" and b["columnLimits"] is None, b)
    check(f"peers.unique_but_not_parallel_{name}", verified(b, "d:q10").get("status") == "unique", b)

  three = [(1, 100, "1. Esquerda", 20, 180), (1, 100, "2. Centro", 230, 370), (1, 100, "3. Direita", 440, 590)]
  b, _ = scope(three, [entry(f"d:q{n}", n, 1, 1) for n in [1, 2, 3]], "d:q2")
  check("peers.multiple_sides_blocked", not b["reliable"] and b["reason"] == "parallel_columns_multiple_sides", b)
  check("peers.multiple_sides_verified", verified(b, "d:q1").get("status") == verified(b, "d:q3").get("status") == "unique", b)

  stacked = [(1, 100, "9. Atual", 40, 250), (1, 110, "77. Falso peer", 320, 560), (1, 400, "10. Proxima", 40, 250)]
  b, _ = scope(stacked, entries, "d:q9")
  check("peers.false_peer_bottom_preserved", b["boundaryMode"] == "vertical" and b["pageLimits"][1]["bottom"] == 400.0, b)
  check("peers.vertical_next_identity", (b.get("nextMarker") or {}).get("number") == 10, b)
  missing_entries = [entry("d:q9", 9, 1, 1), entry("d:missing", 11, 1, 1)]
  b, _ = scope([(1, 100, "9. Atual", 40, 250)], missing_entries, "d:q9")
  check("peers.missing_status", verified(b, "d:missing").get("status") == "missing", b)
  check("peers.missing_next_still_blocks", not b["reliable"] and b["reason"] == "next_marker_not_found", b)

  # Ambiguous parallel previous question is not selected as a peer. With both
  # response clusters observed, existing downstream gates must still abstain.
  mixed = real + [(1, 500, "9. Outra ocorrencia", 40, 250)]
  for i, label in enumerate("ABCDE"):
    mixed += [(1, 130 + i * 24, f"({label}) esquerda", 50, 250),
              (1, 130 + i * 24, f"({label}) direita", 330, 560)]
  b, filtered = scope(mixed, entries, "d:q10")
  check("peers.ambiguous_previous_no_split", b["boundaryMode"] == "vertical" and verified(b, "d:q9").get("status") == "ambiguous", b)
  check("peers.ambiguous_mix_safe", option_count(filtered, b) is None, option_count(filtered, b))

  captured = []
  original_native = runner.observations.from_native_pdf
  original_run = runner._run_with_boundary
  original_ocr = runner._run_ocr
  def capture(*args, **kwargs):
    captured.append(kwargs.get("document_questions"))
    return {}
  try:
    native_bundle = make_bundle({1: [(100, "9. Header")]})
    native_bundle.words = [object()]  # admission only; capture prevents layer execution
    runner.observations.from_native_pdf = lambda *args: native_bundle
    runner._run_with_boundary = capture
    runner._run_ocr = capture
    index_doc = data("d", entries)
    for source in ["text_native", "raster"]:
      doc = {"sourceType": source, "canonicalPath": "synthetic.pdf"}
      runner._run_question(doc, entries[0], {}, {}, ROOT, index_doc)
      check(f"peers.runner_context_{source}", captured[-1] == entries, captured[-1])
  finally:
    runner.observations.from_native_pdf = original_native
    runner._run_with_boundary = original_run
    runner._run_ocr = original_ocr


def test_word_boundary_and_local_reconstruction() -> None:
  # A-U: synthetic observation geometry only; no holdout fixtures or GT hints.
  def words(rows):
    result = []
    for page, top, x, tokens in rows:
      for token in tokens:
        width = max(10, len(token) * 6)
        result.append(observations.ObservedWord(page, token, (x, top, x + width, top + 12), len(result), "synthetic"))
        x += width + 6
    return result
  def bundle(rows, lines=None):
    return observations.ObservationBundle(words(rows), lines or [], [],
      {1: {"pdfWidth": 600, "pdfHeight": 800}, 2: {"pdfWidth": 600, "pdfHeight": 800}}, "synthetic")
  def run(b, entries, qid=None):
    return run_question(b, data("d", entries), qid or entries[0]["questionId"])
  def start(b): return b.get("currentMarker") or {}
  def recon(b): return b.get("lineReconstruction") or {}
  current = entry("d:q5", 5, 1, 1)
  nxt = entry("d:q6", 6, 1, 1)
  normal = [line(1, 100, "Questão 5")]
  b, f = run(bundle([(1, 100, 50, ["Questão", "5"])], normal), [current])
  check("words.A.line_priority", start(b).get("matchSource") == "line", b)
  check("words.A.healthy_preserved", f.lines == normal and not recon(b).get("used"), b)
  b, f = run(bundle([(1, 100, 50, ["Questão", "5"])]), [current])
  check("words.B.keyword_missing_line", b["reliable"] and start(b).get("matchSource") == "word_geometry", b)
  check("words.B.provenance", start(b).get("wordIndexes") == [0, 1] and start(b).get("bbox") == [50,100,108,112], b)
  check("words.N.zero_lines_reconstructed", recon(b).get("used") and f.lines[0].text == "Questão 5", b)
  check("words.N.line_source", bool(f.lines) and f.lines[0].source == "reconstructed_from_words", b)
  for tag, rows in [
    ("C.distant", [(1,100,50,["Questão"]),(1,100,350,["5"])]),
    ("C.other_band", [(1,100,50,["Questão"]),(1,160,100,["5"])]),
    ("C.other_page", [(1,100,50,["Questão"]),(2,100,100,["5"])]),
    ("C.intermediate", [(1,100,50,["Questão","texto","5"])]),
    ("D.wrong", [(1,100,50,["Questão","6"])]),
    ("G.year", [(1,100,50,["Questão","2005"])]),
    ("G.footer", [(1,780,50,["05.","Página"])]),
    ("G.decimal", [(1,100,50,["05.5","valor"])]),
    ("H.parent_child", [(1,100,50,["5-A","item"])]),
  ]:
    b, _ = run(bundle(rows), [current])
    check("words." + tag, not b["reliable"] and b["reason"] == "current_marker_not_found", b)
  numeric = [(1,100,50,["05.","Texto","observado"]),(1,400,50,["06.","Próximo","texto"])]
  b, _ = run(bundle(numeric), [current,nxt])
  check("words.E.unique_numeric", b["reliable"] and start(b).get("matchGrammar") == "numeric_separator", b)
  check("words.L.next_word_bottom", b.get("pageLimits", {}).get(1,{}).get("bottom") == 400, b)
  b, _ = run(bundle(numeric + [(1,200,50,["05.","Outro","texto"])]), [current,nxt])
  check("words.F.duplicate_numeric", not b["reliable"] and b["reason"] == "current_marker_ambiguous", b)
  b, _ = run(bundle([(1,100,50,["Questão","5"]),(1,200,50,["Questão","5"])]), [current])
  check("words.F.duplicate_keyword", not b["reliable"] and b["reason"] == "current_marker_ambiguous", b)
  printed = {**entry("d:q27",27,1,1), "printedQuestionNumber": 7}
  b, _ = run(bundle([(1,100,50,["07.","Atual","texto"]),(1,400,50,["08.","Próxima","texto"])]),
             [printed,{**entry("d:q28",28,1,1),"printedQuestionNumber":8}])
  check("words.I.printed", b["reliable"] and start(b).get("observedQuestionNumber") == 7 and start(b).get("canonicalQuestionNumber") == 27, b)
  duplicate_lines = [line(1,100,"Questão 5"), line(1,200,"Questão 5")]
  b, _ = run(bundle([(1,100,50,["Questão","5"])], duplicate_lines), [current])
  check("words.M.line_ambiguity_not_overridden", not b["reliable"] and b["reason"] == "current_marker_ambiguous", b)

  left, right, bottom = entry("d:q2",2,1,1), entry("d:q7",7,1,1), entry("d:q3",3,1,1)
  rows = [(1,100,50,["02.","Esquerda","texto"]),(1,105,350,["07.","Direita","texto"]),
          (1,400,50,["03.","Próxima","texto"])]
  for i, label in enumerate("ABDE"):
    rows += [(1,150+i*30,50,[f"({label})","local",label]), (1,150+i*30,350,[f"({label})","vizinha",label])]
  merged = [observations.ObservedLine(1,"colunas mescladas",(40,90,590,370),source="synthetic",order_ambiguous=True)]
  b, f = run(bundle(rows,merged), [left,bottom,right])
  check("words.J.two_column", b["reliable"] and b["boundaryMode"] == "two_column", b)
  peer = next((s for s in b.get("verifiedQuestionStarts",[]) if s["questionId"]==right["questionId"]),{})
  check("words.J.verified_word_peer", peer.get("status") == "unique" and peer.get("matchSource") == "word_geometry", peer)
  check("words.O.only_scoped_words", bool(f.words) and all(w.bbox[0] < 200 for w in f.words), f.words)
  check("words.O.local_lines", bool(f.lines) and all("vizinha" not in l.text for l in f.lines) and recon(b).get("used"), b)
  check("words.O.provenance_counts", recon(b).get("inputWordCount") == len(f.words) and recon(b).get("outputLineCount") == len(f.lines), b)
  check("words.R.C_not_invented", all("(C)" not in l.text for l in f.lines), f.lines)
  check("words.S.incomplete_still_gated", option_count(f,b) is None, option_count(f,b))
  check("words.U.index_peer", (b.get("columnEvidence") or {}).get("peerQuestionId") == right["questionId"], b)
  b, _ = run(bundle([(1,100,50,["Questão","5"]),(1,100,350,["77.","Não","indexado"])]),[current])
  check("words.K.unindexed_not_peer", b["reliable"] and b["boundaryMode"] == "vertical", b)
  healthy = [line(1,100,"Questão 5")] + [line(1,150+i*30,f"({label}) texto {label}") for i,label in enumerate("ABCDE")]
  hrows = [(1,100,50,["Questão","5"])] + [(1,150+i*30,50,[f"({label})","texto",label]) for i,label in enumerate("ABCDE")]
  b, f = run(bundle(hrows, healthy),[current])
  check("words.Q.healthy_lines_unchanged", f.lines == healthy and not recon(b).get("used"), b)
  check("words.S.selected_set_still_safe", option_count(f,b)==5, option_count(f,b))
  collapsed = [observations.ObservedLine(1,"página toda fundida",(0,0,590,700),source="synthetic")]
  b, f = run(bundle(hrows,collapsed),[current])
  check("words.P.collapsed_reconstructed", recon(b).get("used") and len(f.lines)==6, b)
  check("words.P.parseable", option_count(f,b)==5, option_count(f,b))
  check("words.P.original_unmutated", collapsed[0].text=="página toda fundida", collapsed)
  check("words.P.no_text_changes", [l.text for l in f.lines] == [" ".join(r[3]) for r in hrows], f.lines)
  # Strong line grammar remains authoritative even with contradictory words.
  b, _ = run(bundle([(1,100,50,["Questão","6"])],[line(1,100,"Questão - 5")]),[current])
  check("words.T.03A_grammar", b["reliable"] and start(b).get("matchGrammar")=="keyword_separator" and start(b).get("matchSource")=="line", b)
  # Single index entry + top isolated numeric header with local observed body.
  solo = [(1,100,50,["05.","Texto","observado"]),(1,130,50,["Corpo","do","texto"]),(1,160,50,["Mais","texto"])]
  b, _ = run(bundle(solo,collapsed),[current])
  check("words.E.solo_top_header", b["reliable"], b)
  b, _ = run(bundle([(1,400,50,["05.","número","isolado"])]),[current])
  check("words.E.no_automatic_numeric", not b["reliable"], b)
  # Tall noise may bridge rows in the global grouping, but cannot become a
  # header token or swallow the target's separate baseline.
  noisy = bundle(numeric)
  noisy.words.append(observations.ObservedWord(1,"ruído",(20,80,48,160),99,"synthetic"))
  b, _ = run(noisy,[current,nxt])
  check("words.E.tall_noise_no_header_loss", b["reliable"] and start(b).get("top")==100, b)
  # An unpadded numbered list below the next padded header is not a second
  # index-backed start. Two genuinely corroborated padded duplicates stay ambiguous.
  b, _ = run(bundle(numeric+[(1,500,50,["5.","item","enumerado"])]),[current,nxt])
  check("words.E.list_not_indexed_header", b["reliable"] and start(b).get("top")==100, b)
  header_only_row = [(1,100,50,["05."]),(1,99,76,["Texto","observado","abaixo"]),
                     (1,280,50,["Corpo","observado"]),(1,320,50,["Mais","texto"])]
  b, _ = run(bundle(header_only_row,collapsed),[current])
  check("words.E.header_before_body_row", b["reliable"] and start(b).get("top")==100, b)
  list_rows = numeric + [(1,500+i*24,50,[f"{n}.","item","interno"]) for i,n in enumerate([4,5,6])]
  b, _ = run(bundle(list_rows),[current,nxt])
  check("words.G.internal_numeric_run_rejected", b["reliable"] and start(b).get("top")==100, b)
  b, _ = run(bundle(list_rows[2:]),[current,nxt])
  check("words.G.list_only_not_question_starts", not b["reliable"] and b["reason"]=="current_marker_not_found", b)
  # OCR adapter may return only words. The runner must not discard that bundle.
  originals = runner.observations.from_ocr_payload, runner._run_with_boundary, Path.exists, Path.read_text
  captured = []
  try:
    runner.observations.from_ocr_payload = lambda *a: bundle([(1,100,50,["Questão","5"])])
    runner._run_with_boundary = lambda *a, **k: captured.append(a[0]) or {"test": True}
    Path.exists = lambda *a: True
    Path.read_text = lambda *a, **k: "{}"
    result = runner._run_ocr({"documentId":"synthetic"},current,current,None,[1],ROOT,document_questions=[current])
    check("words.N.runner_words_only", bool(captured) and result == {"test":True}, result)
  finally:
    runner.observations.from_ocr_payload, runner._run_with_boundary, Path.exists, Path.read_text = originals
  b, _ = run(bundle(numeric+[(1,200,50,["Questão","5"])]),[current,nxt])
  check("words.F.mixed_grammar_duplicate", not b["reliable"] and b["reason"]=="current_marker_ambiguous", b)


def main() -> None:
  test_word_boundary_and_local_reconstruction()
  test_index_backed_column_peers()
  test_target_identity_and_grammar()
  test_parallel_two_column_questions()
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
