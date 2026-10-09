# V5 Tier A Batch02 - effective neutral adjudication

V5_TIER_A_BATCH_02_ADJUDICATED=PASS

## Effective completion and preserved history

Branch `audit/holdout-v5-blind`; source HEAD
`43ba7cd04340ea633d73761263a4f973a7d06e57`.
11 effective documents,148/148 physical pages reviewed,234 canonical questions,
effective unresolved0. This is Batch02 adjudication, NOT the final48-document index.

Documents1-10 and all214 canonical questions imported exclusively and exactly from
the preserved post-pagecount-erratum checkpoint, without opening their PDFs,
reinterpreting decisions or changing any question object. Document11 is the
[separately validated supplement](V5_TIER_A_BATCH_02_SUPPLEMENTAL_ADJUDICATION.md):
12/12 pages,20 canonical questions, raw18, delta+2, minimum3 PASS.
Original doc11 `v5-doc-a08230ae0b1cad7e` remains unresolved in unchanged history;
its full checkpoint is preserved as historical provenance, not promoted to adjudicated.
The unresolved canonical0 placeholder is not a new certification of the old source count.

## Raw/canonical reconciliation

| Order | Effective document | Raw | Canonical | Effective reviewed pages | Status |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | v5-doc-84179ac96b058ffb | 24 | 40 | 25 | adjudicated |
| 2 | v5-doc-e123ad77b8edc98f | 9 | 21 | 12 | adjudicated |
| 3 | v5-doc-815b83630e3d8c98 | 20 | 21 | 9 | adjudicated |
| 4 | v5-doc-e9603e9180e6028b | 4 | 15 | 12 | adjudicated |
| 5 | v5-doc-1babdc250c302165 | 11 | 21 | 18 | adjudicated |
| 6 | v5-doc-d5099c3057735940 | 5 | 15 | 13 | adjudicated |
| 7 | v5-doc-0c51e49589f148bc | 13 | 19 | 12 | adjudicated |
| 8 | v5-doc-02531e2612ade970 | 10 | 20 | 6 | adjudicated_source_incomplete |
| 9 | v5-doc-87d7a7f5696b5a6a | 9 | 22 | 8 | adjudicated |
| 10 | v5-doc-74e153f9c146d887 | 4 | 20 | 21 | adjudicated |
| 11 | v5-doc-e1c73fb849ef80a6 | 18 | 20 | 12 | adjudicated |
| Total | 11 | 127 | 234 | 148 | resolved |

Historical raw109 - replaced historical raw0 + supplemental raw18 = effective raw127.
Canonical214 preserved +20 supplemental =234; deltaVsEffectiveRaw=+107.
These are neutral structural counts, NOT Auditor metrics.
Original package120pages remains immutable. Original physical set after doc10 erratum
had140 reviewed pages, including removed doc11's4. Retained136 + replacement12 =148.
The removed4 reviewed historical pages are not counted in the effective148.

## Permanent methodological caveats

- Doc3 `v5-doc-815b83630e3d8c98`: adjudicated only in frozen_available_pdf_content;
  sourceIntegrityInconclusive=true, originalExamCompletenessCertified=false;
  no replacement. [External decision](V5_SOURCE_INTEGRITY_INCONCLUSIVE_DOC03.md)
  SHA256 `d532deef877a016d4715227395d80f402e3ec49659eea4409dd280ad364be7a4`.
- Doc8 `v5-doc-02531e2612ade970`: adjudicated_source_incomplete; all six frozen
  retention criteria PASS; printedpage1 unavailable, content unknown, no absent
  identity or boundary fabricated. Available6pages and20observed questions only.
- Doc10 `v5-doc-74e153f9c146d887`: sourceFrozenPageCount1/effectivePageCount21.
  Historical pageCount remains1 in the imported object; ranges use effective21
  under [erratum](V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10.md) SHA256
  `80beb7c1f43e2266e20d7554196e852c80f84738ca27c5dd4a7a7b52abb28d6b`.
- Effective doc11 `v5-doc-e1c73fb849ef80a6`: disclosed post-freeze, performance-blind
  replacement from original same-stratum ranking2, inherited slot47/11/22,
  manifest effectiveR1 and supplemental package/adjudication. No global selector rerun.
  Authoritative size182017; pdfinfo size0 remains nonblocking by explicit decision,
  cause not determined, not classified as corruption.

Transport all these caveats and timing/provenance to future final index and V5 evaluation.
Original freezes remain historical, not retroactively rewritten or presented as preregistration.

## Validation and preservation

Independent neutral V5 gates PASS:11distinct document IDs/fingerprints; effective
pages148; at least3 fully adjudicable identities per document; duplicate IDs0;
duplicate canonical numbers within each document0; invalid ranges0; batch leakage0;
fabricated questions0; prior question differences0; all source bindings reconciled.
Prior document records1-10 also structurally equal to their frozen checkpoint.
No mask as V4, no functional/legacy-validator modification, no compatibility claim
for the future official Auditor run. That compatibility remains a separate gate.

Batch01 verified unchanged:11/11 documents,182pages,1136canonical, unresolved0.
Together TierA22/22documents complete; TierAComplete=true; PhaseBComplete=false.
TierB/C/D pending; no global index,144-question selection, GT, Auditor, metrics or merge.

All historical checkpoints, V1-V4, baseline05C1/indexer, V5 protocol/universe,
historical/effective manifests, raw indices/reports, queue, packages, Batch01,
decisions/rules/errata/census, sources/copies/caches remain byte-preserved.
No Git configuration or line-ending normalization. Only new adjudication artifacts,
ignored notes/renders and authorized documentation updates are produced.

## Hash bindings

| Artifact | SHA256 |
| --- | --- |
| [Batch02 effective adjudication](question-index-v5-tier-a-batch-02-adjudication.json) | b2447bf2a0d86e231480902ae26ddd6dcc21ecb58d84648e432ccd5355df0bf3 |
| [Supplemental adjudication](question-index-v5-tier-a-batch-02-supplemental-adjudication.json) | cebf725d79702ce5bad17049e7f5090bf74f61d050f3da71f1cb64d03f3a486b |
| Historical checkpoint post-erratum | 5ca2d24c6ade38b3d7edebd98eb6b761b9ca0f368fefe0524d17427e8f094599 |
| Historical checkpoint resumed | 9cc670b02a5105078328b6cd1b03acc77215c7db825ee07e08c5fa78ae04b305 |
| Historical checkpoint original | b9c79b68cc0544dc9f070de336ab9f9ccb18414eb58267f5100feef5ac3b70d6 |
| New supplemental notes, ignored | d96192505fd51a627305bb11fa6ff28370371cbaf64fc9a793cde278f6e92b98 |
| Batch01 adjudication | e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770 |
| Supplemental package | 350c0edadf4ed0f6f10b85ac00ef9dcc8b61bbb1a2c780ae887bdec0276d8f0f |
| Effective manifestR1 | a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32 |

## State and mandatory STOP

tierABatch01Adjudicated=true; tierABatch02Adjudicated=true; batch02Complete=true;
TierAComplete=true; TierADocumentsAdjudicated=22; PhaseBComplete=false;
finalQuestionIndexCreated=false; questionSelectionExecuted=false;
groundTruthCreated=false; auditorExecuted=false; metricsSeen=false; merge=false.

Next SEPARATE task: **V5 Tier B neutral review package freeze**.
After this single authorized commit/push and remote SHA confirmation, STOP;
do not prepare TierB, start C/D, create global index/selection/GT, run Auditor,
calculate metrics or merge.
