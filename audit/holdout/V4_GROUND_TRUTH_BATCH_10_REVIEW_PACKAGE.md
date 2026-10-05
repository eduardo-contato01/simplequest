# Ground Truth V4 — review package Batch 10

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-10`, com 3 documentos / 9 questoes, nas posicoes 28–30 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `5dbae24861fe4270ce5b7f69ec7d6d191ef6d2cc`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-10-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-9832ec9bb87d` | CMRJ | 2013 | 6º Ano | text_native | `9832ec9bb87dfbf843c744234a29bc6791f7d0461029ba1fdfc6e0816dc46f82` |
| 2 | `doc-9e4d161e7bfb` | CMM | 2013 | 1º Ano | text_native | `9e4d161e7bfb2507917bd7e83efe6cae3de1905e33cb469e7e7b870b48246702` |
| 3 | `doc-a1ddc006ef56` | CMVM | 2025 | 6º Ano | raster | `a1ddc006ef5638f1ead8e452334e2db87a1e9995e02261b34cecb64c8e3b043e` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-9832ec9bb87d:q1` | 1 | 2 | 2 |
| `doc-9832ec9bb87d:q8` | 8 | 4 | 4 |
| `doc-9832ec9bb87d:q20` | 20 | 8 | 8 |
| `doc-9e4d161e7bfb:q2` | 2 | 2 | 2 |
| `doc-9e4d161e7bfb:q12` | 12 | 8 | 8 |
| `doc-9e4d161e7bfb:q17` | 17 | 10 | 10 |
| `doc-a1ddc006ef56:q2` | 2 | 2 | 2 |
| `doc-a1ddc006ef56:q23` | 23 | 12 | 12 |
| `doc-a1ddc006ef56:q28` | 28 | 15 | 15 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-9832ec9bb87d.pdf`
- `02_doc-9e4d161e7bfb.pdf`
- `03_doc-a1ddc006ef56.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `3e213229352cf48a86f1dda46b2853863be593dd35a2c557b649d26fa95a8034`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `e2f44d50c949996db599cf1cca05c6a7c45cf2c661c90b3e25ab7080dce46f00`.
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
