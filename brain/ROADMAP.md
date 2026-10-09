# Roadmap

Trabalho vigente em 2026-10-06. Estado factual em [[ESTADO_ATUAL]]; visão detalhada em [[IDEIAS_E_PROXIMOS_PASSOS]]. O roadmap anterior está integralmente preservado em [[HISTORICO]], fora da leitura padrão.

## Agora — Auditor

1. [x] Postmortem V4 diagnóstico sem patch: cinco unsafe_error e um partial; replay restrito reproduziu os seis, sem rerun oficial.
2. [x] Amostra metadata-only de 24/66 safe_abstention congelada antes de inspeção; causas/recovery classificadas sem extrapolar ganhos para as 66. Nenhuma revisão visual pendente.
3. [x] Patch 01 `selected_response_set_contract`: contrato/provenance preservados downstream; TDD e replay diagnóstico restrito PASS. Ver [Patch 01](../audit/postmortem/V4_PATCH_01_SELECTED_RESPONSE_SET.md).
4. [x] Patch 02 `response_set_completeness`: safety gate de incomplete/ambiguous/unknown aplicável; TDD e replay diagnóstico restrito PASS, sem labels inventados ou stitching. Ver [Patch 02](../audit/postmortem/V4_PATCH_02_RESPONSE_SET_COMPLETENESS.md).
5. [x] Patch 03A `neutral_boundary_identity_and_grammar`: identidade canônica/impressa e variantes neutras target-aware; TDD e replay restrito PASS. Ver [Patch 03A](../audit/postmortem/V4_PATCH_03A_BOUNDARY_IDENTITY_GRAMMAR.md). Boundary inteiro não concluído.
6. [x] Patch 03B `neutral_boundary_scope_and_column_peers`: split exige peer index-backed com match único e geometria; TDD e replay restrito PASS. Ver [Patch 03B](../audit/postmortem/V4_PATCH_03B_BOUNDARY_SCOPE_COLUMNS.md).
7. [x] Patch 03C `neutral_boundary_word_line_reconstruction`: line-first, fallback somente por words observadas e reconstrução dentro de scope reliable; TDD/replay restrito sem unsafe. Ver [Patch 03C](../audit/postmortem/V4_PATCH_03C_BOUNDARY_WORD_RECONSTRUCTION.md). Patches 03A/03B/03C planejados concluídos, não boundary perfeito; CID ausente e abstenções conservadoras permanecem.
8. [x] Patch 04 `marker_role_and_spacing`: parenthesized whitespace e selected membership autoritativo para role; enumerações/controles preservados, TDD/replay restrito sem unsafe. Ver [Patch 04](../audit/postmortem/V4_PATCH_04_MARKER_ROLE_SPACING.md).
9. [x] Patch 05A `visual_response_set_evidence`: native render fallback text-first, cluster visual único + regiões/gates para count; labels unknown sem glyph evidence. TDD/replay dos 30 sem novas regressões unsafe. Ver [Patch 05A](../audit/postmortem/V4_PATCH_05A_VISUAL_RESPONSE_SET.md).
10. [x] Patch05B1 `reconstructed_terminal_closure_guard`: provenance e closure conservadora; TDD/replay de cinco controles PASS. Ver [05B1](../audit/postmortem/V4_PATCH_05B1_RECONSTRUCTED_CLOSURE.md).
11. [x] Patch05B2 `authoritative_selected_set_requires_completeness`: loophole mode unknown fechado; TDD/14 suítes e replay final dos 30 após publicar os dois subpatches PASS, duas regressões reveladas neutralizadas sem nova unsafe. Ver [05B2](../audit/postmortem/V4_PATCH_05B2_COMPLETENESS_APPLICABILITY.md).
    Ambos surgiram da ampliação do regression sample aos 30 no Patch05A; [bisseção](../audit/postmortem/V4_PATCH_05B_SAFETY_BISECT.md) confirmou causas distintas, não um único patch planejado no postmortem original. Observation complementary permaneceu posterior à segurança 05B.
