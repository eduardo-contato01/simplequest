# Patch 03B — neutral_boundary_scope_and_column_peers

Base Patch 03A: `9e488286fa5b87a4d42e08ebd3d3b5fdf666f3b6`.
Branch: `audit/holdout-v4-postmortem-fixes`. Sem merge.

## Problema e decisão arquitetural

Um marker numérico global não prova uma questão paralela. Conteúdo de referência
ou matemática podia gerar x-limits falsos por distância X/alinhamento Y, removendo
a região real. Agora boundary 2D exige conjuntamente:
identidade index-backed + match target-aware único + paralelismo geométrico.

`compute_question_boundary(..., document_questions=None)` recebe opcionalmente
as questões neutras do documento. Runner propaga index_questions(index_document)
pelos caminhos native e OCR até `_run_with_boundary`; não propaga GT como contexto.
Não há mudança de classificação, response Structure/Regions/Fusion ou observação.
Chamadores antigos continuam aceitos; sem contexto não há peer verificado e não
se faz fallback a markers globais para provar coluna. Current/next continuam
usando suas identidades e os gates anteriores.

`verifiedQuestionStarts` resolve todas as entries com pageStart igual à página
atual pelo matcher 03A já existente. Cada diagnóstico contém questionId,
canonicalQuestionNumber, observedQuestionNumber, numberSource, matchGrammar,
matchCount, status (unique/missing/ambiguous) e marker quando único.
Somente unique, distinto da current question, pode alimentar a inferência.
Não se escolhe ocorrência ambígua pela proximidade; indexar um número não valida
qualquer ocorrência desse número no corpo. Peers podem ser anteriores ou posteriores
na ordem documental; não se restringem ao next_question.

Os critérios/thresholds geométricos de `_infer_parallel_column_limits` permanecem
intactos, mas recebem somente os peers verificados. Colunas reais continuam
funcionando; peers válidos nos dois lados continuam produzindo reliable=false /
parallel_columns_multiple_sides. Next marker conserva a autoridade para bottom
vertical, com os critérios de mesma coluna anteriores.

Quando two_column é comprovado, `columnEvidence` registra peerQuestionId,
peerCanonicalQuestionNumber, peerObservedQuestionNumber, peerNumberSource,
peerMatchGrammar, peerMarker e evidências frozen_index_same_page,
unique_target_match, parallel_x_separation, parallel_y_alignment.
Sem prova de coluna, columnEvidence e columnLimits ficam null. Ambiguidade do peer
não invalida automaticamente current; next/membership/completude continuam gates
independentes. Não há regra nova de resposta para compensar scope.

Arquivos funcionais alterados somente: `scripts/audit_question_boundary.py` e
`scripts/audit_response_holdout.py` (propagação mínima de contexto). Gramática global,
matcher/identidade 03A, filtros espaciais e indexador inalterados. Sem reconstrução
por words, OCR resegmentation, header reconstruction, marker role/spacing, visual
recovery, stitching ou uso de resposta/GT na decisão de coluna.

## TDD primeiro e suítes

Novos controles antes do código funcional em audit_question_boundary_selftest.py:
RED completo=33 falhas novas, nenhuma anterior; GREEN=44 checks novos PASS.
Controles A-M: duas colunas reais nos dois sentidos da ordem; números não indexados;
referência numérica duplicada; entry de outra página; peer printed versus canonical;
ordinal Item e keyword separator; distância Y/X insuficiente; peers dos dois lados;
bottom vertical preservado apesar de falso peer; missing/ambiguous diagnosticados.
Spies provam propagação de contexto pelos caminhos native e raster do runner.

O helper de integração do selftest passa o contexto completo quando a API existe;
o teste explícito de presença da API falha em RED. As expectativas anteriores de
recorte, duas colunas e count não foram relaxadas. Um controle adicional mistura
duas response clusters após não selecionar um peer ambíguo: os gates existentes
abstêm count; não foi necessário outro patch de segurança.

Todas as 14 suítes PASS: structure, regions, fusion, holdout, boundary, observations,
OCR content, visual marker evidence, question-index, seletores V3/V4, protocolo V4,
V2 R1/R2. py_compile dos dois módulos funcionais e selftest PASS.

## Replay diagnóstico — 19 IDs únicos

38 chamadas locais pareadas: antes com boundary/runner do commit base carregados
em memória, depois com o patch; demais camadas idênticas. Sem CLI oficial, main,
evaluate_manifest, OCR novo ou execução dos 144. GT somente para classificação
no wrapper diagnóstico, não como input da decisão funcional. V4 já revelado é
regression behavior, não avaliação imparcial.

### Dois targets Patch03B

