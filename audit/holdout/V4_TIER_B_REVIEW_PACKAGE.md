# Holdout V4 Tier B Review Package

## Status

`V4_TIER_B_REVIEW_PACKAGE_READY = PASS`

Tier A neutral adjudication is complete for all 18 Tier A documents.

This package contains all nine Tier B documents. No Tier B adjudication has
occurred yet.

## Documents

| # | Document | Family | Year | Source | Index method | Pages | Raw questions | Raw anomalies |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| 1 | doc-7f0815783d8c | CMC | 2012 | text_native | native | 9 | 30 | 54 |
| 2 | doc-9236ae9f513e | CMSP | 2019 | text_native | native | 12 | 24 | 31 |
| 3 | doc-dce5637b3bd7 | CMT | 2016 | text_native | native | 16 | 20 | 20 |
| 4 | doc-cef618be31e6 | CMRJ | 2022 | text_native | native | 17 | 26 | 16 |
| 5 | doc-074dd67cbd4a | CMSM | 2013 | text_native | ocr | 19 | 16 | 11 |
| 6 | doc-56268e79f6bf | CMSM | 2018 | raster | ocr | 22 | 5 | 8 |
| 7 | doc-f1c03b7dfa39 | CMF | 2020 | text_native | native | 17 | 22 | 8 |
| 8 | doc-bb62e60cf7ed | CMSM | 2023 | text_native | native | 33 | 20 | 5 |
| 9 | doc-1693ea690bbb | CMT | 2023 | text_native | native | 21 | 16 | 3 |

## Integrity

Source PDFs verified by frozen fingerprints: 9/9

Review copies byte-identical to source: 9/9

Review context SHA-256:

`f196e3bc5dd1f859df36be2739cf9d83c9f5ae316c0996ab8caefcd8f64eb933`

Tracked package metadata SHA-256:

`292c4e1b3edb85952d60b25f0aea8159dbc4f93f92dd291bf48ed9ac1a4bbafd`

## Review focus

Tier B is dominated by sequence-level problems:

- duplicate question numbers
- missing question numbers
- non-monotonic numbering
- high anomaly volume

These diagnostics are not assumed to be true errors. The original PDFs must
decide the canonical neutral numbering and page boundaries.

## Restrictions

No response semantics, answer keys, Ground Truth or Auditor output may be used.

## Preservation

`MANUAL_TIER_B_ADJUDICATION_PERFORMED = false`

`FINAL_QUESTION_INDEX_CREATED = false`

`QUESTION_SELECTION_EXECUTED = false`

`GROUND_TRUTH_CREATED = false`

`AUDITOR_EXECUTED = false`
