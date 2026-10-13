# V5 — regra prospectiva de seleção neutra de questões

Algoritmo `v5-qselect-tertile-sha256-v1`, sob autorização da Temporada 12.
Instituído após o freeze do índice canônico e ANTES de escolher os IDs reais.
Não é pré-registro da Fase A. A mensagem do primeiro commit é um identificador
operacional, não uma alegação de registro anterior à inspeção documental.

Esta regra só estará formalmente congelada após o commit
`audit: preregister v5 neutral question selection rule`, push e confirmação do
HEAD remoto. Antes disso, somente preflight sem escolhas e testes sintéticos.
Nenhum resultado oficial faz parte desta primeira publicação.

## Entradas e ordem

[Regra estruturada](v5-question-selection-rule.json),
[seletor independente](v5_select_questions.py) e
[self-tests sintéticos](v5_select_questions_selftest.py).
Nenhum script importa o código funcional do Auditor.

- [Índice canônico](question-index-v5-final.json): SHA256
  `a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7`.
- [Manifest efetivo R1](manifest-v5-documents-effective-r1.json): SHA256
  `a142ed34e5f13baaf566a22f14d1be86d2489c83445778b3a6b5f8d641c8ec32`.
- [Manifest histórico](manifest-v5-documents-frozen.json): SHA256
  `c124fe77bae292cdeebb0045b489a0676784a8dac39400d748fe3c978eb3ca62`.

São 48 documentos efetivos, 741 páginas e 2.136 objetos canônicos.
Associar por documentId E contentFingerprint, jamais por posição presumida.
A saída segue literalmente documents[] do R1; cada pool segue literalmente
questions[] do índice, cuja ordem documental de apresentação é distinta.
Não usar raw, número impresso, página, disciplina ou respostas para escolher.

## Regra matemática imutável

Seed documental congelada, sem alternativa:
`156bb96c58581fd34e8ddc29002a596fc6e03550c24763707b132d8db8337c1e`.

Para n questões, limites `[0, floor(n/3), floor(2*n/3), n]`.
Janelas zero-based, início inclusivo/fim exclusivo: disjuntas, não vazias e
com cobertura completa. Usar posições no array, não questionNumber.

Para cada candidata da janela t (0, 1 ou 2), calcular exatamente:

```text
SHA256(UTF8("v5-question-selection|" + seedSha256 + "|" + documentId + "|" + tertileIndex + "|" + questionId))
```

Valores literais, `|` literal, seed hexadecimal minúscula; não acrescentar
espaços/newline nem normalizar Unicode. Escolher o menor hash hexadecimal
lexicográfico; em empate, menor questionId literal lexicográfico (code points).
Copiar o objeto canônico completo sem mudança, um por janela; manter t=0,1,2.
Empate sintético é testado sem alterar SHA256 na execução oficial.

Saída:48×3=144. Sem troca manual, rejeição por OCR/layout/dificuldade,
favorecimento de resposta, cherry-pick, seed alternativa ou ajuste pós-escolha.

## Gates, materialização e recuperação

Antes do sorteio: os três hashes,48identidades/fingerprints únicos/associação1:1,
2.136IDs únicos/mínimo3 e todos ranges válidos contra páginas efetivas.
Global22 usa o substituto efetivo; global21 mantém histórico1/efetivo21;
global8 conserva lacunas q18–q21. Ressalvas e exceção415 permanecem vinculadas
ao [freeze canônico](V5_FINAL_CANONICAL_QUESTION_INDEX.md); não reabrir PDFs
ou investigação histórica dos auxiliares nem repetir inventário de milhares.

O CLI oficial exige regra/script exatamente iguais aos blobs do commit publicado,
HEAD local/remoto igual ao commit da regra e árvore/stage limpos. Usa um ledger
atômico ignorado de invocação única; persistirá escolhas e hashes imediatamente,
antes da materialização. Recusar uma segunda invocação oficial, mesmo após falha.
Uma falha de materialização não autoriza novo sorteio: preservar checkpoint e STOP.

O manifest derivado preserva cada objeto documental R1 e acrescenta as três
questões exatas, contagem física efetiva, metadata canônico e evidências de escolha
separadas dos objetos. Levar todas ressalvas e provenance pós-freeze do índice.
Não reutilizar nem modificar o envelope funcional do Auditor.

JSON canônico:UTF-8 sem BOM,2espaços/LF/newline final, sem timestamp.
Horário somente na provenance/ledger. Hash da lista de IDs:JSON compacto
`[[documentId,[q1Id,q2Id,q3Id]],...]`, Unicode literal, sem espaços/newline/BOM.

Depois da única execução: verificar independentemente terços, hashes,144IDs
e objetos, metadata R1, associação documental e bytes determinísticos.
Verificação/replay read-only não é nova invocação oficial nem retry de seed.
Publicação do resultado exige segundo commit/push e confirmação do HEAD remoto;
flags formais antes/depois são explicitadas no contrato de publicação, não
promovidas antecipadamente. Nenhum artefato histórico será reescrito.

## Hashes conferidos antes da publicação da regra

| Artefato | SHA256 |
| --- | --- |
| `v5-question-selection-rule.json` | `27300e3cc71beb5082a429367f116d9da40b2b0b505125643cc37f545d16a0af` |
| `v5_select_questions.py` | `57da2202afdae4ce26fe3e133ad22884be9918e83aea7694c97cdb6ef5cda652` |
| `v5_select_questions_selftest.py` | `0d8d397958b1db28d98c6566c9e9359de5561476748b8d0fe41ab90b8255a321` |

Oito testes sintéticos e preflight sem escolhas reais:PASS. O ledger oficial
ainda não existe; invocações oficiais=0 nesta primeira publicação.

## Comandos de execução autorizada

```text
python -B -X utf8 audit/holdout/v5_select_questions_selftest.py
python -B -X utf8 audit/holdout/v5_select_questions.py --preflight
```

SOMENTE após primeiro push confirmado:

```text
python -B -X utf8 audit/holdout/v5_select_questions.py --select --rule-commit <HEAD-publicado-da-regra>
python -B -X utf8 audit/holdout/v5_select_questions.py --verify
```

`--git-exe` permite identificar o executável Git sem mudar configuração.
GTConsulted=false/AuditorConsulted=false/metricsSeen=false; zero PDF/OCR/render,
Ground Truth, execução Auditor ou merge. A preparação de GT humano independente
somente poderá começar em etapa separadamente autorizada após os dois freezes.
