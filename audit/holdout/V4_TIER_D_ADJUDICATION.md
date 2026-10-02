# Holdout V4 — adjudicacao neutra Tier D

## Resultado e autoridade

Adjudicacao humana materializada em 2026-10-02: 8 documentos, 182 questoes raw e 180 questoes canonicas. Todos os tiers de adjudicacao neutra estao concluidos: A 18/18, B 9/9, C 13/13 e D 8/8.

A unica autoridade para numeros e boundaries e o mapeamento humano congelado fornecido pelo operador. Esta etapa nao reinterpreta PDFs, nao refaz revisao visual e nao usa OCR, gabaritos, Ground Truth ou Auditor output. Nao classifica responseMode nem infere optionCount/optionLabels.

## Provenance congelada

- HEAD anterior/pacote preparado: `709695d3bf0909e082d5a40f48efad42c2987f33`.
- [Pacote Tier D](question-index-v4-tier-d-review-package.json): SHA256 `f886838926031e43d294a5f35f20392bd03f0a20424cedd9616874e674c9aa35`.
- Review context: `outputs/audit/holdout/v4-tier-d-review/review-context.json`; SHA256 `ed08fa450fbd92218529dac796b27ab39ab010d56319e5cf50000ec755575fec`.
- Mapeamento humano fornecido: SHA256 `8059ace44206f99965ab0eadaa2f38bf676fa331143d2e7d4b70032619f5bc82`.
- [Raw index preservado](question-index-v4-raw.json): SHA256 `36549f5067f3236fee90112fd1df63fb30c5ca5445ebec77ca139be41d722f79`.
- [Artefato adjudicado Tier D](question-index-v4-tier-d-adjudication.json): SHA256 `78586630fc0552a612ee230c9896d39f39e0cacbb6c8b8e3939e62032b0b0751`.

As adjudicacoes anteriores A unresolved, A neutral, B e C permanecem byte-preservadas; suas referencias e hashes constam do JSON. Os PDFs originais e as copias de review foram verificados somente por hash binario e permanecem preservados. O review-context e o pacote sao snapshots de preparacao e nao foram reescritos para marcar conclusao.

## Contagens

| documentId | Raw | Canonicas | Anomalias raw |
| --- | ---: | ---: | ---: |
| doc-1e18e7252399 | 21 | 20 | 0 |
| doc-2790a3c9786b | 20 | 20 | 0 |
| doc-3e395d355d2c | 40 | 40 | 0 |
| doc-42af2b3d2b27 | 20 | 20 | 0 |
| doc-4310686d43a6 | 20 | 20 | 0 |
| doc-800c2a22f148 | 20 | 20 | 0 |
| doc-b605f7a51fd5 | 20 | 20 | 0 |
| doc-c8d6da47c18b | 21 | 20 | 0 |
| Total | 182 | 180 | 0 |

## Duas exclusoes humanas de Producao Textual

- `doc-1e18e7252399:q21`: QUESTAO 21 impressa, tarefa de Producao Textual na pagina 11; excluida do conjunto canonico.
- `doc-c8d6da47c18b:q21`: QUESTAO 21 impressa, tarefa de Producao Textual iniciada na pagina 10 e continuada na pagina 11; excluida do conjunto canonico.

A nota obrigatoria abaixo esta em neutralNotes dos dois documentos e na provenance das exclusoes:

> source contains a printed "QUESTÃO 21" in the Produção Textual section; excluded from canonical neutral question index because it is the writing task, not one of the objective test questions.

A diferenca 182 -> 180 e deliberada e humana. rawQuestionCount/rawQuestionsInBatch e rawAnomalyCount permanecem como no raw original; nenhuma anomalia automatica foi criada. Zero anomalias automaticas nao substitui adjudicacao humana.

## Identidade e boundaries

questionId segue `documentId:qN`; questionNumber preserva o numero impresso das questoes objetivas. Ha sequencia 1-40 em `doc-3e395d355d2c` e 1-20 nos outros sete documentos. Nao ha reinicio legitimo nem sequenceRun.

Somente dois itens atravessam paginas: `doc-3e395d355d2c:q21` (25-26) e `doc-42af2b3d2b27:q4` (6-7). Todas as demais questoes canonicas possuem pageStart = pageEnd conforme o mapeamento humano.

## Validacoes e isolamento

JSON parseavel, 8 documentos, soma canonica 180, raw 182, IDs unicos e sequenciais, boundaries validos dentro do pageCount congelado, fingerprints correspondentes ao review-context, exclusoes explicitadas e fontes congeladas preservadas. Schema neutro coerente com as adjudicacoes A/B/C; metadados adicionais registram apenas autoridade humana e exclusoes.

- rawQuestionIndexModified = false
- finalQuestionIndexCreated = false
- questionSelectionExecuted = false
- groundTruthCreated = false
- auditorExecuted = false

Proximo passo previsto: construir/finalizar o final question index V4 em outra etapa; nao iniciado nesta execucao. Nenhuma selection, GT ou execucao do Auditor foi realizada.
