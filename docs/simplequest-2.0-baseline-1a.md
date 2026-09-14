# SimpleQuest 2.0 — baseline técnico do Incremento 1A

Referência obrigatória: [análise técnica anterior](simplequest-2.0-analise-tecnica.md), seção 10, “Incremento 1A — preparar uma referência confiável”. Registro em 11/09/2026, sobre o código base `9155102`. A análise anterior foi preservada.

Este incremento corrige a verificação técnica e fixa exemplos para comparação. Não modifica navegação, componentes de interface, conteúdo pedagógico, dados ou impressão. Nenhum trabalho do Incremento 1B ou posterior foi implementado.

## 1. Correções de TypeScript

- `app/revisao/page.tsx`: `prepareForEditing` declara retorno `Question`; a criação de alternativas usa `map<QuestionContentBlock[]>`. O contexto mantém `type: "text"` como discriminante da união, em vez de inferir `string`. O corpo, os valores retornados e as regras de preenchimento são os mesmos; não há conversão por `as Question` nem supressão de erros.
- `types/cloudflare-runtime.d.ts`: declarações oficiais geradas pelo Wrangler 4.92.0 já instalado, usando workerd 1.20260515.1, data de compatibilidade `2026-05-15` e flag `nodejs_compat` do build. Fornecem `cloudflare:workers`, `Fetcher`, `D1Database` e os demais tipos do runtime. Arquivo gerado: não editar manualmente.
- `types/cloudflare-env.d.ts`: estende `Cloudflare.Env` com `DB: D1Database`, correspondente ao binding de `.openai/hosting.json`. A consulta `.all<{ name: string }>()` passa a propagar o tipo até `column` em `db/index.ts`; o parâmetro deixa de ser implicitamente `any` sem alterar SQL ou adicionar casts.
- `tsconfig.json`: exclui `work/`, `dist/` e `.wrangler/`, além de `node_modules/`. Os arquivos auxiliares e as saídas geradas deixam de entrar na verificação. `build/sites-vite-plugin.ts` continua incluído, pois é código-fonte. `strict`, `noEmit` e as demais opções anteriores foram mantidos.
- `package.json`: adiciona `typecheck`, que executa `tsc --noEmit --incremental false`, evitando depender de cache incremental.

Nenhuma versão de dependência foi alterada; `package-lock.json` permanece idêntico. Uma tentativa de instalar `@cloudflare/workers-types` foi rejeitada pela revisão automática por falta de créditos do workspace e não foi executada. As declarações foram obtidas localmente com o gerador oficial já disponível, sem instalação ou download.

Os tipos estão versionados para que `npm run typecheck` não dependa de um build prévio. Quando o runtime ou seus bindings mudarem, executar:

```powershell
npm run build
npm run types:generate
npm run typecheck
```

`types:generate` executa `wrangler types types/cloudflare-runtime.d.ts -c dist/server/wrangler.json --include-env=false`. Usa a configuração gerada pelo Vite/Sites para evitar uma segunda configuração de deploy. `--include-env=false` evita referências tipadas a módulos dentro de `dist/`; os bindings do projeto ficam na pequena declaração de ambiente. Conferir essa declaração contra `.openai/hosting.json` após qualquer mudança de bindings. A geração não executa consultas D1.

## 2. Suíte padrão e contratos

`npm test` mantém o build anterior como pré-requisito e, em seguida, executa `npm run test:contracts`. Este último inclui explicitamente:

- `tests/search.test.mjs`: os cinco testes existentes de acentos, erros ortográficos, sinônimos, números/siglas estritos e ordenação por relevância.
- `tests/rendered-html.test.mjs`: os três testes anteriores, preservados integralmente, incluindo consistência de mídia, validação KaTeX e verificações editoriais.
- `tests/catalog-contracts.test.mjs`: exemplos reais, normalização idempotente sem mutação, prioridade das revisões por ID, preservação da ordem da base, adição de registro manual somente em memória, carregamento normal, fallback para erro HTTP/rede/JSON nas revisões e propagação da falha da base.

