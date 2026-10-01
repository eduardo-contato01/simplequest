# Holdout V3 Postmortem Fixes - Consolidated Validation

Date: 2026-10-01 07:52

## Scope

Base result-freeze commit:

`b3082e093df58d8054f1acda61183d52e5b1a605`

Validated postmortem head:

`28c4b887fe196d376b3bb2c4b3a59000a8e1198d`

Branch:

`audit/holdout-v3-postmortem-fixes`

The V3 holdout is already revealed and is historical diagnostic evidence.
This validation does **not** rerun the official V3 holdout and does **not**
claim post-fix unbiased performance on V3.

## Commit lineage

- `071222fbee89e16f02818712039d570e6ca30e3f`
- `1360746cbf039634bc25d5a14671619aa25d7dd8`
- `3981f1d7c50fd187549a079a0ac1ff57dc8370a1`
- `49d1b3ae4dadb2562bdb329a1281e3921be9b88d`
- `8a3e4476781db415810237f5dcfa29f88a388160`
- `28c4b887fe196d376b3bb2c4b3a59000a8e1198d`

## Changed files since result freeze

- `CONTEXTO_SIMPLEQUEST.md`
- `scripts/audit_observations_selftest.py`
- `scripts/audit_question_boundary.py`
- `scripts/audit_question_boundary_selftest.py`
- `scripts/audit_response_fusion.py`
- `scripts/audit_response_fusion_selftest.py`
- `scripts/audit_response_holdout.py`
- `scripts/audit_response_holdout_selftest.py`
- `scripts/audit_response_structure.py`
- `scripts/audit_response_structure_selftest.py`

## Safety and integrity

- Result-freeze base is an ancestor of the validated head.
- Local and remote branch heads matched before validation.
- Frozen Holdout V3 files were not modified by the postmortem branch.
- 8/8 pinned frozen artifact SHA-256 hashes matched.
- Original official raw output still contains exactly one run JSON and one run MD.
- Original raw JSON/MD remain byte-identical to the frozen tracked result.
- Official run stamp remains `20260930T190037Z`.
- No Holdout V3 rerun occurred.
- No known V3 document IDs, forensic artifact names, frozen result names,
  canonical corpus path, or Ground Truth V3 filename were found in the
  modified production logic.

## Technical validation

- Python compilation: PASS (9/9)
- Selftests: PASS (7/7)
- Runner import / `--help`: PASS
- `git diff --check`: PASS
- Expected diff scope: PASS

## Methodological status

The five postmortem patches are validated as regression fixes against synthetic
and unit-level checks derived from the revealed V3 failure families.

V3 must not be reused as an unbiased benchmark for these patches. Any future
claim about post-fix precision, coverage, abstention, or unsafe-error rate must
use a new unrevealed evaluation set or Holdout V4.

## Result

`CONSOLIDATED_POSTMORTEM_VALIDATION = PASS`
