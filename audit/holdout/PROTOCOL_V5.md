# Holdout V5 blind — protocolo da Fase A

## Base e isolamento

Candidate source commit: `3b306d6a544cc63928ec8adf07640b224651742e`, branch de
origem `audit/holdout-v4-postmortem-fixes`; baseline funcional Patch05C1, 05C2
estacionado/não promovido. Branch própria: `audit/holdout-v5-blind`, criada
exatamente nesse commit com working tree e stage vazios.

Nenhuma mudança funcional do Auditor é permitida desde a criação desta branch
até executar e congelar o primeiro resultado V5. Inclui todo o código funcional,
especialmente `scripts/audit_response_*.py`, `audit_question_boundary.py`,
`audit_observations.py`, `audit_visual_marker_evidence.py` e `ocr_pdf_layer.py`.
Bugs descobertos devem ser registrados, não corrigidos. A ferramenta desta
Fase A vive em `audit/holdout/`, é metadata-only e não importa/executa o Auditor.

V1–V4, resultados/provenance, GT, índices e postmortem continuam imutáveis.
V4 revelado é evidência de desenvolvimento, nunca avaliação limpa da base nova.

## População e novidade documental

A população é a raiz externa já usada pelo inventário. Descobrir caminhos PDF
recursivamente e incorporar também registros do inventário cujo arquivo falte.
Usar somente os campos pré-existentes path/relativePath, institution, year,
series, classification e pageCount de `outputs/audit/corpus-inventory.json`.
Ignorar todos os outros campos, incluindo markers, padrões ou estimativas de
questões. `sourceType` é a classificação neutra pré-existente, não previsão.
Series null é uma categoria explícita `not_applicable_or_unspecified`, não
motivo de excluir PAS/Vestibular. Não inventar metadados dos arquivos novos.

Fingerprint = SHA256 dos bytes completos do PDF, sem extração, render ou leitura
visual. Comparar com o cache pré-existente e parar se houver drift. A validação
de corrupção desta fase usa somente erros já registrados no inventário; não
alega validação completa de PDFs novos sem metadados. Não executar parser/OCR.

Excluir por fingerprint todos os documentos de todos os manifestos V1–V4,
incluindo revisões de V2 e V3. Excluir também os fingerprints do desenvolvimento
original, pilotos, benchmarks, auditorias diagnósticas, caches OCR já utilizados,
targets/replays de postmortem e calibração/inspeção dos patches (incluindo o
experimento 05C2). Ler nesses registros somente identidade/path/fingerprint;
não consultar predictions, response mode, option count/labels, questões ou
métricas dos candidatos. Caches de render existentes devem ser reconciliados
por identidade técnica de caminho/stat/página/DPI, sem abrir suas imagens.

O registry novo persiste fingerprints e fontes/hashes das evidências. Quando
uma referência histórica é um basename, todos os caminhos com o mesmo basename
são excluídos conservadoramente, nunca se escolhe o mais conveniente. Referências
sintéticas de self-tests não representam PDFs do corpus. Ausência, erro neutro,
answer-key role ou metadados insuficientes são registrados, nunca omitidos.

Answer-key role mantém o princípio V2: diretório gabarito/gabaritos; prefixo
`gab_` ou token independente gab inicial/gabarito/gabaritos no basename após
NFKD, remoção de acentos, casefold e separação de `_ - .`/espaços. Tokens ambíguos
não são automaticamente excluídos. Duplicatas de conteúdo têm uma identidade
`v5-doc-` + primeiros 16 hex do fingerprint; manter apenas o primeiro caminho
em ordem NFKC/casefold com barras `/`, registrando os demais como duplicatas.
O universo contém todas as linhas de caminhos, inclusive exclusões; as contagens
de motivos secundários podem se sobrepor. Documentos elegíveis são únicos.

## Desenho determinístico, fixado antes do sorteio

Alvo: 48 documentos. Plano futuro: 3 questões/documento, 144 questões;
nenhum número ou ID de questão é escolhido nesta fase.

Seed material UTF-8 sem newline:
`simplequest-holdout-v5|3b306d6a544cc63928ec8adf07640b224651742e`.
Seed = SHA256 hexadecimal minúsculo desse material. Nenhuma seed alternativa,
retry orientado pelo resultado, troca manual ou relaxamento silencioso.

1. Source quotas: reservar 1 lugar para cada sourceType não vazio. Distribuir
   `48 - número de sources` proporcionalmente às capacidades elegíveis usando
   Hamilton (floors + maiores restos); ties por SHA256(seed + `|source|` + source)
   e source literal. Se alguma quota exceder capacidade, parar, sem redistribuir.
