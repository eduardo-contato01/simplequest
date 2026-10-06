# Patch 02 — response_set_completeness

Base Patch 01: `27b3b608480622ffab57cf97c636e4631500795e`.
Branch: `audit/holdout-v4-postmortem-fixes`. Safety gate, sem merge.

## Problema e contrato

Observar N opções não prova que o conjunto está completo. Suffixes/gaps ou uma
possível continuação terminal podem produzir count plausível, mas incorreto.

Structure agora expõe `responseSetCompleteness` como irmão de `selectedResponseSet`:
`status`, `requiredForOptionEmission`, `selectedLabels`, `evidence` e `blockers`.
Estados: `complete`, `incomplete`, `ambiguous`, `unknown`, separados de confidence.
O gate é aplicável ao conjunto textual padrão single_choice e às opções textuais
de modo mixed; CE/true_false_items, parent_child, enumeração interna, numeric,
discursive e custom/unknown não recebem cegamente a regra de prefixo A.
Para modos isentos: required=false, status=unknown, sem blocker de incompletude.

- `complete`: prefixo contíguo A-C/A-D/A-E, seleção inequívoca, sem sinal de
  continuação residual pela política observacional. Não é prova universal de
  ausência de alternativa invisível; vale dentro dessa capacidade limitada.
- `incomplete`: falta A ou há gap interno sem recovery observacional aceita.
- `ambiguous`: seleção/layout ambíguo ou possível continuação na borda.
- `unknown`: ausência de evidência de fechamento suficiente, inclusive fragmento
  A-B, que já não era emitido pelo gate mínimo existente. Nenhum mínimo quatro.

Labels são calculados somente dos candidatos aceitos do selected set. Recovery
interna anterior continua permitida com sequence_gap + alignment + spatial_cluster;
nenhuma nova recovery ou label é criada. Candidatos rejeitados continuam excluídos
dos slots/count/labels do Patch 01. Não há stitching multipágina.

`detect_edge_sequence_ambiguity` agora aceita prefixos contíguos que ainda possam
ter sucessor no alfabeto de markers existente (incluindo A-D + possível E), sem
inferir esse sucessor. Guarda conjunta: linha adjacente, mesma página, alinhamento,
distância próxima, texto residual curto e ausência de marker reconhecido.
O limite vertical trailing usa o maior entre o piso existente de 20 e a mediana
observada de gaps do próprio cluster, evitando depender só de unidades PDF versus
pixels OCR. O teto oito conta tokens com conteúdo alfanumérico, não operadores
isolados. Não foi ampliado o parser de markers nem criado confusion map.

Fusion adiciona hard blockers `response_set_incomplete` e
`response_set_completeness_uncertain` quando required=true e status != complete:
count=null, labels=unknown (ou null sem slots aplicáveis), interpretationConfidence=low.
Um producer com selected set textual autoritativo mas sem contrato de completude
falha conservadoramente como unknown. Fixtures legadas sem selected contract mantêm
compatibilidade. Structure também bloqueia expectedOptionCount e reduz confiança
de labels quando a completude aplicável não permite emissão.

Arquivos funcionais alterados: `scripts/audit_response_structure.py` e
`scripts/audit_response_fusion.py`. Regions, Holdout/classificador, observation,
OCR, boundary, grammar de markers, clustering/seleção e recovery permanecem intactos.

## TDD e validação

Novos controles em `scripts/audit_response_holdout_selftest.py` antes das mudanças
funcionais: RED com 31 falhas novas, nenhuma falha anterior. GREEN final: 58 checks
novos, incluindo controles A-N, A-C/A-D/A-E reais, suffix CDE/BCDE, gaps ACDE/ABDE,
gap B recuperado pela política anterior, residual terminal sem E inventado,
continuação desalinhada, footer distante, outra página, prosa longa, CE/contexto,
parent_child, numeric/discursive/internal/unknown e multipágina sem stitching.
Patch 01 mantém seus 57 checks PASS. Alta confidence não sobrepõe incomplete,
ambiguous ou unknown; ausência do contrato explícito também bloqueia emissão.

