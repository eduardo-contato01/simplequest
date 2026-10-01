# Holdout V4 Raw Question Index Freeze

## Status

`V4_RAW_QUESTION_INDEX_FROZEN = PASS`

The frozen neutral question indexer was executed once over all 48 selected V4
documents.

No anomaly content was reviewed before this raw freeze.

No manual adjudication was performed.

No questions were selected.

No Ground Truth was created.

The Auditor was not executed.

## Execution

Attempt: 1

Source commit:

`57bcb08502696d158822e0adcaf0284329977282`

Indexer Git blob:

`25ca4665708ba0ad8850f889f5ea0d71e3ff4025`

Method:

`neutral-question-index-v1`

OCR configuration:

`tesseract / 160 dpi / psm 11 / por+eng`

## Raw index

File:

`audit/holdout/question-index-v4-raw.json`

File SHA-256:

`36549f5067f3236fee90112fd1df63fb30c5ca5445ebec77ca139be41d722f79`

Canonical JSON SHA-256:

`6484786953adec29fed77de9a842880d9f359682ff1ceb914d2acb8425794b18`

Documents:

48

The document set and all content fingerprints match the frozen V4 document
selection.

Only neutral question fields are present:

- questionId
- questionNumber
- pageStart
- pageEnd

## Raw diagnostic report

Original ignored output:

`outputs/audit/holdout/v4-question-index-raw-report.json`

Frozen tracked copy:

`audit/holdout/question-index-v4-raw-report.json`

SHA-256:

`25a63bcba067e44fae352b185ec4a5d93791b8bbb04df930a1d96f86e748f390`

The two report files are byte-identical.

## OCR caches

Pre-existing selected-document cache directories: 0

Generated selected-document cache directories during raw indexing:
20

## Methodological state

Raw anomaly content inspected before freeze: false

Manual adjudication performed: false

Question selection executed: false

Ground Truth created: false

Auditor executed: false

Indexer rerun: false

## Next step

With the raw automated result now immutable, its neutral indexing anomalies may
be inspected and adjudicated without using response structure, answer keys,
Ground Truth, or Auditor output.

`QUESTION_INDEX_RAW_EXECUTED = true`

`V4_RAW_QUESTION_INDEX_FROZEN = true`

`QUESTION_SELECTION_EXECUTED = false`

`GROUND_TRUTH_CREATED = false`

`AUDITOR_EXECUTED = false`
