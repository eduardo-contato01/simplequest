# Patch05C2 — visual_header_and_layout_observation

Branch: `audit/holdout-v4-postmortem-fixes`.
Base/HEAD: `8e1779e6a9bcdc517a33a0ff8b33154d3befd09e` (05C1 publicado).

**Estado final: diagnostic experiment / parked capability.**
patch05C2Complete=false; promotedToProduction=false; experimentParked=true.
0/2 targets revelados recuperaram boundary confiável; isso não é failure rate,
coverage ou medição imparcial. Testes sintéticos GREEN não forneceram validação
positiva real. Por decisão externa, produção e testes 05C2 foram revertidos para
o HEAD 05C1 publicado, sem novo OCR, tuning ou ampliação sobre V4 revelado.
Baseline funcional ativo=Patch05C1. Próximo=Holdout V5 blind, NÃO iniciado.

As seções seguintes preservam o histórico do experimento/parada; não descrevem
uma capacidade ativa do Auditor. O fechamento documental está na última seção.

## Preflight e baseline antes de produção

Branch/HEAD esperados, working tree e stage vazios, git diff --check PASS.
Resultado oficial SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

Baseline fresco dos mesmos 30 IDs/ordem dos findings, na base publicada 05C1:
`outputs/audit/postmortem-v4/patch-05c2-layout-header/baseline.json`.
SHA256: `ba98e2e975d81bf93b6c8df8507d3eb2236f347d0d5f501dc24a6607c3f92467`.
Classification/count/labels reproduzem os 30 estados do replay final 05C1.
O baseline acionou sete passes locais 05C1; nenhum header OCR nessa fase.
GT somente no wrapper de classificação diagnóstica, nunca em layout/header/ativação.
Nenhum main/evaluate_manifest/CLI oficial ou execução dos 144.

## Diagnóstico visual anterior ao código funcional

Somente dois PNGs existentes: doc-0db5ce524459 p13 e doc-ad34c4cf7f30 p9.
Nenhum PDF aberto, render novo, rename, alteração de manifest ou fingerprint.
Nome físico histórico 6ANO do primeiro documento permanece intacto; a informação
humana de que a prova visual é 7º Ano não é regra funcional.

Image-only diagnostic contém dimensões, grayscale vertical projection, ink density,
rule/valley candidates, regiões com largura/área, primary words por região, linhas
colapsadas e todas as entries do frozen index com pageStart naquela página.
`image-diagnostic.json` SHA256:
`923567fb80b18c34d92e711e5f3422ce81b0f254b0ab0d49b49f7a46a9e5e24a`.
newOcrExecutions=0 nesta fase; nenhuma busca de parâmetros.

## Capacidade local e contrato

- Hierarquia preservada: matcher normal de linhas -> fallback 03C -> somente
  current_marker_not_found em raster espacialmente colapsado -> layout/header.
  Reliable/ambiguous/nativo/sem índice/sem PNG/geometria incompatível não autorizam
  nova leitura. Multipágina visual permanece não suportada conservadoramente.
- Colapso é objetivo: linha >60% da largura e altura >10% da página e >6 vezes
  a altura mediana das words. Nenhum documentId/questionId participa da ativação.
- Layout usa somente imagem, com análise reduzida a no máximo 800 pixels de
  largura. Grayscale + limiar Otsu derivado da página servem SOMENTE à proposta;
  não são preprocessing do OCR, que recebe o raster original cropped/2x.
- Rules estreitas são rastreadas entre linhas, tolerando inclinação/gaps limitados
  por dimensões. Exigem extensão >=50% da altura e cobertura >=45%. Page frame
  é excluído pela área utilizável em ambos os lados (>=15% da largura) e densidade
  adjacente >=30% da mediana de densidade positiva da própria página.
- Valleys exigem largura >=1,5%, densidade <=20% dessa mediana e conteúdo adjacente
  em ambos os lados. Evidências próximas (2% da largura) formam uma mesma proposta;
  propostas distintas permanecem ambíguas, nunca escolhidas só pela imagem.
- Nenhuma preferência left/right, split em 50%, palavra RASCUNHO/CÁLCULO ou
  classificação/remoção de manuscrito. Essas palavras não definem question column.
- Header OCR limitado em X a cada região proposta, Y pode cobrir a página.
  Tesseract existente por+eng / PSM6 / PIL LANCZOS 2x, uma configuração fixa.
  Crop inward; bbox original = offset + bbox local/2; cache primário não modificado.
- Matching reutiliza exatamente identity/grammar/resolução 03A/03C. Run requer
  >=2 headers explícitos index-backed da página, ordem vertical compatível com
  ordem documental, sem duplicatas. Números não indexados não contam.
- Target único é obrigatório, mesmo com peers; target em duas regiões bloqueia.
  Next observado fornece bottom normal; next exigido na mesma página e ausente
  continua next_marker_not_found. Page end somente pela política existente quando
  next está fora do intervalo ou inexiste, explicitamente diagnosticada.
