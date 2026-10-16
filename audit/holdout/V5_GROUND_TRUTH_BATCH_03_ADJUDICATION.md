# Holdout V5 — Ground Truth Batch03, Temporada14/Episódio03

Branch `audit/holdout-v5-blind`; HEAD inicial local/remoto confirmado:
`ceec02a038a7f4c0476eb1fa78f22fb59b8c719e`. Escopo exclusivo: posições R1
7–9, três documentos e nove questões selecionadas/congeladas. Nenhuma seleção,
reconstrução do índice, inspeção classificatória pelo agente ou consulta a gabarito.

## Coleta, confirmação e autorização

Nove fichas recebidas uma a uma, com PDF integral e página física identificados.
O humano declarou inspeção e análise sem assistência de IA em todas as nove.
São declarações do revisor, não certificação externa de independência.
Codex registrou as decisões e verificou consistência formal, sem adjudicar em
nome do humano, resolver questões ou consultar previsões/métricas do Auditor.

As duas primeiras fichas tiveram confirmação separada. Durante a terceira,
o revisor autorizou considerar o envio de uma ficha completa e consistente como
confirmação individual; dúvidas continuaram exigindo esclarecimento. Essa decisão
é posterior ao início da coleta, não um pré-registro; o protocolo congelado não
foi reescrito. A aprovação final das nove e a autorização de publicação foram
mantidas como gates separados e foram expressamente dadas pelo revisor.

Resumo integral aprovado SHA256:
`2d573bc5c5d8a7fb516255921452365a3ac2ddf33ad020ed5431093e63e65806`.
Autorização final SHA256:
`201a0ccdeef70d89ae2026019d978268e0db95d0bd60b329355a48d3cf3eb32e`.
Checkpoint autorizado SHA256:
`10e4cfb75622691a2f74e27881d0eb7c0fec4089ce7c1ad2a4bd68fc63290dea`.

[Evidência humana](ground-truth-v5-batch-03.human-decisions.json) incorpora
14 eventos originais/confirmados/corrigidos, preflight, checkpoint, resumo,
autorização final, duas reconciliações, autorizações de fluxo/alterações locais,
proteção pré-publicação e quatro prefixos documentais brutos recuperáveis.
Cada evento mantém bytes UTF8, tamanho e SHA256. Estados false em snapshots
anteriores permanecem históricos, não são declarações do estado após publicação.

## Nove fichas aprovadas

| questionId | Página física | Canônico / impresso | optionCount / labels | markerStyle |
| --- | --- | --- | --- | --- |
| v5-doc-9e5595dac9eb75e3:q4 | 2 | 4 / 4 | 4 / A,B,C,D | textual |
| v5-doc-9e5595dac9eb75e3:q19 | 8 | 19 / 19 | 4 / A,B,C,D | textual |
| v5-doc-9e5595dac9eb75e3:q29 | 12 | 29 / 29 | 4 / A,B,C,D | textual |
| v5-doc-c6d6158a42ac379f:q2 | 1 | 2 / 2 | 5 / a,b,c,d,e | parenthesized |
| v5-doc-c6d6158a42ac379f:q7 | 4 | 7 / 7 | 5 / a,b,c,d,e | parenthesized |
| v5-doc-c6d6158a42ac379f:q15 | 7 | 15 / 15 | 5 / a,b,c,d,e | parenthesized |
| v5-doc-0c51e49589f148bc:q4 | 3 | 4 / 4 | 5 / A,B,C,D,E | parenthesized |
| v5-doc-0c51e49589f148bc:q7 | 5 | 7 / 7 | 5 / A,B,C,D,E | parenthesized |
| v5-doc-0c51e49589f148bc:q13 | 6 | 13 / 13 | 5 / A,B,C,D,E | parenthesized |

Todas: responseMode=single_choice, subitems=[], responseControls=[],
layout=vertical, contentKind=text. Campos, notas completas e Unicode são
copiados exatamente do resumo/eventos aprovados, sem normalização ou inferência.
Parênteses das letras não foram convertidos em controles adicionais.

Doc07q4: referência direta a texto fora do recorte, pela frase "ao concluir o
texto". Doc07q19: referência indireta pela palavra "autor", texto na mesma
página, fora do recorte. Doc07q29 e as três questões do Doc08: enunciado e
alternativas conforme notas humanas. Doc09q4: referência direta ao "texto I",
externo ao recorte. Doc09q7: nota literal conserva a necessidade do trecho
anterior/lacunas e a distinção de que a questão começa depois dele; não altera
boundaries nem converte contexto compartilhado em questão adicional.
Doc09q13: referência literal "(linha...)" preservada, sem completar a observação
por inferência. Notas integrais estão no GT e no resumo incorporado à evidência.

