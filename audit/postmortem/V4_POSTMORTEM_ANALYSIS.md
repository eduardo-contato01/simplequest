# Holdout V4 Postmortem

## Status metodológico

V4 já revelado. Resultado oficial preservado; nenhuma execução oficial nova, nenhum patch, tuning, OCR novo ou alteração de cache. Branch separada `audit/holdout-v4-postmortem`; nenhum merge. Este é um diagnóstico, não uma nova medição.

Base: `0eda2880edaa70915e80cc78889cb837307e7d43`. Freeze do resultado: `89f482b373449022423b4d34536160e62774cd2d`. Freeze da amostra, commitado e publicado antes da inspeção: `84ff03278aeae0f9a1b94eecd82fc674e753c8ff`. Seleção metadata-only com algoritmo determinístico e 24 IDs imutáveis; ver [sample freeze](V4_POSTMORTEM_SAMPLE_FREEZE.md) e [sample JSON](v4-postmortem-sample.json).

Replay diagnóstico: exatamente 30 chamadas às camadas existentes via wrapper em outputs; sem main(), CLI oficial ou evaluate_manifest(). officialAuditorExecutionCount=1; officialAuditorRerun=false. Todas as classificações e agreement/sources/count/labels/confidences/blockers comparados reproduzem o resultado: diagnosticReplayMismatch=false. Nenhuma alteração funcional.

Foram revisadas 45 entradas de páginas completas (questão e próxima questão quando aplicável), usando PNG raster existente e render nativo diagnóstico sem OCR. O pacote PDF em `outputs/audit/postmortem-v4/first-analysis/V4_POSTMORTEM_FORENSICS.pdf` organiza A=5 unsafe, B=1 partial, C=24 abstentions. Traces completos por camada em `forensics.json`; snippets limitados, nenhum texto integral nos findings versionados. needsHumanVisualReview=false nos 30; isso não prova que futuros patches resolverão esses casos.

## Baseline

144 executable de 144; correct=60; partial=1; safe_abstention=66; unsafe_error=5; not_applicable=12; not_executable=0. Precision emitida=92,42%; coverage=52,08%. runStamp=20261005T221306Z.

SHA256 do resultado JSON: `2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`; Markdown: `3bc3db2a0330d8bd050adfec4792b4552b01fad832dc04317cf9e6860d24f5cd`; metricsCanonicalJsonSha256: `735e9dc0e61424963133496a47484f9ff184ee135399fdf929946098bba50892`. A serialização canônica segue a convenção existente sort_keys/ensure_ascii=False com espaços padrão; não houve alteração dos bytes congelados.

## Census das abstenções

População completa de 66, consultada antes de qualquer PDF/PNG/OCR/GT notes da amostra. Contagens são exclusivamente metadata do resultado congelado; family preserva os caracteres Unicode/acentuados originais, sem recodificação.

### blockerSignature

| Valor | Quantidade |
| --- | ---: |
| boundary_uncertain | 50 |
| missing_marker_observation | 2 |
| no_explicit_blocker | 13 |
| weak_anchor_only | 1 |

### sourceType

| Valor | Quantidade |
| --- | ---: |
| hybrid | 1 |
| raster | 24 |
| text_native | 41 |

### markerStyle

| Valor | Quantidade |
| --- | ---: |
| parenthesized | 31 |
| symbolic_control | 19 |
| textual | 16 |

### contentKind

| Valor | Quantidade |
| --- | ---: |
| math | 20 |
| mixed | 18 |
| text | 28 |

### agreement

| Valor | Quantidade |
| --- | ---: |
| insufficient | 57 |
| partial | 8 |
| strong | 1 |

### observationConfidence

| Valor | Quantidade |
| --- | ---: |
| low | 58 |
| medium | 8 |

### interpretationConfidence

| Valor | Quantidade |
| --- | ---: |
| low | 57 |
| medium | 9 |

### family

