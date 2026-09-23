from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import audit_holdout_schema as schema
import audit_response_holdout_select as selector


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate_frozen_candidate_pool(
    protocol: dict[str, Any],
    artifact: dict[str, Any],
) -> list[dict[str, Any]]:
    if artifact.get("artifactType") != "frozen-candidate-pool":
        raise schema.HoldoutValidationError(
            "candidatePool: artifactType must be frozen-candidate-pool"
        )

    if artifact.get("protocolVersion") != protocol.get("protocolVersion"):
        raise schema.HoldoutValidationError(
            "candidatePool: protocolVersion mismatch"
        )

    documents = artifact.get("documents")
    if not isinstance(documents, list) or not documents:
        raise schema.HoldoutValidationError(
            "candidatePool: documents missing"
        )

    frame = protocol.get("samplingFrameV3") or {}

    expected_count = int(frame.get("expectedV3CandidatePoolSize", 0))
    if len(documents) != expected_count:
        raise schema.HoldoutValidationError(
            f"candidatePool: expected {expected_count} documents, got {len(documents)}"
        )

    ids: set[str] = set()
    fingerprints: set[str] = set()

    for index, document in enumerate(documents):
        for field in (
            "documentId",
            "canonicalPath",
            "relativePath",
            "normalizedRelativePath",
            "contentFingerprint",
            "family",
            "year",
            "sourceType",
            "pageCount",
        ):
            if field not in document:
                raise schema.HoldoutValidationError(
                    f"candidatePool.documents[{index}]: missing {field}"
                )

        if document["sourceType"] not in schema.SOURCE_CLASSES:
            raise schema.HoldoutValidationError(
                f"candidatePool.documents[{index}]: bad sourceType"
            )

        document_id = document["documentId"]
        fingerprint = document["contentFingerprint"]

        if document_id in ids:
            raise schema.HoldoutValidationError(
                f"candidatePool: duplicate documentId {document_id}"
            )
        if fingerprint in fingerprints:
            raise schema.HoldoutValidationError(
                f"candidatePool: duplicate contentFingerprint {fingerprint}"
            )

        ids.add(document_id)
        fingerprints.add(fingerprint)

    actual_set_hash = schema.reserved_pool_hash(sorted(fingerprints))
    expected_set_hash = frame.get("expectedV3CandidatePoolHash")

    if actual_set_hash != expected_set_hash:
        raise schema.HoldoutValidationError(
            "candidatePool: fingerprint-set hash mismatch"
        )

    if artifact.get("contentFingerprintSetSha256") != actual_set_hash:
        raise schema.HoldoutValidationError(
            "candidatePool: internal fingerprint-set hash mismatch"
        )

    if int(artifact.get("documentCount", -1)) != len(documents):
        raise schema.HoldoutValidationError(
            "candidatePool: internal documentCount mismatch"
        )

    return documents


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Holdout V3 selection from frozen V2 reserved pool."
    )
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--candidate-pool", required=True)
    parser.add_argument("--question-index", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    protocol = _load(args.protocol)
    schema.validate_protocol(protocol)

    if protocol.get("protocolVersion") != "holdout-v3":
        raise schema.HoldoutValidationError(
            "V3 selector requires protocolVersion=holdout-v3"
        )

    artifact_path = Path(args.candidate_pool)
    artifact = _load(artifact_path)

    expected_artifact_hash = (
        protocol.get("samplingFrameV3", {})
        .get("candidatePoolArtifactSha256")
    )
    actual_artifact_hash = schema.sha256_file(artifact_path)

    if actual_artifact_hash != expected_artifact_hash:
        raise schema.HoldoutValidationError(
            "candidatePool: artifact file SHA-256 mismatch"
        )

    expected_canonical_hash = (
        protocol.get("samplingFrameV3", {})
        .get("candidatePoolCanonicalJsonSha256")
    )
    actual_canonical_hash = schema.sha256_json(artifact)

    if actual_canonical_hash != expected_canonical_hash:
        raise schema.HoldoutValidationError(
            "candidatePool: canonical JSON SHA-256 mismatch"
        )

    pool = validate_frozen_candidate_pool(protocol, artifact)

    seed = (
        args.seed
        if args.seed is not None
        else int(protocol["selectionSeed"])
    )

    selection = selector.select_documents(
        pool,
        protocol["randomHoldout"],
        seed,
    )

    if selection["status"] != "ok":
        print(json.dumps(
            {
                "status": selection["status"],
                "unsatisfied": selection["unsatisfied"],
                "stats": selection["stats"],
            },
            ensure_ascii=False,
            indent=2,
        ))
        raise SystemExit(2)

    identity = selector.code_identity()

    provenance = {
        "protocolSha256": schema.sha256_file(args.protocol),
        "inventorySha256": (
            protocol["samplingFrameV3"]["inventorySha256"]
        ),
        "candidatePoolHash": schema.canonical_content_pool_hash(pool),
        "candidatePoolPathHash": schema.sha256_json(
            sorted(d["normalizedRelativePath"] for d in pool)
        ),
        "selectorVersion": schema.selector_version_for(
            protocol["protocolVersion"]
        ),
        "excludedByReason": {},
        **identity,
    }

    question_index = (
        _load(args.question_index)
        if args.question_index
        else None
    )

    if question_index is not None:
        schema.validate_question_index(question_index)

    manifest = selector.build_manifest(
        protocol,
        provenance,
        selection,
        question_index,
        seed,
    )

    manifest["candidatePoolArtifact"] = (
        protocol["samplingFrameV3"]["candidatePoolArtifact"]
    )
    manifest["candidatePoolArtifactSha256"] = actual_artifact_hash
    manifest["candidatePoolCanonicalJsonSha256"] = actual_canonical_hash
    manifest["candidatePoolFingerprintSetSha256"] = (
        artifact["contentFingerprintSetSha256"]
    )
    manifest["candidatePoolCount"] = len(pool)

    schema.validate_manifest(manifest)

    if question_index is not None:
        schema.validate_bindings(
            manifest,
            question_index=question_index,
        )

    schema.write_json(args.out, manifest)

    print(json.dumps(
        {
            "status": "ok",
            "out": args.out,
            "documents": len(manifest["documents"]),
            "candidatePoolCount": len(pool),
            "candidatePoolFingerprintSetSha256":
                artifact["contentFingerprintSetSha256"],
            "selectionCodeState": manifest["selectionCodeState"],
            "selectionSeed": seed,
            "selectedBySource": selection["stats"]["bySource"],
            "selectedFamilies": len(selection["stats"]["families"]),
            "selectedDistinctYears":
                len(selection["stats"]["distinctYears"]),
            "coveredEras": selection["stats"]["coveredEras"],
            "remainingReservedCount": selection["reservedCount"],
            "remainingReservedPoolHash": selection["reservedPoolHash"],
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
