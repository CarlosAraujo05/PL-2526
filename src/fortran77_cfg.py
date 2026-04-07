"""
Context-Free Grammar (CFG) para Fortran 77
Definição formal com anotações e exemplos

Este módulo documenta a CFG e fornece uma referência estruturada
dos passos de derivação para cada construção em Fortran 77.
"""

class FortranCFG:
    """
    Definição completa da Context-Free Grammar para Fortran 77
    baseada nos tokens do lexer.py
    """
    
    # ============================================================================
    # PRODUÇÕES DA GRAMÁTICA EM NOTAÇÃO BNF
    # ============================================================================
    
    GRAMMAR = """
    ============================================================================
    SÍMBOLO INICIAL: program
    ============================================================================
    
    1. PROGRAMA PRINCIPAL
    ─────────────────────
    program             → PROGRAM ID
                          declaration_block
                          statement_block
                          END
    
    declaration_block   → declaration declaration_block
                        | ε
    
    statement_block     → labeled_statement statement_block
                        | ε
    
    ─────────────────────────────────────────────────────────────────────────────
    
    2. DECLARAÇÕES DE TIPO
    ──────────────────────
    declaration         → type_declaration
                        | dimension_declaration
                        | common_declaration
                        | equivalence_declaration
                        | external_declaration
                        | parameter_declaration
                        | data_declaration
                        | save_declaration
                        | intrinsic_declaration
                        | blockdata_declaration
    
    type_declaration    → base_type id_list
                        | base_type DIMENSION dim_spec id_list
    
    base_type           → INTEGER
                        | REAL
                        | DOUBLE PRECISION
                        | COMPLEX
                        | LOGICAL
                        | CHARACTER
                        | CHARACTER * NUMBER
    
    dim_spec            → ( dimension_list )
    
    dimension_list      → dimension_item
                        | dimension_list , dimension_item
    
    dimension_item      → NUMBER
                        | NUMBER : NUMBER
    
    id_list             → ID
                        | id_list , ID
    
    dimension_declaration  → DIMENSION ID ( dimension_list )
    
    common_declaration  → COMMON / ID / id_list
                        | COMMON / ID / id_list common_continuation
    
    common_continuation → , / ID / id_list
                        | common_continuation , / ID / id_list
    
    equivalence_declaration → EQUIVALENCE ( ID , ID ) equivalence_continuation
    
    equivalence_continuation → ( ID , ID ) equivalence_continuation
                             | ε
    
    external_declaration   → EXTERNAL id_list
    
    intrinsic_declaration  → INTRINSIC id_list
    
    parameter_declaration  → PARAMETER ( assignment_list )
    
    assignment_list     → assignment
                        | assignment_list , assignment
    
    assignment          → ID = literal
    
    data_declaration    → DATA id_list / literal_list /
    
    literal_list        → literal
                        | literal_list , literal
    
    save_declaration    → SAVE
                        | SAVE id_list
    
    blockdata_declaration  → BLOCKDATA ID
    
    ─────────────────────────────────────────────────────────────────────────────
    
    3. STATEMENTS
    ─────────────
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
                        | pause_statement
    
    ─────────────────────────────────────────────────────────────────────────────
    
    4. ATRIBUIÇÃO
    ─────────────
    assignment_statement → ID = expression
                         | array_access = expression
    
    array_access        → ID ( index_list )
    
    index_list          → expression
                        | index_list , expression
    
    ─────────────────────────────────────────────────────────────────────────────
    
    5. EXPRESSÕES (Precedência Incorporada)
    ────────────────────────────────────────
    
    Precedência (alta → baixa):
    1. Parêntheses, funções, literais, IDs
    2. Unária: -, +
    3. Potência: **
    4. Multiplicação/Divisão: *, /
    5. Adição/Subtração: +, -
    6. Relacional: .LT., .LE., .GT., .GE., .EQ., .NE.
    7. Negação: .NOT.
    8. Conjunção: .AND.
    9. Disjunção: .OR., .EQV., .NEQV.
    
    expression          → logical_or_expression
    
    logical_or_expression  → logical_and_expression
                           | logical_or_expression .OR. logical_and_expression
                           | logical_or_expression .XOR. logical_and_expression
    
    logical_and_expression → logical_not_expression
                           | logical_and_expression .AND. logical_not_expression
    
    logical_not_expression → relational_expression
                           | .NOT. relational_expression
    
    relational_expression  → additive_expression
                           | additive_expression relational_op additive_expression
    
    relational_op       → .EQ. | .NE. | .LT. | .LE. | .GT. | .GE.
    
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
    
    function_call       → ID ( )
                        | ID ( argument_list )
    
    argument_list       → expression
                        | argument_list , expression
    
    literal             → NUMBER
                        | STRING
                        | .TRUE.
                        | .FALSE.
    
    ─────────────────────────────────────────────────────────────────────────────
    
    6. CONTROLE DE FLUXO
    ────────────────────
    
    if_statement        → IF ( expression ) THEN
                          statement_block
                          else_clause
                          ENDIF
    
    else_clause         → ELSE
                          statement_block
                        | ELSEIF ( expression ) THEN
                          statement_block
                          else_clause
                        | ε
    
    do_loop             → DO LABEL ID = expression , expression
                          statement_block
                          LABEL CONTINUE
    
    do_loop             → DO LABEL ID = expression , expression , expression
                          statement_block
                          LABEL CONTINUE
    
    goto_statement      → GOTO LABEL
    
    ─────────────────────────────────────────────────────────────────────────────
    
    7. ENTRADA/SAÍDA
    ────────────────
    io_statement        → read_statement
                        | write_statement
                        | print_statement
                        | open_statement
                        | close_statement
                        | inquire_statement
                        | backspace_statement
                        | rewind_statement
                        | endfile_statement
    
    read_statement      → READ * , id_list
                        | READ ( unit , format ) id_list
    
    write_statement     → WRITE ( unit , format ) id_list
    
    print_statement     → PRINT * , output_list
                        | PRINT format , output_list
    
    output_list         → expression
                        | output_list , expression
    
    open_statement      → OPEN ( open_spec_list )
    
    close_statement     → CLOSE ( unit )
    
    inquire_statement   → INQUIRE ( unit )
    
    backspace_statement → BACKSPACE ( unit )
    
    rewind_statement    → REWIND ( unit )
    
    endfile_statement   → ENDFILE ( unit )
    
    unit                → NUMBER | *
    
    format              → NUMBER | STRING | *
    
    ─────────────────────────────────────────────────────────────────────────────
    
    8. STATEMENTS DE CONTROLE
    ──────────────────────────
    control_statement   → STOP
                        | RETURN
    
    call_statement      → CALL ID ( )
                        | CALL ID ( argument_list )
    
    continue_statement  → CONTINUE
    
    pause_statement     → PAUSE
                        | PAUSE NUMBER
    
    ─────────────────────────────────────────────────────────────────────────────
    
    9. SUBPROGRAMAS
    ───────────────
    subroutine_def      → SUBROUTINE ID ( )
                          declaration_block
                          statement_block
                          END
    
    subroutine_def      → SUBROUTINE ID ( parameter_list )
                          declaration_block
                          statement_block
                          END
    
    function_def        → type_declaration FUNCTION ID ( )
                          declaration_block
                          statement_block
                          RETURN
                          END
    
    function_def        → type_declaration FUNCTION ID ( parameter_list )
                          declaration_block
                          statement_block
                          RETURN
                          END
    
    parameter_list      → ID
                        | parameter_list , ID
    
    ============================================================================
    """
    
    # ============================================================================
    # EXEMPLOS DE DERIVAÇÃO PASSO A PASSO
    # ============================================================================
    
    EXAMPLES = {
        "hello.for": {
            "code": """      PROGRAM HELLO
      PRINT *, 'Ola, Mundo!'
      END""",
            
            "derivation": """
Derivação: PROGRAMA COM PRINT
────────────────────────────

program
├─ PROGRAM ID
│  └─ 'HELLO'
├─ declaration_block
│  └─ ε (vazio - sem declarações)
├─ statement_block
│  └─ labeled_statement
│     └─ statement
│        └─ io_statement
│           └─ print_statement
│              └─ PRINT * , output_list
│                 └─ expression → logical_or_expression → ... → literal
│                    └─ STRING: 'Ola, Mundo!'
└─ END

Tokens Gerados:
PROGRAM ID(HELLO) PRINT '*' ',' STRING('Ola, Mundo!') END
            """
        },
        
        "fatorial.for": {
            "code": """      PROGRAM FATORIAL
      INTEGER N, I, FAT
      PRINT *, 'Introduza um numero inteiro positivo:'
      READ *, N
      FAT = 1
      DO 10 I = 1, N
          FAT = FAT * I
   10 CONTINUE
      PRINT *, 'Fatorial de ', N, ': ', FAT
      END""",
            
            "derivation": """
Derivação: PROGRAMA COM DO LOOP
────────────────────────────────

program
├─ PROGRAM ID('FATORIAL')
├─ declaration_block
│  └─ type_declaration: INTEGER id_list(N, I, FAT)
├─ statement_block
│  ├─ io_statement → PRINT * , output_list
│  ├─ io_statement → READ * , id_list(N)
│  ├─ assignment_statement: FAT = 1
│  │  └─ expression → literal → NUMBER(1)
│  ├─ do_loop
│  │  ├─ DO LABEL(10) ID(I) = expression(1) , expression(N)
│  │  ├─ statement_block
│  │  │  └─ assignment_statement: FAT = FAT * I
│  │  │     └─ multiplicative_expression
│  │  │        ├─ unary_expression → ID(FAT)
│  │  │        ├─ *
│  │  │        └─ unary_expression → ID(I)
│  │  └─ LABEL(10) CONTINUE
│  └─ io_statement → PRINT * , output_list
└─ END

Construções Importantes:
• DO LABEL ... LABEL CONTINUE (estrutura de loop com label)
• Declaração de múltiplas variáveis: INTEGER N, I, FAT
• Expressão aritmética com precedência: FAT * I
            """
        },
        
        "primo.for": {
            "code": """      PROGRAM PRIMO
      INTEGER NUM, I
      LOGICAL ISPRIM
      PRINT *, 'Introduza um numero inteiro positivo:'
      READ *, NUM
      ISPRIM = .TRUE.
      I = 2
   20 IF (I .LE. (NUM/2) .AND. ISPRIM) THEN
         IF (MOD(NUM, I) .EQ. 0) THEN
            ISPRIM = .FALSE.
         ENDIF
         I = I + 1
         GOTO 20
      ENDIF
      IF (ISPRIM) THEN
         PRINT *, NUM, ' e um numero primo'
      ELSE
         PRINT *, NUM, ' nao e um numero primo'
      ENDIF
      END""",
            
            "derivation": """
Derivação: PROGRAMA COM IF/ELSEIF/GOTO
─────────────────────────────────────

program
├─ PROGRAM ID('PRIMO')
├─ declaration_block
│  ├─ INTEGER N, I
│  └─ LOGICAL ISPRIM
├─ statement_block
│  ├─ assignments iniciais
│  ├─ labeled_statement
│  │  ├─ LABEL(20)
│  │  └─ if_statement
│  │     ├─ IF ( expression ) THEN
│  │     │  └─ logical_or_expression
│  │     │     ├─ logical_and_expression
│  │     │     │  ├─ relational_expression
│  │     │     │  │  ├─ I
│  │     │     │  │  ├─ .LE.
│  │     │     │  │  └─ (NUM/2)  [expressão aritmética]
│  │     │     │  ├─ .AND.
│  │     │     │  └─ logical_not_expression → ID(ISPRIM)
│  │     ├─ statement_block
│  │     │  ├─ nested if_statement
│  │     │  │  └─ assignment: ISPRIM = .FALSE.
│  │     │  ├─ assignment: I = I + 1
│  │     │  └─ goto_statement: GOTO 20
│  │     └─ ENDIF
│  └─ if_statement (segunda condição)
│     ├─ IF (ISPRIM) THEN
│     │  └─ output: NUM e ' numero primo'
│     ├─ ELSE
│     │  └─ output: NUM e ' nao numero primo'
│     └─ ENDIF
└─ END

Construções Importantes:
• Operadores lógicos: .AND., .LE.
• IF/THEN/ELSEIF/ENDIF aninhados
• GOTO para loops backwards (linha 20)
• Operadores relacionais: .LE., .EQ.
• Constantes lógicas: .TRUE., .FALSE.
• Expressões parentetizadas: (NUM/2)
            """
        },
        
        "somaarr.for": {
            "code": """      PROGRAM SOMAARR
      INTEGER NUMS(5)
      INTEGER I, SOMA
      SOMA = 0
      PRINT *, 'Introduza 5 numeros inteiros:'
      DO 30 I = 1, 5
         READ *, NUMS(I)
         SOMA = SOMA + NUMS(I)
   30 CONTINUE
      PRINT *, 'A soma dos numeros e: ', SOMA
      END""",
            
            "derivation": """
Derivação: PROGRAMA COM ARRAYS
───────────────────────────────

program
├─ PROGRAM ID('SOMAARR')
├─ declaration_block
│  ├─ type_declaration: INTEGER DIMENSION(5) NUMS
│  │  └─ dim_spec: ( dimension_list )
│  │     └─ NUMBER(5)
│  └─ type_declaration: INTEGER I, SOMA
├─ statement_block
│  ├─ assignment: SOMA = 0
│  ├─ do_loop
│  │  ├─ DO LABEL(30) ID(I) = 1 , 5
│  │  ├─ statement_block
│  │  │  ├─ io_statement: READ * , array_access
│  │  │  │  └─ NUMS(I)
│  │  │  │     ├─ ID(NUMS)
│  │  │  │     └─ ( index_list )
│  │  │  │        └─ expression → ID(I)
│  │  │  └─ assignment: SOMA = SOMA + NUMS(I)
│  │  │     └─ additive_expression
│  │  │        ├─ ID(SOMA)
│  │  │        ├─ +
│  │  │        └─ array_access(NUMS(I))
│  │  └─ LABEL(30) CONTINUE
│  └─ io_statement: PRINT
└─ END

Construções Importantes:
• Declaração com DIMENSION: INTEGER NUMS(5)
• Acesso a arrays: NUMS(I) (índices como expressões)
• Arrays em I/O: READ *, NUMS(I)
• Loops com índice de array
            """
        },
        
        "conversor.for": {
            "code": """      PROGRAM CONVERSOR
      INTEGER NUM, BASE, RESULT, CONVRT
      
      PRINT *, 'INTRODUZA UM NUMERO DECIMAL INTEIRO:'
      READ *, NUM
      
      DO 10 BASE = 2, 9
         RESULT = CONVRT(NUM, BASE)
         PRINT *, 'BASE ', BASE, ': ', RESULT
   10 CONTINUE
      
      END
      
      INTEGER FUNCTION CONVRT(N, B)
      INTEGER N, B, QUOT, REM, POT, VAL
      VAL = 0
      POT = 1
      QUOT = N
   20 IF (QUOT .GT. 0) THEN
         REM = MOD(QUOT, B)
         VAL = VAL + (REM * POT)
         QUOT = QUOT / B
         POT = POT * 10
         GOTO 20
      ENDIF
      CONVRT = VAL
      RETURN
      END""",
            
            "derivation": """
Derivação: PROGRAMA COM FUNCTION
─────────────────────────────────

program
├─ PROGRAM ID('CONVERSOR')
├─ declaration_block
│  └─ INTEGER NUM, BASE, RESULT, CONVRT
├─ statement_block
│  ├─ io_statement
│  ├─ do_loop
│  │  ├─ DO LABEL(10) ID(BASE) = 2 , 9
│  │  ├─ statement_block
│  │  │  ├─ assignment_statement
│  │  │  │  └─ RESULT = function_call
│  │  │  │     └─ CONVRT ( argument_list )
│  │  │  │        ├─ NUM
│  │  │  │        ├─ ,
│  │  │  │        └─ BASE
│  │  │  └─ io_statement → PRINT
│  │  └─ LABEL(10) CONTINUE
│  └─ END
│
├─ (Fim do programa principal)
│
└─ function_def (SUBPROGRAMA)
   ├─ INTEGER FUNCTION CONVRT ( N , B )
   ├─ declaration_block
   │  └─ INTEGER N, B, QUOT, REM, POT, VAL
   ├─ statement_block
   │  ├─ assignment: VAL = 0
   │  ├─ assignment: POT = 1
   │  ├─ assignment: QUOT = N
   │  ├─ labeled_statement
   │  │  ├─ LABEL(20)
   │  │  └─ if_statement
   │  │     ├─ IF (QUOT .GT. 0) THEN
   │  │     ├─ statement_block
   │  │     │  ├─ assignment: REM = MOD(QUOT, B)
   │  │     │  ├─ assignment: VAL = VAL + (REM * POT)
   │  │     │  ├─ assignment: QUOT = QUOT / B
   │  │     │  ├─ assignment: POT = POT * 10
   │  │     │  └─ goto_statement: GOTO 20
   │  │     └─ ENDIF
   │  ├─ assignment: CONVRT = VAL
   │  └─ control_statement: RETURN
   └─ END

Construções Importantes:
• INTEGER FUNCTION declaração do tipo de retorno
• Chamada de função: CONVRT(NUM, BASE)
• Atribuição ao nome da função: CONVRT = VAL
• RETURN statement
• Chamada a função intrínseca: MOD(QUOT, B)
• Subprograma separado com declarações de parâmetros
            """
        }
    }