| Valor | Quantidade |
| --- | ---: |
| CMB | 1 |
| CMBH | 7 |
| CMBel | 1 |
| CMC | 1 |
| CMF | 8 |
| CMJF | 5 |
| CMM | 9 |
| CMPA | 2 |
| CMR | 3 |
| CMRJ | 2 |
| CMSM | 6 |
| CMSP | 1 |
| CMT | 5 |
| CMVM | 2 |
| COLÉGIO PÓDION | 6 |
| COLÉGIO SÓLIDO | 1 |
| OUTRAS | 4 |
| PAS 1 | 2 |

### era

| Valor | Quantidade |
| --- | ---: |
| 2010-2014 | 10 |
| 2015-2019 | 25 |
| 2020-2025 | 31 |

## Unsafe errors

### doc-42af2b3d2b27:q16 — unsafe_error

- Página(s): 17; CMPA; raster.
- Expected: {"responseMode":"single_choice","optionCount":5,"optionLabels":["A","B","C","D","E"]}. Emitted: {"optionCountHypothesis":4,"optionLabelsHypothesis":"A-D"}.
- Evidência: A quinta alternativa é visível; o cache OCR registra o prefixo (EB), não (E), na linha 9, y=649..682. Só A-D passam aos quatro slots; não há recovered E.
- First failing stage: `observation`; root causes: `observation_missing_or_corrupted`, `marker_detection_failure`, `fusion_policy_failure`; correct evidence upstream: partial.
- Slot incorreto/perdido: Perda do slot E por prefixo OCR corrompido.
- Vazamento da questão vizinha: false; falso marcador: false; marcador real perdido: true; count/labels divergem por razões distintas: false.
- Safety gate: Deveria reter emissão sem evidência de completude e response set consistente.
- Risco generalizável: Sequência observada A-D contínua não prova completude do response set; corrupção terminal produz undercount silencioso.
- Família de correção futura: completude do response set e recuperação corroborada de markers; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

### doc-cef618be31e6:q23 — unsafe_error

- Página(s): 12; CMRJ; text_native.
- Expected: {"responseMode":"single_choice","optionCount":5,"optionLabels":["A","B","C","D","E"]}. Emitted: {"optionCountHypothesis":4,"optionLabelsHypothesis":"unknown"}.
- Evidência: A segunda alternativa é visível como B, mas o texto nativo da linha 24, y=602.75..612.30, começa por (8). Markers/slots A,C,D,E somam quatro. A estrutura seleciona cluster C-E com expectedOptionCount=3; fusion usa quatro candidatos.
- First failing stage: `observation`; root causes: `observation_missing_or_corrupted`, `marker_detection_failure`, `fusion_policy_failure`; correct evidence upstream: partial.
- Slot incorreto/perdido: Perda do slot B; o gap impede labels A-E, mas não impede count=4.
- Vazamento da questão vizinha: false; falso marcador: false; marcador real perdido: true; count/labels divergem por razões distintas: true.
- Safety gate: Deveria reter emissão sem evidência de completude e response set consistente.
- Risco generalizável: Uma lacuna de labels não deve coexistir com count aparentemente seguro; text_native não garante texto fiel.
- Família de correção futura: completude, gaps e proveniência observacional; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

### doc-cf6b56e7abd7:q15 — unsafe_error

- Página(s): 16; CMB; raster.
- Expected: {"responseMode":"single_choice","optionCount":5,"optionLabels":["A","B","C","D","E"]}. Emitted: {"optionCountHypothesis":6,"optionLabelsHypothesis":"A-E"}.
- Evidência: Linha 5, bbox [77,227,1259,286], contém a variável a seguida por traço no enunciado matemático. Ela cria um falso A/slot 0 além de A-E reais. A estrutura seleciona corretamente cluster 1, cinco alternativas; regions/fusion consomem também o candidato rejeitado.
- First failing stage: `marker_detection`; root causes: `marker_detection_failure`, `region_slot_failure`, `fusion_policy_failure`; correct evidence upstream: true.
- Slot incorreto/perdido: Falso slot A do enunciado; seis slots textuais.
- Vazamento da questão vizinha: false; falso marcador: true; marcador real perdido: false; count/labels divergem por razões distintas: true.
- Safety gate: Deveria reter emissão sem evidência de completude e response set consistente.
- Risco generalizável: Pool bruto de candidatos substitui response set selecionado. Labels deduplicadas A-E podem mascarar count=6.
- Família de correção futura: contrato de response set selecionado entre structure, regions e fusion; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