| questionId | mode antes/depois | column x-limits antes/depois | classification/count/labels antes/depois |
| --- | --- | --- | --- |
| doc-3e395d355d2c:q25 | two_column → vertical | [162.505,595.32] → null | safe_abstention/null/null → correct/5/A-E |
| doc-b605f7a51fd5:q20 | two_column → vertical | [0,191.44983351503598] → null | safe_abstention/null/null → safe_abstention/null/null |

Em ambos: reliable=true antes/depois; falsePeerUsedAfter=false; becameUnsafe=false.
AfterPeerMarker=null e afterColumnEvidence=null porque não há split comprovado.

- q25: beforePeerMarker era `23).`, número 23, page=27, top=564.9784, x0=56.64;
  side=right, split=162.505. O match de q23 agora registra ambiguous/matchCount=2;
  nenhum dos dois é escolhido. q24 é unique, mas não paralelo; x-limit falso removido.
- q20: beforePeerMarker era `1 6 8`, número 1, page=14, top=186.39792251572067,
  x0=355.89966703007195; side=left, split=191.44983351503598. Somente q20 possui
  pageStart nessa página, sem entry paralela; marker de conteúdo não pode ser peer.
  Ainda há lacuna visual/symbolic-control, que não foi corrigida nesta etapa.

2/2 falsos column peers neutralizados neste replay diagnóstico. Isso não é
coverage, recovered count global ou recovery percentage. Correct não era requisito.

### Seis regressões Patch 03A

Todos mantêm reliable=true, mode=vertical e resultado inalterado:

| questionId | classification/count/labels antes/depois |
| --- | --- |
| doc-f03e7d17eec1:q20 | correct/5/A-E |
| doc-a1ddc006ef56:q23 | correct/5/A-E |
| doc-bb62e60cf7ed:q27 | correct/5/A-E |
| doc-6dde932fb681:q19 | correct/5/A-E |
| doc-6dde932fb681:q7 | correct/5/A-E |
| doc-1693ea690bbb:q14 | correct/5/A-E |

unsafeRegressionCount=0; canonical/printed e gramática 03A preservados.

### Cinco não-alvos Patch 03C

| questionId | classificação/count/labels antes/depois |
| --- | --- |
| doc-56268e79f6bf:q11 | safe_abstention/null/null |
| doc-56268e79f6bf:q14 | safe_abstention/null/null |
| doc-f4dd01071816:q5 | safe_abstention/null/null |
| doc-c41ddc7b55ec:q2 | safe_abstention/null/null |
| doc-44ea716ed9b7:q54 | safe_abstention/null/null |

Todos permanecem reliable=false/current_marker_not_found, mode=vertical;
unsafeRegressionCount=0. Nenhuma melhoria incidental, adaptação ou reconstrução.

### Seis safety regressions Patches 01/02

| questionId | classificação/count/labels antes/depois |
| --- | --- |
| doc-42af2b3d2b27:q16 | safe_abstention/null/unknown |
| doc-cef618be31e6:q23 | safe_abstention/null/unknown |
| doc-cf6b56e7abd7:q15 | correct/5/A-E |
| doc-eefc3d15076e:q40 | correct/5/A-E |
| doc-f4dd01071816:q20 | correct/4/A-D |
| doc-800c2a22f148:q1 | correct/4/A-D |

Todos inalterados, mode=vertical; unsafeRegressionCount=0. Nenhum candidato rejeitado
usado downstream; contratos membership/completude intactos.

Traces completos (before/after boundaries, peers, evidence, classification/count/labels)
e logs ignorados em outputs/audit/postmortem-v4/patch-03b-boundary-scope-columns/.
SHA256 de diagnostic-replay.json:
`58cfa0eed064e8d270e87410e0e8951cacc0b0196bab7b10d9755ec56b8b02a3`.

## Preservação e auditoria do diff

1.736 arquivos protegidos byte-idênticos: todo audit/holdout, caches OCR, evidências
anteriores e artefatos locais dos Patches 01/02/03A. Resultado/GT/manifest/index/
protocol/OCR preparation intactos. Resultado oficial SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

Diff funcional sem IDs/casos/família/ano/página hardcoded, filtros específicos de
matemática, count/labels/GT como regra. Parsers globais e target-aware existentes,
funções geométricas e thresholds inalterados. Classificação e camadas de resposta
não mudam. git diff --check PASS; CONTEXTO preservado com uma linha incremental;
brain registra somente estado/decisão arquitetural e links.

officialAuditorExecutionCount=1; officialAuditorRerun=false; V4PerformanceClaimed=false;
V5Required=true. Nenhuma métrica/estimativa pós-patch. V4 é not an unbiased evaluation.

Patch03BComplete=true. Próximo separado: neutral_boundary_word_line_reconstruction
(03C), ainda não iniciado. Boundary inteiro não concluído; cinco casos de header
reconstruction continuam pendentes. Sem merge; sem anomalias restantes neste escopo.
