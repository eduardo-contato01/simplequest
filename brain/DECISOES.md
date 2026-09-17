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