### doc-eefc3d15076e:q40 — unsafe_error

- Página(s): 36; CMBH; raster.
- Expected: {"responseMode":"single_choice","optionCount":5,"optionLabels":["A","B","C","D","E"]}. Emitted: {"optionCountHypothesis":6,"optionLabelsHypothesis":"A-E"}.
- Evidência: OCR da área de crédito/site da tirinha, linha 10 bbox [296,894,1045,983], começa por a -. É convertido em falso A antes das opções reais em y>=1163. Structure seleciona cluster 1, cinco A-E; regions/fusion somam seis.
- First failing stage: `marker_detection`; root causes: `marker_detection_failure`, `region_slot_failure`, `fusion_policy_failure`; correct evidence upstream: true.
- Slot incorreto/perdido: Falso slot A proveniente da figura/crédito, não da questão vizinha.
- Vazamento da questão vizinha: false; falso marcador: true; marcador real perdido: false; count/labels divergem por razões distintas: true.
- Safety gate: Deveria reter emissão sem evidência de completude e response set consistente.
- Risco generalizável: Ruído OCR de mídia promove candidato textual forte; contar slots brutos e deduplicar labels diverge.
- Família de correção futura: contrato de response set selecionado e exclusão de texto não-resposta; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

### doc-f4dd01071816:q20 — unsafe_error

- Página(s): 20; CMJF; raster.
- Expected: {"responseMode":"single_choice","optionCount":4,"optionLabels":["A","B","C","D"]}. Emitted: {"optionCountHypothesis":5,"optionLabelsHypothesis":"A-E"}.
- Evidência: O footer OCR da linha 22, bbox [0,1835,1247,1870], começa por E: antes de Seção Técnica de Ensino. A página mostra A-D e FIM DA PROVA; a estrutura seleciona quatro opções. O boundary da última questão inclui rodapé e cria slot E adicional.
- First failing stage: `marker_detection`; root causes: `marker_detection_failure`, `boundary_failure`, `region_slot_failure`, `fusion_policy_failure`; correct evidence upstream: true.
- Slot incorreto/perdido: Falso slot E do rodapé; cinco slots em vez de quatro.
- Vazamento da questão vizinha: false; falso marcador: true; marcador real perdido: false; count/labels divergem por razões distintas: false.
- Safety gate: Deveria reter emissão sem evidência de completude e response set consistente.
- Risco generalizável: Fim do intervalo de página não equivale a fim da região de resposta. Footer textual pode contaminar count e labels juntos.
- Família de correção futura: response set selecionado e escopo neutro de rodapé; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

## Partial

### doc-800c2a22f148:q1 — partial

- Página(s): 2; CMDPII; text_native.
- Expected: {"responseMode":"single_choice","optionCount":4,"optionLabels":["A","B","C","D"]}. Emitted: {"optionCountHypothesis":null,"optionLabelsHypothesis":"A-D"}.
- Evidência: A-D e quatro slots são corretos. O parser estrutural extrai ainda e) de desfazer(-se). dentro da opção D, mesma linha 25, como quinto candidato. Structure seleciona cluster 0 com quatro; fusion compara cinco candidatos brutos com quatro slots e cria count_conflict.
- First failing stage: `marker_detection`; root causes: `marker_detection_failure`, `fusion_policy_failure`; correct evidence upstream: true.
- Slot incorreto/perdido: Nenhum slot espacial falso: conflito artificial vem do candidato inline adicional.
- Vazamento da questão vizinha: false; falso marcador: true; marcador real perdido: false; count/labels divergem por razões distintas: true.
- Safety gate: Abstenção de count protege diante do conflito, mas o conflito é artificial; quatro slots corretos existem.
- Risco generalizável: Candidato inline de texto não deve ser comparado como response set independente; gate absteve count corretamente diante do conflito produzido.
- Família de correção futura: response set selecionado e contrato de provenance; sem implementação.
- needsHumanVisualReview=false: labels/quantidade e localização foram verificadas em página completa; a conclusão causal coincide com o trace, sem inferir semântica da resposta.

