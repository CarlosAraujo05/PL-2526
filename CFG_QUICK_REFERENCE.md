# Quick Reference - CFG Fortran 77

## 📋 Regras Fundamentais

### 1. Estrutura de um Programa

```
program → PROGRAM ID
          declaration_block
          statement_block
          END
```

**Exemplo:**
```fortran
PROGRAM MYPROGRAM
  INTEGER X
  X = 5
END
```

---

### 2. Declarações de Tipo

| Tipo | Sintaxe |
|------|---------|
| Inteiros | `INTEGER ID_LIST` |
| Reais | `REAL ID_LIST` |
| Lógicos | `LOGICAL ID_LIST` |
| Caracteres | `CHARACTER ID_LIST` |
| Arrays | `TYPE ID(DIM_LIST)` |

**Exemplos:**
```fortran
INTEGER N, I, J
REAL X, Y, Z
LOGICAL FLAG
CHARACTER NAME
INTEGER ARRAY(10)
REAL MATRIX(3, 3)
```

---

### 3. Atribuições

```
assignment → ID = expression
           | array_access = expression

array_access → ID ( index_list )
```

**Exemplos:**
```fortran
X = 10
Y = X + 5
ARRAY(I) = 100
MATRIX(I, J) = X * Y
```

---

### 4. Expressões

#### Precedência (Alto → Baixo)

| Nível | Operadores | Exemplo |
|-------|-----------|---------|
| 1 | `()`, funções | `(A+B) * 2` |
| 2 | Unária: `-`, `+` | `-X`, `+Y` |
| 3 | `**` | `2 ** 3` |
| 4 | `*`, `/` | `A * B / C` |
| 5 | `+`, `-` | `A + B - C` |
| 6 | Relacional | `A .LT. B` |
| 7 | `.NOT.` | `.NOT. FLAG` |
| 8 | `.AND.` | `A .AND. B` |
| 9 | `.OR.` | `A .OR. B` |

**Exemplos:**
```fortran
X = 2 + 3 * 4         ! = 14 (multiplicação primeiro)
Y = (2 + 3) * 4       ! = 20 (parênteses forçam ordem)
Z = A .LE. B .AND. C  ! (A ≤ B) ∧ C
FLAG = .NOT. X .EQ. 0 ! ¬(X = 0)
```

---

### 5. Controle de Fluxo

#### IF/THEN/ENDIF

```
if_statement → IF ( expression ) THEN
               statement_block
               [ ELSE statement_block ]
               ENDIF
```

**Exemplo:**
```fortran
IF (X .GT. 0) THEN
  PRINT *, 'Positivo'
ELSE
  PRINT *, 'Não positivo'
ENDIF
```

#### IF/THEN/ELSEIF/ENDIF

```
if_statement → IF ( expression ) THEN
               statement_block
               [ ELSEIF ( expression ) THEN statement_block ]*
               [ ELSE statement_block ]
               ENDIF
```

**Exemplo:**
```fortran
IF (X .LT. 0) THEN
  PRINT *, 'Negativo'
ELSEIF (X .EQ. 0) THEN
  PRINT *, 'Zero'
ELSE
  PRINT *, 'Positivo'
ENDIF
```

#### DO Loop

```
do_loop → DO LABEL ID = expr1 , expr2 [ , expr3 ]
          statement_block
          LABEL CONTINUE
```

**Exemplos:**
```fortran
! Contador de 1 a 10 (incremento padrão = 1)
DO 100 I = 1, 10
  PRINT *, I
100 CONTINUE

! Contador de 1 a 100 com incremento de 2
DO 200 I = 1, 100, 2
  PRINT *, I
200 CONTINUE
```

#### GOTO

```
goto → GOTO LABEL
```

**Exemplo (loop backwards):**
```fortran
10 IF (X .GT. 0) THEN
  X = X - 1
  GOTO 10
ENDIF
```

---

### 6. Entrada/Saída

#### PRINT

```
PRINT * , output_list
PRINT format , output_list

output_list → expression [ , expression ]*
```

**Exemplos:**
```fortran
PRINT *, 'Olá'
PRINT *, X, Y, Z
PRINT *, 'O valor é: ', X
```

#### READ

```
READ * , id_list
READ ( unit , format ) id_list
```

**Exemplos:**
```fortran
READ *, X
READ *, N, I, J
READ *, ARRAY(I)
```

---

### 7. Operadores Lógicos e Relacionais

| Operador | Significado | Tipo |
|----------|-----------|------|
| `.EQ.` | Igualdade | Relacional |
| `.NE.` | Diferença | Relacional |
| `.LT.` | Menor que | Relacional |
| `.LE.` | Menor ou igual | Relacional |
| `.GT.` | Maior que | Relacional |
| `.GE.` | Maior ou igual | Relacional |
| `.AND.` | E lógico | Lógico |
| `.OR.` | Ou lógico | Lógico |
| `.NOT.` | Negação | Lógico |
| `.TRUE.` | Verdadeiro | Constante |
| `.FALSE.` | Falso | Constante |

