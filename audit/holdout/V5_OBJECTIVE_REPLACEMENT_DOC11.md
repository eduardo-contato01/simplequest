# V5 — objective replacement of Batch02 document11

## Authority and methodological disclosure

Branch `audit/holdout-v5-blind`; source HEAD
`70b84aac7ff63a7ed033074beb5dbabcaabbce1d`. Explicit external authorization
on2026-10-08 under the published
[generic insufficient-question-units addendum](V5_INSUFFICIENT_QUESTIONS_REPLACEMENT_RULE.md)
and [doc11 decision](v5-insufficient-questions-decision-doc11.json).
This is a **post-freeze, performance-blind change to the effective population**,
NOT part of the original pre-inspection selection and NOT a selector rerun.
The eight original criteria and decision remain immutable; disclose this exception
in the final V5 methodology. Formal freeze by introducing commit and branch publication.

## Materialized change and unchanged historical selection

| Role | documentId | contentFingerprint |
| --- | --- | --- |
| Historical original | `v5-doc-a08230ae0b1cad7e` | `a08230ae0b1cad7e06f3e15215d54d0e53526e3e5c6b11008f4295a5fb469d09` |
| Effective replacement | `v5-doc-e1c73fb849ef80a6` | `e1c73fb849ef80a6f94a2ecf09718a963bd7c65008f930526605489ac25f8fe3` |

Reason: `insufficient_independent_adjudicable_questions`. Original doc11 had
four available pages reviewed and fewer than three independent identities proved;
no exact original canonical count or PDF-corruption conclusion is invented.

[Historical manifest](manifest-v5-documents-frozen.json) is byte-identical, including
the original doc11. [Effective manifest R1](manifest-v5-documents-effective-r1.json)
has48documents:47 unchanged row objects and this single replacement at manifest
position47, Batch02 position11, global TierA22. The original selection history/seed
are retained as explicitly HISTORICAL provenance, not copied as pre-registration
of this exception. No final index or question selection is created.

Invariants PASS: same family/year/era/series/sourceType, original positions unchanged,
48 unique IDs/fingerprints, source quotas32text_native/15raster/1hybrid, overlap with
prior holdouts/calibration0. The effective document population DOES change; no claim
that the original selected identities remain fully unchanged after replacement.

## Deterministic candidate and technical gates

Original stratum `["text_native","CMSM","2004-2009","1º Ano"]`; original seed
`156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e`.
Read-only ranking of four frozen eligible rows by SHA256(seed+"|"+fingerprint),
then literal fingerprint/path, confirms rank2 exclusively:
`v5-doc-e1c73fb849ef80a6`, ranking hash
`949586a3f14297d8499cb7d89f588e175597fe480bfcc5c2c9b68d448e3d4b6e`.
No candidate of another rank/stratum selected; no complete48 selector executed.

Source exists; binary SHA256 matches frozen fingerprint. Frozen size182017 equals
filesystem stat and bytes read. pypdf6.10.0 strict reader and independent
Poppler pdfinfo26.07.0 both confirm12pages; page objects, positive MediaBoxes,
parent/content references readable; no reader error or warning reported.
These are basic technical integrity gates, not certification of examination-content
completeness or question eligibility.

### Explicit nonblocking file-size caveat

Original `pdfinfoReportedFileSize=0` is preserved, NOT silently corrected or omitted.
The user explicitly authorized `sizeBytes=182017` as authoritative, based on frozen
universe, filesystem and binary reading. The specific cause of the pdfinfo zero is
**not determined**; do not infer corruption. Fingerprint, missing source, real page-count
inconsistency, integrity failure or methodological violation remain blocking gates.

Original command, captured structural metadata, reader results and subsequent external
decision are preserved in ignored `outputs/audit/holdout/v5-tier-a-batch-02-replacement-r1/logs/technical-integrity-original.json`
(SHA256 `1dc382ddbccc915b0b5477da04e37075a9189efa82dbd3b77f64de748d3ed297`).
No visual render/review or question-text extraction was done by the technical check.

## Single frozen neutral indexing execution

Indexer: `scripts/audit_holdout_question_index.py`; Git blob
`25ca4665708ba0ad8850f889f5ea0d71e3ff4025`; local SHA256
`04262953d3949651bd8cf4c236cbd5e7b4e85b64c34db77033c19717824b5d3c`.
Method `neutral-question-index-v1`; fallback tesseract/160DPI/PSM11/por+eng,
unchanged from [protocol freeze](V5_QUESTION_INDEX_PROTOCOL_FREEZE.md).

