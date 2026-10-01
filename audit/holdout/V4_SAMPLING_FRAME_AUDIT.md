# Holdout V4 Sampling Frame Audit

## Status

`V4_SAMPLING_FRAME_FROZEN = PASS`

No random document selection occurred.
No question selection occurred.
No selection seed was chosen.
No Ground Truth was created.
The Auditor was not executed.

## Base

Main:

`b33b98465f3f2b58e4aefc357efa598d8364c22b`

V3 result freeze:

`b3082e093df58d8054f1acda61183d52e5b1a605`

## Historical integrity

The V3 protocol, candidate pool, and final manifest were verified by exact Git
blob identity against the V3 result-freeze commit.

This avoids platform-dependent working-tree byte differences such as LF/CRLF.

## Derivation

V3 candidate documents: 535

V3 revealed documents removed: 48

V4 eligible documents: 487

Expected V3 reserved count: 487

Expected V3 reserved set hash:

`82cc19852f61ca76111680d8f56fbc08bbde563a7b845b5168c34aa513977d63`

Actual V4 set hash:

`82cc19852f61ca76111680d8f56fbc08bbde563a7b845b5168c34aa513977d63`

## Contamination

- V1 overlap: 0
- V2 overlap: 0
- V3 overlap: 0
- Development overlap: 0
- Duplicate content fingerprints: 0
- Duplicate document IDs: 0

## Source distribution

| Source | Documents |
| --- | ---: |
| hybrid | 2 |
| raster | 158 |
| text_native | 327 |

## Era distribution

| Era | Documents |
| --- | ---: |
| 2004-2009 | 35 |
| 2010-2014 | 109 |
| 2015-2019 | 191 |
| 2020-2025 | 152 |

Distinct families: 24

Distinct years: 22

Year range: 2004 to 2025

## V4 candidate pool

File:

`audit/holdout/candidate-pool-v4.json`

File SHA-256:

`cdee45a7273c152a4677dd4074a93b974fae178c0f234f134efc1fb3420b774a`

Canonical JSON SHA-256:

`45b14a93d8021ad4300044aa2fabbe6f2c813d4cf9b3cc69790f0b24a52a0a2b`

Fingerprint-set SHA-256:

`82cc19852f61ca76111680d8f56fbc08bbde563a7b845b5168c34aa513977d63`

## Next step

Only after reviewing this distribution will the V4 protocol, quotas, constraints,
and selection seed be frozen.

`V4_PROTOCOL_FROZEN = false`

`V4_SELECTION_EXECUTED = false`

`AUDITOR_EXECUTED = false`
