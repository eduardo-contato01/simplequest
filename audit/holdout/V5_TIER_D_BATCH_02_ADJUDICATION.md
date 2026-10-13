# Holdout V5 - Tier D Batch02 neutral adjudication

## Scope, recovery and formal freeze

Three frozen documents, global46-48,61physical pages,74canonical questions.
Branch `audit/holdout-v5-blind`; source HEAD
`644be02f2ed772d6b69dcb15ae4b6660b8ef6d63`.
Mode: `assistant-assisted-neutral-visual-review`, not independent human review.

[Adjudication JSON](question-index-v5-tier-d-batch-02-adjudication.json)
SHA256: `eb7f0ed97be8e0c4cbf138c06227b2d2e20b9667e9b87b11898b06e8f001666b`.

The original interrupted checkpoint is preserved byte-identically. Resumption
started exactly at global47physical9, without reopening global46 or inherited
global47physical1-8. All three complete document objects are imported exactly
from the definitive resumed checkpoint into this derivative.

| Ignored checkpoint | SHA256 |
| --- | --- |
| outputs/audit/holdout/v5-tier-d-review/adjudication-notes-batch-02.json | `ea57be989ed65a11a0db18c3418f8e8a9c3ca816e87a8108deba01a7ff452e8e` |
| outputs/audit/holdout/v5-tier-d-review/adjudication-notes-batch-02-resumed.json | `01ad12eb893202c6650b4c8001ddd4fbe7e60c331cf315e011af6179abd26f60` |

Inherited27physical pages/37proved questions, including global46complete
19pages/30questions/4boundary corrections/7multipage bodies, remain intact.
The full global46object and seven global47question objects/eight page-evidence
entries are structurally identical to the original. No inherited decision revised.
This session visually reviewed the remaining34pages: global47physical9-22,
then global48physical1-20. Checkpoints were saved atomically in page blocks and
after documents, with valid JSON/SHA256 and original-checkpoint comparisons.
The prior pending JSON and both stop-validation scripts were inspected for
existence before any use: all absent. No temporary progress promoted.
One delayed local command was resolved by inspecting the saved checkpoint and
confirming its complete bytes/progress; no decision lost or conflicting pending file.

Formal `TierDBatch02Adjudicated=true`/`TierDAdjudicated=true` is conditional:
effective only after introducing commit, successful authorized push, equal
local/remoteHEAD, clean versioned worktree and empty stage. The JSON records
this condition explicitly. Historical/checkpoint flags are immutable snapshots.

## Results and gates

| Batch / global | documentId | Pages | Raw | Canonical | Delta | Corrections | Multipage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / 46 | v5-doc-9b28d28efbbf0354 | 19 | 30 | 30 | 0 | 4 | 7 |
| 2 / 47 | v5-doc-a7256b9befdea91b | 22 | 24 | 24 | 0 | 2 | 0 |
| 3 / 48 | v5-doc-c3bf2d29c7e1d9e8 | 20 | 20 | 20 | 0 | 8 | 0 |
| Total | Three documents | 61 | 74 | 74 | 0 | 14 | 7 |

PASS: literal frozen order46-48/unique IDs/fingerprints; all61physical pages
and evidence registered;74unique canonical IDs; valid physical ranges and
sequential canonical numbers; own starts matched to page evidence; closures
justified; at least three independent adjudicable questions each; zero
unresolved documents/issues, duplicate IDs, invalid ranges, fabricated questions
or batch leakage. Native3/text_native3; raw automatic events=0.

All14corrections are boundary-only. Added identities/captures removed/rebound
identities/numbering restarts/normalizations/human exclusions=0.
Zero raw events and zero net canonical delta do not imply correct raw boundaries.
No indexer-cause inference or response-semantic criterion.

## Neutral structural decisions

### Global46: imported, not reviewed again

