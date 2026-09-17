# Roadmap

## Curto prazo

- Manter este brain atualizado quando arquitetura, decisoes ou estado relevante mudarem.
- Atualizar `README.md` para descrever o SimpleQuest real, comandos atuais e fluxo de dados.
- Resolver divergencia entre `public/data/stats.json` e `public/data/questions.json`, ou remover/explicar o arquivo se nao for usado.
- Melhorar documentacao reprodutivel do importador e das dependencias em `work/source_files`.

## Qualidade e seguranca

- Validar entradas da API com schemas explicitos.
- Separar autorizacao real da nocao editorial de "Administrador".
- Tratar `localStorage` indisponivel ou bloqueado.
- Proteger edicoes nao salvas ao trocar de questao/sair da revisao.

## Produto

- Evoluir navegacao planejada em etapas documentadas em `docs/simplequest-2.0-analise-tecnica.md`.
- Criar fluxo de auditoria em massa conforme [[AUDITORIA_PROVAS]].
- Melhorar exibicao/validacao de questoes com gabarito vazio, anulado ou fora de A-E antes de usar pontuacao automatica.
- Manter impressao e exemplos baseline ao extrair ou reorganizar componentes.

## Importacao

- Tornar pipeline de importacao mais reprodutivel e documentado.
- Priorizar conversao/revisao das questoes com `pending-media`.
- Auditar amostras ricas antes de autenticar lotes.

## Ingestão Assistida de Questões (pós-Auditor)

Etapa **posterior ao Auditor de Provas**. Nao implementar durante a estabilizacao atual do pipeline de auditoria; so deve comecar quando admissao, segmentacao, extracao e confianca por componente estiverem validadas. Nao faz parte do escopo de estabilizacao em andamento.

Objetivo: reutilizar a infraestrutura do Auditor para extrair questoes que ainda nao existem no catalogo diretamente dos PDFs canonicos, evitando copia manual em escala.

Arquitetura conceitual:

```
PDF canonico
-> admissao/segmentacao
-> extracao estruturada da questao
-> staging/draft_import
-> classificacao de metadados
-> revisao por confianca
-> catalogo oficial
```

Requisitos:

- Nunca inserir automaticamente no catalogo oficial; toda ingestao passa por staging e revisao humana.
- Manter referencia ao PDF/pagina/regiao original de cada questao extraida.
- Preservar texto, alternativas, formatacao, tabelas, formulas e midia conforme a capacidade do Auditor.
- Registrar confianca por componente (texto, alternativas, tabela, formula, midia, formatacao inline).
- Derivar instituicao/ano/prova/serie/materia preferencialmente de metadados estruturais do documento, nao de digitacao.
- Classificar tema/subtema/conteudo contra uma taxonomia fechada ja existente, sem criacao livre de categorias.
- Permitir revisao em lote conforme faixas de confianca.
- Usar as 1.217 questoes ja cadastradas como benchmark para medir a fidelidade da extracao automatica.
- Futuramente permitir importar uma prova inteira para staging.

Ver tambem: [[PROBLEMAS_CONHECIDOS]], [[DECISOES]], [[AUDITORIA_PROVAS]].
