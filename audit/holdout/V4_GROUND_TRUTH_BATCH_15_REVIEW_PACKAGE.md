# Ground Truth V4 — review package Batch 15

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-15`, com 3 documentos / 9 questoes, nas posicoes 43–45 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `4fcc6b11e9ef510bc62549efb7970a8683706ed6`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-15-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-e13d030b1f9e` | CMT | 2024 | 1º Ano | text_native | `e13d030b1f9e1e9e61c06f930a8cc35583413459ead8f3213b032d98b48c4cb7` |
| 2 | `doc-ee51036d2382` | OUTRAS | 2024 | 6º Ano | text_native | `ee51036d2382d989fd2423ca1e0a7dfaf7ec8c389d49299e65580ade166d4270` |
| 3 | `doc-eefc3d15076e` | CMBH | 2025 | 1º Ano | raster | `eefc3d15076e47cc143d5b5dd62ebeeed0dc0c206bf07c67ef166bf19ed609c3` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-e13d030b1f9e:q9` | 9 | 8 | 8 |
| `doc-e13d030b1f9e:q15` | 15 | 12 | 12 |
| `doc-e13d030b1f9e:q30` | 30 | 20 | 20 |
| `doc-ee51036d2382:q11` | 11 | 3 | 3 |
| `doc-ee51036d2382:q14` | 14 | 4 | 4 |
| `doc-ee51036d2382:q39` | 39 | 8 | 8 |
| `doc-eefc3d15076e:q13` | 13 | 14 | 14 |
| `doc-eefc3d15076e:q17` | 17 | 18 | 18 |
| `doc-eefc3d15076e:q40` | 40 | 36 | 36 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-e13d030b1f9e.pdf`
- `02_doc-ee51036d2382.pdf`
- `03_doc-eefc3d15076e.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `4868e47b2bd4554748c450fb56b5506fe47597529effef516fe71766df2d8fd8`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `e277b0493c6b947379e17632ddb9a8af1b3eaafd0f34cc604926acf4f2902515`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta. Nenhum recorte, conversao, OCR ou modificacao dos PDFs.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 14–16: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao documental ou de questoes com os Batches 01–13.
- Ultimos nove documentos da selecao congelada, posicoes 40–48; `lastManifestPosition=48`; nenhum documento apos a posicao 48.
- `all16ReviewPackagesPrepared=true`: todos os 48 documentos selecionados possuem pacote de review de GT; Batches 11–16 preparados e aguardando adjudicacao humana.
- GTs 01–10 byte-preservados e humanamente adjudicados; packages 11–13 preservados. Progresso permanece 90/144, com 10/16 batches concluidos e 6 pendentes; 54 questoes aguardam adjudicacao humana (27 dos Batches 11–13 e 27 dos Batches 14–16).
- `questionSelectionExecuted=true`; `selectionReexecuted=false`; 144 selected IDs preservados, mapping SHA256 `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Zero rotulos automaticos de GT: responseMode, optionCount, optionLabels, subitems, responseControls, layout, markerStyle e contentKind nao preenchidos nem inferidos.
- Nenhum JSON de GT 11–16 criado; nenhum GT final criado. Nenhum Auditor output ou gabarito consultado; nenhum merge. Revisao humana pendente.