- X-limits visuais corroborados têm provenance distinta do peer geométrico 03B.
  Saída conserva primaryBoundary, layoutObservation, recoveredBoundary e
  effectiveBoundarySource. Ausência conserva primary; conflito=none/conflict.
- Headers carregam source=layout_header_ocr, observationFamily=ocr_text,
  isComplementary, layoutRegionId, bbox/confidence, matchGrammar, indexQuestionId
  e canonical/printed identity. Passes da mesma imagem NÃO são fontes independentes.
- OCR bruto pode conter alternativas, mas 05C2 consome somente starts para boundary.
  Header words/lines não são passadas à Structure/Regions. Boundary recuperado
  filtraria o bundle PRIMÁRIO pelo caminho normal; 05C1 mantém elegibilidade geral,
  sem chamada especial por target, alteração de completude ou inferência de labels.

Arquivos funcionais locais: observations, question_boundary e holdout.
Structure, Regions, Fusion, visual detector e OCR helper global inalterados.

## TDD RED/GREEN

26 falhas novas RED registradas ANTES de produção; controles anteriores PASS.
GREEN: 30 checks 05C2 PASS, incorporados à suíte boundary, sem Tesseract real.
Fixtures A-Z: reliable/ambiguous/sem cache; rules/frame/valley estreita/one-sided;
propostas ambíguas; neutralidade; runs 24..26 e 26..28; target ausente/duplicado
em uma ou duas regiões; número 77 não indexado; top/next/page-end; X-limits;
ruído visual e palavras scratch não criam política; mesma família; integração
primária/05C1; isolamento de options, crop round-trip/provenance e imutabilidade.
14 suítes existentes PASS + py_compile antes do diagnóstico real.
Logs `tdd-red.log`, `tdd-red.json`, `tests.json` e logs das suítes em outputs ignorados.

## Diagnóstico real único — limite observado e parada

Quatro execuções header OCR (duas regiões por página). Sem erros de engine/crop,
sem variação de PSM/scale, sem parameter search, sem processamento do manuscrito.

| Target | Imagem | Regiões X propostas (Y=0..altura) | Evidência | Headers index-backed / seleção |
| --- | --- | --- | --- | --- |
| doc-0db5ce524459:q26 | 4283x6208 | [0,2109.3775]; [2253.92875,4283] | vertical_rule | nenhum; nenhuma região selecionada |
| doc-ad34c4cf7f30:q26 | 1323x1872 | [0,653.23125]; [694.575,1323] | vertical_rule + whitespace_valley | somente q25 na região0; run insuficiente, nenhuma seleção |

Primeiro target: região0 produziu 187 words / 51 linhas, região1 55 / 34.
Não observou header q26 utilizável; linha de q27=`E QUESTÃO 27 |` possui prefixo
não decorativo, não aceito pela gramática ancorada. Não remover E ou reinterpretar
tokens para promover o header. Mesmo q27 isolado não provaria target q26.

Segundo target: região0 259 words / 66 linhas, região1 141 / 40. Linhas:
`FquestTÃO 24`, `Questão 25`, `EQuEsTÃO 26`. q25 é explicitamente reconhecido;
keywords q24/q26 estão corrompidos, apesar de números 24/26 observados. Não reparar
keyword por fuzzy substitution, retirar prefixo nem inferir q26 pelo índice.

Ambos: beforeReliable=false/current_marker_not_found;
recoveredReliable=false/layout_target_not_found; targetHeader=null; nextHeader=null;
effectiveBoundarySource=primary. primaryBoundary não é silenciosamente promovido.
Regiões corretas como proposta não garantem reconhecimento do header.

`header-diagnostic.json` SHA256:
`7ad63e1db4690e48480472cd9c3a50c75c0db47abc1423b7879aae80f1bcfc6d`.
Crops original/2x, raw OCR/confidence, words/lines mapeadas e runs salvos sob
`outputs/audit/postmortem-v4/patch-05c2-layout-header/headers/`.

## Pipeline, replay e safety NÃO concluídos

Conforme seção 29, STOP depois dos dois diagnósticos: nenhum pipeline completo
pós-patch dos targets, 05C1 nesses targets ou replay30 final foi executado.
Before de ambos=safe_abstention/null/null; after classification/count/labels e
becameUnsafe NÃO avaliados. Não declarar newUnsafeRegressionCount=0 pós-patch.
Os quatro OCRs forneceram apenas diagnóstico neutro de boundary, não respostas.

Controles abaixo foram preservados no baseline fresco, não revalidados em replay
final: q17 correct/5/A-E; q11 correct/4/A-D; q13 safe_abstention/null/unknown;
q5 visual partial/5/unknown; q20 e q1 conservative; q54 safe_abstention/null/null.

## Preservação, ingestão futura e metodologia

