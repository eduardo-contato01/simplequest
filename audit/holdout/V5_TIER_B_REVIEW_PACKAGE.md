# Holdout V5 — Tier B neutral review package

V5_TIER_B_NEUTRAL_REVIEW_PACKAGE_PREPARATION=PASS

## Scope and freeze

Branch `audit/holdout-v5-blind`; source HEAD
`9e54809e5c36e330e7a481d4e2e12f0dfb7bfa9a`.
Preparation only: four complete binary PDF copies and neutral context/list/package.
Formal freeze is the introducing commit and publication on the same branch.
No PDF parsing, rendering, new text extraction, OCR, indexing or visual review.
No anomaly interpretation, question correction, canonical count or minimum-three certification.

The queue SHA256 transcription error in the execution instruction was corrected by
explicit external decision to the full frozen value shown below. The original queue
was not regenerated or modified. Passed preflight was reused after unchanged HEAD,
clean working tree/stage and source-byte identity were confirmed.

## Immutable Tier B order

Only `reviewQueue` entries with `reviewTier == "B"`, in their existing order:
global positions23–26. No reranking, new population selection or replacement.
Tier B rows are exactly equal in the historical and effective R1 manifests.

| Tier / global / manifest order | documentId | Family / year / series | Pages | Raw questions | Raw anomalies | Method |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 1 / 23 / 19 | `v5-doc-e0b6c6a249033308` | PAS 1 / 2010 / — | 22 | 60 | 82 | native |
| 2 / 24 / 16 | `v5-doc-dd8461744150ef4b` | CMRJ / 2012 / 6º Ano | 9 | 19 | 28 | native |
| 3 / 25 / 3 | `v5-doc-a37b092e0e967efc` | CMC / 2025 / 6º Ano | 28 | 39 | 26 | native |
| 4 / 26 / 33 | `v5-doc-143f3f337e22fb52` | CMF / 2025 / 6º Ano | 33 | 38 | 20 | native |
| Total | 4 documents | — | 92 | 156 | 156 | native4 / ocr0 |

The156 anomalies are automatic diagnostic EVENTS, not156 confirmed defects or
Auditor metrics. Raw identities, numbers, page ranges and anomaly arrays were copied
exactly from the frozen raw index/report, without interpretation or corrections.
All four frozen sources remain eligible and unreplaced. Fingerprints match4/4;
manifest/report/queue page counts match the frozen two-reader census4/4.
The48-PDF census was not rerun. No examination-content completeness is certified.

## Local ignored review package

Directory: `outputs/audit/holdout/v5-tier-b-review/`.
Only `copies/`, `review-context.json` and `FILES_TO_REVIEW.txt` created.

| Tier order | Complete review copy | Source SHA256 = copy SHA256 |
| --- | --- | --- |
| 1 | `01__v5-doc-e0b6c6a249033308.pdf` | `e0b6c6a249033308b2a83a54a73997342f2f5ca9a4ea502e0d5c11bfbdf7ce59` |
| 2 | `02__v5-doc-dd8461744150ef4b.pdf` | `dd8461744150ef4bd83208fbadb512a403a915633d0dcfb681df4b56f869dcac` |
| 3 | `03__v5-doc-a37b092e0e967efc.pdf` | `a37b092e0e967efc24dd4806830ad446c8d9a10bda7ae83ea1180090a36ac5bf` |
| 4 | `04__v5-doc-143f3f337e22fb52.pdf` | `143f3f337e22fb529c8e610ca215f16214b425761ec1bd9b47e121a384bf2474` |

All4 copies are byte-identical to their complete original sources; no pages removed,
selected or cropped. The sources/copies were read only as binary bytes for hashing
and equality, not opened for content inspection.

The context records tier/global/manifest order, documentId/fingerprint, canonical
and relative paths, family/year/series/sourceType/indexMethod, physical pageCount,
rawQuestionCount/rawAnomalyCount/type counts, unchanged rawQuestions/rawAnomalies,
copy paths/hashes and frozen source bindings. The list contains only these4 documents,
in frozen order, with copy name and neutral counts; no Tier A/C/D leakage.

## Evidence policy for a later separate adjudication

Allowed ONLY after freeze/publication and separate authorization:

- visible question number and start;
- continuation/end and physical page positions;
- sections, numbering restarts and structural organization;
- document-declared neutral item count;
- already available neutral native/OCR text.

