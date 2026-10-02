# Ground Truth V4 — review package Batch 06

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-06`, com 3 documentos / 9 questoes, nas posicoes 16–18 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `ad56c700fe73db35407943f700dcfa24176fc1c7`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-06-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-42af2b3d2b27` | CMPA | 2019 | 1º Ano | raster | `42af2b3d2b27f4028c36e7298f79cfe81291db82e6b7bd098bcaa1e34c9f41ec` |
| 2 | `doc-4310686d43a6` | CMBH | 2016 | 6º Ano | text_native | `4310686d43a6869a4470e38db614688ebde542a860b04ebeb0b742649fec4ac4` |
| 3 | `doc-44ea716ed9b7` | PAS 1 | 2016 | null | text_native | `44ea716ed9b726f56e3a6243bf6c3822f168b051b02b00ae85c742719fd888de` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-42af2b3d2b27:q1` | 1 | 3 | 3 |
| `doc-42af2b3d2b27:q12` | 12 | 14 | 14 |
| `doc-42af2b3d2b27:q16` | 16 | 17 | 17 |
| `doc-4310686d43a6:q2` | 2 | 3 | 3 |
| `doc-4310686d43a6:q8` | 8 | 4 | 4 |
| `doc-4310686d43a6:q14` | 14 | 7 | 7 |
| `doc-44ea716ed9b7:q22` | 22 | 6 | 6 |
| `doc-44ea716ed9b7:q54` | 54 | 9 | 9 |
| `doc-44ea716ed9b7:q88` | 88 | 15 | 15 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-42af2b3d2b27.pdf`
- `02_doc-4310686d43a6.pdf`
- `03_doc-44ea716ed9b7.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `96aed2434f2c3f404e077e595b1faca9b4a7a1f3327858ff89cd2741c78e6dda`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `3919d03b4731fc398618c3a14cfa963cbf397d7bf7407b56946a031a126b72b8`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 05–07: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao com os Batches 01–04.
- Batches 01–04 preservados e humanamente adjudicados; progresso permanece 36/144, com 12 batches pendentes e 27 questoes adicionais aguardando revisao humana.
- `questionSelectionExecuted=true`, sem alterar ou reexecutar selecao.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Nenhum campo de Ground Truth preenchido; nenhum JSON de GT dos Batches 05–07 criado. Nenhum Auditor output ou gabarito consultado. Revisao humana pendente.
