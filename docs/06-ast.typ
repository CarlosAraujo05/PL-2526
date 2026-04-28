= Representação Intermédia (AST)
// - Hierarquia de nós em ast_nodes.py
// - Tipos de nós: declarações, statements, expressões, subprogramas
// - Estrutura da árvore e exemplos

A AST em `ast_nodes.py` usa `dataclass`. Nós principais: `Program`, `CompilationUnit`, `TypeDeclaration`, `AssignmentStatement`, `IfThenElse`, `DoLoop`, `GotoStatement`, `BinaryOp`, `UnaryOp`, `Variable`, `ArrayAccess`, `FunctionCall`, `Literal`.

A AST separa análise sintática da geração de código. O `codegen.py` percorre a árvore para gerar instruções VM, podendo aplicar otimizações antes (dobragem de constantes, código morto).