12. [x] Patch05C1 `scoped_complementary_marker_ocr`: fallback conservador reliable/crop/markers explícitos; TDD/14 suítes/compile e replay30 sem nova unsafe. Dois revealed targets obtiveram conjuntos completos; q13 abstém por A não reconhecido. Gutter diagnóstico confirmou recognition limit e não entrou em produção; nenhum parameter search. Ver [05C1](../audit/postmortem/V4_PATCH_05C1_SCOPED_COMPLEMENTARY_MARKER_OCR.md). Isso não é métrica de coverage.
13. [~] Patch05C2 `visual_header_and_layout_observation`: experimento diagnóstico encerrado/estacionado, capability NÃO promovida; 0/2 targets revelados recuperaram boundary, sem métrica de coverage. Produção/testes revertidos para 05C1; revisitar somente se evidência futura/blind justificar. Ver [05C2](../audit/postmortem/V4_PATCH_05C2_VISUAL_HEADER_LAYOUT.md).
14. [x] V5 Phase A document selection/freeze: branch `audit/holdout-v5-blind`, candidate `3b306d6a544cc63928ec8adf07640b224651742e`/baseline05C1; 48 documentos metadata-only determinísticos, overlap zero com V1–V4/calibração, antes de inspeção de questões. Ver [freeze V5](../audit/holdout/V5_DOCUMENT_SELECTION_FREEZE.md). Auditor funcional congelado; V5 completo NÃO concluído.
15. [x] V5 Phase B1 raw neutral question index freeze: protocolo/config congelados antes da execução única, 48 documentos/1063 questões brutas; validações automáticas PASS, sem adjudicação. Ver [raw freeze](../audit/holdout/V5_QUESTION_INDEX_RAW_FREEZE.md). Phase B inteira NÃO concluída.
16. [x] V5 Phase B2a neutral triage freeze: política V4 sem retuning, queue48/tiers A22/B4/C14/D8, nenhum PDF/review visual/correção. Ver [triagem B2a](../audit/holdout/V5_QUESTION_INDEX_TRIAGE.md). Todos os 48 continuam sujeitos à revisão neutra futura; índice final NÃO concluído.
17. [x] V5 B2b Tier A Batch01 review package freeze: 11 documentos nas posições fixas 1–11/22, fingerprints e cópias byte-idênticas 11/11, context neutro ignorado e hashes congelados; nenhuma adjudicação/render/OCR. Ver [package Batch01](../audit/holdout/V5_TIER_A_BATCH_01_REVIEW_PACKAGE.md). Tier A e Phase B NÃO concluídos; Batch02 intocado.
18. [x] V5 B2b Tier A Batch01 neutral adjudication: 11/11 documentos, 182/182 páginas disponíveis, 1136 questões canônicas (raw345/delta+791), unresolved=0. [Relatório Batch01](../audit/holdout/V5_TIER_A_BATCH_01_ADJUDICATION.md); adendo pós-freeze aplicado ao doc8 (26 objetos, q18–q21 não fabricadas), checkpoint histórico preservado; documentos 1–7 não re-adjudicados. Somente Batch01 concluído, Tier A/Phase B NÃO concluídos. Próxima prioridade separada: V5 B2b Tier A Batch02 review package freeze; Batch02 não preparado/aberto aqui. Final index/selection/GT/Auditor/metrics=false. GT somente após selection freeze; Auditor somente após GT/config/cache freeze, execução primeira única/imutável e métricas somente após result freeze.
19. [x] V5 B2b Tier A Batch02 review package freeze: posições globais 12–22/22, 11 documentos, 120 páginas e 109 questões brutas; fontes/fingerprints/cópias byte-idênticas 11/11, sem reranking ou substituição. [Package Batch02](../audit/holdout/V5_TIER_A_BATCH_02_REVIEW_PACKAGE.md). Batch01/adendo preservados; nenhuma inspeção visual, adjudicação ou avaliação de source incompleteness nesta preparação. Próximo separado: V5 B2b Tier A Batch02 neutral visual adjudication. Tier A/Phase B NÃO concluídos; final index/selection/GT/Auditor/metrics=false.
20. Avaliar novamente precision + coverage em V5 blind depois dos freezes e da execução autorizada, buscando recuperar cobertura sem perder precisão.

Futuro condicionado à recorrência do padrão q13: possible marker-glyph recognition / alternate observation strategy. Nenhuma tarefa ou Patch05C3 criado agora.

Meta operacional: precision >= 99,5%; coverage >= 80%; unsafe_error <= 0,5%; direção ideal de precision 99,8–99,9%. São metas futuras, não o desempenho atual.

