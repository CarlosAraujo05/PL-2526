# Context-Free Grammar for Fortran 77
## Using tokens from lexer.py in BNF notation

# ============================================================================
# PROGRAM STRUCTURE
# ============================================================================

program -> PROGRAM ID declaration_block statement_block END

declaration_block -> declaration declaration_block
                   | ε

statement_block -> labeled_statement statement_block
                 | ε

# ============================================================================
# DECLARATIONS
# ============================================================================

declaration -> type_declaration
             | dimension_declaration
             | common_declaration
             | equivalence_declaration
             | external_declaration
             | parameter_declaration
             | data_declaration
             | save_declaration
             | intrinsic_declaration
             | blockdata_declaration

type_declaration -> base_type id_list
                  | base_type DIMENSION '(' dimension_list ')' id_list

base_type -> INTEGER
           | REAL
           | DOUBLE REAL
           | COMPLEX
           | LOGICAL
           | CHARACTER
           | CHARACTER '*' INTEGER_LIT

dimension_list -> dimension_item
                | dimension_list ',' dimension_item

dimension_item -> INTEGER_LIT
                | INTEGER_LIT ':' INTEGER_LIT

id_list -> ID
         | id_list ',' ID

dimension_declaration -> DIMENSION ID '(' dimension_list ')'

common_declaration -> COMMON '/' ID '/' id_list
                    | COMMON '/' ID '/' id_list common_continuation

common_continuation -> ',' '/' ID '/' id_list
                    | common_continuation ',' '/' ID '/' id_list

equivalence_declaration -> EQUIVALENCE '(' ID ',' ID ')' equivalence_continuation

equivalence_continuation -> '(' ID ',' ID ')' equivalence_continuation
                          | ε

external_declaration -> EXTERNAL id_list

intrinsic_declaration -> INTRINSIC id_list

parameter_declaration -> PARAMETER '(' assignment_list ')'

assignment_list -> assignment
                 | assignment_list ',' assignment

assignment -> ID '=' literal

data_declaration -> DATA id_list '/' literal_list '/'

literal_list -> literal
              | literal_list ',' literal

save_declaration -> SAVE
                  | SAVE id_list

blockdata_declaration -> BLOCKDATA ID

# ============================================================================
# STATEMENTS
# ============================================================================

labeled_statement -> LABEL statement
                   | statement

statement -> assignment_statement
           | if_statement
           | do_loop
           | goto_statement
           | call_statement
           | io_statement
           | control_statement
           | continue_statement
           | pause_statement

assignment_statement -> ID '=' expression
                      | array_access '=' expression

array_access -> ID '(' index_list ')'

index_list -> expression
            | index_list ',' expression

# ============================================================================
# EXPRESSIONS
# ============================================================================

expression -> logical_or_expression

logical_or_expression -> logical_and_expression
                       | logical_or_expression OR logical_and_expression
                       | logical_or_expression XOR logical_and_expression

logical_and_expression -> logical_not_expression
                        | logical_and_expression AND logical_not_expression

logical_not_expression -> relational_expression
                        | NOT relational_expression

relational_expression -> additive_expression
                       | additive_expression relational_op additive_expression

relational_op -> EQ
               | NE
               | LT
               | LE
               | GT
               | GE

additive_expression -> multiplicative_expression
                     | additive_expression '+' multiplicative_expression
                     | additive_expression '-' multiplicative_expression

multiplicative_expression -> power_expression
                            | multiplicative_expression '*' power_expression
                            | multiplicative_expression '/' power_expression

power_expression -> unary_expression
                  | power_expression POW unary_expression

unary_expression -> primary_expression
                  | '-' unary_expression
                  | '+' unary_expression

primary_expression -> literal
                    | ID
                    | array_access
                    | '(' expression ')'
                    | function_call

function_call -> ID '(' argument_list ')'
               | ID '(' ')'

argument_list -> expression
               | argument_list ',' expression

literal -> INTEGER_LIT
         | REAL_LIT
         | STRING_LIT
         | TRUE
         | FALSE

# ============================================================================
# CONTROL FLOW STATEMENTS
# ============================================================================

if_statement -> IF '(' expression ')' THEN statement_block else_clause ENDIF

else_clause -> ELSE statement_block
             | ELSEIF '(' expression ')' THEN statement_block else_clause
             | ε

do_loop -> DO LABEL ID '=' expression ',' expression statement_block LABEL CONTINUE
         | DO LABEL ID '=' expression ',' expression ',' expression statement_block LABEL CONTINUE

goto_statement -> GOTO LABEL

# ============================================================================
# I/O STATEMENTS
# ============================================================================

io_statement -> read_statement
              | write_statement
              | print_statement
              | open_statement
              | close_statement
              | inquire_statement
              | backspace_statement
              | rewind_statement
              | endfile_statement

read_statement -> READ '*' ',' id_list
                | READ '(' unit ',' format ')' id_list

write_statement -> WRITE '(' unit ',' format ')' id_list

print_statement -> PRINT '*' ',' output_list
                 | PRINT format ',' output_list

output_list -> expression
             | output_list ',' expression

open_statement -> OPEN '(' open_spec_list ')'

open_spec_list -> open_spec
                | open_spec_list ',' open_spec

open_spec -> ID '=' expression

close_statement -> CLOSE '(' unit ')'

inquire_statement -> INQUIRE '(' unit ')'

backspace_statement -> BACKSPACE '(' unit ')'

rewind_statement -> REWIND '(' unit ')'

endfile_statement -> ENDFILE '(' unit ')'

unit -> INTEGER_LIT
      | '*'

format -> INTEGER_LIT
        | STRING_LIT
        | '*'

# ============================================================================
# CONTROL STATEMENTS
# ============================================================================

control_statement -> STOP
                   | RETURN

call_statement -> CALL ID '(' argument_list ')'
                | CALL ID '(' ')'

continue_statement -> CONTINUE

pause_statement -> PAUSE
                 | PAUSE INTEGER_LIT

# ============================================================================
# SUBPROGRAM DEFINITIONS
# ============================================================================

subroutine_def -> SUBROUTINE ID '(' parameter_list ')' declaration_block statement_block END
                | SUBROUTINE ID '(' ')' declaration_block statement_block END

function_def -> base_type FUNCTION ID '(' parameter_list ')' declaration_block statement_block RETURN END
              | base_type FUNCTION ID '(' ')' declaration_block statement_block RETURN END

parameter_list -> ID
                | parameter_list ',' ID
    

