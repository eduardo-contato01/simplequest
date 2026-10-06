# Patch 03C — neutral_boundary_word_line_reconstruction

Branch: `audit/holdout-v4-postmortem-fixes`.
Base: `8ebdd70e1863d822a730176fd87a9a476e7cdc96`. Sem merge.

## Contrato neutro e prioridades

Current, next e verified peers compartilham resolução line-first. Um ou mais
matches de linha encerram o matching dessa identidade: unique usa a linha;
ambiguous continua conservador, sem fallback por words. Somente zero matches
permite buscar words da página/número esperado pelo índice. Canonical/printed,
ordem documental, grammar 03A e política index-backed 03B são preservados.

O fallback constrói uma baseline local a partir de tokens realmente observados.
Keyword/number devem compartilhar banda Y, ordem e distância X; texto intermediário,
referências internas, número errado, decimal, ano e parent-child não são headers.
Não há fuzzy substitution, decoding de CID ou confusion map. Words altas/ruído
não podem unir bandas diferentes para identificar o header. Cada start registra
page, bbox/top/x0, texto mínimo, wordIndexes, canonical/observed number, numberSource,
matchGrammar, evidence e source/matchSource=`word_geometry`.

Número com separador não basta: além do corpo observado adjacente, exige
corroboração index-backed por ordem/alinhamento ou paralelismo e formato numérico
compatível. Uma linha ambígua não fornece essa corroboração. Runs de três ou mais
subitems numéricos próximos/alinhados são rejeitados. Duplicatas plausíveis,
inclusive entre gramáticas diferentes, continuam ambiguous; não se escolhe a
ocorrência conveniente. Números não indexados não viram verified peers.

Uma página com uma só entry pode não ter peer. Nesse caso exige simultaneamente:
header numérico no topo do corpo/margem, observação original larga e verticalmente
colapsada e múltiplas linhas de corpo alinhadas observadas. Os critérios relativos
à geometria são gerais, cobertos por controles negativos; não há regra por prova,
página, número, count/labels ou Ground Truth. Bare numeric sem separador continua
insuficiente neste fallback. Limite conservador intencional, não novo indexador.

## Reconstrução somente dentro de scope comprovado

Primeiro filtra words por centro contra pageLimits (Y e, quando comprovado, X).
Somente essas words entram em `group_words_into_lines` no wrapper local; nenhuma
word vizinha participa da reconstrução. A mesma filtragem visual anterior permanece.
Não muda defaults globais da Observation Layer.

Reconstrói somente com reliable boundary + words, e razão objetiva: zero linhas
filtradas, originais cruzando a coluna, orderAmbiguous, linha larga/verticalmente
colapsada com sublinhas separáveis, ou start por words ausente nas linhas locais.
Sem necessidade, preserva as linhas originais. Trabalha por página, sem stitching.
Não modifica o bundle original; preserva texto, wordIndexes e ordem page/top/X.
Linhas reconstruídas têm source=`reconstructed_from_words`.

Boundary expõe `questionStartMatchSource` e `lineReconstruction` com used/reason,
inputWordCount/outputLineCount e diagnósticos por página. Runner aceita bundle OCR
com words mesmo sem lines; essa é sua única alteração funcional. Structure,
Regions, Fusion, classificação, indexador, adapter e OCR permanecem intactos.
Arquivos funcionais: audit_question_boundary.py e audit_response_holdout.py.

## TDD e validação

46 checks novos sintéticos, controles A-U e refinamentos em boundary selftest.
RED inicial antes do código funcional: 22 falhas novas; controles antigos PASS.
Ciclos adicionais antes dos respectivos refinamentos: baseline/enumeração=3,
run interno=2, runner words-only=1, duplicata entre gramáticas=1. Total RED=29.
GREEN final: 46/46 novos + controles anteriores PASS. As 14 suítes existentes e
py_compile dos três arquivos Python alterados PASS.

Inclui linha prioritária, ambiguidade não sobreposta, current/next por words,
keyword distante/em outra banda/página, número errado/ano/decimal/footer/parent-child,
duplicatas, printed distinto, peer index-backed, duas colunas e exclusão de vizinha,
zero linhas, colapso, linhas saudáveis, C ausente não inventado e gates 01/02.
Expectativas anteriores não foram relaxadas. Bbox esperada de uma fixture foi
corrigida aritmeticamente; uma tentativa adicional teve SyntaxError no selftest
antes de executar checks, reparado antes de repetir RED/GREEN, sem mudar produção.

## Replay restrito — regression behavior, não avaliação imparcial

Somente os 19 IDs autorizados. Passagem final: 38 chamadas locais pareadas
base/patch; não chama main/evaluate_manifest ou CLI oficial, nem executa os 144.
GT é usado somente pelo wrapper para classificação, nunca pelo matching neutro.
Nenhum novo OCR/render. PDF nativo somente pelo adapter existente, sem reconhecer
glifos novos; raster usa os caches existentes byte-preservados.