## Safe abstention sample

24/66, sem substituição após abertura visual. Categoria é diagnóstico de um pré-requisito recuperável, não promessa de emissão segura nem de resolução de todas as camadas. Todas as abstenções atuais são conservadoras diante das observações/policies disponíveis. `recoverable_boundary` inclui dois boundaries indevidamente considerados reliable, não apenas os que apresentam boundary_uncertain.

| questionId | Stratum | Diagnóstico / recuperabilidade | Causa observada | Risco de relaxar gate |
| --- | --- | --- | --- | --- |
| doc-27775227a392:q1 | ["text_native","parenthesized","mixed"] | recoverable_structure | Markers ( a )..( e ) existem nas linhas nativas 13-17, mas gramática não aceita espaços; regiões confundem alternativas com enumeração interna (nove subitems). | Distinguir enumeração interna I-IV de alternativas; não promover nove subitems a nove opções. |
| doc-27775227a392:q14 | ["text_native","parenthesized","math"] | recoverable_structure | Cinco prefixes ( a )..( e ) presentes no native; markers fortes ausentes e cinco slots classificados como subitem. | Espaçamento/minúsculas não provam papel; exigir response set coerente. |
| doc-3fb1e1ce24be:q32 | ["text_native","parenthesized","mixed"] | recoverable_structure | Native expõe cinco prefixes parenthesized espaçados; zero markers fortes. Oito slots misturam três answer_option fracos e cinco subitems; weak_anchor_only bloqueia corretamente. | Não converter weak anchors/linhas de continuação em alternativas. |
| doc-f03e7d17eec1:q20 | ["hybrid","parenthesized","math"] | recoverable_boundary | Native híbrido contém Questao - 20 e A-E; variante com hífen não entra nos marcadores atuais; boundary false descarta 27 linhas. | Aceitar variante somente com número/posição/ordem coerentes, não abrir página inteira. |
| doc-eefc3d15076e:q17 | ["raster","parenthesized","mixed"] | requires_new_observation_capability | Boundary correto; OCR colapsa opções e figura em uma linha y=417..1038. Algumas palavras C/E sobrevivem; não há cinco markers completos/slots. | Reagrupar words pode ajudar, mas cache não sustenta recuperação completa dos cinco labels; não presumir cinco. |
| doc-2790a3c9786b:q4 | ["raster","parenthesized","text"] | recoverable_structure | Structure já seleciona cinco A-E com confiança alta e cinco markers reais; regions atribuem três subitems e apenas dois answer_option a opções minúsculas. | Corrigir associação/papel com evidência; não tratar toda enumeração a-e como resposta. |
| doc-f4dd01071816:q13 | ["raster","symbolic_control","math"] | requires_new_observation_capability | Quatro A-D visíveis, mas bundle filtrado expõe somente D como marker; words não apresentam conjunto A-D íntegro. | Não inferir opções faltantes pela quantidade esperada; exigir observação complementar. |
| doc-5d61be2ac853:q11 | ["raster","symbolic_control","text"] | requires_new_observation_capability | Quatro opções A-D visíveis; OCR filtrado tem três linhas e somente A como marker, com geometria/conteúdo colapsados. | Texto residual não prova quatro slots; novas observações precisam controles de regressão. |
| doc-3fb1e1ce24be:q12 | ["text_native","parenthesized","math"] | recoverable_structure | Native contém a-d com espaços dentro dos parênteses e e compacto; só E vira marker forte. Cinco slots existem, quatro classificados subitem. | Papéis/continuações não podem ser decididos apenas pela caixa das letras. |
| doc-3e395d355d2c:q25 | ["text_native","parenthesized","text"] | recoverable_boundary | Cabeçalho central Questão 25 correto; falso peer 23). do conteúdo em x=56.64 induz two_column/right x>=162.505 e exclui opções A-E em x=56.64. | Não usar qualquer número do conteúdo como prova de coluna paralela. |
| doc-b605f7a51fd5:q5 | ["text_native","symbolic_control","math"] | recoverable_visual | Cinco labels circulados visíveis não aparecem como texto de marcador no native; zero markers/evidence/slots. Render visual existente não contribui nesta execução. | Detector de círculos pode recuperar count; identificar A-E requer evidência do glyph, não apenas círculo. |
| doc-b605f7a51fd5:q20 | ["text_native","symbolic_control","mixed"] | recoverable_boundary | Fração do conteúdo 1 6 8 vira peer em x=355.90; two_column/left x<=191.45 remove todas as 24 linhas. Cinco labels circulados também exigem suporte visual. | Reparar scope é pré-requisito, não promessa de emissão; símbolos circulados continuam não textuais. |
| doc-56268e79f6bf:q11 | ["raster","parenthesized","math"] | recoverable_boundary | OCR header QUESTÃO e 11 colapsados com cabeçalho institucional; words preservam localização e opções a-e. Current_marker_not_found esvazia bundle. | Ressegmentar geometria do header; não associar número do ano/rodapé. |
| doc-56268e79f6bf:q14 | ["raster","parenthesized","mixed"] | recoverable_boundary | Mesmo colapso header QUESTÃO/14; opções a-e observadas separadamente no cache; boundary não associa número atual. | Validar ordem/página/posição do header, não substring genérica. |
| doc-a1ddc006ef56:q23 | ["raster","parenthesized","text"] | recoverable_boundary | Header 23. A partir ... existe no OCR, mas NUMERIC_RE rejeita sequência numérica seguida por A isolado (proteção de parent-child). Q22/Q24 são encontrados. | Manter proteção contra subitems; testar headers legítimos começando por A sem aceitar falsas questões. |
| doc-f4dd01071816:q5 | ["raster","symbolic_control","mixed"] | recoverable_boundary | Palavra 05. em [141,221,172,240] sobrevive no OCR, mas quase toda a página vira uma única linha bbox 0..1256. Boundary não encontra q5. | Words/geometria precisam ressegmentação antes do scope; conteúdo não deve ser aceito em bloco inteiro. |
| doc-0db5ce524459:q26 | ["raster","textual","math"] | requires_new_observation_capability | Página com coluna de cálculos/manuscrito; cache possui só cinco linhas extensas e header 26 não foi preservado de forma utilizável. A página visual identifica questão/opções. | Não recuperar número pelo parecido 07 nem pelos rabiscos; exige observação mais fiel. |
| doc-ad34c4cf7f30:q26 | ["raster","textual","mixed"] | requires_new_observation_capability | Página com q24/q25/q26 e coluna de cálculo; quatro linhas OCR, uma bbox y=218..1721. Número 26/associação de alternativas não estão íntegros. | Não promover texto/manuscrito da coluna vizinha; não basta relaxar boundary. |
| doc-c41ddc7b55ec:q2 | ["raster","textual","text"] | recoverable_boundary | Words preservam 02. em x=84,y=571 e 07. em x=663,y=578; linhas mesclam colunas. Header atual e A/B/D locais observáveis, C local perdido. | Scope por coluna é pré-requisito; poderá ainda precisar observação complementar do C, sem adivinhar count. |
| doc-bb62e60cf7ed:q27 | ["text_native","parenthesized","math"] | recoverable_boundary | Canonical q27 usa printedQuestionNumber=7, section=mathematics no índice; página/header impresso 07. Boundary procura 27 e ignora metadado neutro já congelado. | Preservar questionId/ordem canônica; usar seção+printed sem relabeling do GT. |
| doc-6dde932fb681:q19 | ["text_native","parenthesized","mixed"] | recoverable_boundary | Native registra 19º Item e cinco A-E; gramática atual não reconhece ordinal antes de Item. | Exigir posição de início/ordem, evitando referências ao item no enunciado. |
| doc-6dde932fb681:q7 | ["text_native","parenthesized","text"] | recoverable_boundary | Native registra 7º Item e A-E; mesma variante ordinal não reconhecida. | Não confundir contexto Texto 3/itens 7 a 9 com começo da questão. |
| doc-44ea716ed9b7:q54 | ["text_native","symbolic_control","math"] | recoverable_boundary | 54 é marcador neutro na coluna direita; linhas nativas mesclam colunas e número não inicia a linha usada pelo detector. A-D/Tipo C estão visíveis. | Reconstruir ordem por words/colunas, preservando itens C/E e controles sem resposta múltipla. |
| doc-1693ea690bbb:q14 | ["text_native","symbolic_control","mixed"] | recoverable_boundary | Native contém prefixo PUA U+F0D8 antes de Questão 14 (e 15); match ancorado falha apesar de A-E e header íntegros. | Tratar decoração com provenance/posição; não remover indiscriminadamente símbolos C/E do conteúdo. |

