from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_v2_r2 as r2  # noqa: E402
import audit_holdout_schema as schema  # noqa: E402

FAILURES: list[str] = []

EXPECTED_HASHES = {
  "question-index-v2.json": "0aafa72592c73597d087b8b57150be11f0c8a866ff133a03b6deeea01171afb7",
  "manifest-v2-b2.json": "f1b7d5b24d68b57bc4d954ef92d62c93c18bd59dbdc07ce48a1270a8d4ab2275",
  "question-index-v2-r1.json": "e9f9d8a3c1a7d7f617d76f8fb92d9facdaccecdbbab2600ec8bff69807c39686",
  "manifest-v2-b2-r1.json": "b506578b591d187f154d3a0dd8e5d579d65e06225c799808c83d681aa6f11a26",
}

EXPECTED_R2_COUNTS = {
  "doc-e57019a7359b": 40, "doc-98decdcd5e66": 20, "doc-f24160c86424": 30,
  "doc-5b13e6839c6f": 20, "doc-05a2dbd5dc88": 40, "doc-3abeaa820030": 40,
  "doc-fc9052837176": 24, "doc-018fde8484ec": 40, "doc-dbb0fb93b539": 20,
  "doc-00dc74ed4789": 20, "doc-416026f09a09": 20, "doc-0ccd40b73099": 20,
  "doc-8084259f61f8": 20, "doc-fb15983ac5ea": 30, "doc-530c1f0284e3": 40,
  "doc-7edc53bcc309": 20, "doc-c494569a6fe7": 20, "doc-9a32009f9e63": 24,
  "doc-7bc527197266": 150, "doc-8d679e7b8193": 150,
}

HUMAN_PAGES = {
  "doc-3abeaa820030:q9": [6],
  "doc-530c1f0284e3:q24": [12],
  "doc-5b13e6839c6f:q16": [9],
  "doc-83a6bd21c3df:q12": [15, 16],
  "doc-83a6bd21c3df:q18": [21],
}


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def _load():
  return (
    r2.load_json(r2.QUESTION_INDEX_R1),
    r2.load_json(r2.MANIFEST_B2_R1),
    r2.load_json(r2.ADJUDICATION),
    r2.load_json(r2.GT_R1_SCAFFOLD),
  )


def test_frozen_artifacts() -> None:
  for name, expected in EXPECTED_HASHES.items():
    check(f"frozen.{name}", schema.sha256_file(ROOT / "audit" / "holdout" / name) == expected)
  check("frozen.gt_r1", schema.sha256_file(r2.GT_R1_SCAFFOLD) ==
        "475e4f3dc8f280f8f2d0d832cebc1b4440867c270483957d09204e2de28f466f")


def test_adjudication_consolidation() -> None:
  adjudication = r2.load_json(r2.ADJUDICATION)
  check("adjudication.count", len(adjudication["documents"]) == 20, len(adjudication["documents"]))
  sources = {document["source"] for document in adjudication["documents"]}
  check("adjudication.sources", sources == {"r2-neutral-review", "r2-vest-neutral-review"}, sources)
  for document in adjudication["documents"]:
    expected = EXPECTED_R2_COUNTS[document["documentId"]]
    total = sum(len(span["questionNumbers"]) for run in document["runs"] for span in run["spans"])
    check(f"adjudication.count.{document['documentId']}", total == expected, total)


