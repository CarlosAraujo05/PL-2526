= Análise Sintática
// - Gramática independente de contexto (BNF) em CFG.md
// - Implementação com PLY Yacc (parser.py)
// - Construção da Árvore Sintática Abstrata (AST)
// - Tratamento de erros sintáticos

O `parser.py` usa `ply.yacc` (LALR(1)) com gramática BNF em `CFG.md`. A precedência de operadores é garantida pela hierarquia: `logical_or` → `logical_and` → `relational` → `additive` → `multiplicative` → `power` → `unary` → `primary`.

O parser integra verificações semânticas: duplicados, variáveis não declaradas, dimensões de arrays, labels em ciclos `DO`, e saltos `GOTO`. Cada regra constrói nós da AST (`ast_nodes.py`). Erros sintáticos lançam `SyntaxError`, semânticos lançam `SemanticError`.