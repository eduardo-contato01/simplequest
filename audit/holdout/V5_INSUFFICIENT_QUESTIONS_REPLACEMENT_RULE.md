# Holdout V5 — insufficient independent question units replacement rule

## Authority, timing and scope

Explicit external decision on 2026-10-08; branch `audit/holdout-v5-blind`,
source HEAD `4a28656d22531ab7ee9f7b56e9b6cbce61fda860`.
Formal freeze is the commit introducing this addendum and the
[structured decision](v5-insufficient-questions-decision-doc11.json).

This is a **post-freeze, performance-blind protocol addendum**, not a rewrite of
[PROTOCOL_V5.md](PROTOCOL_V5.md) and not pre-registration before source inspection.
The original replacement policy did not include this reason. Its timing and effect
must appear in the final V5 methodological evaluation. This execution is exclusively
documentary and metadata-only: no PDFs opened, no new adjudication or replacement.

## Generic rule — all eight conditions required

Classification: `insufficient_independent_adjudicable_questions`.
A previously selected and frozen document, after neutral review of every available
page, offers fewer than `questionsPerDocument` independent, directly observable
identities with fully justified boundaries. The V5 minimum is three.

Replacement may be considered only when **all eight** conditions hold:

1. The document was selected and frozen before inspection.
2. Every available page has been fully reviewed under neutral policy.
3. Neutral evidence establishes fewer than the required three independent,
   completely adjudicable question identities.
4. No question, identity or boundary is fabricated to reach the minimum.
5. No GT, Auditor output or performance metric has been consulted.
6. A next still-eligible candidate exists in the SAME frozen stratum and ranking.
7. Its identity comes exclusively from the original ranking, without prior
   inspection of candidate content.
8. The decision is documented before any V5 question selection; an eventual
   replacement must also have explicit errata/provenance before selection.

Failure of any condition requires STOP for explicit resolution, not an automatic
cross-stratum swap, relaxed minimum or convenient source. The rule is generic across
families, document types and tiers, including future B/C/D cases. It is not a rule
for essays, CMSM or this particular PDF. OCR convenience, response type, layout
preference and expected performance are forbidden criteria.

The [source-incompleteness retention rule](V5_OBJECTIVE_SOURCE_INCOMPLETENESS_RULE.md)
is distinct: it requires sufficient directly adjudicable questions and no eligible
same-stratum substitute. The [doc3 integrity decision](V5_SOURCE_INTEGRITY_INCONCLUSIVE_DOC03.md)
and [doc10 pagination erratum](V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10.md) remain unchanged.

## Application — Batch02 document11, evidence not reopened

- Document: `v5-doc-a08230ae0b1cad7e`.
- Fingerprint: `a08230ae0b1cad7e06f3e15215d54d0e53526e3e5c6b11008f4295a5fb469d09`.
- CMSM / 2006 / 1º Ano / text_native / Tier A.
- Batch02 order11, global Tier A order22; four physical pages; historical raw count0.
- Existing neutral checkpoint: pages1–2 one unnumbered continuous block,
  page3 RASCUNHO, page4 blank body; all four pages reviewed.
- Fewer than three independent fully adjudicable identities proved:
  `minimumRequiredQuestions=3`, `minimumSatisfied=false`.
- No exact canonical total of zero or one is certified by this decision.
  Raw0 is historical metadata, not proof of a canonical count.
- No synthetic IDs, boundaries or paragraph splitting; historical unresolved
  status and all checkpoint decisions remain untouched.

The frozen path contains “redação”. That name is not a replacement criterion or
evidence of PDF corruption. Insufficient independent question identities do not
automatically establish corruption, missing pages, fingerprint drift or duplicate PDF.
This decision draws none of those conclusions.

All eight criteria are documented individually in the JSON. Metadata eligibility of
the next candidate does NOT certify its structural integrity or minimum question count.

## Original ranking — read-only metadata verification

Stratum: `["text_native","CMSM","2004-2009","1º Ano"]`.

Original seed:
`156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e`.

Ranking: `SHA256(seed + "|" + contentFingerprint)`; ties by literal fingerprint,
then literal canonicalPath. Only the four eligible rows in this frozen stratum
were ranked; the complete48 selector was neither imported nor executed.

