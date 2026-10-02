# V4 Tier C Neutral Adjudication

Status: COMPLETE

Protocol: `holdout-v4`. Tier: `C`.
Documents adjudicated: 13.
Raw questions in batch: 311.
Canonical questions adjudicated: 430.

## Authority and provenance

The completed human visual review supplied by the operator on 2026-10-02 is
the authority for every question number and page interval. This step only
materialized those decisions; it did not reinterpret PDFs, rerun visual review,
or use OCR to replace human decisions.

Human-source attachment SHA256:
`d1a33898b821afa9dedda805d2a0d86e5a039436674463ac64c391c4d4f6f653`.

Source review-package commit: `2b748255905ae7c2df2fef1e075266231aa862c4`.
Review package: `audit/holdout/question-index-v4-tier-c-review-package.json`.
SHA256: `cc32720c0545cd63323c3b70644b16c3b48b3faa196d87371e39a70bb5c558ab`.

Frozen review context:
`outputs/audit/holdout/v4-tier-c-review/review-context.json`.
SHA256: `65a408795facf5f478f4d19dbb2e544f46260db06edea237d1e16a8fb2a13b6e`.

Tier A/B artifacts are schema/provenance references only and remain unchanged.
The original review package/context remain frozen at their pre-adjudication
state; this adjudication artifact records completion separately.

## Counts

| Document | Raw questions | Canonical questions | Raw anomalies |
| --- | ---: | ---: | ---: |
| doc-ad34c4cf7f30 | 9 | 40 | 17 |
| doc-ee51036d2382 | 24 | 40 | 14 |
| doc-6381aed53bb1 | 36 | 40 | 11 |
| doc-89561bb8f1fe | 9 | 20 | 11 |
| doc-eefc3d15076e | 29 | 40 | 11 |
| doc-27775227a392 | 26 | 30 | 4 |
| doc-3fb1e1ce24be | 36 | 40 | 4 |
| doc-f03e7d17eec1 | 15 | 40 | 4 |
| doc-03a9e3fe97aa | 39 | 40 | 1 |
| doc-08d3b1b8b1e8 | 39 | 40 | 1 |
| doc-143e13dc75ed | 19 | 20 | 1 |
| doc-9e4d161e7bfb | 11 | 20 | 1 |
| doc-cf6b56e7abd7 | 19 | 20 | 1 |

## Identity and boundaries

For all 13 documents, canonical questionNumber equals the printed number.
questionId is `documentId + ":q" + questionNumber`; numbering is sequential
from 1 to the canonical count, with no numbering restart or sequenceRun.

Only these five human-specified questions span multiple pages:

- doc-6381aed53bb1:q2: PDF pages 2-3.
- doc-6381aed53bb1:q3: PDF pages 3-4.
- doc-6381aed53bb1:q5: PDF pages 4-5.
- doc-6381aed53bb1:q16: PDF pages 11-12.
- doc-f03e7d17eec1:q18: PDF pages 20-21.

Every other question has pageStart = pageEnd on the human-specified page.
Cover, base-text, continuation-only, textual-production, draft and blank pages
without a new question were not turned into new questions. Document-specific
neutral notes preserve those human statements.

## Isolation and preservation

No answer key, correct answer, Ground Truth, Auditor output, responseMode,
optionCount/optionLabels inference, benchmark semantic classification or
downstream contaminating data was used. Auditor V1 architecture remains frozen.

Tier A: 18/18 preserved. Tier B: 9/9 preserved.
Tier C adjudication: true. Tier D: not started.
Original PDFs and the raw question index are byte-preserved.

`RAW_QUESTION_INDEX_MODIFIED = false`
`FINAL_QUESTION_INDEX_CREATED = false`
`QUESTION_SELECTION_EXECUTED = false`
`GROUND_TRUTH_CREATED = false`
`AUDITOR_EXECUTED = false`

## Artifact

`audit/holdout/question-index-v4-tier-c-adjudication.json`

SHA256: `61e20f03f2fa8decb55ad61975ed2d3e8cc6812ecf1100e1b481b5e4b0a2aee6`.
