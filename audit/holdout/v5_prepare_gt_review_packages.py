"""Mechanical, label-free V5 review packages; stdlib only, no PDF parser/Auditor.

Run selftests first. --prepare creates/resumes all batches; --verify is read-only.
Existing completed artifacts are never overwritten. Incomplete .pending files
belong exclusively to this preparer and can be regenerated on automatic resume.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path

SOURCE_HEAD = "1605ff5a07cfcbfd5b11b161422bb7eb27398907"
INPUT_HASHES = {
    "audit/holdout/manifest-v5-questions-frozen.json": "91cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46",
    "audit/holdout/manifest-v5-questions-frozen.provenance.json": "f78ef04d6e425e64315dd175386dcdda49b260b5abd2099c90f5558b5a3129ee",
    "audit/holdout/question-index-v5-final.json": "a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7",
}
IDS_HASH = "11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a"
FIELDS = ("responseMode", "optionCount", "optionLabels", "subitems", "responseControls",
          "layout", "markerStyle", "contentKind", "notes")
OUT = "outputs/audit/holdout"
PROGRESS = OUT + "/v5-ground-truth-preparation"
TECHNICAL_MANIFEST = "audit/holdout/v5-gt-review-batches-manifest.json"
# Whitelist neutral source caveats; never infer labels from metadata or notes.
CAVEATS = ("neutralNotes", "sourceIncomplete", "sourceIncompleteReason",
           "sourceMissingQuestionNumbers", "sourceMissingPrintedPages",
           "sourceIntegrityInconclusive", "originalExaminationCompletenessCertified",
           "originalExamCompletenessCertified", "adjudicationScope", "evidenceScope",
           "sourceVersion", "sourceVersionProvenance", "replacementProvenance",
           "pageCountErratum", "pageCountErratumSha256", "technicalSizeCaveat",
           "sectionNumberingPolicy", "canonicalizationPolicy")
METHODOLOGY = {
    "sourceScope": "frozen_available_pdf_content; no certification of original examination completeness",
    "replacement": "canonical global22 effective replacement; historical original retained only as provenance; post-freeze/performance-blind",
    "pageCount": "canonical global21 sourceFrozenPageCount=1, effectivePhysicalPageCount=21; physical ranges use21",
    "numbering": "canonical global8 has26 objects q1-17/q22-30; no q18-21 fabricated",
    "modifiedSource": "canonical global48 frozen available modified version; no reconstruction of institutional original",
    "historicalAuxiliaryIntegrity": "415 old auxiliaries prospectively preserved; not_independently_verifiable; historicalByteIdentityVerified=false; exception not reopened",
    "schemaCompatibility": "own neutral V5 package validator; legacy functional schema supports only V1-V4; future filled GT V5 integration is a separate unresolved gate before official Auditor",
    "independence": "no human decisions imported or simulated; prior assisted neutral adjudication is not independent human GT",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(p):
    return json.loads(Path(p).read_bytes().decode("utf-8"))


def atomic_new(p, data):
    """Idempotent publication; mismatch of a completed file is a STOP."""
    p = Path(p)
    if p.exists():
        require(p.read_bytes() == data, f"existing artifact differs: {p}")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    pending = p.with_name(p.name + ".pending")
    with pending.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(pending, p)


def atomic_progress(p, obj):
    data = encoded(obj)
    if p.exists() and p.read_bytes() == data:
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    pending = p.with_name(p.name + ".pending")
    with pending.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(pending, p)


def entry(root, p):
    return {"name": p.name, "path": p.relative_to(root).as_posix(),
            "sizeBytes": p.stat().st_size, "sha256": file_hash(p)}


def validate_inputs(manifest, provenance, index, expected_ids=IDS_HASH):
    docs = manifest["documents"]
    require(manifest["protocolVersion"] == index["protocolVersion"] == "holdout-v5", "protocolVersion")
    require(len(docs) == len(index["documents"]) == 48, "48 documents required")
    require(manifest["documentsCount"] == 48 and manifest["selectedQuestionsCount"] == 144, "selected totals")
    require(index["totalPhysicalPages"] == 741 and index["canonicalQuestions"] == 2136, "canonical totals")
    require(sum(len(d["questions"]) for d in index["documents"]) == 2136, "canonical objects")
    pools = {d["documentId"]: d for d in index["documents"]}
    require(len(pools) == 48, "duplicate canonical documentId")
    ids, fingerprints, ordered = set(), set(), []
    for doc in docs:
        did, fp = doc["documentId"], doc["contentFingerprint"]
        require(did in pools and pools[did]["contentFingerprint"] == fp, f"binding: {did}")
        require(fp not in fingerprints, f"duplicate fingerprint: {did}")
        fingerprints.add(fp)
        require(len(doc["selectedQuestions"]) == 3, f"three questions: {did}")
        canonical = pools[did]
        require(doc["canonicalDocumentMetadata"] == {k: v for k, v in canonical.items() if k != "questions"}, f"metadata: {did}")
        require(doc["effectivePhysicalPageCount"] == canonical["effectivePhysicalPageCount"], f"effective pages: {did}")
        for q in doc["selectedQuestions"]:
            qid = q["questionId"]
            require(qid not in ids and qid.startswith(did + ":"), f"question binding/duplicate: {qid}")
            ids.add(qid)
            matches = [c for c in canonical["questions"] if c["questionId"] == qid]
            require(matches == [q], f"exact selected object: {qid}")
            require(type(q["pageStart"]) is int and type(q["pageEnd"]) is int and
                    1 <= q["pageStart"] <= q["pageEnd"] <= doc["effectivePhysicalPageCount"], f"pages: {qid}")
        ordered.append([did, [q["questionId"] for q in doc["selectedQuestions"]]])
    require(len({d["documentId"] for d in docs}) == 48 and len(ids) == 144, "unique totals")
    require(sum(d["effectivePhysicalPageCount"] for d in docs) == 741, "physical total")
    require(digest(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) == expected_ids, "ordered IDs hash/R1 order")
    require(provenance["orderedSelectedIds"] == ordered and provenance["orderedSelectedIdsSha256"] == expected_ids, "provenance IDs")
    require(provenance["officialInvocationCount"] == 1 and provenance["officialRetries"] == 0, "selection invocation provenance")
    return docs


def load_inputs(root):
    inputs = []
    for p, h in INPUT_HASHES.items():
        require(file_hash(root / p) == h, f"frozen input hash: {p}")
        inputs.append(read_json(root / p))
    require(inputs[1]["resultSha256"] == INPUT_HASHES[next(iter(INPUT_HASHES))], "provenance result hash")
    return validate_inputs(*inputs)


def batch_dir(root, batch):
    return root / OUT / f"v5-ground-truth-batch-{batch:02d}-review"


def pdf_name(position, doc):
    return f"{position:02d}_{doc['documentId']}.pdf"


def identity(doc, q):
    return {"documentId": doc["documentId"], "contentFingerprint": doc["contentFingerprint"],
            "questionId": q["questionId"], "canonicalQuestionNumber": q["questionNumber"],
            "pageStart": q["pageStart"], "pageEnd": q["pageEnd"],
            "pages": list(range(q["pageStart"], q["pageEnd"] + 1))}


def payloads(root, batch, docs):
    start = (batch - 1) * 3 + 1
    context_docs, questions = [], []
    for pos, doc in enumerate(docs, start):
        meta = doc["canonicalDocumentMetadata"]
        context_docs.append({"r1Position": pos, "canonicalGlobalOrder": meta["globalOrder"],
                             "documentId": doc["documentId"], "contentFingerprint": doc["contentFingerprint"],
                             "pdfName": pdf_name(pos, doc),
                             "pdfPath": (batch_dir(root, batch) / pdf_name(pos, doc)).relative_to(root).as_posix(),
                             "canonicalSourcePath": doc["canonicalPath"],
                             "sourceFrozenPageCount": doc["sourceFrozenPageCount"],
                             "effectivePhysicalPageCount": doc["effectivePhysicalPageCount"],
                             "sourceCaveats": {k: copy.deepcopy(meta[k]) for k in CAVEATS if k in meta},
                             "selectedQuestions": [identity(doc, q) for q in doc["selectedQuestions"]]})
        questions.extend({**identity(doc, q), **dict.fromkeys(FIELDS)} for q in doc["selectedQuestions"])
    context = {"artifactType": "neutral_human_review_context", "protocolVersion": "holdout-v5",
               "batch": f"{batch:02d}", "r1Positions": list(range(start, start + 3)),
               "frozenInputSha256s": INPUT_HASHES, "orderedSelectedIdsSha256": IDS_HASH,
               "methodologyCaveats": METHODOLOGY, "documents": context_docs}
    template = {"artifactType": "blank_human_annotation_template", "protocolVersion": "holdout-v5",
                "batch": f"{batch:02d}", "humanAdjudicated": False,
                "groundTruthBatchCreated": False, "identityFieldsLocked": True,
                "nullMeaning": "unannotated; not a human uncertainty decision",
                "questions": questions}
    upload_names = [pdf_name(pos, d) for pos, d in enumerate(docs, start)] + [
        "review-context.json", "ANNOTATION_TEMPLATE.json", "FILES_TO_UPLOAD.txt", "INTEGRITY_MANIFEST.json"]
    return {"review-context.json": encoded(context), "ANNOTATION_TEMPLATE.json": encoded(template),
            "FILES_TO_UPLOAD.txt": ("\n".join(upload_names) + "\n").encode("utf-8")}


def approved_copies(root, doc):
    """Only previously prepared neutral V5 review copies; no corpus-wide search."""
    for directory in ("v5-tier-a-batch-01-review", "v5-tier-a-batch-02-review",
                      "v5-tier-a-batch-02-replacement-r1", "v5-tier-b-review",
                      "v5-tier-c-review", "v5-tier-d-review"):
        base = root / OUT / directory
        if base.exists():
            yield from sorted(base.glob(f"**/*{doc['documentId']}*.pdf"))


def source_for(root, doc):
    source = Path(doc["canonicalPath"])
    try:
        actual = file_hash(source)
    except OSError as exc:
        reason = type(exc).__name__
        for candidate in approved_copies(root, doc):
            require(file_hash(candidate) == doc["contentFingerprint"], f"fallback fingerprint: {candidate}")
            return candidate, {"mode": "preexisting_hash_verified_copy", "originalPath": str(source),
                               "originalUnavailableReason": reason, "sourcePath": str(candidate),
                               "sourceSha256": doc["contentFingerprint"]}
        raise ValueError(f"mandatory PDF unavailable: {doc['documentId']} / {source}") from exc
    require(actual == doc["contentFingerprint"], f"original fingerprint: {source}")
    return source, {"mode": "original", "sourcePath": str(source), "sourceSha256": actual}


def copy_pdf(root, doc, target):
    source, provenance = source_for(root, doc)
    require(source.stat().st_size == doc["sizeBytes"], f"source size: {source}")
    if target.exists():
        require(file_hash(target) == doc["contentFingerprint"], f"existing PDF differs: {target}")
        return provenance
    target.parent.mkdir(parents=True, exist_ok=True)
    pending = target.with_name(target.name + ".pending")
    with source.open("rb") as src, pending.open("wb") as dst:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            dst.write(block)
        dst.flush()
        os.fsync(dst.fileno())
    require(file_hash(pending) == doc["contentFingerprint"] and pending.stat().st_size == doc["sizeBytes"], f"copy integrity: {pending}")
    os.replace(pending, target)
    return provenance


def verify_batch(root, batch, docs):
    base = batch_dir(root, batch)
    inv = read_json(base / "INTEGRITY_MANIFEST.json")
    require(inv["batch"] == f"{batch:02d}" and inv["frozenInputSha256s"] == INPUT_HASHES, "inventory binding")
    expected = payloads(root, batch, docs)
    names = [pdf_name(pos, d) for pos, d in enumerate(docs, (batch - 1) * 3 + 1)] + list(expected)
    require([e["name"] for e in inv["files"]] == names, "inventory order/files")
    require({p.name for p in base.iterdir()} == set(names) | {"INTEGRITY_MANIFEST.json"}, f"unexpected/missing package files: {base}")
    for e in inv["files"]:
        require(e == entry(root, base / e["name"]), f"inventory integrity: {e['path']}")
    for name, data in expected.items():
        require((base / name).read_bytes() == data, f"neutral context/template binding: {base / name}")
    for pos, doc in enumerate(docs, (batch - 1) * 3 + 1):
        require(file_hash(base / pdf_name(pos, doc)) == doc["contentFingerprint"], f"prepared PDF fingerprint: {doc['documentId']}")
        record = inv["pdfSources"][pos - ((batch - 1) * 3 + 1)]
        require(record["documentId"] == doc["documentId"] and record["sourceSha256"] == doc["contentFingerprint"], "PDF provenance binding")
        require(record["mode"] in ("original", "preexisting_hash_verified_copy"), "PDF provenance mode")
    return {"batch": f"{batch:02d}", "r1Positions": list(range((batch - 1) * 3 + 1, batch * 3 + 1)),
            "directory": base.relative_to(root).as_posix(), "documentIds": [d["documentId"] for d in docs],
            "questionIds": [q["questionId"] for d in docs for q in d["selectedQuestions"]],
            "files": inv["files"] + [entry(root, base / "INTEGRITY_MANIFEST.json")],
            "pdfSources": inv["pdfSources"], "verified": True}


def prepare_batch(root, batch, docs):
    base = batch_dir(root, batch)
    checkpoint = root / PROGRESS / f"batch-{batch:02d}.json"
    if (base / "INTEGRITY_MANIFEST.json").exists():
        result = verify_batch(root, batch, docs)
        atomic_new(checkpoint, encoded(result))
        return result
    ledger_path = root / PROGRESS / f"batch-{batch:02d}-files.json"
    ledger = read_json(ledger_path) if ledger_path.exists() else {"batch": f"{batch:02d}", "files": [], "pdfSources": []}
    for e in ledger["files"]:
        require(e == entry(root, root / e["path"]), f"partial progress integrity: {e['path']}")
    artifacts = [(pdf_name(pos, doc), doc) for pos, doc in enumerate(docs, (batch - 1) * 3 + 1)]
    expected = payloads(root, batch, docs)
    for name, doc in artifacts:
        record = next((e for e in ledger["pdfSources"] if e["documentId"] == doc["documentId"]), None)
        if record is None:
            record = {"documentId": doc["documentId"], **copy_pdf(root, doc, base / name)}
            ledger["pdfSources"].append(record)
        e = entry(root, base / name)
        require(e["sha256"] == doc["contentFingerprint"] and e["sizeBytes"] == doc["sizeBytes"], f"PDF: {name}")
        if e not in ledger["files"]:
            ledger["files"].append(e)
        atomic_progress(ledger_path, ledger)
    for name, data in expected.items():
        atomic_new(base / name, data)
        e = entry(root, base / name)
        if e not in ledger["files"]:
            ledger["files"].append(e)
        atomic_progress(ledger_path, ledger)
    inventory = {"artifactType": "neutral_review_file_integrity", "protocolVersion": "holdout-v5",
                 "batch": f"{batch:02d}", "frozenInputSha256s": INPUT_HASHES,
                 "selfHashConvention": "own hash stored in parent technical manifest and batch checkpoint; no recursive self-hash",
                 "files": ledger["files"], "pdfSources": ledger["pdfSources"]}
    atomic_new(base / "INTEGRITY_MANIFEST.json", encoded(inventory))
    result = verify_batch(root, batch, docs)
    atomic_new(checkpoint, encoded(result))
    return result


def consolidated(root, docs, batches):
    qids = [q for b in batches for q in b["questionIds"]]
    require(len(batches) == 16 and len(qids) == len(set(qids)) == 144, "complete disjoint coverage")
    require([d for b in batches for d in b["documentIds"]] == [d["documentId"] for d in docs], "R1 partition")
    return {"artifactType": "neutral_human_gt_review_packages_manifest", "protocolVersion": "holdout-v5",
            "sourceHead": SOURCE_HEAD, "branch": "audit/holdout-v5-blind",
            "frozenInputSha256s": INPUT_HASHES, "orderedSelectedIdsSha256": IDS_HASH,
            "preparerSha256": file_hash(Path(__file__)),
            "selftestSha256": file_hash(Path(__file__).with_name("v5_prepare_gt_review_packages_selftest.py")),
            "reviewProtocolSha256": file_hash(root / "audit/holdout/V5_GROUND_TRUTH_REVIEW_PROTOCOL.md"),
            "methodologyCaveats": METHODOLOGY,
            "publicationStatusAtCreation": "pending_introducing_commit_and_push",
            "publicationContract": "effective after introducing commit, push and matching remote HEAD; local packages remain ignored and hash-bound",
            "gates": {"reviewPackagesPrepared": 16, "documentsCovered": 48, "selectedQuestionsCovered": 144,
                      "uniqueQuestionIds": 144, "missingQuestions": 0, "duplicateQuestionIds": 0,
                      "documentFingerprintMismatches": 0, "invalidPageRanges": 0,
                      "labelsAutoFilled": 0, "humanDecisionsImported": 0, "groundTruthBatchesCreated": 0,
                      "groundTruthFinalCreated": False, "auditorExecuted": False, "metricsSeen": False},
            "formalStateAfterPublication": {"PhaseBComplete": True, "questionSelectionFrozen": True,
                                           "groundTruthReviewPackagesPrepared": True,
                                           "groundTruthHumanAdjudicationComplete": False, "groundTruthCreated": False,
                                           "auditorExecuted": False, "metricsSeen": False, "merge": False},
            "batches": batches}


def run(root, prepare=False):
    docs = load_inputs(root)
    batches = []
    for batch in range(1, 17):
        block = docs[(batch - 1) * 3:batch * 3]
        batches.append(prepare_batch(root, batch, block) if prepare else verify_batch(root, batch, block))
        print(f"batch{batch:02d} PASS:3 documents/9 questions/blank template", flush=True)
    report = consolidated(root, docs, batches)
    if prepare:
        atomic_new(root / TECHNICAL_MANIFEST, encoded(report))
        atomic_new(root / PROGRESS / "all-batches-complete.json", encoded(report))
    else:
        require((root / TECHNICAL_MANIFEST).read_bytes() == encoded(report), "technical manifest deterministic binding")
        require((root / PROGRESS / "all-batches-complete.json").read_bytes() == encoded(report), "complete checkpoint binding")
    print(json.dumps(report["gates"], ensure_ascii=False), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[2], args.prepare)
