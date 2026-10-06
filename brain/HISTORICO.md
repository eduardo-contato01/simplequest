# Histórico

Este arquivo guarda planos antigos, milestones concluídos e decisões de sequência que deixaram de ser o roadmap vigente. Não faz parte da leitura padrão: consultar somente quando for necessário entender como o projeto chegou ao estado atual ou recuperar a origem de uma decisão/etapa antiga.

Detalhes cronológicos continuam em [CONTEXTO_SIMPLEQUEST.md](../CONTEXTO_SIMPLEQUEST.md); este histórico não é uma cópia do log. Trabalho vigente em [[ROADMAP]] e estado factual em [[ESTADO_ATUAL]].

## Snapshot do ROADMAP anterior — antes da reorganização de 2026-10-06

Fonte: `brain/ROADMAP.md` no commit `89f482b373449022423b4d34536160e62774cd2d`. Conteúdo integral preservado abaixo, com apenas dois níveis acrescentados aos headings para encaixar nesta seção. As tarefas pendentes deste snapshot não descrevem o estado corrente.

### Roadmap

#### Curto prazo

Prioridade: continuar o Holdout V4 a partir do checkpoint A/B concluido, com arquitetura V1 congelada e isolamento da adjudicacao neutra (ver [[AUDITORIA_PROVAS#Holdout V4 — checkpoint apos Tier B]]).

1. Continuar o Holdout V4 apos este checkpoint de documentacao; Tier C ainda nao iniciado.
2. Adjudicar os 13 documentos Tier C com a evidencia neutra permitida pelo protocolo.
3. Adjudicar os 8 controles Tier D.
4. Construir o final question index somente depois de concluir as adjudicacoes.
5. Executar question selection somente depois do indice final.
6. Criar Ground Truth V4 depois da selecao de questoes.
7. Executar Auditor V4 somente apos Ground Truth congelado conforme o protocolo.

- Manter este brain atualizado quando arquitetura, decisoes ou estado relevante mudarem.
- Atualizar `README.md` para descrever o SimpleQuest real, comandos atuais e fluxo de dados.
- Resolver divergencia entre `public/data/stats.json` e `public/data/questions.json`, ou remover/explicar o arquivo se nao for usado.
- Melhorar documentacao reprodutivel do importador e das dependencias em `work/source_files`.

#### Qualidade e seguranca

- Validar entradas da API com schemas explicitos.
- Separar autorizacao real da nocao editorial de "Administrador".
- Tratar `localStorage` indisponivel ou bloqueado.
- Proteger edicoes nao salvas ao trocar de questao/sair da revisao.

#### Produto

- Evoluir navegacao planejada em etapas documentadas em `docs/simplequest-2.0-analise-tecnica.md`.
- Criar fluxo de auditoria em massa conforme [[AUDITORIA_PROVAS]].
- Melhorar exibicao/validacao de questoes com gabarito vazio, anulado ou fora de A-E antes de usar pontuacao automatica.
- Manter impressao e exemplos baseline ao extrair ou reorganizar componentes.

#### Importacao

- Tornar pipeline de importacao mais reprodutivel e documentado.
- Priorizar conversao/revisao das questoes com `pending-media`.
- Auditar amostras ricas antes de autenticar lotes.

#### Ingestão Assistida de Questões (pós-Auditor)

Etapa **posterior ao Auditor de Provas**. Nao implementar durante a estabilizacao atual do pipeline de auditoria; so deve comecar quando admissao, segmentacao, extracao e confianca por componente estiverem validadas. Nao faz parte do escopo de estabilizacao em andamento.

Objetivo: reutilizar a infraestrutura do Auditor para extrair questoes que ainda nao existem no catalogo diretamente dos PDFs canonicos, evitando copia manual em escala.

Arquitetura conceitual:

```
PDF canonico
-> admissao/segmentacao
-> extracao estruturada da questao
-> staging/draft_import
-> classificacao de metadados
-> revisao por confianca
-> catalogo oficial
```

Requisitos:

- Nunca inserir automaticamente no catalogo oficial; toda ingestao passa por staging e revisao humana.
- Manter referencia ao PDF/pagina/regiao original de cada questao extraida.
- Preservar texto, alternativas, formatacao, tabelas, formulas e midia conforme a capacidade do Auditor.
- Registrar confianca por componente (texto, alternativas, tabela, formula, midia, formatacao inline).
- Derivar instituicao/ano/prova/serie/materia preferencialmente de metadados estruturais do documento, nao de digitacao.
- Classificar tema/subtema/conteudo contra uma taxonomia fechada ja existente, sem criacao livre de categorias.
- Permitir revisao em lote conforme faixas de confianca.
- Usar as 1.217 questoes ja cadastradas como benchmark para medir a fidelidade da extracao automatica.
- Futuramente permitir importar uma prova inteira para staging.

Ver tambem: [[PROBLEMAS_CONHECIDOS]], [[DECISOES]], [[AUDITORIA_PROVAS]].

## Milestones posteriores ao checkpoint A/B do snapshot

- Adjudicações neutras A/B/C/D concluídas; Final Question Index V4 congelado com 48 documentos e 1.732 questões; seleção de 144 questões concluída.
- GT V4 final congelado em `d9a37577c844213152a9db8c3cded1166c3a4cb9`; configuração OCR em `5c3263e0f2e9d3f9e8aa490a4fb6b2e45455eae3`; preparação dos caches em `394ce73f38848ec90f520a25b8d3ce71dd14099a`.
- Primeira execução oficial única V4, runStamp=20261005T221306Z, formalmente congelada e publicada em `89f482b373449022423b4d34536160e62774cd2d`. Artefatos preservados; interpretação é posterior ao freeze.

Referências: [[AUDITORIA_PROVAS]], [[ESTADO_ATUAL]] e [provenance do resultado V4](../audit/holdout/results/auditor-v1-holdout-v4-first-run.provenance.json).