A flag `--experimental-strip-types` permite importar os utilitários TypeScript também no Node 22.13 declarado no projeto; esta execução usou Node 26.4.0. Não houve alteração do requisito de Node. Os novos testes importam funções públicas e verificam resultados, sem ler ou procurar a implementação em `app/page.tsx`. Os testes antigos ainda contêm verificações textuais; migrá-las durante futuras extrações exigirá preservar os respectivos comportamentos, sem simplesmente removê-las.

Resultado: **18 testes aprovados, zero falhas, zero ignorados** (incluindo subtestes). Os mocks de `fetch` são restaurados pelo runner e não acessam a API real.

## 3. Rotas, dados e exemplos funcionais

Rotas atuais: `/` para busca, respostas e montagem/impressão; `/revisao` para curadoria; `/api/questions/revisions` para revisões. Não existem novas páginas implementadas nesta entrega.

Referência de dados: `public/data/questions.json`, com **1.217 questões**. SHA-256 dos bytes do arquivo, igual antes e depois:

```text
ed602ca11d3a454edb279822079ff068f8efae085cd93f385b8faca98c1007eb
```

Os exemplos são registros existentes, identificados em [baseline-cases.json](../tests/fixtures/baseline-cases.json). A fixture contém somente identificadores e a composição de referência, sem sobrescrever o catálogo. [capture.json](baseline-1a/capture.json) contém também SHA-256 de `JSON.stringify` de cada registro bruto para distinguir futuras edições editoriais de mudanças de apresentação. A apresentação usa a normalização atual do modelo; não se deve gravar essa normalização de volta no JSON para reproduzir o baseline.

| Caso | ID / identificação | O que comparar | Gabarito |
| --- | --- | --- | --- |
| Apenas texto | `cmb-2003-2-3` — CMB 2003, Q2 | Soma de cinco ímpares consecutivos com resultado 625; enunciado e cinco alternativas somente textuais. | A |
| Matemática inline | `cmb-2003-4-5` — CMB 2003, Q4 | Fração `\frac{3}{28}` entre “a fração” e “quatro vezes maior”; permanece dentro da frase. | E |
| Fórmula em bloco | `cmb-2003-1-2` — CMB 2003, Q1 | Expressão com potências e frações, separada de “A expressão” e “É igual a:”. O modelo normaliza o display para bloco. | E |
| Tabela | `cmb-2008-13-159` — CMB 2008, Q13 | Uma linha, cinco células: F=80794, G=16832, H=49698, I=83160, J=24840; sem cabeçalho, tamanho configurado 13. | D |
| Imagens no enunciado | `cmb-2003-11-12` — CMB 2003, Q11 | Operação com figuras e quadro de somas; preservar a sequência texto → imagem → texto → imagem. Arquivos `cmb-2003-11_1.webp` (291×55) e `_2.webp` (431×315). | C |
| Imagens nas alternativas | `cmb-2014-15-291` — CMB 2014, Q15 | Pilha de cubos no enunciado (`cmb-2014-15.webp`, 571×393) e cinco pares de vistas em `_a.webp` até `_e.webp`; escala das alternativas 50%. | B |
| Bloqueio editorial | `cmb-2003-2-3` — CMB 2003, Q2 | `isLocked=true`, autenticação e evento `authenticated` no histórico. Na busca, selo “Autenticada · Admin”; na revisão, campos protegidos desabilitados. | A |

Todos os seis registros escolhidos estão `ready` e bloqueados na base. Bloqueio editorial não impede responder ou selecionar a questão na página inicial. O fluxo existente exige motivo de pelo menos cinco caracteres para desbloquear; a API retorna 423 para mudanças protegidas em questão bloqueada. Esses fluxos de escrita não foram executados contra o banco nesta tarefa.

