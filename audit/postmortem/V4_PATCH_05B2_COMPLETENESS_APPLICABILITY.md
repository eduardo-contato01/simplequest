# Patch05B2 — authoritative_selected_set_requires_completeness

Branch: `audit/holdout-v4-postmortem-fixes`.
Base Patch05B1: `21aa7fbf995594c6052e6fd9069246c404ca8f77`.
Diagnóstico publicado: `f07b046430bb799a975736749941e4fe3330637e`.
As duas causas distintas surgiram da ampliação do regression sample no
Patch05A e foram confirmadas na [bisseção](V4_PATCH_05B_SAFETY_BISECT.md).
05B1 trata terminal closure/provenance; 05B2 trata applicability, separadamente.

## Contrato observado, sem GT

`response_set_requires_completeness()` é compartilhado entre Structure e
Fusion. Mantém a exigência anterior single_choice/mixed; adicionalmente um
selected set autoritativo com pelo menos três candidates aceitos de
answer_marker, labels no domínio A-E, exige completude independentemente
de mode. Portanto C-D-E retorna missing_initial_label/incomplete/required=true.
B-C-D-E e gap A-C-D também não autorizam emissão. A-C/A-D/A-E originais
podem ser complete mesmo com mode unknown; isso não reclassifica mode.

A Fusion exige contrato quando a regra se aplica: contrato ausente fica
unknown/required=true; um required=false obsoleto não permite bypass de
status diferente de complete. A cópia preserva inputs e estado semântico;
confidence não substitui closure. Membership continua Patch01, incluindo
somente recovery interna previamente aceita; não promove candidato rejeitado.

C/E contextual tem dois markers, não três standard answer labels;
true_false_items/response controls/parent_child permanecem separados.
Numeric/discursive sem selected answer set e visual-only sem autoridade
textual não recebem esse gate. Ambiguidade mantém blockers existentes.

Produção: Structure + ajuste mínimo em Fusion, justificado pelo gate consumidor
mode unknown e contrato ausente/obsoleto. Nenhuma alteração de boundary,
Regions, observations, detector ou thresholds; nenhuma regra por ID, documento,
family/year/page, GT, expected count/labels, OCR, CID, glyph ou clamp.

## TDD e validação antes do commit funcional

44 checks novos em audit_response_holdout_selftest.py: seis sequências
autoritativas com mode unknown; required/status/count/labels/reason/hard gate;
suffix C/E com recovery D e mode unknown; recovery preservada;
consumer sem contrato ou com flag false, input imutável; 05B1 em mode unknown;
CE/parent_child/controles/numeric/discursive; ambiguidade e visual-only.

RED antes da produção: 25 falhas novas, demais checks passaram.
GREEN: 417 checks holdout; todas as 14 suítes existentes PASS + py_compile
de scripts audit_*.py. Logs ignorados em
`outputs/audit/postmortem-v4/patch-05b-separated-safety/`.

## Replay intermediário — somente cinco IDs

| ID | Após 05B2: classification / count / labels |
| --- | --- |
| doc-eefc3d15076e:q17 | safe_abstention / null / unknown |
| doc-5d61be2ac853:q11 | safe_abstention / null / unknown |
| doc-b605f7a51fd5:q5 | partial / 5 / unknown |
| doc-56268e79f6bf:q11 | correct / 5 / A-E |
| doc-56268e79f6bf:q14 | correct / 5 / A-E |

Nenhum unsafe; controles e boundaries idênticos à baseline Patch05A.
`b2-replay.json` SHA256:
`6e3e2552d21869e1652a6951fbd4d5e5bd63b38d327a68abaee4b31467d170f3`.

## Preservação e metodologia

1.861 arquivos protegidos byte-preservados: todo audit/holdout, GT, manifest,
index, protocol, OCR preparation/caches, native render e evidências anteriores.
Official result SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

`officialAuditorExecutionCount=1`; `officialAuditorRerun=false`;
`newOCRExecutions=0`; `V4PerformanceClaimed=false`; `V5Required=true`.
Nenhum CLI oficial/main/evaluate_manifest ou execução dos 144.

Estado no commit funcional: subpatch implementado/testado; replay final dos
30 ainda pendente, a executar somente após publicar 05B1/05B2, conforme pedido.
A conclusão do replay e UMA entrada CONTEXTO 05B2 + replay final serão
registradas depois, em fechamento somente documental, sem alterar produção.
Observation_complementary_capability não iniciada; sem merge.

