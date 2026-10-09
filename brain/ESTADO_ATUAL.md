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
- Ground Truth V4 por batches: Batches [01](../audit/holdout/ground-truth-v4-batch-01.json), [02](../audit/holdout/ground-truth-v4-batch-02.json), [03](../audit/holdout/ground-truth-v4-batch-03.json), [04](../audit/holdout/ground-truth-v4-batch-04.json), [05](../audit/holdout/ground-truth-v4-batch-05.json), [06](../audit/holdout/ground-truth-v4-batch-06.json), [07](../audit/holdout/ground-truth-v4-batch-07.json), [08](../audit/holdout/ground-truth-v4-batch-08.json), [09](../audit/holdout/ground-truth-v4-batch-09.json), [10](../audit/holdout/ground-truth-v4-batch-10.json), [11](../audit/holdout/ground-truth-v4-batch-11.json), [12](../audit/holdout/ground-truth-v4-batch-12.json), [13](../audit/holdout/ground-truth-v4-batch-13.json), [14](../audit/holdout/ground-truth-v4-batch-14.json), [15](../audit/holdout/ground-truth-v4-batch-15.json), [16](../audit/holdout/ground-truth-v4-batch-16.json) humanamente adjudicados/materializados, 48 documentos / 144 questoes; progresso 144/144, 16/16 batches concluidos e 0 pendentes. Question Selection V4 permanece congelada; GT V4 final consolidado, validado em UTF-8 e formalmente congelado no commit d9a37577c844213152a9db8c3cded1166c3a4cb9; Auditor V4 nao executado (`false`).
- Review packages GT V4 [Batch 02](../audit/holdout/V4_GROUND_TRUTH_BATCH_02_REVIEW_PACKAGE.md), [Batch 03](../audit/holdout/V4_GROUND_TRUTH_BATCH_03_REVIEW_PACKAGE.md) e [Batch 04](../audit/holdout/V4_GROUND_TRUTH_BATCH_04_REVIEW_PACKAGE.md) preservados como snapshots de preparacao; adjudicacoes humanas concluidas e materializadas separadamente, 9 documentos / 27 questoes. Batch 01 preservado.
- Review packages GT V4 [Batch 05](../audit/holdout/V4_GROUND_TRUTH_BATCH_05_REVIEW_PACKAGE.md), [Batch 06](../audit/holdout/V4_GROUND_TRUTH_BATCH_06_REVIEW_PACKAGE.md) e [Batch 07](../audit/holdout/V4_GROUND_TRUTH_BATCH_07_REVIEW_PACKAGE.md) preservados como snapshots de preparacao; adjudicacoes humanas concluidas e materializadas separadamente, 9 documentos / 27 questoes. Batches 01-04 preservados.
- Review packages GT V4 [Batch 08](../audit/holdout/V4_GROUND_TRUTH_BATCH_08_REVIEW_PACKAGE.md), [Batch 09](../audit/holdout/V4_GROUND_TRUTH_BATCH_09_REVIEW_PACKAGE.md) e [Batch 10](../audit/holdout/V4_GROUND_TRUTH_BATCH_10_REVIEW_PACKAGE.md) preservados como snapshots da preparacao pos-errata (source HEAD `5dbae24861fe4270ce5b7f69ec7d6d191ef6d2cc`); adjudicacoes humanas concluidas e materializadas separadamente nos GTs 08-10, 9 documentos / 27 questoes; q19.pages=[14,15] preservado. Progresso atual 144/144; Batches 01-07 e selecao congelada preservados; GT final validado e formalmente congelado; Auditor nao executado.
- Adjudicacao neutra usa apenas evidencia permitida pelo protocolo, sem answer keys, Ground Truth, Auditor output ou novas heuristicas para casos individuais.
- Reparo objetivo pos-freeze concluido: doc-6381aed53bb1:q19 passou de 14-14 para 14-15; 144 selected IDs preservados, sem reexecutar selecao; GT humano 01-07 intacto; errata incorporada ao GT Batch 08 com pages=[14,15]. Ver [errata](../audit/holdout/V4_OBJECTIVE_ERRATUM_Q19_PAGE_RANGE.md).
- Review packages GT V4 [Batch 11](../audit/holdout/V4_GROUND_TRUTH_BATCH_11_REVIEW_PACKAGE.md), [Batch 12](../audit/holdout/V4_GROUND_TRUTH_BATCH_12_REVIEW_PACKAGE.md) e [Batch 13](../audit/holdout/V4_GROUND_TRUTH_BATCH_13_REVIEW_PACKAGE.md) preservados como snapshots de preparacao de batches independentes; adjudicacoes humanas fornecidas materializadas separadamente nos GTs 11-13, 9 documentos / 27 questoes; PDFs integrais byte-identicos e contexts sem rotulos de GT. Batches 01-10 byte-preservados; progresso atual 144/144, selecao congelada; GTs 11-13 humanamente adjudicados/materializados; GT final=true/validado; Auditor=false.
- Review packages GT V4 [Batch 14](../audit/holdout/V4_GROUND_TRUTH_BATCH_14_REVIEW_PACKAGE.md), [Batch 15](../audit/holdout/V4_GROUND_TRUTH_BATCH_15_REVIEW_PACKAGE.md) e [Batch 16](../audit/holdout/V4_GROUND_TRUTH_BATCH_16_REVIEW_PACKAGE.md) preservados como snapshots de preparacao: ultimos 9 documentos / 27 questoes, posicoes 40-48; adjudicacoes humanas fornecidas materializadas separadamente nos GTs 14-16. Todos os 16 batches e 48 documentos selecionados possuem pacote de review; Batches 01-16 humanamente adjudicados/materializados, 0 questoes pendentes. Question Selection congelada; GTs 01-10 concluidos e byte-preservados, progresso 144/144; packages 11-13 preservados; PDF hybrid original preservado byte-identicamente; GT final criado/validado e formalmente congelado; Auditor nao executado.
- Compatibilidade objetiva do schema corrigida antes do freeze final: consolidacao temporariamente bloqueada pela rejeicao de `numeric_response`; validador agora aceita `numeric` legado e `numeric_response`, sem conversao nem mudanca da arquitetura V1. GT V4 Batches 01-16 completos, 144/144, decisoes humanas preservadas e 16/16 validacoes PASS; GT final consolidado losslessly em UTF-8 e provenance consistente; freeze GT V4 concluido; proximo passo=preflight cego e primeira execucao oficial unica, em etapa separada e explicitamente autorizada; Auditor nao executado.
- Ground Truth V4 final: [GT final](../audit/holdout/ground-truth-v4.json) e [provenance](../audit/holdout/ground-truth-v4.provenance.json) criados/validados em UTF-8, 16/16 batches consolidados, 48 documentos / 144/144 questoes, humanDecisionDifferences=0; numeric_response=1 preservado, provenance consistente com bytes reais. Freeze formal realizado no commit d9a37577c844213152a9db8c3cded1166c3a4cb9 (freezeVersion=1). Ver [freeze GT V4](../audit/holdout/V4_GROUND_TRUTH_FREEZE.md).
- Configuracao OCR de execucao V4 congelada pelo commit de introducao: [config](../audit/holdout/ocr-execution-config-v4.json), Tesseract / 160 DPI / PSM 6 / por+eng / full-document herdados do V3 oficial, sem reutilizar PSM 11 do indexador neutro. Drift pdftoppm 25.07.0 -> 26.07.0 registrado, sem tuning V4. Ver [freeze OCR](../audit/holdout/V4_OCR_EXECUTION_CONFIG_FREEZE.md).
- Preparacao dos caches OCR V4 congelada pelo commit de introducao do [manifest de preparacao](../audit/holdout/ocr-cache-preparation-v4.json): 16/16 caches full-document, 15 raster + 1 hybrid, 315/315 renders e 43/43 required pages acessiveis pelo contrato literal do runner. Normalizacao global de padding concluida por quatro renames, sem mudar bytes dos PNGs ou os 16 ocr.json e sem reexecutar OCR. Ver [freeze da preparacao](../audit/holdout/V4_OCR_CACHE_PREPARATION_FREEZE.md).
- Preflight cego anterior ao run: 48/48 PDF fingerprints, schemas/bindings, oito hashes funcionais e sete self-tests PASS; GT/config/preparacao dos caches frozen=true, cachesReady=16/16, renders=315/315 e required pages=43/43. Question Selection preservada.
- Primeira execucao oficial V4 concluida exatamente uma vez (Auditor=true, exitCode=0, rerun=false), source commit 394ce73f38848ec90f520a25b8d3ce71dd14099a, runStamp=20261005T221306Z; 144 records validados somente por identidade/ordem/fingerprint. [JSON](../audit/holdout/results/auditor-v1-holdout-v4-first-run.json) e [Markdown](../audit/holdout/results/auditor-v1-holdout-v4-first-run.md) copiados byte-identicamente do raw; [provenance](../audit/holdout/results/auditor-v1-holdout-v4-first-run.provenance.json) pronta para freeze formal pelo commit de introducao. Metricas nao exibidas/analisadas e failure analysis nao iniciada. Proximo passo, somente apos commit/push e em etapa separada: abrir e interpretar o resultado congelado. Estados Auditor=false nas notas de preparacao acima sao historicos. Checkpoint em [[AUDITORIA_PROVAS#Holdout V4 — checkpoint apos Tier B]].

Ver tambem: [[ARQUITETURA]], [[PROBLEMAS_CONHECIDOS]], [[ROADMAP]], [[AUDITORIA_PROVAS]].

## Checkpoint corrente — 2026-10-06

- Primeira execução oficial V4 formalmente frozen no commit `89f482b373449022423b4d34536160e62774cd2d`, publicado em `audit/holdout-v4`; runStamp=20261005T221306Z, execução única, sem rerun.
- Métricas abertas somente depois do freeze; conferidas no [resultado congelado](../audit/holdout/results/auditor-v1-holdout-v4-first-run.json), sem executar Auditor ou fazer postmortem nesta reorganização.
- V4: 144 executáveis; 60 correct; 1 partial; 66 safe_abstention; 5 unsafe_error; 12 not_applicable; 0 not_executable. Precision emitida=92,42%; coverage=52,08%.
- Próximo passo: postmortem dos 5 unsafe_error + 1 partial, sem patch inicial, e análise amostral estruturada das 66 abstenções. Objetivo: recuperar coverage sem perder precisão.
- Se houver patch funcional após analisar o V4, avaliar em V5 blind holdout; V4 e suas fontes permanecem congelados.
- Visão de produto consolidada em [[IDEIAS_E_PROXIMOS_PASSOS]], distinta da implementação atual. [[ROADMAP]] contém somente trabalho atual/futuro; o roadmap antigo foi movido integralmente para [[HISTORICO]].
- Notas anteriores do V4 foram preservadas como snapshots históricos; este checkpoint corrente prevalece para leitura do estado atual.

## Checkpoint corrente — postmortem V4 diagnóstico, 2026-10-06

- Postmortem concluído na branch separada `audit/holdout-v4-postmortem`: cinco unsafe_error + um partial analisados integralmente e 24/66 safe_abstention por amostra metadata-only congelada/publicada em `84ff03278aeae0f9a1b94eecd82fc674e753c8ff`, antes de abrir suas páginas.
- Replay diagnóstico de 30 casos reproduziu as classificações/campos comparados; 45 entradas de páginas completas revisadas, nenhuma revisão visual humana pendente. Resultado oficial preservado; officialAuditorExecutionCount=1, officialAuditorRerun=false; nenhum patch ou mudança funcional/cache/GT.
- Famílias: markers corrompidos ou falsos, response set selecionado versus candidatos brutos, papéis de slots e completude/fusion; coverage também limitado por identidade/gramática/scope de boundary e observação visual. Categorias na amostra: boundary=13, structure=5, visual=1, observação complementar=5; não extrapolar para as 66 nem tratar como ganho medido.
- Próximo passo: priorizar correções generalizáveis/TDD com controles positivos/negativos, começando por response set/completude. Qualquer patch pós-V4 exige V5 blind para avaliação imparcial; sem merge nesta etapa. Ver [análise](../audit/postmortem/V4_POSTMORTEM_ANALYSIS.md) e [findings](../audit/postmortem/v4-postmortem-findings.json).

## Checkpoint corrente — Patch 01 pós-V4, 2026-10-06

- `selected_response_set_contract` implementado na branch `audit/holdout-v4-postmortem-fixes`: Structure → Regions → Fusion preservam conjunto selecionado e provenance; seleção ambígua continua conservadora.
- TDD RED/GREEN, 14 suítes e regressão diagnóstica dos seis casos obrigatórios PASS. Completude não corrigida; resultado oficial e fontes/caches intactos, execução oficial única, sem rerun.
- V4 revelado não é benchmark pós-patch; V5 blind obrigatório antes de claims. Próximo passo separado: `response_set_completeness`. Detalhes/limitações no [Patch 01](../audit/postmortem/V4_PATCH_01_SELECTED_RESPONSE_SET.md); sem merge.

## Checkpoint corrente — Patch 02 pós-V4, 2026-10-06

- `response_set_completeness` implementado: incomplete/ambiguous/unknown aplicável bloqueia count/labels; não inventa alternativas nem faz stitching multipágina. Contrato Patch 01 preservado.
- TDD RED/GREEN, 14 suítes e replay diagnóstico dos seis PASS; os dois undercounts revelados agora abstêm, como regression behavior, sem claim de performance. Resultado oficial/fontes/caches intactos; execução oficial única, sem rerun; V5 blind obrigatório.
- Próximo passo separado: `neutral_boundary_identity_and_scope`, ainda não iniciado. Ver [Patch 02](../audit/postmortem/V4_PATCH_02_RESPONSE_SET_COMPLETENESS.md); sem merge.

## Checkpoint corrente — Patch 03A pós-V4, 2026-10-06

- Identity/grammar do boundary implementados: número impresso distinto do canônico e variantes ancoradas de keyword/separador, ordinal Item e decoração; provenance preservada. Índice congelado e contratos dos Patches 01/02 intactos.
- TDD RED/GREEN, 14 suítes e replay diagnóstico restrito a 19 IDs PASS; seis alvos reconhecidos, sem regressão unsafe. V4 apenas regression behavior, execução oficial única sem rerun; V5 blind obrigatório.
- Sem alteração de column scope ou reconstrução por words. Próximo separado: Patch 03B `neutral_boundary_scope_and_column_peers`; boundary inteiro não concluído. Ver [Patch 03A](../audit/postmortem/V4_PATCH_03A_BOUNDARY_IDENTITY_GRAMMAR.md); sem merge.

## Checkpoint corrente — Patch 03B pós-V4, 2026-10-06

- Column split agora exige peer corroborado pelo frozen index e match target-aware único; markers numéricos soltos não provam coluna. Duas colunas reais e next bottom preservados, sem alterar gramática 03A ou camadas de resposta.
- TDD RED/GREEN, 14 suítes e replay diagnóstico restrito a 19 IDs PASS; dois falsos peers neutralizados, sem regressões unsafe nos Patches 01/02/03A. Resultado/fontes/caches intactos, execução oficial única sem rerun; V5 blind obrigatório, sem claim de performance.
- Próximo separado: Patch 03C `neutral_boundary_word_line_reconstruction`, ainda não iniciado. Ver [Patch 03B](../audit/postmortem/V4_PATCH_03B_BOUNDARY_SCOPE_COLUMNS.md); boundary inteiro não concluído, sem merge.

## Checkpoint corrente — Patch 03C pós-V4, 2026-10-06

- Boundary line-first preserva matches únicos/ambíguos; somente ausência permite fallback target-aware por words observadas. Peers continuam index-backed; reconstrução local recebe somente words já filtradas por scope reliable, sem mudar texto/OCR/camadas de resposta.
- TDD, 14 suítes e replay restrito aos 19 IDs PASS sem unsafe. Quatro starts/reconstruções dos cinco alvos observáveis; q54 continua ausente por tokens CID, sem decoding. q5/q2 abstêm; q20 raster perde emissão conservadoramente após reconstrução. Sem claim de performance; resultado/fontes/caches preservados, execução oficial única, V5 blind obrigatório.
- Patches planejados 03A/03B/03C concluídos, não boundary perfeito. Próximo separado: `marker_role_and_spacing`. Ver [Patch 03C](../audit/postmortem/V4_PATCH_03C_BOUNDARY_WORD_RECONSTRUCTION.md); sem merge.

## Checkpoint corrente — Patch 04 pós-V4, 2026-10-07

- `marker_role_and_spacing` concluído: parenthesized whitespace suportado; selected response set autoritativo preserva answer-option role. Lowercase isoladamente não define subitem; enumerações internas, campos e controles permanecem separados.
- TDD, 14 suítes e replay diagnóstico de 24 IDs sem regressão unsafe; resultado/fontes/caches intactos, execução oficial única sem rerun/OCR novo. V4 não é avaliação imparcial; V5 blind obrigatório.
- Próximo separado: `visual_and_observation_recovery`, não iniciado. Ver [Patch 04](../audit/postmortem/V4_PATCH_04_MARKER_ROLE_SPACING.md); sem merge.

## Checkpoint corrente — Patch 05A pós-V4, 2026-10-07

- `visual_response_set_evidence` concluído: native PDFs fornecem render somente como fallback text-first, dentro do boundary. Count visual exige cluster único + região/gates; ordem visual nunca inventa labels.
- TDD/14 suítes e replay dos 30 IDs sem nova regressão unsafe; q5 nativo partial/5/unknown. Dois unsafe observacionais já presentes na base atual permanecem fora do escopo. Render-only, sem OCR novo; resultado/fontes/caches preservados, execução oficial única sem rerun, V5 blind obrigatório.
- Próximo separado: `observation_complementary_capability`, não iniciado. Ver [Patch 05A](../audit/postmortem/V4_PATCH_05A_VISUAL_RESPONSE_SET.md); sem merge.

## Checkpoint corrente — Patch05B1 safety, 2026-10-07

- Ampliação do regression sample aos 30 no 05A revelou duas regressões preexistentes introduzidas no 03C; [bisseção](../audit/postmortem/V4_PATCH_05B_SAFETY_BISECT.md) confirmou causas distintas e subpatches separados foram autorizados.
- 05B1 concluído: provenance reconstruída chega à Structure/completude; ausência não prova fechamento de prefixo reconstruído antes de E. TDD e cinco controles reais PASS; q11 agora abstém, A-E reconstruído/visual q5 preservados. Ver [05B1](../audit/postmortem/V4_PATCH_05B1_RECONSTRUCTED_CLOSURE.md).
- Próximo: 05B2 applicability, ainda não implementado; q17 não neutralizado nesta etapa. Observation complementary não iniciada; resultado oficial preservado, execução única sem rerun, V5 blind obrigatório.

## Checkpoint corrente — Patch05B2 applicability, 2026-10-07

- Selected answer set autoritativo com três ou mais labels A-E exige completude mesmo com mode unknown; C-D-E incompleto não emite count. Gate consumidor fecha contrato ausente/required=false obsoleto; CE/controles/parent_child/visual-only preservados. Ver [05B2](../audit/postmortem/V4_PATCH_05B2_COMPLETENESS_APPLICABILITY.md).
- TDD RED/GREEN, 14 suítes e cinco replays intermediários PASS; q17/q11 abstêm nos controles. Replay final dos 30 será feito após publicar os dois commits funcionais; ainda não concluir o safety check ampliado. V4 oficial intacto/sem rerun; V5 blind obrigatório, observation complementary não iniciada.

## Checkpoint corrente — safety 05B1/05B2 fechado, 2026-10-07

- Dois subpatches funcionais separados publicados; replay final dos 30 após ambos PASS: duas regressões unsafe reveladas neutralizadas, nenhuma nova unsafe nos outros 28. q5 visual, A-E reconstruído, cinco targets 04, q20 conservador e q54 preservados; um A-D reconstruído adicional abstém conservadoramente. Ver [fechamento 05B2](../audit/postmortem/V4_PATCH_05B2_COMPLETENESS_APPLICABILITY.md).
- Resultado/fontes/caches congelados preservados; Auditor oficial executado uma vez, sem rerun nem claim V4, V5 blind obrigatório. Próximo separado: `observation_complementary_capability`, não iniciado; sem merge.

## Checkpoint corrente — Patch05C1 fechado, 2026-10-07

- `scoped_complementary_marker_ocr` concluído como fallback conservador: boundary reliable, crop do raster cacheado, Tesseract por+eng/PSM6/2x, conjuntos explicitamente observados e compatíveis; mesma imagem não conta como fontes independentes. Completude/gates 05B preservados. Ver [05C1](../audit/postmortem/V4_PATCH_05C1_SCOPED_COMPLEMENTARY_MARKER_OCR.md).
- q17/q11 obtêm conjuntos explícitos completos; q13 permanece abstention por marker A não reconhecido. Gutter diagnóstico único recuperou B, não A, e NÃO entrou em produção. TDD/14 suítes/compile e replay dos mesmos 30 PASS sem nova unsafe; resultado/fontes/caches congelados intactos, execução oficial única sem rerun, nenhum claim V4; V5 blind obrigatório.
- Capacidade completa não significa todos os targets recuperados. Próximo separado: 05C2 `visual_header_and_layout_observation`, NÃO iniciado. Estratégia alternativa de marker-glyph somente futura se o padrão q13 recorrer; nenhuma tarefa/05C3 criada, sem merge.

## Checkpoint corrente — experimento 05C2 estacionado, 2026-10-07

- Baseline funcional permanece Patch05C1. 05C2 foi experimento diagnóstico não promovido: regiões de layout detectáveis, mas header OCR não sustentou target identity (A sem indexed headers, B somente q25; 0/2 boundaries confiáveis recuperados, não métrica de coverage). Ver [05C2](../audit/postmortem/V4_PATCH_05C2_VISUAL_HEADER_LAYOUT.md).
- Produção e testes exclusivos revertidos ao HEAD 05C1 publicado; diagnóstico e parada preservados, nenhuma busca de parâmetros/GT para layout-header ou claim unsafe pós-patch. Visual region proposal não integra o Auditor ativo; revisitar somente com evidência futura/blind, evitando overfitting ao V4 revelado.
- Próximo=Holdout V5 blind, com protocolo separado, NÃO iniciado nesta execução. Pódion permanece material interno de auditoria/treinamento, conforme nota futura em [[IMPORTADOR]]; sem publicação automática ou alteração do manifest V4. Sem merge.

## Checkpoint corrente — Holdout V5 Fase A, 2026-10-07

- Branch `audit/holdout-v5-blind` criada exatamente no candidate `3b306d6a544cc63928ec8adf07640b224651742e`; baseline05C1, 05C2 estacionado. Código funcional do Auditor congelado até o primeiro resultado V5 executado/congelado; nenhum patch nesta preparação.
- Somente seleção documental/freeze concluídos: 1.167 caminhos descobertos, 407 conteúdos elegíveis, 48 documentos determinísticos (32 native/15 raster/1 hybrid), 23 famílias/21 anos/quatro eras/sete categorias de série. Overlap por fingerprint com V1–V4 e calibração=0; sem trocas manuais. Ver [protocolo](../audit/holdout/PROTOCOL_V5.md) e [freeze](../audit/holdout/V5_DOCUMENT_SELECTION_FREEZE.md).
- Seleção anterior a inspeção; questionInspection/selection/GT/Auditor/metrics V5=false. Nenhum índice de questões V5; artefatos V1–V4/postmortem/caches preservados, sem merge. Único hybrid não exposto consumido por V5; futura Final Blind Evaluation precisará de novo acervo nessa categoria, sem reciclar documentos.
- Próximo separado: V5 Phase B neutral question index + question selection freeze. V5 completo NÃO concluído; nenhuma questão selecionada nesta fase. Pódion continua interno conforme [[IMPORTADOR]], sem promoção ao catálogo.
- Limitação futura registrada, sem correção: validador legado suporta V1–V4, não V5. Manifest atual é documental; compatibilidade/bindings de execução exigirão gate explícito, sem alterar Auditor funcional congelado nem contornar protocolVersion silenciosamente.

## Checkpoint corrente — Holdout V5 Phase B1, 2026-10-07

- Raw neutral question index congelado após execução única dos 48 documentos: 1063 questões brutas, um documento com zero questões preservado; integridade automática PASS. Protocolo/config do mesmo indexador V4 congelados antes da execução, sem tuning ou revisão humana de PDFs/anomalias. Ver [raw freeze](../audit/holdout/V5_QUESTION_INDEX_RAW_FREEZE.md).
- V1–V4/postmortem/caches antigos, Phase A e código funcional05C1/schema preservados; 05C2 permanece estacionado. Somente cache neutro novo do índice, não cache do Auditor; OCR do índice não define OCR futuro do Auditor.
- Somente B1 concluída; próximo separado=V5 Phase B2 neutral question-index adjudication/final freeze. Final index/selection/GT/Auditor/metrics=false; nenhuma adjudicação nesta execução, sem merge. Limitação do validator legado V1–V4 permanece para gate futuro.

## Checkpoint corrente — Holdout V5 Phase B2a, 2026-10-07

- Fila de triagem neutra congelada dos 48 documentos, política V4 sem retuning: A=22/B=4/C=14/D=8. Derivação somente de raw/report/manifest congelados; nenhuma inspeção PDF/visual ou adjudicação/correção. Todos os 48 permanecem obrigados à revisão neutra futura, inclusive controles D. Ver [triagem B2a](../audit/holdout/V5_QUESTION_INDEX_TRIAGE.md).
- Phase A/B1/raw/caches e código funcional05C1 preservados; 05C2 estacionado. Somente B2a concluída, não índice final/Phase B inteira; próximo separado=B2b neutral review/adjudication. Final index/selection/GT/Auditor/metrics=false; sem merge.

## Checkpoint corrente — V5 Tier A Batch01 pausado, 2026-10-08

- Revisão neutra local pausada no documento 8 com source incompleto: 14/14 páginas disponíveis revisadas, 26 inícios observados, q18–q21 indisponíveis; documentos 9–11 não retomados. Batch01/Tier A/Phase B NÃO concluídos.
- [Adendo metodológico pós-freeze, performance-blind](../audit/holdout/V5_OBJECTIVE_SOURCE_INCOMPLETENESS_RULE.md): sem substituto elegível no mesmo estrato, manter o documento e registrar source gap separado, sem fabricar questões/boundaries. Resolução será aplicada somente na retomada autorizada; notas históricas/unresolved preservadas.
- Original protocol/Phase A/raw/queue/package e código funcional05C1 intactos; nenhum final index, question selection, GT, Auditor ou métricas V5. Próximo separado=retomar Tier A Batch01 neutral adjudication após freeze do adendo; Batch02 intocado, sem merge.

## Checkpoint corrente — V5 Tier A Batch01 adjudicado, 2026-10-08

- Retomada após adendo congelado: 11/11 documentos e 182/182 páginas disponíveis, 1136 questões canônicas (raw345/delta+791), unresolved=0. [Relatório e validação](../audit/holdout/V5_TIER_A_BATCH_01_ADJUDICATION.md). Documentos 1–7 preservados sem nova adjudicação visual; 9–11 revisados em ordem, notas incrementais salvas por documento.
- Doc8 resolvido como adjudicated_source_incomplete: 26 objetos observados, sourceMissing=[18,19,20,21], nenhum objeto/boundary fabricado; unresolved histórico preservado. Seis grupos paralelos, zero reinícios/normalizações/humanExclusions; duas questões multipágina no doc10. Sem response semantics, gabaritos, GT ou Auditor consultados.
- Somente Batch01 concluído; Tier A inteiro/Phase B NÃO concluídos. Próximo separado=Tier A Batch02 review package freeze, não preparado/aberto nesta execução. Protocolo original/adendo/Phase A/B1/B2a/raw/queue/package/Auditor/indexer/V1–V4/baseline05C1 intactos; final index/selection/GT/Auditor/metrics=false, sem merge.

## Checkpoint corrente — V5 Batch02, integridade inconclusiva do documento 3, 2026-10-08

- [Decisão externa pós-freeze e performance-blind](../audit/holdout/V5_SOURCE_INTEGRITY_INCONCLUSIVE_DOC03.md): manter `v5-doc-815b83630e3d8c98` e fingerprint congelados; integridade original inconclusiva, sem certificação de completude, substituição não autorizada e exceção anterior de source incompleteness não aplicada.
- Escopo futuro=`frozen_available_pdf_content`. As 21 identidades do doc3 continuam candidatas; comprovar identidade/boundaries, especialmente quanto à página física 7. Ambiguidade impede elegibilidade/adjudicação integral e exige nova decisão externa. Ressalva e timing pós-freeze devem acompanhar a documentação metodológica final V5.
- Checkpoint/diagnóstico preservados; documentos 1/2 adjudicados (40/21), doc3 unresolved, documentos 4–11 não iniciados. Batch02/Tier A/Phase B incompletos; próxima execução separada=retomar revisão neutra Batch02 a partir da comprovação de boundaries do doc3, antes de 4–11. Nenhuma nova inspeção/OCR/adjudicação aqui; final index/selection/GT/Auditor/metrics/merge=false.

## Checkpoint corrente — V5 errata objetiva de paginação, 2026-10-08

- [Errata aditiva doc10](../audit/holdout/V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10.md): censo estrutural dos48 PDFs com dois leitores confirma fingerprints48/48, concordância48/48 e única divergência `v5-doc-74e153f9c146d887`, pageCount congelado1/efetivo21. Fontes e metadados congelados intactos; seleção invariante por inspeção estática, sem reexecução. Errata pós-freeze/performance-blind deve ser aplicada explicitamente por hash em derivados futuros, mantendo limites de página validados.
- Checkpoint retomado preservado: docs1–9 adjudicados/115páginas/194questões, doc3 com integridade original inconclusiva e escopo PDF disponível, doc8 source incompleto documentado. Doc10 parado antes de adjudicação; doc11 visualmente não iniciado. Batch02 histórico120páginas/efetivo140; restam25 (21+4). Nenhuma revisão visual/OCR/extração de conteúdo nova nesta errata.
- Batch02/TierA/PhaseB incompletos; próxima execução separada=retomar revisão neutra Batch02 sob errata a partir do doc10, preservando1–9, depois11. Nenhuma mudança funcional05C1/validator, seleção/GT/Auditor/métricas/finalIndex/merge=false. Estados anteriores são checkpoints históricos; o checkpoint local retomado prevalece para progresso.

## Checkpoint corrente — V5 insuficiência de questões do Batch02 doc11, 2026-10-08

- Checkpoint local pós-errata preservado: documentos1–10 adjudicados,214 questões canônicas nesses dez,140/140 páginas efetivas do Batch02 original revisadas; doc11 `v5-doc-a08230ae0b1cad7e` permanece unresolved. Quatro páginas revisadas, menos de três identidades independentes adjudicáveis comprovadas; esta decisão não certifica contagem canônica zero/um nem corrupção do PDF.
- [Regra geral pós-freeze, performance-blind](../audit/holdout/V5_INSUFFICIENT_QUESTIONS_REPLACEMENT_RULE.md) e [decisão estruturada](../audit/holdout/v5-insufficient-questions-decision-doc11.json): oito critérios cumulativos, não pré-registrada antes da inspeção, aplicável genericamente inclusive a futuros Tiers B/C/D; exceção deve acompanhar a metodologia final. Próximo candidato do mesmo estrato/ranking original=`v5-doc-e1c73fb849ef80a6`, identificado somente por metadados; PDF/conteúdo não consultados, mínimo de questões não presumido.
- Nenhuma substituição física/lógica ou manifest efetivo criado; manifest histórico, três checkpoints e todos os freezes anteriores preservados. Batch02/TierA/PhaseB incompletos; finalIndex/selection/GT/Auditor/metrics/merge=false. Próxima prioridade separadamente autorizada=`V5 objective replacement materialization and supplemental review package`, com provenance própria e freeze suplementar antes da adjudicação visual; STOP após este commit/push.

## Checkpoint corrente — V5 substituição doc11 e package suplementar, 2026-10-08

- [Substituição objetiva r1](../audit/holdout/V5_OBJECTIVE_REPLACEMENT_DOC11.md) materializada sob adendo pós-freeze/performance-blind: original `v5-doc-a08230ae0b1cad7e` preservado no histórico; efetivo `v5-doc-e1c73fb849ef80a6` no mesmo estrato/ranking2/posição47+Batch02/11+TierA/22,48documentos/uma substituição/47linhas intactas/quotas e overlap0 preservados. Exceção não pré-registrada; população efetiva difere da original e possui provenance própria.
- Candidato fingerprint correto/12páginas confirmadas por pypdf+pdfinfo/sizeBytes182017; pdfinfoReportedFileSize0 preservado como divergência técnica explicitamente não bloqueante, causa não determinada, sem inferir corrupção. Indexador congelado executado uma vez somente no candidato: native/raw18/anomalias2 sem correção, processamento automático neutro registrado; nenhuma revisão visual ou contagem canônica/mínimo3 certificados.
- [Package suplementar](../audit/holdout/V5_TIER_A_BATCH_02_SUPPLEMENTAL_REVIEW_PACKAGE.md) validado, freeze formal pelo commit de introdução/publicação desta etapa antes da revisão visual. Docs1–10/214questões e três checkpoints preservados;140páginas revisadas no conjunto original,136retidas no efetivo+12pendentes=148sob errata doc10. Batch02/TierA/PhaseB incompletos; próximo separado=`V5 Tier A Batch02 supplemental neutral visual adjudication`; finalIndex/selection/GT/Auditor/metrics/merge=false, sem TierB.

## Checkpoint corrente - V5 Tier A completo, 2026-10-09

- [Batch02 efetivo adjudicado](../audit/holdout/V5_TIER_A_BATCH_02_ADJUDICATION.md):11documentos/148páginas/234questões canônicas, rawhistórico109/rawefetivo127/delta+107/unresolved0. Docs1–10/214questões e decisões importados exatamente do checkpoint congelado, sem nova inspeção.
- [Suplemento doc11](../audit/holdout/V5_TIER_A_BATCH_02_SUPPLEMENTAL_ADJUDICATION.md):12/12páginas/20questões/raw18/delta+2; q4 e q8 observadas, só q12 multipágina7–8; mínimo3 e boundaries PASS. Package publicado antes da revisão; substituição pós-freeze no manifest efetivoR1 explícita, original unresolved preservado no histórico.
- Batch01 conferido11/182/1136/unresolved0; TierAComplete=true/TierADocumentsAdjudicated=22, PhaseBComplete=false. Doc3 integridade original inconclusiva/doc8 source incompleto/doc10 frozen1/efetivo21 permanecem documentados e devem acompanhar os derivados futuros.
- Fontes/checkpoints/caches/freezes/código05C1/indexador/configGit preservados; sem OCR/rerun. Final index/selection/GT/Auditor/metrics/merge=false. Próximo SEPARADO=V5 Tier B neutral review package freeze; não preparado aqui, STOP após commit/push.

## Checkpoint corrente — V5 package Tier B, 2026-10-09

- [Package neutro Tier B](../audit/holdout/V5_TIER_B_REVIEW_PACKAGE.md) preparado e validado:4documentos/92páginas/156raw/156eventos automáticos (não defeitos confirmados), ordem global23–26 imutável, native4/ocr0, fingerprints/cópias byte-idênticas4/4. Contexto/lista ignorados vinculados por SHA256; freeze formal pelo commit de introdução/publicação.
- TierAComplete=true/22documentos/330páginas efetivas/1370canônicas preservados, incluindo manifest efetivoR1 e decisões/erratas/checkpoints pós-freeze. TierBAdjudicated=false/PhaseBComplete=false; sem inspeção PDF/render/OCR/extração nova/indexador/interpretação raw nesta preparação; finalIndex/selection/GT/Auditor/metrics/merge=false.
- Próximo SEPARADO=V5 Tier B neutral visual adjudication após publicação; STOP após push, sem TierC/D.

## Checkpoint corrente — V5 Tier B adjudicado, 2026-10-09

- [Adjudicação neutra Tier B](../audit/holdout/V5_TIER_B_ADJUDICATION.md): quatro documentos em ordem23–26,92/92 páginas,220 canônicas/raw156/delta+64, unresolved0; B01/B02/B03/B04=120/20/40/40. Revisão assistida pelo agente após publicação do package, sem alegação humana independente. Quatro multipágina somente no B04;156 diagnósticos raw resolvidos estruturalmente, não métricas.
- TierAComplete=true/22 documentos/330 páginas/1370 canônicas preservados sem reabrir seus PDFs; TierBAdjudicated=true/PhaseBComplete=false. Decisões/erratas/checkpoints/manifestR1 e ressalvas metodológicas anteriores continuam obrigatórios para futuros derivados.
- Final index/selection/GT/Auditor/metrics/merge=false; sem novo OCR/extração/indexador/censo ou mudança funcional. Próximo SEPARADO=V5 Tier C neutral review package freeze, não iniciado; STOP após commit/push, sem TierC/D.

## Checkpoint Holdout V5 — Tier C package neutro (2026-10-09)

- [Package Tier C](../audit/holdout/V5_TIER_C_REVIEW_PACKAGE.md) preparado e validado:14documentos/185páginas/279raw/73eventos automáticos, global27–40 literal, native9/ocr5; duas unidades operacionais7+7 antes de visual, sem nova seleção/redistribuição.
- Batch01=7documentos/89páginas/103raw/60eventos; Batch02=7/96/176/13. Fontes/cópias14/14 byte-idênticas, raw/contexto/listas íntegros, sem parser/censo/render/OCR/indexador ou interpretação/adjudicação nesta etapa.
- Tiers publicados A22/330/1370 eB4/92/220/unresolved0 intactos, sem reabrir PDFs; ressalvas/source incompleto/integridade inconclusiva/errata/substituição pós-freeze e manifestR1 transportados.
- TierAComplete=true/TierBAdjudicated=true/TierCPrepared=true/TierCAdjudicated=false/PhaseBComplete=false; finalIndex/selection/GT/Auditor/metrics/merge=false. Próximo SEPARADO=V5 Tier C Batch01 neutral visual adjudication, não iniciado; publicação pelo commit/push e STOP, sem Batch01/02 ou TierD.

## Checkpoint corrente — V5 Tier C Batch01 adjudicado, 2026-10-09

- [Batch01 neutro](../audit/holdout/V5_TIER_C_BATCH_01_ADJUDICATION.md):7documentos global27–33/89páginas/174canônicas (40/30/20/20/20/24/20), raw103/delta+71/9multipágina/17correções de ranges/unresolved0. Revisão assistida pelo agente, sem alegação humana independente.
- Retomada exatamente doc3p5; docs1–2/31páginas/70questões e evidência doc3p1–4 importados do checkpoint original byte-intacto. Checkpoint retomado separado, salvamento atômico; nenhuma reinspeção dos documentos concluídos.
- TierAComplete=true/22documentos/330páginas/1370canônicas eTierBAdjudicated=true/4/92/220 intactos; provenance pós-freeze/manifestR1/ressalvas preservados. TierCBatch01Adjudicated=true/TierCBatch02Adjudicated=false/TierCAdjudicated=false/PhaseBComplete=false.
- FinalIndex/selection/GT/Auditor/metrics/merge=false; código funcional05C1/fontes/freezes/configGit intactos, sem novo OCR/extração/indexador/censo. Próximo SEPARADO=V5 Tier C Batch02 neutral visual adjudication, não iniciado; STOP após publicação, sem TierD.

## Checkpoint corrente — V5 Tier C completo, 2026-10-09

- [Batch02 neutro](../audit/holdout/V5_TIER_C_BATCH_02_ADJUDICATION.md):7documentos global34–40/96páginas/190canônicas (30/20/20/20/20/40/40), raw176/delta+14/2multipágina/46ranges corrigidos/14identidades observadas adicionadas/13eventos estruturais/zero unresolved/mínimo3por documento PASS.
- Finalização importa os sete objetos exatamente do checkpoint definitivo SHA56f83a70727464d32f20be40e681194cd98ef20c8c90af62c783da78ec00de34, preservado; revisão assistida já concluída em duas execuções,64+32páginas/110+80questões, sem nova inspeção PDF/render ou alegação humana independente. SHA incremental anterior é histórico, não comparado aos bytes atuais.
- Tier C completo:Batch01 byte-idêntico7/89/174 eBatch02 7/96/190; total14documentos/185páginas/364canônicas/279raw/73eventos/11multipágina/unresolved0, ordem27–40 sem sobreposição/omissão. TierCBatch01Adjudicated=true/TierCBatch02Adjudicated=true/TierCAdjudicated=true/PhaseBComplete=false.
- Tiers A22/330/1370 eB4/92/220, provenance pós-freeze/manifestR1/ressalvas/source incompleto/integridade inconclusiva/errata/substituição e fontes/código05C1/configGit intactos. FinalIndex/selection/GT/Auditor/metrics/merge=false; sem novo OCR/extração/indexador/censo.
- Próximo SEPARADO=V5 Tier D neutral review package freeze, não iniciado/TierDPrepared=false. STOP após publicação; nenhum índice global48documentos ou seleção144questões nesta etapa.
