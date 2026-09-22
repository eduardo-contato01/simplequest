# Auditor V1 — Structural Holdout report

- protocol: holdout-v2
- commit: bde7d961ee982bd50dc1c0a79b6519356556f57d
- hashes: {'manifestSha256': '738bb8398aa6e168223116bd69547d47f9df03ba6bc6523ac073118dee733e60', 'questionIndexSha256': None, 'groundTruthSha256': '8c1b61c7fbbb5a8a6031b8056c1f265f97622c2d8dac1a0ae27f6eef66cbfee6'}

## Metrics
- questions: 144 (executable 138)
- classes: {'correct': 21, 'partial': 12, 'safe_abstention': 33, 'unsafe_error': 59, 'not_applicable': 13, 'not_executable': 6}
- coverage: 0.8913  abstention: 0.2391
- question-level emitted precision: 0.3708
- optionCount: {'applicable': 122, 'emitted': 80, 'correct': 24, 'precision': 0.3, 'coverage': 0.6557, 'abstention': 0.3443, 'undercount': 5, 'overcount': 54}
- optionLabels: {'applicable': 122, 'emitted': 82, 'correct': 81, 'precision': 0.9878, 'coverage': 0.6721}
- unsafe_error: 59 (low 0 / medium-high 59)
- false conflict rate: 1.0 (15 conflicts)

## Documents
- documents without unsafe_error ratio: 0.375
