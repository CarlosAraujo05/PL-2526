= Análise Léxica
// - Formato fixed-format do Fortran 77 (colunas 1-5, 6, 7-72)
// - Implementação com PLY (lexer.py)
// - Tokens reconhecidos e operadores
// - Tratamento de comentários e continuação de linhas

O `lexer.py` usa `ply.lex` e trata o formato fixed-format Fortran 77: colunas 1-5 (labels), 6 (continuação/comentário), 7-72 (código). O pré-processador `FortranPreprocessor` une linhas e remove comentários antes da tokenização.

Tokens: palavras-chave (`PROGRAM`, `IF`, `DO`, etc.), operadores (`.GT.`, `**`), literais (inteiros, reais, strings, `.TRUE.`/`.FALSE.`) e identificadores (até 6 caracteres, maiúsculas). O lexer é case-insensitive. Erros léxicos lançam `LexerError` com linha de origem.