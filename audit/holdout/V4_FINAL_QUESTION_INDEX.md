# Holdout V4 — Final Question Index neutro congelado

## Resultado

48/48 documentos neutralmente adjudicados e consolidados na ordem da review queue V4. A autoridade exclusiva das questoes canonicas sao as cinco adjudicacoes congeladas, sem substituir decisoes humanas pelo raw.

| Tier | Documentos | Questoes canonicas |
| --- | ---: | ---: |
| A | 18 | 876 |
| B | 9 | 246 |
| C | 13 | 430 |
| D | 8 | 180 |
| Total | 48 | 1732 |

Tier A e a uniao disjunta das adjudicacoes unresolved e neutral: 6 + 12 = 18 documentos; 214 + 662 = 876 questoes. As somas foram calculadas programaticamente dos arrays adjudicados.

## Linhagem e hashes

- HEAD anterior: `4735ea5e3cf108b7c79ea9fa8b9c7aafff0bb563`.
- [Final question index](question-index-v4-final.json): SHA256 `c6552696da6cfc6bb96b04d1060fba676062991252b4cb92fffd2d93e1e8b0f8`.
- [question-index-v4-tier-a-unresolved-adjudication.json](question-index-v4-tier-a-unresolved-adjudication.json): SHA256 `252cb855129bf544bc1982a08856fe8b1212784bac0e33e8f435c7f01398a0e3`.
- [question-index-v4-tier-a-neutral-adjudication.json](question-index-v4-tier-a-neutral-adjudication.json): SHA256 `9873515ef637abfd7f38b8907fd24f09b6685997591731ea9b8ae8d964569524`.
- [question-index-v4-tier-b-adjudication.json](question-index-v4-tier-b-adjudication.json): SHA256 `837ef7f04c5745140ab7850b9be975935e66d53bf55cfdbf3ce2de5f407377d7`.
- [question-index-v4-tier-c-adjudication.json](question-index-v4-tier-c-adjudication.json): SHA256 `61e20f03f2fa8decb55ad61975ed2d3e8cc6812ecf1100e1b481b5e4b0a2aee6`.
- [question-index-v4-tier-d-adjudication.json](question-index-v4-tier-d-adjudication.json): SHA256 `78586630fc0552a612ee230c9896d39f39e0cacbb6c8b8e3939e62032b0b0751`.
- [Manifest documental](manifest-v4-a.json): SHA256 `be69ceafd2fde2ce00f5f72966c12e22d33f575785ddc00ae57030fe74b2dccc`.
- [Review queue](question-index-v4-review-queue.json): SHA256 `088bb091436bb8a195244da2a037394d0da02f66835e2be228fa029809f92592`.
- [Raw index](question-index-v4-raw.json): SHA256 `36549f5067f3236fee90112fd1df63fb30c5ca5445ebec77ca139be41d722f79`.

O JSON preserva integralmente cada documento adjudicado e suas questoes, acrescentando apenas metadata neutra da fila (family, year, sourceType, indexMethod, pageCount e reviewTier). `adjudicatedQuestionCount` e a contagem canonica por documento, preservada da origem.

`sourceAdjudications[].provenance` preserva os metadados completos das fontes, incluindo politicas de canonicalizacao, excecoes, autoridade e exclusoes humanas. Flags historicas das fontes permanecem sem alteracao nesse namespace; o estado atual do final index esta nas flags da raiz e no summary.

## Provenance preservada

- Tier A: exclusoes de paginas paralelas, politica de idiomas e printedQuestionNumberExceptions, com neutralNotes e numeros impressos preservados.
- Tier B: identidade canonica continua, sectionNumberingPolicy, section e printedQuestionNumber corrigido, sem reabrir reinicios por disciplina.
- Tier C: mapeamento humano congelado, numeros e boundaries preservados.
- Tier D: humanExclusions e notas explicitas preservadas; `doc-1e18e7252399:q21` e `doc-c8d6da47c18b:q21` continuam ausentes das questoes canonicas por serem Producao Textual. Nao foram criadas anomalias automaticas para essas exclusoes.

Nenhuma decisao humana, renumeracao ou boundary foi alterada nesta consolidacao. Campos de provenance existentes, inclusive sequenceRun quando presente, sao copiados sem filtragem.

## Estatisticas estruturais

- Raw total: 1024; canonico total: 1732; diferenca canonico menos raw: +708.
- Minimo por documento: 14; maximo: 180; mediana: 22,5.
- Distribuicao (questoes por documento: numero de documentos): 14: 1; 20: 19; 21: 4; 24: 1; 30: 6; 40: 13; 100: 1; 125: 2; 180: 1.
- Documentos com contagem alterada em relacao ao raw: 41.
- Comparacao por mesmo questionId, apenas estrutural: 391 ranges alterados entre 984 IDs compartilhados, em 47 documentos. IDs iguais nao implicam equivalencia de conteudo quando a origem registra normalizacao de identidade.

Estas metricas nao foram usadas para question selection nem para reabrir adjudicacao.

## Contagens e ordem congelada

