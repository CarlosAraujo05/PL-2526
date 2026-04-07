# PL-2526 - Context-Free Grammar (CFG) para Fortran 77

## 📋 Visão Geral

Este projeto apresenta uma **Context-Free Grammar (CFG) completa** para **Fortran 77**, baseada nos tokens definidos no `lexer.py`. A gramática foi desenvolvida com exemplos práticos usando os testes disponíveis.

### Arquivos Principais

1. **`FORTRAN77_CFG.md`** - Documentação completa da gramática em Markdown
   - Definição formal em notação BNF
   - Hierarquia de precedência de operadores
   - 5 exemplos de análise completos com derivações

2. **`src/fortran77_cfg.py`** - Implementação Python da gramática
   - Definição estruturada das produções
   - Exemplos com derivações passo-a-passo
   - Interface CLI para visualizar exemplos

3. **`src/lexer.py`** - Analisador léxico (PLY)
   - Tokens base para a gramática
   - Reconhecimento de palavras-chave, operadores, literais

4. **Testes** - Programas Fortran 77 de validação
   - `tests/hello.for` - Programa simples
   - `tests/fatorial.for` - Loops (DO/CONTINUE)
   - `tests/primo.for` - Controle de fluxo (IF/THEN/GOTO)
   - `tests/somaarr.for` - Arrays
   - `tests/conversor.for` - Funções e subprogramas

---

## 🎯 Estrutura da Gramática

### Símbolo Inicial
```
program → PROGRAM ID declaration_block statement_block END
```

### Principais Categorias de Produções

| Categoria | Exemplo | Produção |
|-----------|---------|----------|
| **Programa** | `PROGRAM HELLO ... END` | `program → PROGRAM ID ... END` |
| **Declarações** | `INTEGER N, I, FAT` | `type_declaration → base_type id_list` |
| **Atribuição** | `FAT = FAT * I` | `assignment_statement → ID = expression` |
| **Arrays** | `NUMS(5)`, `NUMS(I)` | `array_access → ID ( index_list )` |
| **Expressões** | `I .LE. (NUM/2) .AND. ISPRIM` | Precedência incorporada na gramática |
| **Loops** | `DO 10 I = 1, N ... CONTINUE` | `do_loop → DO LABEL ID = ... LABEL CONTINUE` |
| **Condicionais** | `IF ... THEN ... ENDIF` | `if_statement → IF ( expr ) THEN ... ENDIF` |
| **I/O** | `PRINT *, 'texto'` | `print_statement → PRINT * , output_list` |
| **Funções** | `FUNCTION CONVRT(N,B) ... RETURN END` | `function_def → type ... FUNCTION ... RETURN END` |

### Hierarquia de Precedência de Operadores

(De **maior** para **menor** precedência)

1. **Parênteses, Funções, Literais, IDs**
2. **Unária:** `-`, `+`
3. **Potência:** `**`
4. **Multiplicação/Divisão:** `*`, `/`
5. **Adição/Subtração:** `+`, `-`
6. **Relacional:** `.LT.`, `.LE.`, `.GT.`, `.GE.`, `.EQ.`, `.NE.`
7. **Negação Lógica:** `.NOT.`
8. **Conjunção Lógica:** `.AND.`
9. **Disjunção Lógica:** `.OR.`, `.XOR.`

---

## 📚 Exemplos de Uso

### Visualizar a Gramática Completa

```bash
python src/fortran77_cfg.py --grammar
```

### Ver Todos os Exemplos com Derivações

```bash
python src/fortran77_cfg.py --all
```

### Ver um Exemplo Específico

```bash
python src/fortran77_cfg.py hello.for
python src/fortran77_cfg.py fatorial.for
python src/fortran77_cfg.py primo.for
python src/fortran77_cfg.py somaarr.for
python src/fortran77_cfg.py conversor.for
```

---

## 🔍 Exemplo de Análise: hello.for

### Código Fonte
```fortran
      PROGRAM HELLO
      PRINT *, 'Ola, Mundo!'
      END
```

### Derivação pela Gramática
```
program
├─ PROGRAM ID('HELLO')
├─ declaration_block → ε (sem declarações)
├─ statement_block
│  └─ io_statement
│     └─ print_statement
│        └─ PRINT * , output_list
│           └─ expression → literal
│              └─ STRING('Ola, Mundo!')
└─ END
```

### Tokens Gerados pelo Lexer
```
PROGRAM ID(HELLO) PRINT '*' ',' STRING(Ola, Mundo!) END
```

---

## 🔀 Exemplo de Análise: primo.for (Complexo)

### Trecho com Operadores Lógicos
```fortran
   20 IF (I .LE. (NUM/2) .AND. ISPRIM) THEN
      IF (MOD(NUM, I) .EQ. 0) THEN
         ISPRIM = .FALSE.
      ENDIF
      I = I + 1
      GOTO 20
   ENDIF
```

### Derivação da Expressão Booleana
```
IF ( expression ) THEN
  └─ logical_or_expression
     └─ logical_and_expression
        ├─ relational_expression
        │  ├─ I
        │  ├─ .LE.
        │  └─ additive_expression
        │     └─ (NUM / 2)  [precedência: divisão antes]
        ├─ .AND.
        └─ logical_not_expression
           └─ ID(ISPRIM)
```