Distribuição **somente da amostra**: `recoverable_structure=5`; `recoverable_boundary=13`; `requires_new_observation_capability=5`; `recoverable_visual=1`. Sem extrapolação percentual às 66 e sem estimativa ponderada. Casos multi-lacuna (por exemplo q20 do doc-b605f7a51fd5 e q2 do doc-c41ddc7b55ec) podem exigir observação adicional mesmo depois de reparar boundary.

Root causes dos seis obrigatórios (multi-label; não somar como casos exclusivos): `observation_missing_or_corrupted=2`; `marker_detection_failure=6`; `fusion_policy_failure=6`; `region_slot_failure=3`; `boundary_failure=1`. Causas da amostra são contadas separadamente no findings JSON.

## Padrões encontrados

### Segurança

- Cinco unsafe não decorrem de alternativas de questões vizinhas. Dois perdem markers reais, três promovem conteúdo não-resposta.
- Sequência A-D contínua não prova ausência de E; labels unknown com gap não torna count seguro.
- Labels deduplicadas A-E escondem seis slots; count e labels precisam consistência do mesmo response set.
- O partial mantém quatro slots corretos, mas compara com candidato inline falso. Abstém count diante do conflito, porém o conflito é fabricado upstream.

### Coverage e observation

- Há marcadores presentes e não aproveitados: espaços nos parênteses, minúsculas e papel subitem versus answer_option.
- Raster pode colapsar linhas/colunas; palavras com bbox úteis sobrevivem em alguns casos, mas não em todos. Native pode conter (8) no lugar de (B), ou não expor glyph circulado.
- Cinco casos exigem observação complementar no diagnóstico; não inventar markers pelo GT ou pela expectativa A-E.
- Círculo observado não prova glyph/label. Reutilizar capacidade visual existente para count requer testes, não introduzir silenciosamente uma nova família.

