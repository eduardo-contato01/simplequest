# V5 Tier A / Batch02 — neutral review package freeze

V5_TIER_A_BATCH_02_REVIEW_PACKAGE_FROZEN=PASS

## Escopo e provenance

Somente V5 Phase B2b, Tier A / Batch02 review package freeze.
Branch: `audit/holdout-v5-blind`; source HEAD: `4219083faf63d66865fdf7b60ec1a878da60bd41`.
Preflight: branch/HEAD obrigatórios, working tree limpa, stage vazio, git diff --check PASS.
Freeze formal pelo commit de introdução; um commit/push e STOP antes da revisão visual.

[Batch01 já adjudicado](V5_TIER_A_BATCH_01_ADJUDICATION.md), preservado byte a byte.
Somente o seu estado/provenance foi conferido; nenhuma página foi reaberta e nenhuma
decisão anterior foi reinterpretada. Tier A inteiro/Phase B ainda NÃO concluídos.

## Batch posicional imutável

Tier A possui 22 documentos. Batch02 usa exatamente posições 12–22 da ordem já congelada
na [review queue](question-index-v5-review-queue.json). Nenhum ranking foi recalculado;
sem reranking, redistribuição, substituição por conveniência ou vazamento de Tier B/C/D.
Metadados, pageCount e método provêm exclusivamente dos JSONs congelados, sem parser PDF.
sourceType e indexMethod são campos distintos e foram preservados literalmente.

| Batch / global Tier A | documentId | Family | Year | Series | Source type | Index method | Pages | Raw questions | Raw anomalies |
| --- | --- | --- | ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 / 12 | `v5-doc-84179ac96b058ffb` | CMR | 2023 | 6º Ano | raster | ocr | 25 | 24 | 22 |
| 2 / 13 | `v5-doc-e123ad77b8edc98f` | CMCG | 2015 | 6º Ano | text_native | ocr | 12 | 9 | 12 |
| 3 / 14 | `v5-doc-815b83630e3d8c98` | CMF | 2008 | 6º Ano | text_native | native | 9 | 20 | 11 |
| 4 / 15 | `v5-doc-e9603e9180e6028b` | CMJF | 2015 | 1º Ano | raster | ocr | 12 | 4 | 11 |
| 5 / 16 | `v5-doc-1babdc250c302165` | CMS | 2018 | 6º Ano | raster | ocr | 18 | 11 | 10 |
| 6 / 17 | `v5-doc-d5099c3057735940` | CMJF | 2010 | 1º Ano | raster | ocr | 13 | 5 | 10 |
| 7 / 18 | `v5-doc-0c51e49589f148bc` | CMCG | 2011 | 6º Ano | raster | ocr | 12 | 13 | 6 |
| 8 / 19 | `v5-doc-02531e2612ade970` | CMSM | 2006 | 1º Ano | raster | ocr | 6 | 10 | 5 |
| 9 / 20 | `v5-doc-87d7a7f5696b5a6a` | CMC | 2011 | 6º Ano | raster | ocr | 8 | 9 | 5 |
| 10 / 21 | `v5-doc-74e153f9c146d887` | CMSP | 2019 | 6º Ano | raster | ocr | 1 | 4 | 4 |
| 11 / 22 | `v5-doc-a08230ae0b1cad7e` | CMSM | 2006 | 1º Ano | text_native | ocr | 4 | 0 | 1 |
| Total | 11 documentos | — | — | — | — | — | 120 | 109 | 97 |

As 109 questões e 97 eventos são estados brutos, não contagem canônica, erros confirmados
ou métricas do Auditor. O documento com rawQuestionCount=0 continua no package e NÃO foi
investigado. Nenhuma conclusão sobre questão perdida, falso marker, boundary, reinício,
exclusão estrutural ou incompletude de source foi feita.

## Fontes e cópias

sourceFilesPresent=11/11; fingerprintsMatched=11/11; fingerprintMismatch=0;
reviewCopiesByteIdentical=11/11. Hash binário completo das fontes comparado com o fingerprint
congelado; cópias também comparadas byte a byte. Não houve leitura visual ou extração PDF.

| Batch order | documentId | SHA256 fonte = cópia |
| --- | --- | --- |
| 1 | `v5-doc-84179ac96b058ffb` | `84179ac96b058ffb43a18ffbbaea9b573e43759b6c5942fa3b1d09266ac2afe6` |
| 2 | `v5-doc-e123ad77b8edc98f` | `e123ad77b8edc98fdb7184c07925a676766bad4cb9d744cb3a22a2355cda0f54` |
| 3 | `v5-doc-815b83630e3d8c98` | `815b83630e3d8c9899695cdcc4a30f96ee4a5f411d541d954c534cd5a8f9ef1a` |
| 4 | `v5-doc-e9603e9180e6028b` | `e9603e9180e6028ba3c7bb833cffd85d864e7f35233076c5fad1a96e26446207` |
| 5 | `v5-doc-1babdc250c302165` | `1babdc250c302165ff32a5601fda24c215ab8b17eb0e78ee52d0e241bf132c40` |
| 6 | `v5-doc-d5099c3057735940` | `d5099c30577359406ebc4faf4974434bf10f84fe24a3cc186dc162e7c866c838` |
| 7 | `v5-doc-0c51e49589f148bc` | `0c51e49589f148bc6f66b4b1822b3bf78b9a57f7e78a055f09648703d9230d87` |
| 8 | `v5-doc-02531e2612ade970` | `02531e2612ade970720cc0a153080e77869fc9edc6f2a74cfed882f5aeec2138` |
| 9 | `v5-doc-87d7a7f5696b5a6a` | `87d7a7f5696b5a6afbf9a10842a994b8ca6e759269b3aea0080faef0a2360b4e` |
| 10 | `v5-doc-74e153f9c146d887` | `74e153f9c146d8878547d6f5fd0538953c61fcb15f17f27c6d1cfcddfadee53d` |
| 11 | `v5-doc-a08230ae0b1cad7e` | `a08230ae0b1cad7e06f3e15215d54d0e53526e3e5c6b11008f4295a5fb469d09` |

