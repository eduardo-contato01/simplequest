# Holdout V5 — neutral question index protocol freeze (B1)

`V5_QUESTION_INDEX_PROTOCOL_FROZEN = PASS`

Este é o snapshot **anterior à execução**, criado/hash-congelado no workspace
antes de invocar o indexador. Freeze versionado formal pelo commit de introdução
deste protocolo e do raw; a execução preserva os bytes deste protocolo. Flags
false abaixo descrevem este momento, não o estado posterior do raw freeze.

## Base e documentos

- Branch: `audit/holdout-v5-blind`.
- Source commit / Phase A HEAD: `3e83b7d1f20f75a7f80a7fcca230c73e3ebac326`.
- Candidate funcional: `3b306d6a544cc63928ec8adf07640b224651742e`, baseline05C1;
  05C2 estacionado/não promovido.
- Manifest Phase A: `audit/holdout/manifest-v5-documents-frozen.json`.
- Manifest file SHA256: `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- phaseAComplete=true; selectedDocuments=48.
- sourceFilesPresent=48/48; sourceFingerprintsMatched=48/48;
  sourceFingerprintMismatch=0, após novo hash binário dos PDFs.
- Preflight UTC: `2026-10-07T19:21:46.136496+00:00`.
- Working tree limpa / stage vazio antes desta preparação.

## Indexador/configuração imutáveis

- Indexer path: `scripts/audit_holdout_question_index.py`.
- Indexer Git blob: `25ca4665708ba0ad8850f889f5ea0d71e3ff4025` (igual ao freeze V4).
- Local file SHA256: `04262953d3949651bd8cf4c236cbd5e7b4e85b64c34db77033c19717824b5d3c`.
- indexMethodVersion: `neutral-question-index-v1`.
- OCR fallback: `engine=tesseract`, `dpi=160`, `psm=11`, `lang=por+eng`.
- `scripts/ocr_pdf_layer.py` local SHA256:
  `006f6139528fd3f38f8c8f7f587c8384cf553d2253076a1b929c81478e551121`.
- Tesseract runtime: `tesseract v5.4.0.20240606`; traineddata por/eng existentes.

Esta configuração pertence SOMENTE ao índice neutro; NÃO define o OCR futuro
do Auditor V5. Sem tuning, alteração de algoritmo ou troca de configuração após
ver documentos. Nenhum código funcional/indexador/schema será alterado.

## Execução autorizada e isolamento

Uma única invocação do indexador congelado, diretamente com o manifest V5:

```text
python -X utf8 -u scripts/audit_holdout_question_index.py --manifest audit/holdout/manifest-v5-documents-frozen.json --out audit/holdout/question-index-v5-raw.json --report audit/holdout/question-index-v5-raw-report.json
```

O CLI lê o manifest como fonte documental e não chama o validator legado.
Manter `protocolVersion=holdout-v5`. `audit_holdout_schema.py` aceita somente
V1–V4 e permanece intocado; compatibilidade para execução oficial do Auditor
será tratada separadamente antes do primeiro run. Não trocar version para V4.

Cache permitido: somente `outputs/audit/holdout/ocr/<documentId>/` do indexador.
preexistingV5IndexCaches=0. Diretórios/cache neutros antigos são byte-protegidos;
`outputs/audit/ocr/` principal/V1–V4 permanece intacto. Caches não serão staged.
O indexador usa seu renderer nativo congelado e fallback Tesseract, sem invocar
o CLI `ocr_pdf_layer.py` ou o Auditor. Sem `--only`, `--no-ocr` ou monkeypatches.

Saída somente neutra: documentId/contentFingerprint, questionId/questionNumber,
pageStart/pageEnd, anomalias automáticas de numeração/boundary e provenance
técnica. Report separado conserva método/pageCount e os mesmos dados neutros.
Proibidos responseMode/optionCount/optionLabels/markerStyle de resposta, respostas,
gabaritos, conteúdo semântico, layout de alternativas, predictions e métricas.

Após a execução, somente validações automáticas de schema neutro/identidade,
unicidade, pages e contagens técnicas/hashes. Raw produzido deve permanecer
byte-idêntico, sem corrigir contagens/números/boundaries ou interpretar anomalias
item a item. Zero questões em documento será registrado, não removido/substituído.
Falha técnica implica registrar e STOP, nunca rerun para melhorar contagens.

## Estado anterior à execução

- questionIndexProtocolFrozen=true
- frozenBeforeExecution=true
- rawQuestionIndexExecuted=false
- questionSelectionExecuted=false
- questionSelectionStarted=false
- groundTruthCreated=false
- groundTruthStarted=false
- auditorExecuted=false
- metricsSeen=false
- manualPdfInspection=false
- rawAnomaliesHumanReviewed=false

Próximo dentro desta B1: produzir raw uma vez, validar/congelar seus bytes e
commit/push, depois STOP. Nenhuma adjudicação/review package/final index,
manifest-v5-b, seleção das três questões, GT ou Auditor nesta fase. B2 será
neutral question-index adjudication/final freeze, em etapa separada.
