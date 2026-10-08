# Holdout V5 — Tier A Batch01 neutral adjudication

V5_TIER_A_BATCH_01_ADJUDICATED=PASS

## Scope and completion

Phase B2b-2, Tier A, Batch01 only. Base/branch: `ec1f6af770b7197a48438eb39d855ff74fc9d73d` / `audit/holdout-v5-blind`.
All 11 frozen documents and 182/182 available physical PDF pages reviewed; unresolvedDocuments=0.
This is the adjudication artifact of one batch, NOT the final global question index.
Tier A has 22 frozen documents; tierAComplete=false, Phase B incomplete, Batch02 untouched.

## Raw vs canonical

Counts describe neutral index reconstruction, not Auditor metrics.

| Order | Document | Raw | Canonical | Delta | Physical pages reviewed | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| 1 | v5-doc-ccc36240e82f271d | 28 | 120 | +92 | 16/16 | adjudicated |
| 2 | v5-doc-9341853cd786543a | 50 | 110 | +60 | 24/24 | adjudicated |
| 3 | v5-doc-bd657a7d79e90389 | 31 | 120 | +89 | 24/24 | adjudicated |
| 4 | v5-doc-1fb8c32edfae9126 | 48 | 130 | +82 | 22/22 | adjudicated |
| 5 | v5-doc-a8e098aad9a7ece4 | 60 | 120 | +60 | 20/20 | adjudicated |
| 6 | v5-doc-ae2f4e91af8a01f9 | 57 | 150 | +93 | 17/17 | adjudicated |
| 7 | v5-doc-4ec5bc5117bb7440 | 51 | 180 | +129 | 16/16 | adjudicated |
| 8 | v5-doc-7a302456c4a6afbe | 2 | 26 | +24 | 14/14 | adjudicated_source_incomplete |
| 9 | v5-doc-b1498826d8a54db3 | 7 | 110 | +103 | 12/12 | adjudicated |
| 10 | v5-doc-506c709758cb13a9 | 7 | 30 | +23 | 11/11 | adjudicated |
| 11 | v5-doc-e223f9e9c5cea0cb | 4 | 40 | +36 | 6/6 | adjudicated |
| Total | Batch01 | 345 | 1136 | +791 | 182/182 | 11 resolved |

## Objective source incompleteness

Document `v5-doc-7a302456c4a6afbe` (order 8): status=adjudicated_source_incomplete;
sourceIncomplete=true; sourceIncompleteReason=missing_physical_pages_or_content_gap;
declaredItemCount=30; observable canonical=26; missing source numbers=[18,19,20,21];
sourceMissingCategory=source_gap_not_human_exclusion.
Only q1–q17 and q22–q30 exist. fabricatedQuestions=0; sourceMissingQuestionObjectCount=0;
missingBoundariesInferred=false; humanExclusions=[].

All 14 available pages had already been reviewed. The observed question-number gap and
printed-footer jump from 9 to 12 are recorded in the frozen decision, not a conjecture
about the historical cause. No eligible automatic replacement exists in the same frozen stratum.
The [post-freeze, performance-blind addendum](V5_OBJECTIVE_SOURCE_INCOMPLETENESS_RULE.md)
and [external decision](v5-objective-source-incompleteness-01.json) were frozen at the base commit
before this resumption. This is explicitly NOT retroactive pre-registration.

The prior unresolved status, issues and notes remain verbatim in historicalReviewCheckpoint.
Only the 26 previously observed identities and page ranges were materialized.
No page of document 8 was visually reopened; missing questions/ranges were not reconstructed.
The validation's discontinuous-sequence exception applies exclusively to this frozen case.
Documents 9–11 have no newly observed source gaps; sourceIncompleteDocuments=1.

## Structural decisions

### Parallel sections

Six groups represent alternative language blocks occupying the same numbered section slot;
they are not genuine sequential numbering restarts. The first complete language block in PDF
order represents that slot; the other representations are explicitly excluded from duplicate
canonical identities, not counted as human exclusions of unique questions.

- v5-doc-ccc36240e82f271d: PARTE I — LÍNGUA INGLESA; Explicit cover instruction for all foreign-language options, same Part I position and 1..10 sequence; first complete block in PDF order.
- v5-doc-9341853cd786543a: PARTE I — LÍNGUA ESPANHOLA; Cover instruction3 declares language options; same Part I slot and1..10 sequence; first complete block. PARTE I only; page5 Part II retained
- v5-doc-bd657a7d79e90389: PARTE I — LÍNGUA ESPANHOLA; Explicit cover instruction3 and same Part I1..10 slot; first complete block.
- v5-doc-1fb8c32edfae9126: PARTE I — LÍNGUA INGLESA; Explicit cover instruction2, parallel headings and numbering; first complete block in PDForder.
- v5-doc-a8e098aad9a7ece4: PARTE I — LÍNGUA INGLESA; Cover declares options for1..8; first complete block in PDForder.
- v5-doc-b1498826d8a54db3: PARTE 1 — LÍNGUA ESPANHOLA; Visible shared PARTE1 slot, distinct language headings, identical1..10 ranges and PARTE2 continuation11; first complete representation in PDForder. No historical family pattern used. French block only on page2; Spanish q6..10 on page2 retained; English block on page3 excluded

