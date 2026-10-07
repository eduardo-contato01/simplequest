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
