# Holdout V5 — Tier C neutral review package

V5_TIER_C_NEUTRAL_REVIEW_PACKAGE_PREPARATION=PASS

## Scope and publication

Branch `audit/holdout-v5-blind`; source HEAD `bec7b817f1d05122712dd81286f39fde80f1d59e`.
Preparation ONLY: one package for14documents, with two deterministic operational
batches frozen before visual inspection. Formal freeze requires its introducing
commit, successful push and confirmation of equal local/remote SHA.
No PDF parser, census rerun, render, page/content inspection, text extraction,
new OCR, indexer, visual adjudication or interpretation of raw anomalies.

## Frozen order and operational batches

Select exclusively `reviewQueue` entries with `reviewTier == "C"`, in the
literal frozen order, global27–40. No ranking, filtering, redistribution,
document selection or substitution. All14rows are unchanged in historical/effective
manifests; every document remains eligible, unreplaced and
`pending_neutral_visual_review`.

`reviewBatchAssignmentRule=first_7_then_last_7_in_frozen_tier_c_order`.
Batches are only operational review units, not new quotas or populations.
No canonical count or minimum-three certification is made.

| C / global / batch-order | documentId | Pages | Raw | Automatic events | Frozen method |
| --- | --- | ---: | ---: | ---: | --- |
| 1 / 27 / 01-1 | v5-doc-906c5ae29d59a1ff | 15 | 20 | 19 | native |
| 2 / 28 / 01-2 | v5-doc-91b5252bd14b8900 | 16 | 12 | 13 | native |
| 3 / 29 / 01-3 | v5-doc-675affeba8d87308 | 12 | 10 | 10 | native |
| 4 / 30 / 01-4 | v5-doc-2442b4ab742e42f2 | 10 | 13 | 8 | ocr |
| 5 / 31 / 01-5 | v5-doc-d12896e095155245 | 17 | 10 | 4 | ocr |
| 6 / 32 / 01-6 | v5-doc-3a0c4b28948e4a30 | 8 | 21 | 3 | native |
| 7 / 33 / 01-7 | v5-doc-47ff0591259f48eb | 11 | 17 | 3 | ocr |
| 8 / 34 / 02-1 | v5-doc-cb4e2c7c9e714d00 | 19 | 26 | 3 | ocr |
| 9 / 35 / 02-2 | v5-doc-2300b505b11855a2 | 7 | 18 | 2 | native |
| 10 / 36 / 02-3 | v5-doc-429b811d62a29a28 | 17 | 18 | 2 | ocr |
| 11 / 37 / 02-4 | v5-doc-bc5d90aa69fa3416 | 12 | 17 | 2 | native |
| 12 / 38 / 02-5 | v5-doc-c6d6158a42ac379f | 9 | 18 | 2 | native |
| 13 / 39 / 02-6 | v5-doc-78d5d0d89420b8d3 | 15 | 39 | 1 | native |
| 14 / 40 / 02-7 | v5-doc-9e5595dac9eb75e3 | 17 | 40 | 1 | native |
| Total | 14documents | 185 | 279 | 73 | native9 / ocr5 |

| Batch | C positions | Global positions | Documents | Pages | Raw | Events |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 01 | 1–7 | 27–33 | 7 | 89 | 103 | 60 |
| 02 | 8–14 | 34–40 | 7 | 96 | 176 | 13 |

The73events are31duplicate_question_number and42missing_question_number
automatic diagnostics, not confirmed defects, missing-source certifications or
Auditor metrics. SourceTypes=text_native9/raster5. Raw question identities,
numbers and ranges and raw anomaly objects/order remain unchanged.

The raw index carries documentId on each anomaly; the per-document report uses
the containing row as its envelope. After comparing that envelope convention,
all event data agree; context retains the raw-index objects exactly, including
documentId. No event or question was corrected, filtered or normalized.

## Binary integrity and existing census

Canonical paths and full fingerprints were extracted from the frozen queue and
manifest, never reconstructed from abbreviated IDs. Sources exist14/14;
binary source hashes match14/14. Queue, manifests, raw report and frozen
two-reader census page counts agree14/14. Existing census reports both readers
agree and no mismatch for these14documents. No new PDF parsing/census was needed.
None belongs to A/B/D or the historical/replacement doc11 slot.

Single complete copies per document, no duplicate batch copies:
`outputs/audit/holdout/v5-tier-c-review/copies/`.

