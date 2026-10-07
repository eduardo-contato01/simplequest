# V4 Patch05B — safety bisection: parada por causas distintas

Data: 2026-10-07. Branch: `audit/holdout-v4-postmortem-fixes`.
Base e HEAD preservados: `98bae929c8300d2a4fe4cc23678ab4c09b274bd3`.

## Resultado e escopo

A bisseção local reproduziu as duas regressões pela primeira vez no Patch03C,
`403eb0155544a867fe5f70b2b8efa2f9a024222a`. A reconstrução de linhas é o
gatilho comum, mas os defeitos semânticos de autorização são distintos:

- q11: falso fechamento terminal de um prefixo reconstruído A-C.
- q17: bypass da exigência de completude em `mode=unknown`, com C-D-E,
  e não falso fechamento de um prefixo A-C/A-D.

Cumprida a condição de parada da seção 13 do pedido: somente diagnóstico e
propostas separadas; nenhum código funcional alterado. Patch05B não concluído;
as duas regressões continuam presentes. Não foram iniciados TDD, replay
pós-patch de 30 IDs, observation complementary, OCR, CID ou glyph recognition.
Não houve staging, commit, push ou merge.

## Método e evidências

Preflight PASS: branch/HEAD exigidos, working tree e stage inicialmente limpos,
`git diff --check` sem erros, resultado oficial com SHA256 esperado.

Foram feitas exatamente 16 chamadas locais: somente os dois IDs, em cada um
dos oito commits. Os módulos Python de cada commit foram carregados via
`git show` em processos isolados, com imports históricos consistentes;
nenhum checkout/worktree/branch foi trocado. Fontes, índice, protocolo e caches
permaneceram congelados. GT foi usado apenas no wrapper de classificação;
nenhuma decisão de emissão recebeu contagem/labels esperados.

Artefatos ignorados: `outputs/audit/postmortem-v4/patch-05b-safety-bisect/`.
`A.json` a `H.json` e `all.json` contêm boundary, reconstrução, inputs/source
das linhas, candidatos/evidence, selectedResponseSet/labels, completude/evidence,
slots/origins, Fusion blockers e ambas as confidences. A-E não possuem o
campo `lineReconstruction` no código histórico; essa ausência foi registrada,
não preenchida com diagnósticos fictícios. A também precede os contratos 01/02.

SHA256 de `all.json`:
`c676c7c8e43666d3531734c9b5a15fafa70aa96f5f6d5437886abb809599144d`.

## Bisseção

Cada resultado abaixo é `classification / count / labels`.
q17 = `doc-eefc3d15076e:q17`; q11 = `doc-5d61be2ac853:q11`.

| Estado / commit | q17 | q11 | firstUnsafeForQ17 | firstUnsafeForQ11 |
| --- | --- | --- | --- | --- |
| A postmortem `07a40333ade4d1a027d6f6ef39eff55e08875fe8` | safe_abstention / null / null | safe_abstention / null / unknown | false | false |
| B Patch01 `27b3b608480622ffab57cf97c636e4631500795e` | safe_abstention / null / null | safe_abstention / null / unknown | false | false |
| C Patch02 `a1ded90cbba3232565cb102ddd279e9e684ffb7e` | safe_abstention / null / null | safe_abstention / null / unknown | false | false |
| D Patch03A `9e488286fa5b87a4d42e08ebd3d3b5fdf666f3b6` | safe_abstention / null / null | safe_abstention / null / unknown | false | false |
| E Patch03B `8ebdd70e1863d822a730176fd87a9a476e7cdc96` | safe_abstention / null / null | safe_abstention / null / unknown | false | false |
| F Patch03C `403eb0155544a867fe5f70b2b8efa2f9a024222a` | unsafe_error / 3 / unknown | unsafe_error / 3 / A-C | true | true |
| G Patch04 `10f778593c06be50228035ebb911192cdbee7f06` | unsafe_error / 3 / unknown | unsafe_error / 3 / A-C | false | false |
| H Patch05A `98bae929c8300d2a4fe4cc23678ab4c09b274bd3` | unsafe_error / 3 / unknown | unsafe_error / 3 / A-C | false | false |

Em E/F/H, ambos têm boundary `reliable=true`, `reason=ok`, vertical e os
mesmos limites locais. F introduz `lineReconstruction.used=true`,
`reason=collapsed_full_width_line`: q17 usa 51 words/21 linhas; q11 usa
139 words/29 linhas. Todas essas linhas expõem `reconstructed_from_words`,
mas chegam à Structure com `is_reconstructed=false`.

## Causa 1 — q11: fechamento por ausência em observação degradada

Antes (E): linhas OCR colapsadas; candidatos A/C/A em clusters distintos,
nenhum selectedResponseSet e somente um answer_option. O padrão tem papel
desconhecido, sem count emitido. Não havia blocker explícito: faltava evidência
positiva suficiente para satisfazer o gate de emissão.

