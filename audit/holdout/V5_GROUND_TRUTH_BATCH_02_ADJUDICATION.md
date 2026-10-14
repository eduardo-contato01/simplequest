# Holdout V5 — Ground Truth Batch02, Temporada14/Episódio02

Branch `audit/holdout-v5-blind`; HEAD inicial local/remoto confirmado:
`093ab08cf83237c4ec0fbc9b33be952449eaa318`. Working tree e staging vazios
antes da materialização. Escopo exclusivo: posições R1 4–6, três documentos
e nove questões selecionadas/congeladas; nenhuma seleção ou reconstrução.

## Coleta e autorização

Nove fichas recebidas interativamente, uma questão por vez, com identificação
do PDF integral e da página física. O revisor declarou inspeção das páginas e
análise sem assistência de IA nas nove classificações. Codex não classificou
visualmente as questões, não resolveu respostas e não consultou Auditor/métricas.

O resumo completo foi apresentado após a coleta, incluindo controles, notas,
correção, distinção canônica/impressa e ressalva contextual. A autorização final
confirmou expressamente as nove fichas e a publicação exclusiva deste batch,
vinculada à versão exata do resumo SHA256:
`ffc8393f3097375d576b9315c465d16aaf9cfb1eb6db890691ff42ac9ca760f9`.
Autorização final SHA256:
`d7f58198dbefee4b030ce94e4341e52816c05a9e6c424b2f3492f8fc2b755afc`.

[Evidência humana versionada](ground-truth-v5-batch-02.human-decisions.json)
incorpora dez eventos brutos, inclusive ficha pendente e correção posterior,
com bytes UTF8 recuperáveis, tamanho, caminho e SHA256. Também incorpora
preflight, checkpoint completo, proteção pré-publicação, resumo e autorização.
Snapshots com autorização/GT=false continuam históricos; não foram reescritos.
Checkpoint completo SHA256:
`6b281206a8281e26ce1486d0d508f70cedd4a2f535610b51f0a6707c03a3ce53`.

## Nove registros aprovados

| questionId | Página física | Canônico / impresso | responseMode | optionCount / labels | layout | markerStyle | contentKind |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v5-doc-78d5d0d89420b8d3:q8 | 4 | 8 / 8 | single_choice | 4 / A,B,C,D | vertical | textual | text |
| v5-doc-78d5d0d89420b8d3:q17 | 6 | 17 / 17 | single_choice | 4 / A,B,C,D | vertical | textual | text |
| v5-doc-78d5d0d89420b8d3:q39 | 14 | 39 / 39 | single_choice | 4 / A,B,C,D | vertical | textual | mixed |
| v5-doc-906c5ae29d59a1ff:q5 | 3 | 5 / 5 | single_choice | 4 / a,b,c,d | vertical | textual | text |
| v5-doc-906c5ae29d59a1ff:q17 | 7 | 17 / 17 | single_choice | 4 / a,b,c,d | vertical | textual | text |
| v5-doc-906c5ae29d59a1ff:q28 | 12 | 28 / 8 | single_choice | 4 / a,b,c,d | vertical | textual | text |
| v5-doc-7a302456c4a6afbe:q1 | 3 | 1 / 1 | single_choice | 5 / a,b,c,d,e | vertical | textual | text |
| v5-doc-7a302456c4a6afbe:q14 | 8 | 14 / 14 | single_choice | 5 / a,b,c,d,e | vertical | textual | text |
| v5-doc-7a302456c4a6afbe:q30 | 13 | 30 / 30 | single_choice | 5 / a,b,c,d,e | vertical | textual | text |

Todos `subitems=[]`. Somente as três questões do documento05 têm quatro
controles `( )` cada, um por alternativa a–d, representados como objetos
label/role/pages/notes. As outras seis têm `responseControls=[]`. Letras e
Unicode, incluindo minúsculas e espaços das notas, copiados sem normalização.

Doc04q8 referencia texto fora do recorte; q17 tem enunciado e alternativas;
q39 contém enunciado/imagem/continuação/alternativas. Doc05q17 depende da
anedota na mesma página7; q5 e q28 têm enunciado e alternativas com controles.
Doc06q1 referencia poema na mesma página3. Doc06q14 mantém literalmente
“pressupõe-se” sobre o possível papel motivador do Texto14 precedente, externo
à questão: hipótese do revisor, não dependência comprovada. Doc06q30 tem
enunciado e alternativas. Notas completas e declarações individuais estão no GT
e na evidência; nenhuma dependência de outra página foi declarada.

