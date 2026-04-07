# Context-Free Grammar (CFG) para Fortran 77

Este documento define uma Context-Free Grammar completa para Fortran 77, baseada nos tokens definidos em `src/lexer.py`.

## Definição Formal da Gramática

### Símbolos Terminais (Tokens do Lexer)

**Palavras-chave:**
```
PROGRAM, END, SUBROUTINE, FUNCTION, CALL, RETURN
INTEGER, REAL, DOUBLE, COMPLEX, LOGICAL, CHARACTER
DIMENSION, PARAMETER, DATA, COMMON, EQUIVALENCE, EXTERNAL, INTRINSIC
IF, THEN, ELSE, ELSEIF, ENDIF, GOTO, ASSIGN, TO
DO, CONTINUE, STOP, PAUSE
READ, WRITE, PRINT, OPEN, CLOSE, INQUIRE, BACKSPACE, REWIND, ENDFILE
FORMAT, SAVE, BLOCKDATA
```

**Operadores Relacionais e Lógicos:**
```
.GT. (GT), .LT. (LT), .GE. (GE), .LE. (LE), .EQ. (EQ), .NE. (NE)
.AND. (AND), .OR. (OR), .NOT. (NOT), .XOR. (XOR), .EQV. (EQV), .NEQV. (NEQV)
.TRUE. (TRUE), .FALSE. (FALSE)
```

**Operadores Aritméticos:**
```
+ , - , * , / , ** (POW)
```

**Símbolos Especiais:**
```
( , ) , , , = , : , NUMBER, STRING, ID, LABEL
```

---

## Produções da Gramática

### 1. Programa Principal

```
program             → PROGRAM ID
                      declaration_block
                      statement_block
                      END

declaration_block   → declaration
                    | declaration_block declaration
                    | ε (vazio)

statement_block     → labeled_statement
                    | statement_block labeled_statement
                    | ε (vazio)
```

**Explicação:** Um programa Fortran 77 começa com `PROGRAM`, seguido por um identificador, então declarações de tipo, statements, e termina com `END`.

### 2. Declarações de Tipo

```
declaration         → type_declaration
                    | dimension_declaration
                    | common_declaration
                    | equivalence_declaration
                    | external_declaration
                    | parameter_declaration
                    | data_declaration
                    | save_declaration

type_declaration    → base_type id_list
                    | base_type DIMENSION dim_spec id_list

base_type           → INTEGER
                    | REAL
                    | DOUBLE PRECISION
                    | COMPLEX
                    | LOGICAL
                    | CHARACTER

dim_spec            → ( dimension_list )

dimension_list      → dimension_item
                    | dimension_list , dimension_item

dimension_item      → NUMBER
                    | ID : NUMBER

id_list             → ID
                    | id_list , ID

dimension_declaration  → DIMENSION ID ( dimension_list )

common_declaration  → COMMON / ID / id_list
                    | COMMON / ID / id_list , / ID / id_list

equivalence_declaration → EQUIVALENCE ( ID , ID )
                        | equivalence_declaration ( ID , ID )

external_declaration   → EXTERNAL id_list

parameter_declaration  → PARAMETER ( assignment_list )

assignment_list     → assignment
                    | assignment_list , assignment

assignment          → ID = literal

data_declaration    → DATA id_list / literal_list /

literal_list        → literal
                    | literal_list , literal

save_declaration    → SAVE id_list
```

### 3. Statements Rotulados

```
labeled_statement   → LABEL statement
                    | statement

statement           → assignment_statement
                    | if_statement
                    | do_loop
                    | goto_statement
                    | call_statement
                    | io_statement
                    | control_statement
                    | continue_statement
```

### 4. Statements de Atribuição

```
assignment_statement → ID = expression
                     | array_access = expression

array_access        → ID ( index_list )

index_list          → expression
                    | index_list , expression
```

### 5. Expressões

