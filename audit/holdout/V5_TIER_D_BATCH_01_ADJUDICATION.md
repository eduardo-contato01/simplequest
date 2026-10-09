# Holdout V5 - Tier D Batch01 neutral adjudication

## Scope, recovery and publication

Five frozen documents, global positions41-45,73physical pages,108canonical
questions. Branch `audit/holdout-v5-blind`; finalization source HEAD
`67179c4173046549aaf34d3812b7a5338f55fdb0`.
Mode: `assistant-assisted-neutral-visual-review`, not independent human review.

[Adjudication JSON](question-index-v5-tier-d-batch-01-adjudication.json)
SHA256: `4a9a42a7e8bf2a24626e64c79a39fc8d404050cab66a689e792b66b4584dfae8`.

The five complete document objects are imported exactly from the definitive
checkpoint; no question, boundary, evidence or adjudication decision is revised.
This execution is documentary finalization: zero new visual pages, no reopening
of PDFs/renders, OCR, text extraction, indexer or PDF parser/census execution.

Both ignored checkpoints are SHA-validated and remain byte-identical:

| Checkpoint | SHA256 |
| --- | --- |
| outputs/audit/holdout/v5-tier-d-review/adjudication-notes-batch-01.json | `92e426f4ed6f8039b11395a8dc9520fe305f385968230ad5bd3bbc786476d65b` |
| outputs/audit/holdout/v5-tier-d-review/adjudication-notes-batch-01-resumed.json | `89cd797ba235bc9e8dcd2887bd8f0663d770d70d4c643db5d5b1849b4f718516` |

The first session recorded document1physical1-4,eight identities,three
boundary corrections and one multipage body. Resumption began at physical5;
those eight question objects,four page-evidence entries and three corrections
remain exactly equal to the original checkpoint. The remaining69physical
pages were reviewed sequentially in the resumed session. No inherited page
reopened and no inherited decision revised. The definitive checkpoint's
unpublished/context-limit flags remain an immutable historical snapshot;
new publication status belongs exclusively to this derivative/documentation.

Formal freeze and `TierDBatch01Adjudicated=true` take effect only after the
introducing commit, successful authorized push, equal local/remoteHEAD and
clean versioned working tree/empty stage. Until then publication is pending.

## Results and gates

| Batch / global | documentId | Pages | Raw | Canonical | Delta | Corrections | Multipage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 / 41 | v5-doc-05c35f7183da4927 | 12 | 20 | 20 | 0 | 7 | 3 |
| 2 / 42 | v5-doc-0d7bc5575df13886 | 10 | 20 | 20 | 0 | 1 | 0 |
| 3 / 43 | v5-doc-1b6b371a30f5cd22 | 19 | 24 | 24 | 0 | 3 | 1 |
| 4 / 44 | v5-doc-34e3910f5e106aae | 7 | 12 | 20 | +8 | 12 | 0 |
| 5 / 45 | v5-doc-80e01b1d6082d26b | 25 | 24 | 24 | 0 | 4 | 0 |
| Total | Five documents | 73 | 100 | 108 | +8 | 27 | 4 |

PASS: five unique document IDs/fingerprints in literal frozen order41-45;
all73physical pages and their evidence registered;108unique canonical IDs;
valid in-range pageStart/pageEnd and sequential canonical numbers; own starts
matched to page evidence; documented continuation for all four multipage
questions; at least three independent adjudicable questions each; zero
unresolved documents/issues, duplicate IDs, invalid ranges, fabricated
questions or batch leakage. Raw events=0; minimum-three certified for allfive.

The27corrections comprise15boundary-only corrections and12identity/boundary
replacements. Zero automatic diagnostics, adjudication corrections and actual
source defects are separate categories. These structural counts are not
Auditor metrics; no cause of indexer behavior or PDF corruption is inferred.
Document-level counts retain the exact checkpoint representation; root totals
and explicit multipage evidence provide schema-consistent semantic validation.

## Global44: effective reconciliation, not delta-only inference

Physical1contains twelve numbered administrative instructions under
INSTRUÇÕES; none is an own question start. All12raw captures at that location
are rejected as incidental administrative numbering.

Twenty independent own ordinal headers,1º Item through20º Item, are proved
on physical2-7. The cover's umbrella wording does not collapse independently
headed bodies into a single unit. Their physical locations are:

| Physical page | Own printed/canonical item numbers |
| --- | --- |
| 2 | 1-4 |
| 3 | 5-8 |
| 4 | 9-10 |
| 5 | 11-14 |
| 6 | 15-18 |
| 7 | 19-20 |

Every body closes on its own start page; actual item12is physical5-5,
not raw1-7. All20real bodies are absent from the raw capture locations.
Canonical ID strings:q1-:q12are explicitly rebound to these distinct actual
bodies, with rejection/provenance of the corresponding raw administrative
captures; only:q13-:q20(eight strings) are absent from the raw ID set.

