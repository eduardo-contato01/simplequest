# Holdout V4 Selector Freeze

## Status

`V4_SELECTOR_FROZEN = PASS`

No real V4 document selection was executed during this stage.

The V4 protocol and candidate pool remain frozen.

## Selector

V4 wrapper:

`scripts/audit_holdout_v4_select.py`

SHA-256:

`e6a46acb47d29b75dee6c643be07452b734f27b56565ccfcbfff9169d899a416`

Generic deterministic selector:

`scripts/audit_response_holdout_select.py`

SHA-256:

`a13f6cc0f53228c6464caf5fab8b8abcf9481f95d5c87b3844a8415164733e27`

## Frozen behavior

- protocolVersion must be `holdout-v4`
- candidate-pool file hash must match protocol
- candidate-pool canonical JSON hash must match protocol
- fingerprint-set hash must match protocol
- source/era/family/year frame metadata must match
- seed override is forbidden
- working tree must be clean during real selection
- output cannot overwrite an existing manifest
- selection constraints come only from frozen protocol
- no alternate-seed search exists in this wrapper

## Validation

Synthetic selector selftest: PASS

Real V4 selection executed: false

Question selection executed: false

Ground Truth created: false

Auditor executed: false

## Next step

After this selector freeze is committed and pushed, the real candidate pool may
be processed exactly once with seed `20261001`.

`V4_SELECTION_EXECUTED = false`
