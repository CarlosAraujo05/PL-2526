= Otimizações e Geração de Código

== Otimização (Middle-end)
Antes de gerar código, a Árvore Sintática Abstrata (AST) passa por um módulo de otimização (`optimizer.py`). Implementámos passagens de otimização focadas na melhoria de performance (valorização), nomeadamente:
- *Constant Folding*: Expressões binárias (`+`, `-`, `*`, `/`) entre literais numéricos são avaliadas em tempo de compilação.
- *Dead Code Elimination (DCE)*: Remoção de código inatingível (e.g. instruções após um `GOTO` ou `RETURN` que não possuam `label`).

== Geração de Código VM (Back-end)
O módulo `codegen.py` implementa o padrão *Visitor* para percorrer a AST e gerar um ficheiro `.vm` com as instruções para a máquina virtual baseada em pilha (stack machine).

=== Mapeamento de Construções Fortran
- *Variáveis e Atribuições*: Utiliza-se um contador global de endereços. A cada variável não mapeada é atribuído um offset. A escrita faz-se com `STOREG addr` e a leitura com `PUSHG addr`. Arrays usam instruções correspondentes (`STOREA`).
- *Aritmética e Lógica*: Expressões são avaliadas em pós-ordem. Operadores geram as instruções nativas: `ADD`, `SUB`, `MUL`, `DIV`, `INFEQ`, `SUPEQ`, etc.
- *Controlo de Fluxo (IF / GOTO)*: As _labels_ de Fortran (inteiros 1-5 colunas) são mapeadas para _labels_ VM unívocas (ex: `L0`, `L1`). Instruções como `JZ` (Jump if Zero) e `JUMP` realizam os desvios.
- *Ciclos (DO)*: Um DO loop `DO 10 I=1,N` inicializa a variável de iteração, define a _label_ de início, testa a condição (saída via `JZ`), corre o corpo, incrementa a variável, e faz o `JUMP` para o início.
- *I/O*: `READ` extrai o input e armazena via `STOREG`. `PRINT` coloca as expressões na pilha e emite `WRITEI`, `WRITELN` ou `WRITES`.