Effective reconciliation:20proved bodies,12incidental captures removed,
12existing numeric ID strings rebound,eight new ID strings;20-12=+8net.
The twelve identity/boundary replacements are counted among the27corrections,
not as acceptance of the old identities. No legitimate question excluded,
no synthetic identity, numbering restart or response-layout criterion.
Full per-record evidence is retained in addedCanonicalQuestions,
removedRawCaptures,corrections and rawCaptureReconciliation. The delta alone
is not used to infer the numbers of additions/removals or the indexer's cause.

## Other recorded structural decisions

- Global41:20own Portuguese bodies. Onlyq4=2-3,q14=7-8andq17=9-10are
  multipage. q20ends11; distinctly headed unnumbered writing material11-12
  is not q20continuation or a syntheticq21.
- Global42:20own Portuguese bodies,all single-page; shared TextIIafterq10
  does not extend it. q20closes10before distinct unnumbered production
  material. Printed pagination is physical+1; boundaries use physical pages.
- Global43:mathematics1-12thenPortuguese13-24without restart; onlyq1=2-3
  is multipage. q12ends9before scratch10,q16ends13before shared TextII14,
  q24ends17before distinct writing18/scratch19.
- Global45:mathematics1-12thenPortuguese13-24without restart; allsingle-page.
  q12ends13,q15ends15,q17ends17,q24ends21above the Portuguese end marker.
  Physical22-25are distinct unnumbered writing material/instructions/draft,
  notq24continuation or syntheticq25. Printed pagination is physical-1.

Distinct unnumbered blocks follow published Tier B/Tier C conventions,
not response-semantics classification. No new methodological exception.
All73physical-page evidence records,108question objects and corrections
remain in the JSON unchanged from the definitive checkpoint.

## Frozen bindings and historical caveats

| Artifact | SHA256 |
| --- | --- |
| Tier D package JSON | `2f0a37b84525f8e3b6197dd4c7da4baed1544384937be5649507063ac2156c2c` |
| Tier D review-context | `bb1630214f46df213ad98feb3b183c78e6149c254de3c18f319f74fb3c7e89d3` |
| Batch01 review list | `9901b55c1ac228efdc2f789d50097a8951f0b0c27000b159d996ed4d83dbe695` |
| Original raw index | `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84` |
| Original review queue | `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b` |
| Historical manifest | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| Effective manifest R1 | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |

Remaining protocol/universe/census/prior-tier/decision/errata/addenda/checkpoint
bindings are transported directly from the frozen package/checkpoint and
verified against actual bytes. No frozen artifact regenerated or flag changed.

Tiers A22documents/330effective pages/1370canonical,B4/92/220and
C14/185/364remain intact without re-adjudication. Preserve post-freeze,
performance-blind provenance: available-source incompleteness without
fabricated identities; TierABatch02doc3original integrity inconclusive and
frozen_available_pdf_content scope; doc10historical1/effective21erratum;
doc11same-stratum/originalranking2replacement and effectiveR1population
change with original unresolved history retained; sizeBytes182017authoritative,
pdfinfoReportedFileSize0nonblocking/cause undetermined. No retroactive
preregistration or original-examination completeness certification.

Prior Poppler warnings on documents1,2,3,5 are recorded as structurally
nonblocking; causes undetermined, no automatic corruption finding.
Document4has no recorded render warnings; some lines reach the right border,
but recorded own starts/closures are unambiguous. No PDF/editorial repair.

## Preservation actually executed

Existing preservation mechanism reused, without redundant snapshots.
This finalization rechecked5394protected binding paths,representing5390distinct
files; four absolute/relative aliases are not counted as separate files.
Original and definitive TierD checkpoints plus12prior TierD renders were
checked additionally. Source bindings and five complete PDF fingerprints were
hashed as binary data only, without content/page inspection.

For publication,5386distinct protected files remain byte-identical; four
authorized documentation files retain their entire historical byte prefixes
with append-only updates. Functional baseline Patch05C1 and indexer/Auditor
code remain unchanged; Gitconfiguration/autocrlf and historical line endings
are preserved. Only the two derivatives,one CONTEXTO entry and factual
append-only brain updates are staged; no outputs/checkpoints/PDFs/renders.

## Conditional state and mandatory STOP

```text
TierAComplete=true
TierBAdjudicated=true
TierCAdjudicated=true
TierDPrepared=true
TierDBatch01Adjudicated=true (effective only after successful commit/push)
TierDBatch02Adjudicated=false
TierDAdjudicated=false
PhaseBComplete=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
groundTruthStarted=false
auditorExecuted=false
metricsSeen=false
merge=false
```

One introducing commit:
`audit: adjudicate v5 tier d batch 01 neutral question index`.
Authorized push to origin/audit/holdout-v5-blind and matching local/remoteHEAD
required. STOP after publication. Next separately authorized task:
**V5 Tier D Batch02 neutral visual adjudication**.
No global48-document index,144-question selection,GT,Auditor,metrics or merge.
