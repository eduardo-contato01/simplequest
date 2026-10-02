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

## Auditor / Holdout V4 — checkpoint 2026-10-02

- Branch: `audit/holdout-v4`. Arquitetura V1 do Auditor **congelada para avaliacao**.
- Camadas atuais: (1) admission/preflight; (2) marker/profile/page scope; (3) OCR content; (4) response structure; (5) visual marker evidence; (6) response regions/slots; (7) response evidence fusion; (8) observation adapter OCR/native.
- Tudo continua shadow/read-only onde aplicavel; a V1 de OCR ainda **nao** produz `difference`.
- Nenhuma hipotese de estrutura e promovida ao catalogo.
- Candidate pool V4 congelado; selecao documental concluida com 48 documentos; raw neutral question index congelado.
- Tier A: 18/18 adjudicados. Tier B: 9/9 adjudicados e commitados, com 246 questoes canonicas.
- Tier C: 13/13 adjudicados, com 430 questoes canonicas. Tier D: 8/8 adjudicados, com 180 questoes canonicas (182 raw; duas QUESTAO 21 de Producao Textual excluidas por decisao humana). Todos os tiers de adjudicacao neutra estao concluidos.
- Tier C review package preservado e congelado; adjudicacao concluida (`true`) a partir da revisao visual humana fornecida. Ver [adjudicacao Tier C](../audit/holdout/V4_TIER_C_ADJUDICATION.md).
- Tier D review package/contexto preservados como snapshots de preparacao; adjudicacao humana concluida (`true`). Ver [adjudicacao Tier D](../audit/holdout/V4_TIER_D_ADJUDICATION.md).
- Final Question Index V4 criado e congelado (`true`): 48/48 documentos adjudicados, 1.732 questoes canonicas (A=876, B=246, C=430, D=180). Ver [indice final V4](../audit/holdout/V4_FINAL_QUESTION_INDEX.md). Question Selection V4 concluida (`true`): 144 questoes, 3 por documento, seed 20261001; serializacao UTF-8 reparada sem nova selecao, com os mesmos 144 IDs. Phase A e indice final preservados. Ver [freeze da selecao](../audit/holdout/V4_QUESTION_SELECTION_FREEZE.md).
- Ground Truth V4: nao criado nem congelado (`false`). Batch 01 preparado para revisao humana: 3 documentos / 9 questoes; adjudicacao humana pendente. Ver [pacote GT Batch 01](../audit/holdout/V4_GROUND_TRUTH_BATCH_01_REVIEW_PACKAGE.md). Auditor V4: nao executado (`false`).
- Adjudicacao neutra usa apenas evidencia permitida pelo protocolo, sem answer keys, Ground Truth, Auditor output ou novas heuristicas para casos individuais.
- Proximo passo previsto: criar Ground Truth V4 em etapa posterior; ainda nao iniciado. Auditor ainda nao executado. Restricoes e checkpoint atualizado em [[AUDITORIA_PROVAS#Holdout V4 — checkpoint apos Tier B]].

Ver tambem: [[ARQUITETURA]], [[PROBLEMAS_CONHECIDOS]], [[ROADMAP]], [[AUDITORIA_PROVAS]].