## Fechamento pós-publicação — replay final original dos 30

Executado somente após commit/push dos dois subpatches funcionais:

- PATCH05B_BISECT_COMMIT = `f07b046430bb799a975736749941e4fe3330637e`.
- PATCH05B1_COMMIT = `21aa7fbf995594c6052e6fd9069246c404ca8f77`.
- PATCH05B2_COMMIT = `bc84ee4f83ee7d6a241c0b495f34b4168e2b30fb`.

Baseline: Patch05A `98bae929c8300d2a4fe4cc23678ab4c09b274bd3`,
`after-validated.json` SHA256
`d1249a2ec24ce822c00c75f088fb9deda32583760b8c69d2931850e2e8cb58f9`.
Mesmos 30 IDs originais (24 abstentions + cinco unsafe + um partial do
postmortem congelado), não os 144. GT somente no wrapper de classificação;
index neutro é autoritativo para páginas/ordem. Nenhum official runner.

| ID | Baseline classification/count/labels | Após 05B1 + 05B2 |
| --- | --- | --- |
| doc-5d61be2ac853:q11 | unsafe_error / 3 / A-C | safe_abstention / null / unknown |
| doc-eefc3d15076e:q17 | unsafe_error / 3 / unknown | safe_abstention / null / unknown |
| doc-b605f7a51fd5:q5 | partial / 5 / unknown | partial / 5 / unknown |
| doc-f4dd01071816:q20 | safe_abstention / null / unknown | safe_abstention / null / unknown |
| doc-44ea716ed9b7:q54 | safe_abstention / null / null | safe_abstention / null / null |
| doc-800c2a22f148:q1 | correct / 4 / A-D | safe_abstention / null / unknown |

`knownRevealedUnsafeTargetsBefore=2`; `knownRevealedUnsafeTargetsAfter=0`;
nos outros 28, `newUnsafeRegressionCount=0`. São resultados de segurança da
amostra revelada, não unsafe rate/precision ou métricas oficiais.

27/30 estados classification/count/labels inalterados. A-E reconstruído de
doc-56268e79f6bf:q11/q14 permanece correct/5/A-E. Cinco targets Patch04
doc-27775227a392:q1/q14, doc-3fb1e1ce24be:q32/q12 e doc-2790a3c9786b:q4
permanecem correct/5/A-E. Boundary, candidateRefs, slot counts e modes
permanecem idênticos à baseline em todos os 30; nenhuma membership nova.

Efeito conservador adicional investigado: doc-800c2a22f148:q1 possui A-D
inteiramente reconstruído por `original_line_order_ambiguous` já na baseline,
39 words/8 linhas. Provenance antes perdida passa a bloquear closure por
ausência antes de E, pela regra geral 05B1; não há erro de label/corte ou
adaptação individual. Não foi recuperado count por GT nem criada exceção para
reverter essa abstenção; originais saudáveis A-C/A-D permanecem verdes no TDD.

q17: status=incomplete/required=true, evidence missing_initial_label,
hard blocker response_set_incomplete. q11: unknown/required=true, evidence
reconstructed_terminal_closure_unproven, hard blocker
response_set_completeness_uncertain. Ambos bloqueiam count/labels, não só
confidence. Nenhuma neutralização depende de classificação hardcoded.

`final-replay.json` SHA256:
`bcc8f165137072f1e180510d86cfa25a92b985bcb8f2ff5b66fc1d5e36cefa27`.
Validação final dos controles/membership/safety e byte-preservação PASS.
Total desta etapa funcional: 40 chamadas locais, cinco 05B1 + cinco 05B2 +
30 final; nenhuma chamada extra/replay oficial ou OCR novo.

Fechamento documental posterior aos commits funcionais, sem alterar produção;
CONTEXTO recebe UMA entrada 05B2 + replay final, preservando diagnóstico e 05B1.
`patch05B1Complete=true`; `patch05B2Complete=true`;
`knownRevealedSafetyRegressionsNeutralized=true`.
Próximo: observation_complementary_capability, NÃO iniciado. V5 blind continua
obrigatório; officialAuditorExecutionCount=1, officialAuditorRerun=false,
V4PerformanceClaimed=false, merge=false.
