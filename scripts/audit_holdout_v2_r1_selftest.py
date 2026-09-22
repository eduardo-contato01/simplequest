from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_v2_r1 as r1  # noqa: E402
import audit_holdout_schema as schema  # noqa: E402

FAILURES: list[str] = []

EXPECTED_HASHES = {
  "question-index-v2.json": "0aafa72592c73597d087b8b57150be11f0c8a866ff133a03b6deeea01171afb7",
  "manifest-v2-b2.json": "f1b7d5b24d68b57bc4d954ef92d62c93c18bd59dbdc07ce48a1270a8d4ab2275",
  "question-index-v2-r1.adjudication.json": None,
}


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def _load_all():
  return (
    r1.load_json(r1.QUESTION_INDEX_V2),
    r1.load_json(r1.MANIFEST_B2),
    r1.load_json(r1.GROUND_TRUTH_SCAFFOLD),
    r1.load_json(r1.ADJUDICATION),
  )


def test_frozen_artifacts_unchanged() -> None:
  for name, expected in EXPECTED_HASHES.items():
    path = ROOT / "audit" / "holdout" / name
    if expected is None:
      continue
    check(f"frozen.{name}", schema.sha256_file(path) == expected)


def test_occurrence_ids() -> None:
  questions = r1.adjudicated_questions("doc-7765d0b79b38", r1.adjudication_by_id(_load_all()[3])["doc-7765d0b79b38"]["runs"])
  ids = [question["questionId"] for question in questions]
  check("occurrence.q1_three", [qid for qid in ids if ":q1:" in qid] ==
        ["doc-7765d0b79b38:q1:o1", "doc-7765d0b79b38:q1:o2", "doc-7765d0b79b38:q1:o3"], ids[:12])
  check("occurrence.q11_legacy", "doc-7765d0b79b38:q11" in ids)
  check("occurrence.q11_no_suffix", "doc-7765d0b79b38:q11:o1" not in ids)
  check("occurrence.unique", len(ids) == len(set(ids)))


def test_multiple_runs() -> None:
  adjudication = r1.adjudication_by_id(_load_all()[3])
  questions = r1.adjudicated_questions("doc-1cc59e302f33", adjudication["doc-1cc59e302f33"]["runs"])
  runs = sorted({question["sequenceRun"] for question in questions})
  check("runs.four", runs == [1, 2, 3, 4], runs)
  check("runs.count", len(questions) == 140, len(questions))
  check("runs.reset_q1_present", [q["questionId"] for q in questions].count("doc-1cc59e302f33:q1:o1") == 1)


def test_page_and_counts() -> None:
  adjudication = r1.adjudication_by_id(_load_all()[3])
  for document_id, expected_count in r1.EXPECTED_COUNTS.items():
    questions = r1.adjudicated_questions(document_id, adjudication[document_id]["runs"])
    check(f"count.{document_id}", len(questions) == expected_count, len(questions))
    check(f"pages.{document_id}", all(q["pageStart"] <= q["pageEnd"] for q in questions))
    check(f"idsunique.{document_id}", len({q["questionId"] for q in questions}) == len(questions))


def test_selection_document_order() -> None:
  historical_index, historical_manifest, _, adjudication = _load_all()
  r1_index = r1.build_r1_index(historical_index, adjudication)
  manifest = r1.build_r1_manifest(historical_manifest, r1_index)
  try:
    r1.verify_expected_selections(manifest)
    check("selection.expected", True)
  except schema.HoldoutValidationError as exc:
    check("selection.expected", False, str(exc))
  check("selection.total", sum(len(d["selectedQuestions"]) for d in manifest["documents"]) == 144)
  for document_id, expected_count in r1.EXPECTED_COUNTS.items():
    doc = next(d for d in manifest["documents"] if d["documentId"] == document_id)
    index_doc = next(d for d in r1_index["documents"] if d["documentId"] == document_id)
    check(f"selection.tertile.{document_id}", len(doc["selectedQuestions"]) == 3 and len(index_doc["questions"]) == expected_count)


def test_no_reroll_determinism() -> None:
  historical_index, historical_manifest, _, adjudication = _load_all()
  first = r1.build_r1_manifest(historical_manifest, r1.build_r1_index(historical_index, adjudication))
  second = r1.build_r1_manifest(historical_manifest, r1.build_r1_index(historical_index, adjudication))
  a = [q["questionId"] for d in first["documents"] for q in d["selectedQuestions"]]
  b = [q["questionId"] for d in second["documents"] for q in d["selectedQuestions"]]
  check("reroll.same", a == b)


def test_preserve_untouched_documents() -> None:
  historical_index, historical_manifest, _, adjudication = _load_all()
  adjudicated = set(r1.adjudication_by_id(adjudication))
  r1_index = r1.build_r1_index(historical_index, adjudication)
  manifest = r1.build_r1_manifest(historical_manifest, r1_index)
  index_by_id = {d["documentId"]: d for d in r1_index["documents"]}
  hist_index_by_id = {d["documentId"]: d for d in historical_index["documents"]}
  hist_manifest_by_id = {d["documentId"]: d for d in historical_manifest["documents"]}
  index_ok = all(index_by_id[d]["questions"] == hist_index_by_id[d]["questions"] for d in index_by_id if d not in adjudicated)
  manifest_ok = all(next(x for x in manifest["documents"] if x["documentId"] == d)["selectedQuestions"]
                    == hist_manifest_by_id[d]["selectedQuestions"] for d in hist_manifest_by_id if d not in adjudicated)
  check("preserve.index40", index_ok)
  check("preserve.manifest40", manifest_ok)


def test_ground_truth_migration() -> None:
  historical_index, historical_manifest, historical_gt, adjudication = _load_all()
  adjudicated = set(r1.adjudication_by_id(adjudication))
  r1_index = r1.build_r1_index(historical_index, adjudication)
  manifest = r1.build_r1_manifest(historical_manifest, r1_index)
  scaffold = r1.build_gt_scaffold(manifest, r1_index, manifest_file_sha256="x", index_file_sha256="y")
  scaffold, report = r1.migrate_ground_truth(historical_gt, scaffold, adjudicated)
  schema.validate_ground_truth(scaffold)
  check("gt.total", report["total"] == 144, report["total"])
  check("gt.annotated", report["annotated"] == 31, report["annotated"])
  check("gt.unknown", report["unknown"] == 113, report["unknown"])
  check("gt.ambiguous", report["ambiguousCount"] == 0, report["ambiguous"])
  check("gt.missing", report["missingCount"] == 0, report["missing"])
  check("gt.dropped_annotated", report["droppedAnnotatedCount"] == 5, report["droppedAnnotated"])
  check("gt.migrated_145e_q83", "doc-145e6ae80517:q83" in report["migrated"])


def main() -> None:
  test_frozen_artifacts_unchanged()
  test_occurrence_ids()
  test_multiple_runs()
  test_page_and_counts()
  test_selection_document_order()
  test_no_reroll_determinism()
  test_preserve_untouched_documents()
  test_ground_truth_migration()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks do Holdout V2 R1 passaram.")


if __name__ == "__main__":
  main()
