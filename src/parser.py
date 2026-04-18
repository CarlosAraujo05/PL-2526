"""
Parser for Fortran 77 using PLY (Python Lex-Yacc).

Builds an abstract syntax tree (AST) from a token stream.
"""

import ply.yacc as yacc
import sys
from lexer import tokens, build_lexer
from ast_nodes import *


# ============================================================================
# PROGRAM STRUCTURE
# ============================================================================

def p_program_unit(p):
    """program_unit : program
                    | program_unit function_definition
                    | program_unit subroutine_definition"""
    if isinstance(p[1], Program):
        # First rule: just the program
        p[0] = CompilationUnit(main_program=p[1], subprograms=[])
    else:
        # Second/third rule: compilation unit + subprogram
        unit = p[1]
        subprog = p[2]
        unit.subprograms.append(subprog)
        p[0] = unit


def p_program(p):
    """program : PROGRAM ID declaration_block statement_block END"""
    p[0] = Program(
        name=p[2],
        declarations=p[3] if p[3] else [],
        statements=p[4] if p[4] else [],
        lineno=p.lineno(1)
    )


def p_declaration_block(p):
    """declaration_block : declaration_block declaration
                         | empty"""
    if p[1] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_statement_block(p):
    """statement_block : statement_block labeled_statement
                       | empty"""
    if p[1] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# ============================================================================
# DECLARATIONS
# ============================================================================

def p_declaration(p):
    """declaration : type_declaration
                   | dimension_declaration
                   | common_declaration
                   | equivalence_declaration
                   | external_declaration
                   | parameter_declaration
                   | data_declaration
                   | save_declaration
                   | intrinsic_declaration
                   | blockdata_declaration"""
    p[0] = p[1]


def p_type_declaration(p):
    """type_declaration : base_type id_or_array_list
                        | base_type DIMENSION '(' dimension_list ')' id_list"""
    if len(p) == 3:
        # Simple or array type declaration with id_or_array_list
        p[0] = TypeDeclaration(dtype=p[1], ids=p[2], lineno=p.lineno(1))
    else:
        # Type with DIMENSION keyword declaration
        # For now, treat as separate declarations
        p[0] = TypeDeclaration(dtype=p[1], ids=p[6], lineno=p.lineno(1))


def p_id_or_array_list(p):
    """id_or_array_list : id_or_array
                        | id_or_array_list ',' id_or_array"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_id_or_array(p):
    """id_or_array : ID
                   | ID '(' dimension_list ')'"""
    if len(p) == 2:
        # Simple ID, not an array
        p[0] = {'name': p[1], 'dimensions': None}
    else:
        # Array declaration
        p[0] = {'name': p[1], 'dimensions': p[3]}


def p_base_type(p):
    """base_type : INTEGER
                  | REAL
                  | DOUBLE REAL
                  | COMPLEX
                  | LOGICAL
                  | CHARACTER
                  | CHARACTER '*' INTEGER_LIT"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = 'DOUBLE REAL'
    else:
        p[0] = f'CHARACTER*{p[3]}'


def p_dimension_list(p):
    """dimension_list : dimension_item
                      | dimension_list ',' dimension_item"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_dimension_item(p):
    """dimension_item : INTEGER_LIT
                      | INTEGER_LIT ':' INTEGER_LIT"""
    if len(p) == 2:
        p[0] = (1, p[1])
    else:
        p[0] = (p[1], p[3])


def p_id_list(p):
    """id_list : ID
               | id_list ',' ID"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_dimension_declaration(p):
    """dimension_declaration : DIMENSION ID '(' dimension_list ')'"""
    p[0] = DimensionDeclaration(var=p[2], dimensions=p[4], lineno=p.lineno(1))


def p_common_declaration(p):
    """common_declaration : COMMON '/' ID '/' id_list
                          | COMMON '/' ID '/' id_list common_continuation"""
    block_name = p[3]
    ids = p[5]
    # TODO: Handle common_continuation for multiple blocks
    p[0] = CommonDeclaration(block_name=block_name, ids=ids, lineno=p.lineno(1))


def p_common_continuation(p):
    """common_continuation : ',' '/' ID '/' id_list
                            | common_continuation ',' '/' ID '/' id_list"""
    # Placeholder for continuation
    p[0] = None


