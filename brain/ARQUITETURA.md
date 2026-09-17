# Arquitetura

## Stack

- UI: React 19, TypeScript, CSS global em `app/globals.css`.
- Rotas: convenções de App Router, executadas por Vinext sobre Vite.
- Runtime: Cloudflare Worker em `worker/index.ts`.
- Dados persistidos: Cloudflare D1 via Drizzle.
- Matematica: KaTeX para exibição; MathLive para edição de fórmulas.
- Assets: JSON e imagens estáticas em `public/`.

## Fluxo de dados

1. `public/data/questions.json` fornece o catálogo base.
2. `/api/questions/revisions` retorna revisões salvas em D1.
3. `mergeQuestionCatalog()` sobrepõe revisões por `id` e adiciona cadastros manuais.
4. `normalizeQuestionContent()` aplica normalizações de compatibilidade.
5. `QuestionBlocks`, `QuestionAlternatives` e `QuestionMedia` renderizam o resultado.

## Rotas e responsabilidades

- `/`: composição em `app/page.tsx`; usa `useQuestionsWorkspace()`.
- `/revisao`: painel cliente em `app/revisao/page.tsx`; carrega base + revisões e salva alterações pela API.
- `/api/questions/revisions`: GET, POST e DELETE em `app/api/questions/revisions/route.ts`.
- `/_vinext/image`: endpoint do Worker para otimização Vinext; as imagens das questões usam `<img>` direto.

## Persistência

- Catálogo canônico versionado: `public/data/questions.json`.
- Revisões e cadastros manuais: tabela D1 `question_revisions`.
- Estado local da home: `localStorage` chave `simplequest:questions-view:v1`.
- Estado local da revisão: `localStorage` chave `simplequest:review-view:v1`.

## Banco

- Schema em `db/schema.ts`.
- Acesso em `db/index.ts`.
- A tabela `question_revisions` armazena listas e blocos como JSON serializado em colunas `TEXT`.
- `ensureQuestionRevisionTable()` cria tabela, índices e colunas faltantes em tempo de requisição.
- Migrações versionadas ficam em `drizzle/`.

## Componentes centrais

- `app/question-model.ts`: tipos, normalização, merge e carregamento do catálogo.
- `app/hooks/useQuestionCatalog.ts`: carregamento cliente do catálogo.
- `app/hooks/useQuestionsWorkspace.ts`: filtros, busca, página, respostas, seleção e persistência local da home.
- `app/components/QuestionBlocks.tsx`: renderizador de blocos de texto, fórmula, script, tabela e imagem.
- `app/components/ContentBlocksEditor.tsx`: editor de blocos ricos no painel de revisão.

Ver tambem: [[MODELO_DE_QUESTAO]], [[IMPORTADOR]], [[DECISOES]].
