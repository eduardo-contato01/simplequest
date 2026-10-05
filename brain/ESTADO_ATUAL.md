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

## Auditor / Holdout V4 — checkpoint 2026-10-05

- Branch: `audit/holdout-v4`. Arquitetura V1 do Auditor **congelada para avaliacao**.
- Camadas atuais: (1) admission/preflight; (2) marker/profile/page scope; (3) OCR content; (4) response structure; (5) visual marker evidence; (6) response regions/slots; (7) response evidence fusion; (8) observation adapter OCR/native.
- Tudo continua shadow/read-only onde aplicavel; a V1 de OCR ainda **nao** produz `difference`.
- Nenhuma hipotese de estrutura e promovida ao catalogo.
- Candidate pool V4 congelado; selecao documental concluida com 48 documentos; raw neutral question index congelado.
- Tier A: 18/18 adjudicados. Tier B: 9/9 adjudicados e commitados, com 246 questoes canonicas.
- Tier C: 13/13 adjudicados, com 430 questoes canonicas. Tier D: 8/8 adjudicados, com 180 questoes canonicas (182 raw; duas QUESTAO 21 de Producao Textual excluidas por decisao humana). Todos os tiers de adjudicacao neutra estao concluidos.
- Tier C review package preservado e congelado; adjudicacao concluida (`true`) a partir da revisao visual humana fornecida. Ver [adjudicacao Tier C](../audit/holdout/V4_TIER_C_ADJUDICATION.md).
- Tier D review package/contexto preservados como snapshots de preparacao; adjudicacao humana concluida (`true`). Ver [adjudicacao Tier D](../audit/holdout/V4_TIER_D_ADJUDICATION.md).
- Final Question Index V4 criado e congelado (`true`): 48/48 documentos adjudicados, 1.732 questoes canonicas (A=876, B=246, C=430, D=180). Ver [indice final V4](../audit/holdout/V4_FINAL_QUESTION_INDEX.md). Question Selection V4 concluida (`true`): 144 questoes, 3 por documento, seed 20261001; serializacao UTF-8 reparada sem nova selecao, com os mesmos 144 IDs. Phase A preservada; indice final reparado objetivamente conforme errata abaixo. Ver [freeze da selecao](../audit/holdout/V4_QUESTION_SELECTION_FREEZE.md).
- Ground Truth V4 por batches: Batches [01](../audit/holdout/ground-truth-v4-batch-01.json), [02](../audit/holdout/ground-truth-v4-batch-02.json), [03](../audit/holdout/ground-truth-v4-batch-03.json), [04](../audit/holdout/ground-truth-v4-batch-04.json), [05](../audit/holdout/ground-truth-v4-batch-05.json), [06](../audit/holdout/ground-truth-v4-batch-06.json), [07](../audit/holdout/ground-truth-v4-batch-07.json), [08](../audit/holdout/ground-truth-v4-batch-08.json), [09](../audit/holdout/ground-truth-v4-batch-09.json), [10](../audit/holdout/ground-truth-v4-batch-10.json), [11](../audit/holdout/ground-truth-v4-batch-11.json), [12](../audit/holdout/ground-truth-v4-batch-12.json), [13](../audit/holdout/ground-truth-v4-batch-13.json), [14](../audit/holdout/ground-truth-v4-batch-14.json), [15](../audit/holdout/ground-truth-v4-batch-15.json), [16](../audit/holdout/ground-truth-v4-batch-16.json) humanamente adjudicados/materializados, 48 documentos / 144 questoes; progresso 144/144, 16/16 batches concluidos e 0 pendentes. Question Selection V4 permanece congelada; GT V4 final ainda nao criado nem congelado (`false`); Auditor V4 nao executado (`false`).
- Review packages GT V4 [Batch 02](../audit/holdout/V4_GROUND_TRUTH_BATCH_02_REVIEW_PACKAGE.md), [Batch 03](../audit/holdout/V4_GROUND_TRUTH_BATCH_03_REVIEW_PACKAGE.md) e [Batch 04](../audit/holdout/V4_GROUND_TRUTH_BATCH_04_REVIEW_PACKAGE.md) preservados como snapshots de preparacao; adjudicacoes humanas concluidas e materializadas separadamente, 9 documentos / 27 questoes. Batch 01 preservado.
- Review packages GT V4 [Batch 05](../audit/holdout/V4_GROUND_TRUTH_BATCH_05_REVIEW_PACKAGE.md), [Batch 06](../audit/holdout/V4_GROUND_TRUTH_BATCH_06_REVIEW_PACKAGE.md) e [Batch 07](../audit/holdout/V4_GROUND_TRUTH_BATCH_07_REVIEW_PACKAGE.md) preservados como snapshots de preparacao; adjudicacoes humanas concluidas e materializadas separadamente, 9 documentos / 27 questoes. Batches 01-04 preservados.
- Review packages GT V4 [Batch 08](../audit/holdout/V4_GROUND_TRUTH_BATCH_08_REVIEW_PACKAGE.md), [Batch 09](../audit/holdout/V4_GROUND_TRUTH_BATCH_09_REVIEW_PACKAGE.md) e [Batch 10](../audit/holdout/V4_GROUND_TRUTH_BATCH_10_REVIEW_PACKAGE.md) preservados como snapshots da preparacao pos-errata (source HEAD `5dbae24861fe4270ce5b7f69ec7d6d191ef6d2cc`); adjudicacoes humanas concluidas e materializadas separadamente nos GTs 08-10, 9 documentos / 27 questoes; q19.pages=[14,15] preservado. Progresso atual 144/144; Batches 01-07 e selecao congelada preservados; GT final nao congelado e Auditor nao executado.
- Adjudicacao neutra usa apenas evidencia permitida pelo protocolo, sem answer keys, Ground Truth, Auditor output ou novas heuristicas para casos individuais.
- Reparo objetivo pos-freeze concluido: doc-6381aed53bb1:q19 passou de 14-14 para 14-15; 144 selected IDs preservados, sem reexecutar selecao; GT humano 01-07 intacto; errata incorporada ao GT Batch 08 com pages=[14,15]. Ver [errata](../audit/holdout/V4_OBJECTIVE_ERRATUM_Q19_PAGE_RANGE.md).
- Review packages GT V4 [Batch 11](../audit/holdout/V4_GROUND_TRUTH_BATCH_11_REVIEW_PACKAGE.md), [Batch 12](../audit/holdout/V4_GROUND_TRUTH_BATCH_12_REVIEW_PACKAGE.md) e [Batch 13](../audit/holdout/V4_GROUND_TRUTH_BATCH_13_REVIEW_PACKAGE.md) preservados como snapshots de preparacao de batches independentes; adjudicacoes humanas fornecidas materializadas separadamente nos GTs 11-13, 9 documentos / 27 questoes; PDFs integrais byte-identicos e contexts sem rotulos de GT. Batches 01-10 byte-preservados; progresso atual 144/144, selecao congelada; GTs 11-13 humanamente adjudicados/materializados; GT final=false; Auditor=false.
- Review packages GT V4 [Batch 14](../audit/holdout/V4_GROUND_TRUTH_BATCH_14_REVIEW_PACKAGE.md), [Batch 15](../audit/holdout/V4_GROUND_TRUTH_BATCH_15_REVIEW_PACKAGE.md) e [Batch 16](../audit/holdout/V4_GROUND_TRUTH_BATCH_16_REVIEW_PACKAGE.md) preservados como snapshots de preparacao: ultimos 9 documentos / 27 questoes, posicoes 40-48; adjudicacoes humanas fornecidas materializadas separadamente nos GTs 14-16. Todos os 16 batches e 48 documentos selecionados possuem pacote de review; Batches 01-16 humanamente adjudicados/materializados, 0 questoes pendentes. Question Selection congelada; GTs 01-10 concluidos e byte-preservados, progresso 144/144; packages 11-13 preservados; PDF hybrid original preservado byte-identicamente; GT final nao criado/congelado; Auditor nao executado.
- Proximo passo previsto: consolidacao/freeze do GT V4 final em etapa posterior; GTs 01-16 completos, 144/144, 16/16 batches e 0 pendentes. Nenhum GT final criado e nenhum Auditor executado nesta materializacao. Restricoes e checkpoint atualizado em [[AUDITORIA_PROVAS#Holdout V4 — checkpoint apos Tier B]].

Ver tambem: [[ARQUITETURA]], [[PROBLEMAS_CONHECIDOS]], [[ROADMAP]], [[AUDITORIA_PROVAS]].