Snapshot de 1.972 arquivos protegidos antes de produção: todo audit/holdout,
resultados oficiais/GT/manifest/index/protocol/OCR preparation, caches OCR primários,
native visual caches e TODA evidência anterior, incluindo 05C1/closeout/gutter.
Byte-identidade revalidada após STOP; outputs novos separados/ignorados.
Config Git preservada; core.autocrlf=true; sem .gitattributes/gitignore novos.
git diff --check PASS; avisos LF/CRLF esperados, nenhuma mudança de configuração.
CONTEXTO recebe somente UMA nova linha incremental de parada; histórico preservado.

Pódion é material interno/scanner; não publicar automaticamente. Nota de ingestão
FUTURA em brain/IMPORTADOR.md propõe catalogEligible=false,
usageScope=internal_audit_training e sourceProvenance=scanned_physical_copy.
Sem lógica de site/publicação, nem alteração de manifest V4 ou influência no Auditor.
Roadmap, ESTADO_ATUAL e AUDITORIA_PROVAS não foram marcados concluídos.

officialAuditorExecutionCount=1; officialAuditorRerun=false;
layoutHeaderOcrExecutions=4; baseline05C1OcrExecutions=7;
GTUsedForLayoutHeader=false; parameterSearch=false;
V4PerformanceClaimed=false; V5Required=true. V4 é material diagnóstico revelado,
não avaliação imparcial, coverage/precision/recovery-rate ou métrica pós-patch.

Working tree alterada localmente, stage vazio; HEAD/base inalterado.
patch05C2Complete=false; merge=false. Sem novo commit/push. Não iniciar V5.
Decisão externa necessária antes de qualquer fechamento conservador ou refinamento.

## Fechamento documental — decisão externa, 2026-10-07

05C2 estacionado, NÃO promovido e NÃO concluído como patch funcional. Layout regions
foram detectáveis, mas header OCR não sustentou target identity: A sem indexed headers,
B somente q25, target q26 não observado como header válido; nenhum boundary recuperado.
Continuar exigiria ampliar/tunar a observação sobre V4 revelado, aumentando risco
de overfitting antes de avaliação blind. Revisitar somente se evidência futura/blind
justificar. Visual region proposal pode ser reutilizada futuramente, não é Auditor ativo.

### Classificação e restauração

- A, produção: scripts/audit_observations.py, audit_question_boundary.py e
  audit_response_holdout.py — alterações 05C2 revertidas integralmente para 8e1779e....
- B, testes: audit_question_boundary_selftest.py restaurado; arquivo exclusivo
  scripts/audit_visual_layout_selftest.py retirado da branch funcional.
- C, relatório: este diagnóstico preservado, com estado final explícito.
- D, CONTEXTO: entrada de parada preservada; UMA nova entrada final curta.
- E, documentação: ROADMAP/ESTADO_ATUAL/AUDITORIA_PROVAS registram parked/non-promoted;
  nota futura Pódion em IMPORTADOR preservada integralmente.
- F, outputs: diagnósticos ignorados preservados; diff da tentativa e selftest
  exclusivo arquivados em outputs/.../patch-05c2-layout-header/parked-source/.

Arquivos restaurados comparados byte a byte com blobs do HEAD 05C1; git diff scripts
vazio. productionRestoredTo05C1=true; testsRestoredTo05C1=true;
productionDiffFrom05C1=false; patch05C2TestsInProductionBranch=false.
Status Git residual sem diff foi limpo por update-index --really-refresh, sem
git add de código, mudança de core.autocrlf ou .gitattributes.

Somente documentação/histórico participa do commit
`audit: park visual header layout experiment`; functionalFilesStaged=0.
As 14 suítes do baseline 05C1 restaurado e py_compile PASS neste fechamento,
com Tesseract real explicitamente bloqueado nos testes. newOcrExecutions=0.
Preservação revalidada: 1.972 arquivos protegidos e 59 artefatos do experimento
anteriores ao fechamento, incluindo código/teste arquivados; logs novos isolados
em outputs/.../patch-05c2-layout-header/park-closeout/.
Sem replay30/144, novo OCR, PSM/scale/preprocessing/header repair/inferência,
novas regras left/right ou utilização de scratch words. parameterSearch=false;
GTUsed=false para layout/header e neste fechamento; GT histórico do baseline
permanece somente no wrapper de classificação, como documentado acima.
Nenhum claim unsafe pós-patch: produção experimental descartada, não validada
ou promovida por resultado sintético. Nenhuma nova métrica V4.

Resultado V4/GT/manifest/index/protocol/OCR preparation/caches primários e evidências
05C1 anteriores preservados; baseline funcional permanece 05C1. Nota Pódion não
altera catálogo/site/manifest/fingerprint ou nome físico. Outputs não são staged.
Próximo=holdout_v5_blind, com protocolo separado; NÃO criado nesta execução.
Após commit documental/push, parar; merge=false.
