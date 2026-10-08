# Holdout V5 — objective page-count erratum, Batch02 document10

V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10=PASS

## Authority, timing and scope

Explicit user authorization on 2026-10-08; source HEAD
`58ed0af2c1f961168feb86c699e8ed065bd607f7`, branch `audit/holdout-v5-blind`.
Formal freeze by the introducing commit. This is an additive post-freeze objective
metadata erratum, performance-blind, discovered after document selection and during
neutral Batch02 review, before question selection, GT or Auditor V5.
It is not a retroactive pre-registration or a rewrite of [PROTOCOL_V5.md](PROTOCOL_V5.md).

No visual adjudication resumed in this execution. Structural metadata access to all48
frozen originals was explicitly authorized only for binary hash/page count. No PDF
text/content extraction, OCR, rendering, GT, Auditor, metrics or semantic inspection.

## Affected document and objective finding

- documentId: `v5-doc-74e153f9c146d887`.
- Family CMSP; year2019; series6ºAno; sourceType=raster; indexMethod=ocr.
- TierA, Batch02 order10, global TierA21; manifest order12.
- PDF SHA256 = frozen fingerprint =
  `74e153f9c146d8878547d6f5fd0538953c61fcb15f17f27c6d1cfcddfadee53d`.
- frozenPageCount=1; verifiedActualPageCount=21; effectivePageCount=21; delta=+20.

The discrepancy was first diagnosed when the previous authorized Batch02 resumption
stopped at document10 before visual question review. Source/review-copy binary
fingerprints matched the freeze. The historical resumed checkpoint remains immutable.
The current independently confirmed census establishes a metadata error, not PDF
corruption or new examination-content completeness certification.

## Origin and propagation — frozen values NOT rewritten

The original metadata source is pre-V5 `outputs/audit/corpus-inventory.json`, SHA256
`9c6a365adb0da7036ac965437ebec590fc01c72641b21f0297a20e02b72014c8`. Its neutral row for this exact canonicalPath
has pageCount1 and error=null. The universe/manifest carry that same1; queue and
Batch02 package preserve the propagated count. All original files remain byte-identical.

The raw index was produced considering the frozen metadata and must NOT be interpreted
as a certified inventory of all21pages. This does not authorize rerunning the indexer,
regenerating raw, changing raw IDs or reselecting documents. Do not estimate how many
questions additional pages contain: only later authorized direct neutral review can
determine their observable canonical identities/boundaries.

## Global confirmation and bindings

[Census of all48](V5_PAGE_COUNT_CENSUS.md): pypdf6.10.0 and independent Poppler
pdfinfo26.07.0 agree48/48; binary fingerprints match48/48; technical failures0;
pageCountMismatchCount1, exclusively this document,1→21. No value chosen manually.
The census discloses a recoverable startxref warning on another PDF with matching
counts; all PDFs were readable for page metadata, no source was repaired.

| Artifact | SHA256 |
| --- | --- |
| [Erratum JSON](v5-objective-pagecount-erratum-doc10.json) | 80beb7c1f43e2266e20d7554196e852c80f84738ca27c5dd4a7a7b52abb28d6b |
| Ignored census JSON | f27ac3cd5e0c3b1f80667ed0ae9b8565794b16cddaccee010c7d9a6b283acc7f |
| Frozen manifest | c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62 |
| Frozen universe | dd64269956de6c7210fe0e8cc4cbb23dc799925adefa4c5e6dd603ff997c5933 |
| Original protocol | 77f8bb06d7c8eadba79c7ef70a580eebeff2d74f324017ae8e220f11bea9bb95 |
| Original Batch02 package | 33e9ba54c4ff51801a2fad094d0cf6613728494bd085697c4c8f53f42a166f01 |
| Resumed checkpoint | 9cc670b02a5105078328b6cd1b03acc77215c7db825ee07e08c5fa78ae04b305 |
| Original checkpoint | b9c79b68cc0544dc9f070de336ab9f9ccb18414eb58267f5100feef5ac3b70d6 |

Further raw/report/queue/Batch01/document3 decision/diagnostic bindings are in the JSON.
The ignored census and versioned technical report are bound by the same census hash.

## Selection invariance — static evidence, no rerun

`selectionInvariantToPageCountCorrection=true`, based on direct static inspection:

- `outputs/audit/holdout/v5-phase-a/prepare.py:172–183`: eligibility reasons depend
  on exposure, presence/error, answer-key role, required neutral metadata and
  duplicate fingerprint. pageCount is copied at180, not tested as a criterion.
- `audit/holdout/v5_document_selection.py:76`: consumes the frozen eligible flag;
  quotas58–73 depend on source capacities; cell52–53 on source/family/year-era/series.
- Ranking83–84 uses seed+fingerprint, fingerprint and canonicalPath; score98–106
  uses diversity/capacity counters and hash ties, never pageCount.
- Identity derives from fingerprint (verify144). pageCount only appears in the
  neutral-field whitelist32, not the selector's eligibility, quotas, strata,
  ranking, order or identity criteria. Source bytes and all such inputs unchanged.

Selector SHA256: `fda14af52b9aff1350942645fb89ae7a5332bafab7ec1a48e6df20876482dc74`.
Eligibility-preparation script SHA256: `af599d555140aee7d9fdbd5debfc6171957106d293e2434cac39070e17fbf618`.
Neither script was imported/executed or edited. No verifier/selection rerun.
Selected IDs/order, seed, quotas, tier/batch assignments and fingerprints remain frozen.

## Effective precedence for future derived artifacts

Historical frozen1 remains in manifest/universe/raw provenance/queue/package/context.
The explicit hash-identified erratum supplies effective21 only for future authorized
adjudication. Derived documents must propagate:

```text
sourceFrozenPageCount=1
effectivePageCount=21
pageCountErratum=audit/holdout/v5-objective-pagecount-erratum-doc10.json
pageCountErratumSha256=80beb7c1f43e2266e20d7554196e852c80f84738ca27c5dd4a7a7b52abb28d6b
```

Boundaries remain mandatory and must satisfy1≤pageStart≤pageEnd≤effectivePageCount.
No validator may simply ignore page limits. No validator/functional code changed here;
if future binding/schema support is needed, it requires a separate authorized step.
Do not silently substitute effective values into old frozen artifacts or checkpoints.
This contract does not create final question index or authorize question selection.

## Batch02 impact and preserved progress

Frozen package totalPhysicalPages120 remains historical. Independently verified
Batch02 effective total140; delta+20. Preserved progress: documents1–9 adjudicated,
115pages actually reviewed and194questions in resolved documents. Remaining25pages:
document10=21 and document11=4. No additional question-count estimate or new review.

Doc3 remains adjudicated only within frozen available PDF, with integrity inconclusive
and no original-exam completeness certification; the formal decision is unchanged.
Doc8's source-incompleteness decision remains in the resumed checkpoint; not reclassified.
Document10 remains stopped before visual adjudication;11 visually not started.
Structural page counting here is not manual question inspection or resumed review.

## Preservation, methodology and STOP

Preflight confirmed4884 historically bound files and protected152 additional current
files, including checkpoints/renders and current tracked/output evidence. Only the
three additive versioned technical artifacts plus incremental CONTEXTO and factual
ESTADO_ATUAL/AUDITORIA_PROVAS updates are authorized. Prior documentation history is
retained; ROADMAP untouched, Batch02/TierA NOT marked complete.
V1–V4/results/GT/caches, functional05C1, V5 PhaseA/B1/B2a, Batch01, Batch02 package,
original protocol/addendum, decisions/checkpoints and source PDF bytes remain preserved.
No core.autocrlf/config/line-ending normalization; no functional changes.

```text
postFreezeObjectiveMetadataErratum=true
performanceBlind=true
pdfOpenedForStructuralMetadata=true
manualQuestionInspection=false
contentExtraction=false
rendersCreated=false
ocrExecuted=false
selectedDocumentIdsChanged=false
sourcePdfChanged=false
questionSelectionExecuted=false
GTCreated=false
auditorExecuted=false
metricsSeen=false
finalQuestionIndexCreated=false
Batch02Incomplete=true
TierAComplete=false
phaseBComplete=false
merge=false
```

After authorized commit/push: STOP. Next separately authorized execution=resume
Batch02 neutral visual adjudication under this frozen erratum, from document10,
preserving1–9 and then11. Do not resume now, create Batch02 adjudication/final index,
prepare TierB, select questions, createGT, executeAuditor, calculate metrics or merge.
