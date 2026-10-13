# Regras permanentes de engenharia de auditoria

Política instituída em 2026-10-13. Leitura obrigatória antes de trabalhos com
PDFs, indexadores, holdouts, Ground Truth (GT) ou Auditor, conforme
[AGENTS.md](../AGENTS.md) e o [índice do brain](../brain/00_INDEX.md).

Este documento estabelece procedimentos e requisitos para trabalhos futuros.
Não implementa um gate, autoriza execução ou modifica contratos congelados.
O componente integrado P0/P1 e seus testes são **implementação futura**.
Em holdouts já congelados prevalecem o protocolo e as decisões/erratas autorizadas
daquela execução; não aplicar novas exigências retroativamente nem reprocessar
fontes sem autorização. Uma incompatibilidade contratual exige STOP e decisão
explícita, não alteração silenciosa do protocolo ou do runner.

## A. Princípios

- Separar fatos observados, hipóteses, limitações e decisões autorizadas.
- Exigir evidência verificável, vinculada à fonte exata e ao contrato aplicável.
- Preferir soluções simples, determinísticas, testáveis e recuperáveis.
- Não inferir corrupção de um warning; registrar o diagnóstico e investigar
  apenas no escopo autorizado. Causa não determinada permanece não determinada.
- Ausência de anomalias automáticas não garante correção do índice. Contagem
  física de páginas não certifica completude editorial da prova institucional
  original, nem a quantidade de identidades canônicas disponíveis.
- Não fabricar questões, preencher lacunas ou renumerar objetos adjudicados
  para satisfazer contagens. Preservar identidades, ordem, boundaries e ressalvas.
- Proteger o cegamento e a sequência publicada de freezes. Revisão estrutural
  assistida por agente não equivale a GT humano independente.
- Uma exceção pós-freeze deve registrar autorização, motivo, caminhos afetados,
  momento, limites, evidências e impactos metodológicos. Nunca fingir pré-registro.

## B. Preflight de páginas: P0 e P1

### P0 — antes da indexação e seleção, em novos holdouts

O planejamento de um novo pipeline deve prever o preflight físico independente
antes da indexação e da seleção documental ou de questões. Enquanto a integração
não existir, cumprir o procedimento somente por etapa explicitamente autorizada;
não declarar que o runner o executa automaticamente.

1. Resolver a fonte obrigatória e calcular o SHA256 completo dos bytes do PDF.
   Confirmar presença e legibilidade; vincular toda evidência ao fingerprint exato.
2. Contar páginas físicas com pypdf e confirmar independentemente com
   Poppler/pdfinfo, sobre o mesmo arquivo identificado por hash. Não reutilizar
   o número do inventário como se fosse o resultado de um dos leitores.
3. Registrar versões dos leitores e do ambiente necessário à reprodução,
   comandos/parâmetros, resultados, exit codes e diagnósticos originais.
   Persistir a evidência no momento da leitura, inclusive warnings.
4. Comparar as duas contagens e o metadata de inventário. Concordância física
   não apaga uma divergência histórica; discordância entre leitores não se resolve
   escolhendo o número mais conveniente.
5. Em derivados autorizados, distinguir `sourceFrozenPageCount` de
   `effectivePhysicalPageCount`. Registrar a origem/hash de cada valor e sua
   precedência; nunca sobrescrever manifests, índices ou sidecars congelados.
6. Tratar divergências por decisão explícita e, após freeze, errata aditiva com
   provenance, timing e ressalvas. Sem autorização, STOP antes de reprocessar,
   selecionar ou promover novos valores. Não usar resultados de resposta para
   justificar admissibilidade, substituição ou correção.

O limite físico efetivo deve satisfazer concordância dos leitores e permanecer
associado ao mesmo fingerprint. Se a fonte mudar entre leitura e uso, o resultado
não pode ser reutilizado. Validar limites de questões por
`1 <= pageStart <= pageEnd <= effectivePhysicalPageCount`, sem assumir que o
metadata histórico corresponde ao tamanho físico real.

Tamanho reportado por ferramenta é distinto do tamanho dos bytes no filesystem.
Uma divergência técnica recuperável, como tamanho reportado zero com arquivo
binário legível, hash correto e páginas concordantes, requer evidência e decisão
registradas; não implica automaticamente corrupção nem dispensa os demais gates.

