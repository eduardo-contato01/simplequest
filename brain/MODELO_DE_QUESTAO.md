# Modelo De Questao

Fonte principal: `app/question-model.ts`.

## `Question`

Campos principais:

- Identidade/proveniencia: `id`, `sourceRow`, `sourceDocument`, `sourceBookmark`.
- Classificacao: `school`, `year`, `number`, `subjects`, `difficulty`.
- Resposta: `answer`, `answerType`.
- Conteudo legado: `content`, `preview`, `stem`, `alternatives`, `formula`, `tableData`, `imageUrls`.
- Conteudo rico: `contentBlocks`, `alternativeBlocks`.
- Estado editorial: `status`, `isCustom`, `updatedAt`, `authenticatedAt`, `authenticatedBy`, `isLocked`, `lockedAt`, `lockedBy`, `lastUnlockReason`, `auditTrail`.

## Formatos de resposta

- `ABCDE`: alternativas A-E.
- `ABCD`: alternativas A-D.
- `CE`: Certo/Errado.

O catalogo atual usa efetivamente `ABCDE` em todas as questoes, mas a UI e os testes cobrem os outros modos.

## Blocos ricos

`contentBlocks` representa o enunciado. `alternativeBlocks` representa cada alternativa como uma lista de blocos.

Tipos implementados:

- `text`: texto, segmentos opcionais (`bold`, `italic`, `underline`), `section` e alinhamento.
- `formula`: LaTeX, com `display` `inline` ou `block`.
- `script`: base + valor em sobrescrito ou subscrito.
- `table`: dados textuais, linhas de cabecalho, tamanho de fonte e `content` inline opcional.
- `image`: URLs, dimensoes naturais, escala 25/50/75/100 e opcao `hiddenByDefault`.
- `pending-media`: marcador de midia encontrada mas ainda nao convertida.

## Renderizacao

- `QuestionBlocks` filtra blocos por `hasMath`, `hasTable` e `hasMedia`.
- Formulas usam KaTeX com `throwOnError: false`, `strict: "ignore"` e `trust: false`.
- Imagens usam `QuestionMedia`, com revelacao opcional, ampliacao em modal e modo de impressao.
- Tabelas suportam uma sintaxe propria: `|` separa colunas, quebra de linha separa linhas, `^` mescla acima, `>` mescla a esquerda e `~` cria celula invisivel.

## Normalizacao

- `structureQuestion()` separa enunciado e alternativas quando necessario.
- `questionContentBlocks()` cria blocos a partir de campos legados quando `contentBlocks` nao existe.
- `normalizeImportedFormulaAlternatives()` move formulas finais para alternativas quando a importacao deixou alternativas implicitas.
- `repairCmb2004Question3()` contem reparo especifico para `cmb-2004-3-34`.
- `normalizeQuestionContent()` normaliza formulas inline/bloco e mescla textos adjacentes.

Ver tambem: [[IMPORTADOR]], [[PROBLEMAS_CONHECIDOS]].
