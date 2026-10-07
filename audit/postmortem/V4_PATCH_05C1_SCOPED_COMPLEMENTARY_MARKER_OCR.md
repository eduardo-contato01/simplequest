# Patch05C1 — scoped_complementary_marker_ocr

Branch: `audit/holdout-v4-postmortem-fixes`.
Base/HEAD preservado: `7cbdf63ded87da7eebb5cdb65f89dd37f23a2a95`.
Base funcional: [05B2](V4_PATCH_05B2_COMPLETENESS_APPLICABILITY.md), com
[05B1](V4_PATCH_05B1_RECONSTRUCTED_CLOSURE.md) preservado.

Estado final: **patch05C1CapabilityComplete=true**;
allRevealedTargetsRecovered=false; q13KnownRecognitionLimit=true.
Fechamento autorizado após aceitar a abstenção conservadora q13 e validar
replay30, testes, preservação e diff. A primeira parada e o diagnóstico 05C1b
abaixo são registros históricos; a seção E contém o estado final prevalente.

## A. Implementação principal 05C1

- Primary-first: conjunto primário autoritativo completo com count emitido não
  aciona OCR. Boundary unreliable, scope ausente e raster incompatível também não.
- Adapter exige bundle `ocr_cache`, PNG existente com dimensões exatamente iguais
  à geometria primária e pageLimits concretos para todos os crops. Não presume
  compatibilidade entre PDF points e pixels de render nativo.
- Crop inward: ceil de x0/top, floor de x1/bottom, interseção com imagem. Crop
  antecede OCR e conserva limites de coluna/próxima questão. Nenhum PDF renderizado.
- PIL LANCZOS fixo, upscale 2.0; helper existente `ocr_pdf_layer.tesseract_page()`,
  Tesseract instalado, `por+eng`, PSM 6. Nenhuma matrix, retuning ou engine novo.
- Bbox original = offset do crop + bbox local/2. Words são reagrupadas por
  `audit_observations.group_words_into_lines`, não pelo agrupador simplificado OCR.
- Words/lines registram complementary_ocr, scoped_tesseract, boundary_crop,
  isComplementary, ocrConfidence e observationFamily=ocr_text. Não são original
  nem reconstructed_from_words; markers/refs de Regions conservam source complementar.
- Pipeline complementar separado, sem concatenar passes. Resultado conserva
  primaryStructure, complementaryStructure e effectiveResponseSetSource.
- Promoção exige selected set autoritativo não ambíguo, completude required/complete,
  somente markers explícitos A-E materializados pelo parser existente, sem recovery
  geométrica/completion, sem concorrentes ou conflito primário, e emissão permitida
  pela Fusion. Não altera semântica da Structure/completude.
- Compatibilidade compara labels primários explícitos, incluindo rejeitados de
  forma conservadora, com markers selecionados complementares da mesma página.
  Tolerância X/Y = duas vezes a maior altura observada das linhas; não depende
  de ID/família/página/GT. Recovery primária não é evidência explícita de label.
- Somente o pipeline efetivo fornece slots. Fusion mapeia complementary_ocr para
  a mesma textual_marker origin; dois passes da mesma imagem não dão strong
  agreement. Os dois targets promovidos ficaram partial/medium/medium.

Produção alterada: observations, holdout e mapeamento de origem em Fusion.
Boundary, Structure, Regions, detector visual, OCR helper e gramática intactos.
GTUsedForActivation=false; boundaryChanged=false. Artefatos novos ficam sob
outputs ignorados; nenhum cache OCR primário ou PNG congelado é sobrescrito.

## TDD RED/GREEN

Antes de produção: fixtures A-Z em holdout selftest, RED=26 falhas novas pela
ausência do contrato scoped fallback; 417 checks anteriores passaram.
GREEN final: 50 checks novos executados (incluindo imutabilidade por cenário),
467 checks do holdout PASS; todas as 14 suítes determinísticas PASS + py_compile.
OCR real não participa dos selftests: adapter stub fornece words/bboxes/confidence.

