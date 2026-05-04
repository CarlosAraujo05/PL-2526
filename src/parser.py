"""
Parser for Fortran 77 using PLY (Python Lex-Yacc).

Builds an abstract syntax tree (AST) from a token stream.
"""

import ply.yacc as yacc
import sys
from lexer import tokens, build_lexer
from symbol_table import SymbolTable, SemanticError, Symbol
from ast_nodes import *

# ============================================================================
# PROGRAM STRUCTURE
# ============================================================================

def p_program_unit(p):
    r"""program_unit : program
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
    r"""program : PROGRAM ID declaration_block statement_block END"""
    
    p.parser.current_program_unit = 'program'
    
    declarations = p[3] if p[3] else []
    statements = p[4] if p[4] else []
    
    symtab = p.parser.symbols
    # Pre-validate declarations (parameters are already added to symtab in p_parameter_declaration)
    for decl in declarations:
        if hasattr(decl, 'ids') and decl.ids:
            # TypeDeclaration: check first variable is declared
            symtab.lookup(decl.ids[0]['name'], decl.lineno)
    
    p[0] = Program(
        name=p[2],
        declarations=declarations,
        statements=statements,
        lineno=p.lineno(1)
    )


def p_declaration_block(p):
    r"""declaration_block : declaration_block declaration
                         | empty"""
    if p[1] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


def p_statement_block(p):
    r"""statement_block : statement_block labeled_statement
                       | empty"""
    if p[1] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []


# ============================================================================
# DECLARATIONS
# ============================================================================

def p_declaration(p):
    r"""declaration : type_declaration
                   | parameter_declaration"""
    p[0] = p[1]


def p_type_declaration(p):
    r"""type_declaration : base_type id_or_array_list"""
    symtab = p.parser.symbols
    dtype = p[1]
    lineno = p.lineno(1)
    
    for id_info in p[2]:
        name = id_info['name']
        dims = id_info['dimensions']
        
        if dims is not None:
            symbol = Symbol(name=name, kind='array', dtype=dtype, dimensions=dims, lineno=lineno)
        else:
            symbol = Symbol(name=name, kind='variable', dtype=dtype, dimensions=None, lineno=lineno)
        
        symtab.declare(symbol)
    
    p[0] = TypeDeclaration(dtype=dtype, ids=p[2], lineno=lineno)


def p_id_or_array_list(p):
    r"""id_or_array_list : id_or_array
                        | id_or_array_list ',' id_or_array"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_id_or_array(p):
    r"""id_or_array : ID
                   | ID '(' INTEGER_LIT ')'"""
    if len(p) == 2:
        # Simple ID, not an array
        p[0] = {'name': p[1], 'dimensions': None}
    else:
        # Array declaration
        p[0] = {'name': p[1], 'dimensions': p[3]}


def p_base_type(p):
    r"""base_type : INTEGER
                  | REAL
                  | LOGICAL
                  | CHARACTER
                  | CHARACTER '*' INTEGER_LIT"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f'CHARACTER*{p[3]}'


def p_parameter_declaration(p):
    r"""parameter_declaration : PARAMETER '(' assignment_list ')'"""
    symtab = p.parser.symbols
    # Add each parameter to the symbol table with kind='parameter'
    for assignment in p[3]:
        if isinstance(assignment.target, Variable):
            name = assignment.target.name
            # Determine the type from the literal value
            dtype = assignment.value.kind if hasattr(assignment.value, 'kind') else 'INTEGER'
            # Check if already declared
            if symtab.is_declared(name):
                symbol = symtab.lookup(name, assignment.lineno)
                # If already a parameter, raise error (duplicate parameter)
                if symbol.is_parameter():
                    raise SemanticError(f"Duplicate parameter declaration: '{name}'", assignment.lineno)
                # Otherwise, update kind to parameter
                symbol.kind = 'parameter'
            else:
                symbol = Symbol(name=name, kind='parameter', dtype=dtype, dimensions=None, lineno=assignment.lineno)
                symtab.declare(symbol)
    p[0] = ParameterDeclaration(assignments=p[3], lineno=p.lineno(1))


def p_assignment_list(p):
    r"""assignment_list : assignment
                       | assignment_list ',' assignment"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_assignment(p):
    r"""assignment : ID '=' literal"""
    p[0] = AssignmentStatement(
        target=Variable(name=p[1], lineno=p.lineno(1)),
        value=p[3],
        lineno=p.lineno(1)
    )





# ============================================================================
# STATEMENTS
# ============================================================================

