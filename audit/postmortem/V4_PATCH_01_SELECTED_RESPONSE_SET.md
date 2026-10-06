# Patch 01 — selected_response_set_contract

Base: `07a40333ade4d1a027d6f6ef39eff55e08875fe8` (postmortem concluído).
Branch: `audit/holdout-v4-postmortem-fixes`. Patch funcional generalizável, sem merge.

## Contrato e escopo

Structure selecionava um cluster, mas Regions e Fusion voltavam a consumir answer
candidates brutos. Agora `selectedResponseSet` expõe clusterId, labels, ambiguous,
candidateRefs e candidates sem texto integral. A identidade usa clusterId, page,
lineIndex, ordinalWithinLine, label e spanWithinLine. Labels incluem somente
candidatos explícitos selecionados e recovery já aceito pela política existente.

O contrato só é autoritativo com cluster existente e seleção não ambígua (incluindo
ambiguidade de layout). O adapter conserva apenas answer markers desse conjunto;
Regions aplica o mesmo filtro, não acrescenta opções visuais/fallback não associadas
e preserva controles, campos e subitems. Fusion usa o mesmo conjunto para contagem
estrutural/conflitos e valida membership dos slots e observações. Provenance com
clusterId, candidateRef, selectedResponseSetMember e recovered chega até os slots
fundidos; refs de slots rejeitados ficam disponíveis como diagnóstico.

Seleção ambígua mantém candidatos concorrentes e blocker `competing_response_sets`,
sem count seguro. Sem contrato, permanece a compatibilidade legada. Recovery
continua exigindo sequence_gap + alignment + spatial_cluster e bbox válido, além
de membership no conjunto selecionado. Não houve mudança de parser, clustering,
score, threshold, boundary, OCR ou capacidade de observação. Sem IDs, textos,
famílias, anos ou páginas V4 no código funcional; nenhum clamp de count para 4/5.

Arquivos funcionais: `scripts/audit_response_structure.py`,
`scripts/audit_response_regions.py`, `scripts/audit_response_fusion.py` e
`scripts/audit_response_holdout.py`.

## TDD e não regressão

Testes sintéticos adicionados primeiro em `audit_response_holdout_selftest.py`,
exercitando Structure → adapter → Regions → Fusion. RED antes de qualquer edição
funcional: 23 checks novos falharam; checks antigos passaram. Reproduções incluem
6/A-E com falso A anterior, 5/A-E com footer após A-D, count_conflict artificial
por inline e ausência de bloqueio da ambiguidade estrutural. Logs locais ignorados
em `outputs/audit/postmortem-v4/patch-01-selected-response-set/`.

GREEN depois: 57 checks novos, controles A-F, A-C/A-D/A-E reais, identidade inline/ordinal,
internal enumeration como subitem, parent_child/CE/response_control preservados,
recovery válida, recovery incompleta ou de outra página rejeitada, label ausente
não inventada, consumer direto com input stale e observação rejeitada fundida.
Compilação dos quatro módulos funcionais e dois selftests alterados: PASS.

As 14 suítes existentes passaram: response structure, regions, fusion, holdout;
question boundary; observations; OCR content; visual marker evidence; question
index; seletores V3/V4; protocolo V4; V2 R1/R2.

Alteração adicional justificada: `scripts/audit_question_boundary_selftest.py`
é teste de integração existente e precisava passar o novo contrato. Seus três
controles sem recorte agora exigem abstention em vez de reproduzir overcounts.
O controle multipágina expõe uma limitação preexistente da Structure: clustering
por página seleciona A-B, deixando C-E em outro cluster. O novo contrato produz
count=null em vez de unir silenciosamente esses clusters. Teste registra o
fragmento selecionado e abstention; os asserts de recorte e de questão vizinha
continuam intactos. Isso é perda conservadora de emissão, não correção de
completude; a política de seleção multipágina NÃO foi alterada neste patch.

## Revealed V4 regression cases — diagnostic regression behavior

Antes: resultado oficial congelado. Depois: wrapper diagnóstico usando somente
os seis IDs obrigatórios, sem CLI/main/evaluate_manifest oficial, sem executar
os 144 casos, sem métricas agregadas e sem OCR novo. `selectedSetUsed=true` e
`rejectedCandidateUsedAfter=false` nos seis, comprovados por refs estruturais no
adapter, slots de Regions e slots de Fusion, não apenas por contagem final.

| questionId | targetOfPatch | before (classification/count/labels) | after (classification/count/labels) | selectedSetUsed | rejectedCandidateUsedAfter |
| --- | --- | --- | --- | --- | --- |
| doc-42af2b3d2b27:q16 | false | unsafe_error / 4 / A-D | unsafe_error / 4 / A-D | true | false |
| doc-cef618be31e6:q23 | false | unsafe_error / 4 / unknown | unsafe_error / 3 / unknown | true | false |
| doc-cf6b56e7abd7:q15 | true | unsafe_error / 6 / A-E | correct / 5 / A-E | true | false |
| doc-eefc3d15076e:q40 | true | unsafe_error / 6 / A-E | correct / 5 / A-E | true | false |
| doc-f4dd01071816:q20 | true | unsafe_error / 5 / A-E | correct / 4 / A-D | true | false |
| doc-800c2a22f148:q1 | true | partial / null / A-D | correct / 4 / A-D | true | false |

No segundo undercount, Structure seleciona C-E; o A externo deixa de entrar em
Regions/Fusion. A passagem 4 → 3 é consequência natural do contrato, não ajuste
para esse caso. Ambos os undercounts seguem sem correção; nenhum E/B foi inferido.

Artefato local: `outputs/audit/postmortem-v4/patch-01-selected-response-set/diagnostic-replay.json`.
SHA256: `efb2ebcd06f6416a053c9043e5ad4368c2146527dbcaa1655e5089b7673dfcca`.

## Preservação e metodologia

Snapshot antes/depois: 1.666 arquivos protegidos byte-idênticos, incluindo todo
`audit/holdout/`, caches OCR e evidência do postmortem anterior. GT, manifest,
index, protocol, preparação OCR e resultado oficial intactos. SHA256 do resultado:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

`officialAuditorExecutionCount=1`; `officialAuditorRerun=false`;
`productionPatch=true`; `V4PerformanceClaimed=false`; `V5Required=true`.
Este replay é **not an unbiased evaluation**: V4 revelado é desenvolvimento e
regressão, não benchmark pós-patch. Nenhuma claim de precision, coverage ou unsafe
rate. V5 blind é obrigatório antes de qualquer medição imparcial pós-patch.

Patch 01 concluído. Próximo passo separado: `response_set_completeness`.
Boundary/header grammar, role/spacing e observation capability continuam pendentes.
