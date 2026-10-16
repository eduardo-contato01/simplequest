"""Isolated, lossless V5 Batch03 materialization and verification.

Only consumes approved human records and frozen metadata. No Auditor, PDF parser,
OCR, classification, selection or metrics imports. --verify is read-only and uses
the embedded mandatory evidence even when the operational journal is absent.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile

HEAD = "ceec02a038a7f4c0476eb1fa78f22fb59b8c719e"
SUMMARY_SHA = "2d573bc5c5d8a7fb516255921452365a3ac2ddf33ad020ed5431093e63e65806"
AUTH_SHA = "201a0ccdeef70d89ae2026019d978268e0db95d0bd60b329355a48d3cf3eb32e"
CHECKPOINT_SHA = "10e4cfb75622691a2f74e27881d0eb7c0fec4089ce7c1ad2a4bd68fc63290dea"
PROTECTION_SHA = "ed197cb9059310768a64cbb71e46a3184f0f4d7d616dfb3381662a4c29ec751b"
WORK = "outputs/audit/holdout/v5-ground-truth-batch-03-adjudication"
BASE = "audit/holdout/ground-truth-v5-batch-03"
GT, PROV, EVIDENCE = BASE + ".json", BASE + ".provenance.json", BASE + ".human-decisions.json"
RESPONSE_FIELDS = ("responseMode", "optionCount", "optionLabels", "subitems", "responseControls", "layout", "markerStyle", "contentKind", "notes")
ORIGIN_FIELDS = ("annotationOrigin", "independentHumanAdjudicationClaimed", "externalIndependenceCertification", "aiClassificationAssistanceDeclared")
ENUMS = {
    "responseMode": {"single_choice", "true_false", "numeric_response", "numeric", "discursive", "other", "unknown"},
    "layout": {"vertical", "two_column", "grid", "parent_child", "internal_enumeration", "mixed", "none", "unknown"},
    "markerStyle": {"textual", "parenthesized", "circled_outline", "circled_filled", "symbolic_control", "mixed", "none", "unknown"},
    "contentKind": {"text", "math", "media", "mixed", "none", "unknown"},
}
STATES = {"PhaseBComplete": True, "questionSelectionFrozen": True, "groundTruthStarted": True,
          "groundTruthBatch01Created": True, "groundTruthBatch02Created": True, "groundTruthBatch03Created": True,
          "groundTruthQuestionsAdjudicated": 27, "groundTruthQuestionsRemaining": 117,
          "groundTruthHumanAdjudicationComplete": False, "groundTruthFinalCreated": False,
          "auditorExecuted": False, "metricsSeen": False, "merge": False}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def atomic_new(target, data):
    if target.exists():
        require(target.read_bytes() == data, f"existing artifact mismatch: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=target.name + ".", suffix=".pending", dir=target.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        require(Path(temporary).read_bytes() == data, "atomic readback")
        require(not target.exists(), f"concurrent artifact appeared: {target}")
        os.replace(temporary, target)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def embed(target, root):
    raw = target.read_bytes()
    return {"path": target.relative_to(root).as_posix(), "sha256": sha(raw), "sizeBytes": len(raw), "rawUtf8": raw.decode("utf-8")}


def unpack(item):
    raw = item["rawUtf8"].encode("utf-8")
    require(len(raw) == item["sizeBytes"] and sha(raw) == item["sha256"], "embedded evidence integrity: " + item["path"])
    return raw


def build_evidence(root):
    work = root / WORK
    cp = strict_json((work / "checkpoint.json").read_bytes())
    pf = strict_json((work / "preflight.json").read_bytes())
    supporting = cp["repositoryChangeAuthorizations"] + cp["collectionWorkflowAuthorizations"] + cp["reconciliationEvidence"]
    prefixes = []
    for reference in pf["documentationRawPrefixes"]:
        raw = (work / reference["rawPrefixEvidence"]).read_bytes()
        require(sha(raw) == reference["rawSha256"], "raw prefix evidence")
        prefixes.append({"path": reference["path"], "sha256": sha(raw), "sizeBytes": len(raw), "rawBase64": base64.b64encode(raw).decode("ascii")})
    return {"artifactType": "mandatory_human_decision_evidence", "protocolVersion": "holdout-v5",
            "annotationVersion": 1, "batchId": "holdout-v5-batch-03", "sourceHead": HEAD,
            "approvedSummary": embed(work / cp["finalSummaryForApproval"]["path"], root),
            "finalHumanAuthorization": embed(work / "batch-final-authorization.json", root),
            "sourcePreflight": embed(work / "preflight.json", root), "sourceCheckpoint": embed(work / "checkpoint.json", root),
            "prepublicationProtection": embed(work / "prepublication-protection.json", root),
            "rawDecisionEvents": [embed(work / r["path"], root) for r in cp["records"]],
            "workflowAndRepositoryAuthorizationsAndReconciliations": [embed(work / r["path"], root) for r in supporting],
            "documentationRawPrefixEvidence": prefixes,
            "sourceSnapshotsRemainUnchanged": True,
            "rawUtf8Convention": "UTF8 round-trip restores original event bytes; pending snapshots remain historical, not current claims",
            "independentHumanReviewClaims": 9, "aiAssistedHumanVerifiedQuestions": 0,
            "externalIndependenceCertified": False, "independenceClaimScope": "reviewer declarations only; not external certification",
            "auditorExecuted": False, "metricsSeen": False}


def validate_evidence(e):
    require(e["protocolVersion"] == "holdout-v5" and e["batchId"] == "holdout-v5-batch-03" and e["sourceHead"] == HEAD, "evidence scope")
    for key, expected in (("approvedSummary", SUMMARY_SHA), ("finalHumanAuthorization", AUTH_SHA),
                          ("sourceCheckpoint", CHECKPOINT_SHA), ("prepublicationProtection", PROTECTION_SHA)):
        require(e[key]["sha256"] == expected and sha(unpack(e[key])) == expected, "frozen authority: " + key)
    summary, auth, cp, pf, protection = [strict_json(unpack(e[key])) for key in
        ("approvedSummary", "finalHumanAuthorization", "sourceCheckpoint", "sourcePreflight", "prepublicationProtection")]
    require(e["sourcePreflight"]["sha256"] == cp["preflight"]["sha256"] == summary["preflight"]["sha256"], "preflight binding")
    require(auth["approvedSummarySha256"] == SUMMARY_SHA == protection["approvedSummarySha256"], "approved exact summary")
    require(protection["finalAuthorizationSha256"] == AUTH_SHA and protection["authorizedCheckpointSha256"] == CHECKPOINT_SHA, "protection authority")
    for key in ("nineQuestionRecordsConfirmed", "finalPublicationAuthorized", "preserveAllClassificationsAndNotes",
                "preserveExplicitCorrectionsAndHistory", "nineDecisionsDeclaredWithoutAi", "preservePreviousBatchesAndFreezes",
                "preexistingUserChangesMayRemainUnstaged", "allOtherMandatoryGatesRequired", "stopAfterPublication"):
        require(auth.get(key) is True, "explicit authorization: " + key)
    require(auth["externalIndependenceCertificationAuthorized"] is False, "no external certification authority")
    require(cp["humanDecisionsReceived"] == cp["humanDecisionsConfirmed"] == 9 and not cp["pendingQuestionIds"] and cp["nextQuestionId"] is None, "nine completed decisions")
    require(cp["materializationAuthorized"] is True and cp["finalSummaryApproved"] is True, "final approval required")
    require(cp["finalHumanAuthorization"]["sha256"] == AUTH_SHA and cp["finalSummaryForApproval"]["sha256"] == SUMMARY_SHA, "checkpoint approvals")
    require(len(e["rawDecisionEvents"]) == len(cp["records"]) == 14, "fourteen original events")
    confirmed, events = {}, {}
    for item, ref in zip(e["rawDecisionEvents"], cp["records"]):
        require(Path(item["path"]).name == ref["path"] and item["sha256"] == ref["sha256"], "immutable event binding")
        event = strict_json(unpack(item))
        require(event["identity"]["questionId"] == ref["questionId"], "event identity")
        require(event["individualConfirmation"]["confirmed"] == ref["confirmed"], "event confirmation binding")
        events[ref["path"]] = event
        if ref["confirmed"]:
            require(ref["questionId"] not in confirmed, "duplicate confirmed decision")
            confirmed[ref["questionId"]] = (event, ref)
    require(len(confirmed) == len(summary["decisions"]) == 9, "summary coverage")
    require(list(confirmed) == cp["confirmedQuestions"] == [d["identity"]["questionId"] for d in summary["decisions"]], "confirmed order")
    for i, decision in enumerate(summary["decisions"], 1):
        event, ref = confirmed[decision["identity"]["questionId"]]
        require(decision["position"] == i and decision["sourceRecord"] == ref, "summary source event")
        for key in ("identity", "fields", "printedQuestionNumber", "classificationOrigin", "individualConfirmation"):
            require(decision[key] == event[key], "human decision difference: " + key)
        require(decision["confirmedObservationalDescriptions"] == event.get("confirmedObservationalDescriptions"), "confirmed description")
        require(not event["unresolvedIssues"] and event["individualConfirmation"]["physicalPagesExamined"] == event["identity"]["pages"], "human inspection/closure")
    support_refs = cp["repositoryChangeAuthorizations"] + cp["collectionWorkflowAuthorizations"] + cp["reconciliationEvidence"]
    require(len(support_refs) == len(e["workflowAndRepositoryAuthorizationsAndReconciliations"]), "support coverage")
    for item, ref in zip(e["workflowAndRepositoryAuthorizationsAndReconciliations"], support_refs):
        require(Path(item["path"]).name == ref["path"] and sha(unpack(item)) == ref["sha256"], "support authority")
    for item, ref in zip(e["documentationRawPrefixEvidence"], pf["documentationRawPrefixes"]):
        raw = base64.b64decode(item["rawBase64"], validate=True)
        require(item["path"] == ref["path"] and len(raw) == item["sizeBytes"] == ref["rawBytes"] and sha(raw) == item["sha256"] == ref["rawSha256"], "recoverable raw prefix")
    require(len(e["documentationRawPrefixEvidence"]) == 4, "four protected prefixes")
    # Explicit corrections remain additional events, never edits to their originals.
    for original_name, corrected_name, scope in (("record-007.json", "record-008.json", "labels"), ("record-011.json", "record-012.json", "description")):
        original, corrected = events[original_name], events[corrected_name]
        ref = next(r for r in cp["records"] if r["path"] == original_name)
        require(corrected["sourceRecord"] == {"path": original_name, "sha256": ref["sha256"]}, "correction source binding")
        expected = copy.deepcopy(original["fields"])
        if scope == "labels":
            require(expected["optionLabels"] == '["a", "b", "c", "d". "e"]', "original punctuation retained")
            expected["optionLabels"] = ["a", "b", "c", "d", "e"]
        else:
            require("A–E" in corrected["confirmedObservationalDescriptions"]["markerStyle"], "human uppercase clarification")
        require(corrected["fields"] == expected, "correction outside authorized scope")
    return summary, auth, pf, protection


def check_preservation(root, pf, protection):
    for ref in pf["verifiedFiles"] + protection["additionalReadOnlyFiles"]:
        require(sha((root / ref["path"]).read_bytes()) == ref["expectedSha256"], "historical hash: " + ref["path"])
    prefix_by_path = {r["path"]: r for r in pf["documentationRawPrefixes"]}
    for ref in protection["trackedFilePreservation"]:
        raw = (root / ref["path"]).read_bytes()
        if ref["path"] in prefix_by_path:
            prefix = prefix_by_path[ref["path"]]
            require(sha(raw[:prefix["rawBytes"]]) == prefix["rawSha256"], "historical documentation prefix: " + ref["path"])
        else:
            require(sha(raw) == ref["prepublicationRawSha256"], "episode physical preservation: " + ref["path"])
    for ref in protection["userChanges"]:
        require(sha((root / ref["path"]).read_bytes()) == ref["expectedRawSha256"], "preexisting user bytes: " + ref["path"])


def approved_questions(summary):
    return [{**d["identity"], "printedQuestionNumber": d["printedQuestionNumber"], **d["fields"],
             **{key: d["classificationOrigin"][key] for key in ORIGIN_FIELDS}} for d in summary["decisions"]]


def validate_questions(questions, approved, manifest, index):
    docs = manifest["documents"][6:9]
    selected = [(d, q) for d in docs for q in d["selectedQuestions"]]
    require(len(questions) == len(approved) == len(selected) == 9 and len(docs) == 3, "batch size")
    require([q["questionId"] for q in questions] == [q["questionId"] for _, q in selected], "IDs and order")
    require(len({q["questionId"] for q in questions}) == 9, "unique question IDs")
    for actual, expected, (doc, frozen) in zip(questions, approved, selected):
        require(actual == expected, "human decision difference: " + actual["questionId"])
        require(actual["documentId"] == doc["documentId"] and actual["contentFingerprint"] == doc["contentFingerprint"], "document/fingerprint binding")
        canonical = next(d for d in index["documents"] if d["documentId"] == doc["documentId"])
        require(canonical["contentFingerprint"] == actual["contentFingerprint"], "canonical fingerprint")
        require(frozen == next(q for q in canonical["questions"] if q["questionId"] == frozen["questionId"]), "selected object preservation")
        require(actual["canonicalQuestionNumber"] == frozen["questionNumber"], "canonical number")
        if "printedQuestionNumber" in frozen:
            require(actual["printedQuestionNumber"] == frozen["printedQuestionNumber"], "frozen printed number")
        require(actual["pageStart"] == frozen["pageStart"] and actual["pageEnd"] == frozen["pageEnd"], "boundaries")
        require(actual["pages"] == list(range(frozen["pageStart"], frozen["pageEnd"] + 1)), "physical pages")
        require(1 <= actual["pageStart"] <= actual["pageEnd"] <= doc["effectivePhysicalPageCount"], "physical range")
        for key, allowed in ENUMS.items():
            require(actual[key] in allowed, "invalid enum: " + key)
        count, labels = actual["optionCount"], actual["optionLabels"]
        require(count is None or (type(count) is int and count >= 0), "optionCount type")
        require(labels is None or (isinstance(labels, list) and all(isinstance(x, str) for x in labels)), "optionLabels type")
        require(count is None or labels is None or count == len(labels), "count/labels inconsistency")
        require(isinstance(actual["notes"], str), "notes type")
        for key in ("subitems", "responseControls"):
            require(actual[key] is None or isinstance(actual[key], list), key + " type")
            for item in actual[key] or []:
                require(set(item) == {"label", "role", "pages", "notes"}, "structured element keys")
                require(all(isinstance(item[k], str) for k in ("label", "role", "notes")), "structured strings")
                require(item["pages"] == actual["pages"], "structured pages")
        require(actual["independentHumanAdjudicationClaimed"] is True and actual["aiClassificationAssistanceDeclared"] is False and actual["externalIndependenceCertification"] is False, "reviewer declaration scope")
    return {"batch03Documents": 3, "batch03Questions": 9, "batch03UniqueQuestionIds": 9,
            "unknownQuestionIds": 0, "crossDocumentBindings": 0, "fingerprintMismatches": 0,
            "invalidPageRanges": 0, "selectionModified": False, "humanDecisionsReceived": 9,
            "humanDecisionsConfirmed": 9, "humanDecisionDifferences": 0, "unconfirmedHumanDecisions": 0,
            "reviewerDeclaredIndependentQuestions": 9, "aiAssistedHumanVerifiedQuestions": 0,
            "externalIndependenceCertified": False,
            "unknownClassificationQuestions": sum(any(q[k] == "unknown" for k in ENUMS) or any(q[k] is None for k in ("optionCount", "optionLabels", "subitems", "responseControls")) for q in questions),
            "auditorExecuted": False, "metricsSeen": False}


def run(root, materialize=False):
    evidence = build_evidence(root) if materialize else strict_json((root / EVIDENCE).read_bytes())
    summary, auth, pf, protection = validate_evidence(evidence)
    check_preservation(root, pf, protection)
    manifest = strict_json((root / "audit/holdout/manifest-v5-questions-frozen.json").read_bytes())
    index = strict_json((root / "audit/holdout/question-index-v5-final.json").read_bytes())
    parent = strict_json((root / "audit/holdout/v5-gt-review-batches-manifest.json").read_bytes())
    ids_raw = json.dumps([[d["documentId"], [q["questionId"] for q in d["selectedQuestions"]]] for d in manifest["documents"]], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    require(sha(ids_raw) == pf["orderedSelectedIdsSha256"] == "11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a", "144-ID identity")
    questions = approved_questions(summary)
    gates = validate_questions(questions, approved_questions(summary), manifest, index)
    evidence_bytes = encoded(evidence)
    docs = manifest["documents"][6:9]
    frozen_hashes = {r["path"]: r["expectedSha256"] for r in pf["verifiedFiles"] if r["path"] in (
        "audit/holdout/manifest-v5-questions-frozen.json", "audit/holdout/manifest-v5-questions-frozen.provenance.json",
        "audit/holdout/question-index-v5-final.json", "audit/holdout/v5-gt-review-batches-manifest.json")}
    caveats = [{"questionId": "v5-doc-0c51e49589f148bc:q7", "basis": "Literal human note preserves required preceding passage as context while the question starts after it; frozen boundaries unchanged."}]
    bindings = {"doc08Q2": "punctuation correction explicitly authorized, original event preserved",
                "doc09Q4": "uppercase A-E confirmed; only descriptive wording corrected, labels and notes unchanged",
                "doc09Q7": "preceding passage dependency preserved literally, without changing canonical question boundaries"}
    gt = {"artifactType": "reviewer_approved_ground_truth_batch", "protocolVersion": "holdout-v5", "annotationVersion": 1,
          "freezeVersion": 1, "batchId": "holdout-v5-batch-03", "sourceHead": HEAD, "documentsCount": 3, "questionsCount": 9,
          "r1Positions": [7, 8, 9], "documentFingerprints": {d["documentId"]: d["contentFingerprint"] for d in docs},
          "frozenInputFileSha256s": frozen_hashes, "approvedSummarySha256": SUMMARY_SHA,
          "humanDecisionEvidence": {"path": EVIDENCE, "sha256": sha(evidence_bytes)},
          "humanAdjudicated": True, "humanAdjudicatedMeaning": "nine records individually inspected and approved by the human reviewer, including explicit final approval; collection workflow exception is recorded",
          "independentHumanReviewClaims": 9, "aiAssistedHumanVerifiedQuestions": 0, "externalIndependenceCertified": False,
          "independenceClaimScope": "nine reviewer declarations without AI classification assistance; not external certification",
          "contextualCaveats": caveats, "reviewerConditionBindings": bindings,
          "freezeStatusAtCreation": "ready_for_introducing_commit_and_push",
          "formalFreezeRule": "introducing commit, push, matching remote HEAD, empty stage and no episode-introduced changes; three byte-preserved preexisting user changes may remain under explicit final authorization",
          "expectedPostPublicationStates": STATES, "futureRunnerCompatibilityResolved": False,
          "auditorExecuted": False, "metricsSeen": False, "ocrExecuted": False, "merge": False,
          "documents": [{"documentId": d["documentId"], "contentFingerprint": d["contentFingerprint"], "effectivePhysicalPageCount": d["effectivePhysicalPageCount"], "selectedQuestionIds": [q["questionId"] for q in d["selectedQuestions"]]} for d in docs],
          "questions": questions}
    gt_bytes = encoded(gt)
    provenance = {"artifactType": "ground_truth_batch_provenance", "protocolVersion": "holdout-v5", "annotationVersion": 1,
                  "batchId": "holdout-v5-batch-03", "sourceHead": HEAD,
                  "groundTruth": {"path": GT, "sha256": sha(gt_bytes), "sizeBytes": len(gt_bytes)},
                  "humanDecisionEvidence": {"path": EVIDENCE, "sha256": sha(evidence_bytes), "sizeBytes": len(evidence_bytes)},
                  "approvedSummarySha256": SUMMARY_SHA, "finalAuthorizationSha256": AUTH_SHA,
                  "completedHumanCheckpointSha256": CHECKPOINT_SHA, "prepublicationProtectionSha256": PROTECTION_SHA,
                  "frozenInputFileSha256s": frozen_hashes, "orderedSelectedIdsSha256": sha(ids_raw),
                  "batchPackageFiles": parent["batches"][2]["files"],
                  "historicalPreservationReferences": pf["verifiedFiles"] + protection["additionalReadOnlyFiles"],
                  "preservationCoverageMeaning": protection["coverageMeaning"],
                  "trackedPhysicalEpisodeGuards": len(protection["trackedFilePreservation"]),
                  "preexistingUserChangesExcludedFromCommit": protection["userChanges"],
                  "materializerAndValidatorSha256": sha(Path(__file__).read_bytes()),
                  "syntheticSelftestSha256": sha(Path(__file__).with_name("v5_ground_truth_batch03_selftest.py").read_bytes()),
                  "gates": gates, "deterministicSerialization": "UTF8/noBOM/LF/indent2/final newline",
                  "contextualCaveats": caveats, "reviewerConditionBindings": bindings,
                  "priorBatches01And02Preserved": True, "priorBatch01ExceptionPreserved": True,
                  "accumulatedReviewClaimsAfterPublication": {"declaredWithoutAi": 26, "aiAssistedHumanVerified": 1, "externalIndependenceCertified": False},
                  "methodologyCaveats": parent["methodologyCaveats"], "futureRunnerCompatibilityResolved": False,
                  "freezeStatusAtCreation": "ready_for_introducing_commit_and_push", "expectedPostPublicationStates": STATES,
                  "nextStep": "STOP; no Batch04/global GT/OCR/Auditor/metrics/merge"}
    outputs = ((EVIDENCE, evidence_bytes), (GT, gt_bytes), (PROV, encoded(provenance)))
    for name, raw in outputs:
        require(not (root / name).exists() or (root / name).read_bytes() == raw, "existing artifact mismatch: " + name)
    for name, raw in outputs:
        if materialize:
            atomic_new(root / name, raw)
        else:
            require((root / name).read_bytes() == raw, "published deterministic artifact: " + name)
    receipt = {"groundTruthSha256": sha(gt_bytes), "provenanceSha256": sha(encoded(provenance)), "humanEvidenceSha256": sha(evidence_bytes), "gates": gates}
    if materialize:
        atomic_new(root / WORK / "materialization-validation.json", encoded(receipt))
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--materialize", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[2], args.materialize)