### Construções Demonstradas
- ✅ Operadores lógicos (`.AND.`, `.LE.`)
- ✅ Expressões parentetizadas (`.LE. (NUM/2)`)
- ✅ IF/THEN/ELSEIF/ENDIF aninhados
- ✅ GOTO para loops backwards
- ✅ Constantes lógicas (`.TRUE.`, `.FALSE.`)

---

## 📊 Exemplo de Análise: somaarr.for (Arrays)

### Código
```fortran
      INTEGER NUMS(5)
      DO 30 I = 1, 5
         READ *, NUMS(I)
         SOMA = SOMA + NUMS(I)
   30 CONTINUE
```

### Derivação
```
declaration
└─ type_declaration
   ├─ INTEGER
   ├─ DIMENSION (5)
   └─ ID(NUMS)

do_loop
├─ DO LABEL(30) ID(I) = 1 , 5
├─ array_access: NUMS(I)
│  ├─ ID(NUMS)
│  └─ ( index_list )
│     └─ expression → ID(I)
└─ LABEL(30) CONTINUE
```

### Construções Demonstradas
- ✅ Declaração com dimensão: `INTEGER NUMS(5)`
- ✅ Acesso a arrays: `NUMS(I)` (índices como expressões)
- ✅ Arrays em I/O: `READ *, NUMS(I)`
- ✅ Loops com contadores de array

---

## 🎓 Exemplo de Análise: conversor.for (Funções)

### Código (Subprograma)
```fortran
      INTEGER FUNCTION CONVRT(N, B)
      INTEGER N, B, QUOT, REM, POT, VAL
      VAL = 0
      POT = 1
      CONVRT = VAL
      RETURN
      END
```

### Derivação
```
function_def
├─ type_declaration: INTEGER FUNCTION CONVRT(N, B)
├─ parameter_list: N, B
├─ declaration_block: INTEGER N, B, QUOT, REM, POT, VAL
├─ statement_block
│  ├─ assignments
│  └─ assignment: CONVRT = VAL
├─ control_statement: RETURN
└─ END
```

### Construções Demonstradas
- ✅ Declaração de função: `INTEGER FUNCTION`
- ✅ Parâmetros formais: `(N, B)`
- ✅ Atribuição ao nome da função
- ✅ RETURN statement
- ✅ Chamada de função: `CONVRT(NUM, BASE)`

---

## 📖 Notação Utilizada

A gramática usa **BNF (Backus-Naur Form)** com as seguintes convenções:

```
→       : Produção (regra)
|       : Alternativa (ou)
ε       : Epsilon (derivação vazia)
[...]   : Comentário explicativo
(...)   : Agrupamento
...     : Repetição
```

### Exemplo de Leitura

```
expression → logical_or_expression
           | logical_or_expression .OR. logical_and_expression

Lê-se: "Uma expressão é ou uma disjunção lógica,
        ou uma disjunção lógica seguida de .OR. e uma conjunção lógica"
```

---

## ✅ Validação com Testes

Cada arquivo de teste valida diferentes aspectos da gramática:

| Arquivo | Aspecto | Construções |
|---------|---------|-------------|
| `hello.for` | Programa simples | PROGRAM, PRINT, END |
| `fatorial.for` | DO loops | INTEGER, DO...CONTINUE, expressões aritméticas |
| `primo.for` | Controle de fluxo | IF/THEN/ELSEIF/ENDIF, GOTO, operadores lógicos |
| `somaarr.for` | Arrays | DIMENSION, array access, READ |
| `conversor.for` | Funções | FUNCTION, RETURN, chamadas de função |

---

## 🛠️ Tokens Suportados (do lexer.py)

### Palavras-chave
```
PROGRAM, END, SUBROUTINE, FUNCTION, CALL, RETURN
INTEGER, REAL, DOUBLE, COMPLEX, LOGICAL, CHARACTER
DIMENSION, PARAMETER, DATA, COMMON, EQUIVALENCE, EXTERNAL, INTRINSIC
IF, THEN, ELSE, ELSEIF, ENDIF, GOTO, ASSIGN, TO
DO, CONTINUE, STOP, PAUSE
READ, WRITE, PRINT, OPEN, CLOSE, INQUIRE, BACKSPACE, REWIND, ENDFILE
FORMAT, SAVE, BLOCKDATA
```

### Operadores
```
.GT., .LT., .GE., .LE., .EQ., .NE.
.AND., .OR., .NOT., .XOR., .EQV., .NEQV.
.TRUE., .FALSE.
** (potência)
```

### Símbolos Especiais
```
+ - * / ( ) , = : 
(além de NUMBER, STRING, ID, LABEL)
```

---

## 📝 Características Principais da Gramática

✅ **Completa** - Cobre todas as construções Fortran 77 básicas
✅ **Não Ambígua** - Precedência e associatividade bem definidas
✅ **Validada** - Testada com 5 programas Fortran 77 reais
✅ **Documentada** - Exemplos práticos com derivações passo-a-passo
✅ **LL(1) Compatível** - Adequada para análise por descida recursiva

---

## 🔗 Referências

- **Fortran 77 Standard** - ISO/IEC 1539:1980
- **PLY (Python Lex-Yacc)** - https://www.dabeaz.com/ply/
- **BNF Notation** - https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form

---

## 📄 Licença

Este projeto é fornecido como material educacional.