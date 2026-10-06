# Roadmap

Trabalho vigente em 2026-10-06. Estado factual em [[ESTADO_ATUAL]]; visão detalhada em [[IDEIAS_E_PROXIMOS_PASSOS]]. O roadmap anterior está integralmente preservado em [[HISTORICO]], fora da leitura padrão.

## Agora — Auditor

1. Fazer postmortem V4 sem patch: 5 unsafe_error e 1 partial.
2. Analisar também uma amostra estruturada dos 66 safe_abstention para entender perda de cobertura.
3. Classificar causas raiz: undercount, overcount, conflitos e abstenções; não assumir a causa antes da análise.
4. Implementar depois somente correções generalizáveis, com TDD, controles positivos e negativos e sem regras específicas para casos individuais.
5. Se houver mudança funcional após analisar o V4, criar novo Holdout V5 cego; preservar o primeiro resultado V4.
6. Avaliar novamente precision + coverage, buscando recuperar cobertura sem perder precisão.

Meta operacional: precision >= 99,5%; coverage >= 80%; unsafe_error <= 0,5%; direção ideal de precision 99,8–99,9%. São metas futuras, não o desempenho atual.

Ver [[AUDITORIA_PROVAS]]. Esta reorganização documental não executa postmortem, patch ou Auditor.

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
