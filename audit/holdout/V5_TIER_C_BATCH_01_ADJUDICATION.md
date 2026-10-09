# Holdout V5 - Tier C Batch01 neutral visual adjudication

## Scope and resumption

Seven frozen documents, global27-33, all89physical pages adjudicated in frozen order.
Branch: `audit/holdout-v5-blind`; source/published-package HEAD:
`9aa754048f68d8aacca8c2b6df41fe6534525591`.
Mode: `assistant-assisted-neutral-visual-review`; no independent human review claimed.

[Adjudication JSON](question-index-v5-tier-c-batch-01-adjudication.json)
SHA256: `2d39dfe43f0b96c11336e6fce0b29aa34cba65f4691f555310676b27329720ce`.

The original ignored checkpoint remained byte-identical:
`outputs/audit/holdout/v5-tier-c-review/adjudication-notes-batch-01.json`,
SHA256 `a8a1ee559dcd138b0598e40aea1c30b9a6e8d07c3f2865c18675c7ac27a6e498`.
Documents1-2 were imported as exact complete objects (31pages/70questions/five
multipage), not reopened. Document3pages1-4 and their evidence were imported
exclusively from that verified checkpoint; this execution began exactly at
document3physical5. No exceptional reinspection occurred.
54new physical pages reviewed: document3pages5-12, then documents4-7 completely.

Separate resumed notes were initialized only from the original checkpoint and
saved by atomic rename after each relevant advance and completed document:
`outputs/audit/holdout/v5-tier-c-review/adjudication-notes-batch-01-resumed.json`.
Final SHA256: `b7787622069fd5c218e5574b8e542b99bcc792bf718feb0a529a75b02a8e213f`.
The original is not overwritten; both checkpoints/renders remain ignored.

## Frozen bindings

- [Tier C package](question-index-v5-tier-c-review-package.json): `e5b51ac600e65564aecd7c9f4178212c108354817ad95805a97dace1883e1ced`.
- Review-context: `540420ff89308f7bd9d22c28cd24e8dc4f1c43e1f59f42d59074d4ba45aa64c4`.
- Batch01 list: `0555833929ad2c704ac1ad2af9087ba6d26c412438b6df5472c13204debd81a2`.
- [Raw index](question-index-v5-raw.json): `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- [Raw report](question-index-v5-raw-report.json): `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- [Queue](question-index-v5-review-queue.json): `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b`.
- [Effective manifest R1](manifest-v5-documents-effective-r1.json): `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32`.

Remaining full bindings and post-freeze provenance are transported directly from
the published package and verified without regeneration. Seven copy fingerprints
match the frozen full fingerprints; no source/copy PDF modified.

## Results

| C order / global | documentId | Physical pages | Raw | Canonical | Delta | Multipage | Existing raw corrections | Events resolved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / 27 | v5-doc-906c5ae29d59a1ff | 15 | 20 | 40 | +20 | 5 | 3 | 19 |
| 2 / 28 | v5-doc-91b5252bd14b8900 | 16 | 12 | 30 | +18 | 0 | 2 | 13 |
| 3 / 29 | v5-doc-675affeba8d87308 | 12 | 10 | 20 | +10 | 4 | 3 | 10 |
| 4 / 30 | v5-doc-2442b4ab742e42f2 | 10 | 13 | 20 | +7 | 0 | 3 | 8 |
| 5 / 31 | v5-doc-d12896e095155245 | 17 | 10 | 20 | +10 | 0 | 6 | 4 |
| 6 / 32 | v5-doc-3a0c4b28948e4a30 | 8 | 21 | 24 | +3 | 0 | 0 | 3 |
| 7 / 33 | v5-doc-47ff0591259f48eb | 11 | 17 | 20 | +3 | 0 | 0 | 3 |
| Total | Seven documents | 89 | 103 | 174 | +71 | 9 | 17 | 60 |

71directly observed identities absent from raw added; no raw identity discarded.
60automatic events (30duplicate/30missing) interpreted structurally, not Auditor
metrics or60source defects. Zero unresolved. No question invented from a gap or
from a cover-declared total. Full per-page evidence and literal event objects
remain in JSON/checkpoints.

## Structural decisions

### C01 - preserved from checkpoint

Portuguese printed1-20 onphysical3-9; Mathematics restarts printed1-20 on10-15.
Canonical ordinals1-40 disambiguate the two genuine sequential sections while
printedQuestionNumber/section/sequenceRun remain explicit.
Raw20closes8-9, not8-15. Raw10closes4-5; raw12closes5-6.
Multipage: canonical10=4-5,12=5-6,14=6-7,20=8-9,39=14-15.
All observations/notes/corrections/evidence unchanged from the original checkpoint.

### C02 - preserved from checkpoint

30own numbered bodies. Initial1-5are directly headedphysical2-3, despite raw
starting6. Portuguese1-15physical2-7, Mathematics16-30physical8-15, no restart.
Raw7closes5, not6; raw29closes15, not administrative back16.
Shared introductions do not extend previous bodies. No multipage question.
Exact complete object imported unchanged; no PDF reopened.

### C03 - resumed exactly at physical5

