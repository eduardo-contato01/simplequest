# Orientacoes Para Agentes

Antes de mudancas importantes no SimpleQuest:

1. Leia `brain/00_INDEX.md` e `brain/ESTADO_ATUAL.md`.
2. Consulte os documentos relacionados a area alterada, especialmente arquitetura, modelo de questao, importador, auditoria, decisoes, roadmap e problemas conhecidos.
3. Atualize o brain somente quando uma decisao, arquitetura, comportamento ou estado relevante mudar.
4. Nunca registre senhas, tokens, credenciais ou dados pessoais.
5. Evite duplicar documentacao que ja exista em `docs/` ou no proprio brain; prefira links e resumos operacionais.

Este repositorio usa o brain como memoria persistente curta para humanos e agentes de IA. Ele nao deve virar diario de execucao nem deposito de logs.

## Leitura orientada para trabalho novo

- ROADMAP faz parte da leitura inicial junto de ESTADO_ATUAL, após consultar brain/00_INDEX.md.
- Consulte brain/IDEIAS_E_PROXIMOS_PASSOS.md para decisões de produto/UX; a visão aprovada não equivale a implementação atual.
- HISTORICO não deve ser carregado por padrão.
- Consulte brain/HISTORICO.md somente quando for preciso recuperar contexto antigo ou a origem de uma decisão/etapa.
- CONTEXTO_SIMPLEQUEST.md continua sendo log cronológico incremental, não documento de leitura inicial.

## Regras permanentes para auditoria e holdouts

Antes de trabalhar com PDFs, indexadores, holdouts, Ground Truth ou Auditor, leia
obrigatoriamente [a política de engenharia de auditoria](docs/AUDIT_ENGINEERING_RULES.md)
e os protocolos congelados aplicáveis. As regras permanentes são:

1. Exigir preflight físico independente de PDFs antes de indexação e seleção em novos pipelines/holdouts.
2. Verificar SHA256 completo e contagem física com pypdf e Poppler/pdfinfo; persistir versões, diagnósticos e divergências.
3. Persistir evidências e hashes históricos necessários no momento de sua criação, nunca apenas em memória.
4. Classificar previamente fontes essenciais congeladas, evidências obrigatórias de decisão e auxiliares reproduzíveis.
5. Usar checkpoints atômicos e tarefas longas recuperáveis, com verificação em blocos persistentes.
6. Preservar bytes locais e line endings históricos; distinguir conteúdo físico do conteúdo filtrado pelo Git.
7. Aplicar STOP proporcional a bloqueios materiais ou contratuais, sem transformar warnings já avaliados em novos bloqueios.
8. Proteger o cegamento, a sequência de freezes e os protocolos imutáveis; não usar GT, gabaritos ou métricas para admissibilidade.
9. Proibir certificações retroativas sem evidência independente; hashes atuais são apenas prospectivos quando falta referência histórica.
10. Exigir autorização explícita, escopo delimitado e rastreabilidade para exceções pós-freeze, sem fingir pré-registro nem reescrever contratos históricos.

O componente integrado P0/P1 é implementação futura, não funcionalidade já
presente no runner. Esta política não autoriza mudanças funcionais, reprocessamento
de holdouts congelados ou avanço de fase sem autorização própria.