| Rank | documentId | Ranking SHA256 |
| --- | --- | --- |
| 1 | `v5-doc-a08230ae0b1cad7e` | `6ce137f9c74bf544bb114596c0a7832842a1ebec402d88e344db8b9d106f3369` |
| 2 | `v5-doc-e1c73fb849ef80a6` | `949586a3f14297d8499cb7d89f588e175597fe480bfcc5c2c9b68d448e3d4b6e` |
| 3 | `v5-doc-d3a3743c1ccecc1a` | `b9d9543fa0aaf33166b97eb6b4a360d3fee18ff36d4c6730ec3c4b06625d9c95` |
| 4 | `v5-doc-76e602e26d866e2e` | `e5305924e2d3aa1a9590c3b10a245b9fb1f28a0ad96799fb31189e156ac473de` |

Rank1 is the sole original selected document in this stratum. Rank2 is still eligible
in the frozen universe and is absent from the historical manifest:

`replacementCandidate=v5-doc-e1c73fb849ef80a6`

`replacementCandidateContentFingerprint=e1c73fb849ef80a6f94a2ecf09718a963bd7c65008f930526605489ac25f8fe3`

Its PDF/content was NOT consulted. No candidate canonical count, minimum-three
certification or future selected question IDs are asserted or computed.

## Population, provenance and preservation

The historical manifest remains frozen with document11; no effective manifest,
physical/logical replacement or new supplemental package exists from this execution.
Current document selection is untouched. An eventual replacement WILL change the
effective document population and must have its own erratum/provenance linking the
historical and effective manifests, original ranking and this disclosed exception.
Do not claim the original selection remains fully unchanged after that future swap.

Preserved checkpoints under
`outputs/audit/holdout/v5-tier-a-batch-02-review/`:

| Checkpoint | SHA256 |
| --- | --- |
| adjudication-notes-post-pagecount-erratum.json | `5ca2d24c6ade38b3d7edebd98eb6b761b9ca0f368fefe0524d17427e8f094599` |
| adjudication-notes-resumed.json | `9cc670b02a5105078328b6cd1b03acc77215c7db825ee07e08c5fa78ae04b305` |
| adjudication-notes.json | `b9c79b68cc0544dc9f070de336ab9f9ccb18414eb58267f5100feef5ac3b70d6` |

Current checkpoint: documents1–10 adjudicated,214 canonical questions in those ten,
all140 effective physical pages of the original Batch02 reviewed; doc11 unresolved,
Batch02/Tier A/Phase B incomplete. Original package120-page metadata remains historical
under the separately frozen doc10 erratum; no original artifact is rewritten.

JSON bindings preserve original protocol/universe/manifest/raw/report/queue,
Batch02 package/context, Batch01 adjudication, doc3 decision, source-incompleteness
addendum, doc10 erratum, census and selector hashes. Functional Auditor/indexer,
V1–V4, sources, caches and existing review material are unchanged. No census rerun,
raw regeneration, new render, OCR, validator change or configuration normalization.

## Future conditional sequence — NOT authorized here

Next priority: **V5 objective replacement materialization and supplemental review package**.

A separate explicitly authorized execution must:

1. Materialize objective replacement with errata and historical/effective manifest
   provenance, keeping the original manifest immutable.
2. Confirm candidate fingerprint and structural integrity.
3. Prepare neutral supplementary artifacts under frozen indexer/configuration,
   without rerunning or modifying the original raw index.
4. Freeze a candidate-specific supplemental review package BEFORE visual adjudication.
5. Only then perform separately authorized neutral visual adjudication; its eligibility
   and minimum question count must be established, never assumed.

No step above is performed now; no final index, question selection, GT, Auditor,
metrics, Tier B preparation or merge. After this commit/push, STOP.

```text
postFreezeProtocolAddendum=true
preRegisteredBeforeSourceInspection=false
performanceBlind=true
replacementCandidateIdentified=true
replacementCandidatePdfOpened=false
replacementPerformed=false
effectiveManifestCreated=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
groundTruthStarted=false
auditorExecuted=false
metricsSeen=false
Batch02Incomplete=true
tierAComplete=false
phaseBComplete=false
```
