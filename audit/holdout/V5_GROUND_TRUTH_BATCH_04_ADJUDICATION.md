# Holdout V5 — Ground Truth Batch04, Temporada14/Episódio04

Branch `audit/holdout-v5-blind`; HEAD inicial local/remoto confirmado:
`8599a934a5490866c305c0411d6c6e25106dca8e`. Escopo exclusivo: posições R1
10–12, três documentos e nove questões previamente selecionadas. Nenhuma nova
seleção, reconstrução de índice, classificação visual pelo agente ou consulta
a gabarito, predições, resultados ou métricas V5.

## Aprovação e evidência obrigatória

As nove fichas foram recebidas uma por vez e confirmadas individualmente pelo
humano. A exceção de confirmação por envio do Batch03 NÃO foi estendida.
Depois das nove confirmações foi apresentado o resumo integral; a autorização
final aprovou expressamente campos, notas, correções, representação dos subitens,
21 eventos de provenance e publicação exclusiva condicionada aos gates.

Resumo aprovado SHA256:
`5a9e6e92016799a4d30fdd6455852c253ab8b92972b60bfb7d4b8f6940d0f9ce`.
Autorização final SHA256:
`9d6f6e667d29f417688792c82b93e21aa3a3106b31d92a656ec640b9591e599c`.
Checkpoint humano completo SHA256:
`21d58db0959184f186a895569eefebba449421dafeb28f3b17009cad1b8e4db8`.
Preflight SHA256:
`63706d2c857d85fb7224a131f5ef7246eed73c4419c13cb0f0918b892a63735c`.

[Evidência humana](ground-truth-v5-batch-04.human-decisions.json) incorpora os
21 eventos brutos/correções/confirmações com caminho, tamanho, SHA256 e bytes
UTF8 recuperáveis; resumo, autorização literal, checkpoint, preflight, prompt
de execução, guardas físicos, quatro prefixos históricos brutos e fontes/testes
operacionais com execução sintética persistida. Snapshots anteriores com
materializationAuthorized=false continuam históricos, sem reescrita; a autoridade
posterior reside no registro final separado, explicitamente vinculado ao resumo.

## Nove decisões humanas

| questionId | Página física | optionCount / labels | contentKind |
| --- | --- | --- | --- |
| v5-doc-91b5252bd14b8900:q4 | 3 | 4 / A,B,C,D | text |
| v5-doc-91b5252bd14b8900:q14 | 7 | 4 / A,B,C,D | text |
| v5-doc-91b5252bd14b8900:q21 | 11 | 4 / A,B,C,D | mixed |
| v5-doc-34e3910f5e106aae:q3 | 2 | 5 / A,B,C,D,E | mixed |
| v5-doc-34e3910f5e106aae:q11 | 5 | 5 / A,B,C,D,E | mixed |
| v5-doc-34e3910f5e106aae:q18 | 6 | 5 / A,B,C,D,E | mixed |
| v5-doc-74e153f9c146d887:q5 | 6 | 5 / A,B,C,D,E | text |
| v5-doc-74e153f9c146d887:q10 | 11 | 5 / A,B,C,D,E | text |
| v5-doc-74e153f9c146d887:q16 | 17 | 5 / A,B,C,D,E | mixed |

Todas responseMode=single_choice/layout=vertical/markerStyle=parenthesized/
responseControls=[]. As oito primeiras têm subitems=[]. Somente Doc12q16
tem três objetos label/role/pages/notes, I/II/III em ordem, role=internal_content,
pages=[17], explicitamente aprovados pelo humano. São conteúdo interno não
classificatório, não alternativas ou respostas independentes. A fração matemática
no segundo subitem II foi declarada pelo humano; optionCount permanece5 e labels
A–E. A imagem/fração e as notas integrais/Unicode foram preservadas sem inferência.

Doc10q4: contexto anterior compartilhado na mesma página, referência indireta
"contexto da informação". A nota original mencionava questão5; o humano esclareceu
que analisou questão4, autorizando a correção apenas dessa referência. Eventos
originais e cadeia de esclarecimento/confirmação permanecem íntegros.
Doc10q14: referência "no trecho". Doc10q21: tabela, contentKind=mixed.
Nas duas, descrição original "cinco" contradizia valor4/labelsA–D/notasquatro;
correções explícitas para "quatro" mudaram apenas a descrição, não os rótulos.

Doc11q3 e q11: imagens decorativas pertencentes às questões, conforme notas
humanas; Doc11q18: gráfico importante para respondê-la. Os cabeçalhos 3º/11º/18º
Item não foram usados pelo agente para inferir o modo ou os marcadores.
Doc12q5/q10: enunciado e alternativas textuais. Doc12q16: conteúdo misto com
subitens/imagem/fração. Nenhuma nota foi substituída por resumos deste relatório;
as notas completas estão no GT e no resumo aprovado incorporado à evidência.

## Errata congelada de paginação — Documento12/CMSP

