"""Isolated deterministic Batch02 materialization after explicit human approval.

No PDF parsing, classification, Auditor imports, legacy-schema changes or selection.
--verify can use the versioned embedded evidence without the operational journal.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile

INITIAL_HEAD = "093ab08cf83237c4ec0fbc9b33be952449eaa318"
SUMMARY_SHA = "ffc8393f3097375d576b9315c465d16aaf9cfb1eb6db890691ff42ac9ca760f9"
AUTH_SHA = "d7f58198dbefee4b030ce94e4341e52816c05a9e6c424b2f3492f8fc2b755afc"
CHECKPOINT_SHA = "6b281206a8281e26ce1486d0d508f70cedd4a2f535610b51f0a6707c03a3ce53"
PROTECTION_SHA = "0cd84781a208858d8c35c2df7471dba5afd699a43106fc156aa9dcd116ea34c8"
WORK = "outputs/audit/holdout/v5-ground-truth-batch-02-adjudication"
EVIDENCE = "audit/holdout/ground-truth-v5-batch-02.human-decisions.json"
GT = "audit/holdout/ground-truth-v5-batch-02.json"
PROV = "audit/holdout/ground-truth-v5-batch-02.provenance.json"
RESPONSE_FIELDS = ("responseMode", "optionCount", "optionLabels", "subitems", "responseControls", "layout", "markerStyle", "contentKind", "notes")
QUESTION_FIELDS = ("documentId", "contentFingerprint", "questionId", "canonicalQuestionNumber", "printedQuestionNumber", "pageStart", "pageEnd", "pages", *RESPONSE_FIELDS, "annotationOrigin", "independentHumanAdjudicationClaimed", "externalIndependenceCertification", "aiClassificationAssistanceDeclared")
ENUMS = {
    "responseMode": {"single_choice", "true_false", "numeric_response", "numeric", "discursive", "other", "unknown"},
    "layout": {"vertical", "two_column", "grid", "parent_child", "internal_enumeration", "mixed", "none", "unknown"},
    "markerStyle": {"textual", "parenthesized", "circled_outline", "circled_filled", "symbolic_control", "mixed", "none", "unknown"},
    "contentKind": {"text", "math", "media", "mixed", "none", "unknown"},
}
STATES = {"PhaseBComplete": True, "questionSelectionFrozen": True, "groundTruthStarted": True,
          "groundTruthBatch01Created": True, "groundTruthBatch02Created": True,
          "groundTruthQuestionsAdjudicated": 18, "groundTruthQuestionsRemaining": 126,
          "groundTruthHumanAdjudicationComplete": False, "groundTruthFinalCreated": False,
          "auditorExecuted": False, "metricsSeen": False, "merge": False}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
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

def embedded(target, root):
    raw = target.read_bytes()
    return {"path": target.relative_to(root).as_posix(), "sha256": sha(raw), "sizeBytes": len(raw), "rawUtf8": raw.decode("utf-8")}

def unpack(record):
    raw = record["rawUtf8"].encode("utf-8")
    require(len(raw) == record["sizeBytes"] and sha(raw) == record["sha256"], f"embedded evidence integrity: {record['path']}")
    return raw

def build_evidence(root):
    work = root / WORK
    checkpoint = embedded(work / "checkpoint.json", root)
    require(checkpoint["sha256"] == CHECKPOINT_SHA, "completed checkpoint binding")
    cp = strict_json(unpack(checkpoint))
    events = []
    for reference in cp["records"]:
        item = embedded(work / reference["path"], root)
        require(item["sha256"] == reference["sha256"], "immutable human event")
        events.append(item)
    return {"artifactType": "mandatory_human_decision_evidence", "protocolVersion": "holdout-v5",
            "annotationVersion": 1, "batchId": "holdout-v5-batch-02", "sourceHead": INITIAL_HEAD,
            "approvedSummary": embedded(work / "review-summary-pending-confirmation.json", root),
            "finalHumanAuthorization": embedded(work / "batch-final-authorization.json", root),
            "sourcePreflight": embedded(work / "preflight.json", root), "sourceCheckpoint": checkpoint,
            "prepublicationProtection": embedded(work / "prepublication-protection.json", root),
            "rawDecisionEvents": events, "sourceSnapshotsRemainUnchanged": True,
            "rawUtf8Convention": "UTF8 round-trip restores original event/snapshot bytes; pending snapshots remain historical",
            "independentHumanReviewClaims": 9, "aiAssistedHumanVerifiedQuestions": 0,
            "externalIndependenceCertified": False, "independenceClaimScope": "reviewer declarations only; not external certification",
            "auditorExecuted": False, "metricsSeen": False}

def validate_evidence(evidence):
    require(evidence["protocolVersion"] == "holdout-v5" and evidence["batchId"] == "holdout-v5-batch-02", "evidence scope")
    bindings = (("approvedSummary", SUMMARY_SHA), ("finalHumanAuthorization", AUTH_SHA),
                ("sourceCheckpoint", CHECKPOINT_SHA), ("prepublicationProtection", PROTECTION_SHA))
    for name, expected in bindings:
        require(evidence[name]["sha256"] == expected and sha(unpack(evidence[name])) == expected, f"frozen authority: {name}")
    summary = strict_json(unpack(evidence["approvedSummary"]))
    auth = strict_json(unpack(evidence["finalHumanAuthorization"]))
    cp = strict_json(unpack(evidence["sourceCheckpoint"]))
    pf = strict_json(unpack(evidence["sourcePreflight"]))
    protection = strict_json(unpack(evidence["prepublicationProtection"]))
    require(evidence["sourcePreflight"]["sha256"] == cp["preflight"]["sha256"] == summary["sourcePreflightSha256"], "preflight binding")
    require(auth["approvedSummarySha256"] == SUMMARY_SHA, "authorization names exact summary")
    for field in ("nineQuestionRecordsConfirmed", "structuredRepresentationsConfirmed", "finalPublicationAuthorized",
                  "preserveAllClassificationsAndNotes", "preserveDoc05Q5ControlCorrectionHistory",
                  "preserveCanonicalQ28Printed8Distinction", "preserveDoc06Q14AsHypothesis",
                  "nineDecisionsDeclaredWithoutAi", "preserveBatch01IncludingMethodologicalException", "stopAfterPublication"):
        require(auth.get(field) is True, f"explicit authorization: {field}")
    require(auth["externalIndependenceCertificationAuthorized"] is False, "no external certification authority")
    require(cp["humanDecisionsReceived"] == cp["humanDecisionsConfirmed"] == 9 and not cp["pendingQuestionIds"] and cp["nextQuestionId"] is None, "nine completed human decisions")
    require(len(evidence["rawDecisionEvents"]) == len(cp["records"]) == 10, "ten original human events")
    confirmed = {}
    for item, reference in zip(evidence["rawDecisionEvents"], cp["records"]):
        require(Path(item["path"]).name == reference["path"] and item["sha256"] == reference["sha256"], "checkpoint event binding")
        event = strict_json(unpack(item))
        require(event["identity"]["questionId"] == reference["questionId"], "event question binding")
        if event["individualConfirmation"]["confirmed"]:
            require(event["identity"]["questionId"] not in confirmed, "duplicate confirmed human decision")
            confirmed[event["identity"]["questionId"]] = (event, reference)
    require(len(confirmed) == 9, "nine distinct confirmed decisions")
    for q in summary["questions"]:
        event, reference = confirmed[q["questionId"]]
        require(q["humanSourceEvent"] == {"path": reference["path"], "sha256": reference["sha256"]}, "approved question source event")
        require(all(q[key] == value for key, value in event["identity"].items()), "journal identity difference")
        require(all(q[key] == event["fields"][key] for key in RESPONSE_FIELDS), "journal human decision difference")
        require(q["printedQuestionNumber"] == event["printedQuestionNumber"], "human observed number")
        origin = event["classificationOrigin"]
        require(all(q[key] == origin[key] for key in ("annotationOrigin", "independentHumanAdjudicationClaimed", "externalIndependenceCertification", "aiClassificationAssistanceDeclared")), "origin difference")
        require(q["corrections"] == event["corrections"], "correction history difference")
        require(event["individualConfirmation"]["physicalPagesExamined"] == q["pages"], "source inspected pages")
        require(not event.get("unresolvedIssues", []), "unresolved question decision")
    require(summary["humanDecisionsReceived"] == summary["humanDecisionsConfirmed"] == 9, "summary human coverage")
    require(protection["approvedSummarySha256"] == SUMMARY_SHA and protection["finalAuthorizationSha256"] == AUTH_SHA, "protection binding")
    # Preserve the actual correction, never replace its original evidence.
    original = strict_json(unpack(evidence["rawDecisionEvents"][3]))
    corrected = strict_json(unpack(evidence["rawDecisionEvents"][4]))
    require(original["individualConfirmation"]["confirmed"] is False and "cinco" in original["fields"]["responseControls"], "original five-control statement retained")
    require(corrected["sourceRecord"] == {"path": cp["records"][3]["path"], "sha256": cp["records"][3]["sha256"]}, "correction linked to original bytes")
    require(corrected["corrections"][0]["confirmedCount"] == len(corrected["fields"]["responseControls"]) == 4, "human correction to four controls")
    return summary, auth, pf, protection

def check_frozen(root, pf, protection):
    for reference in pf["verifiedFiles"] + protection["additionalReadOnlyFiles"]:
        require(sha((root / reference["path"]).read_bytes()) == reference["expectedSha256"], f"protected file: {reference['path']}")
    return strict_json((root / "audit/holdout/manifest-v5-questions-frozen.json").read_bytes()), strict_json((root / "audit/holdout/question-index-v5-final.json").read_bytes())

def make_gt(summary, manifest, pf, evidence_sha):
    documents = [{"documentId": d["documentId"], "contentFingerprint": d["contentFingerprint"],
                  "effectivePhysicalPageCount": d["effectivePhysicalPageCount"],
                  "selectedQuestionIds": [q["questionId"] for q in d["selectedQuestions"]]}
                 for d in manifest["documents"][3:6]]
    return {"artifactType": "reviewer_approved_ground_truth_batch", "protocolVersion": "holdout-v5",
            "annotationVersion": 1, "freezeVersion": 1, "batchId": "holdout-v5-batch-02", "sourceHead": INITIAL_HEAD,
            "documentsCount": 3, "questionsCount": 9, "r1Positions": [4, 5, 6],
            "documentFingerprints": {d["documentId"]: d["contentFingerprint"] for d in documents},
            "frozenInputFileSha256s": {r["path"]: r["expectedSha256"] for r in pf["verifiedFiles"][:3]},
            "approvedSummarySha256": SUMMARY_SHA, "humanDecisionEvidence": {"path": EVIDENCE, "sha256": evidence_sha},
            "humanAdjudicated": True, "humanAdjudicatedMeaning": "nine records individually reviewed and explicitly approved in the final summary by the human reviewer",
            "independentHumanReviewClaims": summary["reviewerDeclaredIndependentQuestions"],
            "aiAssistedHumanVerifiedQuestions": summary["aiAssistedQuestions"], "externalIndependenceCertified": False,
            "independenceClaimScope": "nine decisions declared without AI assistance; not external certification",
            "contextualCaveats": copy.deepcopy(summary["contextualCaveats"]),
            "reviewerConditionBindings": {"doc05Q5": "original five-control statement retained; human corrected to four",
                                         "doc05Q28": "canonical q28 / printed question8, physical page12",
                                         "doc06Q14": "possible role of preceding Texto14 remains a reviewer hypothesis, not proven dependency"},
            "freezeStatusAtCreation": "ready_for_introducing_commit_and_push",
            "formalFreezeRule": "introducing commit, push, matching remote HEAD and clean worktree/stage",
            "expectedPostPublicationStates": STATES, "futureRunnerCompatibilityResolved": False,
            "auditorExecuted": False, "metricsSeen": False, "ocrExecuted": False, "merge": False,
            "documents": documents, "questions": [{key: copy.deepcopy(q[key]) for key in QUESTION_FIELDS} for q in summary["questions"]]}

def validate_questions(gt, approved, manifest, index):
    require(gt["protocolVersion"] == "holdout-v5" and gt["annotationVersion"] == 1, "GT V5 version")
    require(len(gt["documents"]) == gt["documentsCount"] == 3 and len(gt["questions"]) == gt["questionsCount"] == 9, "batch size")
    documents = manifest["documents"][3:6]
    selected = [(d, q) for d in documents for q in d["selectedQuestions"]]
    require([q["questionId"] for q in gt["questions"]] == [q["questionId"] for _, q in selected], "question order and IDs")
    require(len({q["questionId"] for q in gt["questions"]}) == 9, "unique question IDs")
    require([d["documentId"] for d in gt["documents"]] == [d["documentId"] for d in documents], "document order")
    for actual, expected, (document, frozen) in zip(gt["questions"], approved["questions"], selected):
        require(actual == {key: expected[key] for key in QUESTION_FIELDS}, f"human decision difference: {actual['questionId']}")
        require(actual["documentId"] == document["documentId"] and actual["contentFingerprint"] == document["contentFingerprint"], "cross-document/fingerprint binding")
        canonical = next(d for d in index["documents"] if d["documentId"] == document["documentId"])
        require(canonical["contentFingerprint"] == actual["contentFingerprint"], "canonical fingerprint")
        require(frozen == next(q for q in canonical["questions"] if q["questionId"] == frozen["questionId"]), "selected object preservation")
        require(actual["canonicalQuestionNumber"] == frozen["questionNumber"], "canonical number")
        if "printedQuestionNumber" in frozen:
            require(actual["printedQuestionNumber"] == frozen["printedQuestionNumber"], "frozen printed number")
        require(actual["pageStart"] == frozen["pageStart"] and actual["pageEnd"] == frozen["pageEnd"], "boundaries preserved")
        require(actual["pages"] == list(range(frozen["pageStart"], frozen["pageEnd"] + 1)), "physical pages")
        require(1 <= actual["pageStart"] <= actual["pageEnd"] <= document["effectivePhysicalPageCount"], "invalid page range")
        for field, values in ENUMS.items():
            require(actual[field] in values, f"invalid enum: {field}")
        count, labels = actual["optionCount"], actual["optionLabels"]
        require(count is None or (type(count) is int and count >= 0), "optionCount type")
        require(labels is None or (isinstance(labels, list) and all(isinstance(label, str) for label in labels)), "optionLabels type")
        require(count is None or labels is None or count == len(labels), "count/labels inconsistency")
        require(isinstance(actual["notes"], str), "notes type")
        for field in ("subitems", "responseControls"):
            require(actual[field] is None or isinstance(actual[field], list), f"{field} type")
            for item in actual[field] or []:
                require(set(item) == {"label", "role", "pages", "notes"}, "structured element keys")
                require(all(isinstance(item[key], str) for key in ("label", "role", "notes")), "structured element strings")
                require(item["pages"] == actual["pages"], "structured element pages")
        require(actual["externalIndependenceCertification"] is False and actual["aiClassificationAssistanceDeclared"] is False, "declared provenance scope")
        require(actual["independentHumanAdjudicationClaimed"] is True, "reviewer independence declaration")
    require(gt["documentFingerprints"] == {d["documentId"]: d["contentFingerprint"] for d in documents}, "root fingerprints")
    require(gt["externalIndependenceCertified"] is False, "no external certification")
    require(all(gt[field] is False for field in ("auditorExecuted", "metricsSeen", "ocrExecuted", "merge")), "forbidden phase flags")
    unknown = sum(any(q[field] == "unknown" for field in ENUMS) or any(q[field] is None for field in ("optionCount", "optionLabels", "subitems", "responseControls")) for q in gt["questions"])
    return {"batch02Documents": 3, "batch02Questions": 9, "batch02UniqueQuestionIds": 9,
            "unknownQuestionIds": 0, "crossDocumentBindings": 0, "fingerprintMismatches": 0,
            "invalidPageRanges": 0, "selectionModified": False, "humanDecisionsReceived": 9,
            "humanDecisionsConfirmed": 9, "humanDecisionDifferences": 0, "unconfirmedHumanDecisions": 0,
            "reviewerDeclaredIndependentQuestions": 9, "aiAssistedHumanVerifiedQuestions": 0,
            "externalIndependenceCertified": False, "unknownClassificationQuestions": unknown,
            "auditorExecuted": False, "metricsSeen": False}

def run(root, materialize=False):
    evidence = build_evidence(root) if materialize else strict_json((root / EVIDENCE).read_bytes())
    approved, auth, pf, protection = validate_evidence(evidence)
    manifest, index = check_frozen(root, pf, protection)
    evidence_bytes = encoded(evidence)
    gt = make_gt(approved, manifest, pf, sha(evidence_bytes))
    gates = validate_questions(gt, approved, manifest, index)
    require(gt["questions"][5]["canonicalQuestionNumber"] == 28 and gt["questions"][5]["printedQuestionNumber"] == 8, "q28/printed8 distinction")
    require("pressupõe-se" in gt["questions"][7]["notes"], "q14 tentative note preserved")
    gt_bytes = encoded(gt)
    require(encoded(make_gt(approved, manifest, pf, sha(evidence_bytes))) == gt_bytes, "deterministic GT")
    parent = strict_json((root / "audit/holdout/v5-gt-review-batches-manifest.json").read_bytes())
    provenance = {"artifactType": "ground_truth_batch_provenance", "protocolVersion": "holdout-v5",
                  "annotationVersion": 1, "batchId": "holdout-v5-batch-02", "sourceHead": INITIAL_HEAD,
                  "groundTruth": {"path": GT, "sha256": sha(gt_bytes), "sizeBytes": len(gt_bytes)},
                  "humanDecisionEvidence": {"path": EVIDENCE, "sha256": sha(evidence_bytes), "sizeBytes": len(evidence_bytes)},
                  "approvedSummarySha256": SUMMARY_SHA, "finalAuthorizationSha256": AUTH_SHA,
                  "completedHumanCheckpointSha256": CHECKPOINT_SHA, "prepublicationProtectionSha256": PROTECTION_SHA,
                  "frozenInputFileSha256s": gt["frozenInputFileSha256s"], "batchPackageFiles": parent["batches"][1]["files"],
                  "batch01Preservation": protection["additionalReadOnlyFiles"],
                  "materializerAndValidatorSha256": sha(Path(__file__).read_bytes()),
                  "syntheticSelftestSha256": sha(Path(__file__).with_name("v5_ground_truth_batch02_selftest.py").read_bytes()),
                  "gates": gates, "deterministicSerialization": "UTF8/noBOM/LF/indent2/final newline",
                  "reviewerDeclaredIndependentQuestions": 9, "aiAssistedHumanVerifiedQuestions": 0,
                  "externalIndependenceCertified": False, "contextualCaveats": gt["contextualCaveats"],
                  "reviewerConditionBindings": gt["reviewerConditionBindings"],
                  "priorBatch01ExceptionPreserved": True, "accumulatedReviewClaimsAfterPublication": {"declaredWithoutAi": 17, "aiAssistedHumanVerified": 1, "externalIndependenceCertified": False},
                  "methodologyCaveats": parent["methodologyCaveats"], "futureRunnerCompatibilityResolved": False,
                  "freezeStatusAtCreation": "ready_for_introducing_commit_and_push", "expectedPostPublicationStates": STATES,
                  "nextStep": "STOP; no Batch03/global GT/OCR/Auditor/metrics/merge"}
    outputs = ((EVIDENCE, evidence_bytes), (GT, gt_bytes), (PROV, encoded(provenance)))
    for name, data in outputs:
        require(not (root / name).exists() or (root / name).read_bytes() == data, f"existing artifact mismatch: {name}")
    for name, data in outputs:
        if materialize:
            atomic_new(root / name, data)
        else:
            require((root / name).read_bytes() == data, f"published deterministic artifact: {name}")
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
