# Holdout V5 — structural page-count census

V5_PAGE_COUNT_CENSUS=PASS_ONLY_AUTHORIZED_DOC10_MISMATCH

Source HEAD: `58ed0af2c1f961168feb86c699e8ed065bd607f7`; branch `audit/holdout-v5-blind`.
Date: 2026-10-08. Explicit structural-only authorization after the Batch02 checkpoint stop.
This is technical metadata verification, not question review or Auditor evaluation.

## Methods and bindings

All 48 original PDFs in frozen manifest order were binary-hashed, then structurally
opened by pypdf 6.10.0 (`len(PdfReader(path).pages)`) and independent Poppler
pdfinfo 26.07.0 (`Pages` metadata field). No OCR, render, text/content extraction,
question inspection, GT, Auditor, metric or selection execution.
PyMuPDF was unavailable; the independently implemented Poppler reader was used.
No values were chosen manually from expected counts.

- Frozen manifest SHA256: `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.
- [Ignored technical JSON](../../outputs/audit/holdout/v5-page-count-census.json), SHA256: `f27ac3cd5e0c3b1f80667ed0ae9b8565794b16cddaccee010c7d9a6b283acc7f`.
- [Additive erratum](v5-objective-pagecount-erratum-doc10.json) binds to the same census SHA256;
  [methodological contract](V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10.md). Formal freeze by introducing commit.

## Aggregate result

48 examined; 48 matching fingerprints; reader disagreements=0; technical failures=0;
pageCount mismatches=1, exclusively `v5-doc-74e153f9c146d887`, 1→21 (+20).
All 48 frozen physical page counts total713; verified actual total733.
These are metadata counts, not Auditor/performance metrics or original-exam completeness certificates.

pypdf emitted object-stream diagnostics on document12 (the affected document) and45.
Document45 additionally reported `incorrect startxref pointer(1)`; its count is19 in
both readers and matches frozen19. Poppler returned exit0 without diagnostics for all48.
This recoverable structural warning is disclosed, not silently fixed or classified
as corruption. All PDFs remained structurally readable for the authorized page census.

## Per-document census

SHA256 below is simultaneously frozen fingerprint and independently verified original binary hash.
All rows have readersAgree=true and fingerprintMatch=true. Order is manifest order,
not Tier A or batch order. No documentary ranking was recomputed.

| Order | documentId | SHA256 | Frozen | pypdf | pdfinfo | Verified | Mismatch | Delta |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | v5-doc-429b811d62a29a28 | 429b811d62a29a28c9e2dfb8f89afc95fb0afa0d0529fe9e67a205dd1aa00605 | 17 | 17 | 17 | 17 | false | 0 |
| 2 | v5-doc-9341853cd786543a | 9341853cd786543a175749ae045cde1732f9909dd8706cd17e0a4dcda30a1a6d | 24 | 24 | 24 | 24 | false | 0 |
| 3 | v5-doc-a37b092e0e967efc | a37b092e0e967efc24dd4806830ad446c8d9a10bda7ae83ea1180090a36ac5bf | 28 | 28 | 28 | 28 | false | 0 |
| 4 | v5-doc-78d5d0d89420b8d3 | 78d5d0d89420b8d3936b823099c7ad00044b008f5cab15b0ec19e28cd88ddf6e | 15 | 15 | 15 | 15 | false | 0 |
| 5 | v5-doc-906c5ae29d59a1ff | 906c5ae29d59a1ff734fd548b7ecd5552cdaab69a0c343496fab4b576f50f72b | 15 | 15 | 15 | 15 | false | 0 |
| 6 | v5-doc-7a302456c4a6afbe | 7a302456c4a6afbe0451df3e4cdf7027dbedee4801f4d24ddc0babaf440e4191 | 14 | 14 | 14 | 14 | false | 0 |
| 7 | v5-doc-9e5595dac9eb75e3 | 9e5595dac9eb75e3dffb955e2a39f1268c330fc4ecabe8250f3c89e17604eb32 | 17 | 17 | 17 | 17 | false | 0 |
| 8 | v5-doc-c6d6158a42ac379f | c6d6158a42ac379fcd8ce8f39cc93b402da5441ad551c671d47d1c976991488b | 9 | 9 | 9 | 9 | false | 0 |
| 9 | v5-doc-0c51e49589f148bc | 0c51e49589f148bc6f66b4b1822b3bf78b9a57f7e78a055f09648703d9230d87 | 12 | 12 | 12 | 12 | false | 0 |
| 10 | v5-doc-91b5252bd14b8900 | 91b5252bd14b8900e1a6d61519bff82687312d2c7b76e28cb8bb0247f58a97cf | 16 | 16 | 16 | 16 | false | 0 |
| 11 | v5-doc-34e3910f5e106aae | 34e3910f5e106aae9ad6f03efcc3456743312f2f7d08c6ded9bfa517c4885e3d | 7 | 7 | 7 | 7 | false | 0 |
| 12 | v5-doc-74e153f9c146d887 | 74e153f9c146d8878547d6f5fd0538953c61fcb15f17f27c6d1cfcddfadee53d | 1 | 21 | 21 | 21 | true | 20 |
| 13 | v5-doc-ae2f4e91af8a01f9 | ae2f4e91af8a01f933ec58bd5ca44449e1b7aba486e324e21a6b3eb08058ed4a | 17 | 17 | 17 | 17 | false | 0 |
| 14 | v5-doc-815b83630e3d8c98 | 815b83630e3d8c9899695cdcc4a30f96ee4a5f411d541d954c534cd5a8f9ef1a | 9 | 9 | 9 | 9 | false | 0 |
| 15 | v5-doc-e9603e9180e6028b | e9603e9180e6028ba3c7bb833cffd85d864e7f35233076c5fad1a96e26446207 | 12 | 12 | 12 | 12 | false | 0 |
| 16 | v5-doc-dd8461744150ef4b | dd8461744150ef4bd83208fbadb512a403a915633d0dcfb681df4b56f869dcac | 9 | 9 | 9 | 9 | false | 0 |
| 17 | v5-doc-a7256b9befdea91b | a7256b9befdea91bb320dce88545d7ddafd85cd3d52e46ce4e27b9ec863c00d2 | 22 | 22 | 22 | 22 | false | 0 |
| 18 | v5-doc-cb4e2c7c9e714d00 | cb4e2c7c9e714d00249004ccfa6d5a29b461ccb978c1535c27f88122c0d4cca8 | 19 | 19 | 19 | 19 | false | 0 |
| 19 | v5-doc-e0b6c6a249033308 | e0b6c6a249033308b2a83a54a73997342f2f5ca9a4ea502e0d5c11bfbdf7ce59 | 22 | 22 | 22 | 22 | false | 0 |
| 20 | v5-doc-2300b505b11855a2 | 2300b505b11855a2b555ea8b24e792948072340d5ceb4e4e7efce1b326784970 | 7 | 7 | 7 | 7 | false | 0 |
| 21 | v5-doc-84179ac96b058ffb | 84179ac96b058ffb43a18ffbbaea9b573e43759b6c5942fa3b1d09266ac2afe6 | 25 | 25 | 25 | 25 | false | 0 |
| 22 | v5-doc-05c35f7183da4927 | 05c35f7183da4927c12b2ae2845f8c2b5e74df2591dd7eabaf63c48ca666223f | 12 | 12 | 12 | 12 | false | 0 |
| 23 | v5-doc-bd657a7d79e90389 | bd657a7d79e90389ae6bced8a39cb07dd1b2cdc162e368f7cad1093f2083552a | 24 | 24 | 24 | 24 | false | 0 |
| 24 | v5-doc-02531e2612ade970 | 02531e2612ade970720cc0a153080e77869fc9edc6f2a74cfed882f5aeec2138 | 6 | 6 | 6 | 6 | false | 0 |
| 25 | v5-doc-e223f9e9c5cea0cb | e223f9e9c5cea0cb1bb88a9ea4efbcba7fb6cb997e99ef19aab92fae14e9730e | 6 | 6 | 6 | 6 | false | 0 |
| 26 | v5-doc-a8e098aad9a7ece4 | a8e098aad9a7ece4f16a549cd1c92f2531903d0f7fff24fe6ed695ff61306ef0 | 20 | 20 | 20 | 20 | false | 0 |
| 27 | v5-doc-4ec5bc5117bb7440 | 4ec5bc5117bb7440c96231090f3e99c63596c3d64607ac0c5ef4d4f41db39e3a | 16 | 16 | 16 | 16 | false | 0 |
| 28 | v5-doc-2442b4ab742e42f2 | 2442b4ab742e42f29fccf524f47f841b7bf2592938c0fd528e6b51c99f952134 | 10 | 10 | 10 | 10 | false | 0 |
| 29 | v5-doc-e123ad77b8edc98f | e123ad77b8edc98fdb7184c07925a676766bad4cb9d744cb3a22a2355cda0f54 | 12 | 12 | 12 | 12 | false | 0 |
| 30 | v5-doc-675affeba8d87308 | 675affeba8d87308980a7e0d328616a1461538ab1bf4f1c2f556aba549078e12 | 12 | 12 | 12 | 12 | false | 0 |
| 31 | v5-doc-506c709758cb13a9 | 506c709758cb13a9f8cc5d5454e168e61a96f5a1731f9003bfc2ae94013c3749 | 11 | 11 | 11 | 11 | false | 0 |
| 32 | v5-doc-3a0c4b28948e4a30 | 3a0c4b28948e4a30c92778da2ef70afef78740b77295639056ee697e9333c6e2 | 8 | 8 | 8 | 8 | false | 0 |
| 33 | v5-doc-143f3f337e22fb52 | 143f3f337e22fb529c8e610ca215f16214b425761ec1bd9b47e121a384bf2474 | 33 | 33 | 33 | 33 | false | 0 |
| 34 | v5-doc-87d7a7f5696b5a6a | 87d7a7f5696b5a6afbf9a10842a994b8ca6e759269b3aea0080faef0a2360b4e | 8 | 8 | 8 | 8 | false | 0 |
| 35 | v5-doc-1b6b371a30f5cd22 | 1b6b371a30f5cd22dfc5ee6e0d24a6cce1f33215aaf0164ebac7d62c9d86628b | 19 | 19 | 19 | 19 | false | 0 |
| 36 | v5-doc-80e01b1d6082d26b | 80e01b1d6082d26b6b022497e81a00b5ebb47e8f0a71c87b9cb17928fb4aa575 | 25 | 25 | 25 | 25 | false | 0 |
| 37 | v5-doc-d5099c3057735940 | d5099c30577359406ebc4faf4974434bf10f84fe24a3cc186dc162e7c866c838 | 13 | 13 | 13 | 13 | false | 0 |
| 38 | v5-doc-b1498826d8a54db3 | b1498826d8a54db31c8803cf1daa3aab8d753b0316de12ba84cf49bb42f1e126 | 12 | 12 | 12 | 12 | false | 0 |
| 39 | v5-doc-1fb8c32edfae9126 | 1fb8c32edfae9126e6faa329a251518338a5728570202e42dfdb918e300b9462 | 22 | 22 | 22 | 22 | false | 0 |
| 40 | v5-doc-d12896e095155245 | d12896e095155245ce24bf2df686b56797c6f9e41e7d5ec27f7e5c2eeaf62a9c | 17 | 17 | 17 | 17 | false | 0 |
| 41 | v5-doc-c3bf2d29c7e1d9e8 | c3bf2d29c7e1d9e8a8ad05f64f313fa8b92bccebea2e90d5dc1d8a6b363faed2 | 20 | 20 | 20 | 20 | false | 0 |
| 42 | v5-doc-0d7bc5575df13886 | 0d7bc5575df13886e7269106b265133d9f1286fca97b8a035e34890a20b98d6e | 10 | 10 | 10 | 10 | false | 0 |
| 43 | v5-doc-1babdc250c302165 | 1babdc250c302165ff32a5601fda24c215ab8b17eb0e78ee52d0e241bf132c40 | 18 | 18 | 18 | 18 | false | 0 |
| 44 | v5-doc-bc5d90aa69fa3416 | bc5d90aa69fa3416e2af5364542d5d6bbb4ba3b8550eca81aeeab2251aa7dd4d | 12 | 12 | 12 | 12 | false | 0 |
| 45 | v5-doc-9b28d28efbbf0354 | 9b28d28efbbf03544b7f805f7b84040c174148e10f132e3ff143161c81ee7b60 | 19 | 19 | 19 | 19 | false | 0 |
| 46 | v5-doc-47ff0591259f48eb | 47ff0591259f48eb52fcd70701aa87fa57010d632b8fda9d796bb2ce5ef2c9cf | 11 | 11 | 11 | 11 | false | 0 |
| 47 | v5-doc-a08230ae0b1cad7e | a08230ae0b1cad7e06f3e15215d54d0e53526e3e5c6b11008f4295a5fb469d09 | 4 | 4 | 4 | 4 | false | 0 |
| 48 | v5-doc-ccc36240e82f271d | ccc36240e82f271de6eec6894138b19f6f939c1b461e399738869c48346cacbe | 16 | 16 | 16 | 16 | false | 0 |

## Scope and STOP

Batch02 frozen120 remains historical; effective140 under explicit erratum only.
115 already-reviewed pages remain preserved; 25 remain (document10=21, document11=4).
Neither document was visually inspected here. Counts say nothing about the number
of questions on additional pages. Batch02/Tier A/Phase B remain incomplete.
Original protocol/manifest/universe/raw/report/queue/packages/checkpoints/PDFs/caches
and functional05C1/V1–V4 remain intact. Only additive technical/documentation records.
After authorized commit/push: STOP; later neutral review needs separate authorization.
