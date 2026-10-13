# V5 — 16 pacotes neutros para revisão humana de Ground Truth

Temporada13. Branch audit/holdout-v5-blind; HEAD inicial local/remoto confirmado
`1605ff5a07cfcbfd5b11b161422bb7eb27398907`, stage/working tree vazios.
Preparação mecânica concluída:16pacotes/48documentos efetivos/144questões,
três documentos/nove questões por batch, na ordem R1 selecionada. Nenhum GT
preenchido, decisão humana importada/simulada, visualização PDF, OCR ou Auditor.

[Protocolo humano](V5_GROUND_TRUTH_REVIEW_PROTOCOL.md),
[preparador recuperável](v5_prepare_gt_review_packages.py),
[testes sintéticos](v5_prepare_gt_review_packages_selftest.py) e
[manifest técnico completo](v5-gt-review-batches-manifest.json).

Manifest técnico SHA256:
`e505dc206846118c6146fd9808a2ecfee745f8f4b5ba1daeda2232aa5661aff0`.
Este manifest registra todos os112arquivos:48PDFs integrais+64auxiliares,
nome/caminho/tamanho/hash por arquivo e provenance das48fontes originais.
Nenhum fallback foi necessário. Todos os fingerprints das cópias coincidem
com os canônicos. PDFs e auxiliares permanecem ignorados, não entram no commit.
Inventário de cada batch contém seis arquivos; seu hash próprio está no
manifest técnico/checkpoint pai. FILES_TO_UPLOAD.txt relaciona os sete arquivos.

## Inputs imutáveis e cobertura

| Fonte | SHA256 |
| --- | --- |
| manifest-v5-questions-frozen.json | 91cd40933a02542d35f41e889c8754873bf92ea6ff5591f079eb3880b5ca4a46 |
| manifest-v5-questions-frozen.provenance.json | f78ef04d6e425e64315dd175386dcdda49b260b5abd2099c90f5558b5a3129ee |
| question-index-v5-final.json | a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7 |
| Lista compacta ordenada de144IDs | 11a9db71ca167739dc6ef52c54e12ccd645789f66e05e1039c86c227d3b76e6a |

Índice48documentos/741páginas/2136objetos preservado, seleção não reexecutada.
Bindings ID+fingerprint, objetos exatos, ranges físicos efetivos e ordem PASS.
BatchNN ocupa posições R1 3*(NN-1)+1 até3*NN, NN=01...16.
Cobertura48/144 completa/disjunta, sem reorder/exclusão/substituição/sorteio.

Diretórios locais:outputs/audit/holdout/v5-ground-truth-batch-01-review/ até
outputs/audit/holdout/v5-ground-truth-batch-16-review/, individualmente listados
no manifest técnico com IDs e hashes. Cada contexto contém somente identidade,
páginas físicas, localização do PDF, inputs congelados e ressalvas de fonte.
Cada template contém nove registros vinculados e todos os nove campos humanos
null. Null aqui é não anotado, não uma resposta ou decisão de incerteza.
Os16templates estão vazios; humanAdjudicated=false em todos.

## Execução, recuperação e conferências

Dez self-tests sintéticos PASS antes de operar sobre fontes reais: bindings
com ordens diferentes, ordem/duplicata, objeto alterado/range inválido, campos
vazios/neutralidade,16partições/retomada sem reescrita, progresso parcial/pending,
drift sem fallback, fonte ausente/fallback byte-idêntico, tampering sem overwrite,
UTF8semBOM/idempotência. Sem corpus/GT/Auditor nos fixtures sintéticos.

Uma execução --prepare completou os16batches com ledger/hash imediato e
checkpoint atômico por batch em outputs/audit/holdout/v5-ground-truth-preparation/.
--verify releu todos os112arquivos antes da publicação, comparando payloads
determinísticos de contexts/templates, fingerprints48/48 e manifest/checkpoint.
Segunda conferência independente em JavaScript confirmou os112hashes/tamanhos,
48IDs documentais únicos/144IDs de questões únicos e16templates sem decisões.
Checkpoint operacional é necessário à recuperação e deve ser retido; PDFs,
contextos/templates/listas/inventários são evidência essencial hash-vinculada.

Gates PASS:reviewPackagesPrepared=16/documentsCovered=48/
selectedQuestionsCovered=144/uniqueQuestionIds=144/missingQuestions=0/
duplicateQuestionIds=0/documentFingerprintMismatches=0/invalidPageRanges=0/
labelsAutoFilled=0/humanDecisionsImported=0/groundTruthBatchesCreated=0/
groundTruthFinalCreated=false/auditorExecuted=false/metricsSeen=false.

## Preservação, ressalvas e compatibilidade

103referências relevantes publicadas conferidas; PDFs originais, sete
adjudicações, índice/seleção, protocolos e código funcional congelado intactos.
Quatro documentos recebem somente adições:CONTEXTO/ESTADO_ATUAL/ROADMAP/
AUDITORIA_PROVAS. Prefixos brutos locais preservados integralmente; staging
deve conservar prefixos históricos Git, sem alteração persistente de endings
ou configuração. Não há nova certificação histórica dos415auxiliares antigos.

Substituição efetiva global22 e timing pós-freeze/performance-blind transportados;
global21 frozen1/efetivo21; global8 q1–17/q22–30 sem fabricar18–21; fontes
incompletas/integridade original inconclusiva; global48 versão modificada/PDF
disponível congelado. Ressalva técnica pdfinfoReportedFileSize0 do substituto
permanece não bloqueante, causa indeterminada, sizeBytes182017 preservado.
415auxiliares histórica=not_independently_verifiable/
historicalByteIdentityVerified=false, preservação prospectiva sob decisão já
publicada; exceção não reaberta nem certificada retroativamente.

Schema próprio neutro V5, sem alterar scripts/audit_holdout_schema.py nem
mascarar V5 como V4. Compatibilidade/integrabilidade do FUTURO GT preenchido
V5 continua gate técnico separado e não resolvido, antes do Auditor oficial.
Revisão estrutural assistida anterior não é GT humano independente; V4 usado
somente como referência de contrato/processo, nunca fonte de rótulos.

## Publicação e STOP

Snapshot materializado antes do commit. Freeze formal pelo commit
`audit: prepare v5 human ground truth review packages`, push da branch e HEAD
remoto igual ao local, working tree/stage vazios. Estados após publicação:
PhaseBComplete=true/questionSelectionFrozen=true/
groundTruthReviewPackagesPrepared=true/groundTruthHumanAdjudicationComplete=false/
groundTruthCreated=false/auditorExecuted=false/metricsSeen=false/merge=false.

STOP após publicação. Próximo passo somente com nova autorização:adjudicação
humana independente do Batch01, três documentos/nove questões. Nenhum GT
preenchido/final, OCR, Auditor, métrica ou merge iniciado automaticamente.
