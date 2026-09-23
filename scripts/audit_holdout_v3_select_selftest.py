from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_schema as schema
import audit_holdout_v3_select as v3


FAILURES: list[str] = []


def check(name: str, condition: bool, detail="") -> None:
    if condition:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        FAILURES.append(name)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_schema_v3_registered() -> None:
    check(
        "schema.v3_supported",
        "holdout-v3" in schema.SUPPORTED_PROTOCOL_VERSIONS,
        schema.SUPPORTED_PROTOCOL_VERSIONS,
    )
    check(
        "schema.v3_selector_version",
        schema.selector_version_for("holdout-v3") == "holdout-v3",
        schema.selector_version_for("holdout-v3"),
    )


def test_frozen_real_pool_without_selection() -> None:
    protocol_path = ROOT / "audit/holdout/protocol-v3.json"
    pool_path = ROOT / "audit/holdout/candidate-pool-v3.json"

    protocol = load(protocol_path)
    artifact = load(pool_path)

    schema.validate_protocol(protocol)

    frame = protocol["samplingFrameV3"]

    check(
        "realpool.file_hash",
        schema.sha256_file(pool_path) == frame["candidatePoolArtifactSha256"],
        schema.sha256_file(pool_path),
    )

    check(
        "realpool.canonical_hash",
        schema.sha256_json(artifact) == frame["candidatePoolCanonicalJsonSha256"],
        schema.sha256_json(artifact),
    )

    documents = v3.validate_frozen_candidate_pool(protocol, artifact)

    check("realpool.count_535", len(documents) == 535, len(documents))

    fingerprints = {d["contentFingerprint"] for d in documents}
    check("realpool.unique_535", len(fingerprints) == 535, len(fingerprints))

    check(
        "realpool.set_hash",
        schema.reserved_pool_hash(sorted(fingerprints))
        == "577c1eed100a3ca3822e783222470209268b324882ec22cd017bdcf21424d789",
    )

    by_source: dict[str, int] = {}
    for document in documents:
        source = document["sourceType"]
        by_source[source] = by_source.get(source, 0) + 1

    check(
        "realpool.source_composition",
        by_source == {
            "text_native": 358,
            "raster": 173,
            "hybrid": 4,
        },
        by_source,
    )

    quota = protocol["randomHoldout"]["sourceQuota"]

    check("protocol.quota_sum_48", sum(quota.values()) == 48, quota)
    check(
        "protocol.quota_exact",
        quota == {
            "text_native": 31,
            "raster": 15,
            "text_low_quality": 0,
            "hybrid": 2,
        },
        quota,
    )


def test_no_prior_revealed_overlap() -> None:
    artifact = load(ROOT / "audit/holdout/candidate-pool-v3.json")
    v1 = load(ROOT / "audit/holdout/manifest-v1.json")
    v2 = load(ROOT / "audit/holdout/manifest-v2.json")
    v1_prov = load(ROOT / "audit/holdout/manifest-v1.provenance.json")

    pool_fps = {
        d["contentFingerprint"]
        for d in artifact["documents"]
    }

    v1_fps = {
        d["contentFingerprint"]
        for d in v1["documents"]
    }

    v2_fps = {
        d["contentFingerprint"]
        for d in v2["documents"]
    }

    dev_fps = set(
        (v1_prov.get("developmentContentFingerprints") or {}).values()
    )

    check("overlap.v1_zero", len(pool_fps & v1_fps) == 0, pool_fps & v1_fps)
    check("overlap.v2_zero", len(pool_fps & v2_fps) == 0, pool_fps & v2_fps)
    check("overlap.dev_zero", len(pool_fps & dev_fps) == 0, pool_fps & dev_fps)


def synthetic_protocol(count: int, fingerprint_hash: str) -> dict:
    return {
        "protocolVersion": "holdout-v3",
        "samplingFrameV3": {
            "expectedV3CandidatePoolSize": count,
            "expectedV3CandidatePoolHash": fingerprint_hash,
        },
    }


def synthetic_doc(index: int, fp: str) -> dict:
    return {
        "documentId": f"doc-{index}",
        "canonicalPath": f"G:/fake/{index}.pdf",
        "relativePath": f"fake/{index}.pdf",
        "normalizedRelativePath": f"fake/{index}.pdf",
        "contentFingerprint": fp,
        "family": "CMX",
        "year": 2020,
        "era": "2020-2025",
        "series": "6o Ano",
        "sourceType": "text_native",
        "pageCount": 10,
        "duplicatePaths": [],
        "duplicateCount": 0,
    }


def test_synthetic_tamper_guards() -> None:
    fps = [
        schema.sha256_text("a"),
        schema.sha256_text("b"),
    ]

    documents = [
        synthetic_doc(1, fps[0]),
        synthetic_doc(2, fps[1]),
    ]

    set_hash = schema.reserved_pool_hash(fps)

    protocol = synthetic_protocol(2, set_hash)
    artifact = {
        "artifactType": "frozen-candidate-pool",
        "protocolVersion": "holdout-v3",
        "documentCount": 2,
        "contentFingerprintSetSha256": set_hash,
        "documents": documents,
    }

    try:
        validated = v3.validate_frozen_candidate_pool(protocol, artifact)
        check("synthetic.valid", len(validated) == 2)
    except Exception as exc:
        check("synthetic.valid", False, str(exc))

    bad_count = dict(artifact)
    bad_count["documentCount"] = 3

    try:
        v3.validate_frozen_candidate_pool(protocol, bad_count)
        check("synthetic.count_tamper_rejected", False, "should raise")
    except schema.HoldoutValidationError:
        check("synthetic.count_tamper_rejected", True)

    bad_hash = dict(artifact)
    bad_hash["contentFingerprintSetSha256"] = "0" * 64

    try:
        v3.validate_frozen_candidate_pool(protocol, bad_hash)
        check("synthetic.hash_tamper_rejected", False, "should raise")
    except schema.HoldoutValidationError:
        check("synthetic.hash_tamper_rejected", True)

    dup_docs = [
        synthetic_doc(1, fps[0]),
        synthetic_doc(2, fps[0]),
    ]

    duplicate_artifact = {
        "artifactType": "frozen-candidate-pool",
        "protocolVersion": "holdout-v3",
        "documentCount": 2,
        "contentFingerprintSetSha256": set_hash,
        "documents": dup_docs,
    }

    try:
        v3.validate_frozen_candidate_pool(protocol, duplicate_artifact)
        check("synthetic.duplicate_rejected", False, "should raise")
    except schema.HoldoutValidationError:
        check("synthetic.duplicate_rejected", True)


def main() -> None:
    test_schema_v3_registered()
    test_frozen_real_pool_without_selection()
    test_no_prior_revealed_overlap()
    test_synthetic_tamper_guards()

    if FAILURES:
        print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
        raise SystemExit(1)

    print("\nTodos os checks do Holdout V3 passaram.")
    print("OFFICIAL_V3_SELECTION_EXECUTED=false")


if __name__ == "__main__":
    main()