For document 9, Spanish q1–q5 is on physical page 1 and q6–q10 on page 2.
The French block on the mixed page 2 and English block on page 3 are parallel; Spanish
on page 2 remains included. Part 2 begins at q11 on page 4. This copy has no cover:
the decision uses the visible repeated Part 1 slot/headings and subsequent Part 2 transition,
not an assumed instruction or historical family pattern. Earlier documents' mixed-page scope
and explicit cover evidence are preserved in their existing notes.

### Numbering, continuation and exclusions

numberingRestarts=0; numberingNormalizations=0; humanExclusions=0.
All normal documents have directly observed continuous canonical numbering starting at 1.
The sole source gap remains unnormalized in document 8.

multiPageQuestions=2, both in `v5-doc-506c709758cb13a9`:
q3 physical pages 2–3; q6 physical pages 3–4. The other numbered bodies end on their starting
physical page. Cross-column flow and shared introductory material are not automatically
multipage question continuations. Page ranges use physical PDF positions, not printed footers.

Covers, instructions, blank/scratch/reference/back pages and separately headed unnumbered
essay material do not generate canonical questions. No numbered question was removed because
of its incidental response layout. Per-document structural exclusions and mixed-page scopes
remain explicit in the JSON. The empty candidate-fill grid on document 11 page 2 is frontmatter,
not an answered key or question-body evidence.

## Evidence policy and resumption provenance

Allowed evidence: visible question numbers, starts, continuation/end, physical page positions,
section transitions and document-declared neutral count.
No responseMode, optionCount, optionLabels or markerStyle classification was performed;
responseSemanticsConsulted=false, answerKeysConsulted=false, GTConsulted=false,
AuditorConsulted=false, metricsSeen=false. Incidental handwritten marks were not used as
answer evidence. No answer or response-layout evidence was transcribed into the question objects.

The review occurred in sessions interrupted by quota. Prior completed documents 1–7 were
NOT visually re-adjudicated. The incremental local notes are the authority for their 930
canonical objects. Prior notes SHA256:
`cd5694c64b83420b044c5f4e1b26e2f20dff7f79f569b1a487b0b4a0d35bd3b5`.
The document 8 exception was resolved under the frozen addendum before reviewing documents 9–11.
Those three documents were reviewed in order, all 29 physical pages; notes were saved immediately
after each document. priorResolvedDocuments=7; priorVisualAdjudicationReperformed=false;
sourceIncompleteResolutionApplied=true; incrementalNotesPreserved=true.

## Validation and preservation

JSON parse/schema/count/provenance checks PASS. documents=11; allAvailablePagesReviewed=11/11;
totalPhysicalPagesReviewed=182; unresolvedDocuments=0; duplicateCanonicalQuestionIds=0;
duplicateCanonicalQuestionNumbersPerDocument=0; invalidPageRanges=0; fingerprintMismatch=0;
batchLeakage=0; sourceMissingQuestionObjectCount=0.

The first seven notes objects remain semantically identical to the preflight snapshot;
the original document 8 checkpoint is also semantically identical and its observed ranges
match every materialized question. The 4,824 protected files are byte-identical to the local
preflight snapshot, including original protocol, addendum/decision, Phase A, B1, B2a,
raw index/report, queue/package/context, functional Auditor/indexer/baseline05C1,
V1–V4, previous outputs/caches and prior renders. Original PDFs unchanged.
review.py and persistent Git configuration unchanged; CONTEXTO history retained byte-for-byte.
Only authorized documentation/adjudication files are staged; functionalFilesStaged=0,
outputFilesStaged=0, pdfFilesStaged=0. No merge or functional change.

## Hashes

| Artifact | SHA256 |
| --- | --- |
| Batch01 adjudication JSON | e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770 |
| Frozen review package | 61f769a6d016a30095e97a16fd1da79396d05ec1ef2f750cff75135b9c7ac59f |
| Frozen review context | fbb49685a7c49f625d03b0aa51356bd137b56e8d3264f9095fb699d750261b77 |
| Frozen raw index | 68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84 |
| Frozen raw report | 62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f |
| Frozen review queue | 027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b |
| Frozen protocol addendum | 6e53620188ef104d5880ee04e84ef382675a64a8fcc927f69543e6ca273e3541 |
| Frozen source-gap decision | 9389c0a0908f7788ef937d6d46ead9f8d1bb97a829ab99c23fff16df493b0e88 |
| Completed ignored incremental notes | ce11333c97b4be37387133a6a3aa0a1c9e85d3619821b502c01a8d4ad405425f |
| Protected-files preflight digest (4,824 files) | 93549182342a599414c50b346b7d786d508b549738cbc922d603f0fb43c7bf4b |

## State and next authorized step

tierABatch01Adjudicated=true; tierAComplete=false; finalQuestionIndexCreated=false;
questionSelectionStarted=false; questionSelectionExecuted=false; groundTruthStarted=false;
groundTruthCreated=false; auditorExecuted=false; metricsSeen=false; merge=false.
Next separate task: Tier A Batch02 review package freeze. No Batch02 preparation or opening
in this execution. After the single Batch01 commit/push, STOP.