### P1 — imediatamente antes da primeira execução oficial do Auditor

- Conferir presença da fonte, SHA256 e contagem física previamente certificada
  pelo procedimento independente, incluindo a provenance de erratas autorizadas.
- Validar os intervalos do índice/seleção congelados contra páginas efetivas,
  sem alterar identidades, boundaries ou flags históricas.
- Validar configuração, caches e entradas congeladas no escopo de metadados
  autorizado; assegurar bindings exatos de fonte, página e configuração.
- Bloquear divergências materiais antes da fase observacional. O gate físico
  não usa GT, gabaritos ou métricas para decidir admissibilidade.
- Não ajustar algoritmos de resposta, OCR ou parâmetros ao desempenho do holdout.
  Não executar novamente o Auditor para contornar um gate ou reparar resultados.

### Estado funcional atual e fronteira da implementação

[scripts/audit_response_holdout.py](../scripts/audit_response_holdout.py) verifica
o fingerprint documental, mas **não possui o novo gate independente P0/P1 de
contagem física com dois leitores aqui especificado**. A verificação de hash
existente não deve ser descrita como integração desse componente.

O `preflight_pdf` de
[scripts/audit_pdf_mvp.py](../scripts/audit_pdf_mvp.py) é distinto: usa pdfplumber
e evidência de segmentação/estrutura. Não substitui a confirmação física
independente por pypdf e Poppler/pdfinfo.

A futura integração exige autorização própria, testes sintéticos e verificação
de compatibilidade com schemas e protocolos. Nenhuma implementação, teste do
Auditor, parser de PDF ou execução do V5 está autorizada por este documento.

## C. Evidências e arquivos

Classificar os artefatos **antes** de produzi-los e definir o contrato de retenção:

| Classe | Papel e obrigação |
| --- | --- |
| Fonte essencial congelada | Entrada necessária à construção/execução; preservar bytes, identidade, hash e provenance independente. |
| Evidência obrigatória de decisão | Justifica uma identidade ou decisão que não pode ser verificada sem ela; preservar a evidência e seu hash, mesmo em arquivos ignorados. |
| Auxiliar reproduzível | Não é entrada canônica nem evidência exclusiva; registrar fonte, versão/configuração e método de reprodução, conforme o contrato. |

O fato de ser PNG, temporário ou ignorado pelo Git não determina a classe.
Se um auxiliar for a única evidência necessária de uma decisão, tratá-lo como
evidência obrigatória e não dispensar sua retenção por conveniência.

Persistir os SHA256 históricos necessários quando os artefatos forem gerados,
junto de caminhos resolvidos, tamanho, classificação, origem e bindings de fonte.
O Git ignore não é uma política de descarte. Usar manifests/inventários existentes
e registros recuperáveis; evitar snapshots redundantes da população e ampliação
retroativa de exigências sem contrato.

Para cada comparação, registrar caminho real, referência histórica independente,
hash esperado, hash atual, método e resultado. Distinguir ocorrências de bindings,
arquivos distintos, aliases, documentos append-only e novos artefatos autorizados.
Não escolher uma referência pelo simples fato de coincidir com o hash atual:
resolver sua autoridade, versão e momento; snapshots de interrupção não se
confundem com checkpoints definitivos posteriores.

Hash atual não é prova histórica independente. Se a referência de um auxiliar
não puder ser recuperada, uma exceção explicitamente autorizada pode permitir
registrar hash/tamanho atuais e comparar novamente ao encerrar a execução.
Classificar `historicalIntegrity=not_independently_verifiable` e
`historicalByteIdentityVerified=false`; a referência é apenas prospectiva.
Não substituir perda de evidência obrigatória por uma certificação circular,
nem alterar documentos antigos para acrescentar garantias retroativas.

## D. Recuperação

Tarefas longas devem ser automatizadas e retomáveis sem baseline exclusivamente
em memória. Checkpoints atômicos devem identificar a última unidade concluída,
fontes e hashes, estado da revisão, resultados efetivamente conferidos e pendências.
Escrever em temporário no mesmo filesystem, validar bytes/estrutura e promover
atomicamente; preservar checkpoints históricos publicados e usar sucessor distinto
quando necessário. Um checkpoint operacional não é novo freeze histórico.

