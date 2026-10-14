"""Isolated post-human materialization/validation. No Auditor imports or PDF parser.

--materialize reads only the approved Batch01 journal and frozen bindings.
--verify compares the published evidence, GT and provenance without new labels.
The legacy functional V1-V4 schema is deliberately not imported or modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

INITIAL_HEAD = "df3e7e688a6eae00512515b3696470af378b7a5b"
SUMMARY_SHA = "7f685dead1a63f568cf409d3cd90779e4e959845bae7f6777559facabbb1d742"
AUTH_SHA = "d012108f2496eb140254f54661ecaef661d2715c50e85d6bbd44e0fd43e1a39a"
WORK = "outputs/audit/holdout/v5-ground-truth-batch-01-adjudication"
EVIDENCE = "audit/holdout/ground-truth-v5-batch-01.human-decisions.json"
GT = "audit/holdout/ground-truth-v5-batch-01.json"
PROV = "audit/holdout/ground-truth-v5-batch-01.provenance.json"
RESPONSE_FIELDS = ("responseMode", "optionCount", "optionLabels", "subitems", "responseControls",
                   "layout", "markerStyle", "contentKind", "notes")
QUESTION_FIELDS = ("documentId", "contentFingerprint", "questionId", "canonicalQuestionNumber",
                   "pageStart", "pageEnd", "pages", *RESPONSE_FIELDS,
                   "annotationOrigin", "independentHumanAdjudicationClaimed")
MODES = {"single_choice", "true_false", "numeric_response", "discursive", "other", "unknown"}
LAYOUTS = {"vertical", "two_column", "grid", "parent_child", "internal_enumeration", "mixed", "none", "unknown"}
MARKERS = {"textual", "parenthesized", "circled_outline", "circled_filled", "symbolic_control", "none", "mixed", "unknown"}
KINDS = {"text", "math", "media", "mixed", "none", "unknown"}
STATES = {"PhaseBComplete": True, "questionSelectionFrozen": True, "groundTruthStarted": True,
          "groundTruthBatch01Created": True, "groundTruthQuestionsAdjudicated": 9,
          "groundTruthQuestionsRemaining": 135, "groundTruthHumanAdjudicationComplete": False,
          "groundTruthFinalCreated": False, "auditorExecuted": False, "metricsSeen": False, "merge": False}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def strict_json(raw):
    def pairs(items):
        d = {}
        for k, v in items:
            require(k not in d, f"duplicate JSON key: {k}")
            d[k] = v
        return d
    return json.loads(raw, object_pairs_hook=pairs)


def atomic_new(target, data):
    if target.exists():
        require(target.read_bytes() == data, f"existing artifact mismatch: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(target.name + ".pending")
    with temp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    require(temp.read_bytes() == data, f"atomic write: {target}")
    os.replace(temp, target)


def embedded(p, root):
    raw = p.read_bytes()
    return {"path": p.relative_to(root).as_posix(), "sha256": sha(raw),
            "sizeBytes": len(raw), "rawUtf8": raw.decode("utf-8")}


def unpack(record):
    raw = record["rawUtf8"].encode("utf-8")
    require(len(raw) == record["sizeBytes"] and sha(raw) == record["sha256"], f"embedded evidence integrity: {record['path']}")
    return raw


def build_evidence(root):
    work = root / WORK
    summary = embedded(work / "review-summary-pending-confirmation.json", root)
    auth = embedded(work / "batch-final-authorization.json", root)
    require(summary["sha256"] == SUMMARY_SHA and auth["sha256"] == AUTH_SHA, "approved summary/final authorization hash")
    cp = strict_json((work / "checkpoint.json").read_bytes())
    require(cp["humanDecisionsReceived"] == cp["confirmedHumanDecisions"] == 9, "nine individual confirmations")
    preflight = embedded(work / "preflight.json", root)
    require(preflight["sha256"] == cp["preflightSha256"], "preflight history")
    events = []
    for e in cp["receivedEvents"]:
        record = embedded(work / e["file"], root)
        require(record["sha256"] == e["sha256"], f"human journal immutable: {e['file']}")
        events.append(record)
    return {"artifactType": "mandatory_human_decision_evidence", "protocolVersion": "holdout-v5",
            "annotationVersion": 1, "batchId": "holdout-v5-batch-01", "sourceHead": INITIAL_HEAD,
            "approvedSummary": summary, "finalHumanAuthorization": auth, "sourcePreflight": preflight,
            "rawDecisionEvents": events,
            "sourceSnapshotsRemainUnchanged": True,
            "rawUtf8Convention": "UTF8 round-trip restores exact original bytes, including operational snapshots; embedded raw journal is not rewritten",
            "wholeBatchStrictlyIndependent": False, "independentHumanReviewClaims": 8,
            "aiAssistedHumanVerifiedQuestions": 1, "auditorExecuted": False, "metricsSeen": False}


def validate_evidence(evidence):
    require(evidence["protocolVersion"] == "holdout-v5", "evidence protocol")
    require(evidence["approvedSummary"]["sha256"] == SUMMARY_SHA, "approved summary binding")
    require(evidence["finalHumanAuthorization"]["sha256"] == AUTH_SHA, "final authorization binding")
    summary = strict_json(unpack(evidence["approvedSummary"]))
    auth = strict_json(unpack(evidence["finalHumanAuthorization"]))
    pf = strict_json(unpack(evidence["sourcePreflight"]))
    require(auth["approvedSummarySha256"] == SUMMARY_SHA, "authorization names exact summary")
    for field in ("nineQuestionRecordsConfirmed", "structuredRepresentationsConfirmed", "finalPublicationAuthorized",
                  "q4ExceptionAuthorized", "q3InternalContentRoleConfirmed", "q98SharedFiguresDependencyMustBePreserved"):
        require(auth.get(field) is True, f"explicit human authorization: {field}")
    require(auth["wholeBatchStrictIndependenceClaimAuthorized"] is False, "no strict independence claim")
    require(summary["individualReviewConfirmationsReceived"] == 9, "summary confirmations")
    latest, event_hashes = {}, {}
    for record in evidence["rawDecisionEvents"]:
        raw = unpack(record)
        # Sole documented operational anomaly: Q38's first record contains
        # materializationAuthorized=false twice. Identical metadata only;
        # every original byte is retained. No duplicate human field is allowed.
        def journal_pairs(items):
            obj = {}
            for k, v in items:
                if k in obj:
                    require(k == "materializationAuthorized" and obj[k] is False and v is False,
                            f"ambiguous journal key: {k}")
                obj[k] = v
            return obj
        event = json.loads(raw, object_pairs_hook=journal_pairs)
        latest[event["questionId"]] = event
        event_hashes[Path(record["path"]).name] = record["sha256"]
    require(len(latest) == 9, "nine received question decisions")
    for q in summary["questions"]:
        require(latest[q["questionId"]].get("reviewConfirmedByHuman") is True, f"individual human confirmation: {q['questionId']}")
        for e in q["sourceEvents"]:
            require(event_hashes.get(e["file"]) == e["sha256"], "question evidence reference")
    return summary, auth, pf


def make_gt(evidence, manifest, evidence_sha):
    summary, auth, pf = validate_evidence(evidence)
    questions = [{k: copy.deepcopy(q[k]) for k in QUESTION_FIELDS} for q in summary["questions"]]
    docs = [{"documentId": d["documentId"], "contentFingerprint": d["contentFingerprint"],
             "effectivePhysicalPageCount": d["effectivePhysicalPageCount"],
             "selectedQuestionIds": [q["questionId"] for q in d["selectedQuestions"]]}
            for d in manifest["documents"][:3]]
    return {"artifactType": "reviewer_approved_ground_truth_batch", "protocolVersion": "holdout-v5",
            "annotationVersion": 1, "freezeVersion": 1, "batchId": "holdout-v5-batch-01",
            "sourceHead": INITIAL_HEAD, "documentsCount": 3, "questionsCount": 9,
            "documentFingerprints": {d["documentId"]: d["contentFingerprint"] for d in docs},
            "frozenInputFileSha256s": pf["frozenInputs"], "approvedSummarySha256": SUMMARY_SHA,
            "humanDecisionEvidence": {"path": EVIDENCE, "sha256": evidence_sha},
            "humanAdjudicated": True,
            "humanAdjudicatedMeaning": "all nine records examined, verified and explicitly approved by the reviewer; NOT a claim of strict independent human classification for all nine",
            "wholeBatchStrictlyIndependent": False, "independentHumanReviewClaims": 8,
            "aiAssistedHumanVerifiedQuestions": 1,
            "methodologicalException": {"questionId": docs[0]["selectedQuestionIds"][0],
                                       "origin": "ai_assisted_human_verified", "strictlyIndependent": False,
                                       "authorization": "explicit external authorization before publication; post-observation, not preregistered"},
            "reviewerConditionBindings": {"doc03Q3Subitems": "three ⋅ internal content elements; not alternatives nor independent responses",
                                         "doc02Q98": "text describes question body only; shared text and two figures are necessary and preserved in notes"},
            "freezeStatusAtCreation": "ready_for_introducing_commit_and_push",
            "formalFreezeRule": "introducing commit, push, matching remote HEAD and clean worktree/stage",
            "expectedPostPublicationStates": STATES,
            "futureRunnerCompatibilityResolved": False,
            "auditorExecuted": False, "metricsSeen": False, "ocrExecuted": False, "merge": False,
            "documents": docs, "questions": questions}


def validate_questions(gt, approved, manifest, index):
    require(gt["protocolVersion"] == "holdout-v5" and gt["annotationVersion"] == 1, "GT V5 annotation version")
    require(len(gt["documents"]) == gt["documentsCount"] == 3, "three documents")
    require(len(gt["questions"]) == gt["questionsCount"] == 9, "nine questions")
    selected = [(d, q) for d in manifest["documents"][:3] for q in d["selectedQuestions"]]
    require([q["questionId"] for q in gt["questions"]] == [q["questionId"] for _, q in selected], "frozen question order and identities")
    require(len({q["questionId"] for q in gt["questions"]}) == 9, "unique questionId")
    require([d["documentId"] for d in gt["documents"]] == [d["documentId"] for d in manifest["documents"][:3]], "frozen R1 document order")
    for actual, expected, (doc, frozen) in zip(gt["questions"], approved["questions"], selected):
        require(actual == {k: expected[k] for k in QUESTION_FIELDS}, f"human decision difference: {actual['questionId']}")
        require(actual["documentId"] == doc["documentId"] and actual["contentFingerprint"] == doc["contentFingerprint"], "cross-document/fingerprint binding")
        canonical = next(d for d in index["documents"] if d["documentId"] == doc["documentId"])
        require(canonical["contentFingerprint"] == doc["contentFingerprint"], "canonical document binding")
        require(frozen == next(q for q in canonical["questions"] if q["questionId"] == frozen["questionId"]), "selected object preservation")
        require(actual["canonicalQuestionNumber"] == frozen["questionNumber"], "canonical number preservation")
        require(actual["pageStart"] == frozen["pageStart"] and actual["pageEnd"] == frozen["pageEnd"], "page boundaries preservation")
        require(actual["pages"] == list(range(frozen["pageStart"], frozen["pageEnd"] + 1)), "physical pages exact")
        require(1 <= actual["pageStart"] <= actual["pageEnd"] <= doc["effectivePhysicalPageCount"], "invalid physical range")
        require(actual["responseMode"] in MODES and actual["layout"] in LAYOUTS and actual["markerStyle"] in MARKERS and actual["contentKind"] in KINDS, "annotation enum")
        count, labels = actual["optionCount"], actual["optionLabels"]
        require(count is None or (type(count) is int and count >= 0), "optionCount type")
        require(labels is None or (isinstance(labels, list) and all(isinstance(s, str) for s in labels)), "optionLabels type")
        require(isinstance(actual["notes"], str), "notes type")
        for field in ("subitems", "responseControls"):
            require(actual[field] is None or isinstance(actual[field], list), f"{field} type")
            for item in actual[field] or []:
                require(set(item) == {"label", "role", "pages", "notes"}, f"{field} object keys")
                require(all(isinstance(item[k], str) for k in ("label", "role", "notes")), f"{field} strings")
                require(item["pages"] == actual["pages"], f"{field} pages")
    fingerprints = {d["documentId"]: d["contentFingerprint"] for d in manifest["documents"][:3]}
    require(gt["documentFingerprints"] == fingerprints, "root fingerprints")
    require(gt["wholeBatchStrictlyIndependent"] is False, "false whole-batch independence claim")
    require(sum(q["independentHumanAdjudicationClaimed"] is True for q in gt["questions"]) == 8, "eight independent claims")
    require(gt["questions"][0]["independentHumanAdjudicationClaimed"] is False and gt["questions"][0]["annotationOrigin"] == "ai_assisted_human_verified", "Q4 disclosure")
    require(gt["auditorExecuted"] is False and gt["metricsSeen"] is False, "forbidden phase flags")
    return {"documents": 3, "questions": 9, "uniqueQuestionIds": 9, "unknownQuestionIds": 0,
            "crossDocumentBindings": 0, "fingerprintMismatches": 0, "invalidPageRanges": 0,
            "selectionModified": False, "humanDecisionsReceived": 9, "humanDecisionDifferences": 0,
            "unconfirmedHumanDecisions": 0, "strictlyIndependentHumanQuestions": 8,
            "authorizedAiAssistedHumanVerifiedQuestions": 1, "unknownClassificationQuestions": sum(
                any(q[f] == "unknown" for f in ("responseMode", "layout", "markerStyle", "contentKind")) for q in gt["questions"]),
            "auditorExecuted": False, "metricsSeen": False}


def frozen_inputs(root, pf):
    for p, h in pf["frozenInputs"].items():
        require(sha((root / p).read_bytes()) == h, f"frozen input: {p}")
    for e in pf["verifiedPackageFiles"]:
        b = (root / e["path"]).read_bytes()
        require(len(b) == e["sizeBytes"] and sha(b) == e["sha256"], f"Batch01 package integrity: {e['path']}")
    return strict_json((root / "audit/holdout/manifest-v5-questions-frozen.json").read_bytes()), strict_json((root / "audit/holdout/question-index-v5-final.json").read_bytes())


def run(root, materialize=False):
    evidence = build_evidence(root) if materialize else strict_json((root / EVIDENCE).read_bytes())
    approved, auth, pf = validate_evidence(evidence)
    manifest, index = frozen_inputs(root, pf)
    evidence_bytes = encoded(evidence)
    gt = make_gt(evidence, manifest, sha(evidence_bytes))
    gates = validate_questions(gt, approved, manifest, index)
    # Latest explicit conditions, checked against the unchanged approved data.
    q3 = gt["questions"][6]
    require([s["label"] for s in q3["subitems"]] == ["⋅", "⋅", "⋅"], "three internal dot elements")
    require(all(s["role"] == "parte interna do conteúdo, não classificatória" for s in q3["subitems"]), "internal role, not alternative or independent response")
    require("duas figuras compartilhados" in gt["questions"][5]["notes"], "Q98 shared figure dependence")
    gt_bytes = encoded(gt)
    require(encoded(make_gt(evidence, manifest, sha(evidence_bytes))) == gt_bytes, "deterministic construction")
    provenance = {"artifactType": "ground_truth_batch_provenance", "protocolVersion": "holdout-v5",
                  "annotationVersion": 1, "batchId": "holdout-v5-batch-01", "sourceHead": INITIAL_HEAD,
                  "groundTruth": {"path": GT, "sha256": sha(gt_bytes), "sizeBytes": len(gt_bytes)},
                  "humanDecisionEvidence": {"path": EVIDENCE, "sha256": sha(evidence_bytes), "sizeBytes": len(evidence_bytes)},
                  "approvedSummarySha256": SUMMARY_SHA, "finalAuthorizationSha256": AUTH_SHA,
                  "frozenInputFileSha256s": pf["frozenInputs"], "batchPackageFiles": pf["verifiedPackageFiles"],
                  "materializerAndValidatorSha256": sha(Path(__file__).read_bytes()),
                  "syntheticSelftestSha256": sha(Path(__file__).with_name("v5_ground_truth_batch01_selftest.py").read_bytes()),
                  "gates": gates, "deterministicSerialization": "UTF8/noBOM/LF/indent2/final newline",
                  "wholeBatchStrictlyIndependent": False, "q4Exception": gt["methodologicalException"],
                  "sourceSerializationNotes": approved["sourceSerializationNotes"],
                  "futureRunnerCompatibilityResolved": False,
                  "freezeStatusAtCreation": "ready_for_introducing_commit_and_push",
                  "expectedPostPublicationStates": STATES, "nextStep": "STOP; Batch02 requires a new authorization"}
    for p, data in ((EVIDENCE, evidence_bytes), (GT, gt_bytes), (PROV, encoded(provenance))):
        if materialize:
            atomic_new(root / p, data)
        else:
            require((root / p).read_bytes() == data, f"published deterministic artifact: {p}")
    receipt = {"groundTruthSha256": sha(gt_bytes), "provenanceSha256": sha(encoded(provenance)),
               "humanEvidenceSha256": sha(evidence_bytes), "gates": gates}
    if materialize:
        atomic_new(root / WORK / "materialization-validation.json", encoded(receipt))
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--materialize", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[2], args.materialize)
