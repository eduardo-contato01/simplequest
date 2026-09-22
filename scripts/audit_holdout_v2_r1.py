from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import audit_holdout_schema as schema
import audit_response_holdout_select as selector

ROOT = Path(__file__).resolve().parents[1]

QUESTION_INDEX_V2 = ROOT / "audit" / "holdout" / "question-index-v2.json"
MANIFEST_B2 = ROOT / "audit" / "holdout" / "manifest-v2-b2.json"
ADJUDICATION = ROOT / "audit" / "holdout" / "question-index-v2-r1.adjudication.json"

QUESTION_INDEX_R1 = ROOT / "audit" / "holdout" / "question-index-v2-r1.json"
QUESTION_INDEX_R1_PROVENANCE = ROOT / "audit" / "holdout" / "question-index-v2-r1.provenance.json"
MANIFEST_B2_R1 = ROOT / "audit" / "holdout" / "manifest-v2-b2-r1.json"
MANIFEST_B2_R1_PROVENANCE = ROOT / "audit" / "holdout" / "manifest-v2-b2-r1.provenance.json"

GROUND_TRUTH_SCAFFOLD = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-scaffold.json"
GROUND_TRUTH_R1_SCAFFOLD = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-r1-scaffold.json"
GROUND_TRUTH_R1_REPORT = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-r1-migration-report.json"

SELECTOR_PATH = ROOT / "scripts" / "audit_response_holdout_select.py"

SELECTION_SEED = 20260918
QUESTIONS_PER_DOCUMENT = 3

ID_POLICY = (
  "legacy docId:qN when N appears once; docId:qN:oK (K = 1-based document order "
  "occurrence) when N appears more than once in the same document"
)
PAGE_END_POLICY = (
  "conservative forward extension: pageEnd is the pageStart of the next "
  "adjudicated question in document order (its own pageStart for the final "
  "question); may overestimate but never truncates before the next unit"
)

# Expected frozen selection for the 8 adjudicated documents (questionId suffix, pageStart).
EXPECTED_SELECTIONS: dict[str, list[tuple[str, int]]] = {
  "doc-2db0fa23d7c8": [("q5", 2), ("q11", 4), ("q20", 7)],
  "doc-145e6ae80517": [("q31", 4), ("q83", 10), ("q113", 13)],
  "doc-1cc59e302f33": [("q24", 8), ("q60", 13), ("q111", 21)],
  "doc-381cca4d6df1": [("q11", 11), ("q14", 14), ("q38", 34)],
  "doc-6b61dd9acf63": [("q4", 5), ("q9", 6), ("q13", 7)],
  "doc-7765d0b79b38": [("q1:o2", 2), ("q28", 7), ("q95", 13)],
  "doc-9e5d2df289e0": [("q5", 5), ("q12", 8), ("q16", 10)],
  "doc-a32f45208796": [("q23", 7), ("q44", 10), ("q97", 17)],
}

EXPECTED_COUNTS = {
  "doc-2db0fa23d7c8": 20,
  "doc-145e6ae80517": 150,
  "doc-1cc59e302f33": 140,
  "doc-381cca4d6df1": 40,
  "doc-6b61dd9acf63": 14,
  "doc-7765d0b79b38": 130,
  "doc-9e5d2df289e0": 20,
  "doc-a32f45208796": 130,
}


def load_json(path: str | Path) -> Any:
  return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
  target = Path(path)
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def adjudication_by_id(adjudication: dict[str, Any]) -> dict[str, dict[str, Any]]:
  return {document["documentId"]: document for document in adjudication["documents"]}