def test_index_r2() -> None:
  r1_index, r1_manifest, adjudication, _ = _load()
  adj = r2.adjudication_by_id(adjudication)
  index = r2.build_r2_index(r1_index, adjudication)
  check("index.documents", len(index["documents"]) == 48)
  check("index.ids", {d["documentId"] for d in index["documents"]} == {d["documentId"] for d in r1_index["documents"]})
  check("index.fingerprints", {d["contentFingerprint"] for d in index["documents"]} ==
        {d["contentFingerprint"] for d in r1_index["documents"]})
  r1_by_id = {d["documentId"]: d["questions"] for d in r1_index["documents"]}
  index_by_id = {d["documentId"]: d["questions"] for d in index["documents"]}
  preserved = [d for d in index_by_id if d not in adj and index_by_id[d] != r1_by_id[d]]
  check("index.preserve28", preserved == [], preserved)
  for document_id, expected in EXPECTED_R2_COUNTS.items():
    count = len(index_by_id[document_id])
    check(f"index.count.{document_id}", count == expected, count)
    nums = [q["questionNumber"] for q in index_by_id[document_id]]
    check(f"index.contiguous.{document_id}", nums == list(range(1, count + 1)))
  # no false Q38 in CMSM 2006 Portuguese
  check("index.no_q38_cmsm2006", 38 not in [q["questionNumber"] for q in index_by_id["doc-98decdcd5e66"]])
  # CMS 2021 canonical pageStarts
  pages = {q["questionNumber"]: q["pageStart"] for q in index_by_id["doc-9a32009f9e63"]}
  check("index.cms2021.pages", (pages[3], pages[13], pages[18]) == (4, 15, 18), (pages[3], pages[13], pages[18]))
  # VEST
  for vest in ("doc-7bc527197266", "doc-8d679e7b8193"):
    nums = [q["questionNumber"] for q in index_by_id[vest]]
    check(f"index.vest.{vest}", nums == list(range(1, 151)), nums[:5])
  # document order = numeric order for these docs
  for document_id in EXPECTED_R2_COUNTS:
    pages_seq = [q["pageStart"] for q in index_by_id[document_id]]
    check(f"index.order.{document_id}", pages_seq == sorted(pages_seq), pages_seq[:10])


def test_selection_r2() -> None:
  r1_index, r1_manifest, _, _ = _load()
  adjudication = r2.load_json(r2.ADJUDICATION)
  index = r2.build_r2_index(r1_index, adjudication)
  manifest = r2.build_r2_manifest(r1_manifest, index)
  check("manifest.documents", len(manifest["documents"]) == 48)
  total = sum(len(d["selectedQuestions"]) for d in manifest["documents"])
  check("manifest.144", total == 144, total)
  check("manifest.3each", all(len(d["selectedQuestions"]) == 3 for d in manifest["documents"]))
  check("manifest.ids", {d["documentId"] for d in manifest["documents"]} ==
        {d["documentId"] for d in r1_manifest["documents"]})
  check("manifest.fingerprints", {d["contentFingerprint"] for d in manifest["documents"]} ==
        {d["contentFingerprint"] for d in r1_manifest["documents"]})
  # deterministic, no reroll
  again = r2.build_r2_manifest(r1_manifest, r2.build_r2_index(r1_index, adjudication))
  a = [q["questionId"] for d in manifest["documents"] for q in d["selectedQuestions"]]
  b = [q["questionId"] for d in again["documents"] for q in d["selectedQuestions"]]
  check("manifest.deterministic", a == b)


def test_gt_migration() -> None:
  r1_index, r1_manifest, adjudication, r1_gt = _load()
  index = r2.build_r2_index(r1_index, adjudication)
  manifest = r2.build_r2_manifest(r1_manifest, index)
  scaffold = r2.build_gt_scaffold(manifest, manifest_file_sha256="x", index_file_sha256="y")
  scaffold, report = r2.migrate_ground_truth(r1_gt, scaffold, set(r2.adjudication_by_id(adjudication)))
  schema.validate_ground_truth(scaffold)
  check("gt.total", report["total"] == 144, report["total"])
  check("gt.source", (report["sourceAnnotated"], report["sourceUnknown"]) == (91, 53))
  check("gt.ambiguous", report["ambiguousCount"] == 0, report["ambiguous"])
  check("gt.missing", report["missingCount"] == 0, report["missing"])
  check("gt.target", report["targetAnnotated"] + report["targetUnknown"] == 144)
  by_id = {q["questionId"]: q for q in scaffold["questions"]}
  for question_id, pages in HUMAN_PAGES.items():
    check(f"gt.humanpages.{question_id}", by_id.get(question_id, {}).get("pages") == pages,
          by_id.get(question_id, {}).get("pages"))


def main() -> None:
  test_frozen_artifacts()
  test_adjudication_consolidation()
  test_index_r2()
  test_selection_r2()
  test_gt_migration()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks do Holdout V2 R2 passaram.")


if __name__ == "__main__":
  main()
