from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_question_index as indexer  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def line(text: str, page: int, top: float, bottom: float | None = None) -> dict:
  return {"text": text, "page": page, "bbox": [40.0, top, 400.0, bottom if bottom is not None else top + 12.0]}


def test_distinct_pages() -> None:
  lines = [line("Questao 1", 1, 100), line("Questao 2", 2, 100), line("QUESTAO 03", 3, 100)]
  markers = indexer.detect_markers(lines)
  seq = indexer.build_sequence(markers, 3, {1: 1000.0, 2: 1000.0, 3: 1000.0})
  check("distinct.numbers", [q["questionNumber"] for q in seq["questions"]] == [1, 2, 3], seq)
  check("distinct.pagestart", [q["pageStart"] for q in seq["questions"]] == [1, 2, 3], seq)
  check("distinct.pageend", [q["pageEnd"] for q in seq["questions"]] == [1, 2, 3], seq)


def test_two_same_page() -> None:
  markers = [{"number": 1, "page": 1, "top": 100.0, "kind": "keyword"}, {"number": 2, "page": 1, "top": 300.0, "kind": "keyword"}]
  seq = indexer.build_sequence(markers, 1, {1: 1000.0})
  check("samepage.end", seq["questions"][0]["pageEnd"] == 1 and seq["questions"][1]["pageEnd"] == 1, seq)


def test_cross_page() -> None:
  markers = [{"number": 1, "page": 1, "top": 900.0, "kind": "keyword"}, {"number": 2, "page": 2, "top": 40.0, "kind": "keyword"}]
  seq = indexer.build_sequence(markers, 2, {1: 1000.0, 2: 1000.0})
  check("crosspage.end", seq["questions"][0]["pageEnd"] == 1, seq)


def test_missing_number() -> None:
  markers = [{"number": n, "page": n, "top": 100.0, "kind": "keyword"} for n in (1, 2, 4)]
  seq = indexer.build_sequence(markers, 4, {p: 1000.0 for p in range(1, 5)})
  check("missing.no_invention", [q["questionNumber"] for q in seq["questions"]] == [1, 2, 4], seq)
  check("missing.anomaly", any(a["type"] == "missing_question_number" and a["number"] == 3 for a in seq["anomalies"]), seq["anomalies"])


def test_duplicate_number() -> None:
  markers = [{"number": 5, "page": 1, "top": 100.0, "kind": "keyword"}, {"number": 5, "page": 2, "top": 100.0, "kind": "keyword"}]
  seq = indexer.build_sequence(markers, 2, {1: 1000.0, 2: 1000.0})
  check("duplicate.one", len(seq["questions"]) == 1, seq)
  check("duplicate.anomaly", any(a["type"] == "duplicate_question_number" for a in seq["anomalies"]), seq["anomalies"])


def test_parent_child_ignored() -> None:
  lines = [line("QUESTAO 15", 1, 100), line("15-A A Bandeira", 1, 130), line("15-B O Hino", 1, 160), line("15-C ...", 1, 190)]
  markers = indexer.detect_markers(lines)
  check("parentchild.one", len(markers) == 1 and markers[0]["number"] == 15, markers)


def test_roman_ignored() -> None:
  lines = [line("I) primeira resposta", 1, 100), line("II) segunda resposta", 1, 130)]
  check("roman.none", indexer.detect_markers(lines) == [], indexer.detect_markers(lines))
  check("roman.not_sequence", indexer.looks_like_question_sequence([]) is False)


def test_unresolved_when_no_marker() -> None:
  seq = indexer.build_sequence([], 10, {})
  check("unresolved.empty", seq["questions"] == [] and seq["anomalies"] == [])


def test_page_bounds() -> None:
  markers = [{"number": 1, "page": 1, "top": 100.0, "kind": "keyword"}, {"number": 2, "page": 5, "top": 100.0, "kind": "keyword"}]
  seq = indexer.build_sequence(markers, 6, {1: 1000.0, 5: 1000.0})
  for question in seq["questions"]:
    check(f"bounds.{question['questionNumber']}", 1 <= question["pageStart"] <= question["pageEnd"] <= 6, question)


def test_fingerprint_mismatch_blocks() -> None:
  with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "fake.pdf"
    path.write_bytes(b"not a pdf")
    document = {"documentId": "doc-x", "canonicalPath": str(path), "contentFingerprint": "deadbeef"}
    try:
      indexer.index_document(document, allow_ocr=False)
      check("mismatch.blocks", False, "should have raised")
    except RuntimeError as exc:
      check("mismatch.blocks", "source_fingerprint_mismatch" in str(exc), str(exc))


