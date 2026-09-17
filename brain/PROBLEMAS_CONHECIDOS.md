# Problemas Conhecidos

## Dados e documentacao

- `README.md` ainda descreve o starter Vinext mais do que o SimpleQuest atual.
- `public/data/stats.json` diverge do catalogo atual.
- Numeros exibidos na home sao fixos, nao derivados do catalogo em runtime.
- Fontes de importacao em `work/` nao sao a fonte versionada principal.

## Catalogo

- Existem questoes com `pending-media`.
- Algumas questoes podem ter gabarito vazio, anulado ou incompatível com correcao simples A-E; isso ja foi apontado nas docs tecnicas existentes.
- `difficulty` e `subjects` vieram de importacao/curadoria livre; nao formam ainda taxonomia pedagogica confiavel.

## Aplicacao

- Autenticacao editorial usa constante `Administrador`; nao comprova identidade nem permissao real.
- A API valida campos obrigatorios, mas nao usa schema robusto para todos os tipos/JSONs.
- `ensureQuestionRevisionTable()` executa criacao/alteracao de tabela em tempo de requisicao.
- Estado em `localStorage` nao e sincronizado entre dispositivos e pode falhar em ambientes com armazenamento bloqueado.
- Edicoes nao salvas na revisao podem ser perdidas ao trocar contexto se o usuario nao salvar.

## Interface e testes

- Parte dos testes ainda depende de contratos especificos de renderizacao/codigo, embora ja existam testes de componentes.
- O lint passa com codigo 0, mas ha avisos em arquivos gerados.
- Impressao depende do navegador; nao existe gerador PDF server-side.

Ver tambem: [[ROADMAP]], [[AUDITORIA_PROVAS]].