| C order | Copy basename | Source SHA256 = full copy SHA256 |
| --- | --- | --- |
| 1 | 01__v5-doc-906c5ae29d59a1ff.pdf | `906c5ae29d59a1ff734fd548b7ecd5552cdaab69a0c343496fab4b576f50f72b` |
| 2 | 02__v5-doc-91b5252bd14b8900.pdf | `91b5252bd14b8900e1a6d61519bff82687312d2c7b76e28cb8bb0247f58a97cf` |
| 3 | 03__v5-doc-675affeba8d87308.pdf | `675affeba8d87308980a7e0d328616a1461538ab1bf4f1c2f556aba549078e12` |
| 4 | 04__v5-doc-2442b4ab742e42f2.pdf | `2442b4ab742e42f29fccf524f47f841b7bf2592938c0fd528e6b51c99f952134` |
| 5 | 05__v5-doc-d12896e095155245.pdf | `d12896e095155245ce24bf2df686b56797c6f9e41e7d5ec27f7e5c2eeaf62a9c` |
| 6 | 06__v5-doc-3a0c4b28948e4a30.pdf | `3a0c4b28948e4a30c92778da2ef70afef78740b77295639056ee697e9333c6e2` |
| 7 | 07__v5-doc-47ff0591259f48eb.pdf | `47ff0591259f48eb52fcd70701aa87fa57010d632b8fda9d796bb2ce5ef2c9cf` |
| 8 | 08__v5-doc-cb4e2c7c9e714d00.pdf | `cb4e2c7c9e714d00249004ccfa6d5a29b461ccb978c1535c27f88122c0d4cca8` |
| 9 | 09__v5-doc-2300b505b11855a2.pdf | `2300b505b11855a2b555ea8b24e792948072340d5ceb4e4e7efce1b326784970` |
| 10 | 10__v5-doc-429b811d62a29a28.pdf | `429b811d62a29a28c9e2dfb8f89afc95fb0afa0d0529fe9e67a205dd1aa00605` |
| 11 | 11__v5-doc-bc5d90aa69fa3416.pdf | `bc5d90aa69fa3416e2af5364542d5d6bbb4ba3b8550eca81aeeab2251aa7dd4d` |
| 12 | 12__v5-doc-c6d6158a42ac379f.pdf | `c6d6158a42ac379fcd8ce8f39cc93b402da5441ad551c671d47d1c976991488b` |
| 13 | 13__v5-doc-78d5d0d89420b8d3.pdf | `78d5d0d89420b8d3936b823099c7ad00044b008f5cab15b0ec19e28cd88ddf6e` |
| 14 | 14__v5-doc-9e5595dac9eb75e3.pdf | `9e5595dac9eb75e3dffb955e2a39f1268c330fc4ecabe8250f3c89e17604eb32` |

All14copies are byte-identical to the originals, including all pages.
No original PDF modified or opened for content, no render opened.
Lowercase copy .pdf extension does not change source bytes.

## Ignored context and review lists

Directory: `outputs/audit/holdout/v5-tier-c-review/`.
Context is restricted to these14documents: global/TierC/batch/manifest order,
frozen identity/paths/family/year/series/sourceType/indexMethod/pageCount,
raw counts/type counts, unchanged rawQuestions/rawAnomalies, complete-copy
paths/hashes and source bindings/provenance. No response-bearing data included.

Complete list follows C1–14; Batch01 equals exactly its first seven lines,
Batch02 its last seven lines. They are complete, disjoint and reference the
same14copies. Each line records order/documentId/copy/pages/raw/events.
Context, three lists and copies are ignored, not versioned.
No adjudication notes, renders, new OCR cache or execution script created.

## Future neutral adjudication policy

ONLY after package publication and separate authorization:

- Review every physical page in frozen order.
- Examine printed numbers/headers, starts, linked continuations and ends.
- Verify numbering restarts, section transitions and structural organization.
- Distinguish incidental numbers from genuine independent question identities.
- Critically assess all raw proposals; automatic counts are not canonical counts.
- Prove at least three fully adjudicable independent questions per document.
- Justify every identity/boundary change using neutral structural evidence.

Forbidden: responseMode, optionCount, optionLabels, markerStyle/response-marker
classification, answers/keys, GT, Auditor output/predictions/metrics, convenience
document selection, OCR/indexer tuning. No permitted visual evidence exercised now.
Raster rendering may support later separately authorized VISUAL inspection only.
No new OCR here or automatically during adjudication without specific
methodological authorization.

## Preserved Tiers A/B and methodological provenance

Published counts transported, not recomputed or visually re-adjudicated:

| Tier | Documents | Effective physical pages | Canonical questions | Unresolved |
| --- | ---: | ---: | ---: | ---: |
| A | 22 | 330 | 1370 | 0 |
| B | 4 | 92 | 220 | 0 |
| Total | 26 | 422 | 1590 | 0 |

All prior identities, boundaries, decisions, notes, checkpoints and bytes preserved.
No TierA/B PDF reopened. Transport unchanged caveats to future derivatives:

- Batch02 doc3: original-exam integrity inconclusive; frozen_available_pdf_content
  only, no original-exam completeness certification.
- Source-incomplete decisions retain absent-source metadata without fabricated
  identity/boundary; observable available content only.
- Batch02 doc10: historical frozenPageCount1/effective21 under the frozen erratum.
- Doc11: post-freeze/performance-blind replacement at original ranking2, same
  frozen stratum and inherited slot; effectiveR1 population change disclosed,
  original unresolved source/checkpoints preserved, no selector rerun or
  retroactive preregistration claim.
- Replacement sizeBytes182017 authoritative; pdfinfoReportedFileSize0 retained
  as nonblocking external-decision caveat, cause undetermined, not corruption.

