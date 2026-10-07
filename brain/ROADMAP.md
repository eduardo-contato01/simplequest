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
    Ambos surgiram da ampliação do regression sample aos 30 no Patch05A; [bisseção](../audit/postmortem/V4_PATCH_05B_SAFETY_BISECT.md) confirmou causas distintas, não um único patch planejado no postmortem original. Observation complementary permanece posterior e não iniciada.
    Próxima prioridade separada: `observation_complementary_capability`, não iniciada; sem regras por casos individuais.
12. Criar novo Holdout V5 cego após as mudanças funcionais; preservar o primeiro resultado V4.
13. Avaliar novamente precision + coverage em V5 blind, buscando recuperar cobertura sem perder precisão.

Meta operacional: precision >= 99,5%; coverage >= 80%; unsafe_error <= 0,5%; direção ideal de precision 99,8–99,9%. São metas futuras, não o desempenho atual.

Ver [[AUDITORIA_PROVAS]]. Postmortem e Patches 01/02/03A/03B/03C/04/05A/05B1/05B2 concluídos; observation complementary e avaliação V5 blind permanecem futuros.

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
