# Patch 03A — neutral_boundary_identity_and_grammar

Base Patch 02: `a1ded90cbba3232565cb102ddd279e9e684ffb7e`.
Branch: `audit/holdout-v4-postmortem-fixes`. Escopo identity/grammar, sem merge.

## Contrato e escopo estrito

O frozen index continua autoritativo para questionId, ordem, páginas, identidade
canônica e metadados impressos. `_observed_question_number` usa printedQuestionNumber
válido; na ausência/invalidez, usa questionNumber. Inteiros positivos na faixa do
indexador e strings de dígitos são válidos; bool, float, zero e texto misto não são.
Identidade canônica, ordem, section e índice não são alterados. A mesma política
é aplicada à questão atual e à próxima em ordem documental.

Boundary retorna canonicalQuestionNumber, observedQuestionNumber e numberSource
(canonical/printed); currentMarker e nextMarker também carregam matchGrammar e
leadingDecorationNormalized, além do texto original e coordenadas observadas.
O número canônico permanece em questionNumber; matching usa identidade impressa.

O matching target-aware conhece somente número esperado e página do índice.
Não recebe count, labels, response mode ou conteúdo do GT. Gramáticas ancoradas:

- `legacy_keyword`: Questão/Questao/Item + número, mantendo acento/case legados;
- `keyword_separator`: keyword + hífen/en dash/em dash/dois-pontos + número;
- `ordinal_item`: número + º/°/.º antes de Item, ancorado no começo;
- `numeric_separator`: número + separador, inclusive sentença iniciada por A-E;
- `legacy_bare_numeric`: fallback numérico legado, sem ampliar sua gramática.

PUA (categoria Unicode Co) e bullets/setas decorativos explícitos só são ignorados
num prefixo exclusivamente decorativo imediatamente anterior a keyword reconhecido.
Não se remove decoração do corpo nem se altera a observação original. References
internas a ITEM não são headers; keyword não pode buscar número após palavras
intermediárias. A regra numérica conserva rejeição de parent-child com dash + A-E,
decimais e headers numéricos repetidos, sem fuzzy numeric substitution.

Zero candidatos => current/next_marker_not_found; múltiplos candidatos, inclusive
gramáticas diferentes, => current/next_marker_ambiguous e reliable=false. Não há
escolha silenciosa por proximidade. Uma linha que satisfaz mais de uma gramática
gera um único candidato, evitando duplicar o mesmo header.

Arquivo funcional alterado somente: `scripts/audit_question_boundary.py`.
Global detect_question_markers e `_infer_parallel_column_limits` permanecem intactos;
variantes target-aware não são promovidas a peers globais. Sem redesign de colunas,
scope, word reconstruction, OCR/resegmentação, marker role/spacing, observation ou
stitching multipágina. Indexador, Structure, Regions, Fusion e runner não alterados.

## TDD primeiro

58 checks novos em `scripts/audit_question_boundary_selftest.py`, antes de alterar
código funcional. RED completo: 46 falhas novas, nenhuma nos controles existentes.
GREEN: os 58 novos e os controles anteriores PASS. Cobertura A-O: canonical normal,
printed distinto/next impresso, variantes keyword/ordinal/PUA, texto original,
numeric + A partir/Basta/Como/Dado/Entre, parent-child, referências internas,
header com número errado, duplicatas atuais/próximas, reset por página e metadados
congelados preservados. Inclui guardas de decimal e printed inválido.

A primeira tentativa do RED foi interrompida por encoding cp1252 do console ao
imprimir PUA, antes de terminar os testes. Executar Python em modo UTF-8 completou
o RED antes de qualquer mudança funcional; sem mudança de conteúdo para contornar.

As 14 suítes existentes PASS: structure, regions, fusion, holdout, boundary,
observations, OCR content, visual marker evidence, question-index, seletores
V3/V4, protocolo V4 e V2 R1/R2. py_compile de boundary e selftest PASS.

## Replay diagnóstico restrito

19 IDs únicos autorizados; 38 chamadas locais pareadas (base e patch). Antes usa
o módulo boundary do commit base carregado em memória; todas as outras camadas
são iguais, incluindo Patches 01/02. Depois usa o boundary atual. Não chama main,
CLI oficial ou evaluate_manifest; sem OCR novo ou execução dos 144. GT só é usado
pelo wrapper para classificação diagnóstica, nunca pelo matching funcional.

### Seis targets Patch03A=true

Em todos: beforeBoundaryReliable=false, beforeReason=current_marker_not_found;
afterBoundaryReliable=true, afterReason=ok; becameUnsafe=false.