def p_equivalence_declaration(p):
    """equivalence_declaration : EQUIVALENCE '(' ID ',' ID ')' equivalence_continuation"""
    groups = [(p[3], p[5])]
    # TODO: Merge with equivalence_continuation
    p[0] = EquivalenceDeclaration(groups=groups, lineno=p.lineno(1))


def p_equivalence_continuation(p):
    """equivalence_continuation : '(' ID ',' ID ')' equivalence_continuation
                                | empty"""
    p[0] = None


def p_external_declaration(p):
    """external_declaration : EXTERNAL id_list"""
    p[0] = ExternalDeclaration(ids=p[2], lineno=p.lineno(1))


def p_intrinsic_declaration(p):
    """intrinsic_declaration : INTRINSIC id_list"""
    p[0] = IntrinsicDeclaration(ids=p[2], lineno=p.lineno(1))


def p_parameter_declaration(p):
    """parameter_declaration : PARAMETER '(' assignment_list ')'"""
    p[0] = ParameterDeclaration(assignments=p[3], lineno=p.lineno(1))


def p_assignment_list(p):
    """assignment_list : assignment
                       | assignment_list ',' assignment"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_assignment(p):
    """assignment : ID '=' literal"""
    p[0] = AssignmentStatement(
        target=Variable(name=p[1], lineno=p.lineno(1)),
        value=p[3],
        lineno=p.lineno(1)
    )


def p_data_declaration(p):
    """data_declaration : DATA id_list '/' literal_list '/'"""
    p[0] = DataDeclaration(ids=p[2], values=p[4], lineno=p.lineno(1))


def p_literal_list(p):
    """literal_list : literal
                    | literal_list ',' literal"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_save_declaration(p):
    """save_declaration : SAVE
                        | SAVE id_list"""
    if len(p) == 2:
        p[0] = SaveDeclaration(lineno=p.lineno(1))
    else:
        p[0] = SaveDeclaration(ids=p[2], lineno=p.lineno(1))


def p_blockdata_declaration(p):
    """blockdata_declaration : BLOCKDATA ID"""
    p[0] = BlockDataDeclaration(name=p[2], lineno=p.lineno(1))


# ============================================================================
# STATEMENTS
# ============================================================================

def p_labeled_statement(p):
    """labeled_statement : INTEGER_LIT statement
                         | statement"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        # INTEGER_LIT before a statement acts as a label
        p[2].label = int(p[1])
        p[0] = p[2]


def p_statement(p):
    """statement : assignment_statement
                 | if_statement
                 | do_loop
                 | goto_statement
                 | call_statement
                 | io_statement
                 | control_statement
                 | continue_statement
                 | pause_statement"""
    p[0] = p[1]


def p_assignment_statement(p):
    """assignment_statement : ID '=' expression
                            | array_access '=' expression"""
    # If p[1] is a string (ID), convert to Variable node
    if isinstance(p[1], str):
        target = Variable(name=p[1], lineno=p.lineno(1))
    else:
        # ArrayAccess node
        target = p[1]
    p[0] = AssignmentStatement(target=target, value=p[3], lineno=p.lineno(1))


def p_array_access(p):
    """array_access : ID '(' index_list ')'"""
    p[0] = ArrayAccess(name=p[1], indices=p[3], lineno=p.lineno(1))


def p_index_list(p):
    """index_list : expression
                  | index_list ',' expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


# ============================================================================
# EXPRESSIONS (operator precedence)
# ============================================================================

def p_expression(p):
    """expression : logical_or_expression"""
    p[0] = p[1]


def p_logical_or_expression(p):
    """logical_or_expression : logical_and_expression
                             | logical_or_expression OR logical_and_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='.OR.', left=p[1], right=p[3], lineno=p.lineno(1))


def p_logical_or_expression_xor(p):
    """logical_or_expression : logical_or_expression XOR logical_and_expression"""
    p[0] = BinaryOp(op='.XOR.', left=p[1], right=p[3], lineno=p.lineno(1))


def p_logical_and_expression(p):
    """logical_and_expression : logical_not_expression
                              | logical_and_expression AND logical_not_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='.AND.', left=p[1], right=p[3], lineno=p.lineno(1))


