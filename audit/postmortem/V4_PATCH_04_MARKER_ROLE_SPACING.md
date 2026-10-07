# Patch 04 — marker_role_and_spacing

Branch: `audit/holdout-v4-postmortem-fixes`.
Base Patch 03C: `403eb0155544a867fe5f70b2b8efa2f9a024222a`. Sem merge.

## Parser e autoridade de papel

PAREN_RE agora aceita whitespace interno no mesmo domínio A-E/a-e do strong
scanner: `(A)`, `( A )`, `(a)`, `( a )`, `(  b  )`, tabs e NBSP. Preserva label,
labelCase, markerShape=parentheses, markerKind=answer_marker, remainder e offsets
span/textStart; não remove whitespace interno do corpo nem faz parsing fuzzy.
Palavras, números, labels compostos, x fora do domínio e A sozinho não entram.
Same-line scanning materializa os prefixes espaçados já considerados fortes.

Regions exclui membros do selectedResponseSet autoritativo da heurística de
lowercase antes de instruction_top. Membership é decidido por Structure e
validado pelo contrato Patch01, não recalculado espacialmente em Regions.
Membros legítimos recebem answer_option com evidence
`selected_response_set_member`; case/shape são style evidence, não papel absoluto.
Campos vazios mantêm response_field; parent_child e response_control preservados.
CE não vira single_choice por essa precedência.

_internal_enumeration e _detect_subitem_lines permanecem intactos. Sequências
lowercase não selecionadas e Roman internas permanecem subitems; sua evidence
registra internal_enumeration, ou internal_enumeration_before_instruction quando
aplicável. Parênteses não garantem resposta: concorrentes ambíguos permanecem
ambíguos pelo seletor anterior. Weak/visual/fallback não ampliam conjunto selecionado.

Somente dois módulos funcionais alterados: audit_response_structure.py (uma regex)
e audit_response_regions.py (precedência/provenance). Sem alteração de scoring,
cluster selection, completeness, boundary, word reconstruction, OCR, observations,
visual detector, Fusion ou runner. Nenhum tuning de pesos, clamp ou regra por caso.

## TDD primeiro

68 checks novos em audit_response_holdout_selftest.py, antes do código funcional.
RED=47 falhas novas; controles anteriores PASS. GREEN=68/68 novos e anteriores
PASS. Controles A-W: parser/offsets/body/strong consistency, uppercase/lowercase
compactos/espaçados, instrução posterior, lowercase interna antes de upper/lower
answer set, Roman, parent-child/controles/CE/campos, conjuntos concorrentes,
weak anchors, A-D/A-E legítimos, gap bloqueado por Patch02 e same-line scanner.
Nenhuma expectativa anterior relaxada.

As 14 suítes atuais e py_compile dos três arquivos Python alterados PASS:
structure, regions, fusion, holdout, boundary, observations, OCR content, visual
marker evidence, question index, seletores V3/V4, protocolo V4, V2 R1/R2.

## Replay diagnóstico restrito

24 IDs únicos autorizados, uma passagem com 48 chamadas pareadas base/patch.
Antes usa Structure/Regions da base carregados em memória; depois usa os módulos
atuais. Adapter e Fusion apontam ao módulo correspondente, sem modificar arquivos.
Demais camadas, boundary e fontes idênticos. Não chama main/evaluate_manifest/CLI
oficial, os 144, OCR novo, render novo ou glyph recovery. Raster usa PNG/OCR cache
existente; native usa adapter existente somente leitura. GT somente para
classificação diagnóstica, não para parsing/roles/scoring. 24 fingerprints PASS.

### Cinco alvos: classification / count / labels

| questionId | before | after | becameUnsafe |
| --- | --- | --- | --- |
| doc-27775227a392:q1 | safe_abstention / null / null | correct / 5 / A-E | false |
| doc-27775227a392:q14 | safe_abstention / null / null | correct / 5 / A-E | false |
| doc-3fb1e1ce24be:q32 | safe_abstention / null / unknown | correct / 5 / A-E | false |
| doc-2790a3c9786b:q4 | safe_abstention / null / unknown | correct / 5 / A-E | false |
| doc-3fb1e1ce24be:q12 | safe_abstention / null / unknown | correct / 5 / A-E | false |

### Structure

Todos after: cinco alternativeMarkerCandidates A/B/C/D/E, labelCase=lower,
markerShape=parentheses; um responseSetCandidate clusterId=0/size=5; selected
clusterId=0, labels=A-E, ambiguous=false, authoritative=true. Inferência after:
single_choice/high, A-E/high, expectedOptionCount=5/high. internalEnumerationCandidates
de Structure=[] antes/depois nos cinco (Roman não é cluster A-E); os quatro Roman
reais de q1 continuam explicitamente presentes em Regions como subitems.