Exact PowerShell command:

```powershell
& 'C:\Users\trans\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 -u scripts/audit_holdout_question_index.py --manifest audit/holdout/manifest-v5-documents-effective-r1.json --only v5-doc-e1c73fb849ef80a6 --out outputs/audit/holdout/v5-tier-a-batch-02-replacement-r1/only-mode-out-not-written.json --report outputs/audit/holdout/v5-tier-a-batch-02-replacement-r1/neutral-index-report.json
```

UTC2026-10-08T21:47:00.8037406Z →21:47:01.9582282Z; exitCode0;
executionCount1; rerun=false; processedDocuments1; method=native; pageCount12;
rawQuestions18; automaticAnomalies2. No OCR fallback or renders/cache created.
Python3.12.14/pdfplumber0.11.9; Tesseract5.4.0.20240606 available for frozen fallback.
Execution command/argv/runtime/input hash/timestamps/output are preserved in the
ignored execution log, bound by the erratum JSON.

`--only` returns before writing `--out`: its absence is expected, not a failure.
The report was written exclusively under ignored outputs and remains byte-identical.
[Supplemental raw](question-index-v5-tier-a-batch-02-supplemental-raw.json) copies the
single report result's questions/anomalies unchanged. No original/global raw rerun,
correction, normalization, new IDs by human interpretation or raw-based replacement.

Automatic native content extraction DID occur for neutral indexing. This is not
manual visual adjudication. Raw18/anomalies2 do not establish canonical count,
minimum-three eligibility or selected questions; those remain unproved.

## Hash bindings

| Artifact | SHA256 |
| --- | --- |
| Historical manifest | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| Effective manifest R1 | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |
| [Replacement erratum JSON](v5-objective-replacement-doc11.json) | `d68c681e089bda68cf091046700c9be88bcf09eb147cb824728e83a82cccd9a4` |
| Supplemental raw | `acac51b72a64fd8b327f647cfcde209dea1fff41f567600f456104ab0bff479b` |
| Ignored neutral indexer report | `0325f19cddf358d348ebc95a965c6549d7c084ce070def22a5219d0aa4db409f` |

Erratum JSON binds the frozen rule/decision, original protocol/universe/manifest,
raw/report/queue, Batch01, Batch02 original package/context, doc3/8 decisions,
doc10 erratum/census and three historical checkpoints. No original artifact,
source PDF, existing cache, functional05C1/indexer/schema or Git setting changes.
Preservation snapshots cover5096 pre-existing tracked/output/source paths.

Legacy `audit_holdout_schema.py` supports only V1–V4, not V5; it was not invoked,
changed or spoofed to V4. The direct frozen neutral CLI does not call it. This
preparation's independent read-only structural/binding/identity/quota/page-range
checks do not claim official Auditor readiness. Legacy execution compatibility
remains a separately authorized future gate.

## Progress and STOP

Original checkpoint remains10adjudicated/214canonical questions and140pages reviewed
in the ORIGINAL set, including removed doc11's4pages. In the effective set, retained
docs1–10 account for136already-reviewed pages; replacement12pages pending; effective
Batch02 physical total148 after existing doc10 pagination erratum. The47 unaffected
manifest rows retain original frozen metadata; doc10's effective21 is supplied by
its immutable erratum, never silently rewritten to replace frozen1.

The [supplemental review package](V5_TIER_A_BATCH_02_SUPPLEMENTAL_REVIEW_PACKAGE.md)
must be published before future visual review. ReplacementPerformed=true;
historicalManifestUnchanged=true; effectiveManifestCreated=true;
candidateTechnicalPdfOpened=true; candidateNeutralIndexerExecuted=true.
ManualVisualAdjudication=false; canonicalCountKnown=false; minimumThreeCertified=false.
Batch02/TierA/PhaseB incomplete; finalIndex/selection/GT/Auditor/metrics/merge=false.

After introducing commit/push, STOP. Next separately authorized step:
**V5 Tier A Batch02 supplemental neutral visual adjudication**.
Do not reopen/re-adjudicate docs1–10, close Batch02, prepare TierB, select questions,
create GT, execute Auditor, calculate metrics or merge.
