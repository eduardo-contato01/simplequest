# Importador

Fonte principal: scripts em `scripts/`, especialmente `extract_question_media.py`.

## Pipeline atual confirmado

- Le `public/data/questions.json`.
- Agrupa questoes por `sourceDocument` e `sourceBookmark`.
- Procura DOCX em `work/source_files`.
- Abre DOCX como ZIP e le `word/document.xml` e `word/_rels/document.xml.rels`.
- Delimita questoes por bookmarks com padrao parecido com `CMB_2004_3`.
- Extrai texto, tabelas, formulas OMML, imagens e runs de sobrescrito/subscrito.
- Fórmulas OMML em parágrafos comuns são convertidas por `omml_to_latex()` e preservadas como blocos `formula`.
- Tabelas DOCX são extraídas por `table_text()` como texto/sintaxe interna a partir de `w:t`; OMML dentro de células não entra no texto da célula nessa etapa.
- Converte imagens PNG/JPG/JPEG/GIF para WebP em `public/question-media`.
- Atualiza campos do catalogo quando executado com `--extract`.
- Gera relatorio em `work/analysis_output/media-extraction.json`.

## Scripts auxiliares

- `scripts/rename_question_media.py`: renomeia imagens para padrao derivado de escola/ano/numero e arquiva orfas em `work/orphaned-question-media`.
- `scripts/catalog_image_dimensions.py`: registra dimensoes naturais das imagens ja extraidas.
- `scripts/capture-print-baseline.mjs`: captura/verifica referencia de impressao e interacoes; nao e importador de provas.

## Possiveis perdas de fidelidade

- Formatos de imagem fora de PNG/JPG/JPEG/GIF viram `pending-media`.
- Conversao OMML para LaTeX cobre varios casos, mas nao garante equivalencia completa para toda matematica do Word.
- Tabelas Word sao transformadas em texto/sintaxe interna; detalhes de layout original podem se perder.
- Fórmulas dentro de células de tabela podem se perder na importação atual, pois a célula é reduzida a texto (`w:t`) antes de ser representada como bloco `table`.
- O modelo atual consegue renderizar fórmulas dentro de tabela quando o bloco `table` usa `content` com blocos inline `formula`, mas `tableData` sozinho é textual e não representa fórmula de forma nativa.
- A separacao de alternativas depende de heuristica pelos ultimos blocos textuais conforme o numero de alternativas.
- Texto formatado importado pelo script atual nao cobre todos os estilos possiveis do Word.
- Midias e parte das fontes ficam em `work/`, que nao e fonte versionada principal.

## Cuidados

- Nao executar importacao em massa sem backup do catalogo e imagens.
- Validar visualmente amostras com texto, formulas, tabelas, imagens no enunciado e imagens nas alternativas.
- Conferir questoes com `pending-media` antes de autenticar.
- Em auditoria de fidelidade, comparar contra o PDF original como fonte canônica. O DOCX ajuda na estrutura, mas não decide conflitos de conteúdo ou formatação.

Ver tambem: [[AUDITORIA_PROVAS]], [[MODELO_DE_QUESTAO]].
