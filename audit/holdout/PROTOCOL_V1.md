# PROTOCOL V1 — Auditor Structural Holdout

## Purpose
Measure structurally, without adapting heuristics to the samples:
structural precision, coverage, abstention, false structural promotion, false conflicts,
`optionCountHypothesis` precision, `optionLabelsHypothesis` precision, and behaviour by
layout/family/source.

## Random vs Challenge
- **Random/stratified holdout** (`manifest-v1.json`): representative behaviour.
- **Challenge set** (`challenge-v1.json`): adversarial robustness.
- Metrics are **never** merged. The 12 development benchmarks
  (`CMBH17 Q2/Q5/Q19`, `CMC11 Q14`, `CMBH18 Q2`, `CMBel17 Q7`, `CMT22 Q15/Q30`, `PAS19 24/75/87/90`)
  are **development/control** and may not appear in either set.

## Selection (random)
- Source: `outputs/audit/corpus-inventory.json`.
- Only independent metadata may be used: file access, validity, fingerprint, family,
  year, series, sourceClass, pageCount, duplicate, explicit development exclusion.
- **Forbidden** for random selection: `responseMode`, `optionCount`, `optionLabels`,
  `markerStyle`, `layout`, `contentKind`, grid/fraction/circles, `questionMarkerPatterns`,
  or any Auditor output that would indicate a "easy" document.
- Target: **48 documents × 3 questions ≈ 144 questions**.
- Constraints: ≤4 documents per family; ≥10 families; ≥10 distinct years; era coverage
  `2004-2009`, `2010-2014`, `2015-2019`, `2020-2025`.
- Source quota (deliberate oversampling of `hybrid`): `text_native=20`, `raster=12`,
  `text_low_quality=12`, `hybrid=4`. Main metrics are reported for the selected set and
  by `sourceClass`; corpus-weighted estimates are **not** the primary metric in V1.
- Deterministic PRNG with an explicit `selectionSeed` (no timestamp, no implicit random).
- Same inventory + config + seed ⇒ identical selection.
- Quotas/constraints that cannot be met produce `selection_constraints_unsatisfied` with
  quota/availability/reason. No silent substitution.
- Eligible, non-selected documents form a **reserved pool**; only `reservedCount` and
  `reservedPoolHash` are recorded. The reserved pool must not be inspected structurally.
- Implementation: `scripts/audit_response_holdout_select.py` (Phase A documents, Phase B questions).

## Question index (neutral)
`question-index-v1.json` contains per document only `documentId`, `fingerprint` and, per
question, `questionId`, `questionNumber`, `pageStart`, `pageEnd`. It contains **no**
mode/count/marker/layout/difficulty information. Production/review may be human or neutral tooling.

## Question selection (3 per document)
Once the index is frozen, split the document's question sequence into tertiles
(first/middle/last) and pick one question deterministically (seeded) inside each tertile.
Fewer than 3 questions: take all questions in order (`n=0→0`, `n=1→1`, `n=2→2`).
Selection never uses layout/content.

## Blind workflow
1. select documents (Phase A);
2. materialise and freeze `manifest-v1.json`;
3. produce the neutral question index;
4. seeded question selection (Phase B), freeze final list;
5. a human produces `ground-truth-v1.json` looking **only** at the canonical PDF;
6. freeze ground truth + SHA-256 hashes;
7. only then run the Auditor.
Ground truth is never pre-filled with Auditor output.

## Ground truth
`ground-truth-v1.json`, one entry per question: `documentId`, `questionId`, `pages`,
`responseMode`, `optionCount`, `optionLabels`, `subitems`, `responseControls`, `layout`,
`markerStyle`, `contentKind`, `notes` (null where not applicable). It describes **structure
only** — no correct answer, no full text, no textual fidelity.

Controlled enums:
- responseMode: `single_choice`, `true_false`, `numeric`, `discursive`, `other`, `unknown`
- layout: `vertical`, `two_column`, `grid`, `parent_child`, `internal_enumeration`, `mixed`, `none`, `unknown`
- markerStyle: `textual`, `parenthesized`, `circled_outline`, `circled_filled`, `symbolic_control`, `none`, `mixed`, `unknown`
- contentKind: `text`, `math`, `media`, `mixed`, `none`, `unknown`