Processar grandes verificações em blocos ajustados ao tempo real de leitura.
Persistir e validar o resultado de cada bloco antes de avançar. A retomada deve
conferir que as referências e arquivos continuam no estado validado e reutilizar
progresso válido automaticamente, sem copiar números de uma execução antiga.

Uma interrupção com checkpoint íntegro é um problema operacional recuperável,
não nova evidência de defeito metodológico. Não reabrir PDFs ou repetir adjudicações
integralmente verificadas apenas para recuperar contexto. Respeitar STOP de
interrupção quando o contrato daquela execução o exigir; preservar progresso,
hash do checkpoint e unidade exata de retomada, sem publicação parcial.

## E. Finais de linha

Separar bytes físicos locais de conteúdo filtrado pelo Git. Registrar qual deles
cada hash e comparação protege. Para documentação append-only, preservar os
bytes históricos e confirmar que só o acréscimo autorizado foi incorporado.

Quando explicitamente autorizado, converter CRLF para LF **exclusivamente em
memória** e comparar o resultado byte a byte com o blob histórico do HEAD.
Igualdade de comprimento ou contagem compatível de CRLF não basta. A referência
do prefixo bruto local e a referência Git comprovam aspectos distintos;
uma não substitui a outra.

Não normalizar arquivos históricos no disco silenciosamente; não mudar
`core.autocrlf` nem criar `.gitattributes` para contornar uma divergência.
Conferir os blobs staged, o diff e os bytes locais após staging. Nenhum commit
pode remover, reordenar ou reformatar histórico sob pretexto de ajuste de newline.

## F. STOP proporcional

Bloqueios materiais ou contratuais exigem STOP antes de execução/publicação:

- Fingerprint de fonte essencial divergente.
- Fonte obrigatória ausente, ilegível ou comprovadamente corrompida.
- Discordância estrutural não resolvida entre leitores.
- Intervalo de questão fora das páginas físicas certificadas.
- Violação de protocolo congelado ou de autorização da etapa.
- Vazamento de GT, gabaritos ou métricas durante uma fase cega.
- Perda irrecuperável de evidência obrigatória de decisão.

Informar o caminho, a cláusula aplicável, o esperado, o observado e a evidência;
nunca editar fontes congeladas para forçar PASS. Exceção não pode dispensar
uma condição declarada irrenunciável por contrato imutável.

Não transformar warnings recuperáveis já avaliados, temporários comprovadamente
reproduzíveis ou interrupções com checkpoint válido em novos bloqueios
metodológicos. Isso não é dispensa genérica: documentar classificação e decisão,
preservar limites e parar se houver divergência real ou perda de evidência essencial.

## G. Aprendizados do Holdout V5

1. `v5-doc-74e153f9c146d887`: o metadata histórico registrava uma página,
   mas pypdf e Poppler/pdfinfo confirmaram 21 páginas físicas do mesmo PDF.
   A [errata objetiva](../audit/holdout/V5_OBJECTIVE_PAGECOUNT_ERRATUM_DOC10.md)
   e o [censo publicado](../audit/holdout/V5_PAGE_COUNT_CENSUS.md) preservam
   o valor histórico e fornecem a precedência efetiva para derivados autorizados.
   Isso não certifica completude editorial, não muda o PDF e não autoriza rerun.
2. Faltavam referências históricas independentes para 411 PNGs dos Tiers B/C/D
   e quatro JSONs intermediários do Tier B. A decisão externa delimitada permitiu
   preservação **prospectiva** dos 415, sem afirmar identidade histórica retroativa.
   Seus caminhos, método, classificação e caráter pós-freeze estão no
   [relatório final do índice V5](../audit/holdout/V5_FINAL_CANONICAL_QUESTION_INDEX.md).
   Os checkpoints intermediários não eram evidência exclusiva: os registros
   completos permaneceram no checkpoint definitivo vinculado por hash e na
   [adjudicação publicada do Tier B](../audit/holdout/V5_TIER_B_ADJUDICATION.md).
