# SimpleQuest 2.0 — entrega do Incremento 1B

Implementação em 11/09/2026, limitada à extração dos blocos compartilháveis. Referências utilizadas: [análise técnica](simplequest-2.0-analise-tecnica.md), [baseline 1A](simplequest-2.0-baseline-1a.md), [fixture](../tests/fixtures/baseline-cases.json) e os artefatos congelados em `docs/baseline-1a/`.

## Divisão de responsabilidades

`app/page.tsx` passou de **376 para 59 linhas** (contagem sem linha vazia final): redução de 317 linhas, aproximadamente **84%**. Mantém cabeçalho, apresentação, nota de migração e a composição das áreas. Não se criou um shell novo.

| Unidade | Responsabilidade |
| --- | --- |
| `QuestionsWorkspace` | Compor filtros, resultados, cartões e paginação; receber o compositor de simulado como filho. Mostrar os estados de carregamento/falha. |
| `QuestionFilters` | Controles de busca e filtros, com valores/opções e callbacks recebidos. |
| `QuestionCard` | Metadados, selo editorial, seleção, expansão, conteúdo e ações do cartão. Não carrega dados e não possui uma cópia local da resposta. |
| `QuestionAlternatives` | Alternativas textuais/estruturadas, resposta selecionada, feedback, interação por clique/Enter/Espaço. Recebe questão, resposta e callback; usa o modelo para obter o gabarito normalizado. |
| `QuestionsPagination` | Controles e limites de paginação, sem filtrar ou ordenar dados. |
| `SimulationComposer` | Título, composição do painel, limpar seleção e chamada original a `window.print()`. |
| `SimulationSelectionSummary` | Lista, remoção, estado vazio e resumo; mantém oito itens visíveis e contador de excedentes. |
| `SimulationPrintSheet` | Markup de impressão original, todos os selecionados na ordem recebida e gabarito separado. |
| `useQuestionCatalog` | Carregamento local, estado do resultado, nova tentativa e descarte de respostas de efeitos já encerrados. Não é cache nem provider global. |
| `useQuestionsWorkspace` | Única fonte local de filtros, ordenação, página, expansão, respostas, revelação, seleção e título. Mantém os algoritmos anteriores de busca/ordenação e a persistência/rolagem existentes. |

As regras de busca e seleção não foram colocadas nos componentes visuais. A seleção continua sendo obtida filtrando o catálogo pelos IDs do `Set`, portanto não adota a ordem de clique nem a ordenação da busca. `questionAnswerFeedback`, no modelo, conserva o tratamento anterior do gabarito (`trim().toUpperCase()`) e sua comparação com a resposta.

`QuestionBlocks`, `QuestionMedia`, `MathFormula` e `search-utils.ts` foram reutilizados sem alterações. Não há alteração em CSS, API, banco, migrações, dependências ou lockfile.

## Carregamento e diferenças intencionais

`loadQuestionCatalogWithStatus` reutiliza a leitura do JSON base, revisões, sobreposição por ID e normalização. Retorna catálogo disponível ou base utilizável com revisões indisponíveis. `loadQuestionCatalog` continua oferecendo o retorno `Question[]` consumido pela curadoria; o contrato HTTP de `/api/questions/revisions` não mudou.

O hook distingue quatro estados:

- `loading`: mantém a indicação “Carregando acervo…”.
- `available`: catálogo carregado com revisões disponíveis, inclusive uma lista vazia de revisões.
- `base-error`: falha HTTP/rede/JSON ou base que não é uma lista; mostra erro e botão “Tentar novamente”.
- `revisions-unavailable`: preserva o fallback normalizado da base, mostra uma mensagem discreta e permite tentar novamente.

Essa distinção é a **diferença funcional intencional solicitada no 1B**. Antes, a falha da base podia resultar em rejeição não tratada e mensagem de busca vazia; o fallback das revisões era silencioso. Os novos estados reutilizam classes existentes. A validação HTTP/formato da base também se aplica ao wrapper que retorna `Question[]`, mantendo a propagação do erro; nenhum fluxo normal da curadoria foi alterado.

O estado continua local a uma instância da página. A chave `simplequest:questions-view:v1`, seus campos e o formato serializado do `Set` foram mantidos. A restauração da rolagem continua aguardando o carregamento e dois frames; agora seu efeito tem cancelamento na desmontagem. `/revisao` conserva seu carregamento e sua própria chave. Não há sincronização nova entre rotas, evento de atualização ou sessão de simulado no banco.

## Paridade e testes

Os sete casos funcionais do 1A foram verificados: texto, fórmula inline, fórmula em bloco, tabela, imagens no enunciado, imagens nas alternativas e questão bloqueada. O simulado misto mantém a ordem CMB 2003 Q1/Q2/Q4/Q11, CMB 2008 Q13 e CMB 2014 Q15; gabarito **E, A, E, C, D, B**.

A captura foi executada com os componentes reais e o CSS compilado, em contexto isolado do Edge 152.0.4191.66. Todas as requisições foram interceptadas e servidas localmente; não houve acesso ao D1, escrita em registros ou alteração do armazenamento do navegador do usuário.

Resultados da comparação:

- Seis artigos, 30 alternativas, oito imagens e uma tabela.
- PNG atual idêntico ao PNG obtido renderizando o HTML congelado do 1A no mesmo navegador.
- HTML autossuficiente atual com **o mesmo SHA-256 do baseline**: `c2005487d67ca8b82640431399571a8a4ad6e03ff5d62e66d6d10b6cc70e8ca9`.
- Preservados os detalhes anteriores: `aria-hidden` da folha, marcadores de alternativas ocultos pelo CSS e quebra de página antes do gabarito. Não houve redesign ou correção visual oportunista.
- Os artefatos de `docs/baseline-1a/` não foram substituídos. A saída de comparação está em `outputs/baseline-1b/`, ignorada pelo Git; o [relatório de verificação](simplequest-2.0-verificacao-1b.json) registra as evidências.

