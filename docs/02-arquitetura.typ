= Arquitetura do Compilador

O compilador possui módulos independentes em `src/`: 
- `lexer.py`: Tokenização (via PLY).
- `parser.py`: Análise sintática e construção da AST.
- `ast_nodes.py`: Nós da árvore abstrata usando `@dataclass`.
- `symbol_table.py`: Tabela de símbolos com escopo.
- `optimizer.py`: Otimizações na AST (Constant Folding, Dead Code Elimination).
- `codegen.py`: Geração de instruções VM (Stack machine).

O `main.py` orquestra o pipeline completo: lê `.for`, gera tokens, constrói a AST, otimiza a árvore, e emite código para um ficheiro `.vm`. Aceita o _flag_ opcional `--comments` (ou `-c`) para incluir comentários explicativos no ficheiro `.vm` gerado (por omissão, o output é limpo).
