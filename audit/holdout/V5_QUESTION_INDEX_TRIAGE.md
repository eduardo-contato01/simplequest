# Holdout V5 — neutral question-index triage freeze (B2a)

`V5_QUESTION_INDEX_TRIAGE_FROZEN=PASS`

Somente triagem documental e ordem de revisão congeladas. Nenhuma inspeção
visual, interpretação individual de eventos, adjudicação ou correção realizada.
Raw index intacto; nenhum final question index, review package ou seleção.

## Fontes congeladas

- Branch: `audit/holdout-v5-blind`.
- Source freeze commit / base HEAD B1:
  `d63f5f9600a1da58cbb726f73ea3b1c32c1143bd`.
- [Raw index](question-index-v5-raw.json) file SHA256:
  `68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84`.
- [Raw report](question-index-v5-raw-report.json) file SHA256:
  `62b44980b921da7545a2aa0dd4d65f24c7e595d319b4294b8f8fcc93988a4d9f`.
- [Phase A manifest](manifest-v5-documents-frozen.json) file SHA256:
  `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- Phase A e B1 completas; fontes mantêm `protocolVersion=holdout-v5`.

Triagem derivada SOMENTE de raw/report/manifest: tipos e contagens de eventos
neutros, identidade e metadados documentais. Caminhos PDF são copiados como
strings do manifest, nunca abertos pelo utilitário. Método native/OCR, família,
ano, série e sourceType são apenas metadados, nunca critérios de tier/ordem.

## Política V4 reaproveitada, sem retuning

Referências metodológicas SOMENTE: [triage V4](V4_QUESTION_INDEX_TRIAGE.md) e
[review queue V4](question-index-v4-review-queue.json), cujo file SHA256 é
`088bb091436bb8a195244da2a037394d0da02f66835e2be228fa029809f92592`.
Nenhuma adjudicação Tier A/B/C/D do V4 foi consultada para decidir documentos V5.

Aplicar em ordem, com precedência A → B → C → D:

1. A: ao menos um `requires_neutral_verification` OU `unresolved_question_start`.
2. B: não A, com `non_monotonic_numbering` OU `rawAnomalyCount >= 20`.
3. C: não A/B, com `rawAnomalyCount > 0`.
4. D: `rawAnomalyCount == 0`; controle de zero anomalias automáticas.

Threshold >=20 imutável; nenhum Tier E. Zero anomalias NÃO certifica índice
canônico correto. `all48DocumentsReviewed=true` mantém os **48/48 documentos
obrigatoriamente sujeitos à revisão neutra futura**, não afirma revisão já
realizada: `manualAdjudicationPerformed=false`, neutralReviewsPerformed=0.

Ordenação única: tier crescente A/B/C/D, rawAnomalyCount decrescente,
documentId crescente. Sem escola, sourceType, OCR, dificuldade, conteúdo,
probabilidade de erro ou desempenho esperado na ordenação.

Review reasons fixos:

- A: `explicit neutral ambiguity or unresolved question-start sequence`
- B: `non-monotonic numbering or high raw anomaly volume`
- C: `remaining raw numbering/boundary anomalies`
- D: `zero automatic anomalies; neutral control review`

`reviewPolicy` conserva exatamente as expressões e evidências da fila V4.
Sua allowedEvidence refere-se SOMENTE à futura revisão neutra autorizada;
em B2a são permitidos apenas os três JSONs congelados, sem PDF/texto de páginas.

## Fila e contagens técnicas

- [Queue](question-index-v5-review-queue.json), file SHA256:
  `027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b`.
- documents=48; uniqueDocumentIds=48; missingDocuments=0; unknownDocuments=0.
- rawQuestions=1063; rawAnomalies=1183.
- Tier A=22; Tier B=4; Tier C=14; Tier D=8; soma=48.
- indexMethodDistribution: native=29; ocr=19.
- Todos aparecem exatamente uma vez; reviewRequired=true,
  responseSemanticsAllowed=false, answerKeyAllowed=false, auditorAllowed=false.
- Documento com zero questões brutas mantido, sem remoção/substituição.

| Evento diagnóstico automático | Contagem |
| --- | ---: |
| duplicate_question_number | 217 |
| missing_question_number | 887 |
| non_monotonic_numbering | 43 |
| requires_neutral_verification | 25 |
| unresolved_question_start | 11 |

Soma=1183 eventos, NÃO 1183 erros reais independentes. 217 duplicates não
significam 217 erros confirmados, e 887 missing events não significam 887
questões realmente ausentes. Nenhuma estimativa de qualidade/correções/coverage.

## Utilitário e gates

[v5_question_index_triage.py](v5_question_index_triage.py), file SHA256:
`d78911d65eb0a6e82ed845af2efe88cef527c8a4f81739b3bbce6cfcf42109be`.

Ferramenta documental em `audit/holdout/`, somente biblioteca padrão Python.
Não importa Auditor/response structure/PDF parser, não renderiza nem executa OCR.
Lê SOMENTE os três inputs congelados e confere seus hashes antes de transformar.
Queue UTF-8 sem BOM/LF, sem timestamps variáveis; reprodução byte-idêntica.

Verificação read-only:

```text
python -X utf8 audit/holdout/v5_question_index_triage.py
```

`--emit` emite a queue determinística; `--write` cria exclusivamente uma queue
ausente, sem sobrescrever freeze existente. Os bytes desta queue foram
materializados a partir de `--emit` e validados pela reprodução read-only.

Gates PASS: identidades/fingerprints/metadados e contagens por documento
conferem com fontes; tipos de eventos e totais exatos; política V4 comparada
literalmente; tiers conferidos por avaliação independente; dez testes sintéticos
incluindo precedência A e threshold 19/20; invariância à inversão da ordem dos
inputs; nenhum campo de predictions ou semântica de resposta na fila.

Freeze formal pelo commit de introdução B2a. Phase A/B1 (inclusive provenance
e protocolos), V1–V4, código funcional/indexador/Auditor e todos os caches
byte-preservados, conferidos contra snapshot de 4102 arquivos anterior à etapa.
Nenhum output/cache/render/PDF/código funcional será staged.

## Estado e STOP

- policyChangedFromV4=false
- phaseB2aComplete=true
- PDFsOpened=false
- rendersCreated=false
- anomaliesHumanReviewed=false
- responseSemanticsConsulted=false
- manualAdjudicationPerformed=false
- rawIndexUnchanged=true
- B1ArtifactsUnchanged=true
- auditorFunctionalCodeChanged=false
- finalQuestionIndexCreated=false
- questionSelectionStarted=false
- questionSelectionExecuted=false
- groundTruthStarted=false
- groundTruthCreated=false
- auditorExecuted=false
- metricsSeen=false
- merge=false

Próximo separado: **V5 Phase B2b neutral review/adjudication**, com revisão
visual neutra somente após autorização. Phase B/índice final NÃO concluídos.
Após commit/push desta B2a: STOP; não iniciar Tier A, abrir PDFs, criar review
packages, corrigir raw, criar final index, selecionar questões, criar GT ou
executar Auditor.
