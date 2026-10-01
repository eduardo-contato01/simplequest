# Holdout V4 Neutral Question-Index Triage

## Status

`V4_QUESTION_INDEX_TRIAGE_FROZEN = PASS`

The raw automated question index remains immutable.

This stage only orders neutral manual review.

No correction has been applied.

No question has been selected.

No Ground Truth has been created.

The Auditor has not been executed.

## Raw result

Documents: 48

Raw questions detected: 1024

Raw diagnostic anomalies: 611

Index methods:

- native: 28
- OCR: 20

## Anomaly events

- missing_question_number: 335
- duplicate_question_number: 213
- non_monotonic_numbering: 35
- requires_neutral_verification: 22
- unresolved_question_start: 6

These are diagnostic events, not confirmed independent errors. A single false
question marker can generate multiple downstream anomalies.

## Review tiers

- Tier A: 18 documents
- Tier B: 9 documents
- Tier C: 13 documents
- Tier D: 8 documents

All 48 documents remain in manual neutral review. Tier D contains the
zero-anomaly controls.

## Queue

| Tier | Document | Method | Raw questions | Anomalies | Types |
| --- | --- | --- | ---: | ---: | --- |
| A | doc-0bd82b9dc803 | native | 33 | 105 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-0aa57ea3e5ed | native | 46 | 90 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-3971adb7884f | native | 17 | 28 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-591f3e819d58 | ocr | 10 | 23 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification, unresolved_question_start |
| A | doc-41045384ae4b | native | 40 | 18 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-c573e686e882 | ocr | 27 | 16 | duplicate_question_number, missing_question_number, requires_neutral_verification |
| A | doc-cd0a32a92382 | ocr | 16 | 15 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-a1ddc006ef56 | ocr | 30 | 14 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-6dde932fb681 | ocr | 5 | 12 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification, unresolved_question_start |
| A | doc-9832ec9bb87d | ocr | 20 | 11 | duplicate_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-44ea716ed9b7 | ocr | 12 | 9 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification, unresolved_question_start |
| A | doc-5d61be2ac853 | ocr | 4 | 9 | missing_question_number, requires_neutral_verification, unresolved_question_start |
| A | doc-a272afbae2ca | native | 47 | 6 | duplicate_question_number, missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-b71d45cbb12c | native | 14 | 5 | duplicate_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-e13d030b1f9e | native | 16 | 4 | missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-f4dd01071816 | ocr | 13 | 4 | missing_question_number, non_monotonic_numbering, requires_neutral_verification |
| A | doc-0db5ce524459 | ocr | 1 | 3 | duplicate_question_number, requires_neutral_verification, unresolved_question_start |
| A | doc-c41ddc7b55ec | ocr | 1 | 2 | requires_neutral_verification, unresolved_question_start |
| B | doc-7f0815783d8c | native | 30 | 54 | duplicate_question_number, non_monotonic_numbering |
| B | doc-9236ae9f513e | native | 24 | 31 | duplicate_question_number, missing_question_number, non_monotonic_numbering |
| B | doc-dce5637b3bd7 | native | 20 | 20 | duplicate_question_number |
| B | doc-cef618be31e6 | native | 26 | 16 | duplicate_question_number, missing_question_number, non_monotonic_numbering |
| B | doc-074dd67cbd4a | ocr | 16 | 11 | duplicate_question_number, missing_question_number, non_monotonic_numbering |
| B | doc-56268e79f6bf | ocr | 5 | 8 | missing_question_number, non_monotonic_numbering |
| B | doc-f1c03b7dfa39 | native | 22 | 8 | duplicate_question_number, missing_question_number, non_monotonic_numbering |
| B | doc-bb62e60cf7ed | native | 20 | 5 | duplicate_question_number, non_monotonic_numbering |
| B | doc-1693ea690bbb | native | 16 | 3 | missing_question_number, non_monotonic_numbering |
| C | doc-ad34c4cf7f30 | ocr | 9 | 17 | missing_question_number |
| C | doc-ee51036d2382 | native | 24 | 14 | missing_question_number |
| C | doc-6381aed53bb1 | native | 36 | 11 | duplicate_question_number, missing_question_number |
| C | doc-89561bb8f1fe | ocr | 9 | 11 | missing_question_number |
| C | doc-eefc3d15076e | ocr | 29 | 11 | missing_question_number |
| C | doc-27775227a392 | native | 26 | 4 | missing_question_number |
| C | doc-3fb1e1ce24be | native | 36 | 4 | missing_question_number |
| C | doc-f03e7d17eec1 | native | 15 | 4 | missing_question_number |
| C | doc-03a9e3fe97aa | native | 39 | 1 | missing_question_number |
| C | doc-08d3b1b8b1e8 | native | 39 | 1 | missing_question_number |
| C | doc-143e13dc75ed | ocr | 19 | 1 | missing_question_number |
| C | doc-9e4d161e7bfb | native | 11 | 1 | missing_question_number |
| C | doc-cf6b56e7abd7 | ocr | 19 | 1 | missing_question_number |
| D | doc-1e18e7252399 | native | 21 | 0 | none |
| D | doc-2790a3c9786b | ocr | 20 | 0 | none |
| D | doc-3e395d355d2c | native | 40 | 0 | none |
| D | doc-42af2b3d2b27 | ocr | 20 | 0 | none |
| D | doc-4310686d43a6 | native | 20 | 0 | none |
| D | doc-800c2a22f148 | native | 20 | 0 | none |
| D | doc-b605f7a51fd5 | native | 20 | 0 | none |
| D | doc-c8d6da47c18b | native | 21 | 0 | none |

## Review restrictions

Allowed:

- question numbers
- question starts
- page continuations
- question end pages
- neutral native/OCR text

Forbidden:

- response structure
- alternative count
- alternative labels
- answer keys
- Ground Truth
- Auditor output

## Artifact

`audit/holdout/question-index-v4-review-queue.json`

SHA-256:

`088bb091436bb8a195244da2a037394d0da02f66835e2be228fa029809f92592`

## Next step

Create the neutral visual/manual adjudication package beginning with Tier A.

`MANUAL_ADJUDICATION_PERFORMED = false`

`QUESTION_SELECTION_EXECUTED = false`

`GROUND_TRUTH_CREATED = false`

`AUDITOR_EXECUTED = false`
