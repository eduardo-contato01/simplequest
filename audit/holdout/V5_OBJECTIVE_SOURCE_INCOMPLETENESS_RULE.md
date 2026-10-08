# Holdout V5 — objective source incompleteness rule

## Timing, disclosure and freeze

This is an explicit **post-freeze, performance-blind protocol addendum** to
[PROTOCOL_V5.md](PROTOCOL_V5.md), not a silently rewritten original protocol.
It arose after an objective source gap was observed during neutral adjudication,
after document selection/freeze but before question selection, Ground Truth or
Auditor execution. This exception was not pre-registered before source inspection.
V5 remains blind to Auditor/performance; its methodology has this disclosed
post-freeze change. No GT, Auditor output, response semantics or V5 metrics were
consulted to make this decision.

Branch: `audit/holdout-v5-blind`. Source HEAD: `3a20aa0037988299b9879dc46d87116a4b042c00`.
Decision date: 2026-10-08. Formal freeze is the commit introducing this addendum
and its [decision artifact](v5-objective-source-incompleteness-01.json).
The original protocol and document manifest remain byte-identical.

## General conservative rule

The rule is independent of family or documentId. Retain a frozen document with
objective source incompleteness only when **all six** conditions hold:

1. The document was selected before inspection.
2. Incompleteness is demonstrated by structural evidence in the document itself.
3. Absent questions/parts cannot receive directly observed boundaries.
4. No automatic eligible replacement exists in the same frozen ranking/stratum.
5. No GT, Auditor or performance information was consulted.
6. At least `questionsPerDocument` completely observable and adjudicable questions remain.

Then keep the document and mark `sourceIncomplete=true`. Do not fabricate
question objects, identities or boundaries to reach a declared count. Only
canonical objects whose identity and pageStart/pageEnd were directly adjudicated
may enter the future final question index. Record unavailable content separately
as source-gap metadata, never in the selectable question pool or as
`humanExclusions`. These are absent source items, not observed semantic exclusions.

If any condition fails, this retention rule does not authorize proceeding: STOP
for explicit resolution. It does not authorize another-stratum replacement,
reuse of holdout/calibration documents, manual swaps or performance-based filtering.
The original replacement policy otherwise remains unchanged.

## Application — Tier A Batch01 document 8

- documentId: `v5-doc-7a302456c4a6afbe`.
- contentFingerprint: `7a302456c4a6afbe0451df3e4cdf7027dbedee4801f4d24ddc0babaf440e4191`.
- `sourceIncomplete=true`.
- `sourceIncompleteReason=missing_physical_pages_or_content_gap`.
- Cover-declared item count: 30.
- All 14/14 available PDF pages were already reviewed in the paused neutral review.
- Directly observed starts: 26, numbered 1..17 and 22..30.
- Unavailable source numbers: 18, 19, 20, 21; no observed pageStart/pageEnd.
- PDF page 9 has visible footer/page 9; PDF page 10 has visible footer/page 12.

The source indicates an objective gap consistent with missing physical pages.
This does not establish the historical cause of the loss as an absolute fact.
The count/pagination gap is structural evidence, not a judgment about answers,
response mode, OCR quality or expected Auditor performance.

Metadata-only verification of the frozen
[eligible universe](v5-eligible-document-universe.json) found exactly one eligible
document in `(raster, COLÉGIO PÓDION, 2020-2025, 5º Ano)`: this document itself.
Therefore `sameStratumReplacementAvailable=false`; no other stratum was searched
for a substitute. The selected document and fingerprint are retained unchanged.

## Future adjudication and selection contract — not executed here

On resumption after this addendum is frozen, the adjudication may use
`status=adjudicated_source_incomplete`: all AVAILABLE content reviewed, absences
explicitly characterized, no invented question objects, original source incomplete.
It does not mean the complete original examination has been reconstructed.

For this document, the future `questions[]` will contain only q1..q17 and q22..q30,
with the numbering gap preserved; no q18..q21 objects without observed boundaries.
Separate metadata will retain `sourceIncomplete=true`, `declaredItemCount=30`
and `sourceMissingQuestionNumbers=[18,19,20,21]`. The missing entries do not count
as `humanExclusions`. The 26 observed questions are the future canonical pool,
subject to materialization of their directly adjudicated identity/page ranges.

`selectableQuestion = canonical question object with fully adjudicated identity + valid page range`.
Source-missing entries are never selectable. The future deterministic selector
will choose 3 questions only from the 26 fully adjudicated objects, never from
the declared 30 items. The plan remains 48 documents × 3 questions = 144 questions.
No selection logic is implemented here; no three IDs are selected or calculated.

## Provenance and preservation

Evidence comes from the external neutral decision and the existing paused notes,
not a reopened visual review. The decision JSON records the frozen input hashes.
The notes remain byte-identical at
`outputs/audit/holdout/v5-tier-a-batch-01-review/adjudication-notes.json`, SHA256
`cd5694c64b83420b044c5f4e1b26e2f20dff7f79f569b1a487b0b4a0d35bd3b5`.
Their historical `unresolved` status is not rewritten in this execution;
the resolution is applied only in a later authorized resumption.

Original protocol, Phase A manifest, raw index/report, triage, queue, Batch01
package, Auditor/indexer, V1–V4, baseline05C1 and local review helper/renders/notes
are preserved. No functional code, selector, source PDF or frozen artifact changes.

```text
postFreezeProtocolAddendum=true
performanceBlind=true
sameStratumReplacementAvailable=false
documentRetained=true
questionObjectsFabricated=0
missingBoundariesInferred=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
groundTruthStarted=false
auditorExecuted=false
metricsSeen=false
Batch01AdjudicationComplete=false
```

## STOP

After this addendum's commit/push, STOP. Documents 9–11 are not resumed here;
Batch01 final adjudication, Batch02 preparation, final index, question selection,
GT, Auditor and metrics remain unstarted. No merge. Next separately authorized
step: resume Tier A Batch01 neutral adjudication under this frozen addendum.
