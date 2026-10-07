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
16. Próxima prioridade separada: V5 Phase B2 neutral question-index adjudication/final freeze. Question selection ainda não iniciada; GT somente após selection freeze, Auditor somente após GT/config/cache freeze, execução primeira única/imutável e métricas somente após result freeze.
17. Avaliar novamente precision + coverage em V5 blind depois dos freezes e da execução autorizada, buscando recuperar cobertura sem perder precisão.

Futuro condicionado à recorrência do padrão q13: possible marker-glyph recognition / alternate observation strategy. Nenhuma tarefa ou Patch05C3 criado agora.

Meta operacional: precision >= 99,5%; coverage >= 80%; unsafe_error <= 0,5%; direção ideal de precision 99,8–99,9%. São metas futuras, não o desempenho atual.

Ver [[AUDITORIA_PROVAS]]. Postmortem e Patches 01/02/03A/03B/03C/04/05A/05B1/05B2/05C1 concluídos; experimento 05C2 estacionado/não promovido; V5 Fases A/B1 concluídas, B2 adjudicação/índice final, seleção de questões, GT e avaliação V5 ainda não iniciados.

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
