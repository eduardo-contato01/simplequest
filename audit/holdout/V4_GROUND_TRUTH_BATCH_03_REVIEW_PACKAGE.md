# Ground Truth V4 — review package Batch 03

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-03`, com 3 documentos / 9 questoes, nas posicoes 7–9 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `8e257b79e7880d1405b5e5b4e1016733cc76e5ce`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-03-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-143e13dc75ed` | CMBel | 2018 | 6º Ano | raster | `143e13dc75ed1583aa4882cefbc4194d0ff1a46c25a80eeb70ad4361467d1dc5` |
| 2 | `doc-1693ea690bbb` | CMT | 2023 | 6º Ano | text_native | `1693ea690bbb39b7680d33da27ccdf0b1ba1415a3f6dcc47ae29cd10fc8f46f8` |
| 3 | `doc-1e18e7252399` | CMB | 2013 | 1º Ano | text_native | `1e18e72523997bdb75457f09eeb084ee5a69c70385c4a70263a627421a5bac5b` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-143e13dc75ed:q2` | 2 | 4 | 4 |
| `doc-143e13dc75ed:q13` | 13 | 11 | 11 |
| `doc-143e13dc75ed:q15` | 15 | 12 | 12 |
| `doc-1693ea690bbb:q3` | 3 | 3 | 3 |
| `doc-1693ea690bbb:q14` | 14 | 10 | 10 |
| `doc-1693ea690bbb:q28` | 28 | 18 | 18 |
| `doc-1e18e7252399:q1` | 1 | 2 | 2 |
| `doc-1e18e7252399:q10` | 10 | 5 | 5 |
| `doc-1e18e7252399:q16` | 16 | 8 | 8 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-143e13dc75ed.pdf`
- `02_doc-1693ea690bbb.pdf`
- `03_doc-1e18e7252399.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `d792db154da04f7403ffabda89e1efcc5f9c9d53fab3e7d89e9fd47b15a1a96d`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `7e916bb745d19d59b305d3bf29f1d0cf8dda7c332cad44fcdef4766df77f5167`.
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