def adjudicated_questions(document_id: str, runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
  rows: list[tuple[int, int, int]] = []
  for run in runs:
    run_ordinal = int(run["runOrdinal"])
    for span in run["spans"]:
      page = int(span["pageStart"])
      for number in span["questionNumbers"]:
        rows.append((run_ordinal, page, int(number)))
  totals = Counter(number for _, _, number in rows)
  seen: Counter[int] = Counter()
  questions: list[dict[str, Any]] = []
  for run_ordinal, page, number in rows:
    if totals[number] == 1:
      question_id = f"{document_id}:q{number}"
    else:
      seen[number] += 1
      question_id = f"{document_id}:q{number}:o{seen[number]}"
    questions.append({
      "questionId": question_id,
      "questionNumber": number,
      "pageStart": page,
      "pageEnd": page,
      "sequenceRun": run_ordinal,
    })
  for index, question in enumerate(questions):
    if index + 1 < len(questions) and questions[index + 1]["pageStart"] > question["pageStart"]:
      question["pageEnd"] = questions[index + 1]["pageStart"]
  return questions


def build_r1_index(historical_index: dict[str, Any], adjudication: dict[str, Any]) -> dict[str, Any]:
  adj = adjudication_by_id(adjudication)
  r1 = {
    "protocolVersion": historical_index["protocolVersion"],
    "indexMethodVersion": historical_index["indexMethodVersion"],
    "createdFromManifest": historical_index["createdFromManifest"],
    "manifestFileSha256": historical_index["manifestFileSha256"],
    "manifestCanonicalJsonSha256": historical_index["manifestCanonicalJsonSha256"],
    "ocrConfig": historical_index.get("ocrConfig"),
    "revision": "r1",
    "adjudication": "question-index-v2-r1.adjudication.json",
    "adjudicatedDocuments": sorted(adj),
    "documents": [
      {
        "documentId": document["documentId"],
        "contentFingerprint": document["contentFingerprint"],
        "questions": adjudicated_questions(document["documentId"], adj[document["documentId"]]["runs"])
        if document["documentId"] in adj else copy.deepcopy(document["questions"]),
      }
      for document in historical_index["documents"]
    ],
    "indexingAnomalies": [
      anomaly for anomaly in historical_index.get("indexingAnomalies", [])
      if anomaly.get("documentId") not in adj
    ],
  }
  return r1


def build_r1_manifest(historical_manifest: dict[str, Any], r1_index: dict[str, Any],
                      seed: int = SELECTION_SEED, count: int = QUESTIONS_PER_DOCUMENT) -> dict[str, Any]:
  index_by_id = {document["documentId"]: document for document in r1_index["documents"]}
  manifest = copy.deepcopy(historical_manifest)
  for document in manifest["documents"]:
    index_document = index_by_id[document["documentId"]]
    document["selectedQuestions"] = selector.select_questions(
      index_document["questions"], seed, document["documentId"], count,
    )
  return manifest


def question_selection_hash(manifest: dict[str, Any]) -> str:
  payload = []
  for document in sorted(manifest["documents"], key=lambda item: item["documentId"]):
    for question in document["selectedQuestions"]:
      payload.append({
        "documentId": document["documentId"],
        "questionId": question["questionId"],
        "questionNumber": question["questionNumber"],
        "pageStart": question["pageStart"],
      })
  return schema.sha256_json(payload)


def _gt_defaults(document_id: str, question: dict[str, Any]) -> dict[str, Any]:
  return {
    "documentId": document_id,
    "questionId": question["questionId"],
    "pages": [question["pageStart"]],
    "responseMode": "unknown",
    "optionCount": None,
    "optionLabels": None,
    "subitems": None,
    "responseControls": None,
    "layout": "unknown",
    "markerStyle": "unknown",
    "contentKind": "unknown",
    "notes": None,
  }


def build_gt_scaffold(manifest: dict[str, Any], question_index: dict[str, Any],
                      manifest_file_sha256: str | None = None,
                      index_file_sha256: str | None = None) -> dict[str, Any]:
  questions = []
  for document in manifest["documents"]:
    for question in document["selectedQuestions"]:
      questions.append(_gt_defaults(document["documentId"], question))
  fingerprints = {document["documentId"]: document["contentFingerprint"] for document in manifest["documents"]}
  return {
    "_workingCopy": "Blind structural GT scaffold (R1). Do not run Auditor until annotation is complete.",
    "protocolVersion": manifest["protocolVersion"],
    "manifestSha256": schema.sha256_json(manifest),
    "sourceManifestFileSha256": manifest_file_sha256,
    "questionIndexFileSha256": index_file_sha256,
    "documentFingerprints": fingerprints,
    "questions": questions,
  }


ANNOTATION_FIELDS = ("pages", "responseMode", "optionCount", "optionLabels", "subitems",
                     "responseControls", "layout", "markerStyle", "contentKind", "notes")


def number_from_question_id(question_id: str) -> int | None:
  marker = ":q"
  index = question_id.rfind(marker)
  if index < 0:
    return None
  digits = ""
  for char in question_id[index + len(marker):]:
    if char.isdigit():
      digits += char
    else:
      break
  return int(digits) if digits else None


def migrate_ground_truth(old_gt: dict[str, Any], new_gt: dict[str, Any],
                         adjudicated_documents: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
  old_by_document: dict[str, list[dict[str, Any]]] = {}
  for entry in old_gt["questions"]:
    old_by_document.setdefault(entry["documentId"], []).append(entry)

  migrated: list[str] = []
  newly_selected: list[str] = []
  ambiguous: list[str] = []
  missing: list[str] = []
  matched_old_ids: set[str] = set()

  for entry in new_gt["questions"]:
    document_id = entry["documentId"]
    candidates = [candidate for candidate in old_by_document.get(document_id, [])
                  if candidate["questionId"] == entry["questionId"]]
    if len(candidates) > 1:
      ambiguous.append(entry["questionId"])
      continue
    if not candidates and document_id in adjudicated_documents:
      entry_number = number_from_question_id(entry["questionId"])
      candidates = [candidate for candidate in old_by_document.get(document_id, [])
                    if number_from_question_id(candidate["questionId"]) == entry_number
                    and entry["pageStart"] in (candidate.get("pages") or [])]
      if len(candidates) > 1:
        ambiguous.append(entry["questionId"])
        continue
    if candidates:
      source = candidates[0]
      for field in ANNOTATION_FIELDS:
        if field in source:
          entry[field] = source[field]
      matched_old_ids.add(source["questionId"])
      migrated.append(entry["questionId"])
    else:
      newly_selected.append(entry["questionId"])

  old_selected_ids = {entry["questionId"] for entry in old_gt["questions"]}
  new_selected_ids = {entry["questionId"] for entry in new_gt["questions"]}
  dropped = sorted(old_selected_ids - new_selected_ids)
  old_annotated = {entry["questionId"] for entry in old_gt["questions"] if entry["responseMode"] != "unknown"}
  dropped_annotated = sorted(question_id for question_id in dropped if question_id in old_annotated)

  annotated = sum(1 for entry in new_gt["questions"] if entry["responseMode"] != "unknown")
  report = {
    "migrated": sorted(migrated),
    "migratedCount": len(migrated),
    "droppedFromCurrentSelection": dropped,
    "droppedFromCurrentSelectionCount": len(dropped),
    "droppedAnnotated": dropped_annotated,
    "droppedAnnotatedCount": len(dropped_annotated),
    "newlySelected": sorted(newly_selected),
    "newlySelectedCount": len(newly_selected),
    "ambiguous": sorted(ambiguous),
    "ambiguousCount": len(ambiguous),
    "missing": sorted(missing),
    "missingCount": len(missing),
    "annotated": annotated,
    "unknown": len(new_gt["questions"]) - annotated,
    "total": len(new_gt["questions"]),
  }
  return new_gt, report


def verify_expected_selections(manifest: dict[str, Any]) -> None:
  for document in manifest["documents"]:
    document_id = document["documentId"]
    if document_id not in EXPECTED_SELECTIONS:
      continue
    suffix = lambda question_id: question_id.split(":", 1)[1]
    got = [(suffix(question["questionId"]), question["pageStart"]) for question in document["selectedQuestions"]]
    expected = EXPECTED_SELECTIONS[document_id]
    if got != expected:
      raise schema.HoldoutValidationError(
        f"R1 selection mismatch for {document_id}: got {got} expected {expected}"
      )


def materialize() -> dict[str, Any]:
  historical_index = load_json(QUESTION_INDEX_V2)
  historical_manifest = load_json(MANIFEST_B2)
  historical_gt = load_json(GROUND_TRUTH_SCAFFOLD)
  adjudication = load_json(ADJUDICATION)

  identity = selector.code_identity()

  r1_index = build_r1_index(historical_index, adjudication)
  schema.validate_question_index(r1_index)

  r1_manifest = build_r1_manifest(historical_manifest, r1_index)
  schema.validate_manifest(r1_manifest)
  verify_expected_selections(r1_manifest)

  adjudicated_documents = set(adjudication_by_id(adjudication))

  # Determinism: a second, independent construction must be byte-identical.
  r1_manifest_again = build_r1_manifest(historical_manifest, build_r1_index(historical_index, adjudication))
  deterministic = json.dumps(r1_manifest, ensure_ascii=False, sort_keys=True) == \
    json.dumps(r1_manifest_again, ensure_ascii=False, sort_keys=True)
  if not deterministic:
    raise schema.HoldoutValidationError("R1 manifest is not deterministic")

  write_json(QUESTION_INDEX_R1, r1_index)
  write_json(MANIFEST_B2_R1, r1_manifest)

  schema.validate_bindings(r1_manifest, question_index=r1_index)

  scaffold = build_gt_scaffold(
    r1_manifest, r1_index,
    manifest_file_sha256=schema.sha256_file(MANIFEST_B2_R1),
    index_file_sha256=schema.sha256_file(QUESTION_INDEX_R1),
  )
  scaffold, migration = migrate_ground_truth(historical_gt, scaffold, adjudicated_documents)

  if migration["ambiguousCount"] != 0:
    raise schema.HoldoutValidationError(f"GT migration ambiguous: {migration['ambiguous']}")
  if migration["missingCount"] != 0:
    raise schema.HoldoutValidationError(f"GT migration missing: {migration['missing']}")

  schema.validate_ground_truth(scaffold)
  schema.validate_bindings(r1_manifest, question_index=r1_index, ground_truth=scaffold)
  write_json(GROUND_TRUTH_R1_SCAFFOLD, scaffold)

  materializer_sha = schema.sha256_file(Path(__file__).resolve())
  adjudication_sha = schema.sha256_file(ADJUDICATION)
  selector_sha = schema.sha256_file(SELECTOR_PATH)

  index_provenance = {
    "artifactType": "holdout-v2-r1-question-index-provenance",
    "protocolVersion": r1_index["protocolVersion"],
    "parentQuestionIndex": "audit/holdout/question-index-v2.json",
    "parentQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_V2),
    "adjudication": "audit/holdout/question-index-v2-r1.adjudication.json",
    "adjudicationFileSha256": adjudication_sha,
    "materializer": "scripts/audit_holdout_v2_r1.py",
    "materializerSha256": materializer_sha,
    "materializationGitCommit": identity["gitCommit"],
    "materializerCodeState": identity["selectionCodeState"],
    "adjudicatedDocuments": sorted(adjudicated_documents),
    "preservedDocuments": len(r1_index["documents"]) - len(adjudicated_documents),
    "idPolicy": ID_POLICY,
    "pageEndPolicy": PAGE_END_POLICY,
    "responseStructureObserved": False,
    "outputQuestionIndex": "audit/holdout/question-index-v2-r1.json",
    "outputQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_R1),
    "deterministic": True,
  }
  write_json(QUESTION_INDEX_R1_PROVENANCE, index_provenance)

  manifest_provenance = {
    "artifactType": "holdout-v2-r1-question-selection-provenance",
    "protocolVersion": r1_manifest["protocolVersion"],
    "parentQuestionIndex": "audit/holdout/question-index-v2-r1.json",
    "parentQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_R1),
    "parentManifestB2": "audit/holdout/manifest-v2-b2.json",
    "parentManifestB2FileSha256": schema.sha256_file(MANIFEST_B2),
    "adjudication": "audit/holdout/question-index-v2-r1.adjudication.json",
    "adjudicationFileSha256": adjudication_sha,
    "materializer": "scripts/audit_holdout_v2_r1.py",
    "materializerSha256": materializer_sha,
    "materializationGitCommit": identity["gitCommit"],
    "materializerCodeState": identity["selectionCodeState"],
    "selectionSeed": r1_manifest["selectionSeed"],
    "questionsPerDocument": int(r1_manifest["selectionConfig"]["questionsPerDocument"]),
    "documents": len(r1_manifest["documents"]),
    "selectedQuestionsTotal": sum(len(document["selectedQuestions"]) for document in r1_manifest["documents"]),
    "selectionMethod": "one random question per document-order tertile (frozen select_questions)",
    "questionSelectionHash": question_selection_hash(r1_manifest),
    "selectionCodeSha256": selector_sha,
    "outputManifest": "audit/holdout/manifest-v2-b2-r1.json",
    "outputManifestFileSha256": schema.sha256_file(MANIFEST_B2_R1),
    "idPolicy": ID_POLICY,
    "pageEndPolicy": PAGE_END_POLICY,
    "determinismCheck": "independent recomputation produced an identical manifest",
    "deterministic": deterministic,
  }
  write_json(MANIFEST_B2_R1_PROVENANCE, manifest_provenance)

  report = {
    "artifactType": "holdout-v2-r1-ground-truth-migration-report",
    "protocolVersion": r1_manifest["protocolVersion"],
    "manifest": "audit/holdout/manifest-v2-b2-r1.json",
    "manifestFileSha256": schema.sha256_file(MANIFEST_B2_R1),
    "parentGroundTruth": "outputs/audit/holdout/ground-truth-v2-scaffold.json",
    "parentGroundTruthFileSha256": schema.sha256_file(GROUND_TRUTH_SCAFFOLD),
    "outputGroundTruth": "outputs/audit/holdout/ground-truth-v2-r1-scaffold.json",
    "outputGroundTruthFileSha256": schema.sha256_file(GROUND_TRUTH_R1_SCAFFOLD),
    **migration,
  }
  write_json(GROUND_TRUTH_R1_REPORT, report)

  return {
    "index": r1_index,
    "manifest": r1_manifest,
    "scaffold": scaffold,
    "migration": report,
    "indexProvenance": index_provenance,
    "manifestProvenance": manifest_provenance,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description="Materialize the neutral Holdout V2 R1 revision.")
  parser.add_argument("--check", action="store_true", help="validate without writing artifacts")
  args = parser.parse_args()
  if args.check:
    historical_index = load_json(QUESTION_INDEX_V2)
    historical_manifest = load_json(MANIFEST_B2)
    adjudication = load_json(ADJUDICATION)
    r1_index = build_r1_index(historical_index, adjudication)
    r1_manifest = build_r1_manifest(historical_manifest, r1_index)
    verify_expected_selections(r1_manifest)
    print(json.dumps({"status": "ok", "check": True,
                      "documents": len(r1_manifest["documents"]),
                      "selectedQuestions": sum(len(d["selectedQuestions"]) for d in r1_manifest["documents"])}))
    return
  result = materialize()
  print(json.dumps({
    "status": "ok",
    "documents": len(result["manifest"]["documents"]),
    "selectedQuestions": sum(len(d["selectedQuestions"]) for d in result["manifest"]["documents"]),
    "questionSelectionHash": result["manifestProvenance"]["questionSelectionHash"],
    "migration": {"migrated": result["migration"]["migratedCount"],
                  "unknown": result["migration"]["unknown"],
                  "droppedAnnotated": result["migration"]["droppedAnnotatedCount"]},
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
