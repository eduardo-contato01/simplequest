# Decisões

## Catálogo base mais revisões

O SimpleQuest usa `questions.json` como base versionada e aplica revisoes do D1 por `id`.

Motivo observado: preservar o acervo importado e permitir curadoria/cadastros sem regravar toda a base.

## PDF como fonte canônica de auditoria

Para auditoria de fidelidade, o PDF original prevalece sobre DOCX e catálogo.

Motivo: os DOCX são transcrições manuais muito fiéis, mas podem conter pequenas correções feitas durante a transcrição. O DOCX continua útil para estrutura, bookmarks, fórmulas, tabelas, imagens e associação das questões.

## Blocos ricos dentro da questão

Texto, fórmulas, scripts, tabelas e imagens ficam em `contentBlocks` e `alternativeBlocks`.

Motivo observado: questões reais combinam vários tipos de conteúdo e precisam manter ordem.

## Campos legados preservados

`content`, `stem`, `alternatives`, `formula`, `tableData` e `imageUrls` continuam existindo.

Motivo observado: compatibilidade com catálogo importado, preview, busca, exportação e normalizações antigas.

## Revisão editorial com trava

Questão autenticada recebe dados de autenticação/trava e fica protegida na API contra alterações de conteúdo sem desbloqueio.

Motivo observado: criar um marco editorial de confiança. Isso não equivale a controle real de permissão por usuário.

## Estado de uso no navegador

Filtros, seleção, respostas, gabaritos revelados, título do simulado e rolagem são salvos em `localStorage`.

Motivo observado: manter continuidade local sem exigir login ou tabelas de usuário.

## Impressão pelo navegador

O simulado usa uma folha escondida e `window.print()`, não geração de PDF no servidor.

Motivo observado: reaproveitar renderização React/CSS e evitar backend de documentos.

## Brain documental

Este diretório deve ser memória operacional curta. Detalhes históricos longos permanecem em `docs/`.

Motivo: evitar que o vault vire diário ou duplicata de logs.

Ver tambem: [[ARQUITETURA]], [[MODELO_DE_QUESTAO]].

## Direção persistente de produto — 2026-10-06

As decisões abaixo orientam trabalho futuro; não declaram funcionalidades já implementadas. Detalhes em [[IDEIAS_E_PROXIMOS_PASSOS]]; sequência em [[ROADMAP]].

### Navegação por perfil

Aluno: Início / Feed / Mundo / Configurações. Professor: Pesquisa / Simulados / Configurações.

Motivo: separar objetivos de aprendizagem e preparação de provas, mantendo experiência consistente por papel.

### Feed leve

O 2.0 prioriza questões, leitura dinâmica, microexplicações, mapas mentais e revisão; vídeo não é prioridade inicial.

Motivo: formatos rápidos, leves e baratos de carregar, combinando prática e explicação.

### Mundo do conhecimento

Casas, prédios e outros elementos representam conhecimento validado e domínio; não premiar apenas tempo de tela nem tratar o mundo como minigame separado.

Motivo: progresso visual deve refletir aprendizado real, não permanência na aplicação.

### Motor único

Auditor e futura ingestão/transcrição compartilham observation, boundary e estrutura; não criar segundo motor independente.

Motivo: reutilizar provenance e confiança por componente, reduzindo duplicação e revisão manual.

### Taxonomia fechada

Taxonomia versionada com IDs estáveis e relações N:N; IA seleciona IDs existentes com confidence, sem criação livre de categorias.

Motivo: manter classificação pedagógica consistente e revisável em escala.

### Onboarding progressivo

Aluno/professor primeiro, seguido de poucas perguntas. Onboarding conversacional por texto/voz/contexto fica para 3.0.

Motivo: personalizar com baixa fricção, sem tornar o conversacional requisito do 2.0.

### Beta 31/12/2026

Marco de beta real e utilizável por professores e alunos, não produto definitivo.

Motivo: orientar um escopo operacional entregável e evolução progressiva.
