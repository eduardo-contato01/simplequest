# Holdout V4 — Ground Truth Batch 01: pacote de revisao humana

Batch 01 preparado, nao adjudicado: 3 documentos / 9 questoes, correspondentes exatamente aos documentos 1-3 da ordem congelada de manifest-v4-b.json. Politica de batches: 16 batches de 3 documentos / 9 questoes; apenas Batch 01 preparado nesta etapa.

## IDs e paginas canonicas

| documentId | questionId | pageStart | pageEnd |
| --- | --- | ---: | ---: |
| doc-03a9e3fe97aa | doc-03a9e3fe97aa:q9 | 4 | 4 |
| doc-03a9e3fe97aa | doc-03a9e3fe97aa:q15 | 7 | 7 |
| doc-03a9e3fe97aa | doc-03a9e3fe97aa:q39 | 16 | 16 |
| doc-074dd67cbd4a | doc-074dd67cbd4a:q4 | 4 | 4 |
| doc-074dd67cbd4a | doc-074dd67cbd4a:q7 | 6 | 6 |
| doc-074dd67cbd4a | doc-074dd67cbd4a:q16 | 13 | 13 |
| doc-08d3b1b8b1e8 | doc-08d3b1b8b1e8:q5 | 3 | 3 |
| doc-08d3b1b8b1e8 | doc-08d3b1b8b1e8:q24 | 10 | 10 |
| doc-08d3b1b8b1e8 | doc-08d3b1b8b1e8:q39 | 16 | 16 |

## Fingerprints e copias integrais

| Documento / arquivo local | Fingerprint / SHA256 do PDF |
| --- | --- |
| 01_doc-03a9e3fe97aa.pdf | `03a9e3fe97aa894b2f95ca8054945eaec95c3d04db17e5801472caec0f4880a8` |
| 02_doc-074dd67cbd4a.pdf | `074dd67cbd4a4d15a7b935c6148c6b31af150b40d59fbb56d3343d68e383a648` |
| 03_doc-08d3b1b8b1e8.pdf | `08d3b1b8b1e80750e4d2179d1c31868bf4b661f2cbc77e1023e78222a508da86` |

Os tres PDFs foram copiados byte-identicos aos originais, sem recorte, modificacao ou reinterpretacao. IDs, fingerprints e boundaries correspondem ao manifest e ao Final Question Index congelados.

## Pacote local e hashes

Diretorio: `outputs/audit/holdout/v4-ground-truth-batch-01-review/`.

O pacote contem somente os tres PDFs integrais, review-context.json e FILES_TO_UPLOAD.txt. Esses arquivos locais sao ignorados pelo Git e nao sao adicionados ao commit.

- review-context.json: SHA256 `97165c032c6784d235cf36736d7f8d26067e47f6a1ccc37405e46d9484d17061`.
- FILES_TO_UPLOAD.txt: SHA256 `12267872f8a34a6d3a33830abc406464cdeb9fe2f7db219d8042f9960a2ad6b5`.
- Pacote: SHA256 `0ff5a7225a1f0b9f7b150c6f17628ee78472a5da8eb0bedefdd56b740aee1608`.

O hash do pacote e SHA256 do JSON compacto UTF-8 da lista [{path,sha256}, ...], na ordem exata de FILES_TO_UPLOAD.txt, incluindo os cinco arquivos. O contexto preserva somente metadata neutra congelada e flags pendentes; nenhum rotulo de GT foi preenchido.

## Fontes congeladas

- Manifest: `audit/holdout/manifest-v4-b.json`; SHA256 `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885`.
- Final Question Index: `audit/holdout/question-index-v4-final.json`; SHA256 `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.

## Estado

- humanAdjudicationComplete = false
- groundTruthBatchCreated = false
- groundTruthFinalCreated = false
- groundTruthCreated = false
- auditorExecuted = false

Adjudicacao humana pendente. Nenhum Ground Truth V4 foi criado ou congelado; somente o pacote de revisao humana esta preparado.
