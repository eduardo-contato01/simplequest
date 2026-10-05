# Holdout V4 - freeze da preparacao dos caches OCR

- Branch: audit/holdout-v4.
- Source HEAD: 5c3263e0f2e9d3f9e8aa490a4fb6b2e45455eae3.
- Revalidacao UTC: 2026-10-05T21:50:52.576725+00:00.
- Configuracao autoritativa: [ocr-execution-config-v4.json](ocr-execution-config-v4.json), congelada no source HEAD.
- Config file SHA256: daa2fd7840901d587a75301cfde76b6dcfc0f3cf57b68bf4db13eb4f03605182.
- Manifest de preparacao: [ocr-cache-preparation-v4.json](ocr-cache-preparation-v4.json).
- Preparation file SHA256 (UTF-8 sem BOM, LF): fc99bf156715b971c2739cff8073d6880d8dbc08394408a67dbaeef9dc0aef98.
- cacheSetCanonicalJsonSha256 pos-normalizacao: 13c7694f146155ab4f3bdd9e9b3700a556b7c81fbb2ecebc48fbafd34ef59f37.
- Ground Truth V4 congelado no commit d9a37577c844213152a9db8c3cded1166c3a4cb9 e preservado.
- Nenhuma execucao oficial V4 detectada; priorV4OfficialRunDetected=false.

## Configuracao e geracao preservadas

- engine=tesseract; engineVersion=tesseract v5.4.0.20240606; dpi=160; psm=6; lang=por+eng; fullDocumentOcr=true.
- Configuracao herdada do V3 oficial; PSM 11 do indexador neutro nao reutilizado.
- pdftoppm version 26.07.0; path congelado: C:\Users\trans\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.EXE.
- Na geracao anterior, o pdftoppm foi fixado somente no PATH do processo filho; nenhum PATH persistente alterado.
- Drift V3 25.07.0 -> 26.07.0 previamente registrado no freeze da configuracao, sem tuning V4.
- 16 documentos na ordem do manifest-v4-b.json: 15 raster + 1 hybrid; 315 paginas full-document.
- Cada cache foi gerado uma unica vez em outputs/audit/ocr/.v4-cache-build/<documentId>/<pdf-slug>/tesseract/, validado antes de mover, e relido no destino consumido pelo runner.
- JSON e PNGs conferiram byte-identicamente entre temporario e destino; somente depois foram removidas as pastas temporarias vazias.
- Caches finais: outputs/audit/ocr/<documentId>/tesseract/ocr.json e rendered/.
- Nenhum cache pre-existente sobrescrito; temporarios ausentes e caches finais preservados localmente.

## Normalizacao mecanica de filenames autorizada

- Interrupcao inicial real preservada no CONTEXTO: 43/43 required pages fisicamente presentes, mas lookup do runner 41/43 por padding no documento de quatro paginas.
- Contrato congelado do runner, sem mudar codigo: page-{page:02d}.png.
- Scan global antes de qualquer rename: renderedFilesScanned=315; collisionCount=0; nomes invalidos=0; targets duplicados=0; destinos diferentes pre-existentes=0.
- renderedFilesRenamed=4, todos em doc-c41ddc7b55ec: page-1.png -> page-01.png; page-2.png -> page-02.png; page-3.png -> page-03.png; page-4.png -> page-04.png.
- Renames/moves no mesmo filesystem, sem re-encode, sem salvar imagens, sem aliases ou arquivos extras.
- SHA256 dos 315 PNGs conferidos antes/depois por documentId/pagina; PNG contentBytesChanged=0.
- ocrJsonChanged=0/16: todos os hashes permanecem exatamente os fornecidos na autorizacao.
- ocrRerun=false; tesseractInvocationsDuringRepair=0; pdftoppmInvocationsDuringRepair=0.
- renderedSetCanonicalJsonSha256 recalculado a partir de [[relativeFilename, sha256], ...] ordenado por filename, com scripts.audit_holdout_schema.sha256_json.
- Somente o rendered set de doc-c41ddc7b55ec mudou: 0cc54738b92d299ca19d171028cef5c69ddb82acf1da250ad7c0be54074d727d -> dc674d949b50474b0c5dce2f052691122d1edee2fac1d6b827805f4e4777dd76.
- Os outros 15 rendered set hashes permaneceram iguais.
- Global hash recalculado sobre as 16 entries completas, na ordem do manifest, pela mesma funcao canonica.
- Hash global anterior d36f9a1ea7205c36cbbf058f5fdc192bf32f1f2fda468ae436b220aead155999 e somente o snapshot PRE-normalizacao, nao o freeze final.
- A normalizacao nao altera configuracao OCR, arquitetura, conteudo OCR, decisoes humanas ou Ground Truth.