Thirty own bodies; mathematics1-15 then Portuguese16-30 without restart.
q2endsphysical2before distinct shared introduction3; q15ends12before shared
Portuguese material12-13; q20ends15before shared TextII/figure16;
q22ends16before shared TextIV/figure17. These four corrections and every
inherited note remain unchanged; q26starts and ends18.
Shared introductions' printed references do not override own headers;
the original note about q27and the shared-text references is retained verbatim.
q28/q29/q30close19before final markers; physical1is administrative cover,
physical13shared text without own question.

The seven inherited multipage bodies are:

| Question | Physical range |
| --- | --- |
| q5 | 4-5 |
| q6 | 5-6 |
| q8 | 6-7 |
| q13 | 9-10 |
| q15 | 11-12 |
| q18 | 14-15 |
| q25 | 17-18 |

### Global47: resumed physical9

Twenty-four own bodies: mathematics1-12 then Portuguese13-24, no restart.
All single-page. q12endsphysical13before mathematics end marker; shared
Portuguese Text1on14and author box beforeq13on15are not q12continuation.
q22ends18before distinct shared Text2/figure; q23starts and ends18.
q24ends19before Portuguese end marker, not raw19-22.
Physical20-22are separately headed unnumbered production material, shared
texts/instructions and scratch sheet; incidental instruction/line numbering
creates no own question and no syntheticq25. Printed pagination=physical-1.
Inherited q1-q7/evidencephysical1-8are unchanged.

### Global48: frozen modified PDF, full review

Twenty own bodies: Portuguese01-10 then mathematics11-20, no restart.
All single-page. q1endsphysical2; distinct TextII/q2on3is not continuation.
q2ends3; distinct TextIII/q3on4is not continuation.
Shared introductions/figures/local glossaries and internal figure labels are
distinguished from own question headers. q20ends18above blank remainder;
physical19-20are separately headed unnumbered production material/instructions/
scratch grid, not q20continuation and not syntheticq21.

Scope=`frozen_available_pdf_content`; source version=`frozen_modified_pdf`.
Frozen relative path:
`CMDPII/Modificadas/CMDPII - 6ANO - 2018_2019 (modificado).pdf`.
Fingerprint:
`c3bf2d29c7e1d9e8a8ad05f64f313fa8b92bccebea2e90d5dc1d8a6b363faed2`.
No assertion of integral reproduction or completeness of the original
institution examination. No editorial/PDF repair or population change.
Printed pagination=physical page.

### Exact raw-to-canonical boundary reconciliation

| Global | Question | Frozen raw | Adjudicated physical range |
| --- | --- | --- | --- |
| 46 | q2 | 2-3 | 2-2 |
| 46 | q15 | 11-14 | 11-12 |
| 46 | q20 | 15-16 | 15-15 |
| 46 | q22 | 16-17 | 16-16 |
| 47 | q12 | 13-15 | 13-13 |
| 47 | q24 | 19-22 | 19-19 |
| 48 | q1 | 2-3 | 2-2 |
| 48 | q2 | 3-4 | 3-3 |
| 48 | q4 | 4-5 | 4-4 |
| 48 | q5 | 5-6 | 5-5 |
| 48 | q6 | 6-7 | 6-6 |
| 48 | q7 | 7-8 | 7-7 |
| 48 | q8 | 8-9 | 8-8 |
| 48 | q20 | 18-20 | 18-18 |

Poppler Symbol/ArialUnicode font warnings remain recorded; reviewed own starts
and closures were observable. Causes undetermined; no automatic corruption
finding. No OCR, new text extraction, indexer, census, training or functional change.

## Tier D closure and V5 structural review

| Scope | Documents | Reviewed pages | Raw | Canonical | Corrections | Multipage | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Batch01, global41-45 | 5 | 73 | 100 | 108 | 27 | 4 | 0 |
| Batch02, global46-48 | 3 | 61 | 74 | 74 | 14 | 7 | 0 |
| Tier D | 8 | 134 | 174 | 182 | 41 | 11 | 0 |