| questionId | markers before → after | responseSetCandidates before → after (clusterId/labels/size/score) | selected before → after | mode before → after |
| --- | --- | --- | --- | --- |
| doc-27775227a392:q1 | 0 → 5 | [] → 0/A-E/5/36.808 | nenhum → A-E autoritativo | unknown → single_choice |
| doc-27775227a392:q14 | 0 → 5 | [] → 0/A-E/5/35.9697 | nenhum → A-E autoritativo | unknown → single_choice |
| doc-3fb1e1ce24be:q32 | 0 → 5 | [] → 0/A-E/5/36.101 | nenhum → A-E autoritativo | unknown → single_choice |
| doc-2790a3c9786b:q4 | 5 A-E → 5 A-E | 0/A-E/5/35.5654 → mesmo | A-E autoritativo → mesmo | single_choice → mesmo |
| doc-3fb1e1ce24be:q12 | 1 E → 5 A-E | 0/E/1/31.6 → 0/A-E/5/35.7705 | nenhum → A-E autoritativo | unknown → single_choice |

Markers before existentes (q4/q12) já eram lower/parentheses. Os scores diferem
somente porque novos markers observados entram; função/pesos não mudaram.

### Regions e Fusion

response_control=0 e response_field=0, Regions blockers=[] antes/depois nos cinco.
After: cinco membros selecionados são answer_option, nenhum deles subitem;
count=5/labels=A-E, agreement=partial, Fusion blockers=[].

| questionId | slots before → after | answer_option before → after | subitem before → after | selected member slots before → after | weak anchors before → after | Fusion agreement before → after | Fusion blockers before → after |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doc-27775227a392:q1 | 9 → 9 | 0 → 5 | 9 → 4 | 0 → 5 | 0 → 0 | partial → partial | missing_marker_observation → [] |
| doc-27775227a392:q14 | 5 → 5 | 0 → 5 | 5 → 0 | 0 → 5 | 0 → 0 | partial → partial | missing_marker_observation → [] |
| doc-3fb1e1ce24be:q32 | 8 → 5 | 3 → 5 | 5 → 0 | 0 → 5 | 3 → 0 | strong → partial | weak_anchor_only → [] |
| doc-2790a3c9786b:q4 | 5 → 5 | 2 → 5 | 3 → 0 | 5 → 5 | 0 → 0 | partial → partial | [] → [] |
| doc-3fb1e1ce24be:q12 | 5 → 5 | 1 → 5 | 4 → 0 | 0 → 5 | 0 → 0 | partial → partial | [] → [] |

q32 strong anterior não autorizava count por weak_anchor_only. After partial
reflete provenance textual/espacial derivada, não confirmação independente.

### Regressões

Todos os 19 não-alvos mantiveram classification/count/labels e boundary idênticos.
Rejeitados usados downstream=false em todos os 24; nenhum novo unsafe.

- Patch03C (5): q11/q14 correct/5/A-E; q5/q2 safe_abstention/null/unknown;
  q54 safe_abstention/null/null. unsafeRegressionCount=0.
- Patch03B (2): q25 correct/5/A-E; q20 safe_abstention/null/null. unsafeRegressionCount=0.
- Patch03A (6): todos correct/5/A-E; printed/canonical/grammars preservados.
  unsafeRegressionCount=0.
- Patch01/02 (6): q16/q23 safe_abstention/null/unknown; q15/q40 correct/5/A-E;
  q1 correct/4/A-D; raster doc-f4dd01071816:q20 safe_abstention/null/unknown.
  unsafeRegressionCount=0. q20 conservador não foi adaptado para voltar a correct.
- q54 CID continua fora do escopo: sem decoding/glyph/OCR/render novo, boundary
  current_marker_not_found. Não se presume glyph pelo índice.

Traces completos por camada/ID e logs ignorados:
outputs/audit/postmortem-v4/patch-04-marker-role-spacing/diagnostic-replay.json.
SHA256: `8b3965ff18079a46f4c9d31bea9a0907ea59f18ad049b8b5db8d92a70fac0bc9`.

## Preservação, metodologia e estado

1.793 arquivos protegidos byte-idênticos: todo audit/holdout, caches OCR e todos
os relatórios/evidências dos patches anteriores. Resultado/GT/manifest/index/
protocol/OCR preparation intactos. Resultado oficial SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

Diff funcional sem IDs/famílias/páginas/textos de questões, GT, expected counts
ou clamp. Clustering/scoring, seleção safety e funções de enumeração anteriores
intactos. Lowercase permanece evidência com posição, nunca autoridade contra
membership selecionado. git diff --check PASS. Brain curto; CONTEXTO preservado
com exatamente uma entrada incremental, sem reescrever histórico.

officialAuditorExecutionCount=1; officialAuditorRerun=false; newOCRExecutions=0;
V4PerformanceClaimed=false; V5Required=true. V4 revelado é desenvolvimento/regressão,
**not an unbiased evaluation**. Resultados locais não são métricas pós-patch;
nenhuma claim de precision, coverage, unsafe rate ou ganho percentual.

patch04Complete=true. Próximo separado=visual_and_observation_recovery
(visual_marker_evidence / observation complementary), não iniciado.
V5 blind obrigatório para avaliação imparcial. Sem anomalia restante neste escopo;
limites conservadores q20/q54 preservados. Sem merge.
