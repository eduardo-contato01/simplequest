# Estado Atual

Última leitura ampla: 2026-09-14. O repositório estava limpo e sincronizado com `origin/main` antes da criação deste vault.

## Produto implementado

- Aplicação Vinext/Vite com React 19 e TypeScript.
- Página `/`: busca no acervo, filtros, cartões de questões, seleção de alternativas, seleção para simulado e impressao via `window.print()`.
- Pagina `/revisao`: curadoria editorial, cadastro manual, edicao rica por blocos, salvar rascunho/pronto, autenticar e travar, desbloquear com motivo, restaurar original e exportar JSON.
- API `/api/questions/revisions`: CRUD parcial de revisoes em D1.
- Catalogo base em `public/data/questions.json`; imagens em `public/question-media/`.

## Numeros confirmados em `questions.json`

- 1.217 questoes.
- 9 fontes: CMB, CMBH, CMBel, CMC, CMCG, CMDPII, CMPA, CMT, OBRL.
- Periodo: 2003-2024.
- Status: 660 `ready`, 557 `review`.
- 295 questoes com `isLocked` e `authenticatedAt`.
- 318 com `hasMath`, 125 com `hasTable`, 412 com `hasMedia`.
- 1.217 declaram formato efetivo `ABCDE`; o codigo tambem suporta `ABCD` e `CE`.
- 450 arquivos `.webp` em `public/question-media/`.
- 463 referencias de imagem em blocos, 450 URLs distintas.
- 6 questoes possuem ao menos um bloco `pending-media`.

## Divergencias observadas

- `README.md` ainda descreve principalmente o starter Vinext, nao o produto SimpleQuest atual.
- `public/data/stats.json` registra 543 `ready` e 674 `review`, divergindo do catalogo atual.
- A interface da home mostra numeros fixos de acervo/backlog; os valores nao sao calculados em tempo de execucao.

## Validacao recente conhecida

- `npm run test` passou apos o ultimo commit publicado.
- `npm run lint` terminou com codigo 0, mas reportou avisos em arquivos gerados/declarações (`outputs/component-contracts.mjs`, `types/cloudflare-runtime.d.ts`).

## Auditor — estagio atual (freeze V1)

- Auditor V1 entrou em fase de **freeze arquitetural / preparacao para holdout**.
- Camadas atuais: (1) admission/preflight; (2) marker/profile/page scope; (3) OCR content; (4) response structure; (5) visual marker evidence; (6) response regions/slots; (7) response evidence fusion; (8) observation adapter OCR/native.
- Tudo continua shadow/read-only onde aplicavel; a V1 de OCR ainda **nao** produz `difference`.
- Nenhuma hipotese de estrutura e promovida ao catalogo.
- Proximo marco: holdout independente e medicao de precision/coverage/abstention por layout/familia.

Ver tambem: [[ARQUITETURA]], [[PROBLEMAS_CONHECIDOS]], [[ROADMAP]], [[AUDITORIA_PROVAS]].