def test_numeric_fallback_and_ocr_like() -> None:
  lines = [line("1. Primeira", 1, 100), line("2. Segunda", 1, 200), line("3. Terceira", 2, 100)]
  markers = indexer.detect_markers(lines)
  check("numeric.fallback", [m["number"] for m in markers] == [1, 2, 3], markers)
  ocr_like = [line("Questao 1", 1, 100), line("Questao 2", 2, 100)]
  check("ocr.sequence", indexer.looks_like_question_sequence(indexer.detect_markers(ocr_like)) is True)


def test_keyword_item_marker() -> None:
  lines = [line("ITEM 01. Primeira afirmacao", 1, 100), line("ITEM 02. Segunda afirmacao", 1, 200)]
  markers = indexer.detect_markers(lines)
  check("item.markers", [m["number"] for m in markers] == [1, 2], markers)
  check("item.kind", all(m["kind"] == "keyword" for m in markers), markers)


def test_item_heading_lowercase() -> None:
  markers = indexer.detect_markers([line("item 27 Considere a situacao", 1, 100)])
  check("itemheading.one", len(markers) == 1 and markers[0]["number"] == 27, markers)


def test_internal_reference_not_start() -> None:
  lines = [line("responda ao item 27 conforme indicado", 1, 100), line("nos itens 21 e 22 discute-se o tema", 1, 130)]
  check("reference.none", indexer.detect_markers(lines) == [], indexer.detect_markers(lines))


def test_bare_numeric_sequence() -> None:
  lines = [line("1 Texto da unidade um", 1, 100), line("2 Texto da unidade dois", 1, 200), line("3 Texto da unidade tres", 1, 300)]
  markers = indexer.detect_markers(lines)
  check("bare.three", [m["number"] for m in markers] == [1, 2, 3], markers)


def test_year_and_decimal_not_markers() -> None:
  check("year.none", indexer.detect_markers([line("2024 foi um ano importante", 1, 100)]) == [])
  check("decimal.none", indexer.detect_markers([line("9.6 million trees in the same area", 1, 100)]) == [])


def test_footer_repetition_suppressed() -> None:
  lines = [
    line("1.o Vestibular de 2009 2.o DIA - 1", 1, 900),
    line("1.o Vestibular de 2009 2.o DIA - 2", 2, 900),
    line("1.o Vestibular de 2009 2.o DIA - 3", 3, 900),
    line("5 Texto de item real", 3, 200),
  ]
  markers = indexer.detect_markers(lines)
  check("footer.suppressed", [m["number"] for m in markers] == [5], markers)


def test_dotted_ocr_and_item_ocr() -> None:
  dotted = indexer.detect_markers([line("01. Primeira", 1, 100), line("02. Segunda", 1, 200), line("03. Terceira", 1, 300)])
  check("dotted.three", [m["number"] for m in dotted] == [1, 2, 3], dotted)
  item = indexer.detect_markers([line("ITEM 03. Terceira afirmacao", 1, 100)])
  check("itemocr.one", len(item) == 1 and item[0]["number"] == 3, item)


def test_uppercase_item_anywhere() -> None:
  markers = indexer.detect_markers([line("fortemente ITEM 16. O finalidade texto", 1, 100)])
  check("itemupper.one", len(markers) == 1 and markers[0]["number"] == 16, markers)


def test_mixed_keyword_numeric_prefers_sequence() -> None:
  lines = [line("QUESTAO 1 Texto", 1, 50)] + [line(f"{n} Texto da unidade", 2, 100 + i * 50) for i, n in enumerate(range(10, 15))]
  markers = indexer.detect_markers(lines)
  check("mixed.numeric", [m["number"] for m in markers] == [10, 11, 12, 13, 14], markers)


def main() -> None:
  test_distinct_pages()
  test_two_same_page()
  test_cross_page()
  test_missing_number()
  test_duplicate_number()
  test_parent_child_ignored()
  test_roman_ignored()
  test_unresolved_when_no_marker()
  test_page_bounds()
  test_fingerprint_mismatch_blocks()
  test_numeric_fallback_and_ocr_like()
  test_keyword_item_marker()
  test_item_heading_lowercase()
  test_internal_reference_not_start()
  test_bare_numeric_sequence()
  test_year_and_decimal_not_markers()
  test_footer_repetition_suppressed()
  test_dotted_ocr_and_item_ocr()
  test_uppercase_item_anywhere()
  test_mixed_keyword_numeric_prefers_sequence()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks do question index neutro passaram.")


if __name__ == "__main__":
  main()