| Ordem na fila | documentId | Tier | Raw | Canonicas | Delta |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | doc-0bd82b9dc803 | A | 33 | 125 | +92 |
| 2 | doc-0aa57ea3e5ed | A | 46 | 125 | +79 |
| 3 | doc-3971adb7884f | A | 17 | 20 | +3 |
| 4 | doc-591f3e819d58 | A | 10 | 30 | +20 |
| 5 | doc-41045384ae4b | A | 40 | 21 | -19 |
| 6 | doc-c573e686e882 | A | 27 | 40 | +13 |
| 7 | doc-cd0a32a92382 | A | 16 | 20 | +4 |
| 8 | doc-a1ddc006ef56 | A | 30 | 40 | +10 |
| 9 | doc-6dde932fb681 | A | 5 | 20 | +15 |
| 10 | doc-9832ec9bb87d | A | 20 | 20 | 0 |
| 11 | doc-44ea716ed9b7 | A | 12 | 100 | +88 |
| 12 | doc-5d61be2ac853 | A | 4 | 14 | +10 |
| 13 | doc-a272afbae2ca | A | 47 | 180 | +133 |
| 14 | doc-b71d45cbb12c | A | 14 | 21 | +7 |
| 15 | doc-e13d030b1f9e | A | 16 | 30 | +14 |
| 16 | doc-f4dd01071816 | A | 13 | 20 | +7 |
| 17 | doc-0db5ce524459 | A | 1 | 30 | +29 |
| 18 | doc-c41ddc7b55ec | A | 1 | 20 | +19 |
| 19 | doc-7f0815783d8c | B | 30 | 21 | -9 |
| 20 | doc-9236ae9f513e | B | 24 | 21 | -3 |
| 21 | doc-dce5637b3bd7 | B | 20 | 40 | +20 |
| 22 | doc-cef618be31e6 | B | 26 | 30 | +4 |
| 23 | doc-074dd67cbd4a | B | 16 | 20 | +4 |
| 24 | doc-56268e79f6bf | B | 5 | 20 | +15 |
| 25 | doc-f1c03b7dfa39 | B | 22 | 24 | +2 |
| 26 | doc-bb62e60cf7ed | B | 20 | 40 | +20 |
| 27 | doc-1693ea690bbb | B | 16 | 30 | +14 |
| 28 | doc-ad34c4cf7f30 | C | 9 | 40 | +31 |
| 29 | doc-ee51036d2382 | C | 24 | 40 | +16 |
| 30 | doc-6381aed53bb1 | C | 36 | 40 | +4 |
| 31 | doc-89561bb8f1fe | C | 9 | 20 | +11 |
| 32 | doc-eefc3d15076e | C | 29 | 40 | +11 |
| 33 | doc-27775227a392 | C | 26 | 30 | +4 |
| 34 | doc-3fb1e1ce24be | C | 36 | 40 | +4 |
| 35 | doc-f03e7d17eec1 | C | 15 | 40 | +25 |
| 36 | doc-03a9e3fe97aa | C | 39 | 40 | +1 |
| 37 | doc-08d3b1b8b1e8 | C | 39 | 40 | +1 |
| 38 | doc-143e13dc75ed | C | 19 | 20 | +1 |
| 39 | doc-9e4d161e7bfb | C | 11 | 20 | +9 |
| 40 | doc-cf6b56e7abd7 | C | 19 | 20 | +1 |
| 41 | doc-1e18e7252399 | D | 21 | 20 | -1 |
| 42 | doc-2790a3c9786b | D | 20 | 20 | 0 |
| 43 | doc-3e395d355d2c | D | 40 | 40 | 0 |
| 44 | doc-42af2b3d2b27 | D | 20 | 20 | 0 |
| 45 | doc-4310686d43a6 | D | 20 | 20 | 0 |
| 46 | doc-800c2a22f148 | D | 20 | 20 | 0 |
| 47 | doc-b605f7a51fd5 | D | 20 | 20 | 0 |
| 48 | doc-c8d6da47c18b | D | 21 | 20 | -1 |

## Validacao e isolamento

Inventario previo: cinco fontes existentes, parseaveis, neutras e holdout-v4; 48 IDs distintos, nenhuma duplicacao/ausencia/extra, fingerprints correspondentes a selecao congelada.

Validacao forte: ordem igual a review queue; metadata e pageCount congelados; questoes e provenance identicas a origem; IDs unicos globalmente; prefixos corretos; boundaries dentro das paginas; contagens por documento e tier iguais a origem; duas exclusoes Tier D mantidas. Raw, manifest, fila e adjudicacoes foram byte-preservados. Os 48 PDFs originais foram verificados somente por hash binario, sem leitura visual/textual ou reinterpretacao.

Nenhum gabarito/answer key, Ground Truth, Auditor output ou artefato downstream foi consultado. Nenhuma classificacao de resposta ou inferencia de alternativas foi feita.

- neutralAdjudicationComplete = true
- finalQuestionIndexCreated = true
- rawQuestionIndexModified = false
- questionSelectionExecuted = false
- groundTruthCreated = false
- auditorExecuted = false

Proximo passo: definir/executar question selection V4 em outra etapa. Esta execucao nao seleciona questoes, nao cria GT, nao executa Auditor e nao faz merge na main.
