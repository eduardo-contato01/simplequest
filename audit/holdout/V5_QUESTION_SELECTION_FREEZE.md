# Holdout V5 — freeze da seleção de 144 questões

## Resultado e autoridade

Temporada12:48documentos efetivos ×3questões =144objetos canônicos únicos.
Uma única invocação oficial; officialRetries=0/manualSwaps=0/alternateSeedRetries=0.
HEAD inicial:`6827bfc10a403e57645b150c1830a2c9806c06c8`.
A regra foi publicada em `cd6ed90b1989c62b24c93fa1218b698c1021b894` e seu
HEAD remoto foi confirmado antes de qualquer escolha real.

[Regra](V5_QUESTION_SELECTION_RULE.md), [JSON da regra](v5-question-selection-rule.json),
[seletor independente](v5_select_questions.py), [testes sintéticos](v5_select_questions_selftest.py),
[manifest selecionado](manifest-v5-questions-frozen.json) e
[provenance](manifest-v5-questions-frozen.provenance.json).
Registro prospectivo DEPOIS do índice neutro e ANTES do sorteio; a mensagem
preregister é operacional, não pré-registro retroativo da FaseA.

Este relatório é materializado antes do segundo commit. O resultado só se
congela formalmente com `audit: freeze v5 question selection 144`, push,
igualdade do HEAD local/remoto, working tree limpa e stage vazio.
O status pending_introducing_commit_and_push no manifest/provenance é snapshot
da criação, não garantia antecipada. publicationContract distingue os estados
formais antes e depois da publicação; não reescrever snapshots históricos.

## Algoritmo e fontes

Algoritmo:`v5-qselect-tertile-sha256-v1`. Seed documental literal:
`156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e`.
Documentos na ordem documents[] do R1; pools na ordem questions[] do índice,
por associação estrita documentId+fingerprint. As ordens documentais das duas
entradas são distintas; nenhuma posição presumida.

Janelas [0,floor(n/3),floor(2*n/3),n], zero-based/início inclusivo/fim exclusivo.
Uma candidata por terço, menor SHA256 lexical da concatenação UTF8 literal
`v5-question-selection|seedSha256|documentId|tertileIndex|questionId`, sem
normalização/whitespace/newline; empate por questionId literal.
Três objetos na ordem dos terços, sem mudar campos, números, IDs ou ranges.

| Artefato | SHA256 dos bytes |
| --- | --- |
| Índice final congelado | `a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7` |
| Manifest efetivoR1 | `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32` |
| Manifest histórico | `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62` |
| Regra publicada | `27300e3cc71beb5082a429367f116d9da40b2b0b505125643cc37f545d16a0af` |
| Seletor publicado | `57da2202afdae4ce26fe3e133ad22884be9918e83aea7694c97cdb6ef5cda652` |
| Manifest das144 | `91cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46` |
| Provenance das144 | `f78ef04d6e425e64315dd175386dcdda49b260b5abd2099c90f5558b5a3129ee` |
| Lista ordenada de144IDs | `11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a` |

Hash dos IDs:JSON compacto UTF8 sem BOM/espaços/newline/normalização Unicode,
[[documentId,[q1Id,q2Id,q3Id]],...], ordemR1/terços.
Manifest UTF8/noBOM/LF/indentação2/newline final, sem timestamp novo.
Horário de execução somente na provenance e no ledger operacional.

## Validação independente e determinismo

PASS:documents48/questionsPerDocument3/selectedQuestions144/uniqueQuestionIds144.
unknownQuestionIds=0/duplicateSelections=0/crossDocumentBindings=0/
fingerprintMismatches=0/invalidPhysicalPageRanges=0/manualSwaps=0/
alternateSeedRetries=0. Mínimo3/janelas disjuntas não vazias/cobertura total PASS.

Oito testes sintéticos antes do primeiro freeze:partições, n<3, bytes do hash,
Unicode sem normalização, empate/prioridade de hash, deepcopy de objetos,
serialização/reprodutibilidade e bindings/ranges inválidos. Nenhum pool real
foi escolhido nesses testes ou no preflight.

Depois da única execução oficial, o oracle Python enumerou e ordenou hashes
sem chamar choose/windows/candidate_hash; reproduziu144IDs/objetos/evidências/
metadata e bytes canônicos. Um segundo oracle JavaScript independente confirmou
as mesmas144escolhas, hashes, posições/janelas e serialização compacta dos IDs.
Deterministic replay=PASS; construção determinística byte a byte=PASS.
Verificações read-only não são novas invocações oficiais nem retries.

## Preservação e ressalvas transportadas

