# V5 Tier A / Batch 01 — neutral review package freeze

V5_TIER_A_BATCH_01_REVIEW_PACKAGE_FROZEN=PASS

## Escopo e provenance

Somente preparação e freeze V5 Phase B2b-1. Nenhuma adjudicação ou decisão canônica foi realizada. Tier A inteiro, Phase B e índice final NÃO estão concluídos.

- Branch: `audit/holdout-v5-blind`.
- Source HEAD: `a9b88e3592fab8db41baf67e142cafb49695d454`.
- Candidate funcional permanece baseline05C1; Patch05C2 estacionado/não promovido.
- Source queue: [question-index-v5-review-queue.json](question-index-v5-review-queue.json).
- Source queue SHA256: `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b`.
- Raw index SHA256: `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- Raw report SHA256: `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- Manifest SHA256: `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- Phase B2a concluída; fila congelada sem novo ranking.

## Batch posicional congelado

Tier A contém 22 documentos. Batch 01 = posições 1–11 da ordem Tier A congelada; Batch 02 = posições 12–22, intocado/não preparado. Não houve reranking, redistribuição ou seleção por família, OCR, anomalias, facilidade, conteúdo ou desempenho esperado. Nenhum documento Tier B/C/D entrou.

Os hashes abaixo são simultaneamente fingerprints das fontes e SHA256 das cópias. Fontes presentes = 11/11; fingerprints matched = 11/11; mismatch = 0; cópias comparadas byte a byte = 11/11. Page counts vieram exclusivamente da queue/raw report congelados, sem parser PDF.

| Posição Tier A / Batch 01 | documentId | SHA256 fonte = cópia |
| --- | --- | --- |
| 1 | `v5-doc-ccc36240e82f271d` | `ccc36240e82f271de6eec6894138b19f6f939c1b461e399738869c48346cacbe` |
| 2 | `v5-doc-9341853cd786543a` | `9341853cd786543a175749ae045cde1732f9909dd8706cd17e0a4dcda30a1a6d` |
| 3 | `v5-doc-bd657a7d79e90389` | `bd657a7d79e90389ae6bced8a39cb07dd1b2cdc162e368f7cad1093f2083552a` |
| 4 | `v5-doc-1fb8c32edfae9126` | `1fb8c32edfae9126e6faa329a251518338a5728570202e42dfdb918e300b9462` |
| 5 | `v5-doc-a8e098aad9a7ece4` | `a8e098aad9a7ece4f16a549cd1c92f2531903d0f7fff24fe6ed695ff61306ef0` |
| 6 | `v5-doc-ae2f4e91af8a01f9` | `ae2f4e91af8a01f933ec58bd5ca44449e1b7aba486e324e21a6b3eb08058ed4a` |
| 7 | `v5-doc-4ec5bc5117bb7440` | `4ec5bc5117bb7440c96231090f3e99c63596c3d64607ac0c5ef4d4f41db39e3a` |
| 8 | `v5-doc-7a302456c4a6afbe` | `7a302456c4a6afbe0451df3e4cdf7027dbedee4801f4d24ddc0babaf440e4191` |
| 9 | `v5-doc-b1498826d8a54db3` | `b1498826d8a54db31c8803cf1daa3aab8d753b0316de12ba84cf49bb42f1e126` |
| 10 | `v5-doc-506c709758cb13a9` | `506c709758cb13a9f8cc5d5454e168e61a96f5a1731f9003bfc2ae94013c3749` |
| 11 | `v5-doc-e223f9e9c5cea0cb` | `e223f9e9c5cea0cb1bb88a9ea4efbcba7fb6cb997e99ef19aab92fae14e9730e` |

## Artefatos congelados

- Package versionado: [question-index-v5-tier-a-batch-01-review-package.json](question-index-v5-tier-a-batch-01-review-package.json).
- Package SHA256: `61f769a6d016a30095e97a16fd1da79396d05ec1ef2f750cff75135b9c7ac59f`.
- Context ignorado: `outputs/audit/holdout/v5-tier-a-batch-01-review/review-context.json`.
- Context SHA256: `fbb49685a7c49f625d03b0aa51356bd137b56e8d3264f9095fb699d750261b77`.
- Lista ignorada: `outputs/audit/holdout/v5-tier-a-batch-01-review/FILES_TO_REVIEW.txt`.
- Lista SHA256: `ba8b67adcc7bd1e8afab4f90d951ff677e271d090257f7d439a4c57c256d1999`.
- Cópias ignoradas: `outputs/audit/holdout/v5-tier-a-batch-01-review/copies/NN__<documentId>.pdf`, NN=01..11.
- PDFs/context/lista não versionados. PDFs completos byte-idênticos; nenhuma página aberta, nenhum render/PNG e nenhum OCR novo.

O context contém somente identidade/provenance, metadata neutra, raw questions (`questionId/questionNumber/pageStart/pageEnd`) e eventos de anomalia neutros, preservados exatamente dos inputs congelados. Anomalias são eventos diagnósticos brutos, NÃO erros confirmados. Nenhuma correção de numbering, boundaries, contagens ou exclusão foi feita.

## Policy neutra

A policy registrada aplica-se à futura adjudicação visual autorizada, não autoriza revisão nesta preparação.

Allowed evidence:

- visible question number
- visible question start
- continuation/end page
- visible section transition
- neutral native/OCR text
- document-declared neutral item count

Forbidden evidence:

- responseMode
- optionCount
- optionLabels
- markerStyle classification
- answer key
- correct answer
- GT
- Auditor output

## Validação e preservação

Validações automáticas: documents=11, uniqueIds=11, allAreTierA=true, globalTierAOrders=1..11, batch02Untouched=true, fingerprintMismatch=0, reviewCopiesByteIdentical=11/11. Provenance e policy comparadas aos inputs congelados; hashes e raw questions/anomalies sem alteração.

Snapshot de preservação: 4126 arquivos preexistentes byte-idênticos, cobrindo Phase A/B1/B2a, raw index/report, review queue, Auditor/indexer, V1–V4, postmortem e caches. Nenhum código funcional alterado; configuração Git preservada. V4 package foi consultado somente para schema/provenance; nenhuma adjudicação V4 consultada para decisões V5.

```text
manualAdjudicationPerformed=false
responseSemanticsConsulted=false
GTConsulted=false
AuditorConsulted=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
questionSelectionExecuted=false
groundTruthStarted=false
groundTruthCreated=false
auditorExecuted=false
metricsSeen=false
visualPagesOpened=false
rendersCreated=false
ocrExecuted=false
```

## Próximo passo e STOP

Próximo: **V5 B2b Tier A Batch01 neutral visual adjudication**, somente em execução separada autorizada. Nenhuma adjudication JSON criada; Batch02 não preparado; índice final/selection/GT/Auditor não iniciados.

Após commit/push deste freeze, STOP obrigatório. Sem merge.