Cobertura: unreliable/no scope/no PNG, primary complete A-D/A-E, elegibilidade,
crop vertical/coluna/exclusão da próxima, round-trip/provenance, parenthesized e
symbolic spacing, não inventar terminais/gaps/início, compatibilidade de prefixo/
suffix, label/geometry conflict, bare A/B/C/P não options, multiline/slots sem
duplicação, mesma origem não independente, falha do engine preservando primária,
visual partial nativo e gates 05B1/05B2 preservados.

A fixture multilinha inicial sobrepunha caixas de continuação e próximo marker;
foi corrigida somente a geometria sintética. A-D com continuação terminal mantém
possible_edge_continuation/ambiguous pelo gate existente; o controle positivo
multilinha usa cinco slots A-E, permitido pelo pedido. Não se relaxou esse gate
para fazer fixture passar. Uma assertion de provenance foi ajustada ao schema
real da Fusion (`textualMarkerRefs`, não `markerObservations`).

## Baseline e diagnóstico real dos três

Baseline fresco salvo ANTES da produção: mesmos 30 IDs originais do postmortem.
Classification/count/labels/boundaries reproduzem o replay final 05B publicado.
Sem main/evaluate_manifest/CLI oficial ou execução dos 144. GT somente no wrapper
de classificação revelada, não nas decisões funcionais.

Baseline SHA256:
`bfa155e1b520d878c503e472db8ac3c018bb4094f4cb1cfbbb4ed1651435c0cf`.
Traces: `outputs/audit/postmortem-v4/patch-05c1-complementary-ocr/baseline.json`.

Motivação humana prévia: q17 mistura figura geométrica com alternativas (A)..(E);
q13 possui A-( )..D-( ); q11 possui esse formato e conteúdo multilinha. Essas
descrições orientam diagnóstico/regressão; não ativam OCR por IDs ou expected count.

| Target | Primária explícita / selected | Página / crop pixels [x0,y0,x1,y1] | Words / lines | Complementar parseado / selected | Completude / compatibility / promoted | Before → after classification/count/labels |
| --- | --- | --- | --- | --- | --- | --- |
| doc-eefc3d15076e:q17 | C,E / C,D,E (D recovery) | 18 / [0,219,1324,1872] | 50 / 13 | A,B,C,D,E / A,B,C,D,E | required=true, complete / compatible / true | safe_abstention/null/unknown → correct/5/A-E |
| doc-f4dd01071816:q13 | D / nenhum | 14 / [0,221,1323,716] | 87 / 17 | C,D / C,D | required=true, incomplete, missing_initial_label / compatible / false | safe_abstention/null/unknown → safe_abstention/null/unknown |
| doc-5d61be2ac853:q11 | A,B,C,D / A,B,C (D rejeitado) | 9 / [0,1071,1323,1871] | 143 / 21 | A,B,C,D / A,B,C,D | required=true, complete / compatible / true | safe_abstention/null/unknown → correct/4/A-D |

Todos: boundary reliable e byte-equivalente ao baseline serializado; uma execução
OCR por target, sem errors; becameUnsafe=false. Agreement/confidences finais:
partial/medium/medium nos três. Os passes promovidos não criam strong agreement.
q17 não transforma o A bare da figura em marker. q11 mantém quatro slots e
conteúdo de continuação com boundaries/association existentes.

Limite q13: leitura local produziu prefixes `A=( .)` e `Esto)` em vez de markers
A/B aceitos. C-( ) e D-( ) sobreviveram; selected C/D não prova início/completude.
Whitespace não corrige substituição de glyph/shape. Não se alterou a gramática
para aceitar esses tokens e não se inferiu label ausente pela sequência.

