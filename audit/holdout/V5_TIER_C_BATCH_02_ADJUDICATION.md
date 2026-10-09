# Holdout V5 - Tier C Batch02 neutral adjudication and Tier C closure

## Scope and recovery

Seven frozen documents, global34-40,96physical pages and190canonical questions.
Branch `audit/holdout-v5-blind`; finalization source HEAD
`52d69ba7475b623431dadc35a0d5a93b0169e234`.
Mode: `assistant-assisted-neutral-visual-review`, not independent human adjudication.

[Batch02 adjudication JSON](question-index-v5-tier-c-batch-02-adjudication.json)
SHA256: `03ccad0a3cf9cf35b31f479b31379f6d264365e579d40270f417c5444fa39883`.

All seven document objects are imported exactly from the definitive ignored
checkpoint, whose structure, identities, evidence and bindings were validated:
`outputs/audit/holdout/v5-tier-c-review/adjudication-notes-batch-02.json`.
SHA256: `56f83a70727464d32f20be40e681194cd98ef20c8c90af62c783da78ec00de34`.
The checkpoint remains byte-identical during this finalization.

Review took place in two previous executions:
documents1-5/64pages/110canonical/one multipage/zero unresolved, followed by
documents6-7/32pages/80canonical/one additional multipage/zero unresolved.
No PDF or render reopened now; zero new visual pages, no re-adjudication.

The earlier incremental whole-checkpoint SHA
`d3c1541565a3fd5080567f4ca30ea6db26bcbae490dfe1c0ae4c4a665b87679f`
is historical: the same incremental file was subsequently updated atomically.
No immutable copy with that old whole-file hash exists locally.
Do not expect it to match the definitive file, or claim byte equality with it.
Current first-five objects match the semantic digest recorded in controlled
resumption (`acf234c3bb9c52533bfd8defd0c31ae9c0fa03639a0e6d4757932365210522e8`,
Python sorted-key compact JSON/ensure_ascii=false/UTF-8). Their retained evidence
and totals agree with the resumption provenance; they were not reconsidered.

## Frozen bindings

