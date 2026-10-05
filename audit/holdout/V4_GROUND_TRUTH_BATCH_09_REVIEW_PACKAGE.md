# Ground Truth V4 — review package Batch 09

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-09`, com 3 documentos / 9 questoes, nas posicoes 25–27 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `5dbae24861fe4270ce5b7f69ec7d6d191ef6d2cc`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-09-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-800c2a22f148` | CMDPII | 2022 | 6º Ano | text_native | `800c2a22f148cade29d12faacc784f5e1e6522360ff77bb0410f6dc1aef16d8f` |
| 2 | `doc-89561bb8f1fe` | CMR | 2017 | 1º Ano | raster | `89561bb8f1fea23a3f17560cabaf979c37ff326672900f5a0197a7fa507fb525` |
| 3 | `doc-9236ae9f513e` | CMSP | 2019 | 6º Ano | text_native | `9236ae9f513e7eba0267c2be6d844b9e532d93b29160c643a3abc481ff50a3c1` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-800c2a22f148:q1` | 1 | 2 | 2 |
| `doc-800c2a22f148:q9` | 9 | 8 | 8 |
| `doc-800c2a22f148:q15` | 15 | 12 | 12 |
| `doc-89561bb8f1fe:q1` | 1 | 2 | 2 |
| `doc-89561bb8f1fe:q10` | 10 | 6 | 6 |
| `doc-89561bb8f1fe:q18` | 18 | 9 | 9 |
| `doc-9236ae9f513e:q7` | 7 | 4 | 4 |
| `doc-9236ae9f513e:q10` | 10 | 6 | 6 |
| `doc-9236ae9f513e:q16` | 16 | 9 | 9 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-800c2a22f148.pdf`
- `02_doc-89561bb8f1fe.pdf`
- `03_doc-9236ae9f513e.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `25064ede28eda261abe52ed841bb91fb22542bede8905e44e9f18388a66f1eff`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `532957171ec5cfd37ed16d0a9458e83c159097bef9f2be5587eda00e4a90abcf`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 08–10: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao com os Batches 01–07.
- Batches 01–07 preservados e humanamente adjudicados; progresso permanece 63/144, com 9 batches pendentes e 27 questoes adicionais aguardando revisao humana.
- `questionSelectionExecuted=true`, sem alterar ou reexecutar selecao.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Nenhum campo de Ground Truth preenchido; nenhum JSON de GT dos Batches 08–10 criado. Nenhum Auditor output ou gabarito consultado. Revisao humana pendente.
