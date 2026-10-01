from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import audit_holdout_schema as schema
import audit_response_holdout_select as selector


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str | Path) -> Any:
  return json.loads(
    Path(path).read_text(
      encoding="utf-8-sig"
    )
  )


def _write_json_lf(
  path: str | Path,
  value: Any,
) -> None:
  target = Path(path)

  target.parent.mkdir(
    parents=True,
    exist_ok=True,
  )

  target.write_bytes(
    (
      json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
      )
      + "\n"
    ).encode(
      "utf-8"
    )
  )


def validate_frozen_candidate_pool(
  protocol: dict[str, Any],
  artifact: dict[str, Any],
) -> list[dict[str, Any]]:

  if (
    artifact.get(
      "artifactType"
    )
    != "frozen-candidate-pool"
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: artifactType mismatch"
    )

  if (
    artifact.get(
      "protocolVersion"
    )
    != "holdout-v4"
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: protocolVersion mismatch"
    )

  documents = artifact.get(
    "documents"
  )

  if (
    not isinstance(
      documents,
      list,
    )
    or not documents
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: documents missing"
    )

  frame = (
    protocol.get(
      "samplingFrameV4"
    )
    or {}
  )

  expected_count = int(
    frame.get(
      "eligibleDocuments"
    )
    or 0
  )

  if len(
    documents
  ) != expected_count:
    raise schema.HoldoutValidationError(
      "candidatePool: document count mismatch"
    )

  ids = set()
  fingerprints = set()

  for index, document in enumerate(
    documents
  ):
    for field in (
      "documentId",
      "canonicalPath",
      "relativePath",
      "normalizedRelativePath",
      "contentFingerprint",
      "family",
      "year",
      "era",
      "sourceType",
      "pageCount",
    ):
      if field not in document:
        raise schema.HoldoutValidationError(
          f"candidatePool.documents[{index}]: "
          f"missing {field}"
        )

    if (
      document[
        "sourceType"
      ]
      not in schema.SOURCE_CLASSES
    ):
      raise schema.HoldoutValidationError(
        f"candidatePool.documents[{index}]: "
        "bad sourceType"
      )

    document_id = document[
      "documentId"
    ]

    fingerprint = document[
      "contentFingerprint"
    ]

    if document_id in ids:
      raise schema.HoldoutValidationError(
        "candidatePool: duplicate documentId"
      )

    if fingerprint in fingerprints:
      raise schema.HoldoutValidationError(
        "candidatePool: duplicate fingerprint"
      )

    ids.add(
      document_id
    )

    fingerprints.add(
      fingerprint
    )

  set_hash = schema.reserved_pool_hash(
    sorted(
      fingerprints
    )
  )

  expected_set_hash = frame.get(
    "contentFingerprintSetSha256"
  )

  if set_hash != expected_set_hash:
    raise schema.HoldoutValidationError(
      "candidatePool: fingerprint-set "
      "hash mismatch"
    )

  if (
    artifact.get(
      "contentFingerprintSetSha256"
    )
    != set_hash
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: internal set hash mismatch"
    )

  if int(
    artifact.get(
      "documentCount",
      -1,
    )
  ) != len(
    documents
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: documentCount mismatch"
    )

  source_distribution = dict(
    Counter(
      document[
        "sourceType"
      ]
      for document in documents
    )
  )

  if (
    source_distribution
    != frame.get(
      "sourceDistribution"
    )
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: source distribution mismatch"
    )

  era_distribution = dict(
    Counter(
      document[
        "era"
      ]
      for document in documents
    )
  )

  if (
    era_distribution
    != frame.get(
      "eraDistribution"
    )
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: era distribution mismatch"
    )

  if len({
    document[
      "family"
    ]
    for document in documents
  }) != int(
    frame.get(
      "distinctFamilies"
    )
    or 0
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: family count mismatch"
    )

  if len({
    int(
      document[
        "year"
      ]
    )
    for document in documents
  }) != int(
    frame.get(
      "distinctYears"
    )
    or 0
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: year count mismatch"
    )

  return documents


def resolve_selection_seed(
  protocol: dict[str, Any],
  override: int | None,
) -> int:

  frozen = int(
    protocol[
      "selectionSeed"
    ]
  )

  if (
    override is not None
    and int(
      override
    )
    != frozen
  ):
    raise schema.HoldoutValidationError(
      "V4 selector forbids overriding "
      "the frozen selectionSeed"
    )

  return frozen