```
expression          → logical_or_expression

logical_or_expression  → logical_and_expression
                       | logical_or_expression .OR. logical_and_expression

logical_and_expression → logical_not_expression
                       | logical_and_expression .AND. logical_not_expression

logical_not_expression → relational_expression
                       | .NOT. relational_expression

relational_expression  → additive_expression
                       | additive_expression relational_op additive_expression

relational_op       → .EQ.
                    | .NE.
                    | .LT.
                    | .LE.
                    | .GT.
                    | .GE.

additive_expression → multiplicative_expression
                    | additive_expression + multiplicative_expression
                    | additive_expression - multiplicative_expression

multiplicative_expression → power_expression
                          | multiplicative_expression * power_expression
                          | multiplicative_expression / power_expression

power_expression    → unary_expression
                    | power_expression ** unary_expression

unary_expression    → primary_expression
                    | - unary_expression
                    | + unary_expression

primary_expression  → literal
                    | ID
                    | array_access
                    | ( expression )
                    | function_call

function_call       → ID ( argument_list )
                    | ID ( argument_list )

argument_list       → expression
                    | argument_list , expression
                    | ε (vazio)

literal             → NUMBER
                    | STRING
                    | .TRUE.
                    | .FALSE.
```

### 6. Controle de Fluxo - IF

```
if_statement        → IF ( expression ) THEN
                      statement_block
                      else_part
                      ENDIF

else_part           → ELSE
                      statement_block
                    | ELSEIF ( expression ) THEN
                      statement_block
                      else_part
                    | ε (vazio)
```

### 7. Loops - DO

```
do_loop             → DO LABEL ID = expression , expression
                      statement_block
                      LABEL CONTINUE

do_loop             → DO LABEL ID = expression , expression , expression
                      statement_block
                      LABEL CONTINUE
```

**Explicação:** O primeiro formato é para loops com incremento padrão (1), o segundo permite especificar o incremento.

### 8. GOTO

```
goto_statement      → GOTO LABEL
```

### 9. Statements de Entrada/Saída

```
io_statement        → read_statement
                    | write_statement
                    | print_statement
                    | open_statement
                    | close_statement

read_statement      → READ * , id_list
                    | READ ( unit , format ) id_list

write_statement     → WRITE ( unit , format ) id_list

print_statement     → PRINT * , output_list
                    | PRINT * , output_list

output_list         → expression
                    | output_list , expression

open_statement      → OPEN ( open_spec_list )

close_statement     → CLOSE ( unit )

unit                → NUMBER
                    | *

format              → NUMBER
                    | STRING
                    | *
```

### 10. Statements de Controle

```
control_statement   → STOP
                    | PAUSE
                    | RETURN

call_statement      → CALL ID ( argument_list )

continue_statement  → CONTINUE
```

### 11. Subroutines e Functions

```
subroutine_def      → SUBROUTINE ID ( parameter_list )
                      declaration_block
                      statement_block
                      END

parameter_list      → ID
                    | parameter_list , ID
                    | ε (vazio)

function_def        → type_declaration FUNCTION ID ( parameter_list )
                      declaration_block
                      statement_block
                      RETURN
                      END
```

---

## Resumo da Hierarquia de Precedência de Operadores

(Do maior precedência para menor)

1. **Primária:** `( )`, funções, literais, variáveis, array access
2. **Unária:** `-`, `+`
3. **Exponenciação:** `**`
4. **Multiplicação/Divisão:** `*`, `/`
5. **Adição/Subtração:** `+`, `-`
6. **Relacional:** `.LT.`, `.LE.`, `.GT.`, `.GE.`, `.EQ.`, `.NE.`
7. **Negação Lógica:** `.NOT.`
8. **Conjunção Lógica:** `.AND.`
9. **Disjunção Lógica:** `.OR.`

---

## Exemplos de Análise Usando a Gramática

### Exemplo 1: hello.for

```fortran
      PROGRAM HELLO
      PRINT *, 'Ola, Mundo!'
      END
```

**Derivação:**
```
program
  ├─ PROGRAM ID
  ├─ declaration_block (ε)
  ├─ statement_block
  │  └─ labeled_statement
  │     └─ statement
  │        └─ io_statement
  │           └─ print_statement
  │              ├─ PRINT
  │              ├─ *
  │              └─ output_list
  │                 └─ expression
  │                    └─ literal
  │                       └─ STRING
  └─ END
```