O teste interativo adicional verificou clique/teclado, acerto/erro, desmarcar resposta, mostrar gabarito, expansão única, ampliação e fechamento de imagens, ausência de seleção acidental ao abrir imagem de alternativa, busca, filtros, ordenação, paginação, título, remoção/limpeza/seleção, `window.print()`, restauração dos campos e rolagem após reload, estados do catálogo e recuperação das falhas.

Os testes antigos foram alterados somente onde a extração invalidou a localização original. As verificações do markup da página passaram a testes do **HTML realmente renderizado** dos componentes, incluindo modos ABCDE/ABCD/CE, feedback, conteúdo rico e resumo com mais de oito selecionados. As verificações textuais de persistência e uso da busca foram apontadas para o hook local, enquanto o comportamento correspondente também foi verificado no navegador. As demais verificações anteriores, incluindo os testes de busca e os contratos do 1A, permanecem.

## Comandos e resultados finais

Ambiente e versões de dependências mantidos em relação ao 1A. Perfil Sites `portable`, sem reconfigurar o projeto.

| Comando | Resultado |
| --- | --- |
| `npm run typecheck` | Aprovado, zero diagnósticos, exit 0. |
| `npm run test:contracts` | Aprovado, **29 testes**, zero falhas/ignorados, exit 0. |
| `npm test` | Aprovado, build e 29 testes, exit 0. |
| `npm run build` | Aprovado, cinco fases Vinext/Vite, exit 0. |
| `node scripts/capture-print-baseline.mjs --compare-baseline --verify-workspace` | Aprovado, comparação de impressão e interações; zero erros de página. |
| `git diff --check` | Aprovado. |

Para repetir a comparação neste ambiente:

```powershell
npm run build
$env:SIMPLEQUEST_PLAYWRIGHT_MODULE='C:/Users/trans/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'
$env:SIMPLEQUEST_BROWSER_EXECUTABLE='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
node scripts/capture-print-baseline.mjs --compare-baseline --verify-workspace
```

O teste de navegador é opcional e usa instalação existente de Playwright; não foi adicionada dependência nem executado download. Os testes padrão de componentes usam Vite e React já instalados, sem navegador/servidor, produzindo apenas um módulo de teste em `outputs/`.

Os avisos anteriores do build continuam: depreciação `module.register()` no Node 26, chunks acima de 500 kB e classificação estática limitada do Vinext. As rotas de saída permanecem `/`, `/revisao` e `/api/questions/revisions`. A falha externa do launcher Sites no Windows está documentada no 1A e não foi corrigida nem contornada dentro do código do produto. O comando direto Vinext passou. Não houve deploy.

## Inventário desta entrega

**Adicionados:**

- `app/components/QuestionsWorkspace.tsx`
- `app/components/QuestionFilters.tsx`
- `app/components/QuestionCard.tsx`
- `app/components/QuestionAlternatives.tsx`
- `app/components/QuestionsPagination.tsx`
- `app/components/SimulationComposer.tsx`
- `app/components/SimulationSelectionSummary.tsx`
- `app/components/SimulationPrintSheet.tsx`
- `app/hooks/useQuestionCatalog.ts`
- `app/hooks/useQuestionsWorkspace.ts`
- `tests/workspace-components.test.mjs`
- `tests/workspace-browser-checks.mjs`
- `docs/simplequest-2.0-incremento-1b.md`
- `docs/simplequest-2.0-verificacao-1b.json`

**Alterados:** `app/page.tsx`, `app/question-model.ts`, `package.json`, `tests/rendered-html.test.mjs`, `tests/catalog-contracts.test.mjs`, `scripts/capture-print-baseline.mjs`.

**Removidos:** nenhum. Alterações pendentes do 1A em `app/revisao/page.tsx`, `tsconfig.json`, tipos e documentos anteriores foram preservadas; não constituem trabalho novo deste incremento. Scripts auxiliares de extração e saídas de teste ficam nos diretórios já ignorados `work/` e `outputs/`.

## Pontos para o Incremento 1C

- O hook local é o único dono do estado desta página; ao criar o provider, transferir essa responsabilidade sem manter duas instâncias ou dois escritores na mesma chave.
- Permanecem as limitações herdadas do armazenamento: validação superficial de JSON e `setItem`/`removeItem` sem tratamento completo de armazenamento bloqueado. Não se ampliou a política de persistência neste incremento.
- A atualização do catálogo ocorre na montagem e na tentativa explícita após falha. Não foi criada invalidação entre rotas nem listener de retorno/foco; tratar a atualização após curadoria junto da futura navegação compartilhada.
- A curadoria continua independente; proteção de edições pendentes e restauração ao navegar devem acompanhar a mudança de navegação futura.
- Testes editoriais antigos ainda usam verificações textuais. A suíte interativa é opcional e requer navegador disponível. A referência PNG usa mídia print contínua, sem fixar paginação física para todos os navegadores.

**Nenhuma funcionalidade do Incremento 1C ou posterior foi implementada.** Sem provider global, compartilhamento de estado entre rotas, novas rotas, BottomNavigation, AppShell, PWA, taxonomia, tabelas, eventos, gamificação, mudanças pedagógicas ou redesign. Trabalho encerrado no 1B; não continuar automaticamente.