### Boundary

- Identidade canônica e numeração impressa por disciplina são distintas; os metadados neutros do índice já existem e foram ignorados em q27/printed 07.
- Header ordinal, hífen e decoração PUA existem na observação, mas a gramática ancorada falha.
- Headers legítimos iniciados por A conflitam com proteção de subitems; word geometry pode ressegmentar headers colapsados e colunas.
- `reliable=true` pode estar errado: número de referência 23). ou numerador de fração gera falsa coluna e elimina opções corretas. Não abrir toda a página como fallback.

### Marker, regions e fusion

- Structure seleciona clusters corretos em três overcounts e no partial, mas candidates rejeitados continuam alimentando regions/fusion.
- A mesma evidência textual gera candidato e slot; concordância derivada não é confirmação independente.
- Quantidade de candidatos, slots, regiões e labels deduplicadas não é intercambiável.
- O contrato de response set/provenance deve anteceder qualquer ampliação de gramática ou relaxamento de gates.

## Candidatos de trabalho

Ordenação qualitativa por impacto potencial, generalidade, risco e testabilidade; não é estimativa de ganhos de coverage. Primeiro segurança, depois recuperação.

1. `selected_response_set_contract`: Structure, regions e fusion devem preservar o mesmo response set selecionado; candidatos rejeitados/inline não são confirmação independente.
   Impacto observado: Três overcounts e um partial observados. Generalidade: Alta: enunciado, mídia, rodapé e texto interno. Risco: Desconsiderar alternativas legítimas espalhadas/multi-set. Testes: Alta: fixtures sintéticas com candidatos falsos, cluster selecionado, duplicatas e inline.

