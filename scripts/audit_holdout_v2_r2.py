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

QUESTION_INDEX_R1 = ROOT / "audit" / "holdout" / "question-index-v2-r1.json"
MANIFEST_B2_R1 = ROOT / "audit" / "holdout" / "manifest-v2-b2-r1.json"

ADJUDICATION = ROOT / "audit" / "holdout" / "question-index-v2-r2.adjudication.json"
QUESTION_INDEX_R2 = ROOT / "audit" / "holdout" / "question-index-v2-r2.json"
QUESTION_INDEX_R2_PROVENANCE = ROOT / "audit" / "holdout" / "question-index-v2-r2.provenance.json"
MANIFEST_B2_R2 = ROOT / "audit" / "holdout" / "manifest-v2-b2-r2.json"
MANIFEST_B2_R2_PROVENANCE = ROOT / "audit" / "holdout" / "manifest-v2-b2-r2.provenance.json"

R2_MAIN_REVIEW = ROOT / "outputs" / "audit" / "holdout" / "r2-neutral-review.json"
R2_VEST_REVIEW = ROOT / "outputs" / "audit" / "holdout" / "r2-vest-neutral-review.json"

GT_R1_SCAFFOLD = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-r1-scaffold.json"
GT_R2_SCAFFOLD = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-r2-scaffold.json"
GT_R2_REPORT = ROOT / "outputs" / "audit" / "holdout" / "ground-truth-v2-r2-migration-report.json"

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

ANNOTATION_FIELDS = ("pages", "responseMode", "optionCount", "optionLabels", "subitems",
                     "responseControls", "layout", "markerStyle", "contentKind", "notes")


