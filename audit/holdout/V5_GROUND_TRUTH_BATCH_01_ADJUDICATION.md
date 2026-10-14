# Holdout V5 — Ground Truth Batch01, Temporada14/Episódio01

Branch `audit/holdout-v5-blind`; HEAD inicial local/remoto confirmado:
`df3e7e688a6eae00512515b3696470af378b7a5b`. Working tree/stage vazios
antes desta materialização. Escopo exclusivo:3documentos/9questões,
posiçõesR1 1–3, sem nova seleção ou modificação dos objetos congelados.

## Revisão recebida e autorização

Nove fichas coletadas interativamente, uma por vez, com observações e
confirmações de inspeção fornecidas pelo usuário revisor. Codex não examinou
visualmente os PDFs para decidir classificações, não resolveu questões e
não consultou GT anterior/predições/Auditor/métricas. PDFs integrais foram
indicados/abertos para inspeção pelo humano; páginas físicas vinculadas.

O resumo completo foi apresentado somente após as nove fichas. A confirmação
final autorizou explicitamente materializar/publicar exclusivamente Batch01,
incluindo representações estruturadas, ressalvas e ausência de mudanças de
rótulos, IDs, ordem, páginas e fingerprints.

[Evidência humana obrigatória](ground-truth-v5-batch-01.human-decisions.json)
contém18registros originais/correções/confirmações com SHA256 e bytes UTF8
recuperáveis, preflight, resumo aprovado e autorização final literal.
Os snapshots pendentes/false permanecem históricos, sem reescrita; a autorização
posterior é independente, explícita e vinculada ao resumo SHA256
`7f685dead1a63f568cf409d3cd90779e4e959845bae7f6777559facabbb1d742`.
Autorização final SHA256:
`d012108f2496eb140254f54661ecaef661d2715c50e85d6bbd44e0fd43e1a39a`.

## Exceção metodológica Q4 e compatibilidade contratual

Doc01Q4 foi inicialmente classificada com assistência de IA, examinada na
página completa4, verificada e aceita pelo revisor humano. A exceção foi
explicitamente autorizada antes da publicação, após observar essa questão;
não foi pré-registrada e não se estende a outras questões/batches.

Batch01 **não é integralmente independente**:oito classificações foram
declaradas pelo revisor como sem IA; uma é assistida/verificada pelo humano.
Essas oito são declarações do revisor, não certificação externa adicional.
Q4 tem annotationOrigin=ai_assisted_human_verified e
independentHumanAdjudicationClaimed=false. wholeBatchStrictlyIndependent=false.
humanAdjudicated=true significa aprovação/verificação humana dos nove
registros, expressamente NÃO independência estrita de todos os nove.

O plano original de coleta independente não foi silenciosamente considerado
satisfeito9/9. A decisão externa modifica somente a admissibilidade da Q4
assistida, com ressalva obrigatória. O [protocolo congelado](V5_GROUND_TRUTH_REVIEW_PROTOCOL.md)
exige declarar assistência e proíbe apresentá-la como revisão independente;
essas condições são preservadas. Não há spoofing, reescrita do protocolo nem
dispensa de condição irrenunciável de identidade/integridade/cegamento.
A ressalva deve acompanhar avaliação metodológica futura; não calcular métricas
nem interpretar impacto de performance nesta etapa.

## Registros materiais

| questionId | Página física | responseMode | optionCount/labels | markerStyle | contentKind |
| --- | --- | --- | --- | --- | --- |
| v5-doc-429b811d62a29a28:q4 | 4 | single_choice | 5/A–E | textual | text |
| v5-doc-429b811d62a29a28:q12 | 10 | single_choice | 5/A–E | textual | text |
| v5-doc-429b811d62a29a28:q18 | 14 | single_choice | 5/A–E | textual | text |
| v5-doc-9341853cd786543a:q1 | 3 | true_false | 0/[] | none | text |
| v5-doc-9341853cd786543a:q42 | 9 | true_false | 0/[] | none | text |
| v5-doc-9341853cd786543a:q98 | 17 | single_choice | 4/A–D | circled_filled | text |
| v5-doc-a37b092e0e967efc:q3 | 5 | single_choice | 5/A–E | parenthesized | mixed |
| v5-doc-a37b092e0e967efc:q21 | 19 | single_choice | 5/A–E | parenthesized | text |
| v5-doc-a37b092e0e967efc:q38 | 26 | single_choice | 5/A–E | parenthesized | text |

Todas layout=vertical. Arrays de labels preservam letras/ordem exatamente.
Doc01Q12:três afirmações internas I/II/III julgadas e referenciadas pelas
alternativas finais. Doc03Q3:três símbolos⋅ distintos em ordem, apenas elementos
internos do conteúdo, sem função de alternativas ou respostas independentes;
duas frações nos dois primeiros, contentKind=mixed conforme o revisor.
Doc01Q4/Q12/Q18:cinco controles de marcação( ) por questão. As demais têm
responseControls=[]; marcadores(A)... não foram promovidos a controles adicionais.

