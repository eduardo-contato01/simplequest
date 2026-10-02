# Holdout V4 Tier D Review Package

## Status

`V4_TIER_D_REVIEW_PACKAGE_READY = PASS`

Protocol: `holdout-v4`. Tier: `D`. Documents: 8.
Tier A: 18/18 complete. Tier B: 9/9 complete. Tier C: 13/13 complete.
Tier D adjudication has not started.

The document set and order are copied exactly from `reviewQueue` entries with
`reviewTier == "D"` in the frozen `audit/holdout/question-index-v4-review-queue.json`.
No sampling or tier classification was rerun. Tier B/C packages were used only
as structural models; no adjudication decisions were reused.

## Controls

| # | Document | Family | Year | Source | Index method | Pages | Raw questions | Raw anomalies |
| ---: | --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| 1 | doc-1e18e7252399 | CMB | 2013 | text_native | native | 11 | 21 | 0 |
| 2 | doc-2790a3c9786b | CMBel | 2019 | raster | ocr | 19 | 20 | 0 |
| 3 | doc-3e395d355d2c | CMPA | 2025 | text_native | native | 37 | 40 | 0 |
| 4 | doc-42af2b3d2b27 | CMPA | 2019 | raster | ocr | 19 | 20 | 0 |
| 5 | doc-4310686d43a6 | CMBH | 2016 | text_native | native | 11 | 20 | 0 |
| 6 | doc-800c2a22f148 | CMDPII | 2022 | text_native | native | 18 | 20 | 0 |
| 7 | doc-b605f7a51fd5 | CMBH | 2015 | text_native | native | 14 | 20 | 0 |
| 8 | doc-c8d6da47c18b | CMB | 2013 | text_native | native | 11 | 21 | 0 |

Frozen raw diagnostics: 182 questions and zero automated anomaly events.
These are not canonical adjudicated counts. Zero automated anomalies does not
establish completeness or replace human neutral review of the eight controls.

## Integrity and files

Original PDF fingerprints verified: 8/8.
Review copies byte-identical to originals: 8/8.
Physical PDF page counts verified against frozen queue/report metadata: 8/8.
Only PDF metadata was read for page counts; no visual review, OCR or Auditor was
executed.

Tracked package: `audit/holdout/question-index-v4-tier-d-review-package.json`.
SHA256: `f886838926031e43d294a5f35f20392bd03f0a20424cedd9616874e674c9aa35`.

Local review directory: `outputs/audit/holdout/v4-tier-d-review/`.
PDF copies, review context and upload list remain ignored/untracked, following
Tier B/C conventions.

Review context: `outputs/audit/holdout/v4-tier-d-review/review-context.json`.
SHA256: `ed08fa450fbd92218529dac796b27ab39ab010d56319e5cf50000ec755575fec`.

Upload list: `outputs/audit/holdout/v4-tier-d-review/FILES_TO_UPLOAD.txt`.
SHA256: `43156981d85e3ba8ee959b09c70db649fe29fbabd6a25bf06fcc63e3aec6154b`.
The list contains exactly eight PDF copies and the neutral review context.

## Isolation

Allowed: visible question numbering and starts/ends, page continuation, section
transitions, declared item counts, neutral document structure, document
identification and fingerprints.

Forbidden: answer keys/correct answers, Ground Truth, Auditor outputs,
responseMode classification, optionCount, optionLabels, downstream heuristics
and any artifact that could contaminate the holdout.
Auditor V1 architecture remains frozen.

## Preservation

Tier A/B/C artifacts and original PDFs remain unchanged.
Raw neutral question index and tier assignments remain frozen.

`ADJUDICATION_COMPLETE = false`
`MANUAL_TIER_D_ADJUDICATION_PERFORMED = false`
`RAW_QUESTION_INDEX_MODIFIED = false`
`FINAL_QUESTION_INDEX_CREATED = false`
`QUESTION_SELECTION_EXECUTED = false`
`GROUND_TRUTH_CREATED = false`
`AUDITOR_EXECUTED = false`
