# V5 Batch02 — integridade inconclusiva do documento 3

V5_SOURCE_INTEGRITY_DECISION_DOC03=RECORDED

## Decisão, autoridade e timing

Decisão externa explicitamente autorizada em 2026-10-08. Branch:
`audit/holdout-v5-blind`; HEAD de origem:
`dbd2c3d23cc8e87b7a32001d22e28d09211e5c19`.
Freeze formal pelo commit que introduz este relatório e a
[decisão estruturada](v5-source-integrity-decision-doc03.json).

Documento: `v5-doc-815b83630e3d8c98`, Tier A / Batch02, posição 3
(global Tier A 14), fingerprint
`815b83630e3d8c9899695cdcc4a30f96ee4a5f411d541d954c534cd5a8f9ef1a`.

**Preservar o PDF congelado, sem substituição e sem certificar a completude
da prova original.** Decisão pós-freeze documental, anterior à seleção de
questões, GT e Auditor; performance-blind e NÃO originalmente pré-registrada.
Não autoriza alterar a população por conveniência ou com base em métricas futuras.

## Evidência já estabelecida, não reexaminada aqui

O diagnóstico ignorado em
`outputs/audit/holdout/v5-tier-a-batch-02-review/source-integrity-doc03.json`
tem SHA256
`0bcce1a253502f96a78516e4f7a7bdea1c3617ddde379da58a0086dba1226f46`.

- PDF contém 9 páginas físicas; capa declara 12 folhas e referencia a folha 10.
- Paginação impressa observada: Fl.02..Fl.08, contínua; última página física
  não numerada e em branco.
- Página 7 possui imagem posicionada parcialmente fora da MediaBox
  (aproximadamente 9,79 pontos na margem direita). MediaBox e CropBox iguais;
  a faixa recortada permanece codificada na imagem incorporada.
- Árvore de páginas legível; nenhum objeto de página órfão encontrado.
- Não se confirmou perda efetiva de bytes nem a completude do caderno original.
  Classificação diagnóstica C: `sourceIntegrityInconclusive=true`.

A validade técnica e a presença de 21 identidades candidatas não comprovam
a integridade do exame original ou os boundaries de cada questão.
Nenhuma nova inspeção visual, renderização, extração PDF, OCR ou adjudicação
foi realizada para registrar esta decisão.

## Por que não substituir nem aplicar a exceção anterior

O [protocolo original](PROTOCOL_V5.md) admite substituição somente por ausência,
drift de fingerprint, corrupção objetiva ou duplicata, pelo próximo elegível
do MESMO ranking/stratum e com errata/provenance explícitos.
O diagnóstico não estabeleceu essas condições neste caso.

Há substituto elegível, `v5-doc-3d252b7c947f51ff`, no estrato congelado
`(text_native, CMF, 2004-2009, 6º Ano)`, conforme metadados já registrados.
Seu PDF não foi aberto. Sua existência, isoladamente, não justifica substituir.

O [adendo anterior](V5_OBJECTIVE_SOURCE_INCOMPLETENESS_RULE.md) NÃO foi aplicado:
os seis critérios não foram integralmente satisfeitos, inclusive ausência
de substituto elegível. Esta decisão separada não reescreve o protocolo,
não altera o adendo, não marca `sourceIncomplete=true` e não resolve
retroativamente o diagnóstico como prova de integridade ou de corrupção.

## Escopo e gates da futura adjudicação

`adjudicationScope=frozen_available_pdf_content`: considerar somente a
representação digital congelada nas nove páginas disponíveis. Isso não certifica
a integridade do exame original. As 21 identidades do checkpoint permanecem
candidatas, sem aprovação automática.

Em retomada separadamente autorizada, cada questão precisa de identidade
diretamente observada, número canônico justificável, pageStart e pageEnd comprovados,
sem ambiguidade estrutural relevante. Verificar especificamente os boundaries
das questões afetadas pela página física 7. O deslocamento da imagem é comprovado,
mas não demonstra que todo conteúdo relevante esteja visível.

