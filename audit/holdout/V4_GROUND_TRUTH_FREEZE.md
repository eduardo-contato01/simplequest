# Ground Truth V4 - consolidacao UTF-8 e freeze

- Branch: audit/holdout-v4; source HEAD: dc276052dee0334166263df0f670df02519baa74.
- Geracao UTC: 2026-10-05T18:30:13.089914+00:00.
- protocolVersion=holdout-v4; annotationVersion=1; freezeVersion=1.
- 16 source batches; 48 documentos; 144 questoes; 144 questionIds unicos.
- Progresso humano=144/144; batches=16/16; pending=0.
- encoding=UTF-8, sem BOM, LF; fontes lidas diretamente do disco.
- Uma tentativa local invalida foi descartada antes de staging, sem constituir freeze ou versao canonica.
- Discrepancia local CRLF/stat resolvida com update-index --really-refresh, sem mudanca de conteudo.
- core.autocrlf=true preservado; normalizedGitContentMatchesHead=true nos tres documentos; cachedDiffAfterRepair=empty; worktreeCleanBeforeRebuild=true.

## Integridade e consolidacao lossless

- sourceReplacementCharacterCount=0; finalReplacementCharacterCount=0.
- sourceQuestions=144; finalQuestions=144; uniqueQuestionIds=144; duplicateQuestionIds=0.
- missing=0; extra=0; changed=0; humanDecisionDifferences=0.
- questionCanonicalHashDifferences=0, comparando os 144 objetos relidos do disco.
- Cada question object foi copiado integralmente com deepcopy dos batches humanos, preservando Unicode, notes, nulls, arrays, campos e valores.
- Ordem: documentos do manifest Phase B e selectedQuestions dentro de cada documento, sem ordenacao alfabetica.
- allSelectedQuestionsCovered=true; allBindingsMatchFinalQuestionIndex=true.
- allDocumentFingerprintsMatchManifest=true; questionOrderMatchesFinalManifest=true.
- unknownQuestions=0; response modes: single_choice=132, true_false=11, numeric_response=1.
- doc-0bd82b9dc803:q40.responseMode=numeric_response preservado, sem conversao para numeric.
- Errata q19 incorporada: doc-6381aed53bb1:q19.pages=[14,15], identica ao batch humano e ao indice final.
- selectedIdsUnchanged=true; mapping SHA256: 301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477.
- selectionReexecuted=false; nenhuma nova decisao humana ou reinterpretacao de PDFs.

## Hashes calculados dos arquivos reais

| Artefato | File SHA256 | Canonical JSON SHA256 |
| --- | --- | --- |
| Ground Truth final | b940caa9f0cd3ffc4136a38310b54881f44343b6def9a5471afeca3abeb90a34 | 90486a8a0fd03ca15aa1688ce702654fa0c8dc88eac9c517661692beb8fda6ba |
| Provenance | da7e676826e9a57911250ac14d1b9a7b7636d81959d5c229902b1a631e58381a | - |
| Manifest Phase B | 763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7 | 26d76c5938b54a92a88b69552db8652ef61e0fb69fc0028cb55b001d20be55d4 |
| Final Question Index | 4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab | 89d852af97c30bc39607d54fc8017c484f0ae3fea8af09a78e29f17311f3a62d |
| Protocol V4 | f70fb425dd17a7a117a02926a8e0c6c7b9e199dc3c3d2640848b5f9a7b325183 | 94ff2f2340339de1487c23bf90b05416634f85852db37bdbdc2ef0811ff221bd |

- groundTruthFileHashMatchesProvenance=true.
- groundTruthCanonicalHashMatchesProvenance=true.
- sourceBatchSetCanonicalJsonSha256=87b2190c5bb32c16182e21777001cb9ff65efcb009bf989319f1cd7046e10b2f.
- Convencao canonica: audit_holdout_schema.sha256_json, UTF-8 json.dumps(ensure_ascii=False, sort_keys=True), separadores padrao.
- O hash do conjunto usa o array sourceGroundTruthBatches completo, reproduzindo exatamente o provenance V3.

## Source batches