def p_logical_not_expression(p):
    """logical_not_expression : relational_expression
                              | NOT relational_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op='.NOT.', operand=p[2], lineno=p.lineno(1))


def p_relational_expression(p):
    """relational_expression : additive_expression
                             | additive_expression relational_op additive_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_relational_op(p):
    """relational_op : EQ
                     | NE
                     | LT
                     | LE
                     | GT
                     | GE"""
    p[0] = p[1]


def p_additive_expression(p):
    """additive_expression : multiplicative_expression
                           | additive_expression '+' multiplicative_expression
                           | additive_expression '-' multiplicative_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_multiplicative_expression(p):
    """multiplicative_expression : power_expression
                                 | multiplicative_expression '*' power_expression
                                 | multiplicative_expression '/' power_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_power_expression(p):
    """power_expression : unary_expression
                        | power_expression POW unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='**', left=p[1], right=p[3], lineno=p.lineno(1))


def p_unary_expression(p):
    """unary_expression : primary_expression
                        | '-' unary_expression
                        | '+' unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op=p[1], operand=p[2], lineno=p.lineno(1))


def p_primary_expression(p):
    """primary_expression : literal
                          | ID
                          | array_access
                          | '(' expression ')'
                          | function_call"""
    if isinstance(p[1], str) and len(p) == 2:
        # Just an ID
        p[0] = Variable(name=p[1], lineno=p.lineno(1))
    elif len(p) == 4:
        # Parenthesized expression
        p[0] = ParenthesizedExpression(expr=p[2], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_function_call(p):
    """function_call : ID '(' argument_list ')'
                     | ID '(' ')'"""
    if len(p) == 4:
        p[0] = FunctionCall(name=p[1], lineno=p.lineno(1))
    else:
        p[0] = FunctionCall(name=p[1], arguments=p[3], lineno=p.lineno(1))


def p_argument_list(p):
    """argument_list : expression
                     | argument_list ',' expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_literal(p):
    """literal : INTEGER_LIT
               | REAL_LIT
               | STRING_LIT
               | TRUE
               | FALSE"""
    if isinstance(p[1], (int, float)):
        kind = 'INTEGER' if isinstance(p[1], int) else 'REAL'
        value = p[1]
    elif p[1] in ('.TRUE.', 'TRUE'):
        kind = 'LOGICAL'
        value = True
    elif p[1] in ('.FALSE.', 'FALSE'):
        kind = 'LOGICAL'
        value = False
    else:
        kind = 'STRING'
        value = p[1]
    p[0] = Literal(value=value, kind=kind, lineno=p.lineno(1))


# ============================================================================
# CONTROL FLOW STATEMENTS
# ============================================================================

def p_if_statement(p):
    """if_statement : IF '(' expression ')' THEN statement_block else_clause ENDIF"""
    then_body = p[6] if p[6] else []
    else_body = p[7][0] if p[7] and p[7][0] else None
    elseif_parts = p[7][1] if p[7] and len(p[7]) > 1 else []
    
    p[0] = IfThenElse(
        condition=p[3],
        then_body=then_body,
        else_body=else_body,
        elseif_parts=elseif_parts,
        lineno=p.lineno(1)
    )


def p_else_clause(p):
    """else_clause : ELSE statement_block
                   | ELSEIF '(' expression ')' THEN statement_block else_clause
                   | empty"""
    if p[1] is None:
        p[0] = (None, [])
    elif p[1] == 'ELSE':
        p[0] = (p[2], [])
    else:  # ELSEIF
        nested = p[7]
        elseif_cond = p[3]
        elseif_body = p[6] if p[6] else []
        p[0] = (nested[0], [(elseif_cond, elseif_body)] + nested[1])


def p_do_loop(p):
    """do_loop : DO INTEGER_LIT ID '=' expression ',' expression statement_block INTEGER_LIT CONTINUE
               | DO INTEGER_LIT ID '=' expression ',' expression ',' expression statement_block INTEGER_LIT CONTINUE"""
    start = p[5]
    stop = p[7]
    if len(p) == 11:
        step = None
        body = p[8]
        label_start = int(p[2])
        label_end = int(p[9])
    else:
        step = p[9]
        body = p[10]
        label_start = int(p[2])
        label_end = int(p[11])
    
    # Validate that labels match
    if label_start != label_end:
        raise ParserError(f"DO loop labels do not match: {label_start} != {label_end}")
    
    p[0] = DoLoop(
        var=p[3],
        start=start,
        stop=stop,
        step=step,
        body=body,
        label=label_start,
        lineno=p.lineno(1)
    )


def p_goto_statement(p):
    """goto_statement : GOTO INTEGER_LIT"""
    p[0] = GotoStatement(target_label=int(p[2]), lineno=p.lineno(1))


# ============================================================================
# I/O STATEMENTS
# ============================================================================

def p_io_statement(p):
    """io_statement : read_statement
                    | write_statement
                    | print_statement
                    | open_statement
                    | close_statement
                    | inquire_statement
                    | backspace_statement
                    | rewind_statement
                    | endfile_statement"""
    p[0] = p[1]


def p_read_statement(p):
    """read_statement : READ '*' ',' read_list
                      | READ '(' unit ',' format ')' read_list"""
    if len(p) == 5:
        p[0] = ReadStatement(unit=None, format_spec=None, variables=p[4], lineno=p.lineno(1))
    else:
        p[0] = ReadStatement(unit=p[3], format_spec=p[5], variables=p[7], lineno=p.lineno(1))


def p_read_list(p):
    """read_list : read_item
                 | read_list ',' read_item"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_read_item(p):
    """read_item : ID
                 | array_access"""
    if isinstance(p[1], str):
        p[0] = p[1]  # Simple ID
    else:
        p[0] = p[1]  # ArrayAccess node


def p_write_statement(p):
    """write_statement : WRITE '(' unit ',' format ')' read_list"""
    p[0] = WriteStatement(unit=p[3], format_spec=p[5], lineno=p.lineno(1))


def p_print_statement(p):
    """print_statement : PRINT '*' ',' output_list
                       | PRINT format ',' output_list"""
    p[0] = PrintStatement(format_spec=p[2], expressions=p[4], lineno=p.lineno(1))


def p_output_list(p):
    """output_list : expression
                   | output_list ',' expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_open_statement(p):
    """open_statement : OPEN '(' open_spec_list ')'"""
    p[0] = OpenStatement(specs=p[3], lineno=p.lineno(1))


def p_open_spec_list(p):
    """open_spec_list : open_spec
                      | open_spec_list ',' open_spec"""
    if len(p) == 2:
        p[0] = {p[1][0]: p[1][1]}
    else:
        p[1][p[3][0]] = p[3][1]
        p[0] = p[1]


def p_open_spec(p):
    """open_spec : ID '=' expression"""
    p[0] = (p[1], p[3])


def p_close_statement(p):
    """close_statement : CLOSE '(' unit ')'"""
    p[0] = CloseStatement(unit=p[3], lineno=p.lineno(1))


def p_inquire_statement(p):
    """inquire_statement : INQUIRE '(' unit ')'"""
    p[0] = InquireStatement(unit=p[3], lineno=p.lineno(1))


def p_backspace_statement(p):
    """backspace_statement : BACKSPACE '(' unit ')'"""
    p[0] = BackspaceStatement(unit=p[3], lineno=p.lineno(1))


def p_rewind_statement(p):
    """rewind_statement : REWIND '(' unit ')'"""
    p[0] = RewindStatement(unit=p[3], lineno=p.lineno(1))


def p_endfile_statement(p):
    """endfile_statement : ENDFILE '(' unit ')'"""
    p[0] = EndfileStatement(unit=p[3], lineno=p.lineno(1))


def p_unit(p):
    """unit : INTEGER_LIT
            | '*'"""
    p[0] = Literal(value=p[1], kind='INTEGER', lineno=p.lineno(1))


def p_format(p):
    """format : INTEGER_LIT
              | STRING_LIT
              | '*'"""
    if isinstance(p[1], int):
        p[0] = Literal(value=p[1], kind='INTEGER', lineno=p.lineno(1))
    elif isinstance(p[1], str):
        if p[1] == '*':
            p[0] = '*'
        else:
            p[0] = Literal(value=p[1], kind='STRING', lineno=p.lineno(1))


# ============================================================================
# CONTROL STATEMENTS
# ============================================================================

def p_control_statement(p):
    """control_statement : STOP
                         | RETURN"""
    if p[1] == 'STOP':
        p[0] = StopStatement(lineno=p.lineno(1))
    else:
        p[0] = ReturnStatement(lineno=p.lineno(1))


def p_call_statement(p):
    """call_statement : CALL ID '(' argument_list ')'
                      | CALL ID '(' ')'"""
    if len(p) == 5:
        p[0] = CallStatement(name=p[2], lineno=p.lineno(1))
    else:
        p[0] = CallStatement(name=p[2], arguments=p[4], lineno=p.lineno(1))


def p_continue_statement(p):
    """continue_statement : CONTINUE"""
    p[0] = ContinueStatement(lineno=p.lineno(1))


def p_pause_statement(p):
    """pause_statement : PAUSE
                       | PAUSE INTEGER_LIT"""
    if len(p) == 2:
        p[0] = PauseStatement(lineno=p.lineno(1))
    else:
        p[0] = PauseStatement(
            duration=Literal(value=p[2], kind='INTEGER', lineno=p.lineno(1)),
            lineno=p.lineno(1)
        )


# ============================================================================
# SUBPROGRAM DEFINITIONS
# ============================================================================

def p_function_definition(p):
    """function_definition : base_type FUNCTION ID '(' parameter_list ')' declaration_block statement_block END
                            | base_type FUNCTION ID '(' ')' declaration_block statement_block END"""
    return_type = p[1]
    name = p[3]
    
    if len(p) == 9:
        # No parameters
        parameters = []
        declarations = p[6] if p[6] else []
        body = p[7] if p[7] else []
    else:
        # With parameters
        parameters = p[5] if p[5] else []
        declarations = p[7] if p[7] else []
        body = p[8] if p[8] else []
    
    p[0] = FunctionDefinition(
        name=name,
        return_type=return_type,
        parameters=parameters,
        declarations=declarations,
        body=body,
        lineno=p.lineno(1)
    )


def p_subroutine_definition(p):
    """subroutine_definition : SUBROUTINE ID '(' parameter_list ')' declaration_block statement_block END
                              | SUBROUTINE ID '(' ')' declaration_block statement_block END"""
    name = p[2]
    
    if len(p) == 8:
        # No parameters
        parameters = []
        declarations = p[5] if p[5] else []
        body = p[6] if p[6] else []
    else:
        # With parameters
        parameters = p[4] if p[4] else []
        declarations = p[6] if p[6] else []
        body = p[7] if p[7] else []
    
    p[0] = SubroutineDefinition(
        name=name,
        parameters=parameters,
        declarations=declarations,
        body=body,
        lineno=p.lineno(1)
    )


def p_parameter_list(p):
    """parameter_list : ID
                      | parameter_list ',' ID"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


# ============================================================================
# EMPTY PRODUCTION
# ============================================================================

def p_empty(p):
    """empty :"""
    p[0] = None


# ============================================================================
# ERROR HANDLING
# ============================================================================

class ParserError(Exception):
    """Raised when a parse error occurs."""
    pass


def p_error(p):
    if p:
        raise ParserError(f"Syntax error at '{p.value}' (line {p.lineno})")
    else:
        raise ParserError("Syntax error: unexpected end of file")


# ============================================================================
# PARSER FACTORY
# ============================================================================

def build_parser(debug=False):
    """Build and return the parser."""
    return yacc.yacc(debug=debug, write_tables=True, start='program_unit')


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file.for>")
        return

    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()

        lexer = build_lexer()
        parser = build_parser()
        ast = parser.parse(source, lexer=lexer)

        if ast:
            print("Parse successful!")
            # Handle both Program and CompilationUnit
            if isinstance(ast, CompilationUnit):
                if ast.main_program:
                    print(f"Program: {ast.main_program.name}")
                    print(f"Declarations: {len(ast.main_program.declarations)}")
                    print(f"Statements: {len(ast.main_program.statements)}")
                print(f"Subprograms: {len(ast.subprograms)}")
            else:
                # Direct Program node
                print(f"Program: {ast.name}")
                print(f"Declarations: {len(ast.declarations)}")
                print(f"Statements: {len(ast.statements)}")
            # Pretty print AST
            import pprint
            pprint.pprint(ast)
        else:
            print("Parse failed: no result")

    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
    except ParserError as e:
        print(f"Parser error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
