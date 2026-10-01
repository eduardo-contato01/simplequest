# Holdout V4 Question Index Protocol Freeze

## Status

`V4_QUESTION_INDEX_PROTOCOL_FROZEN = PASS`

Document selection is already frozen.

Question selection has not occurred.

Ground Truth has not been created.

The Auditor has not been executed.

## Source documents

Selected documents: 48

Source files present: 48/48

Source SHA-256 fingerprints matched: 48/48

Pre-existing OCR caches for selected documents: 0

## Neutral question indexer

Implementation:

`scripts/audit_holdout_question_index.py`

Git blob:

`25ca4665708ba0ad8850f889f5ea0d71e3ff4025`

Local file SHA-256:

`04262953d3949651bd8cf4c236cbd5e7b4e85b64c34db77033c19717824b5d3c`

Method:

`neutral-question-index-v1`

OCR fallback:

`{"engine": "tesseract", "dpi": 160, "psm": 11, "lang": "por+eng"}`

This OCR configuration belongs only to neutral question-number indexing. It does
not modify the Auditor execution OCR configuration.

## Permitted index information

Only:

- questionId
- questionNumber
- pageStart
- pageEnd

No response structure, option count, option labels, layout, marker style,
content kind, correct answer, answer key, or Auditor output may be used.

## Adjudication

The automated raw index must be frozen before manual correction.

Manual adjudication is allowed only for neutral numbering and page-boundary
issues.

Any correction must preserve provenance.

The indexer itself may not be retuned from V4 content.

## Question selection

Questions per document: 3

Seed: 20261001

Question selection is forbidden until the final neutral question index has been
frozen.

## Artifact hashes

Protocol file SHA-256:

`e46b03d48f56e25b6e5c4e80693a2380dee7981b476b76e27292cdf34036f05a`

Protocol canonical JSON SHA-256:

`cee6620fe6952db88c5e748da66598c36fb236ef5c23412a96a4e69f3ec9b745`

## Next stage

Run the frozen neutral indexer over the 48 selected documents and freeze its raw
output before inspecting or correcting anomalies.

`QUESTION_INDEX_RAW_EXECUTED = false`

`QUESTION_SELECTION_EXECUTED = false`

`GROUND_TRUTH_CREATED = false`

`AUDITOR_EXECUTED = false`