## Validacao final cega

- 16/16 ocr.json relidos do destino: parse/config/version/fingerprint/pagesProcessed/sequencia 1..pageCount PASS.
- firstPage=null e lastPage=null em todos os payloads; full-document 16/16.
- 16/16 rendered dirs presentes, contagem de PNGs igual a pagesProcessed, nomes exclusivamente canonicos.
- runnerAddressableRenderedPages=315/315; requiredPagesPhysicallyPresent=43/43; requiredPagesRunnerAddressable=43/43.
- doc-c41ddc7b55ec: page-03.png e page-04.png presentes; page-3.png e page-4.png ausentes.
- Hybrid doc-f03e7d17eec1: 39 paginas completas; page-37.png presente no payload e no path literal.
- 16/16 PDF fingerprints dos caches e 48/48 PDF fingerprints do manifest conferidos.
- Schema/protocolo/manifest/indice final/GT e bindings PASS; 144 selected IDs e pages do indice preservados.
- Sete self-tests pertinentes existentes PASS em fixtures de desenvolvimento, sem avaliar V4: OCR content, response structure, visual marker evidence, response regions, fusion, observations e question boundary.
- 229 arquivos protegidos (audit/holdout pre-existente e scripts) byte-preservados.
- GT frozen=true; OCR config frozen=true; frozenOCRConfigurationIdentifiable=true.
- cachesReady=16/16; cachesMissing=0; requiredPagesMissing=0; officialRunReady=true.
- Nenhuma qualidade OCR avaliada, nenhum OCR comparado com GT, nenhuma fusion/classification dos caches V4 executada.

## Hashes finais por documento

