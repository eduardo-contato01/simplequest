# Ground Truth V4 — review package Batch 12

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-12`, com 3 documentos / 9 questoes, nas posicoes 34–36 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `decfc72df8326e0ddf9045c44bde7feba0524e3f`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-12-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-b71d45cbb12c` | CMM | 2018 | 6º Ano | text_native | `b71d45cbb12c198751e58f3771eafcea7c3f4d4c799d5b1f5666fcddfce53d27` |
| 2 | `doc-bb62e60cf7ed` | CMSM | 2023 | 1º Ano | text_native | `bb62e60cf7ed1c961bcba262fd6136972ae6796d3759d8d1ecda67aab6e8e0fb` |
| 3 | `doc-c41ddc7b55ec` | OUTRAS | 2021 | 6º Ano | raster | `c41ddc7b55ec4e18550e2be6decab59f307b6acc7699ab17e69b7f478330ca4e` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-b71d45cbb12c:q6` | 6 | 4 | 4 |
| `doc-b71d45cbb12c:q14` | 14 | 6 | 6 |
| `doc-b71d45cbb12c:q15` | 15 | 6 | 6 |
| `doc-bb62e60cf7ed:q9` | 9 | 7 | 7 |
| `doc-bb62e60cf7ed:q19` | 19 | 13 | 13 |
| `doc-bb62e60cf7ed:q27` | 27 | 20 | 20 |
| `doc-c41ddc7b55ec:q2` | 2 | 3 | 3 |
| `doc-c41ddc7b55ec:q10` | 10 | 3 | 3 |
| `doc-c41ddc7b55ec:q18` | 18 | 4 | 4 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-b71d45cbb12c.pdf`
- `02_doc-bb62e60cf7ed.pdf`
- `03_doc-c41ddc7b55ec.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `967a5615300afdddb40e6108caf02793e59d9a1d714f11643ab47f636431b40b`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `a314344a6c8baf6c957a4378c6c293cf38d14390bd1bfbb2a933c608f7474365`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta. Nenhum recorte, conversao, OCR ou modificacao dos PDFs.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 11–13: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao documental ou de questoes com os Batches 01–10.
- Batches 01–10 byte-preservados e humanamente adjudicados; progresso permanece 90/144, com 10/16 batches concluidos e 6 pendentes. As novas 27 questoes aguardam adjudicacao humana.
- `questionSelectionExecuted=true`; `selectionReexecuted=false`; 144 selected IDs preservados, mapping SHA256 `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Zero rotulos automaticos de GT: responseMode, optionCount, optionLabels, subitems, responseControls, layout, markerStyle e contentKind nao preenchidos nem inferidos.
- Nenhum JSON de GT 11–13 criado; nenhum GT final criado. Nenhum Auditor output ou gabarito consultado. Nenhum Batch 14 preparado; nenhum merge. Revisao humana pendente.
