# Ground Truth V4 — review package Batch 08

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-08`, com 3 documentos / 9 questoes, nas posicoes 22–24 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `5dbae24861fe4270ce5b7f69ec7d6d191ef6d2cc`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-08-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-6381aed53bb1` | CMJF | 2023 | 6º Ano | text_native | `6381aed53bb131b730a31a328b679e479c6e3e14e796e24f49a7bcb1302d7c7b` |
| 2 | `doc-6dde932fb681` | CMM | 2013 | 1º Ano | text_native | `6dde932fb681b017099925612def8c5d325c9cc899ad7a35f97d56cb07c5b4ae` |
| 3 | `doc-7f0815783d8c` | CMC | 2012 | 6º Ano | text_native | `7f0815783d8c21fcfa4b6022fca3b131df5b7be91e3e4a87784dd86f7ad21de0` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

Atencao: `doc-6381aed53bb1:q5` ocupa as paginas 4–5 (`pageStart=4`, `pageEnd=5`); range de duas paginas preservado, sem colapsar.

Errata upstream refletida: `doc-6381aed53bb1:q19` — page range corrected upstream from 14-14 to 14-15 before human GT adjudication. Ver [errata objetiva](V4_OBJECTIVE_ERRATUM_Q19_PAGE_RANGE.md).

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-6381aed53bb1:q5` | 5 | 4 | 5 |
| `doc-6381aed53bb1:q19` | 19 | 14 | 15 |
| `doc-6381aed53bb1:q36` | 36 | 25 | 25 |
| `doc-6dde932fb681:q6` | 6 | 5 | 5 |
| `doc-6dde932fb681:q7` | 7 | 6 | 6 |
| `doc-6dde932fb681:q19` | 19 | 14 | 14 |
| `doc-7f0815783d8c:q1` | 1 | 3 | 3 |
| `doc-7f0815783d8c:q8` | 8 | 4 | 4 |
| `doc-7f0815783d8c:q21` | 21 | 8 | 8 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-6381aed53bb1.pdf`
- `02_doc-6dde932fb681.pdf`
- `03_doc-7f0815783d8c.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `9750e983410f903efba2508c86c6faf92298a0bc0891f94848ca97e55c6ee16c`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `8a0e1638b76b193df844d7a9192a74560e9128c1ab5242dfe5bc6a780ed56a2a`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 08–10: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao com os Batches 01–07.
- Batches 01–07 preservados e humanamente adjudicados; progresso permanece 63/144, com 9 batches pendentes e 27 questoes adicionais aguardando revisao humana.
- `questionSelectionExecuted=true`, sem alterar ou reexecutar selecao.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Nenhum campo de Ground Truth preenchido; nenhum JSON de GT dos Batches 08–10 criado. Nenhum Auditor output ou gabarito consultado. Revisao humana pendente.