Ver [[AUDITORIA_PROVAS]]. Postmortem e Patches 01/02/03A/03B/03C/04/05A/05B1/05B2/05C1 concluídos; experimento 05C2 estacionado/não promovido; V5 Fases A/B1/B2a concluídas, Tier A Batch01 adjudicado e Batch02 review package congelado. Tier A inteiro/Phase B NÃO concluídos; próximo separado=Tier A Batch02 neutral visual adjudication. Índice final, seleção de questões, GT e avaliação V5 ainda não iniciados.

## Depois — Ingestão/transcrição

1. Definir o contrato StructuredQuestionDraft.
2. Reutilizar observation, boundary e estrutura do Auditor, sem segundo motor independente.
3. Extrair texto, alternativas, mídia, fórmulas, tabelas e provenance.
4. Criar staging/review queue, com referência ao PDF/página/região.
5. Registrar confidence por componente.
6. Fazer revisão humana por exceção e baixa confiança, antes do catálogo oficial.
7. Processar lotes progressivos e medir erros sistêmicos antes de ampliar escala.

Ver [[IMPORTADOR]] e [[IDEIAS_E_PROXIMOS_PASSOS]].

## Taxonomia

1. Definir a primeira versão fechada: discipline/area/content/subcontent/skill.
2. Usar IDs estáveis, relações N:N e confidence.
3. Fazer a IA escolher IDs existentes, sem criação livre de categorias.
4. Encaminhar baixa confiança à revisão humana.

## Produto 2.0

### Aluno

Início / Feed / Mundo / Configurações.

### Professor

Pesquisa / Simulados / Configurações.

Detalhes de aprendizagem, mundo visual, construção de simulados e defaults em [[IDEIAS_E_PROXIMOS_PASSOS]]. São capacidades planejadas, não já implementadas.

## Infraestrutura de produto

Autenticação, onboarding por papel, permissões, design system, mobile, cobrança mínima, testes E2E, performance, observabilidade e backups/hardening.

## Meta 31/12/2026

Beta real para professor/aluno, não produto definitivo. Objetivo mínimo:

- banco significativo de questões, pesquisa e filtros;
- simulados;
- feed inicial e mundo inicial;
- ingestão assistida e taxonomia;
- auth e onboarding;
- interface consistente;
- cobrança inicial;
- estabilidade suficiente para usuários reais.

## Manutenção

- Validar entradas da API com schemas explícitos.
- Implementar autorização real, separada da noção editorial de “Administrador”.
- Tornar localStorage resiliente e proteger edição não salva.
- Atualizar README para o produto real e resolver/explicar a divergência de stats.json.
- Documentar importador e dependências de forma reprodutível.
- Priorizar questões com pending-media e validar amostras ricas antes de autenticar lotes.
- Tratar gabarito vazio, anulado ou incompatível antes de usar pontuação automática.
- Preservar impressão e exemplos baseline nas reorganizações futuras.

Etapas concluídas do Holdout V4 não são tarefas pendentes deste roadmap; consultar [[HISTORICO]], [[AUDITORIA_PROVAS]] e o log cronológico quando necessário.

## Próxima prioridade V5 — decisão de integridade do Batch02, 2026-10-08

- [ ] V5 B2b Tier A Batch02: retomar revisão visual neutra em execução separada, começando pela comprovação de identidades/boundaries do documento 3 sob a [decisão congelada](../audit/holdout/V5_SOURCE_INTEGRITY_INCONCLUSIVE_DOC03.md), especialmente quanto à página7, antes de documentos4–11. PDF retido; integridade do exame original inconclusiva, sem substituição nem aplicação da exceção anterior. 21 identidades ainda candidatas; ambiguidade exige STOP e impede elegibilidade/adjudicação integral.
- Batch02/Tier A/Phase B NÃO concluídos. Checkpoint/diagnóstico e documentos1/2 preservados; documentos4–11 não iniciados. Ressalva/escopo=`frozen_available_pdf_content` e timing pós-freeze devem acompanhar a metodologia final V5. Nenhuma adjudicação nesta decisão; final index/selection/GT/Auditor/metrics/merge=false.

## Próxima prioridade V5 — insuficiência de questões do Batch02 doc11, 2026-10-08

Este checkpoint prevalece sobre as prioridades históricas acima. Documentos1–10
adjudicados/214questões e140páginas do Batch02 original revisadas; doc11 permanece
unresolved com menos de três identidades independentes comprovadas nas4páginas.
Batch02/Tier A/Phase B NÃO concluídos.