`targets.json` SHA256:
`b393c26ef9a3c0895be7ac424729c82453d0e5ee24f64cea6b8c490fff418973`.
Crops originais e 2x, JSON de words OCR/local bboxes/confidence, lines reagrupadas,
parsed markers, selected set, compatibility e effective decision estão sob
`outputs/audit/postmortem-v4/patch-05c1-complementary-ocr/` (ignorados).

## B. Primeira parada q13 — registro histórico

Core implementado e testes GREEN, mas **patch05C1Complete=false**. O diagnóstico
real autorizado executou exatamente três passes Tesseract locais. q17 observou
A-E e q11 observou A-D, promovidos pelos contratos existentes. q13 observou
somente C/D como answer markers parseáveis; A/B permanecem corrompidos.

Cumprida a seção 30: parar sem mudar PSM/scale, preprocessing, thresholds,
gramática ou formatos. Não foram inventados A/B. Sem replay pós-patch dos 30,
staging, commit, push ou merge. As alterações ficam locais, não publicadas.
Próximo passo depende de decisão sobre eventual **05C1b**, não início de 05C2.
Brain/roadmap não foram marcados como concluídos.

### Replay então pendente, controles e fora do escopo

Replay pós-patch 30 **não executado**, em cumprimento à parada q13.
newUnsafeRegressionCount dos 30 **não validado** nesta etapa; nos três diagnósticos
nenhum unsafe. Não declarar safety gate global PASS nem patch concluído.

Controles abaixo são estados do baseline fresco, NÃO resultados pós-patch:

- doc-b605f7a51fd5:q5: partial/5/unknown.
- doc-f4dd01071816:q20: safe_abstention/null/unknown.
- doc-800c2a22f148:q1: safe_abstention/null/unknown, conservador 05B.
- doc-44ea716ed9b7:q54 e os dois Pódion q26: safe_abstention/null/null.

Nenhum desses controles recebeu OCR real nesta etapa. Pódion q26 tem boundary
unreliable e não deve acionar fallback (contrato coberto no TDD); pertence ao
eventual 05C2. q54 CID/header ausente permanece fora do escopo. Arquivo Pódion
com nome histórico incorreto não foi renomeado, manifest/fingerprint não alterados.
Sem glyph recognition, header OCR, CID decoding, column recovery, handwritten
removal, PDF OCR completo, final index/GT/selection novos ou início de 05C2.

### Preservação e estado local na primeira parada

1.891 arquivos protegidos byte-idênticos ao snapshot pré-produção: todo
audit/holdout (resultado, GT, manifest, question index, protocol, OCR preparation),
OCR caches primários/PNGs, native visual cache e evidências anteriores. Nenhuma
alteração de configuração Git, core.autocrlf=true; sem .gitattributes/gitignore.
CONTEXTO recebe UMA entrada incremental de parada, sem reescrever histórico.

Resultado oficial SHA256 preservado:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.
officialAuditorExecutionCount=1; officialAuditorRerun=false;
complementaryOcrExecutions=3; V4PerformanceClaimed=false; V5Required=true.
2/3 targets produziram conjuntos explícitos completos: resultado diagnóstico
revelado, não coverage, precision, unsafe rate ou recovery rate. V5 blind continua
obrigatório para avaliação imparcial; não criado/executado nesta etapa.

Working tree local alterada, stage vazio, HEAD/base inalterados; commit/push não
executados e remote SHA não revalidado. Nenhum merge. Próxima ação: decidir
05C1b diante da corrupção observada em q13; nenhuma ampliação automática.

## 05C1b — aligned marker gutter fallback

C. Diagnóstico somente; nenhuma implementação produtiva de gutter.

Continuação explicitamente autorizada em 2026-10-07, no mesmo worktree/HEAD,
preservando a implementação e a entrada de parada anteriores. Este refinamento
foi descoberto durante 05C1, NÃO estava planejado desde o início. Os estados
descritos acima pertencem à primeira etapa; esta seção registra a continuação.