2. Stratum = tuple `(sourceType, family, era, seriesCategory)`. Eras: 2004–2009,
   2010–2014, 2015–2019, 2020–2025; fora disso, blocos de cinco anos por floor.
   Serialização do tuple: JSON array UTF-8, sem espaços, sem ASCII escaping.
3. Dentro de cada stratum, ordenar por SHA256(seed + `|` + contentFingerprint),
   depois fingerprint e canonicalPath literais. Somente o próximo dessa fila
   pode ser escolhido; nunca pular por layout/qualidade/conteúdo.
4. Em cada posição, escolher source ainda abaixo da quota pelo menor quociente
   exato `selecionadosSource/quotaSource`, ties pelo source hash e source.
5. Dos strata não esgotados desse source, com family abaixo do cap 3, escolher
   o menor score lexicográfico: série ainda não representada (0; já vista=1),
   documentos já escolhidos da family, documentos já escolhidos do year do
   próximo candidato, `selecionadosEra/elegíveisEra`,
   `selecionadosSeries/elegíveisSeries`, `selecionadosStratum/capacidadeStratum`,
   SHA256(seed + `|stratum|` + tupleJSON), tupleJSON. Frações são exatas.
6. Escolher o próximo fingerprint desse stratum, atualizar contadores e repetir
   até 48. A ordem do manifest é a ordem de escolha. Isso usa apenas diversidade
   neutra, nunca desempenho revelado, dificuldade ou adequação de questões.

Gates: pelo menos 48 elegíveis únicos, 48 selecionados únicos, quotas exatas,
ao menos 16 famílias, cap 3 por família, ao menos 12 anos distintos, todas as
eras e séries presentes no frame elegível representadas. Se impossível, parar;
não ajustar algoritmo/seed após observar a seleção. `manualSwaps=0`.

Após o freeze, substituição somente por ausência, drift, corrupção objetiva ou
duplicata, usando automaticamente o próximo do MESMO ranking/stratum com
errata/provenance explícita; se não houver próximo elegível, parar. Não trocar
por escola frequente, OCR, layout, arquivo esquisito ou performance esperada.

## Sequência blind obrigatória

Fase A: protocolo/universo → seleção e freeze de documentos → commit/push → STOP.
Sem PDFs visuais, question inspection/index/selection, GT, OCR, Auditor ou métricas.

Fase B posterior e separadamente autorizada: neutral question index completo
dos documentos já congelados, adjudicação neutra quando necessária e freeze
antes da seleção das 3 questões por documento. Não usar respostas/alternativas
como critérios. Ground Truth somente depois do question-selection freeze,
com adjudicação humana e freeze próprio. OCR de execução/configuração futura
deve ser congelado sem tuning do V5; não reutilizar defaults do indexador como
configuração oficial por conveniência. Auditor somente após GT/config/cache
freeze e preflight cego. A primeira execução oficial é única e imutável.
Não ver/calcular métricas antes do result freeze; bugs/config failures exigem
registro, não rerun silencioso. Depois do primeiro resultado congelado, abrir
métricas em etapa separada. V5 completo NÃO é declarado na Fase A.

V5 é novo holdout blind de desenvolvimento, não a Final Blind Evaluation. A
reserva histórica V4 é evidência imutável do estado naquele freeze; este protocolo
faz seleção nova da população não exposta. Caso uma categoria rara fique sem
documentos não vistos após V5, a Final Blind Evaluation exigirá novo acervo antes
de declarar representatividade nessa categoria; não reciclar V5 nem holdouts.

## Provenance e validação

Registrar SHA256 dos bytes UTF-8 sem BOM dos artefatos novos: universo, registry,
manifest, protocolo e selector. SHA256(candidate source commit) significa SHA256
do texto ASCII hexadecimal de 40 caracteres, sem newline; não é hash da árvore.
O Git SHA continua registrado separadamente. Hashes funcionais da base e fontes
históricas asseguram rastreabilidade. Freeze formal pelo commit de introdução.

Verificação automática read-only: `python -X utf8 audit/holdout/v5_document_selection.py`.
Reproduzir a mesma seleção a partir do universo congelado, inclusive com ordem
de entrada invertida; não é novo sorteio/novo freeze. Verificar overlap zero por
fingerprint contra holdouts e calibração. Um overlap exige STOP antes de staging.

Flags da Fase A: `selectionFrozenBeforeQuestionInspection=true`,
`questionInspectionPerformed=false`, `questionSelectionStarted=false`,
`groundTruthStarted=false`, `auditorExecuted=false`, `metricsSeen=false`.
Manifest é documental, `questionSelectionStatus=not_started`, sem selectedQuestions.
Após commit `audit: freeze holdout v5 document selection` e push da branch V5,
parar obrigatoriamente; sem merge, índice, GT ou Auditor.