Doc05q5: descrição original de cinco controles preservada no evento pendente;
esclarecimento humano corrigiu para quatro, sem alterar os demais campos.
Doc05q28 permanece canônica28/impressa8/Matemática/página12. A numeração
descontínua do Pódion e ausência histórica18–21 não autorizam renumeração ou
fabricação. Seus objetos neutros legados não tinham metadado impresso separado;
os números observados confirmados pelo revisor são metadados do GT/evidência,
sem alteração do índice ou dos objetos selecionados.

## Independência e ressalvas

Batch02: nove declarações humanas sem IA, zero assistidas; são declarações do
revisor, não certificação externa de independência. Cada claim mantém esse
escopo; externalIndependenceCertification=false e externalIndependenceCertified=false.
Nenhuma exceção do Batch01 foi transportada como autorização para este lote.
Batch01 permanece integralmente byte-idêntico, incluindo Q4 assistida/verificada,
três elementos internos⋅ daQ3 e dependência de figuras compartilhadas daQ98.
Acumulado após publicação:17declarações semIA+1assistida/verificada, não18
classificações estritamente independentes certificadas externamente.

Zero classificações `unknown`; uma ressalva contextual explícita naq14 não foi
apagada nem convertida em erro/métrica. Nenhuma ambiguidade humana pendente.
Ressalvas globais pós-freeze/errata/substituição/fontes/versão modificada e
415auxiliares not_independently_verifiable continuam preservadas, sem nova
certificação histórica ou investigação retroativa.

## Artefatos e hashes

| Artefato | SHA256 |
| --- | --- |
| [GT Batch02](ground-truth-v5-batch-02.json) | 70a78627359414c33b51165d41b6db968a642cb12ef9381dc8be662ccd44b816 |
| [Provenance](ground-truth-v5-batch-02.provenance.json) | 27f18c4f71e9a6452832a7c7465833a528c8fcc5b8fd6f42e0c4b8433076756e |
| Evidência humana | 56a8dc38ce5ea53660664008c5746e97791e4bccb06a327c3d9bb2859f37218c |

Seleção SHA25691cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46;
índice SHA256a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7;
manifest técnico SHA256e505dc206846118c6146fd9808a2ecfee745f8f4b5ba1daeda2232aa5661aff0.

## Validação e preservação

[Materializador/validador stdlib isolado](v5_ground_truth_batch02.py), sem executar
a ferramenta congelada Batch01 nem importar o Auditor. [Doze testes sintéticos](v5_ground_truth_batch02_selftest.py)
PASS antes da materialização; --verify/readback/bytes determinísticos e
conferência independente JavaScript campo a campo contra resumo/eventos PASS.
Serialização UTF8semBOM/LF/indent2/newlinefinal; escritas atômicas recuperáveis,
sem sobrescrever artefatos intactos ou produzir rótulos automaticamente.

Gates PASS:batch02Documents3/batch02Questions9/batch02UniqueQuestionIds9/
unknownQuestionIds0/crossDocumentBindings0/fingerprintMismatches0/
invalidPageRanges0/selectionModified=false/humanDecisionsReceived9/
humanDecisionsConfirmed9/humanDecisionDifferences0/unconfirmedHumanDecisions0/
auditorExecuted=false/metricsSeen=false. UnknownClassificationQuestions0;
reviewerDeclaredIndependentQuestions9/aiAssistedHumanVerifiedQuestions0,
externalIndependenceCertified=false.

71comparações de preservação em68caminhos distintos:inputs congelados, sete
arquivos package02,38scripts/sete adjudicações, todos os seis arquivos versionados
e sete arquivos package01. Batch01 e código funcional Patch05C1 intactos;
nenhum preparador16pacotes/seleção/OCR/Auditor/parserPDF foi executado.
Quatro documentos recebem só acréscimos, com prefixos brutos locais e blobs
históricos Git preservados; core.autocrlf=true, sem alteração de config/attributes.
PDFs/templates/packages/objetos selecionados não entram no commit.

Schema próprio holdout-v5, não disfarçado como V4. Compatibilidade futura do GT
V5 com o runner permanece gate separado não resolvido antes do Auditor oficial.
Validar o batch não certifica prontidão para executar o Auditor.

## Freeze e STOP

Freeze formal condicionado ao commit `audit: freeze v5 ground truth batch 02`,
push de audit/holdout-v5-blind, HEAD remoto igual ao local e worktree/stage vazios.
Após essa confirmação:PhaseBComplete=true/questionSelectionFrozen=true/
groundTruthStarted=true/groundTruthBatch01Created=true/groundTruthBatch02Created=true/
groundTruthQuestionsAdjudicated=18/groundTruthQuestionsRemaining=126/
groundTruthHumanAdjudicationComplete=false/groundTruthFinalCreated=false/
auditorExecuted=false/metricsSeen=false/merge=false.

STOP após publicação. Não iniciar Batch03/GTglobal/OCR/Auditor/métricas/merge.