def load_json(path: str | Path) -> Any:
  return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
  target = Path(path)
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _questions_to_spans(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
  spans: list[dict[str, Any]] = []
  current_page = None
  current_numbers: list[int] = []
  for question in questions:
    page = int(question["pageStart"])
    if page != current_page:
      if current_numbers:
        spans.append({"pageStart": current_page, "questionNumbers": current_numbers})
      current_page = page
      current_numbers = []
    current_numbers.append(int(question["questionNumber"]))
  if current_numbers:
    spans.append({"pageStart": current_page, "questionNumbers": current_numbers})
  return spans


def build_adjudication(main_review: dict[str, Any], vest_review: dict[str, Any],
                       r1_manifest: dict[str, Any]) -> dict[str, Any]:
  path_by_id = {document["documentId"]: document["canonicalPath"] for document in r1_manifest["documents"]}
  documents = []
  sources: dict[str, str] = {}
  for source_name, review in (("r2-neutral-review", main_review), ("r2-vest-neutral-review", vest_review)):
    for entry in review["documents"]:
      document_id = entry["documentId"]
      if entry["status"] != "resolved":
        if source_name == "r2-neutral-review":
          # superseded by the dedicated VEST review
          continue
        raise schema.HoldoutValidationError(f"R2 review not resolved: {document_id}")
      questions = []
      for run in entry["runs"]:
        questions.extend(run["questions"])
      documents.append({
        "documentId": document_id,
        "canonicalPath": path_by_id[document_id],
        "source": source_name,
        "runs": [{
          "runOrdinal": run["runOrdinal"],
          "spans": _questions_to_spans(run["questions"]),
        } for run in entry["runs"]],
      })
      sources[document_id] = source_name
  documents.sort(key=lambda item: item["documentId"])
  return {
    "artifactType": "holdout-v2-neutral-boundary-adjudication",
    "adjudicationVersion": "neutral-human-r2",
    "protocolVersion": "holdout-v2",
    "basis": "question number, document order, start page and sequence runs only",
    "responseStructureObserved": False,
    "reviewArtifacts": {
      "r2NeutralReview": {"path": "outputs/audit/holdout/r2-neutral-review.json",
                          "sha256": schema.sha256_file(R2_MAIN_REVIEW)},
      "r2VestNeutralReview": {"path": "outputs/audit/holdout/r2-vest-neutral-review.json",
                              "sha256": schema.sha256_file(R2_VEST_REVIEW)},
    },
    "documents": documents,
  }


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


def build_r2_index(r1_index: dict[str, Any], adjudication: dict[str, Any]) -> dict[str, Any]:
  adj = adjudication_by_id(adjudication)
  r2 = {
    "protocolVersion": r1_index["protocolVersion"],
    "indexMethodVersion": r1_index["indexMethodVersion"],
    "createdFromManifest": r1_index["createdFromManifest"],
    "manifestFileSha256": r1_index["manifestFileSha256"],
    "manifestCanonicalJsonSha256": r1_index["manifestCanonicalJsonSha256"],
    "ocrConfig": r1_index.get("ocrConfig"),
    "revision": "r2",
    "parentRevision": "r1",
    "adjudication": "question-index-v2-r2.adjudication.json",
    "adjudicatedDocuments": sorted(adj),
    "documents": [
      {
        "documentId": document["documentId"],
        "contentFingerprint": document["contentFingerprint"],
        "questions": adjudicated_questions(document["documentId"], adj[document["documentId"]]["runs"])
        if document["documentId"] in adj else copy.deepcopy(document["questions"]),
      }
      for document in r1_index["documents"]
    ],
    "indexingAnomalies": [
      anomaly for anomaly in r1_index.get("indexingAnomalies", [])
      if anomaly.get("documentId") not in adj
    ],
  }
  return r2


def build_r2_manifest(r1_manifest: dict[str, Any], r2_index: dict[str, Any],
                      seed: int = SELECTION_SEED, count: int = QUESTIONS_PER_DOCUMENT) -> dict[str, Any]:
  index_by_id = {document["documentId"]: document for document in r2_index["documents"]}
  manifest = copy.deepcopy(r1_manifest)
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


def build_gt_scaffold(manifest: dict[str, Any], manifest_file_sha256: str | None = None,
                      index_file_sha256: str | None = None) -> dict[str, Any]:
  questions = []
  for document in manifest["documents"]:
    for question in document["selectedQuestions"]:
      questions.append(_gt_defaults(document["documentId"], question))
  fingerprints = {document["documentId"]: document["contentFingerprint"] for document in manifest["documents"]}
  return {
    "_workingCopy": "Blind structural GT scaffold (R2). Do not run Auditor until annotation is complete.",
    "protocolVersion": manifest["protocolVersion"],
    "manifestSha256": schema.sha256_json(manifest),
    "sourceManifestFileSha256": manifest_file_sha256,
    "questionIndexFileSha256": index_file_sha256,
    "documentFingerprints": fingerprints,
    "questions": questions,
  }


def migrate_ground_truth(old_gt: dict[str, Any], new_gt: dict[str, Any],
                         adjudicated_documents: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
  old_by_document: dict[str, list[dict[str, Any]]] = {}
  for entry in old_gt["questions"]:
    old_by_document.setdefault(entry["documentId"], []).append(entry)

  migrated_annotated: list[str] = []
  migrated_unknown: list[str] = []
  newly_selected: list[str] = []
  ambiguous: list[str] = []
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
                    if number_from_question_id(candidate["questionId"]) == entry_number]
      if len(candidates) > 1:
        ambiguous.append(entry["questionId"])
        continue
    if candidates:
      source = candidates[0]
      matched_old_ids.add(source["questionId"])
      if source.get("responseMode") != "unknown":
        for field in ANNOTATION_FIELDS:
          if field in source:
            entry[field] = source[field]
        migrated_annotated.append(entry["questionId"])
      else:
        migrated_unknown.append(entry["questionId"])
    else:
      newly_selected.append(entry["questionId"])

  old_selected_ids = {entry["questionId"] for entry in old_gt["questions"]}
  new_selected_ids = {entry["questionId"] for entry in new_gt["questions"]}
  dropped = sorted(old_selected_ids - new_selected_ids)
  old_annotated = {entry["questionId"] for entry in old_gt["questions"] if entry["responseMode"] != "unknown"}
  dropped_annotated = sorted(question_id for question_id in dropped if question_id in old_annotated)
  dropped_unknown = sorted(question_id for question_id in dropped if question_id not in old_annotated)

  source_annotated = sum(1 for entry in old_gt["questions"] if entry["responseMode"] != "unknown")
  target_annotated = sum(1 for entry in new_gt["questions"] if entry["responseMode"] != "unknown")

  report = {
    "sourceAnnotated": source_annotated,
    "sourceUnknown": len(old_gt["questions"]) - source_annotated,
    "migratedAnnotated": sorted(migrated_annotated),
    "migratedAnnotatedCount": len(migrated_annotated),
    "migratedUnknownIfStillSelected": sorted(migrated_unknown),
    "migratedUnknownIfStillSelectedCount": len(migrated_unknown),
    "droppedAnnotated": dropped_annotated,
    "droppedAnnotatedCount": len(dropped_annotated),
    "droppedUnknown": dropped_unknown,
    "droppedUnknownCount": len(dropped_unknown),
    "newlySelected": sorted(newly_selected),
    "newlySelectedCount": len(newly_selected),
    "ambiguous": sorted(ambiguous),
    "ambiguousCount": len(ambiguous),
    "missing": [],
    "missingCount": 0,
    "targetAnnotated": target_annotated,
    "targetUnknown": len(new_gt["questions"]) - target_annotated,
    "total": len(new_gt["questions"]),
  }
  return new_gt, report


def emit_adjudication() -> dict[str, Any]:
  adjudication = build_adjudication(load_json(R2_MAIN_REVIEW), load_json(R2_VEST_REVIEW), load_json(MANIFEST_B2_R1))
  write_json(ADJUDICATION, adjudication)
  return adjudication


def materialize() -> dict[str, Any]:
  r1_index = load_json(QUESTION_INDEX_R1)
  r1_manifest = load_json(MANIFEST_B2_R1)
  r1_gt = load_json(GT_R1_SCAFFOLD)
  adjudication = load_json(ADJUDICATION)

  identity = selector.code_identity()
  adjudicated_documents = set(adjudication_by_id(adjudication))

  r2_index = build_r2_index(r1_index, adjudication)
  schema.validate_question_index(r2_index)

  r2_manifest = build_r2_manifest(r1_manifest, r2_index)
  schema.validate_manifest(r2_manifest)

  r2_manifest_again = build_r2_manifest(r1_manifest, build_r2_index(r1_index, adjudication))
  deterministic = json.dumps(r2_manifest, ensure_ascii=False, sort_keys=True) == \
    json.dumps(r2_manifest_again, ensure_ascii=False, sort_keys=True)
  if not deterministic:
    raise schema.HoldoutValidationError("R2 manifest is not deterministic")

  write_json(QUESTION_INDEX_R2, r2_index)
  write_json(MANIFEST_B2_R2, r2_manifest)
  schema.validate_bindings(r2_manifest, question_index=r2_index)

  scaffold = build_gt_scaffold(
    r2_manifest,
    manifest_file_sha256=schema.sha256_file(MANIFEST_B2_R2),
    index_file_sha256=schema.sha256_file(QUESTION_INDEX_R2),
  )
  scaffold, migration = migrate_ground_truth(r1_gt, scaffold, adjudicated_documents)

  if migration["ambiguousCount"] != 0:
    raise schema.HoldoutValidationError(f"GT migration ambiguous: {migration['ambiguous']}")
  if migration["missingCount"] != 0:
    raise schema.HoldoutValidationError(f"GT migration missing: {migration['missing']}")

  schema.validate_ground_truth(scaffold)
  schema.validate_bindings(r2_manifest, question_index=r2_index, ground_truth=scaffold)
  write_json(GT_R2_SCAFFOLD, scaffold)

  materializer_sha = schema.sha256_file(Path(__file__).resolve())
  adjudication_sha = schema.sha256_file(ADJUDICATION)

  index_provenance = {
    "artifactType": "holdout-v2-r2-question-index-provenance",
    "protocolVersion": r2_index["protocolVersion"],
    "parentQuestionIndex": "audit/holdout/question-index-v2-r1.json",
    "parentQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_R1),
    "adjudication": "audit/holdout/question-index-v2-r2.adjudication.json",
    "adjudicationFileSha256": adjudication_sha,
    "r2MainReview": "outputs/audit/holdout/r2-neutral-review.json",
    "r2MainReviewFileSha256": schema.sha256_file(R2_MAIN_REVIEW),
    "r2VestReview": "outputs/audit/holdout/r2-vest-neutral-review.json",
    "r2VestReviewFileSha256": schema.sha256_file(R2_VEST_REVIEW),
    "materializer": "scripts/audit_holdout_v2_r2.py",
    "materializerSha256": materializer_sha,
    "materializationGitCommit": identity["gitCommit"],
    "materializerCodeState": identity["selectionCodeState"],
    "adjudicatedDocuments": sorted(adjudicated_documents),
    "preservedDocuments": len(r2_index["documents"]) - len(adjudicated_documents),
    "idPolicy": ID_POLICY,
    "pageEndPolicy": PAGE_END_POLICY,
    "responseStructureObserved": False,
    "outputQuestionIndex": "audit/holdout/question-index-v2-r2.json",
    "outputQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_R2),
    "deterministic": True,
  }
  write_json(QUESTION_INDEX_R2_PROVENANCE, index_provenance)

  migration_summary = {
    "sourceAnnotated": migration["sourceAnnotated"],
    "sourceUnknown": migration["sourceUnknown"],
    "migratedAnnotatedCount": migration["migratedAnnotatedCount"],
    "migratedUnknownIfStillSelectedCount": migration["migratedUnknownIfStillSelectedCount"],
    "droppedAnnotatedCount": migration["droppedAnnotatedCount"],
    "droppedUnknownCount": migration["droppedUnknownCount"],
    "newlySelectedCount": migration["newlySelectedCount"],
    "ambiguousCount": migration["ambiguousCount"],
    "missingCount": migration["missingCount"],
    "targetAnnotated": migration["targetAnnotated"],
    "targetUnknown": migration["targetUnknown"],
  }

  manifest_provenance = {
    "artifactType": "holdout-v2-r2-question-selection-provenance",
    "protocolVersion": r2_manifest["protocolVersion"],
    "parentQuestionIndex": "audit/holdout/question-index-v2-r2.json",
    "parentQuestionIndexFileSha256": schema.sha256_file(QUESTION_INDEX_R2),
    "parentManifestB2": "audit/holdout/manifest-v2-b2-r1.json",
    "parentManifestB2FileSha256": schema.sha256_file(MANIFEST_B2_R1),
    "adjudication": "audit/holdout/question-index-v2-r2.adjudication.json",
    "adjudicationFileSha256": adjudication_sha,
    "materializer": "scripts/audit_holdout_v2_r2.py",
    "materializerSha256": materializer_sha,
    "materializationGitCommit": identity["gitCommit"],
    "materializerCodeState": identity["selectionCodeState"],
    "selectionSeed": r2_manifest["selectionSeed"],
    "questionsPerDocument": int(r2_manifest["selectionConfig"]["questionsPerDocument"]),
    "documents": len(r2_manifest["documents"]),
    "selectedQuestionsTotal": sum(len(document["selectedQuestions"]) for document in r2_manifest["documents"]),
    "selectionMethod": "one random question per document-order tertile (frozen select_questions)",
    "questionSelectionHash": question_selection_hash(r2_manifest),
    "selectionCodeSha256": schema.sha256_file(SELECTOR_PATH),
    "outputManifest": "audit/holdout/manifest-v2-b2-r2.json",
    "outputManifestFileSha256": schema.sha256_file(MANIFEST_B2_R2),
    "idPolicy": ID_POLICY,
    "pageEndPolicy": PAGE_END_POLICY,
    "determinismCheck": "independent recomputation produced an identical manifest",
    "deterministic": deterministic,
    "migrationSummary": migration_summary,
  }
  write_json(MANIFEST_B2_R2_PROVENANCE, manifest_provenance)

  report = {
    "artifactType": "holdout-v2-r2-ground-truth-migration-report",
    "protocolVersion": r2_manifest["protocolVersion"],
    "manifest": "audit/holdout/manifest-v2-b2-r2.json",
    "manifestFileSha256": schema.sha256_file(MANIFEST_B2_R2),
    "parentGroundTruth": "outputs/audit/holdout/ground-truth-v2-r1-scaffold.json",
    "parentGroundTruthFileSha256": schema.sha256_file(GT_R1_SCAFFOLD),
    "outputGroundTruth": "outputs/audit/holdout/ground-truth-v2-r2-scaffold.json",
    "outputGroundTruthFileSha256": schema.sha256_file(GT_R2_SCAFFOLD),
    **migration,
  }
  write_json(GT_R2_REPORT, report)

  return {
    "index": r2_index,
    "manifest": r2_manifest,
    "scaffold": scaffold,
    "migration": report,
    "indexProvenance": index_provenance,
    "manifestProvenance": manifest_provenance,
  }


def main() -> None:
  parser = argparse.ArgumentParser(description="Materialize the neutral Holdout V2 R2 revision.")
  parser.add_argument("--emit-adjudication", action="store_true")
  parser.add_argument("--check", action="store_true")
  args = parser.parse_args()
  if args.emit_adjudication:
    adjudication = emit_adjudication()
    print(json.dumps({"status": "ok", "adjudication": str(ADJUDICATION),
                      "documents": len(adjudication["documents"])}, ensure_ascii=False))
    return
  if args.check:
    adjudication = load_json(ADJUDICATION)
    r2_index = build_r2_index(load_json(QUESTION_INDEX_R1), adjudication)
    r2_manifest = build_r2_manifest(load_json(MANIFEST_B2_R1), r2_index)
    print(json.dumps({"status": "ok", "check": True, "documents": len(r2_manifest["documents"]),
                      "selectedQuestions": sum(len(d["selectedQuestions"]) for d in r2_manifest["documents"])}))
    return
  result = materialize()
  print(json.dumps({
    "status": "ok",
    "documents": len(result["manifest"]["documents"]),
    "selectedQuestions": sum(len(d["selectedQuestions"]) for d in result["manifest"]["documents"]),
    "questionSelectionHash": result["manifestProvenance"]["questionSelectionHash"],
    "migration": {
      "migratedAnnotated": result["migration"]["migratedAnnotatedCount"],
      "droppedAnnotated": result["migration"]["droppedAnnotatedCount"],
      "targetAnnotated": result["migration"]["targetAnnotated"],
      "targetUnknown": result["migration"]["targetUnknown"],
      "ambiguous": result["migration"]["ambiguousCount"],
      "missing": result["migration"]["missingCount"],
    },
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
