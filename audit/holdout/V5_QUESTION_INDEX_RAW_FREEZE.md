# Holdout V5 — raw neutral question index freeze (B1)

`V5_RAW_QUESTION_INDEX_FROZEN = PASS`

Somente Phase B1 concluída. Raw produzido uma vez pelo indexador congelado,
validado automaticamente e preservado sem qualquer correção/adjudicação.
Phase B inteira e V5 completo NÃO concluídos.

## Execução e protocolo

- Branch: `audit/holdout-v5-blind`.
- Source commit / Phase A HEAD: `3e83b7d1f20f75a7f80a7fcca230c73e3ebac326`.
- Candidate funcional: `3b306d6a544cc63928ec8adf07640b224651742e` (05C1 ativo;
  05C2 estacionado/não promovido).
- Indexer: `scripts/audit_holdout_question_index.py`, Git blob
  `25ca4665708ba0ad8850f889f5ea0d71e3ff4025`.
- Indexer local file SHA256:
  `04262953d3949651bd8cf4c236cbd5e7b4e85b64c34db77033c19717824b5d3c`.
- Method: `neutral-question-index-v1`.
- OCR fallback do índice: `tesseract / 160 dpi / psm 11 / por+eng`.
- Protocolo criado/hash-congelado ANTES da execução; seus bytes permaneceram
  idênticos após a execução. Freeze versionado pelo commit de introdução B1.
- [Protocol freeze](V5_QUESTION_INDEX_PROTOCOL_FREEZE.md) SHA256:
  `092cf05076e4f5d2557716eb81627090d32310b33390fdc968d0575142c82518`.
- Phase A manifest file SHA256:
  `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- attempt=1; indexerRerun=false; exitCode=0; processedDocuments=48.
- Início UTC: `2026-10-07T19:23:05.204885+00:00`.
- Fim UTC: `2026-10-07T19:29:35.782853+00:00`.

Manifest e índice mantêm `protocolVersion=holdout-v5`; execução direta do
indexador não depende do validator legado. `audit_holdout_schema.py` permanece
intocado e aceita somente V1–V4. Compatibilidade para Auditor V5 será tratada
em etapa futura separada; o OCR acima NÃO congela o OCR futuro do Auditor.

## Artefatos imutáveis

- Raw: [question-index-v5-raw.json](question-index-v5-raw.json).
- Raw file SHA256:
  `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- Raw canonical JSON SHA256 (`ensure_ascii=False`, `sort_keys=True`):
  `7b0a0ce4e2233d9d6f359f23c7f9a2996226a9840bb443fae3592b4247c2d252`.
- Report técnico: [question-index-v5-raw-report.json](question-index-v5-raw-report.json).
- Report file SHA256:
  `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- [Provenance B1](question-index-v5-raw.provenance.json).

Raw/report conservam os bytes produzidos pelo indexador (UTF-8 sem BOM,
CRLF do runtime Windows). File hashes referem-se a esses bytes locais; não
são hashes de Git blob nem do clean filter. Configuração Git preexistente
`core.autocrlf=true` permanece inalterada. Nenhuma normalização manual.

## Estatísticas estruturais automáticas

- documentsIndexed=48; sourceFilesPresent=48/48;
  sourceFingerprintsMatched=48/48; sourceFingerprintMismatch=0.
- totalRawQuestions=1063.
- min/max/median por documento: 0 / 60 / 19.5.
- documentsWithZeroQuestions=1. Documento mantido, sem substituição/remoção;
  questão neutra de indexação reservada para B2.
- nativeIndexedDocuments=29; ocrIndexedDocuments=19.
- totalIndexingAnomalies=1183.

Contagens de anomalias por tipo, SEM revisão/interpretação individual:

| Tipo automático | Contagem |
| --- | ---: |
| duplicate_question_number | 217 |
| missing_question_number | 887 |
| non_monotonic_numbering | 43 |
| requires_neutral_verification | 25 |
| unresolved_question_start | 11 |

Esses números descrevem somente o índice bruto; não são métricas de qualidade
do Auditor, precision, coverage ou unsafe, nem contagem canônica adjudicada.

## Gates e preservação

- JSON parseável; schema neutro por whitelist automática, sem campos de
  resposta/alternativas/semântica/predictions/métricas.
- documentsIndexed=48; unknownDocumentIds=0; missingDocumentIds=0;
  fingerprintMismatch=0; duplicateDocumentIds=0;
  duplicateQuestionIdsGlobal=0.
- Todas as questões têm identidade neutra consistente e
  `1 <= pageStart <= pageEnd <= pageCount` do report técnico.
- Report e raw contêm as mesmas questões e anomalias automáticas.
- preexistingV5IndexCaches=0; newIndexOcrDocuments=19; newIndexOcrPages=240.
- Cache novo somente em `outputs/audit/holdout/ocr/<documentId>/`;
  nenhum cache/output staged.
- 3677 entradas de snapshots de preservação conferidas por SHA256:
  V1–V4, postmortem/05C2 estacionado, scripts/05C1 e caches anteriores intactos.
- Phase A manifest/universe/exclusion registry/protocolo/freeze/provenance e
  utilitário preservados byte a byte; nenhum código funcional/schema alterado.

## Estado e parada

- phaseB1Complete=true
- rawQuestionIndexExecuted=true
- frozenBeforeExecution=true
- manualPdfInspection=false
- rawAnomaliesHumanReviewed=false
- finalQuestionIndexCreated=false
- questionSelectionStarted=false
- questionSelectionExecuted=false
- groundTruthStarted=false
- groundTruthCreated=false
- auditorExecuted=false
- metricsSeen=false
- merge=false

Próximo separado: **V5 Phase B2 neutral question-index adjudication/final
freeze**. Nenhum review package, final index, manifest-v5-b, seleção das três
questões, GT ou Auditor nesta execução. Após commit/push B1: STOP.