def main() -> None:
  parser = argparse.ArgumentParser(
    description=(
      "Holdout V4 deterministic document "
      "selection from the frozen V4 pool."
    )
  )

  parser.add_argument(
    "--protocol",
    required=True,
  )

  parser.add_argument(
    "--candidate-pool",
    required=True,
  )

  parser.add_argument(
    "--seed",
    type=int,
    default=None,
  )

  parser.add_argument(
    "--out",
    required=True,
  )

  args = parser.parse_args()

  protocol = _load(
    args.protocol
  )

  schema.validate_protocol(
    protocol
  )

  if (
    protocol.get(
      "protocolVersion"
    )
    != "holdout-v4"
  ):
    raise schema.HoldoutValidationError(
      "V4 selector requires "
      "protocolVersion=holdout-v4"
    )

  artifact_path = Path(
    args.candidate_pool
  )

  artifact = _load(
    artifact_path
  )

  frame = protocol[
    "samplingFrameV4"
  ]

  actual_file_sha = schema.sha256_file(
    artifact_path
  )

  if (
    actual_file_sha
    != frame[
      "candidatePoolArtifactSha256"
    ]
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: file SHA mismatch"
    )

  actual_canonical_sha = schema.sha256_json(
    artifact
  )

  if (
    actual_canonical_sha
    != frame[
      "candidatePoolCanonicalJsonSha256"
    ]
  ):
    raise schema.HoldoutValidationError(
      "candidatePool: canonical SHA mismatch"
    )

  pool = validate_frozen_candidate_pool(
    protocol,
    artifact,
  )

  seed = resolve_selection_seed(
    protocol,
    args.seed,
  )

  identity = selector.code_identity()

  if (
    identity.get(
      "selectionCodeState"
    )
    != "clean"
  ):
    raise schema.HoldoutValidationError(
      "V4 selection requires a clean "
      "working tree"
    )

  selection = selector.select_documents(
    pool,
    protocol[
      "randomHoldout"
    ],
    seed,
  )

  if (
    selection[
      "status"
    ]
    != "ok"
  ):
    print(
      json.dumps(
        {
          "status":
            selection[
              "status"
            ],

          "unsatisfied":
            selection[
              "unsatisfied"
            ],

          "stats":
            selection[
              "stats"
            ],
        },
        ensure_ascii=False,
        indent=2,
      )
    )

    raise SystemExit(
      2
    )

  provenance = {
    "protocolSha256":
      schema.sha256_file(
        args.protocol
      ),

    "inventorySha256":
      artifact.get(
        "sourceInventorySha256"
      ),

    "candidatePoolHash":
      schema.canonical_content_pool_hash(
        pool
      ),

    "candidatePoolPathHash":
      schema.sha256_json(
        sorted(
          document[
            "normalizedRelativePath"
          ]
          for document in pool
        )
      ),

    "selectorVersion":
      schema.selector_version_for(
        protocol[
          "protocolVersion"
        ]
      ),

    "selectorSha256":
      schema.sha256_file(
        Path(
          __file__
        )
      ),

    "excludedByReason":
      {},

    **identity,
  }

  manifest = selector.build_manifest(
    protocol,
    provenance,
    selection,
    question_index=None,
    seed=seed,
  )

  manifest[
    "candidatePoolArtifact"
  ] = frame[
    "candidatePoolArtifact"
  ]

  manifest[
    "candidatePoolArtifactSha256"
  ] = actual_file_sha

  manifest[
    "candidatePoolCanonicalJsonSha256"
  ] = actual_canonical_sha

  manifest[
    "candidatePoolFingerprintSetSha256"
  ] = artifact[
    "contentFingerprintSetSha256"
  ]

  manifest[
    "candidatePoolCount"
  ] = len(
    pool
  )

  schema.validate_manifest(
    manifest
  )

  output = Path(
    args.out
  )

  if output.exists():
    raise schema.HoldoutValidationError(
      "V4 selection output already exists; "
      "refusing to overwrite"
    )

  _write_json_lf(
    output,
    manifest,
  )

  print(
    json.dumps(
      {
        "status":
          "ok",

        "out":
          str(
            output
          ),

        "documents":
          len(
            manifest[
              "documents"
            ]
          ),

        "selectionSeed":
          seed,

        "selectedBySource":
          selection[
            "stats"
          ][
            "bySource"
          ],

        "selectedFamilies":
          len(
            selection[
              "stats"
            ][
              "families"
            ]
          ),

        "selectedDistinctYears":
          len(
            selection[
              "stats"
            ][
              "distinctYears"
            ]
          ),

        "coveredEras":
          selection[
            "stats"
          ][
            "coveredEras"
          ],

        "reservedCount":
          selection[
            "reservedCount"
          ],

        "reservedPoolHash":
          selection[
            "reservedPoolHash"
          ],

        "gitCommit":
          identity.get(
            "gitCommit"
          ),

        "selectionCodeState":
          identity.get(
            "selectionCodeState"
          ),
      },
      ensure_ascii=False,
      indent=2,
    )
  )


if __name__ == "__main__":
  main()
