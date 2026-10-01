# Holdout V4 Tier C Review Package

## Status

`V4_TIER_C_REVIEW_PACKAGE_READY = PASS`

Protocol: `holdout-v4`. Tier: `C`. Documents: 13.
Tier A: 18/18 complete. Tier B: 9/9 complete.
Tier C adjudication has not started. Tier D remains untouched.

The document set and order are copied exactly from `reviewQueue` entries with
`reviewTier == "C"` in the frozen `audit/holdout/question-index-v4-review-queue.json`.
No new sampling, tier reassignment, or Tier B adjudication decisions were used.

## Documents

| # | Document | Family | Year | Source | Index method | Pages | Raw questions | Raw anomalies |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| 1 | doc-ad34c4cf7f30 | COLÉGIO PÓDION | 2024 | raster | ocr | 14 | 9 | 17 |
| 2 | doc-ee51036d2382 | OUTRAS | 2024 | text_native | native | 8 | 24 | 14 |
| 3 | doc-6381aed53bb1 | CMJF | 2023 | text_native | native | 29 | 36 | 11 |
| 4 | doc-89561bb8f1fe | CMR | 2017 | raster | ocr | 11 | 9 | 11 |
| 5 | doc-eefc3d15076e | CMBH | 2025 | raster | ocr | 39 | 29 | 11 |
| 6 | doc-27775227a392 | CMF | 2022 | text_native | native | 16 | 26 | 4 |
| 7 | doc-3fb1e1ce24be | CMF | 2024 | text_native | native | 25 | 36 | 4 |
| 8 | doc-f03e7d17eec1 | CMPA | 2023 | hybrid | native | 39 | 15 | 4 |
| 9 | doc-03a9e3fe97aa | COLÉGIO SÓLIDO | 2022 | text_native | native | 16 | 39 | 1 |
| 10 | doc-08d3b1b8b1e8 | COLÉGIO SÓLIDO | 2021 | text_native | native | 17 | 39 | 1 |
| 11 | doc-143e13dc75ed | CMBel | 2018 | raster | ocr | 20 | 19 | 1 |
| 12 | doc-9e4d161e7bfb | CMM | 2013 | text_native | native | 12 | 11 | 1 |
| 13 | doc-cf6b56e7abd7 | CMB | 2017 | raster | ocr | 20 | 19 | 1 |

Raw diagnostics: 311 questions and 81 anomaly events. These are not canonical
adjudicated counts or confirmed errors.

## Integrity and files

Original PDF fingerprints verified: 13/13.
Review copies byte-identical to originals: 13/13.
Original PDFs and frozen raw index preserved.

Tracked metadata: `audit/holdout/question-index-v4-tier-c-review-package.json`.
SHA256: `cc32720c0545cd63323c3b70644b16c3b48b3faa196d87371e39a70bb5c558ab`.

Local review directory: `outputs/audit/holdout/v4-tier-c-review/`.
PDF copies and review context remain ignored/untracked, following Tier B convention.

Review context: `outputs/audit/holdout/v4-tier-c-review/review-context.json`.
SHA256: `65a408795facf5f478f4d19dbb2e544f46260db06edea237d1e16a8fb2a13b6e`.

Upload list: `outputs/audit/holdout/v4-tier-c-review/FILES_TO_UPLOAD.txt`.
SHA256: `084b7492ba65368927e678dfd9f13b94d337d17438abd515a97d577c70b4d532`.
It lists exactly the 13 PDF copies and the neutral review context, with no separate
answer keys, Ground Truth, Auditor outputs, or other downstream files.

## Isolation

Allowed: visible question number/start, continuation and final page, visible
section transitions, printed numbering, document-declared item count, and neutral
page/document structure.

Forbidden: answer keys/correct answers, Ground Truth, Auditor output,
responseMode classification, optionCount/optionLabels inference, benchmark
semantic classification, and any other downstream contaminating data.
Auditor V1 architecture remains frozen; no new heuristics or layout rules were
introduced.

## Preservation

`ADJUDICATION_COMPLETE = false`
`MANUAL_TIER_C_ADJUDICATION_PERFORMED = false`
`RAW_QUESTION_INDEX_MODIFIED = false`
`FINAL_QUESTION_INDEX_CREATED = false`
`QUESTION_SELECTION_EXECUTED = false`
`GROUND_TRUTH_CREATED = false`
`AUDITOR_EXECUTED = false`