### Diagnóstico raw q13 antes de qualquer alteração de produção

Inspecionados os words OCR originais da passagem complementar completa, suas
bboxes locais 2x/confidences, words mapeadas à página e linhas reagrupadas.
Nenhum novo OCR nesse primeiro diagnóstico. Os tokens não contêm formas A/B
corretas que tenham sido apenas perdidas pelo parser/agrupamento.

Coordenadas abaixo no espaço original da página, [x0,y0,x1,y1]; confidence
é a confidence do word Tesseract (0..1), não confidence estrutural independente.

| Região humana de diagnóstico | Tokens do prefixo / bbox / confidence | Raw line reagrupada | parse_marker |
| --- | --- | --- | --- |
| A | `A=(` / [152,508,197.5,530.5] / 0.7564; `.)` / [240.5,508,246.5,530.5] / 0.7119 | `A=( .) 26;`, bbox [152,507.5,292,530.5] | false |
| B | `Esto)` / [154,550.5,247,572.5] / 0.2209 | `Esto) 20;`, bbox [154,550.5,292.5,572.5] | false |
| C | `C-(` / [154,592,199.5,614.5] / 0.2605; `)30;` / [243,591.5,293,614.5] / 0.7686 | `C-( )30;`, bbox [154,591.5,293,614.5] | true, label C, explicit answer_marker |
| D | `D-(` / [155,634.5,200,657] / 0.2540; `)` / [243.5,634,249,657] / 0.2540 | `D-( ) 45.`, bbox [155,634,293,657] | true, label D, explicit answer_marker |

A existe como letra, mas a forma do marker está corrompida (`=` e `.`).
B não existe como token B: a região foi OCRizada como um único token `Esto)`,
unindo/corrompendo label e forma. C possui fechamento unido ao conteúdo `30;`,
mas o parser aceita seu prefixo; D tem fechamento separado e também é aceito.
Não é justificável reparar A/B por whitespace. Parser/Structure não alterados.
Diagnóstico completo, incluindo raw words no espaço 2x:
`outputs/audit/postmortem-v4/patch-05c1-complementary-ocr/05c1b/raw-q13-diagnosis.json`.

### Derivação geométrica prévia e única passagem gutter

Derivação em wrapper diagnóstico ignorado, NÃO em produção:

- Somente C/D explícitos do full pass; mesmo estilo dash/responseField=present,
  mesma página, selected complementar incomplete e não competing.
- Marker form bbox usa união de words intersectando spanEnd do prefixo parseado.
  Conserva cada token inteiro para não cortar o fechamento quando unido ao corpo.
  C: [154,591.5,293,614.5], largura 139; D: [155,634,249,657], largura 94.
- median marker x=154.5, median height=23; desvio X máximo=0.5, dentro da
  tolerância derivada da altura. A confiança baixa de um word não converte
  parsing explícito em recovery; strong aqui significa forma explicitamente parseada.
- Faixa X = median x menos uma altura até maior right do prefixo mais uma altura:
  [131.5,316]. Restringe ao boundary existente; Y permanece exatamente [221,716].
  Crop inward efetivo [132,221,316,716], imagem 184x495; OCR em 368x990.
- Mesma imagem raster cacheada, PIL LANCZOS 2x, Tesseract por+eng PSM6.
  Bbox de volta = [132,221] + bbox local/2. Sem GT/expected count/A-B esperados
  na derivação, coordenadas de target como regra, mudança de engine ou busca de parâmetros.

Uma tentativa inicial foi bloqueada ANTES de OCR pelo guard de compatibilidade:
o wrapper usou altura 1872, mas a imagem/cache primário têm altura 1871.
Corrigido SOMENTE o wrapper para ler a geometria do payload primário. O registro
da tentativa foi preservado como gutter-preflight-failed.json, executions=0.
Depois disso, exatamente **uma execução Tesseract gutter**, sem outra combinação.

