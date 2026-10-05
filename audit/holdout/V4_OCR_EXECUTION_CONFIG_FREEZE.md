# Holdout V4 - freeze da configuracao OCR de execucao

- Branch: audit/holdout-v4.
- Source HEAD: d9a37577c844213152a9db8c3cded1166c3a4cb9.
- Preparacao UTC: 2026-10-05T19:39:19.763789+00:00.
- Config: audit/holdout/ocr-execution-config-v4.json.
- Config file SHA256 (bytes UTF-8 sem BOM, LF): daa2fd7840901d587a75301cfde76b6dcfc0f3cf57b68bf4db13eb4f03605182.
- Ground Truth V4 ja congelado no commit d9a37577c844213152a9db8c3cded1166c3a4cb9, preservado.
- Auditor V4 ainda nao executado; priorV4OfficialRunDetected=false.
- Preflight anterior: officialRunReady=false; fontes/schema/bindings, self-tests e 48/48 fingerprints PASS; preparo bloqueado por caches ausentes e falta de configuracao formal de execucao.
- A configuracao formal deste artefato resolve a indefinicao de configuracao; apos seu commit, officialRunReady=false somente por caches pendentes.

## Base metodologica e configuracao herdada

- inheritedFromV3=true.
- Precedente: audit/holdout/results/auditor-v1-holdout-v3-first-run.provenance.json.
- File SHA256 do precedente: 45e6460fb6656c3d8ac05372e64c948e589fab9248de159208ffc0de4ff32398.
- Configuracao herdada do OCR oficial V3, sem usar performance ou conteudo V4 para escolher parametros.
- engine=tesseract; dpi=160; psm=6; lang=por+eng; fullDocumentOcr=true.
- O PSM 11 do question index V4 pertence exclusivamente ao indexador neutro, separado dos caches do Auditor; questionIndexPsm11Reused=false.
- Todos os documentos que exigem cache receberao OCR de todas as paginas, nao apenas das tres questoes selecionadas.
- A politica full-document reproduz a preparacao oficial anterior, nao condiciona o preparo ao sorteio, mantem todas as paginas disponiveis e evita page-selection adaptada ao V4.
- retunedFromV4=false; v4ResultsAvailableAtFreeze=false; v4ResultsConsultedForDecision=false.
- Nenhuma metrica V4 foi gerada ou consultada; nenhum PSM alternativo testado; nenhuma heuristica ou codigo funcional alterado.

## Ambiente observado, sem alteracao

- Tesseract path: C:\Program Files\Tesseract-OCR\tesseract.exe.
- Tesseract version: tesseract v5.4.0.20240606.
- Tessdata path: C:\Users\trans\Documents\SimpleQuest\tmp\tessdata.
- Idiomas obrigatorios por e eng disponiveis; idiomas observados: eng, osd, por.
- pdftoppm path: C:\Users\trans\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.EXE.
- pdftoppm version: pdftoppm version 26.07.0.
- pdftoppmVersionDriftFromV3=true; previousVersion=25.07.0; currentVersion=26.07.0.
- reason: local environment/tool version changed before any V4 Auditor run.
- Drift de ferramenta registrado antes de qualquer run V4, sem tuning baseado em resultados V4; o parametro funcional de renderizacao permanece dpi=160.
- Nenhuma instalacao, troca de versao, alteracao de PATH ou retuning nesta etapa.

## Cache consumidor e preparo pendente

- cacheConsumerPathPattern: outputs/audit/ocr/<documentId>/tesseract/.
- ocrPayload: outputs/audit/ocr/<documentId>/tesseract/ocr.json.
- renderedPages: outputs/audit/ocr/<documentId>/tesseract/rendered/.
- Caches necessarios=16 (15 raster + 1 hybrid); caches existentes=0/16; caches gerados nesta etapa=0.
- Os 16 diretorios tesseract/ continuam ausentes, como no preflight.
- O OCR neutro historico do indexador e separado e nao foi reutilizado como cache de execucao do Auditor.
- Nenhum OCR V4 destinado aos caches da primeira execucao oficial foi executado antes deste freeze; nenhum OCR sera executado nesta mesma etapa, mesmo apos o commit.

Documentos pendentes:

- doc-0db5ce524459
- doc-143e13dc75ed
- doc-2790a3c9786b
- doc-42af2b3d2b27
- doc-56268e79f6bf
- doc-591f3e819d58
- doc-5d61be2ac853
- doc-89561bb8f1fe
- doc-a1ddc006ef56
- doc-ad34c4cf7f30
- doc-c41ddc7b55ec
- doc-c573e686e882
- doc-cf6b56e7abd7
- doc-eefc3d15076e
- doc-f03e7d17eec1
- doc-f4dd01071816

## Freeze formal e proximo passo

- O commit Git que introduz este JSON constitui o freeze formal da configuracao OCR da primeira execucao oficial V4.
- Nenhum cache para essa execucao pode ser gerado antes desse commit existir.
- Proximo passo permitido apos o commit, em etapa separada: gerar os 16 caches full-document conforme a configuracao congelada e revalidar a prontidao.
- Auditor=false; evaluate_manifest nao chamado; nenhuma metrica ou resultado V4 criado.
- GT, manifest, question index, protocolo e codigo funcional preservados; nenhum merge.
