= Arquitetura do Compilador
// - Visão geral da pipeline: lexer → parser → AST → análise semântica → geração de código
// - Organização modular do código (estrutura de diretórios)

O compilador tem módulos independentes em `src/`: `lexer.py` (tokenização), `parser.py` (análise sintática + AST), `ast_nodes.py` (nós da árvore), `symbol_table.py` (tabela de símbolos) e `codegen.py` (geração VM). O `main.py` orquestra o pipeline: lê `.for`, normaliza formato fixed-format, gera tokens com `ply.lex`, constrói AST com `ply.yacc`, e emite instruções VM. A separação de responsabilidades facilita manutenção e teste.