### Resultado e STOP obrigatório

27 words / 10 lines; errors=[]; markers explícitos **B,C,D**, nenhum A.

| Região de diagnóstico | Gutter observed_as / raw line | Prefix words confidence | Parse |
| --- | --- | --- | --- |
| A | `Rel.) 28;`, bbox [152,507.5,292,530.5] | `Rel.)`=0.3069; `28;`=0.7969 | false |
| B | `B-( ) 20;`, bbox [154,550.5,292.5,572.5] | `B-(`=0.9051; `)`=0.8897 | true, B |
| C | `C-( )30;`, bbox [154,591.5,293,614.5] | `C-(`=0.7728; `)30;`=0.7933 | true, C |
| D | `D-( )45.`, bbox [155,634,293,657] | `D-(`=0.7574; `)45.`=0.8114 | true, D |

Full C/D + gutter B/C/D possui união observada B/C/D, C/D nas mesmas bboxes;
não há observação explícita A. Essa união é diagnóstico, NÃO merge/fallback
implementado em produção. Structure existente aplicada somente às linhas gutter
seleciona B/C/D, required=true, incomplete/missing_initial_label,
blocker=response_set_incomplete. Não se presume A nem se promove q13.

Cumprida a seção 4: **STOP**. aligned_marker_gutter_fallback não implementado;
TDD 05C1b RED/GREEN não iniciado, pois a condição diagnóstica anterior falhou.
Os 50 checks novos/467 holdout/14 suítes da etapa 05C1 anterior continuam sendo
a última validação conhecida; não foi alegado um novo GREEN nesta continuação.
Nenhum código funcional/teste/engine helper alterado nesta etapa. Nenhum aumento
de agreement/confidence por concordância entre passes; dados permanecem source
complementary_ocr/observationFamily=ocr_text do adapter 05C1, sem nova origem.

Não repetidos q17/q11/q13 pelo pipeline, nem replay final dos 30; q13 permanece
safe_abstention/null/unknown no resultado funcional anterior. newUnsafeRegressionCount
dos 30 continua não validado; patch05C1Complete=false. Sem staging/commit/push,
sem 05C2. A entrada de parada 05C1 foi preservada; CONTEXTO ganha somente registro
incremental do diagnóstico/parada 05C1b, NÃO fechamento concluído.

Artefatos gutter/raw JSON/crops/words/lines/parser ignorados sob `05c1b/`.
gutter-diagnostic.json SHA256:
`562a08b9b6a76173ae05c19f1cc2c65dbb6fc53090d20747fad27db61572ca6e`.
Baseline e targets 05C1 anteriores preservados com seus SHA256 acima.
Preservação dos 1.891 arquivos protegidos revalidada, incluindo todo holdout,
official result/GT/manifest/index/protocol, OCR caches primários e native cache.
Official SHA permanece 2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734.
officialAuditorExecutionCount=1; officialAuditorRerun=false;
complementaryOcrExecutions nesta continuação=1 (gutter), acumulado 05C1=4;
V4PerformanceClaimed=false; V5Required=true; merge=false.

## D. Decisão de NÃO transformar gutter em produção

Após as duas paradas, foi autorizada a conclusão da capacidade geral com q13
como limitação conservadora conhecida. Ausência de recovery em todos os targets
não invalida um fallback que exige observação explícita e conserva abstenção.

O gutter observou B/C/D, mas não A; portanto scope amplo não é o único gargalo.
Não implementar aligned_marker_gutter_fallback; não repetir gutter, buscar
parâmetros, reparar glyph por mapa/template ou inferir A pela presença de B/C/D.
Helpers/artefatos gutter permanecem somente nos outputs ignorados. Nenhuma mudança
funcional adicional foi feita no fechamento, nem testes para fazer q13 passar.

**q13 estabelece um limite conhecido de reconhecimento; a observação complementar
permanece conservadora e não infere o marker ausente.** q13 não é defeito de
segurança do contrato e permanece safe_abstention/null/unknown, promoted=false.