Eight documents in exact global41-48order, complete/disjoint batches, zero
missing/duplicate documents or canonical IDs and minimum-three PASS for all8.
Batch01JSON/Markdown/checkpoints/renders preserved; no previous PDF reopened.
Its12identity-boundary replacements/15boundary-only corrections remain unchanged;
combined41corrections=29boundary-only+12identity-boundary replacements.

Published tiers A22/330pages/1370canonical, B4/92/220, C14/185/364 and
D8/134/182reconcile to48effective documents/741pages/2136canonical identities.
Counts/IDs/fingerprints/pages transported from published artifacts, not new
adjudications. Early Tier A uses pagesReviewedCount/reviewedPages rather than
pageCount; doc10effective21is retained under the frozen erratum.
No global canonical index file created or frozen; `PhaseBComplete=false`.

## Frozen bindings and mandatory historical caveats

| Artifact | SHA256 |
| --- | --- |
| Tier D package | `2f0a37b84525f8e3b6197dd4c7da4baed1544384937be5649507063ac2156c2c` |
| Review-context | `bb1630214f46df213ad98feb3b183c78e6149c254de3c18f319f74fb3c7e89d3` |
| Batch02 list | `837fb437e21946215977f641377bbd0f37a632efb140c4897da37371add39062` |
| Tier D Batch01 adjudication | `4a9a42a7e8bf2a24626e64c79a39fc8d404050cab66a689e792b66b4584dfae8` |
| Raw index | `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84` |
| Review queue | `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b` |
| Historical manifest | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| Effective manifestR1 | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |

Remaining protocol/universe/census/prior-tier/decision/errata/addenda bindings
are copied directly into the JSON and checked against actual local bytes.
All three source/copy fingerprints checked in full as binary data; PDFs unmodified.
Source-incomplete histories remain distinct from original-integrity certification.
TierABatch02doc3original integrity inconclusive/frozen_available_pdf_content,
doc10historical1/effective21erratum, doc11same-stratum/ranking2post-freeze
replacement/effectiveR1population change and original unresolved checkpoints
all preserved. Replacement sizeBytes182017authoritative; pdfinfoReportedFileSize0
nonblocking/cause undetermined, not automatic corruption. No retroactive
preregistration or new methodological exception. Caveats must propagate to
the final index and later V5 evaluation.

## Preservation actually executed

Original checkpoint hash/provenance/state,20root sourceSHA bindings,24additional
decision/checkpoint bindings and three full source/copy pairs verified.
Existing preservation path lists reused, plus current tracked files and preexisting
Tier review assets:5558current-session unique binding paths/5558distinct files.
Complete binary baseline/rechecks held only in memory; no redundant snapshot.
This is pre/post preservation for this execution, not a new independent historic
freeze. The original session's5471paths/5467files/four aliases remains separately
reported historical evidence, not silently substituted for current coverage.

Before authorized documentation append, all5558binary hashes match.
For publication,5554protected files remain byte-identical; four documentation
files retain their full historical byte prefixes and historical line endings,
with append-only updates. Functional05C1/indexer/Auditor/code/.gitattributes/
PDFs/copies/freezes/prior checkpoints remain unchanged.
Gitconfiguration compared against this session's preflight bytes; core.autocrlf=true,
no config mutation/line-ending normalization. Only the six authorized derivative/
documentation files staged; no outputs/checkpoints/renders/caches/PDFs/scripts.

## Conditional state and mandatory STOP

After successful introducing commit/push:
TierAComplete=true/TierBAdjudicated=true/TierCAdjudicated=true/TierDPrepared=true;
TierDBatch01Adjudicated=true/TierDBatch02Adjudicated=true/TierDAdjudicated=true.
PhaseBComplete=false/finalQuestionIndexCreated=false/questionSelectionStarted=false/
questionSelectionExecuted=false/groundTruthStarted=false/groundTruthCreated=false/
auditorExecuted=false/metricsSeen=false/merge=false.

One commit: `audit: adjudicate v5 tier d batch 02 neutral question index`.
STOP after publication. Next separately authorized:
**V5 final canonical question index consolidation and freeze**.
Do not create global index, select144questions, GT, Auditor, metrics or merge.
