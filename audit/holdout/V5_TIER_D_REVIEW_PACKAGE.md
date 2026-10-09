# Holdout V5 — Tier D neutral review package

V5_TIER_D_NEUTRAL_REVIEW_PACKAGE_PREPARATION=PASS

## Scope and publication

Branch `audit/holdout-v5-blind`; source HEAD
`fa7648a41e0b298a2f816e0582afb9272112cad0`.

Preparation only: eight complete binary copies, neutral review-context, three
review lists and one versioned package. Formal freeze and `TierDPrepared=true`
take effect only after the introducing commit, successful push and identical
local/remote SHA. No batch started; no visual inspection, PDF parser, census
rerun, render, text extraction, OCR, indexer or adjudication performed.

[Package JSON](question-index-v5-tier-d-review-package.json)
SHA256: `2f0a37b84525f8e3b6197dd4c7da4baed1544384937be5649507063ac2156c2c`.

## Immutable Tier D order and operational batches

Only frozen queue entries with `reviewTier == "D"`, literal global positions
41–48. No reranking, convenience filtering, population selection, replacement,
quota change or document leakage. All eight rows are unchanged in historical
and effective manifests and remain in the eligible effective population.

`reviewBatchAssignmentRule=first_5_then_last_3_in_frozen_tier_d_order`.

The split uses frozen positions and physical page counts before visual review,
solely to balance operational page workload. It does not alter tiers, priority,
selection, quotas or adjudication policy. No additional copies per batch.

| D / global / batch-order | documentId | Pages | Raw | Automatic events | Method |
| --- | --- | ---: | ---: | ---: | --- |
| 1 / 41 / 01-1 | v5-doc-05c35f7183da4927 | 12 | 20 | 0 | native |
| 2 / 42 / 01-2 | v5-doc-0d7bc5575df13886 | 10 | 20 | 0 | native |
| 3 / 43 / 01-3 | v5-doc-1b6b371a30f5cd22 | 19 | 24 | 0 | native |
| 4 / 44 / 01-4 | v5-doc-34e3910f5e106aae | 7 | 12 | 0 | native |
| 5 / 45 / 01-5 | v5-doc-80e01b1d6082d26b | 25 | 24 | 0 | native |
| 6 / 46 / 02-1 | v5-doc-9b28d28efbbf0354 | 19 | 30 | 0 | native |
| 7 / 47 / 02-2 | v5-doc-a7256b9befdea91b | 22 | 24 | 0 | native |
| 8 / 48 / 02-3 | v5-doc-c3bf2d29c7e1d9e8 | 20 | 20 | 0 | native |
| Total | Eight documents | 134 | 174 | 0 | native8 / ocr0 |

Source types: `text_native=8`. Raw identities, question numbers, page ranges
and empty anomaly arrays are copied exactly from frozen raw index/report.
No boundaries corrected, canonical identities added or question counts certified.

| Batch | D positions | Global positions | Documents | Pages | Raw | Events |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 01 | 1–5 | 41–45 | 5 | 73 | 100 | 0 |
| 02 | 6–8 | 46–48 | 3 | 61 | 74 | 0 |

## Binary integrity and local ignored artifacts

All eight canonical paths were taken directly from the queue/effective manifest,
not reconstructed from IDs. Complete source SHA256 equals frozen fingerprint.
Source, queue, manifests, report and existing two-reader census agree on physical
page counts. Existing census bindings were verified; no PDF parser/census rerun.

Single byte-identical complete copies under
`outputs/audit/holdout/v5-tier-d-review/copies/`:

| D order | Copy basename | Source SHA256 = complete copy SHA256 |
| --- | --- | --- |
| 1 | 01__v5-doc-05c35f7183da4927.pdf | `05c35f7183da4927c12b2ae2845f8c2b5e74df2591dd7eabaf63c48ca666223f` |
| 2 | 02__v5-doc-0d7bc5575df13886.pdf | `0d7bc5575df13886e7269106b265133d9f1286fca97b8a035e34890a20b98d6e` |
| 3 | 03__v5-doc-1b6b371a30f5cd22.pdf | `1b6b371a30f5cd22dfc5ee6e0d24a6cce1f33215aaf0164ebac7d62c9d86628b` |
| 4 | 04__v5-doc-34e3910f5e106aae.pdf | `34e3910f5e106aae9ad6f03efcc3456743312f2f7d08c6ded9bfa517c4885e3d` |
| 5 | 05__v5-doc-80e01b1d6082d26b.pdf | `80e01b1d6082d26b6b022497e81a00b5ebb47e8f0a71c87b9cb17928fb4aa575` |
| 6 | 06__v5-doc-9b28d28efbbf0354.pdf | `9b28d28efbbf03544b7f805f7b84040c174148e10f132e3ff143161c81ee7b60` |
| 7 | 07__v5-doc-a7256b9befdea91b.pdf | `a7256b9befdea91bb320dce88545d7ddafd85cd3d52e46ce4e27b9ec863c00d2` |
| 8 | 08__v5-doc-c3bf2d29c7e1d9e8.pdf | `c3bf2d29c7e1d9e8a8ad05f64f313fa8b92bccebea2e90d5dc1d8a6b363faed2` |

