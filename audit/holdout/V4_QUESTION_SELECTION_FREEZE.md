# Holdout V4 — Question Selection congelada

## Resultado

Seed `20261001`; 48 documentos; 3 questoes por documento; 144 selectedQuestions e 144 IDs globalmente unicos. Selecao original validada com deterministic replay PASS antes da tentativa de serializacao que falhou. Nenhuma selecao ou replay foi reexecutado durante este reparo.

## Reparo de materializacao

- selectionReexecuted = false
- materializationRepair = true
- selectedQuestionIdsPreservedFromFailedSerializationAttempt = true
- reason: UTF-8 serialization repair after cp1252/U+FFFD corruption; no question choice changed.

O manifest invalido foi usado somente para recuperar os 144 IDs previamente escolhidos. A estrutura foi reconstruida da Phase A intacta, e cada questao foi recuperada pelo ID no Final Question Index congelado. Nao houve recodificacao dos caracteres perdidos nem tentativa de selecionar novas questoes.

Os registros nao commitados de conclusao da tentativa falha em CONTEXTO e brain foram restaurados ao HEAD; os registros atuais foram escritos somente apos validar o reparo. Historico commitado preservado.

## Preservacao de IDs

Lista canonica: [[documentId, [q1Id, q2Id, q3Id]], ...], na ordem Phase A. Hash SHA256 dos bytes UTF-8 do JSON compacto sem espacos, equivalente a JSON.stringify da lista, sem normalizacao Unicode.

- selectedIdsBeforeRepairHash: `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`
- selectedIdsAfterRepairHash: `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`
- Igualdade antes/depois: PASS.
- IDs recuperados coincidem exatamente com o resultado do replay anteriormente validado; nenhuma chamada a select_questions() ou select_documents() neste reparo.

## Validacoes criticas

- UTF-8 estrito, sem BOM, com LF e caracteres Unicode literais.
- invalidReplacementCharacterCount = 0 (U+FFFD literal e escape JSON ausentes).
- documentNonSelectionDifferences = 0: todos os campos documentais exceto selectedQuestions sao deep-equal a Phase A.
- Todos os campos da raiz, exceto documents, permanecem identicos a Phase A.
- Ordem dos 48 documentos exatamente igual a Phase A; 3 questoes por documento.
- 144 selectedQuestions / 144 IDs unicos, todos vinculados ao documento correto no Final Question Index.
- questionNumber/pageStart/pageEnd e campos adicionais de identidade preservados integralmente dos objetos canonicos.
- Uma questao por terco canonico, verificada por posicao, sem executar novamente a funcao de selecao.
- COLÉGIO, PÓDION, 6º Ano e 9º Ano preservados exatamente como na Phase A; sem normalizacao de strings.
- doc-1e18e7252399:q21 e doc-c8d6da47c18b:q21 continuam ausentes por serem Producao Textual.

Phase A e Final Question Index usam ordens documentais distintas ja congeladas; a associacao e por documentId. Nenhuma das ordens ou da lista canonica de questoes foi alterada.

## Linhagem e hashes finais

- HEAD anterior: `878d67918d87dadb1c6e04346f6fd6ec14d1cee3`.
- Funcao original usada somente na tentativa anterior: `scripts/audit_response_holdout_select.py:select_questions`; generic selector SHA256 `a13f6cc0f53228c6464caf5fab8b8abcf9481f95d5c87b3844a8415164733e27`.
- selectionCodeState original: `clean`, capturado antes dos arquivos da tentativa falha.
- [Phase A](manifest-v4-a.json): SHA256 `be69ceafd2fde2ce00f5f72966c12e22d33f575785ddc00ae57030fe74b2dccc`; canonical JSON SHA256 `cd4e2a6a39c736d5f7cd58f53095e920d88ef98858e9fc42fd75a5fd6250a1c1`.
- [Final Question Index](question-index-v4-final.json): SHA256 `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab`; canonical JSON SHA256 `89d852af97c30bc39607d54fc8017c484f0ae3fea8af09a78e29f17311f3a62d`; 48 documentos / 1.732 questoes.
- [Phase B reparada](manifest-v4-b.json): SHA256 `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7`; canonical JSON SHA256 `26d76c5938b54a92a88b69552db8652ef61e0fb69fc0028cb55b001d20be55d4`.
- [Provenance Phase B](manifest-v4-b.provenance.json): SHA256 `921bfd858c472164a3d50eae153444105eab6170a482cd793372bc4c805cbb42`.

Hashes canonical JSON dos artefatos seguem audit_holdout_schema.sha256_json, como no V3. O hash da lista de IDs usa a convencao compacta definida acima.

## Distribuicao e isolamento

32 documentos text_native, 15 raster e 1 hybrid; 22 familias e 17 anos distintos. Eras cobertas: 2004-2009, 2010-2014, 2015-2019 e 2020-2025.

Nao houve alternate seed, retry, cherry-pick, selecao documental, reinterpretacao de PDF, consulta a respostas/gabaritos, criacao de GT ou execucao do Auditor.

## Estado congelado

- neutralAdjudicationComplete = true
- finalQuestionIndexCreated = true
- questionSelectionExecuted = true
- groundTruthCreated = false
- auditorExecuted = false
- freezeStatus = ready_for_ground_truth_annotation

Proximo passo: Ground Truth V4 em outra etapa. Nenhum merge ou alteracao da main.

## Reparo objetivo de metadata pos-freeze — 2026-10-05

Somente pageEnd da selectedQuestion doc-6381aed53bb1:q19 mudou de 14 para 15. Nenhuma selecao ou replay foi reexecutado; seed, ordem documental e os mesmos 144 IDs permanecem congelados. O final index foi reparado objetivamente; por isso questionIndexChangedAfterFreeze=true na provenance, sem mudanca de escolha.

- selectionReexecuted = false
- selectedQuestionIdsChanged = false
- objectiveMetadataRepair = true
- selected IDs before/after SHA256 = 301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477 (identicos).
- Manifest B SHA256 atual = 763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7.

GT humano 01-07: zero diferencas estruturais ou de bytes em questions[]; progresso 63/144. Review packages/contextos 08-10 nao regenerados e aguardam regeneracao no novo source state. GT final=false; Auditor=false. O registro de reparo UTF-8 anterior permanece historico e intacto. Ver [errata](V4_OBJECTIVE_ERRATUM_Q19_PAGE_RANGE.md).