Forbidden: response semantics, responseMode, option count/labels, markerStyle or
response-marker classification, answers/keys, Ground Truth, Auditor predictions/output
and Auditor metrics. None of the permitted visual evidence was exercised here.
All physical pages must be reviewed in that later task; no raw anomaly is adjudicated now.

## Preserved Tier A and post-freeze provenance

Batch01 unchanged:11documents/182pages/1136canonical/unresolved0.
Effective Batch02 unchanged:11documents/148pages/234canonical/unresolved0.
Tier A complete:22documents/330effectivepages/1370canonical. Phase B incomplete.

Preserve and transport the existing caveats to future derivatives:

- Batch02 doc3: source integrity inconclusive; only frozen_available_pdf_content,
  original examination completeness not certified.
- Source-incomplete exceptions: frozen decisions/criteria and unavailable content
  remain explicit; no absent identity or boundary fabricated.
- Batch02 doc10: frozenPageCount1/effective21 under the unchanged pagination erratum.
- Batch02 doc11: post-freeze/performance-blind replacement at original ranking2;
  effective R1 population change disclosed, no retroactive preregistration or selector rerun;
  original unresolved source, decisions and historical checkpoints retained.
- Replacement sizeBytes182017 remains authoritative; pdfinfoReportedFileSize0
  remains the documented nonblocking technical divergence, cause not determined,
  not automatically classified as PDF corruption.

Bindings to decisions/rules/errata, supplemental package/adjudication and all historical
checkpoints are in `preservedPostFreezeProvenance.sourceArtifacts` of the JSON.
No Tier A PDF reopened and no adjudicated question visually revalidated.

## SHA256 bindings

Hashes are SHA256 of filesystem bytes, not Git blob identifiers.
New text artifacts use UTF-8 without BOM.

| Artifact | SHA256 |
| --- | --- |
| [Tier B package JSON](question-index-v5-tier-b-review-package.json) | `e3936b66d71a31652d811e26854073d2b6fcf60cfc0e8d6188d1090223bfc4c0` |
| Ignored review context | `cd54a2f285600deb70db43b03fac4733f514f58e9c78d3f4235632b60a1b4f95` |
| Ignored files list | `eb5d7307da6f04c0fd987c09b71a5a1fa83e11615c4af2068fa328e7c4065fef` |
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

## Gates and preservation

PASS:4unique document IDs/fingerprints, correct frozen order,92pages/156raw/156events,
native4/ocr0, source fingerprints/copies4/4, duplicate raw IDs0, invalid raw ranges0,
Tier leakage0, raw arrays unchanged, context/list bindings reconciled and neutral
field policy enforced. No canonical decisions or response-bearing fields included.

Pre-existing snapshot5146files checked:5142protected files remain byte-identical;
four authorized documentation files preserve their entire prior byte prefixes and
receive only incremental checkpoint/log additions. Coverage includes V1–V4,
Patch05C1 functional baseline/indexer/Auditor, V5 protocol/universe/manifests/raw/queue,
Tier A artifacts/decisions/errata/checkpoints, original PDFs, copies and prior caches.
Git configuration/autocrlf and historical line endings are unchanged.
Functional diff against baseline05C1 is empty; no legacy validator modification
or claim of official V5 Auditor execution readiness.

Only this package JSON/Markdown and authorized CONTEXTO/brain documents are staged.
PDFs, ignored context/list, caches/renders/checkpoints and frozen sources are not staged.

## State and mandatory STOP

```text
TierAComplete=true
TierBAdjudicationPerformed=false
TierBAdjudicated=false
PhaseBComplete=false
manualAdjudicationPerformed=false
rawQuestionIndexModified=false
finalQuestionIndexCreated=false
questionSelectionExecuted=false
groundTruthCreated=false
auditorExecuted=false
metricsSeen=false
ocrExecuted=false
newTextExtractionPerformed=false
indexerExecuted=false
responseSemanticsConsulted=false
answerKeysConsulted=false
GTConsulted=false
AuditorConsulted=false
merge=false
```

TierBPackageFrozen=true is established only after introducing commit, push and
remote SHA confirmation. STOP immediately after publication.
Next separately authorized task: **V5 Tier B neutral visual adjudication**.
No opening review copies, Tier C/D preparation, final index,144-question selection,
GT, Auditor, metrics or merge in this execution.