## Metrics
- coverage, abstention, questionLevelEmittedPrecision;
- optionCount: applicable/emitted/correct/precision/coverage/abstention + undercount/overcount;
- optionLabels: applicable/emitted/correct/precision/coverage;
- unsafe_error split by interpretation confidence (low vs medium/high — main risk metric);
- false conflict rate.
`null` is **not** automatically abstention: applicability comes from ground truth
(numeric/discursive with no options ⇒ `not_applicable`, not abstention).

Result categories: `correct`, `partial`, `safe_abstention`, `unsafe_error`,
`not_applicable`, `not_executable`. `not_executable` is never an abstention.
`optionCountHypothesis` null when applicable is `safe_abstention`; an emitted wrong count is
`unsafe_error` with direction `under`/`over`.

Document-level summary is produced in addition to question-level metrics
(`documentHasUnsafeError`, `documentsWithoutUnsafeErrorRatio`). Slices with N<20 are
`descriptiveOnly=true`. Promotion readiness is diagnostic only — no automatic boolean and
no hardcoded threshold.

## OCR policy (future execution phase)
OCR generation is permitted only as preparation: frozen configuration, same for the whole
applicable split, never retuned from holdout results, outputs cached. OCR failures stay
observable as `not_executable` (no silent document substitution). No OCR in this round.

## Anti-contamination
Development cases must not appear in the manifest; duplicate fingerprints must not appear
in incompatible splits; the runner never edits manifest/ground truth. After a case is
inspected and code changes because of it, that case ceases to be independent evidence and
moves to `development/regression`; a later evaluation requires a reserved unseen subset or
a new versioned manifest.

## Content identity and freeze
- `path`, `relativePath`, filename and `documentId` are **not** content fingerprints.
- `contentFingerprint` = SHA-256 of the canonical PDF bytes. `documentId` is derived from it
  (`doc-<fingerprint[:12]>`), so moving a file does not create a new candidate/document.
- Candidate dedupe is by `contentFingerprint`. For byte-identical copies, the canonical
  path is the lexicographically smallest `normalizedRelativePath`; other paths are recorded
  in `duplicatePaths`/`duplicateCount` and never counted as independent documents.
- Development/control exclusion uses `contentFingerprint` (a byte-identical copy of a
  development PDF in another folder is excluded automatically); a path guard remains as a
  complement.
- `validate_no_content_overlap` rejects the same `contentFingerprint` appearing in
  development, random holdout and challenge at once.
- `candidatePoolHash` is canonical over `(contentFingerprint, family, year, series, sourceType)`
  sorted deterministically; `candidatePoolPathHash` is an optional operational hash over paths.
  `reservedPoolHash` hashes sorted unique content fingerprints; `reservedCount` counts unique
  content documents.
- The manifest records provenance frozen at selection time: `protocolVersion`,
  `selectorVersion`, `selectionSeed`, `protocolSha256`, `inventorySha256`,
  `candidatePoolHash`, `gitCommit`, `selectionCodeState` (`clean`/`dirty`), and
  `selectorSha256` as fallback. Dirty working tree is allowed but recorded.
- `question-index-v1.json` references documents by `documentId` + `contentFingerprint`;
  `validate_bindings` rejects a mismatch against the manifest. `ground-truth-v1.json` binds
  via `manifestSha256` and/or `documentFingerprints`; a GT built for one PDF version cannot
  be evaluated against another.
- The runner verifies each document's `contentFingerprint` before executing; a mismatch
  yields `source_fingerprint_mismatch` and the document/question is `not_executable`
  (no automatic fingerprint update, no silent substitution).
- Fingerprint cache (`outputs/audit/holdout/content-fingerprints.json`) keys by path with
  `sizeBytes`/`mtimeNs`; entries are recomputed when size or mtime changes. The frozen
  manifest still stores the SHA-256 of content.
- No bulk hashing of the corpus is performed before the real selection preflight.

## Future changes
Protocol changes require a new versioned file (`protocol-v2`, `manifest-v2`, …). No tuning
of thresholds against the final holdout metrics.
