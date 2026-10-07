# Patch05B1 — reconstructed_terminal_closure_guard

Branch: `audit/holdout-v4-postmortem-fixes`.
Base/diagnóstico publicado: `f07b046430bb799a975736749941e4fe3330637e`.
Decisão: implementar separadamente as duas causas confirmadas na
[bisseção](V4_PATCH_05B_SAFETY_BISECT.md); este subpatch trata somente q11.
Ambas surgiram ao ampliar o regression sample para os 30 IDs originais,
não como um único patch previsto pelo postmortem inicial.

## Regra geral

O adapter preserva `ObservedLine.is_reconstructed` a partir de
`source=reconstructed_from_words`. Markers explícitos e recovery geométrica
interna conservam essa evidence em candidates/clusters/selectedResponseSet.
Candidate refs continuam sendo identidade estrutural, sem texto integral;
a provenance permanece no candidate referenciado, não muda a identidade.

Completude registra `reconstructed_from_words`. Um prefixo A-C/A-D que
depende de observação reconstruída não usa ausência de continuação como
fechamento terminal: status=unknown, evidence
`reconstructed_terminal_closure_unproven`. O gate existente da Fusion bloqueia
count/labels, não apenas confidence. Mixed sets também dependem de coverage
degradada; um candidate original não certifica ausência no restante do scope.
O último label reconstruído bloqueia, assim como um prefixo cuja cobertura
depende de candidates reconstruídos anteriores; isso não inventa D/E ausentes.

A-C/A-D/A-E originais permanecem completos. A-E reconstruído pode ser
completo porque E encerra o domínio suportado, sem presumir cinco opções
para todas as questões. Gap interno/recovery aceita, CE, parent_child,
selected membership e visual-only permanecem nas políticas existentes.

Produção: somente `audit_response_holdout.py` e `audit_response_structure.py`.
Nenhuma mudança de boundary, Regions, Fusion, detector, thresholds ou OCR;
sem IDs, GT, family/year/page ou clamp como policy.

## TDD e validação

57 checks novos em `audit_response_holdout_selftest.py`: originais A-C/A-D/A-E;
reconstructed A-C/A-D/A-E; adapter/candidates/clusters/selected/evidence/refs;
mixed com terminal ou início reconstruído; resíduo terminal ambíguo;
gap interno com provenance; CE/parent_child; candidato rejeitado e visual-only.
Os controles visuais completos do Patch05A também continuam na suíte.

Antes da produção: RED, 22 falhas novas, nenhuma falha antiga.
Depois: GREEN, 373 checks do holdout; cinco suítes relacionadas PASS
(structure, regions, fusion, question_boundary, holdout) + py_compile.
Logs ignorados em `outputs/audit/postmortem-v4/patch-05b-separated-safety/`.

## Replay intermediário — somente cinco IDs

| ID | Após 05B1: classification / count / labels |
| --- | --- |
| doc-5d61be2ac853:q11 | safe_abstention / null / unknown |
| doc-56268e79f6bf:q11 | correct / 5 / A-E |
| doc-56268e79f6bf:q14 | correct / 5 / A-E |
| doc-b605f7a51fd5:q5 | partial / 5 / unknown |
| doc-f4dd01071816:q20 | safe_abstention / null / unknown |

q11 era unsafe_error/3/A-C na base Patch05A. Os quatro controles conservam
classification/count/labels; boundaries de todos os cinco são idênticos à base.
Nenhum unsafe no replay autorizado. `b1-replay.json` SHA256:
`2d580db9306c60bb3202d3363d2a822bb700f4b3a7a5161ee22eb306db8cdc2c`.
Não houve replay de q17 nesta etapa: seu defeito de aplicabilidade continua
separado, a corrigir no 05B2. Não declarar os dois casos neutralizados ainda.

## Preservação e estado

1.861 arquivos protegidos byte-preservados: todo audit/holdout (official
result/GT/manifest/index/protocol/OCR preparation), OCR caches, native render
e evidências anteriores, incluindo bisseção. Histórico CONTEXTO preservado,
somente uma linha incremental 05B1; brain curto com links.
Official result SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

`patch05B1Complete=true`; `officialAuditorExecutionCount=1`;
`officialAuditorRerun=false`; `newOCRExecutions=0`;
`V4PerformanceClaimed=false`; `V5Required=true`; merge=false.
Revealed regression sample safety result, não métrica oficial.
Próximo: 05B2 `authoritative_selected_set_requires_completeness`;
observation_complementary_capability não iniciada.
