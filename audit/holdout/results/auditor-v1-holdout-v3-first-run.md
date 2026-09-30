# Auditor V1 — Structural Holdout report

- protocol: holdout-v3
- commit: c45e3491d95533ac10ac9e911c4fb03545c60e0f
- hashes: {'manifestSha256': '797dba3b37587e6fe4bf264c563f4c27668155e5f7284e5c132b648aa8dedebc', 'questionIndexSha256': '8c7c9bb2ac95d4d9811f3bbd1f122873fd0d8fc3fa31eb5f60ed55862949b066', 'groundTruthSha256': '5b8a0623c115db59872f196023bc5d2339fc739035da152a9ec9f81353f69034'}

## Metrics
- questions: 144 (executable 144)
- classes: {'correct': 68, 'partial': 1, 'safe_abstention': 50, 'unsafe_error': 6, 'not_applicable': 19, 'not_executable': 0}
- coverage: 0.6111  abstention: 0.3472
- question-level emitted precision: 0.92
- optionCount: {'applicable': 125, 'emitted': 75, 'correct': 69, 'precision': 0.92, 'coverage': 0.6, 'abstention': 0.4, 'undercount': 5, 'overcount': 1}
- optionLabels: {'applicable': 125, 'emitted': 71, 'correct': 69, 'precision': 0.9718, 'coverage': 0.568}
- unsafe_error: 6 (low 0 / medium-high 6)
- false conflict rate: 1.0 (1 conflicts)

## Documents
- documents without unsafe_error ratio: 0.8958