def p_labeled_statement(p):
     r"""labeled_statement : INTEGER_LIT statement
                          | statement"""
     if len(p) == 2:
         p[0] = p[1]
     else:
         # INTEGER_LIT before a statement acts as a label
         label_num = int(p[1])
         p[2].label = label_num
         p[0] = p[2]
         # Register label in label_map for GOTO validation
         p.parser.label_map[label_num] = p.lineno(1)


def p_statement(p):
    r"""statement : assignment_statement
                 | if_statement
                 | do_loop
                 | goto_statement
                 | call_statement
                 | io_statement
                 | control_statement
                 | continue_statement"""
    p[0] = p[1]


def infer_expression_type(expr, symtab):
    """
    Infer the type of an expression node.
    
    Args:
        expr: AST expression node
        symtab: SymbolTable instance
        
    Returns:
        str: Type string ('INTEGER', 'REAL', 'LOGICAL', 'CHARACTER', 'STRING')
    """
    if isinstance(expr, Literal):
        return expr.kind
    
    if isinstance(expr, Variable):
        symbol = symtab.lookup(expr.name, expr.lineno)
        return symbol.dtype
    
    if isinstance(expr, ArrayAccess):
        symbol = symtab.lookup(expr.name, expr.lineno)
        return symbol.dtype
    
    if isinstance(expr, BinaryOp):
        # Fortran 77 type promotion: REAL op INTEGER -> REAL
        left_type = infer_expression_type(expr.left, symtab)
        right_type = infer_expression_type(expr.right, symtab)
        
        # Arithmetic operators
        if expr.op in ('+', '-', '*', '/'):
            if left_type == 'REAL' or right_type == 'REAL':
                return 'REAL'
            return 'INTEGER'
        
        # Relational operators return LOGICAL
        if expr.op in ('.EQ.', '.NE.', '.LT.', '.LE.', '.GT.', '.GE.'):
            return 'LOGICAL'
        
        # Logical operators
        if expr.op in ('.AND.', '.OR.'):
            return 'LOGICAL'
        
        # Power operator
        if expr.op == '**':
            if left_type == 'REAL' or right_type == 'REAL':
                return 'REAL'
            return 'INTEGER'
    
    if isinstance(expr, UnaryOp):
        if expr.op == '.NOT.':
            return 'LOGICAL'
        # Unary + or -
        return infer_expression_type(expr.operand, symtab)
    
    if isinstance(expr, FunctionCall):
        # Look up function return type
        symbol = symtab.lookup(expr.name, expr.lineno)
        return symbol.dtype
    
    if isinstance(expr, ParenthesizedExpression):
        return infer_expression_type(expr.expr, symtab)
    
    return 'INTEGER'  # Default fallback


def p_assignment_statement(p):
    r"""assignment_statement : ID '=' expression
                            | array_access '=' expression"""
    symtab = p.parser.symbols

    if isinstance(p[1], str):
        # Scalar assignment: check if target is a parameter
        symbol = symtab.lookup(p[1], p.lineno(1))
        if symbol.is_parameter():
            raise SemanticError(f"Cannot assign to parameter '{p[1]}'", p.lineno(1))
        target = Variable(name=p[1], lineno=p.lineno(1))
        
        # Type compatibility check
        target_type = symbol.dtype
        value_type = infer_expression_type(p[3], symtab)
        if not symtab.is_type_compatible(value_type, target_type):
            raise SemanticError(
                f"Type mismatch in assignment: cannot assign {value_type} to {target_type} variable '{p[1]}'",
                p.lineno(1)
            )
    else:
        # Array element assignment: check if array itself is a parameter
        symtab.check_array_access(p[1].name, 1, p.lineno(1))
        array_symbol = symtab.lookup(p[1].name, p.lineno(1))
        if array_symbol.is_parameter():
            raise SemanticError(f"Cannot assign to array parameter '{p[1].name}'", p.lineno(1))
        target = p[1]
        
        # Type compatibility check for array element
        target_type = array_symbol.dtype
        value_type = infer_expression_type(p[3], symtab)
        if not symtab.is_type_compatible(value_type, target_type):
            raise SemanticError(
                f"Type mismatch in assignment: cannot assign {value_type} to {target_type} array element '{p[1].name}'",
                p.lineno(1)
            )

    p[0] = AssignmentStatement(target=target, value=p[3], lineno=p.lineno(1))