Para comparação manual futura: filtrar instituição CMB e o ano, localizar o número da questão, expandir, conferir os blocos/alternativas e o gabarito. Na questão com imagens, conferir também abertura/ampliação e fechamento por Escape. Abrir o registro bloqueado em `/revisao` somente para leitura; não autenticar, desbloquear, salvar ou excluir os exemplos.

### Simulado misto de referência

Título: **SimpleQuest — referência 1A**. Selecionar os seis IDs da fixture, inclusive em ordem inversa, e comparar a saída nesta ordem:

1. CMB 2003 Q1 — fórmula em bloco — **E**.
2. CMB 2003 Q2 — texto — **A**.
3. CMB 2003 Q4 — matemática inline — **E**.
4. CMB 2003 Q11 — duas imagens — **C**.
5. CMB 2008 Q13 — tabela — **D**.
6. CMB 2014 Q15 — imagem e imagens nas alternativas — **B**.

A seleção usa a ordem do catálogo, não a ordem dos cliques nem a ordenação visível da busca. Filtros e paginação não removem os IDs selecionados. O resumo mostra no máximo oito itens e um contador de excedentes; a impressão usa todos. A seleção e o título pertencem ao estado local `simplequest:questions-view:v1`; não há registro de simulado persistido em tabela. O estado da curadoria usa `simplequest:review-view:v1`. Essas chaves não foram migradas.

Qualquer futura verificação de escrita deverá usar uma **cópia descartável** do banco e um perfil de navegador isolado. Não apontar esse teste para D1 remoto nem para o estado original em `.wrangler/state`. Parar os processos que usam o SQLite antes de copiar o estado completo, incluindo arquivos WAL/SHM presentes; configurar a instância de teste para usar apenas essa cópia. Este incremento não fez escrita no banco nem precisou copiá-lo.

## 4. Referência congelada da impressão

- [print.html](baseline-1a/print.html): DOM renderizado da folha real, com CSS compilado, imagens e fontes incorporados. Não depende de servidor, banco, `dist/` ou JavaScript para abrir depois. **Na tela normal fica oculto**, como a folha original; usar `Ctrl+P` para visualizar a impressão. Não adicionar estilos de conveniência ao arquivo congelado.
- [print.png](baseline-1a/print.png): captura visual contínua com mídia CSS `print`, largura de 794 px; permite inspecionar o conteúdo sem abrir o diálogo. Não representa paginação física A4.
- [capture.json](baseline-1a/capture.json): navegador, data, hashes, ordem e verificações realizadas.

A captura monta `Home` e seus componentes reais, com o CSS do build, em contexto efêmero do Edge 152.0.4191.66. Todas as requisições são interceptadas: catálogo e assets locais, revisões vazias. Não há conexão com o backend ou uso de localStorage do usuário. A fixture carrega os IDs em ordem inversa para verificar a ordem final. Foram conferidos título, seleção, seis artigos, cinco alternativas por artigo, gabarito, fórmula inline, fórmula em bloco, uma tabela, oito imagens carregadas e cinco imagens nas alternativas do último artigo. Zero erros de página. Reabrir o HTML congelado na mesma sessão produziu um PNG idêntico ao da folha original.

Isso é uma referência do catálogo base, não uma captura de revisões remotas ou uma certificação de todas as combinações de impressão. A captura verifica o CSS de quebra de página do gabarito; a quantidade física de páginas depende do navegador e das opções do diálogo e não foi fixada no PNG.

### Estrutura e regras atuais a preservar

`section.print-sheet[aria-hidden="true"]` é irmã de `.app-shell`. Contém cabeçalho com título, campos Nome/Data, um `article` por selecionada e `div.answer-key` ao final. Cada artigo contém número sequencial e instituição/ano, `QuestionBlocks` em modo `print` e `ol type="A"` com as alternativas. Alternativas estruturadas também usam `QuestionBlocks`, com `print compact`; as demais usam texto e o fallback do modo de resposta. O gabarito usa a resposta oficial, ou `—` se vazia, independentemente das respostas dadas pelo aluno.

