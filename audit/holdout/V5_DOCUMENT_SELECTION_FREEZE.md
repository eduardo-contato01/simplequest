# Holdout V5 blind — document selection freeze (Fase A)

`V5_PHASE_A_DOCUMENT_SELECTION_FROZEN = PASS`

Base funcional imutável: Patch05C1; 05C2 estacionado/não promovido.
Source branch: `audit/holdout-v4-postmortem-fixes`.
Candidate source commit: `3b306d6a544cc63928ec8adf07640b224651742e`.
Branch V5: `audit/holdout-v5-blind`; HEAD antes/depois da criação igual à base,
working tree e stage inicialmente vazios. Freeze formal pelo commit de introdução.

## Universo neutro e exclusões

1.167 caminhos PDF descobertos; 407 conteúdos únicos elegíveis. Inventário
pré-existente: 1.154 registros; mais 13 arquivos encontrados na raiz, excluídos
por falta de metadados neutros, sem abrir seus PDFs. Outro registro existente
tem year null; total de exclusões primárias por metadata insuficiente: 14.
Series null permanece categoria válida para PAS/Vestibular.

| Motivo primário | Caminhos excluídos |
| --- | ---: |
| Holdouts anteriores | 193 |
| Calibração/desenvolvimento fora dos holdouts | 39 |
| Diretório de gabarito | 495 |
| Filename de gabarito | 19 |
| Metadados neutros insuficientes | 14 |

Os 193 caminhos de holdout correspondem aos 192 fingerprints distintos de
V1–V4. O registry de calibração contém 147 fingerprints, incidindo em 148 caminhos,
incluindo documentos já excluídos por holdout; portanto os totais secundários
não são aditivos. Duplicatas: 11 caminhos além do primeiro de cada fingerprint,
todos já excluídos por motivos anteriores. Elegíveis não têm conteúdo duplicado.
Ausentes/erros de corrupção conhecidos no inventário: 0. Todos os fingerprints
do inventário foram rechecados por hash binário, sem drift; não houve parser,
extração, OCR ou validação visual de PDFs novos.

Evidências de exclusão abrangem todos os manifestos V1–V4 e revisões, seis
documentos originais de desenvolvimento, pilotos/benchmarks, auditorias/cache
OCR anteriores e postmortem/replays/patches. Três renders nativos existentes
foram reconciliados pelo contrato técnico de cache, sem abrir imagens.
82 referências literais sintéticas de self-tests não representam documentos
reais; unresolvedHistoricalDocumentIdentities=0.

## Seleção determinística

[Protocolo completo](PROTOCOL_V5.md),
[universo neutro](v5-eligible-document-universe.json),
[registry de exclusões](v5-prior-document-exclusions.json),
[manifest documental](manifest-v5-documents-frozen.json) e
[provenance](manifest-v5-documents-frozen.provenance.json).

Seed material: `simplequest-holdout-v5|3b306d6a544cc63928ec8adf07640b224651742e`.
Seed SHA256: `156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e`.
Algoritmo fixado antes da seleção: quotas Hamilton por source, filas de hash
por source/family/era/series, diversidade neutra e cap 3 por family. Frações
exatas e tie-breaks serializados estão no protocolo/selector; nenhum critério
de resposta, layout, dificuldade, OCR provável ou performance revelada.

TargetDocuments=48; selectedDocuments=48; 23 famílias; 21 anos distintos;
máximo por família=3. Sete categorias de série e todas as quatro eras cobertas.

| Source | Elegíveis | Selecionados | Restantes |
| --- | ---: | ---: | ---: |
| text_native | 277 | 32 | 245 |
| raster | 129 | 15 | 114 |
| hybrid | 1 | 1 | 0 |

text_low_quality: nenhum conteúdo único elegível não exposto após as exclusões;
não foi removido por previsão de dificuldade. Era distribution: 2004–2009=8,
2010–2014=11, 2015–2019=15, 2020–2025=14. Series: 1º=12, 5º=1, 6º=23,
7º=1, 8º=1, 9º=1, not_applicable_or_unspecified=9. Distribuições completas e
strata no manifest; ranking reproduzível pelo selector read-only.

Selection invocations=1; alternateSeedRetries=0; manualSwaps=0;
objectiveReplacements=[]; constraintsRelaxed=false. A única correção de
materialização foi atualizar referências SHA256 de rascunhos CRLF para os
arquivos novos UTF-8 sem BOM/LF; equivalência JSON comprovada, sem reselection.
Nenhum arquivo antigo teve line endings/configuração alterados.

O hybrid remanescente da reserva histórica V4 foi consumido por este novo V5,
conforme a população/quotas neutras do protocolo separado. Artefatos V4 não
mudaram. A futura Final Blind Evaluation precisará de novo acervo hybrid para
cobrir essa categoria sem reciclar documentos vistos; este V5 NÃO é tal avaliação.

## Hashes dos bytes finais

| Artefato | SHA256 |
| --- | --- |
| v5-eligible-document-universe.json | dd64269956de6c7210fe0e8cc4cbb23dc799925adefa4c5e6dd603ff997c5933 |
| v5-prior-document-exclusions.json | 124c8741d578c7a70bf087ae0f7f28716c15adfb7c4d7d5ccf3dad19023faa66 |
| manifest-v5-documents-frozen.json | c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62 |
| PROTOCOL_V5.md | 77f8bb06d7c8eadba79c7ef70a580eebeff2d74f324017ae8e220f11bea9bb95 |
| v5_document_selection.py | fda14af52b9aff1350942645fb89ae7a5332bafab7ec1a48e6df20876482dc74 |
| manifest-v5-documents-frozen.provenance.json | 8f96193787df4ccbe9faa08b09514dde36008a691ca5084c49217e9789665e8d |
| Candidate source commit (ASCII 40 hex, sem newline) | aedd26824957a58304206b5839ab0918fd95f4c5d40b4915aee62abd6834a7b8 |

## Gates e STOP

Verificador automático metadata-only: `python -X utf8 audit/holdout/v5_document_selection.py`.
Seleção reproduzida com entrada invertida; os mesmos 48 documentos/ordem/strata.
SHA256s reais conferidos; overlap verificado por fingerprint:

- priorHoldoutFingerprintOverlap=0
- priorPatchCalibrationDocumentOverlap=0
- selectionFrozenBeforeQuestionInspection=true
- questionInspectionPerformed=false
- questionSelectionStarted=false
- groundTruthStarted=false
- auditorExecuted=false
- metricsSeen=false (V5)
- V1–V4 unchanged=true
- auditorFunctionalCodeChanged=false
- phaseAComplete=true; V5Complete=false; merge=false

Manifest não contém selectedQuestions. 3/documento e 144 são somente plano.
Nenhum question-index-v5, GT ou resultado V5 foi criado. Auditor/funcionalidade,
artefatos antigos e caches/evidências anteriores preservados. CONTEXTO recebeu
uma única entrada incremental, preservando integralmente o histórico.

Limitação de integração futura registrada, não corrigida: o validador legado
`scripts/audit_holdout_schema.py` declara suporte somente a holdout-v1..v4.
Este manifest V5 é artefato documental da Fase A, não envelope de execução do
runner. A compatibilidade/bindings de execução precisarão de gate explícito em
etapa futura, preservando a base funcional congelada; não alterar schema/runner
nem trocar silenciosamente protocolVersion para contornar validação nesta fase.

Próximo, somente em autorização separada: **V5 Phase B neutral question index +
question selection freeze**. Depois do commit/push desta Fase A: STOP; não
abrir documentos selecionados, gerar índice/GT, executar Auditor ou fazer merge.