## E. Fechamento da capacidade — 2026-10-07

**A capacidade está concluída como fallback conservador de observação;
a recuperação dos targets permanece intencionalmente incompleta.**

### Contratos e diff audit

reliableBoundaryOnly=true; primaryFirst=true; localCropOnly=true;
cachedRasterPreserved=true; complementaryOcrEngine=tesseract;
complementaryOcrLang=por+eng; complementaryPsm=6; complementaryScale=2.0;
complementaryStructureSeparate=true; explicitMarkersOnly=true;
primaryCompatibilityRequired=true; duplicateObservationNotIndependent=true;
completenessGatesPreserved=true; GTUsedForActivation=false; boundaryChanged=false;
noParameterSearch=true; gutterFallbackProduction=false.

Revisado todo diff funcional: observations + holdout + mapeamento complementar
para origem textual em Fusion. Nenhuma regra por IDs/família/CMJF/CMBH/q13,
expected count/labels, crop de target ou recovery hardcoded A. Identidade existente
é usada somente para localizar caches/outputs/índice, nunca como critério de
ativação ou promoção. GT anterior permanece só no contrato de classificação;
não participa do novo caminho observacional. Boundary/Structure/parser/Regions/
visual detector/OCR helper global sem diff. Os quatro arquivos de produção/teste
05C1 conservam os hashes do início desta etapa de fechamento.

### Testes repetidos, sem novos checks

Initial RED=26; 50 checks novos 05C1 mantidos, holdout=467 checks PASS.
Selftests diretamente afetados observations/holdout/fusion repetidos PASS.
Todas as 14 suítes repetidas PASS: visual marker evidence, structure, regions,
holdout, fusion, boundary, OCR content, observations, V4 selector/protocol,
V3 selector, V2 R1/R2 e question index. py_compile PASS. OCR dos unit tests
continua stubbed/determinístico. Nenhum teste 05C1b ou exceção para q13 adicionado.
Logs e resultados em outputs/audit/postmortem-v4/patch-05c1-complementary-ocr/closeout/.

### Replay final dos mesmos 30 IDs

Uma passagem, exatamente 30 chamadas locais, baseline SHA e base 7cbdf63...
verificados; mesmos IDs/ordem dos findings 05A/05B. Nenhum CLI oficial/main/
evaluate_manifest, execução dos 144 ou tuning. GT somente no wrapper de
classificação revelada; fingerprints verificados e boundary inalterado nos 30.

newUnsafeRegressionCount=0; dois safety targets 05B permanecem non-unsafe.

| Target | Full markers | Gutter no replay | Completude / promoted | Before → after |
| --- | --- | --- | --- | --- |
| doc-eefc3d15076e:q17 | A-E explícitos | não executado | complete/required=true; true | safe_abstention/null/unknown → correct/5/A-E |
| doc-f4dd01071816:q13 | C,D explícitos | não executado; diagnóstico anterior B,C,D, sem A | incomplete/required=true; false | safe_abstention/null/unknown → safe_abstention/null/unknown |
| doc-5d61be2ac853:q11 | A-D explícitos | não executado | complete/required=true; true | safe_abstention/null/unknown → correct/4/A-D |

Nos três, primaryCompatibility=true e becameUnsafe=false. Só os conjuntos
completos observados alimentam a resposta efetiva. Agreement dos promovidos
continua partial, confidences medium/medium, sem dupla contagem.

