# V5 — protocolo de coleta humana da estrutura de resposta

Temporada13 prepara instrumentos de revisão, não Ground Truth adjudicado.
Os 16 batches são fatias consecutivas de três documentos do manifest selecionado
R1 (posições1–3,4–6,...,46–48), nove questões por batch. Nenhuma nova seleção.
Identidades, fingerprints, números canônicos e páginas físicas estão travados;
eventual divergência exige STOP/decisão externa, nunca correção livre pelo revisor.

## Escopo e independência

Em futura etapa explicitamente autorizada, um humano examinará as questões nos
PDFs integrais para identificar estrutura de resposta e apresentação visual.
Não resolver a questão, procurar gabarito ou usar outputs do Auditor.
Não inferir por família/instituição/ano, nem presumir A–E.
Codex não preenche rótulos em nome de humano e não define humanAdjudicated=true
a partir de inspeção própria. Assistência de IA futura deve ser declarada;
não equivale a revisão humana independente. Nesta preparação não houve inspeção
visual, extração, OCR, renders, importação de decisões ou simulação de revisão.

## Campos e referência de contrato

Valores de referência lidos estaticamente de scripts/audit_holdout_schema.py,
contrato histórico V4, sem importar/executar o código ou copiar rótulos de GT.

| Campo | Referência e significado para futura decisão humana |
| --- | --- |
| responseMode | single_choice: escolher uma alternativa; true_false: julgar C/E; numeric_response: fornecer número; numeric: alias legado, não converter silenciosamente; discursive: resposta escrita aberta; other: estrutura diferente comprovada, explicada em notes; unknown: evidência insuficiente |
| optionCount | Inteiro não negativo com contagem de alternativas reais; null se não aplicável ou desconhecida, distinguindo o motivo em notes. Não contar enumerações internas nem controles como alternativas |
| optionLabels | Array de strings exatamente observadas, preservando ordem/Unicode; null se não aplicável ou não comprovável, com motivo. Nunca inventar sequência a partir da contagem |
| subitems | Extensão descritiva: lista de objetos label/role/pages/notes, somente itens observados; [] quando ausência comprovada; null quando desconhecido/não aplicável, explicado. Enumeração a)/b)/c) do enunciado não é automaticamente alternativa. Subitens avaliativos C/E são distintos de opções |
| responseControls | Extensão descritiva: lista de objetos label/role/pages/notes para caixas, círculos de marcação ou campos observados; [] quando ausência comprovada; null quando desconhecido/não aplicável, explicado. Controles não são novas alternativas |
| layout | vertical: sequência vertical; two_column: duas colunas; grid: grade; parent_child: organização pai/subitens; internal_enumeration: enumeração interna; mixed: combinação; none: ausência comprovada; unknown: evidência insuficiente |
| markerStyle | textual: letra/número textual; parenthesized: marcador entre parênteses; circled_outline: círculo vazado; circled_filled: círculo preenchido; symbolic_control: controle/símbolo; none: ausência comprovada; mixed: combinação; unknown: evidência insuficiente |
| contentKind | text: conteúdo textual; math: matemático; media: imagem/diagrama/tabela predominante; mixed: combinação; none: ausência comprovada; unknown: evidência insuficiente. Descreve conteúdo, não resposta correta |
| notes | Explicação humana livre, com páginas físicas/evidência, papéis e incertezas; não incluir gabarito, solução ou dados pessoais |

Exemplos são conceituais, não decisões do V5: escolha única com quatro ou cinco
alternativas; julgamento C/E; resposta numérica; resposta discursiva; enunciado
com subitens internos antes das alternativas reais; opções com imagens ou símbolos;
arranjo vertical, em colunas ou misto. Contar apenas o conjunto real de respostas.

Todo campo de resposta dos templates permanece null, inclusive notes.
Aqui null significa somente **não anotado**, não uma decisão de incerteza.
Na futura adjudicação, usar unknown nos enums quando faltar evidência e explicar
em notes; em counts/arrays usar null acompanhado do motivo explícito. Distinguir
ausência comprovada de desconhecimento. Se o formato não representar o caso,
registrar pendência técnica sem inventar resposta nem alterar o binding.

## Compatibilidade e integridade

O schema funcional legado aceita somente V1–V4. Estes instrumentos têm
protocolVersion=holdout-v5 e validação própria neutra; não são GT preenchido e
não se fazem passar por V4. subitems/responseControls/notes são extensões de
coleta que o validador legado não valida semanticamente. Compatibilidade de
leitura/validação do futuro GT V5 e integração com Auditor são um gate técnico
SEPARADO ainda não resolvido, obrigatório antes da execução oficial futura.
Nenhum código funcional congelado foi modificado para contornar esse gate.

Cada pacote ignorado contém três PDFs integrais, review-context.json,
ANNOTATION_TEMPLATE.json, FILES_TO_UPLOAD.txt e INTEGRITY_MANIFEST.json.
O inventário cobre os seis primeiros arquivos; seu próprio tamanho/hash são
guardados no checkpoint de batch e no manifest técnico pai, evitando auto-hash
recursivo. A lista de upload inclui os sete arquivos. O protocolo humano é
versionado e deve acompanhar a instrução de revisão, sem duplicação por batch.

Preparador isolado stdlib: testes sintéticos antes de --prepare; gravações
atômicas e hashes imediatos em ledger ignorado; retomada verifica arquivos
concluídos e não os sobrescreve. .pending incompleto é temporário exclusivamente
gerado pelo preparador, recuperável; divergência em arquivo final exige STOP.
--verify realiza nova leitura/hash de todos os arquivos, compara contexts e
templates byte a byte com a seleção e valida cobertura/disjunção/neutralidade.
Nenhum parser de PDF é necessário: páginas efetivas já congeladas são a autoridade.

Originais devem bater com fingerprints. Drift nunca é ocultado por fallback.
Somente indisponibilidade de caminho autoriza cópia preexistente em package
neutro V5, byte-idêntica por hash, com origem/motivo registrados. Sem source
essencial comprovada, STOP. Cópias não são convertidas, recortadas ou alteradas.

## Ressalvas obrigatórias e sequência

Preservar substituto efetivo global22 e provenance pós-freeze/performance-blind;
global21 frozen1/efetivo21; global8 números não contíguos/q18–21 indisponíveis;
fontes incompletas/integridade original inconclusiva; global48 versão modificada
congelada. Escopo é PDF disponível congelado, não certificação da prova original.
Os415auxiliares antigos continuam not_independently_verifiable, prospectivamente
preservados, historicalByteIdentityVerified=false; não reabrir a exceção nem
certificar retroativamente sua integridade histórica. Ver freeze do índice V5.

Publicar estes instrumentos somente após todos os gates e nova conferência final.
STOP após commit/push/HEAD remoto igual. Próximo passo exige nova autorização:
adjudicação humana independente Batch01, três documentos/nove questões.
Não iniciar automaticamente GT preenchido/final, OCR, Auditor, métricas ou merge.
