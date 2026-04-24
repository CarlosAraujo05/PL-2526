# Context-Free Grammar for Fortran 77
## Using tokens from lexer.py in BNF notation

# ============================================================================
# PROGRAM STRUCTURE
# ============================================================================

program_unit -> program
              | program_unit function_definition
              | program_unit subroutine_definition

program -> PROGRAM ID declaration_block statement_block END

declaration_block -> declaration declaration_block
                   | ε

statement_block -> labeled_statement statement_block
                 | ε

# ============================================================================
# DECLARATIONS
# ============================================================================

declaration -> type_declaration
             | parameter_declaration

type_declaration -> base_type id_or_array_list

base_type -> INTEGER
           | REAL
           | LOGICAL
           | CHARACTER
           | CHARACTER '*' INTEGER_LIT

id_or_array_list -> id_or_array
                  | id_or_array_list ',' id_or_array

id_or_array -> ID
             | ID '(' INTEGER_LIT ')'

parameter_declaration -> PARAMETER '(' assignment_list ')'

assignment_list -> assignment
                 | assignment_list ',' assignment

assignment -> ID '=' literal 
# ============================================================================
# STATEMENTS
# ============================================================================

labeled_statement -> INTEGER_LIT statement
                   | statement

statement -> assignment_statement
           | if_statement
           | do_loop
           | goto_statement
           | call_statement
           | io_statement
           | control_statement
           | continue_statement

assignment_statement -> ID '=' expression
                      | array_access '=' expression

array_access -> ID '(' expression ')'


# ============================================================================
# EXPRESSIONS
# ============================================================================

expression -> logical_or_expression

logical_or_expression -> logical_and_expression
                       | logical_or_expression OR logical_and_expression

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

do_loop -> DO INTEGER_LIT ID '=' expression ',' expression statement_block INTEGER_LIT CONTINUE
         | DO INTEGER_LIT ID '=' expression ',' expression ',' expression statement_block INTEGER_LIT CONTINUE

goto_statement -> GOTO INTEGER_LIT

# ============================================================================
# I/O STATEMENTS
# ============================================================================

io_statement -> read_statement
              | write_statement
              | print_statement

read_statement -> READ '*' ',' read_list
                | READ '(' unit ',' format ')' read_list

write_statement -> WRITE '(' unit ',' format ')' read_list

print_statement -> PRINT '*' ',' output_list
                 | PRINT format ',' output_list

output_list -> expression
             | output_list ',' expression

read_list -> read_item
           | read_list ',' read_item

read_item -> ID
           | array_access

# Removed: open_statement, close_statement, inquire_statement, 
# backspace_statement, rewind_statement, endfile_statement (unsupported keywords)

# ============================================================================
# CONTROL STATEMENTS
# ============================================================================

control_statement -> RETURN

call_statement -> CALL ID '(' argument_list ')'
                | CALL ID '(' ')'

continue_statement -> CONTINUE

# Removed: pause_statement (unsupported keyword)

# Removed: STOP keyword support (not in lexer)

# ============================================================================
# SUBPROGRAM DEFINITIONS
# ============================================================================

subroutine_def -> SUBROUTINE ID '(' parameter_list ')' declaration_block statement_block END
                | SUBROUTINE ID '(' ')' declaration_block statement_block END

function_def -> base_type FUNCTION ID '(' parameter_list ')' declaration_block statement_block END
              | base_type FUNCTION ID '(' ')' declaration_block statement_block END

parameter_list -> ID
                | parameter_list ',' ID