| Documento | Paginas | ocrJsonSha256 | renderedSetCanonicalJsonSha256 |
| --- | --- | --- | --- |
| doc-0db5ce524459 | 15 | 4cd2330bc16aae87b3f9554130ed5946befc87d114975947b32b346bc9b18842 | 3c7deafa0ef50b64e4ebb50247110a5fca3937fd4dd434af91e9349d609494fa |
| doc-143e13dc75ed | 20 | 182c71f60f6d3180e65dbbac05b20cf0aeb87ca8e9f49d50e6a4ef4368de6e70 | a92fbc0135984c1f7bee2c9ec5c7dac2f73d880925d90b5a6e46a685c174a3de |
| doc-2790a3c9786b | 19 | bac7668282896e5623052e96646bffd3555e84c0c6cbfa5c0be4e9e9d2ee5a9d | 0722eb6d01f0f2b1467eaea753129e904a940e66f0ba3efd90bdb26728e45bda |
| doc-42af2b3d2b27 | 19 | e56f3e24fac274aea378ca5f54efdcb07271d53108846a5d640801d5bd78ae60 | 4d5dc98177137986476c266b5fe96d08bbf8030ee33053c29067df447fe9d0cb |
| doc-56268e79f6bf | 22 | a747735d8730e7b6c527c3d85f3bf465ee6cb91aa6206b41545695af47090c75 | 2acab8fd1768d92315ede81be4cef1bdc3314333a2d596ce34fe6ba3f3d91768 |
| doc-591f3e819d58 | 15 | 816c45167ceb71c5d4639291324bb6c314e155cd6882d76048031a38572ba88a | 237ef4c81891f89bdc79bcef6bcc20a9298926629e2c5ea2d922f3f58e68f71d |
| doc-5d61be2ac853 | 13 | 8dc0a21cf9890137d123d3ce56081e99ec0e2ea3adf02529fd674e801de8006a | a1aff311db38e0c80e4c9b3f63b5f166bb580d6721e94b06761390f4772cc1fa |
| doc-89561bb8f1fe | 11 | f12616094645875e265811815d977a91bf89dbb05f60b5340bf88d3bbdd66d9e | 6c5b43dc54779291163e7ae23f8b71e17f9c4ec130d40a505022969b4ebbf7ac |
| doc-a1ddc006ef56 | 24 | a21b32b72d9b0a5d2add3be0a132002e0372acacac46fdc836e280163a9ad165 | 4c49984d6f8315b8de0828b9605a85cb890e37306f2a6c35876a0464c595e1d6 |
| doc-ad34c4cf7f30 | 14 | 77cc4ab829510f46cb1409640d168eb4bf28331d3c26fa8aab5fb844a281ec29 | 47e535981be371745ceef4d7c15b8f07d72c843b719db3f10e9ec0d30f082172 |
| doc-c41ddc7b55ec | 4 | 7d07c151b707aaa658097f9e84c297af6cebb918ca6fc15ab551fdfdf77c20a2 | dc674d949b50474b0c5dce2f052691122d1edee2fac1d6b827805f4e4777dd76 |
| doc-c573e686e882 | 20 | 56ad5efdc14f4f80cc1154b2dbe8a68f9818189e0120585e19c37f576e202751 | 4db50de3a9c09378531c86ed7a5afd995a9ef5eef9de785cfe77b04707b0ce96 |
| doc-cf6b56e7abd7 | 20 | 56c9cea339e8a6aede5b18096cee73bcd877fce33dd3adc869d361ee9fda707a | 0cdb652ec413595fb6152b86b70adda6cefc22071e45a4a830815d3ea001c6b4 |
| doc-eefc3d15076e | 39 | 868058a2de5882f7c19fef20217b29a79a3013841317a714248fb3f73887c25e | 1f0d52a9e97920d29f8d479481ee7b19772469cbfa0c8023e4f46f6fc4d7a0f0 |
| doc-f03e7d17eec1 | 39 | f858189a97413b73b0f0f2b29ad2d8cb09180ab2d9c97489dec829c2aa81409a | 9f706c9a89eca2a602ef139277d969789788a1a67a0fb7ae8c6e10f4ad322bd8 |
| doc-f4dd01071816 | 21 | d6653f6fbd40a8622d508f1c23605ac8955d9d1d887cb2f09d79fdd8b460a24c | f0146b0372de7af3c622bcf7f727f48fa3f7ea62e8c167bfc2e30fabb391387f |

## Seguranca experimental e freeze

- configurationChanged=false; alternateParametersTested=false; v4ResultsConsulted=false; metricsGenerated=false; evaluateManifestCalled=false; auditorExecuted=false.
- Manifest versionado inclui somente metadados/hashes, nunca OCR text, words ou lines.
- Outputs permanecem ignorados pelo Git e nao entram no stage/commit; os hashes versionados identificam os caches locais.
- Codigo, config OCR, GT, manifest documental, question index e protocolo preservados; nenhum merge.
- O commit que introduz o manifest de preparacao constitui o freeze formal dos caches; nao ha auto-referencia ao futuro SHA do commit.
- Proximo passo separado: ultimo preflight cego e primeira execucao oficial unica, somente em etapa explicitamente autorizada.
- Nenhum Auditor nem metrica sera executado nesta mesma etapa, inclusive apos commit/push.
