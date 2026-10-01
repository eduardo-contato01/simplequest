# Holdout V4 Protocol Freeze

## Status

`V4_PROTOCOL_FROZEN = PASS`

No document selection occurred.
No question selection occurred.
No Ground Truth was created.
The Auditor was not executed.

## Frozen selection design

Seed: `20261001`

Documents: 48

Questions per document: 3

Target questions: 144

| Source | Selected | Reserved |
| --- | ---: | ---: |
| text_native | 32 | 295 |
| raster | 15 | 143 |
| hybrid | 1 | 1 |

The final remaining hybrid document is reserved for the separate Final Blind
Evaluation.

## Diversity constraints

- maximum documents per family: 3
- minimum families: 16
- minimum distinct years: 12
- all four eras required
- no fixed era quota
- no seed search
- no alternate-seed retry
- no silent constraint relaxation

## Development gate

V4 remains the final blind development holdout only if its result does not cause
a substantive Auditor logic change.

If V4 causes a new heuristic, parser/fusion/boundary change, OCR retune,
threshold change, or new blocker, another blind holdout is required before the
Final Blind Evaluation.

## Recovery audit

Three freeze attempts stopped before commit, push, selection, Ground Truth, or
Auditor execution.

The most recent failure was caused by the recovery guard's path parser, not by
the V4 protocol or selection design.

This recovery no longer parses `git status --porcelain` by fixed character
offset. Tracked changes and untracked files are obtained independently.

Schema state before final recovery:

`ALREADY_PATCHED`

Index entry before normalization:

`H scripts/audit_holdout_schema.py`

Index entry after normalization:

`H scripts/audit_holdout_schema.py`

## Hashes

Protocol file SHA-256:

`f70fb425dd17a7a117a02926a8e0c6c7b9e199dc3c3d2640848b5f9a7b325183`

Protocol canonical JSON SHA-256:

`94ff2f2340339de1487c23bf90b05416634f85852db37bdbdc2ef0811ff221bd`

Candidate pool fingerprint-set SHA-256:

`82cc19852f61ca76111680d8f56fbc08bbde563a7b845b5168c34aa513977d63`

## Next stage

The deterministic V4 document selection may now be executed exactly once with
the frozen seed.

`V4_SELECTION_EXECUTED = false`

`GROUND_TRUTH_CREATED = false`

`AUDITOR_EXECUTED = false`