- [ ] **V5 objective replacement materialization and supplemental review package**:
  execução separadamente autorizada sob o [adendo geral pós-freeze](../audit/holdout/V5_INSUFFICIENT_QUESTIONS_REPLACEMENT_RULE.md);
  errata/provenance histórica e efetiva, confirmação objetiva do candidato
  `v5-doc-e1c73fb849ef80a6`, artefatos neutros suplementares sob configuração congelada
  sem reexecutar raw original e freeze do package específico antes da adjudicação visual.
- Candidato determinado somente pelo ranking original; PDF não aberto e contagem
  mínima não presumida. Nenhuma substituição/manifest efetivo nesta decisão;
  final index/selection/GT/Auditor/metrics/merge=false. Não retomar adjudicação agora.

## Próxima prioridade V5 — package suplementar doc11, 2026-10-08

Este checkpoint prevalece sobre as prioridades históricas acima.

- [x] Substituição objetiva pós-freeze materializada: manifest efetivo r1 com48documentos,
  uma substituição no mesmo estrato/ranking2 e47linhas preservadas; histórico intacto.
  Ver [errata](../audit/holdout/V5_OBJECTIVE_REPLACEMENT_DOC11.md).
- [x] Package suplementar validado: freeze formal pelo commit de introdução e publicação
  desta etapa, antes da adjudicação visual. Uma cópia byte-idêntica/12páginas; índice
  neutro suplementar em execução única/native/raw18/anomalias2, sem contagem canônica
  ou mínimo3 certificados. [Package](../audit/holdout/V5_TIER_A_BATCH_02_SUPPLEMENTAL_REVIEW_PACKAGE.md).
- [ ] **V5 Tier A Batch02 supplemental neutral visual adjudication**: execução separada
  após publicação, somente o substituto `v5-doc-e1c73fb849ef80a6`; preservar docs1–10
  e checkpoints. Adjudicação suplementar pendente; Batch02/TierA/PhaseB incompletos.
- Nenhuma revisão visual/selection/GT/Auditor/métricas/finalIndex/merge nesta preparação;
  não iniciar TierB. Ressalva técnica pdfinfoFileSize0 não bloqueante por decisão externa,
  causa não determinada; tamanho binário182017/fingerprint/páginas12 confirmados.

## Próxima prioridade V5 - Tier A concluído, 2026-10-09

Este checkpoint prevalece sobre as prioridades históricas acima.

- [x] V5 Tier A Batch02 neutral adjudication:11documentos efetivos/148páginas/234questões, unresolved0. [Fechamento](../audit/holdout/V5_TIER_A_BATCH_02_ADJUDICATION.md);214questões anteriores intactas, somente substituto12páginas/20questões revisado após publicação do package.
- [x] Tier A completo:22documentos, Batch01 validado11/182páginas/1136questões e Batch02 validado11/148páginas/234questões; PhaseBComplete=false.
- [ ] **V5 Tier B neutral review package freeze**: próxima tarefa SEPARADA, ainda não iniciada. TiersB/C/D continuam pendentes.
- Manifest efetivoR1 e substituição pós-freeze/performance-blind explícitos; original doc11 unresolved no histórico, checkpoints e decisões1–10 preservados. Ressalvas doc3/doc8/doc10 permanecem obrigatórias na metodologia final.
- Final index/selection/GT/Auditor/metrics/merge=false; STOP após commit/push, sem preparar TierB nesta execução.

## Próxima prioridade V5 — package Tier B, 2026-10-09

Este checkpoint prevalece sobre as prioridades históricas acima.

- [x] V5 Tier B neutral review package:4documentos/92páginas/156raw/156eventos automáticos, ordem congelada23–26, cópias byte-idênticas4/4 e contexto neutro vinculado por hash; freeze formal pelo commit de introdução/publicação. [Package Tier B](../audit/holdout/V5_TIER_B_REVIEW_PACKAGE.md).
- [ ] **V5 Tier B neutral visual adjudication**: próxima execução separadamente autorizada, após publicação; nenhuma adjudicação ou correção raw nesta preparação. TiersC/D pendentes.
- TierAComplete=true/22documentos/330páginas/1370canônicas; TierBAdjudicated=false/PhaseBComplete=false. Ressalvas e provenance pós-freeze preservadas; final index/selection/GT/Auditor/metrics/merge=false; STOP após push.