Dois ciclos adicionais TDD: RED=1 para geometria em escala maior e RED=1 para
espaçamento de operadores; ambos GREEN antes do replay final. Guardas negativas
mantêm prosa longa, linha desalinhada e footer distante sem falsa ambiguidade.
São refinamentos gerais de adjacência/tamanho residual, não regras por ID/texto.

Todas as 14 suítes existentes PASS: structure, regions, fusion, holdout, question
boundary, observations, OCR content, visual marker evidence, question-index,
seletores V3/V4, protocolo V4 e V2 R1/R2. Syntax/py_compile dos arquivos alterados PASS.

## Diagnostic regression behavior — somente seis IDs revelados

Antes: replay Patch 01. Depois: wrapper diagnóstico local, não CLI/main/runner
oficial completo/evaluate_manifest. Nenhum caso adicional aos seis IDs autorizados.
Duas tentativas interrompidas no primeiro ID revelaram os limites geométrico e de
tokenização acima; depois houve passagem completa dos seis. Oito chamadas locais
no total, seis IDs únicos; nenhuma execução oficial nova ou OCR novo.

| questionId | targetPatch02 | before (classification/count/labels) | after (classification/count/labels) | completenessStatus | completenessEvidence |
| --- | --- | --- | --- | --- | --- |
| doc-42af2b3d2b27:q16 | true | unsafe_error / 4 / A-D | safe_abstention / null / unknown | ambiguous | possible_edge_continuation; adjacent_line; alignment; edge_sequence_gap; near_edge; observed_option_cadence |
| doc-cef618be31e6:q23 | true | unsafe_error / 3 / unknown | safe_abstention / null / unknown | incomplete | missing_initial_label |
| doc-cf6b56e7abd7:q15 | false | correct / 5 / A-E | correct / 5 / A-E | complete | contiguous_prefix_from_a; no_observed_edge_continuation |
| doc-eefc3d15076e:q40 | false | correct / 5 / A-E | correct / 5 / A-E | complete | contiguous_prefix_from_a; no_observed_edge_continuation |
| doc-f4dd01071816:q20 | false | correct / 4 / A-D | correct / 4 / A-D | complete | contiguous_prefix_from_a; no_observed_edge_continuation |
| doc-800c2a22f148:q1 | false | correct / 4 / A-D | correct / 4 / A-D | complete | contiguous_prefix_from_a; no_observed_edge_continuation |

Nos seis: selectedResponseSetUsed=true; rejectedCandidatesUsedDownstream=false,
verificados por refs estruturais no adapter, Regions e Fusion. Patch01 targets
regressed=false. Neutralização dos undercounts é regression behavior por abstenção,
não recuperação automática das opções perdidas nem ganho medido de cobertura.

Artefatos/logs ignorados: `outputs/audit/postmortem-v4/patch-02-response-set-completeness/`.
SHA256 de `diagnostic-replay.json`:
`d74a30ffc5b9c92198ef4d18bd2aa96f6369992b65be697ce426b4323fe80221`.

## Preservação e metodologia

1.689 arquivos protegidos byte-idênticos: todo audit/holdout, caches OCR, evidência
anterior e artefatos locais Patch 01. GT/manifest/index/protocol/preparação OCR e
resultado oficial intactos. Resultado SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

officialAuditorExecutionCount=1; officialAuditorRerun=false; V4PerformanceClaimed=false;
V5Required=true. V4 revelado é desenvolvimento/regressão, **not an unbiased
evaluation**. Nenhuma execução dos 144, métrica agregada ou claim de precision,
coverage, unsafe rate ou ganho percentual pós-patch. V5 blind continua obrigatório.

Patch 02 concluído. Próximo passo separado: `neutral_boundary_identity_and_scope`.
Boundary não iniciado. Limitações: completude é dependente das observações;
fragmento multipágina permanece conservador, sem stitching/recuperação de coverage.
