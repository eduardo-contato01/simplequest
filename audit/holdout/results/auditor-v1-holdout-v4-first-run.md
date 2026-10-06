# Auditor V1 — Structural Holdout report

- protocol: holdout-v4
- commit: 394ce73f38848ec90f520a25b8d3ce71dd14099a
- hashes: {'manifestSha256': '26d76c5938b54a92a88b69552db8652ef61e0fb69fc0028cb55b001d20be55d4', 'questionIndexSha256': '89d852af97c30bc39607d54fc8017c484f0ae3fea8af09a78e29f17311f3a62d', 'groundTruthSha256': '90486a8a0fd03ca15aa1688ce702654fa0c8dc88eac9c517661692beb8fda6ba'}

## Metrics
- questions: 144 (executable 144)
- classes: {'correct': 60, 'partial': 1, 'safe_abstention': 66, 'unsafe_error': 5, 'not_applicable': 12, 'not_executable': 0}
- coverage: 0.5208  abstention: 0.4583
- question-level emitted precision: 0.9242
- optionCount: {'applicable': 132, 'emitted': 65, 'correct': 60, 'precision': 0.9231, 'coverage': 0.4924, 'abstention': 0.5076, 'undercount': 2, 'overcount': 3}
- optionLabels: {'applicable': 132, 'emitted': 65, 'correct': 63, 'precision': 0.9692, 'coverage': 0.4924}
- unsafe_error: 5 (low 0 / medium-high 5)
- false conflict rate: 1.0 (1 conflicts)

## Documents
- documents without unsafe_error ratio: 0.8958
