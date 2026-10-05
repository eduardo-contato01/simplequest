# Holdout V4 — errata objetiva de page range q19

Data: 2026-10-05. Source HEAD: `aa0d5bdacef8c640dfb5b3f6b3255595c2908778`.
Branch: `audit/holdout-v4`.

## Correcao e autoridade

- documentId: `doc-6381aed53bb1`.
- questionId: `doc-6381aed53bb1:q19`.
- Old page range: 14-14.
- Corrected page range: 14-15.
- pageStart permanece 14; somente pageEnd muda de 14 para 15.

Autoridade: verificacao visual humana fornecida pelo operador. Evidencia neutra: pagina 14 contem o inicio de q19, climograma e afirmacoes I-V; pagina 15 contem suas alternativas impressas A-E, seguidas do inicio de q20. Nao houve nova leitura visual/textual dos PDFs, adjudicacao de resposta, inferencia de responseMode/optionCount ou consulta a gabarito.

## Cadeia corrigida

- [Tier C](question-index-v4-tier-c-adjudication.json): q19.pageEnd e nota objetiva acrescentada ao neutralNotes existente do documento; 13 documentos / 430 questoes preservados.
- [Final index](question-index-v4-final.json): mesma boundary e nota; SHA atual da fonte Tier C atualizado; 48 documentos / 1.732 questoes preservados.
- [Manifest B](manifest-v4-b.json): somente q19.pageEnd.
- [Provenance B](manifest-v4-b.provenance.json): hashes de arquivo/canonical JSON derivados atualizados; questionIndexChangedAfterFreeze=true registra o reparo, nao nova escolha; seed 20261001 e metadata de selecao original preservados.
- Relatorios Tier C, final index e freeze atualizados com hashes atuais e adendos, sem reescrever o historico.
- GT batches 01-07: somente sourceManifestFileSha256/sourceQuestionIndexFileSha256 atualizados.
- CONTEXTO recebe uma entrada incremental; brain registra o reparo e a necessidade de regeneracao futura de 08-10.

Provenance de fontes historicas continua historica: sourceReviewContext/sourceHumanAdjudication de Tier C e sourcePriorTierCAdjudicationSha256 da fonte Tier D mantem os snapshots originais. As metricas e flags de etapas anteriores nos relatorios/artefatos originais nao sao recalculadas ou convertidas em estado atual por este reparo. Raw ja registra q19 em 14-15 e permanece byte-identico.

## SHA256 de arquivo antes/depois

| Artefato | Antes | Depois |
| --- | --- | --- |
| question-index-v4-tier-c-adjudication.json | `61e20f03f2fa8decb55ad61975ed2d3e8cc6812ecf1100e1b481b5e4b0a2aee6` | `bcc5898931127ec11f5d2c25412da4ccba20005ce6707c00133cc24be6c66d6a` |
| question-index-v4-final.json | `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8` | `4681bb8b257642ba1709c7c908791c011c16bc94b88c0071b4a971515c0bb4ab` |
| manifest-v4-b.json | `7250a9bd00f54bb49e0c68da468f4a5fb22dde9cd99943681642c582a619b885` | `763290a582e5ed9436717c8cd754bb4501ad5a6f6aa5c69d8b3287014e93f8e7` |
| manifest-v4-b.provenance.json | `b023ced0ed1b565e56113f10f87585ca25216a937c0f1facfedd721aa2e68eec` | `921bfd858c472164a3d50eae153444105eab6170a482cd793372bc4c805cbb42` |

Canonical JSON SHA256 atual: final index `89d852af97c30bc39607d54fc8017c484f0ae3fea8af09a78e29f17311f3a62d`; manifest B `26d76c5938b54a92a88b69552db8652ef61e0fb69fc0028cb55b001d20be55d4`. Convencao: audit_holdout_schema.sha256_json (JSON UTF-8, ensure_ascii=false, sort_keys=true, separadores padrao).

## Provas de preservacao

Lista de IDs: UTF-8 JSON compacto sem espacos `[[documentId,[selectedQuestionId1,selectedQuestionId2,selectedQuestionId3]],...]`, na ordem documental congelada.

- selected IDs before hash: `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`.
- selected IDs after hash: `301c9ff28731ca5d3ddbd2c1deb6429afa61d0f6d45497dd6cba634972a1e477`.
- hashes identicos = true; 48 documentos / 144 selected questions / 144 IDs unicos.
- selectionReexecuted = false; selectedQuestionIdsChanged = false; objectiveMetadataRepair = true.
- Final Index IDs changed = false; nenhuma outra questao/boundary canonica mudou.
- groundTruthHumanDecisionDifferences = 0: questions[] de todos os GTs 01-07 comparados estruturalmente e byte a byte, sem mudanca; 63 questoes / progresso 63/144.
- Raw index e 48 PDFs originais preservados por SHA256 binario; pacotes/contextos 08-10 e seus PDFs/listas locais preservados por hash.
- Batch 08 adjudicated = false; reviewPackagesRegenerated = false.
- GT final = false; Auditor = false; nenhum merge.

Reason na provenance: "Corrected canonical pageEnd of doc-6381aed53bb1:q19 from 14 to 15 after human visual verification."

## Pendencia explicita

Review packages/contextos 08-10 permanecem snapshots do source state anterior e nao foram corrigidos/regenerados neste commit. Precisam ser regenerados contra o novo HEAD em uma etapa posterior antes de continuar a adjudicacao humana.
