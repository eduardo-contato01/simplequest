# Ground Truth V4 — review package Batch 04

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-04`, com 3 documentos / 9 questoes, nas posicoes 10–12 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `8e257b79e7880d1405b5e5b4e1016733cc76e5ce`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-04-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-27775227a392` | CMF | 2022 | 6º Ano | text_native | `27775227a392c3acfe055f03b7ad4e6563b6718d3d597a07fc3b9c3a35ccac3f` |
| 2 | `doc-2790a3c9786b` | CMBel | 2019 | 1º Ano | raster | `2790a3c9786b6786e7e06da4583ca7dee76a931bd8fb23d8e504fab3dbed5f97` |
| 3 | `doc-3971adb7884f` | CMRJ | 2017 | 6º Ano | text_native | `3971adb7884fc87184ecbb9c32f05952f9b2a3fbd2c5b54b1c428c664fb0bb9e` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-27775227a392:q1` | 1 | 1 | 1 |
| `doc-27775227a392:q14` | 14 | 9 | 9 |
| `doc-27775227a392:q26` | 26 | 15 | 15 |
| `doc-2790a3c9786b:q4` | 4 | 4 | 4 |
| `doc-2790a3c9786b:q13` | 13 | 11 | 11 |
| `doc-2790a3c9786b:q14` | 14 | 11 | 11 |
| `doc-3971adb7884f:q3` | 3 | 3 | 3 |
| `doc-3971adb7884f:q12` | 12 | 7 | 7 |
| `doc-3971adb7884f:q15` | 15 | 8 | 8 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-27775227a392.pdf`
- `02_doc-2790a3c9786b.pdf`
- `03_doc-3971adb7884f.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `09cac341893555fa0af5976cf5a909679843a743c02fc829f41f791d372c7006`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `6fc62d00935bc3f43869add9ba10fe99ab8b5203a592fa022102062824cf3df0`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 02–04: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao com o Batch 01.
- Batch 01 preservado; `questionSelectionExecuted=true`, sem alterar ou reexecutar selecao.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Nenhum campo de Ground Truth preenchido; nenhum JSON de GT dos Batches 02–04 criado. Nenhum Auditor output ou resultado V4 consultado. Revisao humana pendente.
