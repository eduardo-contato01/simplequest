# Ground Truth V4 — review package Batch 11

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-11`, com 3 documentos / 9 questoes, nas posicoes 31–33 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `decfc72df8326e0ddf9045c44bde7feba0524e3f`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-11-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-a272afbae2ca` | VESTIBULAR_UNB | 2007 | null | text_native | `a272afbae2ca3bd4bcc36e14869cb0f2b6d11b9daea5c203ef0e9c0326e9d19a` |
| 2 | `doc-ad34c4cf7f30` | COLÉGIO PÓDION | 2024 | null | raster | `ad34c4cf7f30b6c8a0ba2cfd5c6cef41e74b64e66ffc568dee16d3cada78cd83` |
| 3 | `doc-b605f7a51fd5` | CMBH | 2015 | 6º Ano | text_native | `b605f7a51fd572b4de2594787e7a5b5fcdb258ec199532bb8853c8301815198f` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao. Somente identidade e intervalos canonicos, sem rotulos de Ground Truth.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-a272afbae2ca:q1` | 1 | 2 | 2 |
| `doc-a272afbae2ca:q112` | 112 | 11 | 11 |
| `doc-a272afbae2ca:q137` | 137 | 14 | 14 |
| `doc-ad34c4cf7f30:q5` | 5 | 4 | 4 |
| `doc-ad34c4cf7f30:q26` | 26 | 9 | 9 |
| `doc-ad34c4cf7f30:q33` | 33 | 12 | 12 |
| `doc-b605f7a51fd5:q5` | 5 | 4 | 4 |
| `doc-b605f7a51fd5:q7` | 7 | 5 | 5 |
| `doc-b605f7a51fd5:q20` | 20 | 14 | 14 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-a272afbae2ca.pdf`
- `02_doc-ad34c4cf7f30.pdf`
- `03_doc-b605f7a51fd5.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `564c91b742f97aa0716800792c7ee9aae1c63af882508d30ff7bfb72133bac62`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `03973f8fe23ee6c9730281f6bc71785e47604c4671b9b85dee2d5f8922149f10`.
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