Doc08q2: ponto em vez de vírgula na lista original preservado no evento007;
correção explicitamente autorizada no evento008, sem trocar identificadores.
Doc09q4: descrição original a–e versus labels A–E preservada no evento011;
evento012 confirma maiúsculas e corrige apenas a descrição. Nenhum campo de
classificação ou nota dessa questão foi alterado. A confusão anterior sobre a
existência da ficha3/9 e sua correção humana também permanecem nas reconciliações;
nenhuma ficha/decisão foi transferida da2/9 para a3/9.

## Artefatos e integridade

| Artefato | SHA256 |
| --- | --- |
| [GT Batch03](ground-truth-v5-batch-03.json) | bc2b23198b5b6a49dd370e4f16ea2ae4c0ed3698a1df1ac17e2bbfb70db9d83a |
| [Provenance](ground-truth-v5-batch-03.provenance.json) | 182b5bd002e13c71244a5c7408281a8f02e5a906ccc6e440ef60015b8b4badf5 |
| Evidência humana | 4a5643f0063ce47462c82f171b7cd735dd50ee429c235a2da1515423f6b44283 |

[Materializador/validador V5 isolado](v5_ground_truth_batch03.py) e
[12 testes sintéticos](v5_ground_truth_batch03_selftest.py), sem imports do
Auditor ou alteração de schema legado. Testes PASS antes da materialização;
--verify/readback e conferência independente JavaScript campo a campo PASS.
JSONs UTF8semBOM/LF/indent2/newlinefinal; gravação atômica recuperável,
recusa a sobrescrever artefatos divergentes; evidência incorporada permite
verificação posterior sem depender do diretório operacional ignorado.

Gates:3documentos/9questões/9IDs únicos, ordem e identidades exatas,
unknownQuestionIds0/crossDocumentBindings0/fingerprintMismatches0/
invalidPageRanges0/humanDecisionsReceived9/humanDecisionsConfirmed9/
humanDecisionDifferences0/unconfirmedHumanDecisions0/unknownClassificationQuestions0.
Nove declarações semIA/zero assistidas neste lote, externalIndependenceCertified=false.

Seleção SHA25691cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46;
provenance seleçãoSHAf78ef04d6e425e64315dd175386dcdda49b260b5abd2099c90f5558b5a3129ee;
índiceSHAa0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7;
manifest técnicoSHAe505dc206846118c6146fd9808a2ecfee745f8f4b5ba1daeda2232aa5661aff0;
lista144IDsSHA11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a.
Objetos selecionados iguais aos objetos canônicos, sem nova seleção ou reparo.

## Preservação e exceções delimitadas

88 comparações com referências históricas em82caminhos distintos:inputs,
package03, packages01/02,38scripts/sete adjudicações e12arquivos versionados
dos Batches01/02. Todos byte-idênticos. Além disso,871arquivos rastreados
preexistentes tiveram conteúdo comparado a blobs independentes do HEAD e
guardas físicos pré-publicação. Em135deles, CRLF→LF somente em memória foi
necessário para equivalência Git; esse resultado não é alegação de identidade
física histórica com o blob. Seus snapshots físicos protegem apenas o episódio.
Os quatro documentos de acompanhamento recebem somente acréscimos;
prefixos brutos locais e conteúdo histórico Git devem permanecer intactos.

Alterações preexistentes do usuário em .gitignore, AGENTS.md e brain/00_INDEX.md
foram confirmadas/autorizadas e preservadas fora do commit. Autorização final
permite sua permanência unstaged após publicação, em substituição ao gate
original de worktree inteiramente limpa; os demais gates não foram dispensados.
O requisito final é stage vazio e nenhuma alteração introduzida pelo episódio
remanescente, além desses três arquivos byte-preservados.

Batch01 conserva sua Q4assistida/verificada, três⋅internos e figuras compartilhadas;
Batch02 conserva correção5→4controles, q28/impressa8 e hipóteseTexto14.
Acumulado após publicação:26declarações semIA+1assistida/verificada, não27
classificações estritamente independentes externamente certificadas.
Ressalvas pós-freeze/substituição/errata/fontes/versão modificada e415auxiliares
not_independently_verifiable permanecem intactas, sem reabertura ou certificação
histórica retroativa. core.autocrlf=true/configuração/attributes preservados.

## Freeze e STOP

Freeze formal condicionado ao commit `audit: freeze v5 ground truth batch 03`,
push na branch correta, HEAD remoto igual, stage vazio e apenas as três alterações
preexistentes autorizadas na worktree. Após confirmação:27/144 (18,75%),117restantes,
3/16batches concluídos/13restantes;PhaseBComplete=true/questionSelectionFrozen=true/
groundTruthStarted=true/groundTruthBatch03Created=true/
groundTruthHumanAdjudicationComplete=false/groundTruthFinalCreated=false/
auditorExecuted=false/metricsSeen=false/merge=false.

Compatibilidade futura GT V5/runner continua gate técnico separado não resolvido;
validar este batch não autoriza o Auditor. Nenhuma execução OCR/seleção/preparador/
Auditor, consulta a previsões/métricas ou merge. STOP absoluto após publicação;
não iniciar Batch04, consolidar GTfinal ou executar novas etapas automaticamente.
