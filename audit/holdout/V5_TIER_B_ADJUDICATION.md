# Holdout V5 - Tier B neutral visual adjudication

## Scope and publication

Four frozen Tier B copies reviewed completely in their published order (global23-26).
Package publication precedes this review: source HEAD
`9d9071bf3212bb6ff15ac8ca7f93bb0828ed0e6f`, branch `audit/holdout-v5-blind`.
All92physical pages were visually inspected in order. Boundaries are physical PDF
positions, not printed footers or raw proposed spans.

Adjudication mode: `assistant-assisted-neutral-visual-review`.
No independent human adjudication is claimed. Artifact:
[neutral Tier B JSON](question-index-v5-tier-b-adjudication.json).
SHA256: `74e70b49127776451369b16d7642e188cb42182c67c27644b03c3aad37d57e66`.

## Frozen bindings

- [Published review package](question-index-v5-tier-b-review-package.json): `e3936b66d71a31652d811e26854073d2b6fcf60cfc0e8d6188d1090223bfc4c0`.
- Review-context (ignored): `cd54a2f285600deb70db43b03fac4733f514f58e9c78d3f4235632b60a1b4f95`.
- FILES_TO_REVIEW (ignored): `eb5d7307da6f04c0fd987c09b71a5a1fa83e11615c4af2068fa328e7c4065fef`.
- [Raw index](question-index-v5-raw.json): `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- [Raw report](question-index-v5-raw-report.json): `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- [Queue](question-index-v5-review-queue.json): `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b`.
- [Historical manifest](manifest-v5-documents-frozen.json): `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- [Effective manifest R1](manifest-v5-documents-effective-r1.json): `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32`.
- Completed incremental notes (ignored): `d4667539485687103d00587b9bd2af773eb3def2a5dbcaf7471069d06fb075c0`.

Remaining protocol/universe/census/Tier A/addenda/decision/checkpoint bindings are
copied from the published package and directly verified. No frozen artifact was
regenerated, corrected or overwritten.

## Results

| documentId | Physical pages | Raw | Canonical | Delta | Raw events resolved | Multipage | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v5-doc-e0b6c6a249033308 | 22 | 60 | 120 | +60 | 82 | 0 | 0 |
| v5-doc-dd8461744150ef4b | 9 | 19 | 20 | +1 | 28 | 0 | 0 |
| v5-doc-a37b092e0e967efc | 28 | 39 | 40 | +1 | 26 | 0 | 0 |
| v5-doc-143f3f337e22fb52 | 33 | 38 | 40 | +2 | 20 | 4 | 0 |
| Total | 92 | 156 | 220 | +64 | 156 | 4 | 0 |

Raw diagnostics:85duplicate-number,64missing-number and7nonmonotonic events.
These are frozen index diagnostics, NOT Auditor performance metrics or156confirmed
source defects. Every event is retained with its neutral interpretation and physical
evidence pages in the JSON.

79existing raw identity/boundary records corrected only in the adjudicated
derivative;67independently observed canonical identities absent from raw added;
3incidental raw line captures removed. Net canonical delta=67-3=64.
No printed-number normalization or genuine numbering restart was needed.
One parallel-language group in B01 was structurally canonicalized under the
already published policy; no new methodological exception was introduced.

## Per-document structural decisions

### B01 - v5-doc-e0b6c6a249033308

120genuine numbered bodies1-120 are independently visible. The raw maximum115
does not define the canonical count:116-120 each have visible starts on physical21.
Physical1 is cover/instructions. Parallel Part I sections occupy the same1-10slot:
Spanish physical2 is the first complete block in PDF order, followed by French3
and English4-5. The cover explicitly establishes the language choice. Retain
Spanish1-10 once, preserving French/English as excluded parallel representations.
This applies the frozen Tier A convention, not language quality or response semantics.

Part II starts11 onphysical6 and ends120 on21. Column order is reconciled using
printed numbers and actual blocks. Text line numbers, table values and reference
page22 are not question identities. Raw captures on cover/text/table pages are
replaced by genuine body starts.26existing raw spans corrected;60observed missing
raw identities added. All82events resolved structurally. All retained bodies
finish on their own starting physical page; shared introductory blocks do not
automatically extend them.

### B02 - v5-doc-dd8461744150ef4b

20genuine numbered bodies1-20. Initial raw11-before1 is a cover/date/instruction
capture, not a numbering restart. Genuineq1 begins onphysical2; genuineq11 on6.
q18 has its own printed header and complete body onphysical8, so it is added
without inferring its existence from the cover's declared count.
q17 ends on7, beforeq18 on8.13existing spans corrected;1identity added.
All28events resolved; no multipage question or parallel block.

### B03 - v5-doc-a37b092e0e967efc

40genuine numbered bodies1-40: mathematics1-20, then Portuguese21-40,
without restart. Cover instructions1-19 are not genuine item starts.
q1 starts onphysical3, q19 on16. Missing rawq20 is directly headed onphysical17.
Portuguese heading/sharedTextoI on18 has no numbered item start; q21 starts19.
q22 ends19, before vocabulary/q23 on20. q40 ends26; separately headed unnumbered
material27-28 is not its continuation. Frontmatter grid on2 and internal lists
in shared text/requirements do not create identities.
21existing spans corrected;1identity added; all26events resolved. No multipage body.

### B04 - v5-doc-143f3f337e22fb52

40genuine numbered bodies1-40, directly observed. The raw first2and last39
are extraction order, not the visual sequence. Genuineq1 starts and endsphysical3.
Rawq25 on19 andq40 on20 are text line captures; actual own question headers
areq25 on22 andq40 on30. Raw45/70/75on20 are sharedTextoI margin line numbers
and yield no canonical questions anywhere in the fully reviewed copy.
The five missing raw identities19/23/24/31/37 are each proved by their own
printed headers, not fabricated to close gaps.

Four genuine multipage bodies:

- q14physical10-11: closing command on11 structurally follows statements10, beforeq15.
- q19physical13-14: body/diagram13 continues with the same described structure14, beforeq20.
- q20physical14-15: geometric body/diagram14 continues15, followed by the section end.
- q38physical29-30: quoted excerpt29 is completed by its linked command30, beforeq39.

q18/q22/q28/q30/q36/q39 do not extend into the independent bodies or separately
introduced shared material captured by their raw ranges. Blank/scratch pages2,
16-18 and separately headed unnumbered material31-33 do not create numbered items.
19existing spans corrected,5identities added,3incidental captures removed;
all20events resolved. No genuine restart or parallel block.

## Neutral evidence, exclusions and technical caveats

Only printed numbers/headers, visible starts and ends, linked continuations,
physical position, section transitions, structural organization and neutral
declared counts were used. Alternatives were not used as identity/count evidence.
No responseMode/optionCount/optionLabels/markerStyle values, answer semantics,
keys, correct answers, GT, Auditor output/predictions or V5 metrics were consulted,
recorded or classified.

Published Tier A conventions for parallel slots, shared introductions and separately
headed unnumbered material were applied unchanged. Structural exclusions do not
remove any genuinely numbered question because of its response layout.
humanExclusions=0; sourceIncompleteDocuments=0. No absent source object fabricated.
The available copies are fully adjudicated; original examination completeness is
not independently certified.

Poppler emitted recoverable font warnings for B01/B02/B04: no display font for
Symbol/ArialUnicode; B01 additionally reported substitutions for
UniversCondensed,Bold, Circled-Letters and AlbertusMedium (exact recorded messages
in the checkpoint/JSON). Headers and boundaries remained readable. No specific
warning cause or PDF corruption is inferred. B03 had no material rendering
obstruction. PDF fingerprints remain unchanged.

## Checkpoint and completion gates

[Ignored incremental checkpoint](../../outputs/audit/holdout/v5-tier-b-review/adjudication-notes.json)
saved atomically after each completed document. B01/B02 decisions survive the
technical context continuation unchanged; no completed document restarted.
Full per-page neutral evidence and156event resolutions remain recorded.

PASS:4adjudicated documents;92/92physical pages;minimumThreeCertifiedForAll=true;
unresolvedDocuments=0;duplicateCanonicalIds=0;invalidPageRanges=0;
fabricatedQuestions=0;batchLeakage=0;tierAReopened=false;tierAQuestionChanges=0.
Every question ID follows `documentId:qN`; all bounds are within its frozen copy.
No new OCR, text extraction, indexer execution, census, source substitution,
Git configuration or frozen-schema change.

## Preservation and state

Tier A untouched:Batch01=11documents/182pages/1136canonical/unresolved0;
effectiveBatch02=11/148/234/unresolved0; total22/330/1370.
Its PDFs were not reopened. All existing Tier A decisions/questions/checkpoints
and hashes remain intact. Preserve and transport the published caveats:
doc3 original integrity inconclusive/available-PDF scope; source incompleteness;
doc10frozen1/effective21erratum; doc11post-freeze performance-blind replacement at
original ranking2; effective manifest R1; historical unresolved source/checkpoints;
replacement182017bytes/pdfinfoReportedFileSize0/cause undetermined.
No retroactive preregistration claim.

5154preexisting paths checked:5150protected files byte-identical, plus4documentation
prefixes preserved byte-for-byte with append-only factual updates.
V1-V4, Patch05C1, PDFs/copies/caches, indexer/Auditor functional code and all
frozen artifacts preserved. No GT/Auditor output content read for these hash checks.

TierAComplete=true;TierBAdjudicated=true;PhaseBComplete=false.
finalQuestionIndexCreated=false;QuestionSelection=false;GT=false;Auditor=false;
Metrics=false;merge=false;TierCPrepared=false;TierDPrepared=false.
One documentation/adjudication commit and push; STOP afterward.

Next separate priority: **V5 Tier C neutral review package freeze**.
Not prepared or started in this execution.