**Exemplos:**
```fortran
IF (X .EQ. 5) THEN
IF (X .NE. 0) THEN
IF (X .LT. 10 .AND. Y .GT. 5) THEN
IF (.NOT. FLAG) THEN
LOGICAL_VAR = .TRUE.
```

---

### 8. Funções

#### Chamada de Função

```
function_call → ID ( [ argument_list ] )

argument_list → expression [ , expression ]*
```

**Exemplos:**
```fortran
Y = SIN(X)
Z = MAX(A, B, C)
RESULT = CONVRT(NUM, BASE)
```

#### Definição de Função

```
function_def → TYPE FUNCTION ID ( [ parameter_list ] )
               declaration_block
               statement_block
               ID = return_value
               RETURN
               END

parameter_list → ID [ , ID ]*
```

**Exemplo:**
```fortran
INTEGER FUNCTION FACTORIAL(N)
  INTEGER N
  IF (N .LE. 1) THEN
    FACTORIAL = 1
  ELSE
    FACTORIAL = N * FACTORIAL(N-1)
  ENDIF
  RETURN
END
```

---

### 9. Subroutines

```
subroutine_def → SUBROUTINE ID ( [ parameter_list ] )
                 declaration_block
                 statement_block
                 END
```

**Exemplo:**
```fortran
SUBROUTINE PRINT_ARRAY(ARR, SIZE)
  INTEGER SIZE
  INTEGER ARR(SIZE)
  INTEGER I
  DO 10 I = 1, SIZE
    PRINT *, ARR(I)
10 CONTINUE
END
```

---

## 🎯 Padrões Comuns

### Pattern 1: Loop com Acumulador

```fortran
SUM = 0
DO 10 I = 1, N
  SUM = SUM + ARRAY(I)
10 CONTINUE
PRINT *, SUM
```

**CFG Coberta:**
- `assignment_statement` (SUM = 0)
- `do_loop` (DO ... CONTINUE)
- `array_access` (ARRAY(I))
- `additive_expression` (SUM + ARRAY(I))

### Pattern 2: Condicional com Expressão Complexa

```fortran
IF (X .LE. (N/2) .AND. FLAG) THEN
  ! Statements
ENDIF
```

**CFG Coberta:**
- `logical_and_expression` (conecta duas sub-expressões)
- `relational_expression` (X .LE. ...)
- `multiplicative_expression` (N / 2)
- Precedência: `/` antes de `.LE.` antes de `.AND.`

### Pattern 3: Função com Múltiplos Returns

```fortran
INTEGER FUNCTION SIGN(X)
  REAL X
  IF (X .LT. 0) THEN
    SIGN = -1
  ELSEIF (X .EQ. 0) THEN
    SIGN = 0
  ELSE
    SIGN = 1
  ENDIF
  RETURN
END
```

**CFG Coberta:**
- `function_def`
- `if_statement` (com ELSEIF aninhado)
- `assignment_statement` (múltiplas atribuições)
- `relational_expression` (X .LT. 0, X .EQ. 0)

---

## ✅ Checklist de Construções

Verifique se sua análise cobre:

- [ ] Programa principal (PROGRAM ... END)
- [ ] Declarações de tipo (INTEGER, REAL, etc.)
- [ ] Atribuições simples (var = expr)
- [ ] Atribuições em array (arr(i) = expr)
- [ ] Expressões aritméticas
- [ ] Expressões lógicas
- [ ] Operadores relacionais
- [ ] IF/THEN/ELSE/ELSEIF/ENDIF
- [ ] DO loops com LABEL/CONTINUE
- [ ] GOTO
- [ ] PRINT statements
- [ ] READ statements
- [ ] Chamadas de função
- [ ] Definições de função
- [ ] Subroutines
- [ ] Arrays e índices
- [ ] Constantes (.TRUE., .FALSE.)
- [ ] Operadores lógicos (.AND., .OR., .NOT.)
- [ ] Precedência de operadores
- [ ] Parênteses em expressões

---

## 📞 Referência Rápida de Tokens

```
Palavras-chave:
  PROGRAM, END, FUNCTION, SUBROUTINE
  INTEGER, REAL, LOGICAL, CHARACTER
  IF, THEN, ELSE, ELSEIF, ENDIF
  DO, CONTINUE, GOTO, RETURN
  READ, WRITE, PRINT

Operadores:
  .EQ. .NE. .LT. .LE. .GT. .GE.
  .AND. .OR. .NOT.
  .TRUE. .FALSE.
  **

Símbolos:
  + - * / ( ) , = :
```

---

## 🔗 Links para Documentação Completa

- **FORTRAN77_CFG.md** - Gramática completa em BNF
- **CFG_VALIDATION.md** - Validação com exemplos reais
- **src/fortran77_cfg.py** - Exemplos interativos (python script)
- **src/lexer.py** - Definição dos tokens
