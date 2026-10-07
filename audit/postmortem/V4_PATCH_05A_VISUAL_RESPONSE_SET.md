# Patch 05A — visual_response_set_evidence

Base Patch04: `10f778593c06be50228035ebb911192cdbee7f06`.
Branch: `audit/holdout-v4-postmortem-fixes`; sem merge.

## Contrato observacional

O caminho nativo não fornecia render ao detector existente, e o runner raster
descartava hypotheses/ambiguidade antes da Fusion. Agora ambos compartilham:
crop pelo boundary → detector existente → filtro de boundary → associação com
linhas filtradas → hypotheses → somente markers do conjunto visual único.
`visualAlternativeEvidence` continua diagnóstico bruto, não autoridade de slots.
Com dois hypotheses plausíveis, nenhum marker visual fica ativo e o blocker
existente `competing_response_sets` permanece. Um/dois círculos não bastam;
`MIN_CLUSTER_SUPPORT=3` e todos os thresholds do detector permanecem iguais.

Native/hybrid fornece render somente com PDF canônico, boundary reliable e sem
selectedResponseSet textual autoritativo. Render a 160 DPI **não é OCR**; não há
Tesseract, glyph OCR, CID decoding, templates ou labels inferidos por ordem.
`enclosedGlyph=unknown`, slot.label=null; count pode ser emitido enquanto labels
permanecem unknown, somente quando Regions/content association e Fusion permitem.
O blocker `visual_only_content_region_missing` não foi removido nem relaxado.
Raw components podem fornecer conteúdo/math/media, mas não criam anchors.

Boundary.pageLimits é o crop real, incluindo x0/x1 de coluna. Limites em PDF points
são multiplicados por render_info.scale; pixels são arredondados para dentro da
janela. Evidence bbox volta para PDF points; width/height/area brutos também voltam
para suas unidades correspondentes. Nenhum window de benchmark foi copiado e
benchmark não é importado em produção. Renders estão no cache ignorado
`outputs/audit/native-render/`; traces/logs em
`outputs/audit/postmortem-v4/patch-05a-visual-response-set/`.

Correção objetiva de unidades: a tolerância e o score de alinhamento usam
coordinateScale para expressar a tolerância anterior na unidade do bbox. Sem isso,
duas colunas separadas em pixels poderiam virar um único cluster após a conversão
para points. O controle sintético P demonstra a separação e o round-trip com
tolerância de 0,01 point. Não houve retuning de valores do detector.

Provenance completa chega à Fusion e ao retorno do runner em visualDiagnostics:
visualObservationSource, visualAlternativeEvidence, visualResponseSetHypotheses,
visualResponseSetAmbiguous, visualResponseSet, activeVisualMarkerIndexes,
nativeVisualFallbackTriggered, renderedPages, visualPageGeometry e erros neutros
de observação. visualResponseSet conserva support/confidence/ambiguous/markerIndexes.
nativeVisualRenderExecutions conta invocações do helper cacheado, inclusive tentativa;
não deve ser interpretado como número de PNGs novos em uma execução com cache quente.
Neste replay foram duas invocações bem-sucedidas e dois PNGs novos, confirmados
pelos timestamps do cache. newOCRExecutions=0.

Arquivos funcionais: visual_marker_evidence, response_holdout, response_regions
(somente visualIndex original, não reindexação do subconjunto) e response_fusion.
A alteração mínima na Fusion impede que concorrentes visuais diagnósticos
sobreponham um conjunto textual autoritativo. Sem autoridade textual, o gate
concorrente permanece intacto. Controles J/K provam A-D/A-E com dois clusters
visuais e ruído: count/labels textuais não mudam. Membership/completeness dos
Patches01/02, Structure textual, boundary, observations/render helper e OCR intactos.

## TDD e validação

Antes de produção: controles A-W adicionados a audit_response_holdout_selftest.py;
RED=29 falhas novas, demais checks passaram. GREEN inicial=40 checks novos.
Um fixture de coluna tinha conteúdo atravessando o próprio x-limit; corrigido
somente o fixture. Depois foram acrescentadas verificações explícitas de crop
real, ausência de render e flags text-first/unreliable: GREEN final=45 checks.
Fixtures finais contra módulos Patch04 carregados em memória: RED=34 falhas;
não houve restauração/edição de arquivos funcionais para esse controle.

Cobertura: conjunto único/content/count sem labels inventados; um/dois rings;
scatter gráfico; concorrentes bloqueados; cluster + círculo isolado com refs
originais preservadas; ausência de conteúdo bloqueada; autoridade A-D/A-E;
C/E não promovido a single-choice; enumeração interna preservada; crop vertical
e coluna; scale/round-trip; unreliable/text-first sem render; fallback permitido;
render ausente/falha seguro; hypotheses na Fusion; raw components não são markers.
As 14 suítes atuais e py_compile PASS. Logs locais ignorados.

## Revealed regression sample — 30 IDs originais