Every source/copy pair was compared directly byte by byte and hashed in full.
No source or copy opened for page/content inspection; all pages retained.

Ignored artifacts under `outputs/audit/holdout/v5-tier-d-review/`:

- `review-context.json`: only eight D documents; global/tier/manifest/batch
  positions, neutral metadata and paths, full fingerprints, method, pages,
  raw counts, exact original rawQuestions/rawAnomalies, copy paths/hashes and
  frozen source provenance. No canonical decisions or response-bearing data.
- `FILES_TO_REVIEW.txt`: eight lines in frozen order.
- `FILES_TO_REVIEW_BATCH_01.txt`: exactly the first five lines.
- `FILES_TO_REVIEW_BATCH_02.txt`: exactly the last three lines.

Lists are complete and disjoint; every line records position, document,
batch order, copy, pages, raw and events. No ignored file or PDF staged.
No renders, adjudication notes, new caches or execution scripts created.

## Mandatory policy for future authorized review

**Tier D must not be approved merely because the raw index has zero anomalies.**

Every physical page must be visually inspected in a future separately authorized
adjudication: real starts, printed numbers, sections, numbering runs, linked
continuations and ends, incidental administrative numbers, final pages, annexes,
unrecognized independent identities and artificially long raw final boundaries.
At least three independent fully adjudicable questions per document must be
proved then. Canonical Tier D count is unknown; minimum-three is not certified now.

These unchanged raw proposals deserve critical future checks, not an allegation
of confirmed anomaly:

| Global document | Raw proposal | Proposed physical pages |
| --- | --- | --- |
| 44 | q12 | 1–7 |
| 45 | q24 | 21–25 |
| 47 | q24 | 19–22 |
| 48 | q20 | 18–20 |

None of those pages was opened now. Allowed evidence is exclusively neutral
identity/structure: own headers/numbers, real starts, linked continuation/end,
physical positions, section transitions and structural organization. Existing
neutral native/OCR text may support future review under the frozen policy.

Forbidden: responseMode, optionCount, optionLabels, markerStyle/response-marker
classification, alternatives as identity evidence, answer keys, correct answers,
GT, Auditor predictions/output/metrics or convenience-based document choice.
No permitted visual evidence exercised during preparation; no OCR/indexer tuning.

## Prior tiers and post-freeze provenance

Tiers A/B/C are adjudicated and byte-preserved; no previous question re-adjudicated
or PDF reopened. Published counts transported, not a new canonical consolidation:

| Tier | Documents | Effective pages | Canonical | Unresolved |
| --- | ---: | ---: | ---: | ---: |
| A | 22 | 330 | 1370 | 0 |
| B | 4 | 92 | 220 | 0 |
| C | 14 | 185 | 364 | 0 |

Tier C Batch01=7/89/174 and Batch02=7/96/190; both published and intact.
Tier C retains 279 raw / 73 automatic events / 11 multipage questions.
No new global 48-document canonical index created.

All historical caveats remain mandatory for future derivatives:

- Source-incomplete decisions: unavailable source metadata retained; no fabricated
  identities/boundaries or completeness certification.
- Tier A Batch02 doc3: original integrity inconclusive; scope remains
  frozen_available_pdf_content, without original-examination certification.
- Doc10: historical pageCount1 / effective21 under frozen pagination erratum.
- Doc11: same-stratum, original ranking2 replacement under post-freeze,
  performance-blind addendum; effective R1 population change explicit, historical
  unresolved source/checkpoints preserved; no selector rerun or retroactive
  preregistration claim.
- Replacement sizeBytes182017 authoritative; pdfinfoReportedFileSize0 remains
  nonblocking technical divergence, cause undetermined, not automatic corruption.

Full path/SHA256 bindings in preservedPostFreezeProvenance and
additionalFrozenBindings transport the rules, decisions, errata, supplemental
artifacts and historical checkpoints unchanged. No new methodological exception.

## SHA256 bindings

Hashes refer to actual filesystem bytes, not Git blob identifiers.
New text artifacts are UTF-8 without BOM / LF.