| Batch | Fonte | Questoes | File SHA256 | Canonical JSON SHA256 |
| --- | --- | --- | --- | --- |
| 01 | audit/holdout/ground-truth-v4-batch-01.json | 9 | f9e6bb820fafc067af3e2d89df0bd6458a3ccee391cc52de708755d35b4d1f9d | 84f93f69b6d581cb69c8a85994a4e88254db5dead07076a5b16d95ad84e10edd |
| 02 | audit/holdout/ground-truth-v4-batch-02.json | 9 | 476e0abbd21faabc36e75bd5245d03224c65a39d412db481c049e46e80e2e366 | 7d01d265756ef1bdafaa15f3e655cec64e376a64cca56d6a74a091bc0bd2d2a1 |
| 03 | audit/holdout/ground-truth-v4-batch-03.json | 9 | c2e38fa5517734cdae4623a58de639329006c55ef5559cd5babd340451475b2a | 10c99a0168660bd4d26fa1e1cb00f2ef39589266146f920702a2ee7f8bbb9e19 |
| 04 | audit/holdout/ground-truth-v4-batch-04.json | 9 | 0592a5c6f150c0719fc20032ac732949537edc88b37ec60bff76077c86a53967 | 96fb917cbcb28a0528560d33886fc2f52e4e5d334c91ab589928b0ac212f0cb3 |
| 05 | audit/holdout/ground-truth-v4-batch-05.json | 9 | 234dea44c315163c31cdf40883335370def4db22658d7c7564116dea1a1241f9 | b4a02437b9f77d342436c615029df1e6b236f6ec06eb09ec255b2522384dfd4e |
| 06 | audit/holdout/ground-truth-v4-batch-06.json | 9 | 86010594809a966af6d09bc51eb610cda058539ddc52defd9a9e81c9c12119e1 | bdad88b7ec29eda1b24a486b466e736603ffebc083be86f6fc798ca9dc42f5a0 |
| 07 | audit/holdout/ground-truth-v4-batch-07.json | 9 | 6dcaa6f6c03bd97c87c1352dbce0d177c866e2f040eeaa15bd15744ca6466918 | cb9486822a9274dceba3d6551967b262ac4c471915f548f1ec0b9162a8fb1f9d |
| 08 | audit/holdout/ground-truth-v4-batch-08.json | 9 | 00cdc6079cbd0430107bb2045dea27fdb42a6a2dd0b60e7f068f808f43043884 | 3ea4184d9b08fff3c2b998fa473d2cf5bb5943c3d341a59601a71fca33a29202 |
| 09 | audit/holdout/ground-truth-v4-batch-09.json | 9 | 23b83fac0e5dcaa9169565c75e87906241f8fbddfeacebb09a0cdadb2a1ebabc | e82adfee2ad2dc698609884e7cc46e181c88d7f02845ed15e8b4d6d7cf16fce7 |
| 10 | audit/holdout/ground-truth-v4-batch-10.json | 9 | a88938f3ff85a6856ce185724c27dc5237d485ffbf170f91f1224343d0684e41 | 8e9dc042041fc1600f056caebb55ce67f45deaffd43878dec3d740943f0c9667 |
| 11 | audit/holdout/ground-truth-v4-batch-11.json | 9 | 66746e661b49050ca2dd5b1c2409df2fe7d74dc7bd5bb8ee344591700bdebe15 | 69040c18bc203670b8ce4a5082ca7d9614dd02c678bc4b92615967213d4fc241 |
| 12 | audit/holdout/ground-truth-v4-batch-12.json | 9 | aede9b0df8f2311be37398d8dd694f4fbb3322609878e0aa8c9b17610750c45c | 8c9e92d1fad05ae7fd7682306b6149626932d139868726dd10fe63ad837525c3 |
| 13 | audit/holdout/ground-truth-v4-batch-13.json | 9 | 1aa8e97d78b7862927c2c8ea71cec8a1266329c4b5b2c3cc77d41da13a0cb2e7 | 980771b905b83af11a863650e769a816304e34ac275a542af5b2861668785504 |
| 14 | audit/holdout/ground-truth-v4-batch-14.json | 9 | 525665f16ac51c2fc543d776fe89ef9dcd9d44fdc546cf09abc78a53896c11aa | 64da21418facf04ce03bbff9a4e036db799191a0a577561192cf98641348a5ce |
| 15 | audit/holdout/ground-truth-v4-batch-15.json | 9 | befc36efdd7879e2aa65af8cecd193692f018ee45f3707988bda82c5a734e016 | 6ca6aa5643c9746061eff91316f001287b79fa6e337b45673e65c4c68a2375cd |
| 16 | audit/holdout/ground-truth-v4-batch-16.json | 9 | bea8ab092461480f78bfbfa3bd1c54c777356206caf784e96a01504d2b16b007 | 50014012210dd078f43c12049dfbd12ea5a50c34318d2a16937e00679e201654 |

## Validacao e freeze formal

- Todos os 16 batches e GT final relido: validate_ground_truth=PASS; bindings=PASS.
- Testes existentes pertinentes de schema PASS; numeric e numeric_response aceitos sem normalizacao; modo invalido rejeitado.
- Batches 01-16 byte-preservados; manifest Phase B, provenance do manifest, Final Question Index e protocolo byte-preservados.
- Snapshots e flags historicas nao foram retroativamente alterados.
- humanAdjudicated=true; auditorExecutedBeforeFreeze=false; Auditor=false.
- Nenhum output do Auditor consultado ou criado; nenhum Auditor funcional executado.
- GT final pronto para freeze. O commit Git que introduz pela primeira vez ground-truth-v4.json e seu provenance constitui o freeze formal.
- freezeStatus=ready_for_freeze_commit e snapshot de preparacao e nao sera reescrito apos o commit.
- Proximo passo permitido apos o commit de freeze existir: execucao congelada do Auditor V4, em etapa separada.
- Nenhum merge.