| questionId | matchGrammar | numberSource | before classification/count/labels | after classification/count/labels |
| --- | --- | --- | --- | --- |
| doc-f03e7d17eec1:q20 | keyword_separator | canonical | safe_abstention/null/null | correct/5/A-E |
| doc-a1ddc006ef56:q23 | numeric_separator | canonical | safe_abstention/null/null | correct/5/A-E |
| doc-bb62e60cf7ed:q27 | numeric_separator | printed | safe_abstention/null/null | correct/5/A-E |
| doc-6dde932fb681:q19 | ordinal_item | canonical | safe_abstention/null/null | correct/5/A-E |
| doc-6dde932fb681:q7 | ordinal_item | canonical | safe_abstention/null/null | correct/5/A-E |
| doc-1693ea690bbb:q14 | legacy_keyword | canonical | safe_abstention/null/null | correct/5/A-E |

q27 conserva canonical=27/observed=7; q14 registra leadingDecorationNormalized=true,
também na próxima questão decorada quando carregada. São 6/6 target boundaries
reconhecidos neste replay diagnóstico, **não coverage ou ganho de performance**.
Boundary reconhecido não garante emissão segura em outros casos.

### Sete não-alvos (Patch 03B/03C)

| questionId | reliable antes/depois | classificação/count/labels antes/depois |
| --- | --- | --- |
| doc-3e395d355d2c:q25 | true/true | safe_abstention/null/null, inalterado |
| doc-b605f7a51fd5:q20 | true/true | safe_abstention/null/null, inalterado |
| doc-56268e79f6bf:q11 | false/false | safe_abstention/null/null, inalterado |
| doc-56268e79f6bf:q14 | false/false | safe_abstention/null/null, inalterado |
| doc-f4dd01071816:q5 | false/false | safe_abstention/null/null, inalterado |
| doc-c41ddc7b55ec:q2 | false/false | safe_abstention/null/null, inalterado |
| doc-44ea716ed9b7:q54 | false/false | safe_abstention/null/null, inalterado |

unsafeRegressionCount=0. Os dois scopes de coluna conhecidos ainda são indevidamente
reliable; não foram reparados nem certificados por este patch. Page/column limits
dos sete permanecem iguais aos da base.

### Seis safety regressions dos Patches 01/02

| questionId | classificação/count/labels antes/depois |
| --- | --- |
| doc-42af2b3d2b27:q16 | safe_abstention/null/unknown, inalterado |
| doc-cef618be31e6:q23 | safe_abstention/null/unknown, inalterado |
| doc-cf6b56e7abd7:q15 | correct/5/A-E, inalterado |
| doc-eefc3d15076e:q40 | correct/5/A-E, inalterado |
| doc-f4dd01071816:q20 | correct/4/A-D, inalterado |
| doc-800c2a22f148:q1 | correct/4/A-D, inalterado |

unsafeRegressionCount=0; rejeitados não usados downstream. Gates de membership e
completude preservados. Nenhum novo patch de resposta para mascarar erro de boundary.

Artefatos/logs ignorados em `outputs/audit/postmortem-v4/patch-03a-boundary-identity-grammar/`.
SHA256 de diagnostic-replay.json:
`5540824bb0faa4b05cf8c867e18e868ea85de1c2196e416147965fac3bf2f158`.

## Preservação, diff e metodologia

1.714 arquivos protegidos byte-idênticos: todo audit/holdout, caches OCR, evidência
do postmortem e artefatos locais dos Patches 01/02. GT/manifest/index/protocol e
preparação OCR intactos. Resultado oficial SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

Diff funcional sem document IDs/question IDs V4, família/ano/página específicos,
strings de casos ou GT como regra. Código de colunas/filtragem, gramática global
e módulos não autorizados permanecem inalterados; git diff --check PASS.
CONTEXTO preservado com uma entrada incremental; brain recebe somente decisões
arquiteturais/estado corrente e links, sem diário de execução.

officialAuditorExecutionCount=1; officialAuditorRerun=false; V4PerformanceClaimed=false;
V5Required=true. V4 revelado é **not an unbiased evaluation**. Nenhuma métrica
agregada/estimativa de precision, coverage, unsafe rate ou recovery percentage.

Patch03AComplete=true. Próximo separado: `neutral_boundary_scope_and_column_peers`
(Patch 03B), seguido da reconstrução por words/linhas (03C). Boundary inteiro não
está concluído; demais famílias e V5 blind permanecem pendentes. Sem merge.
