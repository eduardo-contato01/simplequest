# PROTOCOL V2 — Auditor Structural Random Holdout

## Why V2 exists
- The V1 candidate frame still contained answer keys (gabaritos): 23/48 selected documents were outside the target population (question booklets).
- The issue was found during neutral question indexing, **before** question selection, ground truth or any structural Auditor run.
- V1 remains historical and byte-identical; it is classified `invalid_for_random_evaluation_due_to_sampling_frame`, not an Auditor failure.
- V2 corrects sampling-frame eligibility (metadata-only) and excludes **all 48 V1 content fingerprints** to preserve independence.

## Scope
Structural holdout only. Snapshots/reports are shadow; the Auditor functional pipeline is unchanged and frozen.

## Sampling frame (metadata-only)
Eligible = documents whose path/basename do not indicate an answer key:
- R1 `answer_key_directory`: a normalized path segment is `gabarito`/`gabaritos`.
- R2 `answer_key_filename`: basename starts with `gab_`.
- R3 `answer_key_filename`: basename contains the independent token `gabarito`/`gabaritos`.
Normalization: NFKD, remove combining accents, casefold, normalize `_ - . \ /` and whitespace; basename and path segments analyzed separately; mojibake is not used as a structural signal.
Ambiguous tokens (`resposta`, `resultado`, `solucao`, `chave`, `correcao`, `espelho`, `cartao`, `folha`, `rascunho`, `instrucoes`, `answer`) are **not** auto-excluded. No exclusion by questionsIndexed, questionMarkerPatterns, OCR/Auditor output, layout, option count, response mode, page count or visual quality.

## Exclusions (single reason per content unit)
Order: metadata valid → answer-key role → development fingerprint → V1 revealed fingerprint → duplicate content. Reasons: `answer_key_directory`, `answer_key_filename`, `development_fingerprint`, `v1_revealed_fingerprint`, `duplicate_content`, `invalid_metadata`.

## Versioning and seed
- `protocolVersion = holdout-v2`; `selectorVersion = holdout-v2`.
- `selectionSeed = 20260918` (kept: the pool changed by legitimate sampling-frame correction, not by observed Auditor performance).
- All 48 V1 fingerprints excluded (23 answer keys + 25 valid booklets already revealed/indexed).
- Development/control excluded by content fingerprint (source: `manifest-v1.provenance.json`).

## Target and quotas (frozen)
- `targetDocuments = 48`, `questionsPerDocument = 3` (one per tertile in the future B2).
- `sourceQuota`: `text_native=28`, `raster=14`, `text_low_quality=2`, `hybrid=4` (sum 48).
- `maxDocumentsPerFamily=4`, `minFamilies=10`, `minDistinctYears=10`, eras `2004-2009 / 2010-2014 / 2015-2019 / 2020-2025`.
- Clean V2 frame (metadata + content, pre-selection): unique eligible 583 → `text_native=386`, `raster=187`, `text_low_quality=2`, `hybrid=8`; 25 families; 22 years.
- `text_low_quality=2` consumes 100% of the known eligible stratum. In the future Phase A, if fewer than 2 unique eligible remain, **abort** with `selection_constraints_unsatisfied` (no silent redistribution).
- `hybrid=4` uses 4 of 8 eligible contents; revalidate ≥4 unique before selection, else **abort**.

## Unchanged from V1
Content-fingerprint identity, dedupe, deterministic selector, reserved pool policy, blind ground truth, Random vs Challenge separation, metrics, anti-contamination, future OCR policy (frozen config, cached, failures observable as not_executable).

## Provenance
Code identity is captured **before** any output written by the selection pipeline (regression guard for the V1 timing issue). The manifest records `protocolSha256`, `inventorySha256`, `candidatePoolHash`, `candidatePoolPathHash`, `gitCommit`, `selectionCodeState`, `selectorSha256`, `excludedByReason`, `v1ExcludedFingerprints`, `reservedPoolHash`, `reservedCount`.

## Future changes
New versions require new versioned files (`protocol-v3`, `manifest-v3`, …). No threshold tuning against final holdout metrics. The challenge set remains separate and must not use the 23 V1 answer keys as adversarial material.