Q98 mantém contentKind=text para corpo/enunciado/alternativas, com dependência
do texto e duas figuras compartilhados externos explicitamente nas notes.
O protocolo não detalhava esse escopo; esclarecimento técnico posterior
confirmado pelo revisor, documentado, sem ampliar o boundary congelado.
Notas originais/Unicode e esclarecimentos aprovados copiados exatamente do resumo;
correções de tipo/grafia/papéis somente após confirmação humana, nunca por
heurística ou normalização silenciosa para satisfazer schema legado.

## Artefatos e hashes dos bytes reais

| Artefato | SHA256 |
| --- | --- |
| [GT Batch01](ground-truth-v5-batch-01.json) | b61d41a1ca5f6ad23aae5c8c9078c97218009a9e5f05ecbe512dd2ea9fc3aacb |
| [Provenance](ground-truth-v5-batch-01.provenance.json) | cd5017d14dbba1d4ccbb2c7197f4f72d0ec29c46a003820c0f03c7a0d081bfe7 |
| Evidência humana | ff7b94a82aa04534e3354759761d7febf30f5a14bdbc9156bca26dab975ab97c |

Fonte seleção SHA91cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46;
índice SHAa0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7;
manifest packages SHAe505dc206846118c6146fd9808a2ecfee745f8f4b5ba1daeda2232aa5661aff0.
Provenance registra os sete arquivos do package Batch01 e seus hashes;
nenhuma reconferência dos112arquivos de todos os batches.

## Validação, preservação e limitações

[Ferramenta isolada stdlib](v5_ground_truth_batch01.py) e
[dez testes sintéticos](v5_ground_truth_batch01_selftest.py), todos PASS antes
da materialização. Nenhum import funcional do Auditor/schema legado.
--materialize cria arquivos/checkpoint atomicamente e sem sobrescrever intactos;
--verify relê fontes/evidências/GT/provenance e exige bytes determinísticos.
Conferência independente JavaScript confirma campos completos, hashes,
Unicode/notes, exceçãoQ4, três⋅ e dependência de figuras daQ98.

Gates PASS:documents3/questions9/uniqueQuestionIds9/unknownQuestionIds0/
crossDocumentBindings0/fingerprintMismatches0/invalidPageRanges0/
selectionModified=false/humanDecisionsReceived9/humanDecisionDifferences0/
unconfirmedHumanDecisions0/auditorExecuted=false/metricsSeen=false.
Zero questões classificadas unknown; ressalvas metodológicas/contextuais não
foram apagadas nem contadas como erros ou métricas.

Entradas congeladas e sete arquivos/PDFs/template do Batch01 byte-idênticos;
38arquivos de scripts/45com sete adjudicações conferidos por referências
históricas publicadas, sem execução. Índice2136/seleção144 e código05C1/schema
intactos; nenhum pacote ou batch posterior, PDF/OCR/cache/configGit alterado.
CONTEXTO/ESTADO_ATUAL/ROADMAP/AUDITORIA_PROVAS recebem somente acréscimos,
com preservação dos prefixos brutos e conferência dos blobs staged.
Ressalvas globais/substituição/errata/fontes/versão modificada/415auxiliares
continuam históricas, sem reinvestigação ou certificação retroativa.

Anomalia operacional não bloqueante:registro bruto inicial daQ38 repetiu
materializationAuthorized=false duas vezes, com valores idênticos. Nenhum campo
humano duplicado/ambíguo; bytes originais/hash preservados na evidência, anotação
técnica explícita e artefatos finais JSON sem chaves duplicadas. Sem mudança
de rótulos por esse detalhe de serialização.

protocolVersion=holdout-v5/annotationVersion1, sem se fazer passar por V4.
Compatibilidade futura do GT V5 com o runner permanece gate separado ainda
não resolvido; nenhum runtime funcional foi alterado e nenhuma prontidão de
Auditor oficial é declarada por validar este batch.

## Freeze e STOP

Freeze formal somente com commit `audit: freeze v5 ground truth batch 01`,
push, HEAD remoto igual ao local e working tree/stage vazios. Snapshots
ready_for_introducing_commit_and_push permanecem históricos após publicação.
Somente então:PhaseBComplete=true/questionSelectionFrozen=true/
groundTruthStarted=true/groundTruthBatch01Created=true/
groundTruthQuestionsAdjudicated=9/groundTruthQuestionsRemaining=135/
groundTruthHumanAdjudicationComplete=false/groundTruthFinalCreated=false/
auditorExecuted=false/metricsSeen=false/merge=false.
9/144adjudicadas significa nove registros verificados/aprovados sob a exceção
declarada, não nove classificações estritamente independentes.

STOP após publicação. Não iniciar Batch02/GTglobal/OCR/Auditor/métricas/merge.
Próximo episódio somente com nova autorização humana explícita.