O botão “Gerar simulado / PDF” está desabilitado sem seleção e chama `window.print()`. Não há geração de arquivo por servidor nem modo de resolução de simulado.

| Elemento | Regra atual |
| --- | --- |
| Papel | `@page`: A4, margens 18 mm verticais e 16 mm horizontais. |
| Visibilidade | `.print-sheet` oculta na tela; em impressão, visível e `.app-shell`/modal de imagem ocultos. |
| Fonte e cabeçalho | Times New Roman/serif, cor #111; título 22 px; Nome/Data 12 px; borda inferior e espaçamento de cabeçalho. |
| Questão | 12 pt, entrelinha 1,42, `white-space: pre-line`, margem inferior 24 px e `break-inside: avoid`; título 13 pt, instituição/ano 9 pt. Artigos maiores que uma página ainda dependem do navegador para fragmentação. |
| Blocos | Grid com gap 10 px; fórmulas em bloco centralizadas, KaTeX com HTML/MathML. Inline preserva continuidade da frase. |
| Tabelas | Largura 100%, bordas colapsadas, tamanho CSS 10 pt; células com borda #555 e padding 4×6 px. Configurações inline do bloco, como fonte 13 no exemplo, prevalecem quando aplicáveis. |
| Alternativas | Grid com gap 5 px, recuo esquerdo 28 px. **O CSS compilado atual resulta em `list-style-type: none`**, mesmo com `type="A"`; os marcadores alfabéticos não aparecem na captura. Comportamento registrado, sem correção visual neste incremento. |
| Imagens | Centralizadas, flex com quebra e gap 8 px; largura automática, limite de altura 105 mm, `object-fit: contain`; `maxWidth` inline respeita escala 25/50/75/100%, padrão 50%. |
| Imagem recolhida | `hiddenByDefault=true` não imprime a imagem, mesmo que ela tenha sido revelada na tela. Blocos `pending-media` não aparecem no renderer. |
| Gabarito | `break-before: page`; itens em flex com gaps 14×28 px, título ocupando toda a largura. |

O fundo e os resets globais também fazem parte da referência; cores de fundo no papel dependem da opção “gráficos de fundo” do navegador. A presença de `aria-hidden` na folha é anterior a esta tarefa. Nenhum desses detalhes foi redesenhado ou corrigido aqui.

### Reproduzir uma captura de comparação

O script opcional `scripts/capture-print-baseline.mjs` usa Vite instalado no projeto e um Playwright/navegador já disponíveis. Não integra a suíte padrão e não instala dependências. A saída fica somente em `outputs/baseline-1a/` (ignorado pelo Git); **não substitui automaticamente a referência em `docs/`**. Após extrair a página no futuro, adaptar a montagem do componente, mantendo as verificações do DOM e contratos; o script não procura trechos literais no código-fonte.

Comandos usados neste ambiente Windows:

```powershell
npm run build
$env:SIMPLEQUEST_PLAYWRIGHT_MODULE='C:/Users/trans/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'
$env:SIMPLEQUEST_BROWSER_EXECUTABLE='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
node scripts/capture-print-baseline.mjs
```

Em outro ambiente, ajustar os dois caminhos ou omitir as variáveis se `playwright` e seu Chromium já estiverem resolvíveis. Comparar o novo HTML/PNG/relatório com os arquivos congelados. O script é ferramenta de captura, não componente do produto.

## 5. Validação final e falha externa documentada

Ambiente: Windows, PowerShell, Node 26.4.0, npm 11.17.0, TypeScript 5.9.3, Vinext 0.0.50, Vite 8.0.13, Wrangler 4.92.0. As versões existentes foram mantidas.

