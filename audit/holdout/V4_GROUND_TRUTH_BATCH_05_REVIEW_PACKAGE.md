# Ground Truth V4 — review package Batch 05

Preparacao para revisao humana, sem adjudicacao. Batch independente: `ground-truth-05`, com 3 documentos / 9 questoes, nas posicoes 13–15 do manifest congelado.

- Branch: `audit/holdout-v4`.
- Commit fonte: `ad56c700fe73db35407943f700dcfa24176fc1c7`.
- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256: `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Indice: `audit/holdout/question-index-v4-final.json`; SHA256: `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- Diretorio local (ignorado pelo Git): `outputs/audit/holdout/v4-ground-truth-batch-05-review/`.

## Documentos e identidades congeladas

| Ordem | Documento | Familia | Ano | Serie | Tipo | Fingerprint SHA256 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `doc-3e395d355d2c` | CMPA | 2025 | 6º Ano | text_native | `3e395d355d2c93d657dd2c71ed2761657828b01de125edd8db351706ee308dd9` |
| 2 | `doc-3fb1e1ce24be` | CMF | 2024 | 6º Ano | text_native | `3fb1e1ce24be68ce1d360d6027d2697a9e084a7a17ebcf69a510e42519d6440d` |
| 3 | `doc-41045384ae4b` | CMC | 2014 | 6º Ano | text_native | `41045384ae4bff042f574053549c4fb19902738f89af6225c4db8a2f901d9eb9` |

## Questoes selecionadas

Paginas fisicas do PDF integral; IDs e boundaries copiados do manifest e conferidos no indice final, sem nova selecao.

| Question ID | Numero canonico | pageStart | pageEnd |
| --- | --- | --- | --- |
| `doc-3e395d355d2c:q4` | 4 | 7 | 7 |
| `doc-3e395d355d2c:q25` | 25 | 27 | 27 |
| `doc-3e395d355d2c:q27` | 27 | 28 | 28 |
| `doc-3fb1e1ce24be:q12` | 12 | 8 | 8 |
| `doc-3fb1e1ce24be:q20` | 20 | 15 | 15 |
| `doc-3fb1e1ce24be:q32` | 32 | 21 | 21 |
| `doc-41045384ae4b:q3` | 3 | 3 | 3 |
| `doc-41045384ae4b:q11` | 11 | 5 | 5 |
| `doc-41045384ae4b:q21` | 21 | 8 | 8 |

## Arquivos para upload

Exatamente cinco arquivos, na ordem de `FILES_TO_UPLOAD.txt`:

- `01_doc-3e395d355d2c.pdf`
- `02_doc-3fb1e1ce24be.pdf`
- `03_doc-41045384ae4b.pdf`
- `review-context.json`
- `FILES_TO_UPLOAD.txt`

- SHA256 de `review-context.json`: `9ff644c4082ca64761f8dfd35f7e08c11b7894cc3f86701135ffa5e66f6be6c8`.
- SHA256 de `FILES_TO_UPLOAD.txt`: `f5e5a7e52067fc385bf8a9aaedd0aff813953a36ba14a6db8a177751bed20786`.
- PDFs integrais, byte-identicos aos originais: `true`; SHA256 de cada copia igual ao fingerprint acima, com comparacao binaria direta.

## Validacao e limites

- Documentos: 3; questoes: 9; questionIds unicos: 9.
- Conjunto dos Batches 05–07: 9 documentos / 27 questoes, 27 questionIds unicos; nenhuma sobreposicao com os Batches 01–04.
- Batches 01–04 preservados e humanamente adjudicados; progresso permanece 36/144, com 12 batches pendentes e 27 questoes adicionais aguardando revisao humana.
- `questionSelectionExecuted=true`, sem alterar ou reexecutar selecao.
- `humanAdjudicationComplete=false`.
- `groundTruthBatchCreated=false`.
- `groundTruthFinalCreated=false`.
- `auditorExecuted=false`.
- Nenhum campo de Ground Truth preenchido; nenhum JSON de GT dos Batches 05–07 criado. Nenhum Auditor output ou gabarito consultado. Revisao humana pendente.