2. `response_set_completeness`: Completude e gaps, inclusive perda terminal; recuperação de marker somente com geometria/cluster corroborados.
   Impacto observado: Dois undercounts; segurança antes de coverage. Generalidade: Alta para OCR e text_native corrompido. Risco: Inventar E/B por expectativa ou reduzir coverage indiscriminadamente. Testes: Controles de conjuntos reais A-D/A-E/CE/custom, gaps e terminal corrompido; nunca clamp.

3. `neutral_boundary_identity_and_scope`: Printed versus canonical/seção, variantes de header, decoração PUA, ressegmentação por words e prova de colunas; excluir peer do conteúdo.
   Impacto observado: 13/24 categorias de amostra; população tem 50 boundary_uncertain, sem extrapolação de recuperação. Generalidade: Alta, mas separar identidade/gramática/geometria em testes independentes. Risco: Vazamento entre questões/colunas e falsos headers; count seguro não é consequência automática. Testes: Headers legítimos e referências negativas, reset por disciplina, matemática simulando números e multipágina.

4. `marker_role_and_spacing`: Markers espaçados/minúsculos, enumeração interna versus answer_option; provenance de papel.
   Impacto observado: Cinco casos da amostra com observações aproveitáveis. Generalidade: Alta para parenthesized. Risco: Transformar subitems em alternativas; opções com continuação. Testes: Controles sintéticos internos a-e/I-IV e conjuntos reais com espaços.

5. `observation_visual_and_resegmentation`: Observação complementar de markers destruídos e símbolos circulados; avaliar capacidades existentes antes de novos detectores.
   Impacto observado: Cinco requires_new_observation_capability e um recoverable_visual; boundary pode ocultar lacunas adicionais. Generalidade: Média/alta para raster, fonte simbólica e manuscrito. Risco: Falsos círculos, arte/rodapé/manuscrito, glyph não observado; custo/latência. Testes: Negativos de figura/controles e medições por provenance; count e label avaliados separadamente.

## Próxima decisão

Priorizar TDD dos contratos de response set selecionado/completude, com controles positivos e negativos sintéticos e casos de desenvolvimento fora do holdout. Depois separar os trabalhos de identidade/gramática/scope neutro, role/spacing e observação visual. Nenhum caso revelado pode virar regra por documentId/questionId; nenhuma quantidade deve ser clampada em quatro/cinco.

**Qualquer patch funcional pós-V4 exigirá V5 blind para medição imparcial.** V4 passa a ser material diagnóstico/regressão, nunca novamente avaliação cega da versão alterada. Não foi criado V5 nesta etapa.

## Preservação e ocorrências operacionais

- GT, manifest, question index, protocol, preparação OCR, PDFs, caches e código funcional permanecem byte-identicamente preservados; resultado oficial e oito hashes funcionais revalidados antes e depois.
- Refresh autorizado de índice Git resolveu dois status M sem byte/config/line-ending changes. core.autocrlf=true; sem .gitattributes. Exit 1/needs update seguido por status/stage vazios foi registrado, sem fallback git add naquela etapa.
- Primeira tentativa do wrapper falhou somente por import/ROOT, antes de executar qualquer caso; corrigido no wrapper ignorado. A execução diagnóstica concluída tem exatamente 30 casos, sem repetição oficial.
- Checkers locais foram corrigidos para a serialização canônica real e para comparar histórico por linhas: HEAD LF versus working tree CRLF preexistente. Não houve normalização dos artefatos congelados.
- Dependência reportlab foi usada do runtime bundled, sem instalação no projeto.
- Os findings não apontam erro de GT/index nos seis obrigatórios; q27 é uso incorreto de printed/canonical pelo boundary, não erro do índice.
- Traces/PDF/imagens permanecem ignorados; hashes finais registrados na entrada incremental de CONTEXTO. Nenhuma interpretação visual ficou pendente neste escopo.

Ver [findings estruturais](v4-postmortem-findings.json).