def validate_goto_labels(parser):
    """
    Validate that all GOTO labels reference existing statement labels.
    
    Args:
        parser: Parser instance with label_map and goto_list
        
    Raises:
        SemanticError: If a GOTO references a non-existent label
    """
    for target_label, lineno in parser.goto_list:
        if target_label not in parser.label_map:
            raise SemanticError(
                f"GOTO to undefined label: {target_label}",
                lineno
            )


def validate_function_assignments(func_def, symtab, lineno):
    """
    Validate that a function name is assigned at least once in its body.
    
    Args:
        func_def: FunctionDefinition AST node
        symtab: SymbolTable instance
        lineno: Line number of function definition
        
    Raises:
        SemanticError: If function name is never assigned
    """
    function_name = func_def.name
    assigned = False
    
    def check_statement(stmt):
        nonlocal assigned
        if isinstance(stmt, AssignmentStatement):
            if isinstance(stmt.target, Variable) and stmt.target.name == function_name:
                assigned = True
        # Recursively check nested statements (IF, DO, etc.)
        if isinstance(stmt, IfThenElse):
            for s in stmt.then_body + (stmt.else_body or []):
                check_statement(s)
            for _, body in stmt.elseif_parts:
                for s in body:
                    check_statement(s)
        if isinstance(stmt, DoLoop):
            for s in stmt.body:
                check_statement(s)
    
    for stmt in func_def.body:
        check_statement(stmt)
    
    if not assigned:
        raise SemanticError(
            f"Function '{function_name}' must be assigned a value in its body",
            lineno
        )





def p_array_access(p):
    r"""array_access : ID '(' expression ')'"""
    symtab = p.parser.symbols
    symtab.check_array_access(p[1], 1, p.lineno(1))
    
    # Check array bounds if index is a literal integer
    index_expr = p[3]
    if isinstance(index_expr, Literal) and index_expr.kind == 'INTEGER':
        symbol = symtab.lookup(p[1], p.lineno(1))
        if symbol.dimensions is not None:
            # Fortran 77 arrays are 1-indexed by default
            lower_bound = 1
            upper_bound = symbol.dimensions
            if not (lower_bound <= index_expr.value <= upper_bound):
                raise SemanticError(
                    f"Array index {index_expr.value} out of bounds for '{p[1]}' (valid range: {lower_bound} to {upper_bound})",
                    p.lineno(1)
                )
    
    p[0] = ArrayAccess(name=p[1], indices=p[3], lineno=p.lineno(1))

# ============================================================================
# EXPRESSIONS (operator precedence)
# ============================================================================

def p_expression(p):
    r"""expression : logical_or_expression"""
    p[0] = p[1]


def p_logical_or_expression(p):
    r"""logical_or_expression : logical_and_expression
                             | logical_or_expression OR logical_and_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='.OR.', left=p[1], right=p[3], lineno=p.lineno(1))


def p_logical_and_expression(p):
    r"""logical_and_expression : logical_not_expression
                              | logical_and_expression AND logical_not_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='.AND.', left=p[1], right=p[3], lineno=p.lineno(1))


def p_logical_not_expression(p):
    r"""logical_not_expression : relational_expression
                              | NOT relational_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op='.NOT.', operand=p[2], lineno=p.lineno(1))


def p_relational_expression(p):
    r"""relational_expression : additive_expression
                             | additive_expression relational_op additive_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_relational_op(p):
    r"""relational_op : EQ
                     | NE
                     | LT
                     | LE
                     | GT
                     | GE"""
    p[0] = p[1]


def p_additive_expression(p):
    r"""additive_expression : multiplicative_expression
                           | additive_expression '+' multiplicative_expression
                           | additive_expression '-' multiplicative_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_multiplicative_expression(p):
    r"""multiplicative_expression : power_expression
                                 | multiplicative_expression '*' power_expression
                                 | multiplicative_expression '/' power_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op=p[2], left=p[1], right=p[3], lineno=p.lineno(1))


def p_power_expression(p):
    r"""power_expression : unary_expression
                        | power_expression POW unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryOp(op='**', left=p[1], right=p[3], lineno=p.lineno(1))


def p_unary_expression(p):
    r"""unary_expression : primary_expression
                        | '-' unary_expression
                        | '+' unary_expression"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op=p[1], operand=p[2], lineno=p.lineno(1))


