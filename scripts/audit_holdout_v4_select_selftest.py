from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(
  0,
  str(
    ROOT
    / "scripts"
  ),
)

import audit_holdout_schema as schema
import audit_holdout_v4_select as v4
import audit_response_holdout_select as selector


FAILURES = 0


def check(
  name,
  condition,
  detail=None,
):
  global FAILURES

  if condition:
    print(
      "PASS",
      name,
    )
    return

  FAILURES += 1

  print(
    "FAIL",
    name,
    repr(
      detail
    ),
  )


def era_for(index):
  return [
    "2004-2009",
    "2010-2014",
    "2015-2019",
    "2020-2025",
  ][
    index % 4
  ]


def year_for(index):
  return [
    2006,
    2011,
    2017,
    2023,
    2007,
    2012,
    2018,
    2024,
    2008,
    2013,
    2019,
    2025,
    2009,
    2014,
    2016,
    2020,
    2005,
    2010,
    2015,
    2021,
    2004,
    2022,
  ][
    index % 22
  ]


def make_document(
  source,
  family,
  index,
):
  doc_id = (
    f"synthetic-{source}-"
    f"{family}-{index}"
  )

  return {
    "documentId":
      doc_id,

    "canonicalPath":
      f"/synthetic/{doc_id}.pdf",

    "relativePath":
      f"{doc_id}.pdf",

    "normalizedRelativePath":
      f"{doc_id}.pdf",

    "contentFingerprint":
      schema.sha256_text(
        doc_id
      ),

    "duplicatePaths":
      [],

    "family":
      family,

    "year":
      year_for(
        index
      ),

    "era":
      era_for(
        index
      ),

    "series":
      "6",

    "sourceType":
      source,

    "pageCount":
      20,
  }


def main():
  documents = []

  index = 0

  for family_index in range(
    12
  ):
    family = (
      f"N{family_index:02d}"
    )

    for _ in range(
      3
    ):
      documents.append(
        make_document(
          "text_native",
          family,
          index,
        )
      )

      index += 1

  for family_index in range(
    6
  ):
    family = (
      f"R{family_index:02d}"
    )

    for _ in range(
      3
    ):
      documents.append(
        make_document(
          "raster",
          family,
          index,
        )
      )

      index += 1

  for family_index in range(
    2
  ):
    documents.append(
      make_document(
        "hybrid",
        f"H{family_index:02d}",
        index,
      )
    )

    index += 1

  fps = sorted(
    document[
      "contentFingerprint"
    ]
    for document in documents
  )

  source_distribution = dict(
    Counter(
      document[
        "sourceType"
      ]
      for document in documents
    )
  )

  era_distribution = dict(
    Counter(
      document[
        "era"
      ]
      for document in documents
    )
  )

  protocol = {
    "selectionSeed":
      20261001,

    "samplingFrameV4": {
      "eligibleDocuments":
        len(
          documents
        ),

      "contentFingerprintSetSha256":
        schema.reserved_pool_hash(
          fps
        ),

      "sourceDistribution":
        source_distribution,

      "eraDistribution":
        era_distribution,

      "distinctFamilies":
        len({
          document[
            "family"
          ]
          for document in documents
        }),

      "distinctYears":
        len({
          document[
            "year"
          ]
          for document in documents
        }),
    },

    "randomHoldout": {
      "targetDocuments":
        48,

      "questionsPerDocument":
        3,

      "maxDocumentsPerFamily":
        3,

      "minFamilies":
        16,

      "minDistinctYears":
        12,

      "eras": [
        "2004-2009",
        "2010-2014",
        "2015-2019",
        "2020-2025",
      ],

      "sourceQuota": {
        "text_native":
          32,

        "raster":
          15,

        "text_low_quality":
          0,

        "hybrid":
          1,
      },
    },
  }

  artifact = {
    "artifactType":
      "frozen-candidate-pool",

    "protocolVersion":
      "holdout-v4",

    "documentCount":
      len(
        documents
      ),

    "contentFingerprintSetSha256":
      schema.reserved_pool_hash(
        fps
      ),

    "documents":
      documents,
  }

  validated = (
    v4.validate_frozen_candidate_pool(
      protocol,
      artifact,
    )
  )

  check(
    "v4selector.pool.validation",
    len(
      validated
    )
    == len(
      documents
    ),
    len(
      validated
    ),
  )

  check(
    "v4selector.seed",
    v4.resolve_selection_seed(
      protocol,
      None,
    )
    == 20261001,
  )

  override_rejected = False

  try:
    v4.resolve_selection_seed(
      protocol,
      123,
    )

  except schema.HoldoutValidationError:
    override_rejected = True

  check(
    "v4selector.seed.override_rejected",
    override_rejected,
  )

  selection = (
    selector.select_documents(
      documents,
      protocol[
        "randomHoldout"
      ],
      20261001,
    )
  )

  check(
    "v4selector.synthetic.status",
    selection[
      "status"
    ]
    == "ok",
    selection,
  )

  check(
    "v4selector.synthetic.count",
    len(
      selection[
        "documents"
      ]
    )
    == 48,
    len(
      selection[
        "documents"
      ]
    ),
  )

  check(
    "v4selector.synthetic.sources",
    selection[
      "stats"
    ][
      "bySource"
    ]
    == {
      "text_native": 32,
      "raster": 15,
      "hybrid": 1,
    },
    selection[
      "stats"
    ][
      "bySource"
    ],
  )

  check(
    "v4selector.synthetic.families",
    len(
      selection[
        "stats"
      ][
        "families"
      ]
    )
    >= 16,
    selection[
      "stats"
    ][
      "families"
    ],
  )

  check(
    "v4selector.synthetic.years",
    len(
      selection[
        "stats"
      ][
        "distinctYears"
      ]
    )
    >= 12,
    selection[
      "stats"
    ][
      "distinctYears"
    ],
  )

  check(
    "v4selector.synthetic.eras",
    set(
      selection[
        "stats"
      ][
        "coveredEras"
      ]
    )
    == {
      "2004-2009",
      "2010-2014",
      "2015-2019",
      "2020-2025",
    },
    selection[
      "stats"
    ][
      "coveredEras"
    ],
  )

  tampered = {
    **artifact,
    "contentFingerprintSetSha256":
      "bad",
  }

  rejected = False

  try:
    v4.validate_frozen_candidate_pool(
      protocol,
      tampered,
    )

  except schema.HoldoutValidationError:
    rejected = True

  check(
    "v4selector.tampered.rejected",
    rejected,
  )

  if FAILURES:
    raise SystemExit(
      1
    )

  print(
    "V4_SELECTOR_SELFTEST = PASS"
  )


if __name__ == "__main__":
  main()