Cada campo documental R1 permanece idêntico; apenas extensões derivadas
autorizadas foram acrescentadas. selectedQuestions contém três objetos exatos;
selectionEvidence guarda hash/terço/posição/janela separadamente.
canonicalDocumentMetadata preserva metadata canônico e ressalvas sem copiar
o pool inteiro. sourceEffectiveManifestMetadata/canonicalIndexMethodology são
snapshots HISTÓRICOS, não flags da execução atual.

Configuração, sete adjudicações, índice de2136objetos, R1/histórico/protocolos/
erratas/código05C1/V1–V4/caches/checkpoints permanecem intactos;
103referências relevantes hash-conferidas, sem inventário massivo novo.

- Global22:apenas substituto efetivo v5-doc-e1c73fb849ef80a6; original retirado
  somente provenance, substituição pós-freeze/ranking2/performance-blind explícita.
- Global21:v5-doc-74e153f9c146d887 mantém pageCount/sourceFrozenPageCount1 e
  effectivePhysicalPageCount21; ranges usam21, não metadata histórico1.
- Global8:v5-doc-7a302456c4a6afbe mantém26objetos com lacunas q18–q21;
  nenhuma identidade fabricada ou renumeração. Fonte disponível incompleta,
  integridade original inconclusiva, página impressa indisponível, exclusões
  paralelas/reinícios e versão modificada global48 permanecem vinculados.
- [Exceção415 já congelada](V5_FINAL_CANONICAL_QUESTION_INDEX.md):411PNG+4JSON
  auxiliares histórica=not_independently_verifiable/historicalByteIdentityVerified=false.
  A seleção não reabriu a investigação, não usou esses auxiliares como inputs
  e não certifica identidade histórica retroativa. Nenhum novo hash de PDF,
  revisão/render/OCR ou inventário de milhares de arquivos nesta temporada.

## IDs escolhidos, ordem R1 e ordem dos terços