Diretório ignorado: `outputs/audit/holdout/v5-tier-a-batch-02-review/`.
Contém somente `copies/`, `review-context.json` e `FILES_TO_REVIEW.txt`.
Naming: `01__v5-doc-84179ac96b058ffb.pdf` até `11__v5-doc-a08230ae0b1cad7e.pdf`.
Cópias completas não versionadas; nenhuma delas foi aberta visualmente.

O context neutro contém batchOrder/globalTierAOrder, identidade/fingerprint, canonicalPath,
reviewCopyPath/SHA256, byteIdenticalToSource e metadata neutra. rawQuestions/rawAnomalies
são iguais aos arrays das fontes congeladas, sem alterar números, ranges, tipos ou notas.
Lista de arquivos conserva a mesma ordem fixa; não contém decisões de adjudicação.

## Policy para adjudicação futura

Allowed evidence SOMENTE para futura revisão separadamente autorizada:

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

Nenhuma evidência visual permitida foi exercida nesta preparação. Não se consultaram
semântica de resposta, gabaritos, GT, Auditor output ou métricas V5.
[Source incompleteness addendum](V5_OBJECTIVE_SOURCE_INCOMPLETENESS_RULE.md) permanece
congelado como provenance, NÃO aplicado preventivamente: sourceIncompleteAssessmentPerformed=false.
Qualquer evidência de source gap só poderá ser avaliada em futura revisão visual autorizada.

## Hashes congelados

Hashes SHA256 dos bytes locais finais UTF-8 sem BOM dos novos arquivos, não Git blobs.

| Artefato | SHA256 |
| --- | --- |
| [Package Batch02](question-index-v5-tier-a-batch-02-review-package.json) | 33e9ba54c4ff51801a2fad094d0cf6613728494bd085697c4c8f53f42a166f01 |
| Review context ignorado | 54fc39261467f1e169917a3e1c3895630ee0b6aaf8979389122f3c4ddd3aa148 |
| Files list ignorada | b8253b2ce544192e70a0af39e40831907a7d8906f93c84c63bdfb2d98b17b00c |
| Frozen review queue | 027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b |
| Frozen raw index | 68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84 |
| Frozen raw report | 62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f |
| Frozen Phase A manifest | c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62 |
| Frozen prior Batch01 adjudication | e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770 |
| Frozen protocol addendum | 6e53620188ef104d5880ee04e84ef382675a64a8fcc927f69543e6ca273e3541 |
| Protected-files snapshot digest (4860 arquivos) | 437d4623513b64b3293493beae2678d96c6f59c55eaddaf69a686c535fd0a143 |

Os hashes context/lista vinculam o package versionado aos artefatos ignorados desta preparação.
A configuração Git preexistente foi preservada; nenhuma normalização de arquivos antigos.

## Validação e preservação

batchDocumentCount=11; uniqueIds=11; globalTierAOrders=12..22; allAreTierA=true;
noTierBCDLeakage=true; totalPhysicalPages=120; rawQuestionsInBatch=109.
Provenance e policy conferem; inputs raw iguais, PDFs/cópias presentes e byte-idênticos.
Schema não contém decisões canônicas ou conteúdo de resposta.

Snapshot prévio de 4860 arquivos, incluindo todos os versionados protegidos
e os outputs/caches prévios em outputs/audit (exceto __pycache__), permanece byte-idêntico.
Inclui Batch01 package/adjudication/relatório/notes/renders/context/copies, addendum/decision,
PROTOCOL_V5.md, Phase A, B1, B2a, raw/report/queue, Auditor/indexer/baseline05C1,
V1–V4, postmortem e caches congelados. PDFs fontes conferidos novamente por hash binário.
Nenhum código funcional alterado; scripts/src/tests sem diff frente ao candidate05C1.
CONTEXTO histórico preservado byte a byte, com uma única nova entrada incremental.
Stage limitado a package/relatório/CONTEXTO/ROADMAP:
functionalFilesStaged=0; pdfFilesStaged=0; outputFilesStaged=0.

## Estado e STOP

```text
batch02PackageFrozen=true
tierABatch01Adjudicated=true
tierAComplete=false
batch01Untouched=true
PDFsOpened=false
visualPagesOpened=false
rendersCreated=false
ocrExecuted=false
manualAdjudicationPerformed=false
adjudicationPerformed=false
sourceIncompleteAssessmentPerformed=false
responseSemanticsConsulted=false
answerKeysConsulted=false
GTConsulted=false
AuditorConsulted=false
finalQuestionIndexCreated=false
questionSelectionStarted=false
questionSelectionExecuted=false
groundTruthStarted=false
groundTruthCreated=false
auditorExecuted=false
metricsSeen=false
merge=false
```

Próximo separado: **V5 B2b Tier A Batch02 neutral visual adjudication**.
Após o push, STOP: não abrir/adjudicar Batch02, não consolidar Tier A, criar final
question index, selecionar questões, criar GT, executar Auditor ou fazer merge.