Se a região cortada impedir comprovar algum boundary: manter a questão
estruturalmente unresolved, não inventar limites, não classificá-la como elegível
à seleção, não declarar o documento integralmente adjudicado e STOP para nova
decisão externa. Se todas as questões efetivamente observáveis satisfizerem os
gates e as validações, o documento poderá ser adjudicado apenas nesse escopo,
preservando a ressalva.

Não fabricar questões/números/páginas nem reconstruir conteúdo para reconciliar
9 páginas com 12 folhas. Não usar GT, gabaritos, Auditor, resposta semântica ou métricas.

## Ressalva metodológica permanente

```text
sourceIntegrityInconclusive=true
objectiveSourceCorruptionConfirmed=null
originalExamCompletenessCertified=false
frozenPdfRetained=true
replacementAuthorized=false
sourceIncompleteExceptionApplied=false
adjudicationScope=frozen_available_pdf_content
performanceBlind=true
postFreezeDecision=true
preRegisteredBeforeSourceInspection=false
questionSelectionStarted=false
groundTruthStarted=false
auditorExecuted=false
metricsSeen=false
```

`objectiveSourceCorruptionConfirmed=null` significa não determinado: não afirma
true nem false. Não se declara `originalExamComplete=true`.

A ressalva, o escopo e o timing pós-freeze devem ser transportados à futura
adjudicação e à documentação metodológica final do V5. Não autorizam alterações
da seleção documental em função de desempenho futuro.

## Bindings e preservação

| Artefato | SHA256 |
| --- | --- |
| Decisão JSON | d532deef877a016d4715227395d80f402e3ec49659eea4409dd280ad364be7a4 |
| Checkpoint de adjudicação ignorado | b9c79b68cc0544dc9f070de336ab9f9ccb18414eb58267f5100feef5ac3b70d6 |
| Diagnóstico técnico ignorado | 0bcce1a253502f96a78516e4f7a7bdea1c3617ddde379da58a0086dba1226f46 |
| Manifest V5 | c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62 |
| Protocolo original | 77f8bb06d7c8eadba79c7ef70a580eebeff2d74f324017ae8e220f11bea9bb95 |
| Adendo anterior | 6e53620188ef104d5880ee04e84ef382675a64a8fcc927f69543e6ca273e3541 |
| Raw index | 68aa187e1e33cc38c92634b2fe362a0e260666e22c8cf58427651b0a6e33ef84 |
| Review queue | 027eac06938f3520ff6c7ca8b4281608d5e31281ac9e16cc3b0d5b418ba9f00b |
| Batch01 adjudication | e7b089ff28946824eb480498b457124ac20aeefc62a2e8cce547a1d7cd09e770 |
| Batch02 package | 33e9ba54c4ff51801a2fad094d0cf6613728494bd085697c4c8f53f42a166f01 |

Outros bindings (raw report, review context e files list) constam na decisão JSON.
Artefatos originais, Batch01, package Batch02, diagnóstico, checkpoint, PDFs,
caches, código funcional do Auditor/indexador e V1–V4 preservados.
O preflight conferiu 4.943 arquivos existentes e hashes binários das 11 fontes/cópias;
somente este registro novo e as atualizações documentais explicitamente autorizadas
podem mudar nesta etapa. Nenhum output local deve entrar no stage.

Checkpoint permanece byte-idêntico: documentos 1/2 têm 40/21 questões adjudicadas;
documento 3 mantém 21 candidatas e status unresolved; documentos 4–11 não iniciados.
Registros antigos do CONTEXTO e brain preservados, com nova entrada incremental
e estado factual separado; não marcar Batch02 ou Tier A completos.

## Próximo e STOP

Batch02Incomplete=true; tierAComplete=false; phaseBComplete=false.
Próxima execução separada: retomar adjudicação visual neutra do Batch02,
começando pela comprovação de identidades/boundaries do documento 3 sob esta
decisão congelada, antes de documentos 4–11.

Após commit/push desta decisão, STOP. Não retomar documentos 3–11, abrir substituto,
preparar Tier B, criar final question index, selecionar questões, criar GT,
executar Auditor, calcular métricas ou fazer merge.