def p_primary_expression(p):
     r"""primary_expression : literal
                           | ID
                           | array_access
                           | '(' expression ')'
                           | function_call"""
     if len(p) == 2:
         # Single-token productions: literal, ID, array_access, function_call (all return nodes/values)
         if isinstance(p[1], str):
             # ID token - convert to Variable node, validate declaration
             symtab = p.parser.symbols
             symtab.lookup(p[1], p.lineno(1))  # Raises SemanticError if not declared
             p[0] = Variable(name=p[1], lineno=p.lineno(1))
         else:
             # literal, array_access, or function_call - already AST nodes
             p[0] = p[1]
     else:
         # len(p) == 4: Parenthesized expression '(' expression ')'
         p[0] = ParenthesizedExpression(expr=p[2], lineno=p.lineno(1))


def p_function_call(p):
     r"""function_call : ID '(' argument_list ')'
                      | ID '(' ')'"""
     if len(p) == 3:
         # No-args case: ID '(' ')'
         p[0] = FunctionCall(name=p[1], arguments=[], lineno=p.lineno(1))
     else:
         # With-args case: ID '(' argument_list ')'
         p[0] = FunctionCall(name=p[1], arguments=p[3], lineno=p.lineno(1))


def p_argument_list(p):
    r"""argument_list : expression
                     | argument_list ',' expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_literal_integer(p):
    r"""literal : INTEGER_LIT"""
    p[0] = Literal(value=p[1], kind='INTEGER', lineno=p.lineno(1))

def p_literal_real(p):
    r"""literal : REAL_LIT"""
    p[0] = Literal(value=p[1], kind='REAL', lineno=p.lineno(1))

def p_literal_string(p):
    r"""literal : STRING_LIT"""
    p[0] = Literal(value=p[1], kind='STRING', lineno=p.lineno(1))

def p_literal_true(p):
    r"""literal : TRUE"""
    p[0] = Literal(value=True, kind='LOGICAL', lineno=p.lineno(1))
def p_literal_false(p):
    r"""literal : FALSE"""
    p[0] = Literal(value=False, kind='LOGICAL', lineno=p.lineno(1))
# ============================================================================
# CONTROL FLOW STATEMENTS
# ============================================================================

def p_if_statement(p):
     r"""if_statement : IF '(' expression ')' THEN statement_block else_clause ENDIF
                    | IF '(' expression ')' THEN statement_block ENDIF"""
     then_body = p[6] if p[6] else []
     
     if len(p) == 8:
         # With else_clause: IF '(' expression ')' THEN statement_block else_clause ENDIF
         else_body = p[7][0] if p[7] and p[7][0] else None
         elseif_parts = p[7][1] if p[7] and len(p[7]) > 1 else []
     else:
         # Without else_clause: IF '(' expression ')' THEN statement_block ENDIF (len == 7)
         else_body = None
         elseif_parts = []
     
     p[0] = IfThenElse(
         condition=p[3],
         then_body=then_body,
         else_body=else_body,
         elseif_parts=elseif_parts,
         lineno=p.lineno(1)
     )


def p_else_clause(p):
    r"""else_clause : ELSE statement_block
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
    r"""do_loop : DO INTEGER_LIT ID '=' expression ',' expression statement_block INTEGER_LIT CONTINUE
               | DO INTEGER_LIT ID '=' expression ',' expression ',' expression statement_block INTEGER_LIT CONTINUE"""
    symtab = p.parser.symbols
    
    symtab.check_scalar_access(p[3], p.lineno(3))
    
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
    
    if label_start != label_end:
        raise SemanticError(
            f"DO loop labels do not match: {label_start} != {label_end}",
            p.lineno(1)
        )
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
    r"""goto_statement : GOTO INTEGER_LIT"""
    target_label = int(p[2])
    # Register GOTO for later validation
    p.parser.goto_list.append((target_label, p.lineno(1)))
    p[0] = GotoStatement(target_label=target_label, lineno=p.lineno(1))


# ============================================================================
# I/O STATEMENTS
# ============================================================================

def p_io_statement(p):
    r"""io_statement : read_statement
                    | print_statement"""
    p[0] = p[1]


def p_read_statement(p):
    r"""read_statement : READ '*' ',' read_list
                      | READ '(' unit ',' format ')' read_list"""
    if len(p) == 5:
        p[0] = ReadStatement(unit=None, format_spec=None, variables=p[4], lineno=p.lineno(1))
    else:
        p[0] = ReadStatement(unit=p[3], format_spec=p[5], variables=p[7], lineno=p.lineno(1))


