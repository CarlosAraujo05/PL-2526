= Representação Intermédia (AST)

A estruturação final das validações recai na geração da *Abstract Syntax Tree (AST)*. Em oposição às implementações baseadas puramente em tuplos nativos em Python, adotou-se o uso estrito de módulos `@dataclass` (`ast_nodes.py`), que propiciam uma semântica rígida, documentada e com verificação de tipo.

A infraestrutura ramifica-se nos seguintes nós de topo:
- `CompilationUnit` e `Program`: O ponto fulcral e originário da representação para o main script e subprogramas.
- _Declarações_: Suportadas via `TypeDeclaration` e parâmetros globais imutáveis.
- _Statements (Instruções)_: Enquadramentos complexos de fluxo via `IfThenElse` (com suporte a ramificações múltiplas de _elseif_), `DoLoop`, saltos explícitos via `GotoStatement`, e as primitivas IO `ReadStatement` / `PrintStatement`.
- _Expressões (Expressions)_: Cálculos puramente avaliados via `BinaryOp`, `UnaryOp`, e resoluções terminadas em `Literal` ou chamadas recursivas `FunctionCall`.

Todos os nós estendem rigorosamente uma classe base abstracta genérica `Node`, na qual o rastreamento da linha (`lineno`) garante depuração clara caso a _Pipeline_ intercetar falhas na Geração ou Otimização. Em última análise, a AST limpa e validada garante o isolamento funcional do Front-end em relação ao Back-end.