- [Tier C package](question-index-v5-tier-c-review-package.json): `e5b51ac600e65564aecd7c9f4178212c108354817ad95805a97dace1883e1ced`; published commit `9aa754048f68d8aacca8c2b6df41fe6534525591`.
- Review-context: `540420ff89308f7bd9d22c28cd24e8dc4f1c43e1f59f42d59074d4ba45aa64c4`.
- Batch02 list: `67d56df97fae275bcf42b409a6348918ebebe6adafe83d1eae4f63eef8ccf044`.
- [Published Batch01](question-index-v5-tier-c-batch-01-adjudication.json): `2d39dfe43f0b96c11336e6fce0b29aa34cba65f4691f555310676b27329720ce`; published commit `52d69ba7475b623431dadc35a0d5a93b0169e234`.
- [Queue](question-index-v5-review-queue.json): `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b`.
- [Raw index](question-index-v5-raw.json): `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- [Raw report](question-index-v5-raw-report.json): `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- [Historical manifest](manifest-v5-documents-frozen.json): `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- [Effective manifest R1](manifest-v5-documents-effective-r1.json): `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32`.

All remaining protocol/universe/census/prior-tier/addenda/decision/checkpoint
bindings are copied directly from frozen artifacts and verified. No regeneration.

## Batch02 results

| Batch / global | documentId | Pages | Raw | Canonical | Delta | Multipage | Existing raw corrections | Events resolved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / 34 | v5-doc-cb4e2c7c9e714d00 | 19 | 26 | 30 | +4 | 1 | 7 | 3 |
| 2 / 35 | v5-doc-2300b505b11855a2 | 7 | 18 | 20 | +2 | 0 | 3 | 2 |
| 3 / 36 | v5-doc-429b811d62a29a28 | 17 | 18 | 20 | +2 | 0 | 5 | 2 |
| 4 / 37 | v5-doc-bc5d90aa69fa3416 | 12 | 17 | 20 | +3 | 0 | 17 | 2 |
| 5 / 38 | v5-doc-c6d6158a42ac379f | 9 | 18 | 20 | +2 | 0 | 2 | 2 |
| 6 / 39 | v5-doc-78d5d0d89420b8d3 | 15 | 39 | 40 | +1 | 0 | 4 | 1 |
| 7 / 40 | v5-doc-9e5595dac9eb75e3 | 17 | 40 | 40 | +0 | 1 | 8 | 1 |
| Total | Seven documents | 96 | 176 | 190 | +14 | 2 | 46 | 13 |

14independently proved identities absent from raw added;46existing raw ranges
corrected only in the derivative. No raw identity removed, human exclusion,
numbering restart/normalization or parallel group. Zero unresolved, duplicate
canonical IDs, invalid ranges, fabricated questions or batch leakage; minimum3each.
The13events (12missing/one duplicate) are automatic structural diagnostics,
not13confirmed source defects or Auditor performance metrics.

## Recorded structural decisions

- Document1:30own numbered bodies. Four additions:4/physical3,7/4,28/18
  and30/19; the last is proved despite being beyond raw maximum29.
  Only q26continues physical16-17. Shared texts do not prolong closed bodies.
- Document2:20own bodies;12/physical5and18/6added. q20ends6, not separate
  subsequent material or scratch page7. Every retained body is single-page.
- Document3:20own bodies;17and18directly headed physical14.
  q20ends15, not the distinct material16-17. Shared introductions/infographic
  numerals do not independently create questions; no multipage body.
- Document4:20own ordinal Item bodies. Administrative instructions1-19 on
  physical2 are not question starts; parent section heading is not an extra item.
  All17existing raw records are reconciled with actual bodies. Added5/physical5,
  7/6and20/12. q19=11-11, not2-12. Every body is single-page.
  Available booklet adjudicated, without reconstruction or certification of
  separately mentioned original-exam booklets.
- Document5:20own bodies;3/physical2and12/6added.
  Parent QUESTAO UNICA is not another identity. Introduction between10and11
  onphysical5does not prolong10. Every body closes on its start page.
- Document6:40own bodies;Portuguese1-20/physical1-8then Mathematics21-40/9-15,
  no restart. q35is directly headed/closed13, not inferred from a gap.
  q10=4-4,q14=5-5,q17=6-6,q20=8-8; all40are single-page.
- Document7:40own bodies;Portuguese1-20then Mathematics21-40without restart.
  Only q24=10-11: own header/table/figure10, linked continuation/closure11
  before an independent introduction. q10=3-3,q12=4-4,q15=5-5,q17=6-6,
  q18=7-7,q20=8-8,q21=9-9,q31=13-13.
  Raw duplicate17/page16does not prove another identity: two inline references
  to17in q38are not own headers; actual q17is independently headed/closed6.
  Original wording preserved, no editorial correction or indexer-cause inference.

Full96page evidence, literal event objects/resolutions, question metadata,
boundaries, additions and corrections remain in the JSON and checkpoint.

## Tier C completion

| Batch | Global positions | Documents | Pages | Raw | Canonical | Events | Multipage | Unresolved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Published01 | 27-33 | 7 | 89 | 103 | 174 | 60 | 9 | 0 |
| Batch02 | 34-40 | 7 | 96 | 176 | 190 | 13 | 2 | 0 |
| Tier C | 27-40 | 14 | 185 | 279 | 364 | 73 | 11 | 0 |

Combined PASS:14unique document IDs, literal frozen order27-40, disjoint batches,
no omitted document, all evidenced identities/bounds and zero unresolved.
Batch01 JSON/Markdown/checkpoints remain byte-identical; its PDFs were not reopened.
The two adjudication JSONs and their bindings suffice; no third consolidation
artifact or global48-document index created.

## Neutral policy, caveats and preservation

Own headers, printed numbers, physical positions, starts, linked continuations,
ends, section transitions and neutral structural organization only.
No responseMode/optionCount/optionLabels/markerStyle values or classifications,
alternatives as identity evidence, answers, keys, GT, Auditor predictions/output
or V5 performance metrics consulted.

Prior Poppler120dpi render warnings for Symbol/ArialUnicode ondocuments4-7
are preserved as recoverable/nonblocking: own headers and boundaries remained
readable. Specific causes undetermined; no automatic corruption inference.
No original-examination completeness certification.

Tiers A22documents/330effective pages/1370canonical andB4/92/220intact.
Post-freeze provenance transported unchanged: available-source incompleteness
without invented identities; TierABatch02doc3original integrity inconclusive;
doc10historical1/effective21erratum; doc11same-stratum/originalranking2replacement
with effectiveR1population change and original unresolved history retained;
182017bytes authoritative/pdfinfoReportedFileSize0nonblocking/cause undetermined.
No retroactive preregistration claim or new methodological exception.

Existing preservation contract reused; no redundant inventory/snapshot.
Preflight5281protected path hashes actually checked and passed.
For publication,5277protected files remain byte-identical and four authorized
documentation files retain their entire historical byte prefixes with append-only
updates. Definitive Batch02 checkpoint SHA checked separately and unchanged.
Functional diff against baseline Patch05C1 empty; Gitconfig/autocrlf unchanged;
no line-ending normalization, frozen-file modification or PDF/content reinspection.

## State and publication

TierCBatch01Adjudicated=true;TierCBatch02Adjudicated=true;TierCAdjudicated=true
only after the combined gates PASS. TierAComplete=true;TierBAdjudicated=true.
TierDPrepared=false;PhaseBComplete=false.
finalQuestionIndexCreated=false;questionSelectionStarted=false;
questionSelectionExecuted=false;groundTruthStarted=false;groundTruthCreated=false;
auditorExecuted=false;metricsSeen=false;merge=false.
No new render/OCR/extraction/indexer/census during finalization.

Formal freeze by one introducing adjudication/documentation commit:
`audit: adjudicate v5 tier c batch 02 neutral question index`,
authorized push and equal local/remoteHEAD with clean working tree/empty stage.
STOP after publication. Next separate priority:
**V5 Tier D neutral review package freeze**, NOT STARTED.