Baseline salvo antes de produção, usando a base Patch04 atual, não o resultado
oficial pré-patches. Depois foram executados somente os mesmos 30 IDs originais
(24 safe congelados + cinco unsafe + um partial do postmortem). GT somente no
wrapper para classificação diagnóstica; nunca ativa fallback ou escolhe markers.
Nenhum main/evaluate_manifest/CLI oficial nem execução dos 144.

Uma tentativa after foi interrompida no primeiro ID por comparação do wrapper
entre chaves inteiras de boundary e chaves serializadas como strings em JSON.
Correção somente no wrapper ignorado: comparar a representação JSON. Depois,
passagem completa dos 30, boundaries idênticos ao baseline. Total=61 chamadas
locais (30 before + uma tentativa after + 30 after final), 30 IDs únicos.
Rechecagem RED em memória inicialmente rejeitou BOM do módulo base; leitura
utf-8-sig corrigida apenas no wrapper, antes de executar testes nessa tentativa.

| questionId | before classification/count/labels | after classification/count/labels |
| --- | --- | --- |
| doc-b605f7a51fd5:q5 | safe_abstention/null/null | partial/5/unknown |
| doc-b605f7a51fd5:q20 | safe_abstention/null/null | partial/5/unknown |

Os outros 28 conservam classification/count/labels. newUnsafeRegressionCount=0.
Isso inclui **dois unsafe já presentes no baseline Patch04**, detectados agora
ao incluir os cinco controles observacionais que não pertenciam ao replay Patch04.
Não são regressões introduzidas pelo Patch05A, nem foram corrigidos nesta etapa.

### Target q5

doc-b605f7a51fd5:q5: boundary reliable; page 4, limits top=110,732/bottom=501,022.
Before: nenhum render/evidence/hypothesis/slot; count=null, labels=null, blockers=[].
After: nativeVisualFallbackTriggered=true; renderedPages=[4]; scale=160/72;
cropPixels=[0,247,1323,1113], cropPoints=[0.0,111.15,595.35,500.85]
(coordenadas decimais em points; vetor x0,y0,x1,y1).
Seis visual candidates brutos; um hypothesis, ambiguous=false, support=5,
confidence=high, adjacentContentEvidence=1; markerIndexes=[1,2,3,4,5].
Cinco active markers, cinco slots/answer_options, content present=5/missing=0.
O candidato isolado do enunciado permanece bruto, sem slot/count adicional.
optionCount=null→5; optionLabels=null→unknown; blockers=[]→[];
safe_abstention→partial; becameUnsafe=false. Nenhum glyph identificado/inventado.

q20 do mesmo documento é efeito incidental do contrato geral: evidence=5,
hypotheses=1/support=5, active=5, partial/5/unknown, sem adaptação específica.

### Cinco controles de observation capability — não targets

| questionId | before e after (inalterados) |
| --- | --- |
| doc-eefc3d15076e:q17 | unsafe_error/3/unknown (preexistente na base atual) |
| doc-f4dd01071816:q13 | safe_abstention/null/unknown |
| doc-5d61be2ac853:q11 | unsafe_error/3/A-C (preexistente na base atual) |
| doc-0db5ce524459:q26 | safe_abstention/null/null |
| doc-ad34c4cf7f30:q26 | safe_abstention/null/null |

Nenhuma recovery/tuning direcionada a esses cinco; observation complementary
continua separado. doc-f4dd01071816:q20 permanece safe_abstention/null/unknown;
doc-44ea716ed9b7:q54 permanece safe_abstention/null/null, boundary uncertain,
sem render fallback e sem CID decoding. Gates anteriores não foram contornados.

Baseline before.json SHA256:
`0d94883b04507f6d0f0cb1fa57c290a0de73d87417b4028c7f289785793408a7`.
After after-validated.json SHA256:
`d1249a2ec24ce822c00c75f088fb9deda32583760b8c69d2931850e2e8cb58f9`.

## Preservação e metodologia

1.816 arquivos protegidos byte-idênticos: todo audit/holdout, GT, manifest,
question index, protocol, OCR preparation/caches e evidências anteriores.
Resultado oficial SHA256 preservado:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.
Diff sem IDs/famílias/anos/páginas/GT/contagens esperadas como regras funcionais;
sem associação A-E por posição, detector novo, threshold tuning, OCR, boundary,
Structure/completeness ou alterações de gitignore/config. CONTEXTO conserva
histórico e recebe somente uma entrada incremental; brain recebe resumo/link.

officialAuditorExecutionCount=1; officialAuditorRerun=false; newOCRExecutions=0;
nativeRenderExecutions=2; V4PerformanceClaimed=false; V5Required=true.
V4 revelado é apenas desenvolvimento/diagnóstico/regressão, **not an unbiased
evaluation**. Nenhuma claim de precision, coverage, unsafe rate ou recovery
percentage pós-patch. V5 blind continua obrigatório.

Patch05AComplete=true; next=observation_complementary_capability, não iniciado.
Limitações restantes: labels visuais unknown; detector existente não prova glyph
nem ausência universal de candidatos invisíveis; dois unsafe observacionais
preexistentes nos controles. Sem merge.
