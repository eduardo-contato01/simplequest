"""V5 neutral selector: stdlib only; never imports or runs the Auditor."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RULE_PATH = "audit/holdout/v5-question-selection-rule.json"
SCRIPT_PATH = "audit/holdout/v5_select_questions.py"
SELFTEST_PATH = "audit/holdout/v5_select_questions_selftest.py"
RESULT = "audit/holdout/manifest-v5-questions-frozen.json"
PROVENANCE = "audit/holdout/manifest-v5-questions-frozen.provenance.json"
OUT = "outputs/audit/holdout/v5-question-selection"
SEED = "156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e"
ALGORITHM = "v5-qselect-tertile-sha256-v1"
INPUTS = {
    "audit/holdout/question-index-v5-final.json": "a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7",
    "audit/holdout/manifest-v5-documents-effective-r1.json": "a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32",
    "audit/holdout/manifest-v5-documents-frozen.json": "c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value, compact=False):
    if compact:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".pending")
    data = encode(value)
    with temporary.open("xb") as file:
        file.write(data)
        file.flush()
        import os
        os.fsync(file.fileno())
    require(temporary.read_bytes() == data, "Temporary verification failed")
    temporary.replace(path)
    require(path.read_bytes() == data, "Atomic output verification failed")
    return sha(data)


def windows(n):
    require(type(n) is int and n >= 3, "At least three canonical objects required")
    bounds = [0, n // 3, (2 * n) // 3, n]
    return list(zip(bounds, bounds[1:]))


def candidate_hash(seed, document_id, tertile, question_id):
    return sha(f"v5-question-selection|{seed}|{document_id}|{tertile}|{question_id}".encode("utf-8"))


def choose(document, seed, hash_fn=candidate_hash):
    result = []
    for t, (start, end) in enumerate(windows(len(document["questions"]))):
        ranked = [(hash_fn(seed, document["documentId"], t, q["questionId"]), q["questionId"], i)
                  for i, q in enumerate(document["questions"][start:end], start)]
        digest, qid, position = min(ranked, key=lambda row: (row[0], row[1]))
        result.append({"tertileIndex": t, "windowStart": start, "windowEndExclusive": end,
                       "canonicalArrayIndex": position, "questionId": qid, "selectionSha256": digest,
                       "question": copy.deepcopy(document["questions"][position])})
    return result


def validate_pool(manifest, index, expected_documents=48, expected_questions=2136):
    docs, canonical = manifest["documents"], index["documents"]
    require(len(docs) == len(canonical) == expected_documents, "Document count mismatch")
    require(len({d["documentId"] for d in docs}) == len(docs), "Duplicate manifest documentId")
    require(len({d["documentId"] for d in canonical}) == len(canonical), "Duplicate index documentId")
    require(len({d["contentFingerprint"] for d in docs}) == len(docs), "Duplicate manifest fingerprint")
    require(len({d["contentFingerprint"] for d in canonical}) == len(canonical), "Duplicate index fingerprint")
    by_id = {d["documentId"]: d for d in canonical}
    require(set(by_id) == {d["documentId"] for d in docs}, "Document identity sets differ")
    ids = set()
    forbidden = {"responseMode", "optionCount", "optionLabels", "markerStyle", "answerKey", "correctAnswer", "predictions"}
    def neutral(value):
        if isinstance(value, dict):
            require(not forbidden.intersection(value), "Forbidden response data")
            for v in value.values():
                neutral(v)
        elif isinstance(value, list):
            for v in value:
                neutral(v)
    for m in docs:
        d = by_id[m["documentId"]]
        require(m["contentFingerprint"] == d["contentFingerprint"], "Fingerprint mismatch")
        require(m["canonicalPath"] == d["canonicalPath"], "Source path mismatch")
        physical = d["effectivePhysicalPageCount"]
        require(type(physical) is int and physical >= 1, "Invalid physical page count")
        windows(len(d["questions"]))
        require("unresolved" not in d["status"], "Active unresolved document")
        for q in d["questions"]:
            require(isinstance(q["questionId"], str) and q["questionId"] not in ids, "Duplicate/invalid questionId")
            ids.add(q["questionId"])
            if "documentId" in q:
                require(q["documentId"] == d["documentId"], "Cross-document canonical object")
            start, end = q["pageStart"], q["pageEnd"]
            require(type(start) is type(end) is int and 1 <= start <= end <= physical, "Invalid physical range")
            neutral(q)
    require(len(ids) == expected_questions, "Canonical question count mismatch")
    return by_id


def inputs_and_rule():
    values = {}
    for relative, expected in INPUTS.items():
        data = (ROOT / relative).read_bytes()
        require(sha(data) == expected, f"Frozen input SHA256 mismatch: {relative}")
        values[relative] = json.loads(data.decode("utf-8"))
    rule_bytes = (ROOT / RULE_PATH).read_bytes()
    rule = json.loads(rule_bytes.decode("utf-8"))
    require(rule["algorithmId"] == ALGORITHM and rule["seedSha256"] == SEED, "Rule or seed mismatch")
    for name, path_field in [("sourceIndex", "sourceIndexSha256"), ("sourceEffectiveManifest", "sourceEffectiveManifestSha256"), ("sourceHistoricalManifest", "sourceHistoricalManifestSha256")]:
        require(INPUTS.get(rule[name]) == rule[path_field], "Rule input binding mismatch")
    index = values[rule["sourceIndex"]]
    manifest = values[rule["sourceEffectiveManifest"]]
    require(manifest["seedSha256"] == values[rule["sourceHistoricalManifest"]]["seedSha256"] == SEED, "Historical seed drift")
    by_id = validate_pool(manifest, index)
    require(sum(d["effectivePhysicalPageCount"] for d in index["documents"]) == 741, "Physical page total mismatch")
    require("v5-doc-a08230ae0b1cad7e" not in by_id and "v5-doc-e1c73fb849ef80a6" in by_id, "Effective replacement drift")
    d = by_id["v5-doc-74e153f9c146d887"]
    require(d["sourceFrozenPageCount"] == 1 and d["effectivePhysicalPageCount"] == 21, "Page erratum drift")
    d = by_id["v5-doc-7a302456c4a6afbe"]
    require(len(d["questions"]) == 26 and not {18, 19, 20, 21}.intersection(q["questionNumber"] for q in d["questions"]), "Canonical gaps drift")
    return rule, rule_bytes, manifest, index, by_id


def materialize(rule, manifest, index, picks, binding):
    documents = []
    for m in manifest["documents"]:
        d = next(d for d in index["documents"] if d["documentId"] == m["documentId"])
        out = copy.deepcopy(m)
        require(not {"selectedQuestions", "selectionEvidence", "canonicalDocumentMetadata"}.intersection(out), "R1 field collision")
        out.update({"sourceFrozenPageCount": m["pageCount"], "effectivePhysicalPageCount": d["effectivePhysicalPageCount"],
                    "canonicalQuestionCount": len(d["questions"]), "selectedQuestions": [copy.deepcopy(p["question"]) for p in picks[m["documentId"]]],
                    "selectionEvidence": [{k: copy.deepcopy(v) for k, v in p.items() if k != "question"} for p in picks[m["documentId"]]],
                    "canonicalDocumentMetadata": {k: copy.deepcopy(v) for k, v in d.items() if k != "questions"}})
        documents.append(out)
    methodology_keys = ["historicalSelection", "effectivePopulation", "pageCountConvention", "sourceIncompleteDocuments",
                        "sourceIntegrityInconclusiveDocuments", "originalExaminationCompletenessCertified", "methodologicalCases",
                        "parallelRepresentationPolicy", "adjudicationMode", "independentHumanAdjudicationClaimed", "groundTruthHumanIndependenceClaimed",
                        "reviewPolicy", "preservedPostFreezeProvenance", "sourceResumptionProvenance", "preservation"]
    return {"artifactType": "neutral_question_selection_manifest", "protocolVersion": "holdout-v5", "branch": "audit/holdout-v5-blind",
            "sourceHead": binding["ruleCommit"], "ruleBinding": binding, "algorithmId": ALGORITHM, "seedSha256": SEED,
            "inputSha256s": INPUTS, "documentsCount": 48, "questionsPerDocument": 3, "selectedQuestionsCount": 144,
            "totalEffectivePhysicalPages": 741, "documentOrder": "effective R1 documents array", "questionOrder": "tertile 0,1,2",
            "sourceEffectiveManifestMetadata": {k: copy.deepcopy(v) for k, v in manifest.items() if k != "documents"},
            "canonicalIndexMethodology": {k: copy.deepcopy(index[k]) for k in methodology_keys},
            "finalQuestionIndexFrozen": True, "questionSelectionExecuted": True,
            "publicationStatusAtCreation": "pending_introducing_commit_and_push",
            "publicationContract": {"requiredCommitMessage": "audit: freeze v5 question selection 144",
                "effectiveOnlyAfterCommitPushRemoteMatch": True,
                "formalStateBeforePublication": {"questionSelectionFrozen": False, "PhaseBComplete": False},
                "formalStateAfterPublication": {"questionSelectionFrozen": True, "PhaseBComplete": True, "selectedQuestions": 144},
                "phaseBDefinition": "published V5 document freeze: neutral canonical index plus question selection freeze"},
            "manualSwaps": 0, "alternateSeedRetries": 0, "GTConsulted": False, "AuditorConsulted": False,
            "groundTruthStarted": False, "groundTruthCreated": False, "ocrExecuted": False, "auditorExecuted": False,
            "metricsSeen": False, "merge": False, "documents": documents}


def ordered_ids(result):
    return [[d["documentId"], [q["questionId"] for q in d["selectedQuestions"]]] for d in result["documents"]]


def git(executable, *arguments):
    return subprocess.run([executable, *arguments], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def binding_for_commit(executable, commit, rule_bytes):
    require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "Full rule commit required")
    paths = [RULE_PATH, SCRIPT_PATH, SELFTEST_PATH]
    digests = {}
    for p in paths:
        data = (ROOT / p).read_bytes()
        require(git(executable, "show", f"{commit}:{p}") == data, f"Published rule/code drift: {p}")
        digests[p] = sha(data)
    require(digests[RULE_PATH] == sha(rule_bytes), "Rule hash mismatch")
    return {"ruleCommit": commit, "rulePath": RULE_PATH, "ruleSha256": digests[RULE_PATH],
            "scriptPath": SCRIPT_PATH, "scriptSha256": digests[SCRIPT_PATH], "selftestSha256": digests[SELFTEST_PATH]}


def official(executable, commit):
    rule, rb, manifest, index, by_id = inputs_and_rule()
    require(git(executable, "branch", "--show-current").decode().strip() == "audit/holdout-v5-blind", "Wrong branch")
    require(git(executable, "rev-parse", "HEAD").decode().strip() == commit, "HEAD is not rule commit")
    require(not git(executable, "status", "--porcelain") and not git(executable, "diff", "--cached", "--name-only"), "Selection requires clean state")
    remote = git(executable, "ls-remote", "--heads", "origin", "refs/heads/audit/holdout-v5-blind").decode().split()[0]
    require(remote == commit, "Rule publication not confirmed")
    binding = binding_for_commit(executable, commit, rb)
    ledger = ROOT / OUT / "official-invocation.json"
    require(not ledger.exists() and not ledger.with_name(ledger.name + ".pending").exists(), "Official invocation already recorded; STOP, never silently rerun")
    require(not (ROOT / RESULT).exists() and not (ROOT / PROVENANCE).exists(), "Existing result; STOP")
    timestamp = datetime.now(timezone.utc).isoformat()
    invocation = {"officialInvocationCount": 1, "officialRetries": 0, "alternateSeedRetries": 0,
                  "sourceHead": commit, "startedAtUTC": timestamp, "status": "started", "binding": binding}
    atomic_json(ledger, invocation)
    picks = {m["documentId"]: choose(by_id[m["documentId"]], SEED) for m in manifest["documents"]}
    result = materialize(rule, manifest, index, picks, binding)
    ids = ordered_ids(result)
    provenance = {"artifactType": "neutral_question_selection_provenance", "sourceHead": commit, **binding,
                  "inputSha256s": INPUTS, "algorithmId": ALGORITHM, "seedSha256": SEED,
                  "executedAtUTC": timestamp, "officialInvocationCount": 1, "officialRetries": 0,
                  "manualSwaps": 0, "alternateSeedRetries": 0, "selectedQuestions": 144,
                  "orderedSelectedIds": ids, "orderedSelectedIdsSha256": sha(encode(ids, compact=True)),
                  "resultPath": RESULT, "resultSha256": sha(encode(result)),
                  "publicationStatusAtCreation": "pending_introducing_commit_and_push",
                  "GTConsulted": False, "AuditorConsulted": False, "metricsSeen": False, "merge": False}
    atomic_json(ROOT / OUT / "selection-checkpoint.json", {"result": result, "provenance": provenance})
    atomic_json(ROOT / RESULT, result)
    atomic_json(ROOT / PROVENANCE, provenance)
    atomic_json(ROOT / OUT / "official-invocation-completed.json", {**invocation, "status": "materialized", "resultSha256": provenance["resultSha256"], "orderedSelectedIdsSha256": provenance["orderedSelectedIdsSha256"]})
    print(json.dumps({"status": "SELECTION_EXECUTED_PENDING_FORMAL_PUBLICATION", "officialInvocations": 1,
                      "documents": 48, "selectedQuestions": 144, "resultSha256": provenance["resultSha256"],
                      "orderedSelectedIdsSha256": provenance["orderedSelectedIdsSha256"]}, indent=2))


def verify(executable):
    rule, rb, manifest, index, by_id = inputs_and_rule()
    raw = (ROOT / RESULT).read_bytes()
    result = json.loads(raw.decode("utf-8"))
    provenance = json.loads((ROOT / PROVENANCE).read_bytes().decode("utf-8"))
    binding = binding_for_commit(executable, provenance["ruleCommit"], rb)
    require(result["ruleBinding"] == binding, "Wrong frozen rule binding")
    # Independent oracle: enumerate canonical indices, construct literal inputs,
    # sort all candidates; does not call windows(), choose(), or candidate_hash().
    replay = {}
    for m in manifest["documents"]:
        d = by_id[m["documentId"]]
        n = len(d["questions"])
        bounds = [0, n // 3, n * 2 // 3, n]
        choices = []
        for t in range(3):
            scores = []
            for position in range(bounds[t], bounds[t + 1]):
                q = d["questions"][position]
                literal = "|".join(["v5-question-selection", SEED, m["documentId"], str(t), q["questionId"]])
                scores.append((hashlib.sha256(literal.encode("utf-8")).hexdigest(), q["questionId"], position))
            digest, qid, position = sorted(scores, key=lambda row: (row[0], row[1]))[0]
            choices.append({"tertileIndex": t, "windowStart": bounds[t], "windowEndExclusive": bounds[t+1],
                            "canonicalArrayIndex": position, "questionId": qid, "selectionSha256": digest,
                            "question": copy.deepcopy(d["questions"][position])})
        replay[m["documentId"]] = choices
    expected = materialize(rule, manifest, index, replay, binding)
    require(result == expected and raw == encode(expected), "Independent IDs/objects/metadata/bytes replay mismatch")
    ids = ordered_ids(expected)
    flat = [qid for _, qs in ids for qid in qs]
    require(len(flat) == len(set(flat)) == 144, "Duplicate selection or count mismatch")
    require(provenance["orderedSelectedIds"] == ids and provenance["orderedSelectedIdsSha256"] == sha(encode(ids, compact=True)), "Ordered ID hash drift")
    require(provenance["resultSha256"] == sha(raw), "Result hash drift")
    require(provenance["officialInvocationCount"] == 1 and provenance["officialRetries"] == provenance["alternateSeedRetries"] == provenance["manualSwaps"] == 0, "Invocation/retry/swap drift")
    ledger = json.loads((ROOT / OUT / "official-invocation.json").read_bytes())
    require(ledger["officialInvocationCount"] == 1 and ledger["sourceHead"] == binding["ruleCommit"], "Invocation ledger drift")
    checks = {"documents": 48, "questionsPerDocument": 3, "selectedQuestions": 144, "uniqueQuestionIds": 144,
              "unknownQuestionIds": 0, "duplicateSelections": 0, "crossDocumentBindings": 0,
              "fingerprintMismatches": 0, "invalidPhysicalPageRanges": 0, "manualSwaps": 0,
              "alternateSeedRetries": 0, "GTConsulted": False, "AuditorConsulted": False, "metricsSeen": False,
              "deterministicReplay": "PASS", "byteIdenticalReconstruction": True,
              "orderedSelectedIdsSha256": sha(encode(ids, compact=True))}
    print(json.dumps(checks, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--select", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--rule-commit")
    parser.add_argument("--git-exe", default="git")
    args = parser.parse_args()
    if args.preflight:
        inputs_and_rule()
        print("PREFLIGHT PASS: 48 documents, 741 effective pages, 2136 canonical objects; no real IDs chosen")
    elif args.select:
        require(args.rule_commit is not None, "--rule-commit required")
        official(args.git_exe, args.rule_commit)
    else:
        verify(args.git_exe)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