Depois (F, ainda G/H): a reconstrução produz candidatos A/B/C com
`responseField=present`, agrupados no cluster 0; D é observado, mas com
`responseField=absent`, em outro cluster. O selectedResponseSet retém A/B/C.
`mode=single_choice`; a completude conclui `complete` usando exatamente
`contiguous_prefix_from_a` + `no_observed_edge_continuation`.
Regions cria três slots strong com conteúdo; Fusion emite 3/A-C, sem blockers,
observationConfidence=medium e interpretationConfidence=medium.

Primeiro failing stage: **Structure / assess_response_set_completeness**.
A proveniência reconstruída é descartada em `_observed_lines()` e não chega
à evidence dos candidatos/contrato. Ausência de continuação aceita pelo
detector não comprova fechamento; inclusive existe D fora do cluster selecionado.
Não se deve promover esse D automaticamente nem inferir quantidade esperada.

Proposta separada (não implementada): propagar provenance existente até
candidatos e contrato; não aceitar ausência observacional como fechamento
terminal de prefixo reconstruído que termine antes de E. Bloquear count/labels
pelo contrato de completude, preservando A-C/A-D originais, A-E reconstruído,
mixed-provenance conservador e recovery interna já aceita. Testar RED/GREEN
sem IDs/GT/clamps ou nova policy visual.

## Causa 2 — q17: completude não obrigatória permite emissão de subconjunto

Antes (E): quatro linhas OCR locais, uma colapsada, zero candidatos e zero
answer_option slots; nenhuma evidência positiva para emitir count.

Depois (F, ainda G/H): só C/E viram markers explícitos. Structure aceita
recovery geométrica interna de D com `sequence_gap`, `alignment` e
`spatial_cluster`, produzindo selectedResponseSet C/D/E.
`_response_mode()` examina os explícitos C/E, sem instrução C/E ou parent-child,
retorna `unknown` e `ce_without_context`. Structure não emite count.

`assess_response_set_completeness()` retorna `status=unknown`,
`requiredForOptionEmission=false`, evidence
`completeness_not_applicable_to_response_mode`. Portanto o teste de início A
nem é executado. Regions forma `one_per_option` com três slots e conteúdo,
origens strong/recovered_geometry/strong. Fusion autoriza count=3 por padrão,
geometria e ausência de blockers, independentemente do mode desconhecido.
Labels continuam unknown; ambas as confidences ficam medium.

Primeiro failing stage: **contrato de aplicabilidade da completude em Structure**;
a emissão insegura se concretiza em **Fusion / allow_count**. O defeito não é
`complete` por `no_observed_edge_continuation`: esse evidence NÃO existe em q17.
Recovery de um gap interno C-E comprova apenas um slot intermediário, não
início/fechamento do conjunto inteiro nem count global. Terminar em E não basta
para tornar C-D-E um conjunto completo.

Proposta separada (não implementada): investigar um contrato geral que exija
completude antes de emitir count de answer_options textuais selecionadas,
inclusive quando a classificação de mode permanece desconhecida. Validar
o gate consumidor sem reclassificar C/E artificialmente, sem desabilitar recovery
interna válida e sem quebrar C/E verdadeiro, parent-child, visual-only ou A-E.
Exige TDD próprio; não é resolvido apenas pelo guard de prefixos reconstruídos.

## Por que parar

O gatilho histórico e a perda de provenance são comuns, mas a hipótese
específica de falso fechamento de prefixo explica apenas q11. Aplicar somente
o guard solicitado para A-C/A-D reconstruído deixaria q17 unsafe: C-D-E
termina em E e seu contrato atualmente nem exige completude. Expandir a
aplicabilidade/consumo desse contrato é uma segunda decisão semântica.
Não foi forçada uma única regra para esconder essa diferença.

## Preservação e metodologia

Todo `audit/holdout/`, incluindo official result, GT, manifest, question index,
protocol e OCR preparation, foi mantido byte-idêntico; caches OCR e evidências
dos patches anteriores/native render também foram comparados por SHA256.
Código funcional/configuração Git não alterados; `core.autocrlf=true`.
CONTEXTO recebeu apenas uma entrada incremental, sem reescrever histórico.

Official result SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

`officialAuditorExecutionCount=1`; `officialAuditorRerun=false`;
`newOCRExecutions=0`; `V4PerformanceClaimed=false`; `V5Required=true`.
Esta bisseção é diagnóstico de regressões conhecidas em amostra revelada,
não avaliação imparcial ou melhoria de métricas.

Próximo passo: solicitar decisão sobre as duas propostas de segurança antes
de implementar Patch05B ou iniciar observation_complementary_capability.
