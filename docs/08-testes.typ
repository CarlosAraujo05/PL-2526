= Testes e Validação
// - Programas de teste (tests/*.for)
// - Casos de teste: fatorial, primos, soma de arrays, etc.
// - Verificação de correção no VM

O compilador foi validado de ponta a ponta com cinco programas baseados nos cenários de teste da disciplina. Para automatizar este processo, foi desenvolvida uma _test suite_ em Python utilizando a biblioteca `pytest` (`tests/test_compiler.py`).

A automação garante a verificação contínua (CI) e testa os seguintes programas:
- `hello.for`: Avalia rotinas básicas de I/O (`PRINT` de _strings_).
- `fatorial.for`: Valida o cálculo matemático, controlo de fluxo complexo iterativo (`DO`) e resolução de variáveis escalares inteiras.
- `primo.for`: Verifica ciclos, manipulação lógica e construções condicionais (`IF`/`GOTO`) e ramificações condicionais baseadas em booleanos implícitos.
- `somaarr.for`: Testa o correto parseamento de dimensões, declarações e acesso por indexação a Arrays Unidimensionais (1D).
- `conversor.for`: Valida a compatibilidade e a transição entre múltiplos subprogramas (Funções e Procedimentos).

Em todos os casos, a suite não só avalia o sucesso da fase léxica e sintática (sem levantar erros do parser/lexer) mas constrói a AST, realiza as otimizações Middle-end via `optimizer.py`, e efetivamente emite o binário (`.vm`). Todos os 5 testes garantem retorno de código de erro zero.