def p_read_list(p):
    r"""read_list : read_item
                 | read_list ',' read_item"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_read_item(p):
    r"""read_item : ID
                 | array_access"""
    if isinstance(p[1], str):
        p[0] = Variable(name=p[1], lineno=p.lineno(1))
    else:
        p[0] = p[1]


def p_print_statement(p):
     r"""print_statement : PRINT '*' ',' output_list
                        | PRINT format ',' output_list"""
     # Both rules have identical symbol count (4), so parser merges them.
     # Distinguish at runtime: if p[2] == '*', it's the first rule; else it's the second rule
     format_spec = p[2] if p[2] != '*' else '*'
     p[0] = PrintStatement(format_spec=format_spec, expressions=p[4], lineno=p.lineno(1))


def p_output_list(p):
    r"""output_list : expression
                   | output_list ',' expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_unit(p):
     r"""unit : INTEGER_LIT
             | '*'"""
     if p[1] == '*':
         p[0] = '*'
     else:
         p[0] = Literal(value=p[1], kind='INTEGER', lineno=p.lineno(1))


def p_format(p):
    r"""format : INTEGER_LIT
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
    r"""control_statement : RETURN"""
    # RETURN only allowed in functions and subroutines, not in main program
    if p.parser.current_program_unit == 'program':
        raise SemanticError(
            "RETURN not allowed in main program",
            p.lineno(1)
        )
    p[0] = ReturnStatement(lineno=p.lineno(1))


def p_call_statement(p):
     r"""call_statement : CALL ID '(' argument_list ')'
                       | CALL ID '(' ')'"""
     if len(p) == 4:
         # No-args case: CALL ID '(' ')'
         p[0] = CallStatement(name=p[2], arguments=[], lineno=p.lineno(1))
     else:
         # With-args case: CALL ID '(' argument_list ')'
         p[0] = CallStatement(name=p[2], arguments=p[4], lineno=p.lineno(1))


def p_continue_statement(p):
    r"""continue_statement : CONTINUE"""
    p[0] = ContinueStatement(lineno=p.lineno(1))


# ============================================================================
# SUBPROGRAM DEFINITIONS
# ============================================================================

def p_function_definition(p):
     r"""function_definition : base_type FUNCTION ID '(' parameter_list ')' declaration_block statement_block END
                             | base_type FUNCTION ID '(' ')' declaration_block statement_block END"""
     p.parser.current_program_unit = 'function'
     return_type = p[1]
     name = p[3]
     
     if len(p) == 8:
         # No parameters: base_type FUNCTION ID '(' ')' declaration_block statement_block END
         parameters = []
         declarations = p[6] if p[6] else []
         body = p[7] if p[7] else []
     else:
         # With parameters: base_type FUNCTION ID '(' parameter_list ')' declaration_block statement_block END (len == 9)
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
     
     # Validate function has at least one assignment to function name
     validate_function_assignments(p[0], p.parser.symbols, p.lineno(1))


def p_subroutine_definition(p):
     r"""subroutine_definition : SUBROUTINE ID '(' parameter_list ')' declaration_block statement_block END
                               | SUBROUTINE ID '(' ')' declaration_block statement_block END"""
     p.parser.current_program_unit = 'subroutine'
     name = p[2]
     
     if len(p) == 7:
         # No parameters: SUBROUTINE ID '(' ')' declaration_block statement_block END
         parameters = []
         declarations = p[5] if p[5] else []
         body = p[6] if p[6] else []
     else:
         # With parameters: SUBROUTINE ID '(' parameter_list ')' declaration_block statement_block END (len == 8)
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
    r"""parameter_list : ID
                      | parameter_list ',' ID"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


# ============================================================================
# EMPTY PRODUCTION
# ============================================================================

def p_empty(p):
    r"""empty :"""
    p[0] = None


# ============================================================================
# ERROR HANDLING
# ============================================================================

class SyntaxError(Exception):
    """Raised when a parse error occurs."""
    pass


def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' (line {p.lineno})")
    else:
        raise SyntaxError("Syntax error: unexpected end of file")


# ============================================================================
# PARSER FACTORY
# ============================================================================

def build_parser(debug=False):
     r"""Build and return the parser."""

     parser = yacc.yacc(debug=debug, write_tables=True, start='program_unit')
     parser.symbols = SymbolTable()  # Add symbol table to parser for semantic analysis
     parser.label_map = {}  # Map: label_number -> lineno
     parser.goto_list = []  # List of (target_label, lineno)
     parser.current_program_unit = 'program'  # Track context: 'program', 'function', 'subroutine'
     return parser

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

        lexer = build_lexer(source_text=source)
        parser = build_parser()
        ast = parser.parse(lexer=lexer)

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
    except SyntaxError as e:
        print(f"Syntax error: {e}")
    except SemanticError as e:
        print(f"Semantic error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