3. As sete adjudicações finais permaneceram intactas. O índice global conservou
   exatamente 48 documentos, 741 páginas e 2.136 objetos canônicos; só seus
   metadados de preservação foram reconciliados antes do freeze. SHA256 final:
   `a0930fe9c409170a5215042883e2bf1121c98bb530b251ad4eb59e5778ed31a7`.
   A etapa documental desta política não modifica esse índice nem suas fontes.
4. Exceções pós-freeze são rastreáveis, não pré-registro retroativo. A
   [regra de substituição por insuficiência](../audit/holdout/V5_INSUFFICIENT_QUESTIONS_REPLACEMENT_RULE.md)
   e a [errata da substituição](../audit/holdout/V5_OBJECTIVE_REPLACEMENT_DOC11.md)
   documentam timing, autorização, população efetiva e limitações metodológicas.
5. Revisão estrutural assistida não equivale a GT humano independente. As
   ressalvas e o escopo do conteúdo disponível devem acompanhar derivados futuros,
   sem novas alegações de corrupção, completude original ou desempenho.

O [protocolo V5](../audit/holdout/PROTOCOL_V5.md) e o
[freeze documental](../audit/holdout/V5_DOCUMENT_SELECTION_FREEZE.md) permanecem
imutáveis. Estado após o freeze do índice: `finalQuestionIndexFrozen=true`,
`PhaseBComplete=false`, `questionSelectionStarted=false`, `groundTruthStarted=false`,
`auditorExecuted=false`, `metricsSeen=false`, `merge=false`.
A seleção/congelamento das 144 questões é etapa separada e exige nova autorização.

## H. Plano de implementação futura

Planejar um componente físico independente, separado da observação/classificação
de respostas: P0 produz evidência vinculada ao PDF e P1 valida bindings, contagens
e limites antes da primeira execução oficial autorizada. Sua interface e sidecar
devem conter identidade/hash da fonte, versões dos dois leitores, contagens,
diagnósticos, valor histórico/efetivo e referências de decisão, sem GT ou métricas.
Definir schema/versionamento, armazenamento e precedência antes de integrar.

Com os mesmos inputs, versões, parâmetros e evidências, o sidecar estrutural
deve ter serialização e SHA256 determinísticos; separar metadados voláteis de
execução do payload determinístico. Não ordenar questões por filesystem nem
introduzir timestamps variáveis no artefato canônico.

Testes futuros devem usar fixtures sintéticas ou fontes de teste permitidas,
sem executar o Auditor V5 nem alterar seus freezes:

| Caso | Resultado esperado |
| --- | --- |
| 1. PDF de 21 páginas com metadata de uma | Dois leitores concordam em 21; valor histórico 1 preservado e efetivo 21 documentado; sem sobrescrever manifest. |
| 2. Discordância entre leitores | STOP estrutural; evidências e versões persistidas; nenhuma contagem escolhida arbitrariamente. |
| 3. Fonte ausente ou fingerprint divergente | Bloqueio antes da fase observacional, com caminho e motivo; sem substituição silenciosa. |
| 4. Intervalo fora das páginas físicas | Rejeição do intervalo contra a contagem efetiva; sem cortar ou prolongar boundaries automaticamente. |
| 5. Warning recuperável | Diagnóstico preservado e decisão proporcional; sem inferir corrupção, dispensar gates ou regenerar a fonte. |
| 6. Checkpoint interrompido e retomado | Salvamento atômico, última unidade e hashes recuperáveis; retomada sem repetir revisão já comprovada. |
| 7. Auxiliar sem referência histórica | Sem PASS histórico; classificação e exceção autorizada prospectiva quando admissível; evidência essencial perdida continua bloqueante. |
| 8. CRLF local versus LF do HEAD | Comparação autorizada em memória com igualdade exata; bytes locais e histórico staged preservados. |
| 9. Sidecar estrutural determinístico | Inputs idênticos reproduzem bytes/hashes, independentemente da ordem de enumeração de arquivos. |
| 10. Ausência de vazamento de GT e métricas | Gate físico não lê campos de resposta/GT/métricas nem os usa para admissibilidade; contratos cegos preservados. |

Nenhum componente, integração ou teste deste plano foi implementado ou executado
nesta etapa. Código funcional Patch05C1, PDFs, manifests, adjudicações, GT e
avaliações V1–V4 continuam congelados. Após publicar esta política, STOP.
