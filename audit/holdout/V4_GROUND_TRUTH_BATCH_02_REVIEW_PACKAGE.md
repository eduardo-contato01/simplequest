# Ground Truth V4 — review package Batch 02

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-02`, com 3 documentos / 9 questoes, nas posicoes 4–6 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `8e257b79e7880d1405b5e5b4e1016733cc76e5ce`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-02-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-0aa57ea3e5ed` | PAS 1 | 2008 | null | text_native | `0aa57ea3e5ed3a939e931d353b419adfb1eb2cecc98d1b81c40b04df2baabaf4` |
| 2 | `doc-0bd82b9dc803` | PAS 2 | 2010 | null | text_native | `0bd82b9dc8033412a81e5f0bc67ada7d5ec4e0c693e8a05a6dc6816e0ee6389d` |
| 3 | `doc-0db5ce524459` | COLÉGIO PÓDION | 2025 | 6º Ano | raster | `0db5ce524459a88bc7d2120a47cd3f19c4909c2c7ee378bde5468892a76cdf9d` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-0aa57ea3e5ed:q31` | 31 | 7 | 7 |
| `doc-0aa57ea3e5ed:q55` | 55 | 10 | 10 |
| `doc-0aa57ea3e5ed:q88` | 88 | 15 | 15 |
| `doc-0bd82b9dc803:q40` | 40 | 8 | 8 |
| `doc-0bd82b9dc803:q57` | 57 | 10 | 10 |
| `doc-0bd82b9dc803:q121` | 121 | 19 | 19 |
| `doc-0db5ce524459:q7` | 7 | 5 | 5 |
| `doc-0db5ce524459:q13` | 13 | 7 | 7 |
| `doc-0db5ce524459:q26` | 26 | 13 | 13 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-0aa57ea3e5ed.pdf`
- `02_doc-0bd82b9dc803.pdf`
- `03_doc-0db5ce524459.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `d36bec4669efb2f2fc6a83adf4011a504757c9381d30de8b1c20c677bea1e16f`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `3919903dd32b48cb53af444ed85b555d05c9eec85035046f06eaf974a75e535a`.
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