| Verificação / comando | Resultado |
| --- | --- |
| `node …/sites/0.1.59/scripts/configure-execution-profile.mjs` | Sucesso; perfil `portable`, `configured: false`, configuração existente preservada. |
| `node node_modules/wrangler/bin/wrangler.js types types/cloudflare-runtime.d.ts -c dist/server/wrangler.json --include-env=false` | Sucesso; tipos oficiais locais gravados. A primeira tentativa encontrou diretório `types/` ausente; foi criado antes da repetição. |
| `npm run typecheck` | **Aprovado**, zero diagnósticos, exit 0. |
| `npm run test:contracts` | **Aprovado**, 18 testes. |
| `npm test` | **Aprovado**, build prévio e os 18 testes, exit 0. |
| `npm run build` | **Aprovado**, cinco fases Vinext/Vite concluídas, exit 0. |
| `node …/sites/0.1.59/scripts/build-site.mjs` | **Falha externa no launcher Windows**, exit 1 antes de iniciar Vinext; diagnóstico abaixo. |
| `node scripts/capture-print-baseline.mjs` com as variáveis acima | **Aprovado**, contratos do DOM e equivalência visual do HTML autossuficiente. |

O wrapper instalado em `C:/Users/trans/.codex/plugins/cache/openai-curated-remote/sites/0.1.59/scripts/build-site.mjs` apenas delega para o script `build` do projeto. Seu `package-manager.mjs` gera, no Windows, uma chamada `cmd.exe /d /s /c` com cada token entre aspas e `windowsVerbatimArguments: true`. Neste ambiente essa chamada faz o shim npm procurar `node_modules/npm/bin/npm-prefix.js` e `npm-cli.js` **dentro do checkout**, onde não existem.

A reprodução isolada com `spawnSync` e apenas `--version` confirmou a origem: a mesma forma de invocação com `"npm"` retornou `MODULE_NOT_FOUND`/exit 1; `npm --version` sem as aspas geradas retornou `11.17.0`/exit 0. Portanto a falha ocorre sem ler ou compilar código SimpleQuest. A execução direta `npm run build` e o build dentro de `npm test` passaram. O plugin externo não foi editado, nem se adicionou um workaround de ambiente ao produto. Esse wrapper permanece com uma limitação Windows claramente documentada; não é apresentado como aprovado.

O artefato gerado contém `dist/server/index.js` com exportação default do Worker e método `fetch`, `dist/server/wrangler.json` com binding D1 `DB` e assets em `../client`, além dos assets de cliente. O relatório de rotas continua limitado a `/`, `/revisao` e `/api/questions/revisions`. Não houve deploy.

Avisos não bloqueantes do build: depreciação `module.register()` no Node 26; chunks maiores que 500 kB; limitação de classificação estática de rotas do Vinext. Não foram feitas otimizações, mudanças de versões ou alterações de rotas para remover esses avisos.

## 6. Arquivos e conclusão de escopo

Alterados: `app/revisao/page.tsx` (somente anotações de tipo), `tsconfig.json` (escopo), `package.json` (comandos).

Adicionados: `types/cloudflare-runtime.d.ts`, `types/cloudflare-env.d.ts`, `tests/catalog-contracts.test.mjs`, `tests/fixtures/baseline-cases.json`, `scripts/capture-print-baseline.mjs`, este documento e `docs/baseline-1a/{print.html,print.png,capture.json}`. `docs/simplequest-2.0-analise-tecnica.md` já existia da análise anterior e permanece sem alteração, embora ainda não versionado no Git.

Mudança de comportamento: apenas na ferramenta de validação, pois `npm test` agora inclui busca e os novos contratos. **Nenhum comportamento do produto foi alterado.** Catálogo, mídias, CSS, banco, migrações, worker, impressão e lockfile não receberam alterações.

Incremento 1A encerrado com TypeScript, testes e build Vinext confiáveis e a falha externa do wrapper Sites diagnosticada. Nenhuma funcionalidade de 1B ou posterior foi implementada: sem nova navegação, `/aprender`, `/simulados`, `/perfil`, shell compartilhado, PWA, taxonomia, alterações pedagógicas, novas tabelas ou mudanças visuais. Não continuar automaticamente para o próximo incremento.
