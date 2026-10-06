# Ideias e próximos passos

## Papel deste documento

Visão consolidada de produto, ideias aprovadas e direções futuras do SimpleQuest. Não descreve funcionalidades já implementadas nem substitui a sequência operacional de [[ROADMAP]]; o estado factual está em [[ESTADO_ATUAL]] e as decisões persistentes em [[DECISOES]].

Consolidação de 2026-10-06. [Análise técnica e planejamento anterior](../docs/simplequest-2.0-analise-tecnica.md) permanecem como referência histórica útil, sem reescrita. Em caso de conflito de visão de produto, a decisão mais recente no brain prevalece enquanto a especificação detalhada não for atualizada. Isso não altera a arquitetura implementada por si só.

## Norte do SimpleQuest 2.0

Entregar até 31/12/2026 uma beta real e utilizável para professores e alunos, não um produto definitivo.

Conectar acervo confiável de questões, prática, revisão, conteúdos educacionais curtos, personalização, progresso, gamificação, criação de simulados, ingestão em escala e experiência visual forte.

## Experiência do aluno — quatro áreas

### 1. Início

Questões, busca, filtros e simulados; continuidade e histórico quando disponíveis. Não apresentar persistência de conta ou histórico como existentes antes de implementá-los.

### 2. Feed de aprendizagem

Uma experiência central do aluno: misturar questões, leitura dinâmica, microexplicações, mapas mentais, resumos/cartões, exemplos curtos, revisões e outros conteúdos leves.

Trabalhar conteúdo novo e conhecimento já adquirido. Com o histórico do aluno, evoluir para reforço de assuntos fracos, revisitação de assuntos antigos, revisão espaçada, adaptação da frequência e combinação de prática com explicação.

Distinguir “viu um conteúdo” de “aprendeu / demonstrou domínio”. Não conceder progresso simplesmente por tempo de tela.

Vídeos não são prioridade inicial do 2.0. A infraestrutura pode continuar compatível com mídia futura; o feed inicial privilegia formatos leves, rápidos e baratos de carregar.

### 3. Mundo do conhecimento

Um mundo visual persistente que evolui conforme o aluno aprende:

- conhecimento validado gera casas e outros elementos;
- mais domínio permite prédios e estruturas mais complexas;
- o mundo cresce dinamicamente;
- disciplinas, áreas ou trilhas podem futuramente formar regiões/distritos;
- revisões podem reforçar e manter construções;
- esquecer conteúdo não deve destruir agressivamente o mundo.

Não é um minigame separado: é uma visualização gamificada do conhecimento construído. Representa aprendizado e domínio, não tempo de tela.

### 4. Configurações

Conta, disciplinas/interesses, preferências, acessibilidade, notificações e demais opções do aluno.

## Experiência do professor — três áreas

### 1. Pesquisa

Questões, busca, filtros, preview, seleção e acesso ao construtor de simulados.

### 2. Simulados

O professor seleciona as questões e controla a apresentação. Prever:

- mostrar ou esconder origem/prova, por exemplo “CMBH - 2026”;
- uma questão por página, texto corrido ou múltiplas questões por página;
- ordenação das questões;
- exportação PDF e DOCX;
- logo, nome/instituição e cabeçalho;
- cabeçalho padrão ou personalizado.

PDF e DOCX devem compartilhar um modelo de documento comum, evitando dois motores conceitualmente separados. A impressão atual pelo navegador continua sendo estado implementado, não prova de que essas exportações futuras já existem.

### 3. Configurações

Salvar defaults de logo, cabeçalho, nome/instituição, origem visível/oculta, layout, questões por página, exportação e demais preferências recorrentes.

Aplicar os defaults automaticamente no construtor, permitindo sobrescrevê-los em um simulado específico.

## Onboarding progressivo

Primeira diferenciação: aluno ou professor. Pode ocorrer antes ou logo após login Google, conforme a arquitetura de identidade escolhida.

Depois, poucas perguntas sutis, sem questionário enorme:

- aluno: série/etapa, objetivos e disciplinas prioritárias;
- professor: disciplinas, segmentos, uso mais comum e preferências básicas de simulado.

### Direção SimpleQuest 3.0

Onboarding/personalização conversacional por texto, voz e contexto, permitindo inferir necessidades sem formulário extenso. Não é requisito do 2.0.

## Auditor e transcrição — motor compartilhado

Não criar um segundo motor independente para transcrever provas. A direção arquitetural futura é:

```text
PDF
-> Observation Layer
-> Question Boundary
-> Response Structure
-> Content Extraction
-> StructuredQuestionDraft
-> Auditor / Confidence
-> Review Queue
-> Catálogo
```

Reutilizar observation, boundary e estrutura do Auditor. Content Extraction, StructuredQuestionDraft e Review Queue são contratos/capacidades futuros a definir, não implementação atual.

O StructuredQuestionDraft deve preservar, quando possível:

- texto e alternativas;
- fórmulas, tabelas e imagens;
- origem, PDF, páginas e regiões;
- instituição, ano, prova, série e disciplina;
- confiança por componente.

A ingestão passa por staging/review queue antes do catálogo oficial. O humano revisa exceções e baixa confiança, em vez de retranscrever ou conferir tudo manualmente. Ver [[IMPORTADOR]] e [[AUDITORIA_PROVAS]].

## Meta operacional do Auditor

Norte para reduzir pelo menos aproximadamente 80% do trabalho humano de conferência:

- coverage automática >= 80%;
- precision automática >= 99,5%;
- meta forte de precision: 99,8% a 99,9%;
- unsafe_error <= 0,5%; ideal: 0,1% a 0,2%;
- not_executable < 1%, com direção próxima de zero.

São objetivos de produto, não resultados já alcançados nem garantia automática de redução humana. Precisão sem cobertura não resolve o produto; cobertura sem precisão também não. Medir conjuntamente precisão, cobertura, erros inseguros e carga de revisão.

Depois de analisar o V4, qualquer mudança funcional exige novo Holdout V5 cego para avaliação limpa, sem retunar o V4 revelado como se continuasse cego.

## Taxonomia pedagógica fechada e versionada

Modelo conceitual:

```text
Disciplina -> Área -> Conteúdo -> Subconteúdo -> Habilidade
discipline -> area -> content -> subcontent -> skill
```

IDs estáveis. Uma questão pode se relacionar a mais de um nó; usar relações N:N quando necessário. A IA escolhe IDs existentes e registra confidence; não cria categorias automaticamente durante a ingestão. Baixa confiança requer revisão humana.

Exemplos de ramos distintos:

- Química -> Química Geral -> Ligações Químicas -> Ligação Covalente.
- Química -> Química Orgânica -> Carbono e Cadeias Carbônicas.

Não confundir classificação pedagógica com trilha de estudo nem transformar rótulos livres legados em categorias novas sem curadoria.

## Escala do acervo

Chegar progressivamente a milhares de questões estruturadas e pesquisáveis:

```text
primeiras centenas -> 1.000 -> 3.000 -> 5.000 -> 10.000
```

A sequência representa lotes de validação e expansão, não substitui a contagem factual do catálogo existente. Não processar dez mil imediatamente sem medir erros sistêmicos nos primeiros lotes.

## Design como parte do produto

Não tratar design como decoração final. Buscar interface moderna, alta legibilidade, identidade própria, excelente experiência mobile, consistência aluno/professor e performance percebida.

O mundo visual deve ser atraente sem competir com o estudo. Acessibilidade e fluidez fazem parte da experiência, não de um acabamento posterior.

## Autenticação da beta

Login seguro, Google como opção prioritária de baixa fricção, papel aluno/professor, sessões, recuperação quando aplicável e autorização/permissões.

Evitar complexidade desnecessária na primeira beta. Não confundir autenticação editorial de questão com autenticação de usuário ou autorização real.

## Cobrança mínima

Primeira versão: plano, checkout, status da assinatura e entitlement/acesso.

Adiar cupons complexos, afiliados, regras comerciais sofisticadas e billing excessivamente flexível.