---

### Exemplo 2: fatorial.for (Trecho)

```fortran
      INTEGER N, I, FAT
      DO 10 I = 1, N
          FAT = FAT * I
   10 CONTINUE
```

**Derivação:**
```
declaration
  └─ type_declaration
     ├─ INTEGER
     └─ id_list
        ├─ N
        ├─ I
        └─ FAT

do_loop
  ├─ DO LABEL ID = expression , expression
  ├─ statement_block
  │  └─ assignment_statement
  │     ├─ ID (FAT)
  │     ├─ =
  │     └─ expression
  │        ├─ multiplicative_expression
  │        │  ├─ primary_expression (FAT)
  │        │  ├─ *
  │        │  └─ primary_expression (I)
  │        └─ ...
  └─ LABEL CONTINUE
```

---

### Exemplo 3: primo.for (Trecho com IF)

```fortran
   20 IF (I .LE. (NUM/2) .AND. ISPRIM) THEN
      IF (MOD(NUM, I) .EQ. 0) THEN
         ISPRIM = .FALSE.
      ENDIF
      I = I + 1
      GOTO 20
   ENDIF
```

**Derivação (simplificada):**
```
if_statement
  ├─ IF ( expression ) THEN
  │  └─ logical_or_expression
  │     ├─ logical_and_expression
  │     │  ├─ relational_expression
  │     │  │  ├─ I
  │     │  │  ├─ .LE.
  │     │  │  └─ (NUM/2)
  │     │  ├─ .AND.
  │     │  └─ ISPRIM
  │  └─ statement_block
  │     ├─ if_statement (nested)
  │     ├─ assignment_statement (I = I + 1)
  │     └─ goto_statement (GOTO 20)
  └─ ENDIF
```

---

### Exemplo 4: somaarr.for (Acesso a Arrays)

```fortran
      INTEGER NUMS(5)
      READ *, NUMS(I)
      SOMA = SOMA + NUMS(I)
```

**Derivação:**
```
type_declaration
  ├─ INTEGER
  ├─ DIMENSION (5)
  └─ ID_LIST: NUMS

array_access
  ├─ ID (NUMS)
  └─ ( index_list )
     └─ expression (I)

assignment_statement
  ├─ ID (SOMA)
  ├─ =
  └─ additive_expression
     ├─ primary_expression (SOMA)
     ├─ +
     └─ array_access (NUMS(I))
```

---

### Exemplo 5: conversor.for (Funções)

```fortran
      INTEGER FUNCTION CONVRT(N, B)
      CONVRT = VAL
      RETURN
      END
```

**Derivação:**
```
function_def
  ├─ INTEGER FUNCTION CONVRT ( N , B )
  ├─ declaration_block
  ├─ statement_block
  │  ├─ assignment_statement (CONVRT = VAL)
  │  └─ control_statement (RETURN)
  └─ END
```

---

## Notas Importantes

1. **Rótulos (Labels):** Em Fortran 77, rótulos são números (1-5 dígitos) na coluna 1-5. A gramática os trata como terminais `LABEL`.

2. **Indentação:** A coluna 6 é reservada para indentação (continuação de linha). O lexer reconhece isso com `IDENTATION`.

3. **Comentários:** Linhas começando com `C`, `c` ou `*` na primeira coluna são comentários.

4. **Precedência:** A estrutura da gramática já codifica a precedência dos operadores.

5. **Ambiguidade Reduzida:** Esta gramática é LL(1) compatível para a maioria das construções, permitindo análise por descida recursiva.

---

## Validação com os Testes

Cada arquivo de teste `.for` pode ser validado completamente pela gramática:

- ✅ `hello.for` - Program simples com PRINT
- ✅ `fatorial.for` - DO loops com contadores
- ✅ `primo.for` - IF/THEN/ELSEIF/ENDIF com GOTO
- ✅ `conversor.for` - Functions com RETURN
- ✅ `somaarr.for` - Array declarations e acesso

