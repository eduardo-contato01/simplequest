# Ground Truth V4 — review package Batch 16

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-16`, com 3 documentos / 9 questoes, nas posicoes 46–48 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `4fcc6b11e9ef510bc62549efb7970a8683706ed6`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-16-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-f03e7d17eec1` | CMPA | 2023 | 6º Ano | hybrid | `f03e7d17eec1cd97788ae2f938dbeb4c91e64c79db0b57e0b064ab28670669d7` |
| 2 | `doc-f1c03b7dfa39` | CMF | 2020 | 6º Ano | text_native | `f1c03b7dfa396041ded2025b519db1c87ab23deee9fd73369916b6ab28fcbef7` |
| 3 | `doc-f4dd01071816` | CMJF | 2015 | 6º Ano | raster | `f4dd0107181635855698e2242629cade64f086ecd5068f81a0ffddb97c25060f` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-f03e7d17eec1:q3` | 3 | 5 | 5 |
| `doc-f03e7d17eec1:q20` | 20 | 22 | 22 |
| `doc-f03e7d17eec1:q38` | 38 | 37 | 37 |
| `doc-f1c03b7dfa39:q5` | 5 | 3 | 3 |
| `doc-f1c03b7dfa39:q15` | 15 | 7 | 7 |
| `doc-f1c03b7dfa39:q22` | 22 | 11 | 11 |
| `doc-f4dd01071816:q5` | 5 | 6 | 6 |
| `doc-f4dd01071816:q13` | 13 | 14 | 14 |
| `doc-f4dd01071816:q20` | 20 | 20 | 20 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-f03e7d17eec1.pdf`
- `02_doc-f1c03b7dfa39.pdf`
- `03_doc-f4dd01071816.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `646417669c24d59fabd2794e50b589839e70be845fa3e8f56cbf89ea842bf807`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `daccab04d6d0f6a8df7018f66103c14aa054d3c533cdbd304d6f75de25f43389`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta. Nenhum recorte, conversao, OCR ou modificacao dos PDFs.
- `doc-f03e7d17eec1`: `sourceType=hybrid` preservado; PDF original preservado byte-identicamente, sem transformacao em text_native/raster nem versao alternativa.

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