Existing rules/decisions/errata/supplemental artifacts/checkpoints are bound
unchanged by path and full SHA256 in preservedPostFreezeProvenance.sourceArtifacts.
No new methodological exception created.

## SHA256 bindings

File hashes refer to actual filesystem bytes, not Git blobs/clean-filter hashes.
New text artifacts are UTF-8 without BOM.

| Artifact | SHA256 |
| --- | --- |
| Tier C package JSON | `e5b51ac600e65564aecd7c9f4178212c108354817ad95805a97dace1883e1ced` |
| Ignored review-context.json | `540420ff89308f7bd9d22c28cd24e8dc4f1c43e1f59f42d59074d4ba45aa64c4` |
| Ignored FILES_TO_REVIEW.txt | `6b6971f6f31e62aed521837adaca6ae6c6de5ace5c4d55ba91a03b08cb8ca422` |
| Ignored FILES_TO_REVIEW_BATCH_01.txt | `0555833929ad2c704ac1ad2af9087ba6d26c412438b6df5472c13204debd81a2` |
| Ignored FILES_TO_REVIEW_BATCH_02.txt | `67d56df97fae275bcf42b409a6348918ebebe6adafe83d1eae4f63eef8ccf044` |
| `audit/holdout/PROTOCOL_V5.md` | `77f8bb06d7c8eadba79c7ef70a580eebeff2d74f324017ae8e220f11bea9bb95` |
| `audit/holdout/question-index-v5-review-queue.json` | `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b` |
| `audit/holdout/question-index-v5-raw.json` | `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84` |
| `audit/holdout/question-index-v5-raw-report.json` | `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f` |
| `audit/holdout/manifest-v5-documents-frozen.json` | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| `audit/holdout/manifest-v5-documents-effective-r1.json` | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |
| `audit/holdout/v5-eligible-document-universe.json` | `dd64269956de6c7210fe0e8cc4cbb23dc799925adefa4c5e6dd603ff997c5933` |
| `outputs/audit/holdout/v5-page-count-census.json` | `f27ac3cd5e0c3b1f80667ed0ae9b8565794b16cddaccee010c7d9a6b283acc7f` |
| `audit/holdout/question-index-v5-tier-a-batch-01-adjudication.json` | `e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770` |
| `audit/holdout/question-index-v5-tier-a-batch-02-adjudication.json` | `b2447bf2a0d86e231480902ae26ddd6dcc21ecb58d84648e432ccd5355df0bf3` |
| `audit/holdout/question-index-v5-tier-b-adjudication.json` | `74e70b49127776451369b16d7642e188cb42182c67c27644b03c3aad37d57e66` |
| `audit/holdout/question-index-v5-tier-b-review-package.json` | `e3936b66d71a31652d811e26854073d2b6fcf60cfc0e8d6188d1090223bfc4c0` |
| `audit/holdout/question-index-v5-raw.provenance.json` | `7a69f89b29143c1887a6ad104cf01aa0f187b9aec73f7dfdd3b2bd749903c3b2` |

## Gates and preservation

PASS:14unique IDs/fingerprints; frozen global27–40/C1–14; exact batches7+7;
185pages/279raw/73events; methods9native/5ocr and sourceTypes9text_native/5raster;
14matching source fingerprints and byte-identical copies; invalid raw ranges0,
duplicate raw IDs0, tier leakage0; raw/context equivalence; complete/disjoint lists;
all full source/context/list/copy hashes reconciled. Neutral field policy checked.
No canonical adjudication/count or minimum-three certificate.

Preflight snapshot5257paths checked:5253protected files remain byte-identical;
four authorized documentation files retain their entire previous byte prefixes
with append-only factual/log additions. Coverage includes all prior V1–V4,
Patch05C1/indexer/Auditor functional code, V5 freezes/manifests/raw/queue,
TiersA/B artifacts/addenda/decisions/errata/checkpoints, original PDFs/copies
and prior caches/renders. Protected contents were hashed, not read as GT/Auditor
evidence. Functional diff against baseline05C1 is empty.
Git configuration/autocrlf and original line endings preserved; no .gitattributes change.
Only package JSON/Markdown and authorized CONTEXTO/brain documentation staged.

## State and mandatory STOP

```text
TierAComplete=true
TierBAdjudicated=true
TierCPrepared=true
TierCAdjudicated=false
TierDPrepared=false
PhaseBComplete=false
visualReview=false
adjudication=false
rawQuestionIndexModified=false
finalQuestionIndexCreated=false
questionSelectionExecuted=false
groundTruthCreated=false
auditorExecuted=false
metricsSeen=false
ocrExecuted=false
indexerExecuted=false
newTextExtractionPerformed=false
responseSemanticsConsulted=false
answerKeysConsulted=false
GTConsulted=false
AuditorConsulted=false
merge=false
```

TierCPrepared describes the prepared package; publication/freeze is established
only by introducing commit, successful push and remote SHA confirmation.
STOP immediately after publication. Next separate task:
**V5 Tier C Batch01 neutral visual adjudication**, NOT STARTED.
No Batch01/02 adjudication, TierD preparation, final48index,144-question
selection, GT, Auditor, metrics or merge in this execution.