Fingerprint `74e153f9c146d8878547d6f5fd0538953c61fcb15f17f27c6d1cfcddfadee53d`.
sourceFrozenPageCount=1 preservado; effectivePageCount=21 e
effectivePhysicalPageCount=21 aplicados explicitamente aos ranges6/11/17.
Autoridade: [errata aditiva](v5-objective-pagecount-erratum-doc10.json), SHA256
`80beb7c1f43e2266e20d7554196e852c80f84738ca27c5dd4a7a7b52abb28d6b`.
Os dois leitores e seu censo são evidência já congelada, não foram executados
novamente. Nenhum bypass do limite, alteração de PDF/metadado histórico ou
certificação de completude da prova institucional original.

## Artefatos, validação e preservação

| Artefato | SHA256 |
| --- | --- |
| [GT Batch04](ground-truth-v5-batch-04.json) | 658ae79ee99b9547c6e5de4d0a77421e7e92e01c78d7df630ad1a0704b713f08 |
| [Provenance](ground-truth-v5-batch-04.provenance.json) | 7e1f64c1b0420830fc89cac45d2964b1dc775ec07f22c0d96bacf2b5120ad14b |
| Evidência humana | b972a542fd7c32535771378e30bf3d8be61c5e119722e411ec19e37d2cbb04b0 |

Materializador/validador stdlib NOVO e isolado no diretório operacional ignorado,
sem imports/execução do Auditor e sem editar scripts congelados. Fonte e12testes
sintéticos incorporados byte-recuperavelmente à evidência; nenhum executável
novo versionado. Testes PASS antes da materialização, recibo de execução e hashes
dos códigos testados persistidos. --verify/readback determinístico e comparação
independente JavaScript dos nove campos/identidades/origins/objetos selecionados
PASS. Novos JSONs UTF8semBOM/LF/indent2/newlinefinal; escrita atômica recuperável,
recusa de sobrescrever arquivo divergente e JSON estrito sem chaves duplicadas.

Gates:documents3/questions9/uniqueQuestionIds9/unknownQuestionIds0/
crossDocumentBindings0/fingerprintMismatches0/invalidPageRanges0/
humanDecisionsReceived9/humanDecisionsConfirmed9/humanDecisionDifferences0/
unconfirmedHumanDecisions0/selectionModified=false/pageCountErratumApplied=true.
Nove análises declaradas sem assistência de IA, zero assistidas neste lote;
externalIndependenceCertified=false, sem alegar certificação externa.

96 caminhos com referências históricas independentes conferidos:inputs,
packages01–04,18arquivos publicados dos Batches01–03,38scripts e sete adjudicações,
além da errata. 877 arquivos rastreados preexistentes protegidos por guardas
físicos de início do episódio e equivalência com blobs do HEAD. Guardas físicos
prospectivos não substituem referências históricas; equivalência CRLF→LF somente
em memória não certifica igualdade física com o blob. Quatro documentos mutáveis
recebem só acréscimos, com prefixos locais e histórico Git preservados.

Batch01 mantém Q4assistida/verificada e ressalvas; Batches02/03 mantêm suas
decisões, correções e exceções históricas. Acumulado após publicação:
35declarações semIA+1assistida/verificada, não36decisões externamente certificadas.
Ressalvas de fontes, substituição/erratas pós-freeze, versão modificada e415
auxiliares not_independently_verifiable permanecem intactas, sem reabertura.

SeleçãoSHA91cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46;
provenanceSHAf78ef04d6e425e64315dd175386dcdda49b260b5abd2099c90f5558b5a3129ee;
índiceSHAa0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7;
manifest pacotesSHAe505dc206846118c6146fd9808a2ecfee745f8f4b5ba1daeda2232aa5661aff0;
lista144IDsSHA11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a.
core.autocrlf=true/configuração/attributes/PDFs/índices/código funcional intactos.
As alterações preexistentes em .gitignore/AGENTS.md/brain/00_INDEX.md permanecem
byte-preservadas fora do staging/commit, conforme autorização explícita.

## Freeze e STOP

Publicação formal condicionada ao commit `audit: freeze v5 ground truth batch 04`,
push em audit/holdout-v5-blind, HEAD remoto igual, stage vazio e nenhuma mudança
introduzida pelo episódio remanescente; somente as três alterações preexistentes
autorizadas podem permanecer. Após confirmação:36/144(25%),108restantes,
4/16batches concluídos/12restantes;groundTruthBatch04Created=true/
groundTruthHumanAdjudicationComplete=false/groundTruthFinalCreated=false/
auditorExecuted=false/metricsSeen=false/merge=false.

Compatibilidade futura GT V5/runner é gate técnico separado não resolvido;
nenhum spoofing de protocolVersion ou mudança de schema funcional legado.
STOP absoluto após publicação. Não iniciar Batch05/GTfinal/OCR/Auditor,
consultar resultados/predições/métricas V5, resolver runner ou fazer merge.