| Controle | Before e after preservados | Observação complementar no replay |
| --- | --- | --- |
| doc-b605f7a51fd5:q5 | partial/5/unknown | não executada; visual 05A preservado |
| doc-f4dd01071816:q20 | safe_abstention/null/unknown | full A-D observado, NÃO promovido por conflito com E primário explícito |
| doc-800c2a22f148:q1 | safe_abstention/null/unknown | não executada; closure conservadora 05B preservada |
| doc-44ea716ed9b7:q54 | safe_abstention/null/null | não executada; unreliable/CID não decodificado |
| doc-0db5ce524459:q26 | safe_abstention/null/null | unreliable; trigger=false, executions=0 |
| doc-ad34c4cf7f30:q26 | safe_abstention/null/null | unreliable; trigger=false, executions=0 |

Efeitos adicionais gerais: doc-f4dd01071816:q5 observa A-D explícitos completos
e compatíveis, safe_abstention/null/unknown → correct/4/A-D; doc-42af2b3d2b27:q16
observa A-E explícitos completos e compatíveis, safe_abstention/null/unknown →
correct/5/A-E. Não são novas regras ou novos targets selecionados: já pertenciam
aos mesmos 30 e acionam o contrato geral. Os outros 26 estados classification/
count/labels são idênticos ao baseline.

doc-c41ddc7b55ec:q2 permanece safe_abstention/null/unknown: full complementar
observa D/E, incompleto e incompatível com A primário. Não inventa labels.
Pódion/q54 permanecem fora do scope; nome físico histórico Pódion não alterado.

replay30.json SHA256:
`a7eb2e64497c49e3538ef67466677ef25009f169a5347b5b579fbbb8f4e5e08c`.
replay-validation.json confirma IDs, controles, boundaries e safety PASS.

### Contabilidade de execuções e metodologia

complementaryFullOcrExecutions=3 no diagnóstico inicial dos três targets;
diagnosticGutterOcrExecutions=1, somente diagnóstico 05C1b. O replay final
necessariamente acrescentou replayFullOcrExecutions=7, em q17/q13/q11, q5 raster,
q2 raster, q16 raster e q20 raster; não confundir os três diagnósticos anteriores
com a contabilidade total. Total full=10; total complementar incluindo gutter=11.
Nenhum gutter executado pelo replay ou em produção.

officialAuditorExecutionCount=1; officialAuditorRerun=false;
V4PerformanceClaimed=false; V5Required=true. Dois dos três revealed diagnostic
targets obtiveram conjuntos explícitos completos: **NOT a coverage metric**.
Nenhum cálculo/claim pós-patch de precision, coverage, unsafe rate ou recovery
rate. V4 revelado é regression behavior, não avaliação imparcial; V5 blind requerido.

### Preservação e estado final

Byte-identidade revalidada contra dois snapshots: 1.891 arquivos pré-produção e
1.926 arquivos de evidência no início do fechamento. Incluem todo audit/holdout,
official V4 result, GT, manifest, index, protocol, OCR preparation, caches OCR
primários/PNGs, native visual caches congelados e todos os diagnósticos anteriores.
Novos outputs closeout isolados e ignorados; nenhum output staged. Configuração
Git preservada (core.autocrlf=true), sem .gitattributes/gitignore novos.

Official result SHA256 permanece:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.
CONTEXTO conserva histórico e ambas as entradas de parada; recebe UMA nova
entrada final após replay30 PASS. Brain e roadmap registram a decisão/estado,
sem transformar o brain em log de execução.

patch05C1CapabilityComplete=true; patch05C1Complete=true;
allRevealedTargetsRecovered=false; q13KnownRecognitionLimit=true;
gutterFallbackProduction=false; merge=false.
Próximo separado: **05C2 visual_header_and_layout_observation**, NÃO iniciado.
Possible marker-glyph recognition/alternate observation strategy fica somente
como futuro condicionado à recorrência do padrão q13; nenhuma tarefa/05C3 criada.

Ocorrência operacional no staging: a primeira chamada git add mencionou por
engano V4_TIER_B_ADJUDICATION.md, sem alterações. Diff cached confirmou que
nenhum artefato holdout entrou no stage; escopo final exatamente nove arquivos
05C1, nenhum output. Bytes congelados revalidados antes do commit.