| Ordem R1 | documentId | IDs t0, t1, t2 |
| --- | --- | --- |
| 1 | `v5-doc-429b811d62a29a28` | `v5-doc-429b811d62a29a28:q4`, `v5-doc-429b811d62a29a28:q12`, `v5-doc-429b811d62a29a28:q18` |
| 2 | `v5-doc-9341853cd786543a` | `v5-doc-9341853cd786543a:q1`, `v5-doc-9341853cd786543a:q42`, `v5-doc-9341853cd786543a:q98` |
| 3 | `v5-doc-a37b092e0e967efc` | `v5-doc-a37b092e0e967efc:q3`, `v5-doc-a37b092e0e967efc:q21`, `v5-doc-a37b092e0e967efc:q38` |
| 4 | `v5-doc-78d5d0d89420b8d3` | `v5-doc-78d5d0d89420b8d3:q8`, `v5-doc-78d5d0d89420b8d3:q17`, `v5-doc-78d5d0d89420b8d3:q39` |
| 5 | `v5-doc-906c5ae29d59a1ff` | `v5-doc-906c5ae29d59a1ff:q5`, `v5-doc-906c5ae29d59a1ff:q17`, `v5-doc-906c5ae29d59a1ff:q28` |
| 6 | `v5-doc-7a302456c4a6afbe` | `v5-doc-7a302456c4a6afbe:q1`, `v5-doc-7a302456c4a6afbe:q14`, `v5-doc-7a302456c4a6afbe:q30` |
| 7 | `v5-doc-9e5595dac9eb75e3` | `v5-doc-9e5595dac9eb75e3:q4`, `v5-doc-9e5595dac9eb75e3:q19`, `v5-doc-9e5595dac9eb75e3:q29` |
| 8 | `v5-doc-c6d6158a42ac379f` | `v5-doc-c6d6158a42ac379f:q2`, `v5-doc-c6d6158a42ac379f:q7`, `v5-doc-c6d6158a42ac379f:q15` |
| 9 | `v5-doc-0c51e49589f148bc` | `v5-doc-0c51e49589f148bc:q4`, `v5-doc-0c51e49589f148bc:q7`, `v5-doc-0c51e49589f148bc:q13` |
| 10 | `v5-doc-91b5252bd14b8900` | `v5-doc-91b5252bd14b8900:q4`, `v5-doc-91b5252bd14b8900:q14`, `v5-doc-91b5252bd14b8900:q21` |
| 11 | `v5-doc-34e3910f5e106aae` | `v5-doc-34e3910f5e106aae:q3`, `v5-doc-34e3910f5e106aae:q11`, `v5-doc-34e3910f5e106aae:q18` |
| 12 | `v5-doc-74e153f9c146d887` | `v5-doc-74e153f9c146d887:q5`, `v5-doc-74e153f9c146d887:q10`, `v5-doc-74e153f9c146d887:q16` |
| 13 | `v5-doc-ae2f4e91af8a01f9` | `v5-doc-ae2f4e91af8a01f9:q24`, `v5-doc-ae2f4e91af8a01f9:q99`, `v5-doc-ae2f4e91af8a01f9:q107` |
| 14 | `v5-doc-815b83630e3d8c98` | `v5-doc-815b83630e3d8c98:q5`, `v5-doc-815b83630e3d8c98:q13`, `v5-doc-815b83630e3d8c98:q20` |
| 15 | `v5-doc-e9603e9180e6028b` | `v5-doc-e9603e9180e6028b:q2`, `v5-doc-e9603e9180e6028b:q8`, `v5-doc-e9603e9180e6028b:q12` |
| 16 | `v5-doc-dd8461744150ef4b` | `v5-doc-dd8461744150ef4b:q6`, `v5-doc-dd8461744150ef4b:q8`, `v5-doc-dd8461744150ef4b:q18` |
| 17 | `v5-doc-a7256b9befdea91b` | `v5-doc-a7256b9befdea91b:q2`, `v5-doc-a7256b9befdea91b:q12`, `v5-doc-a7256b9befdea91b:q17` |
| 18 | `v5-doc-cb4e2c7c9e714d00` | `v5-doc-cb4e2c7c9e714d00:q4`, `v5-doc-cb4e2c7c9e714d00:q15`, `v5-doc-cb4e2c7c9e714d00:q22` |
| 19 | `v5-doc-e0b6c6a249033308` | `v5-doc-e0b6c6a249033308:q27`, `v5-doc-e0b6c6a249033308:q76`, `v5-doc-e0b6c6a249033308:q116` |
| 20 | `v5-doc-2300b505b11855a2` | `v5-doc-2300b505b11855a2:q2`, `v5-doc-2300b505b11855a2:q13`, `v5-doc-2300b505b11855a2:q15` |
| 21 | `v5-doc-84179ac96b058ffb` | `v5-doc-84179ac96b058ffb:q6`, `v5-doc-84179ac96b058ffb:q16`, `v5-doc-84179ac96b058ffb:q35` |
| 22 | `v5-doc-05c35f7183da4927` | `v5-doc-05c35f7183da4927:q1`, `v5-doc-05c35f7183da4927:q9`, `v5-doc-05c35f7183da4927:q20` |
| 23 | `v5-doc-bd657a7d79e90389` | `v5-doc-bd657a7d79e90389:q33`, `v5-doc-bd657a7d79e90389:q43`, `v5-doc-bd657a7d79e90389:q93` |
| 24 | `v5-doc-02531e2612ade970` | `v5-doc-02531e2612ade970:q1`, `v5-doc-02531e2612ade970:q12`, `v5-doc-02531e2612ade970:q14` |
| 25 | `v5-doc-e223f9e9c5cea0cb` | `v5-doc-e223f9e9c5cea0cb:q6`, `v5-doc-e223f9e9c5cea0cb:q24`, `v5-doc-e223f9e9c5cea0cb:q28` |
| 26 | `v5-doc-a8e098aad9a7ece4` | `v5-doc-a8e098aad9a7ece4:q39`, `v5-doc-a8e098aad9a7ece4:q62`, `v5-doc-a8e098aad9a7ece4:q85` |
| 27 | `v5-doc-4ec5bc5117bb7440` | `v5-doc-4ec5bc5117bb7440:q19`, `v5-doc-4ec5bc5117bb7440:q64`, `v5-doc-4ec5bc5117bb7440:q143` |
| 28 | `v5-doc-2442b4ab742e42f2` | `v5-doc-2442b4ab742e42f2:q5`, `v5-doc-2442b4ab742e42f2:q7`, `v5-doc-2442b4ab742e42f2:q20` |
| 29 | `v5-doc-e123ad77b8edc98f` | `v5-doc-e123ad77b8edc98f:q4`, `v5-doc-e123ad77b8edc98f:q8`, `v5-doc-e123ad77b8edc98f:q20` |
| 30 | `v5-doc-675affeba8d87308` | `v5-doc-675affeba8d87308:q5`, `v5-doc-675affeba8d87308:q12`, `v5-doc-675affeba8d87308:q17` |
| 31 | `v5-doc-506c709758cb13a9` | `v5-doc-506c709758cb13a9:q2`, `v5-doc-506c709758cb13a9:q19`, `v5-doc-506c709758cb13a9:q26` |
| 32 | `v5-doc-3a0c4b28948e4a30` | `v5-doc-3a0c4b28948e4a30:q8`, `v5-doc-3a0c4b28948e4a30:q16`, `v5-doc-3a0c4b28948e4a30:q21` |
| 33 | `v5-doc-143f3f337e22fb52` | `v5-doc-143f3f337e22fb52:q1`, `v5-doc-143f3f337e22fb52:q20`, `v5-doc-143f3f337e22fb52:q31` |
| 34 | `v5-doc-87d7a7f5696b5a6a` | `v5-doc-87d7a7f5696b5a6a:q5`, `v5-doc-87d7a7f5696b5a6a:q10`, `v5-doc-87d7a7f5696b5a6a:q16` |
| 35 | `v5-doc-1b6b371a30f5cd22` | `v5-doc-1b6b371a30f5cd22:q8`, `v5-doc-1b6b371a30f5cd22:q15`, `v5-doc-1b6b371a30f5cd22:q20` |
| 36 | `v5-doc-80e01b1d6082d26b` | `v5-doc-80e01b1d6082d26b:q2`, `v5-doc-80e01b1d6082d26b:q15`, `v5-doc-80e01b1d6082d26b:q21` |
| 37 | `v5-doc-d5099c3057735940` | `v5-doc-d5099c3057735940:q2`, `v5-doc-d5099c3057735940:q7`, `v5-doc-d5099c3057735940:q11` |
| 38 | `v5-doc-b1498826d8a54db3` | `v5-doc-b1498826d8a54db3:q10`, `v5-doc-b1498826d8a54db3:q56`, `v5-doc-b1498826d8a54db3:q86` |
| 39 | `v5-doc-1fb8c32edfae9126` | `v5-doc-1fb8c32edfae9126:q30`, `v5-doc-1fb8c32edfae9126:q59`, `v5-doc-1fb8c32edfae9126:q96` |
| 40 | `v5-doc-d12896e095155245` | `v5-doc-d12896e095155245:q5`, `v5-doc-d12896e095155245:q12`, `v5-doc-d12896e095155245:q17` |
| 41 | `v5-doc-c3bf2d29c7e1d9e8` | `v5-doc-c3bf2d29c7e1d9e8:q1`, `v5-doc-c3bf2d29c7e1d9e8:q13`, `v5-doc-c3bf2d29c7e1d9e8:q20` |
| 42 | `v5-doc-0d7bc5575df13886` | `v5-doc-0d7bc5575df13886:q4`, `v5-doc-0d7bc5575df13886:q7`, `v5-doc-0d7bc5575df13886:q15` |
| 43 | `v5-doc-1babdc250c302165` | `v5-doc-1babdc250c302165:q2`, `v5-doc-1babdc250c302165:q8`, `v5-doc-1babdc250c302165:q21` |
| 44 | `v5-doc-bc5d90aa69fa3416` | `v5-doc-bc5d90aa69fa3416:q6`, `v5-doc-bc5d90aa69fa3416:q8`, `v5-doc-bc5d90aa69fa3416:q20` |
| 45 | `v5-doc-9b28d28efbbf0354` | `v5-doc-9b28d28efbbf0354:q3`, `v5-doc-9b28d28efbbf0354:q13`, `v5-doc-9b28d28efbbf0354:q24` |
| 46 | `v5-doc-47ff0591259f48eb` | `v5-doc-47ff0591259f48eb:q4`, `v5-doc-47ff0591259f48eb:q10`, `v5-doc-47ff0591259f48eb:q15` |
| 47 | `v5-doc-e1c73fb849ef80a6` | `v5-doc-e1c73fb849ef80a6:q5`, `v5-doc-e1c73fb849ef80a6:q7`, `v5-doc-e1c73fb849ef80a6:q20` |
| 48 | `v5-doc-ccc36240e82f271d` | `v5-doc-ccc36240e82f271d:q35`, `v5-doc-ccc36240e82f271d:q43`, `v5-doc-ccc36240e82f271d:q95` |

## Estados formais após publicação e STOP

Somente depois do segundo commit/push e HEAD remoto confirmado:
finalQuestionIndexFrozen=true/questionSelectionExecuted=true/
questionSelectionFrozen=true/selectedQuestions144/PhaseBComplete=true.
PhaseBComplete segue o freeze documental publicado:índice neutro mais freeze
da seleção; ambos estarão publicados. Isso não declara V5 completo ou avaliação
executada. Os flags históricos false do índice/manifestR1/políticas anteriores
são snapshots preservados, não reescritos.

GTConsulted=false/AuditorConsulted=false/groundTruthStarted=false/
groundTruthCreated=false/ocrExecuted=false/auditorExecuted=false/
metricsSeen=false/merge=false. Revisão estrutural assistida não é GT humano
independente. Nenhum cherry-pick, inspeção semântica de respostas ou mudança
funcional. STOP após segunda publicação. Próxima etapa só com nova autorização:
Ground Truth V5 com adjudicação humana independente; não preparar pacotes agora.
