"""V5 B2a documentary triage: frozen JSON inputs only, no PDF/OCR/Auditor.

Default: reproduce and check the existing queue, without writing.
--emit: emit deterministic UTF-8 JSON for materialization.
--write: create a missing queue exclusively; never overwrite a frozen queue.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = "audit/holdout/question-index-v5-raw.json"
REPORT = "audit/holdout/question-index-v5-raw-report.json"
MANIFEST = "audit/holdout/manifest-v5-documents-frozen.json"
QUEUE = "audit/holdout/question-index-v5-review-queue.json"
SOURCE_FREEZE_COMMIT = "d63f5f9600a1da58cbb726f73ea3b1c32c1143bd"
SOURCE_HASHES = {
    RAW: "68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84",
    REPORT: "62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f",
    MANIFEST: "c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62",
}
EXPECTED_ANOMALIES = {
    "duplicate_question_number": 217,
    "missing_question_number": 887,
    "non_monotonic_numbering": 43,
    "requires_neutral_verification": 25,
    "unresolved_question_start": 11,
}
REASONS = {
    "A": "explicit neutral ambiguity or unresolved question-start sequence",
    "B": "non-monotonic numbering or high raw anomaly volume",
    "C": "remaining raw numbering/boundary anomalies",
    "D": "zero automatic anomalies; neutral control review",
}
# The four tier expressions and future review evidence are copied from V4.
REVIEW_POLICY = {
    "all48DocumentsReviewed": True,
    "tierA": "requires_neutral_verification or unresolved_question_start",
    "tierB": "non_monotonic_numbering or at least 20 raw anomalies",
    "tierC": "remaining documents with raw anomalies",
    "tierD": "zero-anomaly control documents",
    "allowedEvidence": [
        "question number visible in source PDF",
        "question start page",
        "question continuation/end page",
        "neutral OCR text",
        "neutral native PDF text",
    ],
    "forbiddenEvidence": [
        "responseMode", "optionCount", "optionLabels", "layout classification",
        "markerStyle classification", "correct answer", "answer key",
        "Ground Truth", "Auditor output",
    ],
}


def assign_tier(anomaly_counts):
    """Preexisting V4 precedence; inputs are diagnostic event counts only."""
    if anomaly_counts.get("requires_neutral_verification", 0) or anomaly_counts.get("unresolved_question_start", 0):
        return "A"
    if anomaly_counts.get("non_monotonic_numbering", 0) or sum(anomaly_counts.values()) >= 20:
        return "B"
    return "C" if sum(anomaly_counts.values()) > 0 else "D"


def queue_sort_key(entry):
    return (entry["reviewTier"], -entry["rawAnomalyCount"], entry["documentId"])


def keyed_documents(documents):
    result = {d["documentId"]: d for d in documents}
    assert len(documents) == len(result) == 48, "document count or uniqueness mismatch"
    return result


def sorted_counts(counts):
    return dict(sorted(counts.items()))


def build_queue(raw, report, manifest):
    """Pure deterministic transform; never consult event details or source files."""
    assert raw["protocolVersion"] == manifest["protocolVersion"] == "holdout-v5"
    assert raw["indexMethodVersion"] == "neutral-question-index-v1"
    assert raw["manifestFileSha256"] == SOURCE_HASHES[MANIFEST]
    assert manifest["selectedDocuments"] == 48
    for key in ["questionSelectionStarted", "groundTruthStarted", "auditorExecuted", "metricsSeen"]:
        assert manifest[key] is False
    raw_docs = keyed_documents(raw["documents"])
    reports = keyed_documents(report)
    sources = keyed_documents(manifest["documents"])
    assert set(raw_docs) == set(reports) == set(sources), "missing or unknown documents"
    raw_types_by_doc = {document_id: Counter() for document_id in sources}
    for event in raw["indexingAnomalies"]:
        assert event["documentId"] in sources
        assert event["type"] in EXPECTED_ANOMALIES
        raw_types_by_doc[event["documentId"]][event["type"]] += 1
    queue = []
    question_ids = []
    methods = Counter()
    questions_by_method = Counter()
    anomalies_by_method = Counter()
    all_anomalies = Counter()
    for document_id, source in sources.items():
        document, technical = raw_docs[document_id], reports[document_id]
        assert document["contentFingerprint"] == technical["contentFingerprint"] == source["contentFingerprint"]
        assert document["questions"] == technical["questions"]
        assert technical["method"] in {"native", "ocr"}
        assert type(technical["pageCount"]) is int and technical["pageCount"] > 0
        for question in document["questions"]:
            assert set(question) == {"questionId", "questionNumber", "pageStart", "pageEnd"}
            assert 1 <= question["pageStart"] <= question["pageEnd"] <= technical["pageCount"]
            question_ids.append(question["questionId"])
        types = Counter(event["type"] for event in technical["anomalies"])
        assert types == raw_types_by_doc[document_id], "raw/report anomaly counts differ"
        tier = assign_tier(types)
        entry = {
            "documentId": document_id,
            "contentFingerprint": source["contentFingerprint"],
            "canonicalPath": source["canonicalPath"],
            "family": source["family"],
            "year": source["year"],
            "series": source.get("series"),
            "sourceType": source["sourceType"],
            "indexMethod": technical["method"],
            "pageCount": technical["pageCount"],
            "rawQuestionCount": len(document["questions"]),
            "rawAnomalyCount": sum(types.values()),
            "anomalyTypeCounts": sorted_counts(types),
            "reviewTier": tier,
            "reviewReason": REASONS[tier],
            "reviewRequired": True,
            "responseSemanticsAllowed": False,
            "answerKeyAllowed": False,
            "auditorAllowed": False,
        }
        queue.append(entry)
        method = technical["method"]
        methods[method] += 1
        questions_by_method[method] += entry["rawQuestionCount"]
        anomalies_by_method[method] += entry["rawAnomalyCount"]
        all_anomalies.update(types)
    queue.sort(key=queue_sort_key)
    tiers = Counter(entry["reviewTier"] for entry in queue)
    assert len(question_ids) == len(set(question_ids)) == 1063
    assert all_anomalies == Counter(EXPECTED_ANOMALIES)
    assert sum(all_anomalies.values()) == len(raw["indexingAnomalies"]) == 1183
    assert sum(tiers.values()) == 48 and methods == Counter({"native": 29, "ocr": 19})
    return {
        "artifactType": "holdout-v5-neutral-question-index-review-queue",
        "protocolVersion": "holdout-v5",
        "phase": "B2a",
        "sourceRawIndex": RAW,
        "sourceRawIndexFileSha256": SOURCE_HASHES[RAW],
        "sourceRawReport": REPORT,
        "sourceRawReportFileSha256": SOURCE_HASHES[REPORT],
        "sourceManifest": MANIFEST,
        "sourceManifestFileSha256": SOURCE_HASHES[MANIFEST],
        "sourceFreezeCommit": SOURCE_FREEZE_COMMIT,
        "policySource": "audit/holdout/question-index-v4-review-queue.json",
        "policySourceFileSha256": "088bb091436bb8a195244da2a037394d0da02f66835e2be228fa029809f92592",
        "policyChangedFromV4": False,
        "documents": 48,
        "rawQuestions": 1063,
        "rawAnomalies": 1183,
        "indexMethodDistribution": sorted_counts(methods),
        "questionCountByIndexMethod": sorted_counts(questions_by_method),
        "anomalyCountByIndexMethod": sorted_counts(anomalies_by_method),
        "anomalyTypeCounts": sorted_counts(all_anomalies),
        "reviewTierCounts": {tier: tiers[tier] for tier in "ABCD"},
        "reviewPolicy": REVIEW_POLICY,
        "reviewOrder": ["reviewTier ascending A/B/C/D", "rawAnomalyCount descending", "documentId ascending"],
        "triageEvidence": [RAW, REPORT, MANIFEST],
        "reviewPolicyEvidenceScope": "allowedEvidence applies only to future authorized neutral review, not B2a triage",
        "all48DocumentsReviewed": True,
        "all48DocumentsReviewedMeaning": "all 48 remain mandatory for future neutral review; no review has been performed in B2a",
        "manualAdjudicationPerformed": False,
        "PDFsOpened": False,
        "rendersCreated": False,
        "anomaliesHumanReviewed": False,
        "responseSemanticsConsulted": False,
        "finalQuestionIndexCreated": False,
        "questionSelectionStarted": False,
        "questionSelectionExecuted": False,
        "groundTruthStarted": False,
        "groundTruthCreated": False,
        "auditorExecuted": False,
        "metricsSeen": False,
        "reviewQueue": queue,
    }


def serialize(queue):
    return (json.dumps(queue, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load_inputs():
    payloads = []
    for name in [RAW, REPORT, MANIFEST]:
        data = (ROOT / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == SOURCE_HASHES[name], f"frozen source drift: {name}"
        payloads.append(json.loads(data.decode("utf-8")))
    return payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    queue = build_queue(*load_inputs())
    data = serialize(queue)
    target = ROOT / QUEUE
    if args.emit:
        print(data.decode("utf-8"), end="")
        return
    if args.write:
        with target.open("xb") as handle:
            handle.write(data)
    assert target.is_file(), "queue not materialized; use --emit or --write"
    assert target.read_bytes() == data, "queue differs from deterministic reproduction"
    print(json.dumps({"status": "PASS", "documents": queue["documents"], "rawQuestions": queue["rawQuestions"], "rawAnomalies": queue["rawAnomalies"], "reviewTierCounts": queue["reviewTierCounts"], "queueSha256": hashlib.sha256(data).hexdigest(), "policyChangedFromV4": False, "all48DocumentsReviewed": True}, indent=2))


if __name__ == "__main__":
    main()
