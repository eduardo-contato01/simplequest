# Estruturas de Resposta

Ground truth **humano** levantado para benchmark da futura camada de descoberta de estrutura de resposta. Estes dados **não** são regras de runtime e **não** devem ser hardcodados por instituição/ano.

## Distinção conceitual

O projeto deve distinguir:

- **QuestionResponseStructure** — como a questão espera resposta: `single_choice`, `true_false_items`, `numeric_response`, `discursive`, `subitems`.
- **AlternativeMarkerProfile** — como as alternativas são apresentadas: `markerStyle`, `optionLabels`, `optionCount`, `layout`.

São dimensões independentes. Uma questão `single_choice` pode ter marcadores variados; uma questão com subitens pode ter alternativas reais depois.

## Famílias objetivas A-E

Instituições com provas objetivas de alternativas A-E: CMB, CMBel, CMBH, CMC, CMCG, CMF, CMJF, CMM, CMPA, CMR, CMRJ, CMS, CMSP, CMSM e CMVM.

- A quantidade histórica de questões pode variar.
- A apresentação visual das alternativas varia.

### Estilos de marcador observados

- **CMB**: `A ( )`, `A. ( )`, `A.( )`
- **CMBel**: `( a )`, `(a)`, `a)`, `(A)`.
  - Caso importante: **2017 Q7** possui alternativas em **duas colunas** com gráficos/imagens.
- **CMBH**: círculo vazado/`Ⓐ`, `A)`, `(A)`.
  - Caso importante: **Matemática 2018 Q2** possui subitens `a)`, `b)`, `c)` no enunciado e depois **alternativas reais circled**. Os subitens **não** são alternativas.
- **CMC**: `(A)`, `( A )`
- **CMCG**: `( A )`
- **CMDPII**: A-D, quatro alternativas. Estilos: `a)`, `A.( )`, `(A)`.
- **CMF**: `( a )`, `(a)`, `a)`, `a.`, `A)`
- **CMJF**: `A-( )`, `A. ( )`, `(A)`
- **CMM**: `(A)`
- **CMPA**: `(A)`, `( A )`, `a. ( )`
- **CMR**: `( A )`, `a.`, `a)`, `A.`, círculo vazado/`Ⓐ`, `(A)`, `A.( )`, `A ( )`, `A .( )`, `A. ( )`

### CMT — evolução estrutural

- **2013**: mistura de A-D e questões com 2 itens C/E.
- **2014**: A-C.
- **2015–2021**: A-E.
- **2022+**: 30 questões; 28 questões A-E; questões **15 e 30** possuem cinco itens C/E; subitens numerados `15-A...` e `30-A...`.

`15-A` etc. são **subitens avaliativos de uma questão pai**, não alternativas normais A-E.

## PAS

- **Tipo A**: itens Certo/Errado. Caracterizado pela estrutura “julgue os itens”.
- **Tipo B**: resposta matemática; possui marcador explícito.
- **Tipo C**: múltipla escolha A-D; marcadores em **círculo preto com letra no centro**. Pode ser inferido estruturalmente pelas alternativas A-D mesmo sem identificação textual explícita.
- **Tipo D**: resposta discursiva; possui marcador explícito.

## Princípios arquiteturais

- A futura camada **Alternative Structure Discovery** deve inferir a estrutura a partir do próprio documento; estes dados servem apenas como **benchmark humano de validação**.
- Não hardcodar comportamento por instituição/ano.
- A representação de resposta deve separar `single_choice` / `true_false_items` / `numeric_response` / `discursive` / `subitems` de `markerStyle` / `optionLabels` / `optionCount` / `layout`.

## Casos de benchmark obrigatórios (futuros)

- alternativas A-E comuns;
- A-D;
- A-C;
- círculo vazado;
- círculo preto;
- alternativas em duas colunas;
- alternativas com imagens;
- subitens a/b/c dentro do enunciado antes das alternativas reais;
- CMT 15-A/30-A C/E;
- PAS tipos A/B/C/D.

Ver tambem: [[AUDITORIA_PROVAS]], [[MODELO_DE_QUESTAO]], [[IMPORTADOR]].
