# Holdout V4 Postmortem - sample freeze

- Base: `0eda2880edaa70915e80cc78889cb837307e7d43`; result freeze: `89f482b373449022423b4d34536160e62774cd2d`.
- Resultado oficial preservado: 144 executable; 60 correct, 1 partial, 66 safe_abstention, 5 unsafe_error, 12 not_applicable, 0 not_executable.
- Nenhuma pagina/PDF, PNG, OCR text, GT notes ou evidencia visual foi aberta para esta selecao; somente metadata congelada do resultado foi usada.
- 24/66 safe_abstention selecionados deterministicamente: mandatory missing_marker_observation/weak_anchor_only/hybrid, grupo sem blocker ate 8, boundary_uncertain ate 24; strata lexicograficos `(sourceType, markerStyle, contentKind)`, ranking SHA256 e round-robin conforme JSON.
- Nenhuma substituicao sera feita depois da inspecao visual. A amostra e diagnostica, nao aleatoria proporcional: seus percentuais crus nao estimam recuperabilidade dos 66.
- Os cinco unsafe e um partial sao sempre obrigatorios, fora da amostra de 24.
- Proximo passo, somente depois do commit e push deste freeze: analise forense dos 30 casos.
- Nenhum patch, tuning ou heuristica; Auditor oficial nao rerodado, officialAuditorExecutionCount=1.
- Discrepancia inicial de status Git resolvida apenas por refresh autorizado: os dois arquivos do brain eram byte-identicos ao HEAD; bytes e core.autocrlf=true preservados. Nenhuma conclusao do brain atualizada nesta etapa.
- Family metadata com caracteres de substituicao no resultado congelado e preservada literalmente; nenhuma normalizacao de fontes.