def print_grammar():
    """Imprime a gramática completa"""
    print(FortranCFG.GRAMMAR)


def print_example(filename):
    """Imprime um exemplo específico com derivação"""
    if filename in FortranCFG.EXAMPLES:
        ex = FortranCFG.EXAMPLES[filename]
        print(f"\n{'='*80}")
        print(f"ARQUIVO: {filename}")
        print(f"{'='*80}\n")
        print("CÓDIGO FORTRAN 77:")
        print("─" * 80)
        print(ex["code"])
        print("─" * 80)
        print("\nDERIVAÇÃO SEGUNDO A CFG:")
        print(ex["derivation"])
    else:
        print(f"Exemplo '{filename}' não encontrado.")
        print(f"Exemplos disponíveis: {list(FortranCFG.EXAMPLES.keys())}")


def print_all_examples():
    """Imprime todos os exemplos"""
    for filename in FortranCFG.EXAMPLES.keys():
        print_example(filename)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--grammar":
            print_grammar()
        elif sys.argv[1] == "--all":
            print_all_examples()
        else:
            print_example(sys.argv[1])
    else:
        print("Context-Free Grammar para Fortran 77")
        print("="*80)
        print("\nUso:")
        print(f"  python {sys.argv[0]} --grammar         # Mostra a gramática completa")
        print(f"  python {sys.argv[0]} --all             # Mostra todos os exemplos")
        print(f"  python {sys.argv[0]} <arquivo.for>     # Mostra derivação do arquivo\n")
        print("Exemplos disponíveis:")
        for filename in FortranCFG.EXAMPLES.keys():
            print(f"  - {filename}")
        
        # Mostrar um exemplo por padrão
        print("\n" + "="*80)
        print("EXEMPLO PADRÃO:")
        print_example("hello.for")
