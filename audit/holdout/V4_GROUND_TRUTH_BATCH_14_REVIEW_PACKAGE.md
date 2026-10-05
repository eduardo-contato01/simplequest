# Ground Truth V4 — review package Batch 14

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-14`, com 3 documentos / 9 questoes, nas posicoes 40–42 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `4fcc6b11e9ef510bc62549efb7970a8683706ed6`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-14-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-cef618be31e6` | CMRJ | 2022 | 6º Ano | text_native | `cef618be31e62342be648b0e0d772f5ca53f83f62b417bcacde60efbc1a5c149` |
| 2 | `doc-cf6b56e7abd7` | CMB | 2017 | 1º Ano | raster | `cf6b56e7abd787dcdb64cc2cf7a41b848ba28a413fdde69d71f199b3efe058b2` |
| 3 | `doc-dce5637b3bd7` | CMT | 2016 | 1º Ano | text_native | `dce5637b3bd742052e90e4a2cbf33a3b660250937ddb12cad382ffc7ea03d150` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-cef618be31e6:q2` | 2 | 3 | 3 |
| `doc-cef618be31e6:q16` | 16 | 10 | 10 |
| `doc-cef618be31e6:q23` | 23 | 12 | 12 |
| `doc-cf6b56e7abd7:q3` | 3 | 5 | 5 |
| `doc-cf6b56e7abd7:q12` | 12 | 12 | 12 |
| `doc-cf6b56e7abd7:q15` | 15 | 16 | 16 |
| `doc-dce5637b3bd7:q10` | 10 | 6 | 6 |
| `doc-dce5637b3bd7:q18` | 18 | 10 | 10 |
| `doc-dce5637b3bd7:q30` | 30 | 13 | 13 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-cef618be31e6.pdf`
- `02_doc-cf6b56e7abd7.pdf`
- `03_doc-dce5637b3bd7.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `6976cd253ce735a32288479d5f58248b34ad37e5897e24402866f80af810dc68`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `a01aa1c10d139d64edd39d9b8a73f5e16f5202dbd11a27a388cc83452f9334ef`.
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