Portuguese own1-10 then Mathematics own1-10 under its distinct heading on8.
Canonical1-20; second run printed1-10 explicitly preserved.
Portuguese6ends5before separate sharedTexto03, not6. Portuguese7continues6-7.
Portuguese10ends7before Mathematics8, not7-12.
Four multipage identities: canonical7=6-7,12(Math2)=8-9,
14(Math4)=9-10,19(Math9)=11-12.
Math9has its own header at bottom11 and linked body/closure12 before Math10;
no identity inferred merely from the numbering sequence.
Pages1-4 evidence unchanged from the original; pages5-12 directly inspected now.

### C04 - complete raster copy, no new OCR

20distinct ownITEM01-20; missingraw1/3/4/5/8/12/13 have visible ownheaders.
Physical6repeats printedpage3/8 and the ITEM06/07representation already observed
onphysical4, including the distinctive tables/figures and closed bodies.
This is not a new independent identity, numbering restart or continuation of10.
Retain one identity6and7 at their first complete occurrences4; record repeated
representation separately. All printed content pages1/8through8/8are present.
The cause of the repeated page is not determined; source/copy untouched.
Raw2ends2,7ends4,10ends5. All20bodies close on their starting physicalpage.
No absent source question inferred and no new methodological exception introduced.

### C05 - complete raster copy, no new OCR

20own numbered bodies. Initial1-7directly visiblephysical3-5; own9-11on7.
Raw8closes6,13closes8,16closes10,17closes11,18closes12,20closes13.
SharedTextoIII/IVintroductions are not continuations of8/13.
Physical13explicitly closes the numbered section. Separately headed unnumbered
material14, scratch15, separate booklet cover16 and ruled page17 do not extend20
or receive synthetic numbered identities. Applies the established TierB03/B04
convention, not a response-layout exclusion; humanExclusions=0.
All17pages inspected; no multipage numbered body.

### C06 - complete available native copy

24own numbered bodies, all contained on their respective physicalpages.
Missingraw2directly headed1,12and13directly headed4; three additions.
Printed footers2/9through9/9 map to physical1-8 with constant offset.
Use actual PDF positions; no internal content gap or clipped question boundary
observed. Do not claim independent certification of original-exam completeness.

### C07 - complete raster copy, no new OCR

20ownITEMheaders with closed bodies. Missingraw3directly headed2,7headed4,
11headed6. All17existing raw bounds match; three additions, no multipage body.

## Neutral policy and technical caveats

Only ownheaders/printednumbers, starts, linked continuations/ends, physicalpages,
section transitions, structural organization and neutral declared counts used.
No responseMode/optionCount/optionLabels/markerStyle classification, answers,
keys, GT, Auditor predictions/output or V5 metrics consulted or recorded.
Shared introductions, administrative numerals and graph/table/line numerals
do not independently establish question identities. humanExclusions=0.

Poppler120dpi renders used for visual inspection only; no new OCR, extraction,
indexer run, parser census or tuning. Recoverable no-display-font warnings for
Symbol/ArialUnicode onC01/C02/C06 are recorded exactly. C01's graph-area caveat
is retained from its original checkpoint; no cause inferred. Ownheaders/boundaries
remained readable. No PDF corruption claim or original-exam completeness claim.

## Preservation and completion gates

PASS:7documents/89pages/minimum3each/unresolved0/duplicateIDs0/invalidranges0/
fabricated0/batchLeakage0. IDs use documentId:qN; restarts preserved inC01/C03.
Documents1-2 exact object equality and importedC03pages1-4equality validated.
Original checkpoint SHA remains unchanged; resumed checkpoint has separate provenance.

Existing protection mechanism reused:5278preexisting paths checked;5274protected
files byte-identical and four authorized documentation prefixes byte-preserved
with append-only additions. No redundant global inventory or48PDFcensus created.
Functional diff versus Patch05C1 empty; Gitconfig/autocrlf unchanged.
TiersA=22documents/330pages/1370canonical andB=4/92/220 intact; no prior-tier PDF
reopened. Frozen manifests/raw/queue/package/addenda/decisions/checkpoints,
V1-V4, original PDFs/caches and functional code remain preserved.

Mandatory post-freeze caveats transported verbatim in structured provenance:
source incompleteness without invented identities; original integrity inconclusive
for TierABatch02doc3/available-PDF scope; doc10frozen1/effective21erratum;
doc11same-stratum/originalranking2replacement/performance-blind, effectiveR1
population change and original unresolved checkpoints retained;182017bytes
authoritative/pdfinfoReportedFileSize0nonblocking/cause undetermined, not corruption.
No retroactive preregistration claim.

## State and publication

TierAComplete=true; TierBAdjudicated=true; TierCBatch01Adjudicated=true.
TierCBatch02Adjudicated=false; TierCAdjudicated=false; PhaseBComplete=false.
finalQuestionIndexCreated=false; questionSelectionStarted=false;
groundTruthStarted=false; auditorExecuted=false; metricsSeen=false; merge=false.
TierD not prepared. No144question selection or globalV5questionindex created.

Freeze by the introducing adjudication/documentation commit and authorized push;
confirm equal local/remoteHEAD, clean working tree and empty stage. STOP after push.
Next separate priority: **V5 Tier C Batch02 neutral visual adjudication**.
