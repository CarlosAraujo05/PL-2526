= Otimizações e Geração de Código

== Otimização (Middle-end)
Antes de gerar código, a Árvore Sintática Abstrata (AST) passa por um módulo de otimização (`optimizer.py`). Implementámos passagens de otimização focadas na melhoria de performance (valorização), nomeadamente:
- *Constant Folding*: Expressões binárias (`+`, `-`, `*`, `/`, `**`) e operadores relacionais/lógicos entre literais são avaliados em tempo de compilação, incluindo os limites de ciclos `DO`.
- *Dead Code Elimination (DCE)*: Remoção de código inatingível (instruções após `GOTO` / `RETURN` sem `label`) e eliminação de *dead stores* (atribuições cujo valor nunca é lido posteriormente no mesmo bloco).
- *IF Constant Folding*: Quando a condição de um `IF` é um literal lógico (`.TRUE.` ou `.FALSE.`), o ramo correspondente é colapsado diretamente.

== Geração de Código VM (Back-end)
O módulo `codegen.py` implementa o padrão *Visitor* para percorrer a AST e gerar um ficheiro `.vm` com as instruções para a máquina virtual baseada em pilha (stack machine).

=== Mapeamento de Construções Fortran
- *Variáveis e Atribuições*: Utiliza-se um contador global de endereços. A escrita faz-se com `STOREG addr` (globais) ou `STOREL addr` (locais em subprogramas) e a leitura com `PUSHG` / `PUSHL`. Arrays unidimensionais alocam-se no _heap_ estruturado via `ALLOC` e acedem-se com `LOADN` / `STOREN` (indexação convertida de 1-based para 0-based).
- *Tipos Numéricos*: O compilador distingue `INTEGER` e `REAL`. Operações aritméticas com pelo menos um operando `REAL` geram opcodes float (`FADD`, `FSUB`, `FMUL`, `FDIV`, `FINF`, `FINFEQ`, etc.) e inserem conversões automáticas (`ITOF`, `FTOI`). I/O de reais utiliza `WRITEF` / `ATOF`.
- *Aritmética e Lógica*: Expressões são avaliadas em pós-ordem. Operadores inteiros geram `ADD`, `SUB`, `MUL`, `DIV`, `INFEQ`, `SUPEQ`, etc.
- *Controlo de Fluxo (IF / GOTO)*: As _labels_ de Fortran são mapeadas para _labels_ VM unívocas. Instruções como `JZ` (Jump if Zero) e `JUMP` realizam os desvios.
- *Ciclos (DO)*: Um DO loop inicializa a variável de iteração, testa a condição (`INFEQ`), corre o corpo, incrementa, e repete via `JUMP`.
- *I/O*: `READ` extrai _strings_ do input e converte via `ATOI` / `ATOF` antes de armazenar. `PRINT` coloca as expressões na pilha e emite `WRITEI`, `WRITEF`, `WRITES` ou `WRITELN`.

=== Subprogramas (FUNCTION / SUBROUTINE)
A convenção de chamada segue o modelo da VM: o _caller_ empilha o _slot_ de retorno, os argumentos por ordem inversa, e o endereço da função (`PUSHA` + `CALL`). No _callee_, os parâmetros acedem-se com offsets negativos de `PUSHL` (ex: `PUSHL -1`, `PUSHL -2`) e as variáveis locais alocam-se com `PUSHN`. Antes de cada `RETURN`, o compilador emite `POP n` para libertar o espaço de pilha ocupado pelas locais, garantindo que o `sp` é restaurado corretamente. A potenciação (`**`) e o operador `MOD` são suportados via _helpers_ runtime (`POW:` e `MOD:`) anexados no final do ficheiro `.vm` apenas quando necessário.