Houve quatro passagens locais durante desenvolvimento/validação, a primeira
interrompida após 18 pares por um assert do wrapper que exigia igualdade literal
do resultado safety (mudança conservadora de q20). As outras três completaram
19 pares: 150 chamadas locais, sempre os mesmos 19 IDs únicos. Nenhuma foi unsafe.
O wrapper passou a registrar a mudança conservadora, mantendo STOP obrigatório
para qualquer unsafe_error; nenhuma camada de resposta foi alterada para mascará-la.

### Cinco targets

Em todos beforeReliable=false, beforeReason=current_marker_not_found,
beforeMode=vertical, before=safe_abstention/null/null; becameUnsafe=false.

| questionId | after reliable/reason | matchSource / grammar | after mode | reconstrução / razão | words / linhas reconstruídas | after classification/count/labels |
| --- | --- | --- | --- | --- | --- | --- |
| doc-56268e79f6bf:q11 | true / ok | word_geometry / legacy_keyword | vertical | true / collapsed_full_width_line | 215 / 56 | correct / 5 / A-E |
| doc-56268e79f6bf:q14 | true / ok | word_geometry / legacy_keyword | vertical | true / collapsed_full_width_line | 189 / 49 | correct / 5 / A-E |
| doc-f4dd01071816:q5 | true / ok | word_geometry / numeric_separator | vertical | true / collapsed_full_width_line | 153 / 45 | safe_abstention / null / unknown |
| doc-c41ddc7b55ec:q2 | true / ok | word_geometry / numeric_separator | two_column | true / no_filtered_lines | 25 / 7 | safe_abstention / null / unknown |
| doc-44ea716ed9b7:q54 | false / current_marker_not_found | null / null | vertical | false / not_required | 0 / 0 | safe_abstention / null / null |

q2 mantém somente a coluna esquerda: current 02., peer index-backed 07. e next
03. por words. Enumerações internas 2./3. não escolhem o start. C local ausente
não é inserido. q5 também abstém downstream apesar do header/scope/reconstrução.

q54 é limite observacional: tokens nativos no lugar do número estão representados
como `(cid:...)`, não como 54/54. Não decodificamos, substituímos ou inferimos esses
tokens pelo índice/GT. Ausência mantém reliable=false; não certificamos scope ou
emissão. Suporte sintético a headers numéricos observáveis não recupera um glyph
não reconhecido. Requer observação complementar, fora deste patch.

### Regressões

- Dois targets 03B: boundary vertical/sem falsos peers e resultados preservados;
  q25 correct/5/A-E, q20 safe_abstention/null/null. unsafeRegressionCount=0.
- Seis targets 03A: identidade/grammar e correct/5/A-E preservados, incluindo
  canonical q27/printed 7. unsafeRegressionCount=0.
- Seis safety 01/02: nenhum unsafe; cinco resultados preservados. No raster
  doc-f4dd01071816:q20, reconstrução por linha colapsada expõe ambiguidade pelo
  gate existente: correct/4/A-D → safe_abstention/null/unknown. Perda conservadora
  de emissão neste caso, explicitamente não ganho. unsafeRegressionCount=0.
- Membership/completude preservados; rejeitados usados downstream=false nos 19.

Traces/logs ignorados: outputs/audit/postmortem-v4/patch-03c-boundary-word-reconstruction/.
SHA256 de diagnostic-replay-validated.json:
`993c26917ababb11bd263c739e25447192a0e8bb0e426fcf40e48239045f0ded`.

## Preservação, diff e estado

1.758 arquivos protegidos byte-idênticos: todo audit/holdout, caches OCR,
evidências do postmortem e Patches 01/02/03A/03B. Resultado/GT/manifest/index/
protocol/OCR preparation intactos. Resultado oficial SHA256:
`2284bbb2f309b17115ddef5975121ed843d89799ebab052f47dcf01f995dc734`.

Diff funcional sem IDs V4, famílias/anos/páginas/textos específicos, GT como regra,
counts/labels esperados, clamp ou confusion map. Grammar 03A e inferência geométrica
03B anteriores intactas; demais módulos funcionais sem diff. git diff --check PASS.
CONTEXTO preservado com exatamente uma linha incremental; brain curto com contrato,
estado e próximo passo, sem depósito de logs.

officialAuditorExecutionCount=1; officialAuditorRerun=false; newOCRExecutions=0;
V4PerformanceClaimed=false; V5Required=true. V4 é **not an unbiased evaluation**.
Sem precision/coverage/unsafe-rate/recovery-percentage pós-patch; V5 blind obrigatório.

Patch03CComplete=true; boundaryPlannedPatchesComplete=true (03A/03B/03C), sem afirmar
boundary perfeito. Limites e abstenções acima permanecem. Próximo passo separado:
`marker_role_and_spacing`; observação complementar e V5 blind ainda pendentes.