| Artifact | SHA256 |
| --- | --- |
| Package JSON | `2f0a37b84525f8e3b6197dd4c7da4baed1544384937be5649507063ac2156c2c` |
| review-context.json | `bb1630214f46df213ad98feb3b183c78e6149c254de3c18f319f74fb3c7e89d3` |
| FILES_TO_REVIEW.txt | `4b08580fe3016e8243f2f66a2b12a9e9823719c95783695e1f4fdff326330118` |
| FILES_TO_REVIEW_BATCH_01.txt | `9901b55c1ac228efdc2f789d50097a8951f0b0c27000b159d996ed4d83dbe695` |
| FILES_TO_REVIEW_BATCH_02.txt | `837fb437e21946215977f641377bbd0f37a632efb140c4897da37371add39062` |
| audit/holdout/PROTOCOL_V5.md | `77f8bb06d7c8eadba79c7ef70a580eebeff2d74f324017ae8e220f11bea9bb95` |
| audit/holdout/question-index-v5-review-queue.json | `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b` |
| audit/holdout/question-index-v5-raw.json | `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84` |
| audit/holdout/question-index-v5-raw-report.json | `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f` |
| audit/holdout/manifest-v5-documents-frozen.json | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| audit/holdout/manifest-v5-documents-effective-r1.json | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |
| audit/holdout/v5-eligible-document-universe.json | `dd64269956de6c7210fe0e8cc4cbb23dc799925adefa4c5e6dd603ff997c5933` |
| outputs/audit/holdout/v5-page-count-census.json | `f27ac3cd5e0c3b1f80667ed0ae9b8565794b16cddaccee010c7d9a6b283acc7f` |
| audit/holdout/question-index-v5-tier-a-batch-01-adjudication.json | `e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770` |
| audit/holdout/question-index-v5-tier-a-batch-02-adjudication.json | `b2447bf2a0d86e231480902ae26ddd6dcc21ecb58d84648e432ccd5355df0bf3` |
| audit/holdout/question-index-v5-tier-b-adjudication.json | `74e70b49127776451369b16d7642e188cb42182c67c27644b03c3aad37d57e66` |
| audit/holdout/question-index-v5-tier-b-review-package.json | `e3936b66d71a31652d811e26854073d2b6fcf60cfc0e8d6188d1090223bfc4c0` |
| audit/holdout/question-index-v5-raw.provenance.json | `7a69f89b29143c1887a6ad104cf01aa0f187b9aec73f7dfdd3b2bd749903c3b2` |
| audit/holdout/question-index-v5-tier-c-review-package.json | `e5b51ac600e65564aecd7c9f4178212c108354817ad95805a97dace1883e1ced` |
| audit/holdout/question-index-v5-tier-c-batch-01-adjudication.json | `2d39dfe43f0b96c11336e6fce0b29aa34cba65f4691f555310676b27329720ce` |
| audit/holdout/question-index-v5-tier-c-batch-02-adjudication.json | `03ccad0a3cf9cf35b31f479b31379f6d264365e579d40270f417c5444fa39883` |

Additional complete bindings and historical caveats are in the JSON; all checked
against their actual local frozen bytes.

## Preparation gates and preservation

PASS: branch/source HEAD/local-remote equality; clean preflight/stage;
eight unique D IDs/fingerprints; global41–48 and literal order; 134pages/174raw/
zero automatic events; native8/ocr0/text_native8; eight sources present and
fingerprints correct; eight exact complete copies; unchanged raw identities and
ranges; matching existing census; no duplicate/tier leakage; batches5+3,
complete/disjoint lists; valid neutral context; all full source/list/context/copy
bindings reconciled; no page/content inspection or adjudication.

Existing preservation mechanism reused without a new snapshot/inventory file.
5380 binding paths hashed in preflight, representing 5376 distinct files.
The bindings cover 5284 paths from existing preservation manifests/published
incremental bindings (including Tier C Batch02 artifacts and checkpoint), plus
96 pre-existing Batch02 renders hashed in memory. Four absolute/relative aliases
of the same Tier B copies are counted once as files; all bindings passed.
For publication, 5372 distinct protected files remain byte-identical; four authorized
documentation files retain their entire historical byte prefixes with append-only
updates. The 96 render hashes establish this step's pre/post preservation, not
an independent earlier immutable freeze. They were hashed, never visually opened.

Coverage preserves V1–V4, Patch05C1/indexer/Auditor functional code, V5 population/
manifests/raw/report/queue, Tiers A/B/C, packages/decisions/errata/checkpoints,
PDFs, copies and existing caches/renders. Functional baseline diff is empty.
Git configuration/autocrlf and historical line endings remain unchanged;
no .gitattributes or frozen file overwritten.

## State and mandatory STOP

```text
TierAComplete=true
TierBAdjudicated=true
TierCAdjudicated=true
TierCBatch01Adjudicated=true
TierCBatch02Adjudicated=true
TierDPrepared=true (effective only after publication)
TierDAdjudicated=false
PhaseBComplete=false
canonicalQuestionCountKnown=false
minimumThreeCertified=false
visualReview=false
adjudication=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
groundTruthStarted=false
auditorExecuted=false
metricsSeen=false
merge=false
```

One introducing commit: `audit: freeze v5 tier d neutral review package`.
Only package JSON/Markdown and authorized incremental CONTEXTO/factual brain
updates staged. Freeze requires push plus matching remote SHA and clean worktree.

STOP after publication. Next separate task:
**V5 Tier D Batch01 neutral visual adjudication**, NOT STARTED.
No Batch01/02 review, global final index, 144-question selection, GT, Auditor,
metrics or merge in this execution.
