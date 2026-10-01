from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_schema as schema


FAILURES = 0


def check(name, condition, detail=None):
  global FAILURES

  if condition:
    print("PASS", name)
    return

  FAILURES += 1
  print("FAIL", name, repr(detail))


def main():
  protocol = json.loads(
    (
      ROOT
      / "audit"
      / "holdout"
      / "protocol-v4.json"
    ).read_text(
      encoding="utf-8"
    )
  )

  pool = json.loads(
    (
      ROOT
      / "audit"
      / "holdout"
      / "candidate-pool-v4.json"
    ).read_text(
      encoding="utf-8"
    )
  )

  try:
    schema.validate_protocol(
      protocol
    )
    valid = True
    validation_error = None

  except Exception as exc:
    valid = False
    validation_error = repr(exc)

  check(
    "v4.protocol.validate",
    valid,
    validation_error,
  )

  check(
    "v4.selector.version",
    schema.selector_version_for(
      "holdout-v4"
    ) == "holdout-v4",
    schema.selector_version_for(
      "holdout-v4"
    ),
  )

  quota = protocol[
    "randomHoldout"
  ][
    "sourceQuota"
  ]

  check(
    "v4.quota.total",
    sum(
      int(value)
      for value in quota.values()
    ) == 48,
    quota,
  )

  check(
    "v4.quota.native",
    quota[
      "text_native"
    ] == 32,
    quota,
  )

  check(
    "v4.quota.raster",
    quota[
      "raster"
    ] == 15,
    quota,
  )

  check(
    "v4.quota.hybrid",
    quota[
      "hybrid"
    ] == 1,
    quota,
  )

  check(
    "v4.hybrid.reserve",
    pool[
      "sourceDistribution"
    ][
      "hybrid"
    ]
    - quota[
      "hybrid"
    ]
    == 1,
    quota,
  )

  check(
    "v4.family.cap",
    protocol[
      "randomHoldout"
    ][
      "maxDocumentsPerFamily"
    ] == 3,
    protocol[
      "randomHoldout"
    ],
  )

  check(
    "v4.minimum.families",
    protocol[
      "randomHoldout"
    ][
      "minFamilies"
    ] >= 16,
    protocol[
      "randomHoldout"
    ],
  )

  check(
    "v4.minimum.years",
    protocol[
      "randomHoldout"
    ][
      "minDistinctYears"
    ] >= 12,
    protocol[
      "randomHoldout"
    ],
  )

  check(
    "v4.seed.fixed",
    protocol[
      "selectionSeed"
    ] == 20261001,
    protocol[
      "selectionSeed"
    ],
  )

  check(
    "v4.no.seed.search",
    protocol[
      "constraintPolicy"
    ][
      "noSeedSearch"
    ] is True,
    protocol[
      "constraintPolicy"
    ],
  )

  check(
    "v4.final.gate",
    "new blind holdout"
    in protocol[
      "finalDevelopmentGate"
    ][
      "ifAuditorLogicChangesAfterV4Reveal"
    ],
    protocol[
      "finalDevelopmentGate"
    ],
  )

  if FAILURES:
    raise SystemExit(1)

  print(
    "V4_PROTOCOL_SELFTEST = PASS"
  )


if __name__ == "__main__":
  main()
