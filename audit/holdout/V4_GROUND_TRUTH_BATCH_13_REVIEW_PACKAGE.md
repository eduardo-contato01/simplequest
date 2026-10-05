# Ground Truth V4 — review package Batch 13

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-13`, com 3 documentos / 9 questoes, nas posicoes 37–39 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `decfc72df8326e0ddf9045c44bde7feba0524e3f`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-13-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-c573e686e882` | CMVM | 2024 | 6º Ano | raster | `c573e686e88211332418b68914be57ed2c723977ed92dc7b68f24dd2a167d067` |
| 2 | `doc-c8d6da47c18b` | CMB | 2013 | 6º Ano | text_native | `c8d6da47c18ba8083fb134a62cf3032c6be85ccbf8d2fa5aa921601c8433c1b3` |
| 3 | `doc-cd0a32a92382` | CMCG | 2017 | 6º Ano | text_native | `cd0a32a923828730979adbd73959100d889a3f789e92a6fc379b2ad60a3b1dc6` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-c573e686e882:q12` | 12 | 6 | 6 |
| `doc-c573e686e882:q15` | 15 | 7 | 7 |
| `doc-c573e686e882:q33` | 33 | 18 | 18 |
| `doc-c8d6da47c18b:q4` | 4 | 3 | 3 |
| `doc-c8d6da47c18b:q9` | 9 | 4 | 4 |
| `doc-c8d6da47c18b:q15` | 15 | 7 | 7 |
| `doc-cd0a32a92382:q2` | 2 | 3 | 3 |
| `doc-cd0a32a92382:q13` | 13 | 7 | 7 |
| `doc-cd0a32a92382:q16` | 16 | 7 | 7 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-c573e686e882.pdf`
- `02_doc-c8d6da47c18b.pdf`
- `03_doc-cd0a32a92382.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `39a60784c0009a82083c1534274c652f9d12596692af335d71c7c4dfeea2fa3f`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `2610c1fe0882dc2827b9fd4aed410a93414787795187384c450b0ed87fff254a`.
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
