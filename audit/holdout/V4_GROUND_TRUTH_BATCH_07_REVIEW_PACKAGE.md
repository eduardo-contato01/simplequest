# Ground Truth V4 — review package Batch 07

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-07`, com 3 documentos / 9 questoes, nas posicoes 19–21 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `ad56c700fe73db35407943f700dcfa24176fc1c7`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-07-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-56268e79f6bf` | CMSM | 2018 | 6º Ano | raster | `56268e79f6bf85a1cf08f2a97c69217adfd3410cd126f0ec1e7f5744e0fa0d1e` |
| 2 | `doc-591f3e819d58` | CMC | 2017 | 6º Ano | raster | `591f3e819d5810c359b2a0d9e8a32cdc54a7c6245e0b3cf03d9521a46ee7b3f8` |
| 3 | `doc-5d61be2ac853` | CMJF | 2015 | 6º Ano | raster | `5d61be2ac8537a32577aa37aab20221820b7499b2488f292ac60f49397170fc8` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-56268e79f6bf:q6` | 6 | 8 | 8 |
| `doc-56268e79f6bf:q11` | 11 | 13 | 13 |
| `doc-56268e79f6bf:q14` | 14 | 16 | 16 |
| `doc-591f3e819d58:q10` | 10 | 5 | 5 |
| `doc-591f3e819d58:q19` | 19 | 8 | 8 |
| `doc-591f3e819d58:q21` | 21 | 9 | 9 |
| `doc-5d61be2ac853:q3` | 3 | 8 | 8 |
| `doc-5d61be2ac853:q5` | 5 | 8 | 8 |
| `doc-5d61be2ac853:q11` | 11 | 9 | 9 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-56268e79f6bf.pdf`
- `02_doc-591f3e819d58.pdf`
- `03_doc-5d61be2ac853.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `33134d583a8ff550d39b399618a343f45cdb9dd578c9fb8bcee7ba780dc6bc08`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `27680a2b0029ef4bf0757fb0e0189ddaf57c6ba8d94dcf056ed76101b86e5950`.
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
