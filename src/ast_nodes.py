"""
AST Node Hierarchy for Fortran 77 Compiler.

Defines all node types used to represent the abstract syntax tree
produced by the parser.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Any


# ============================================================================
# BASE NODE
# ============================================================================

@dataclass
class Node:
    """Base class for all AST nodes."""
    lineno: int = 0


# ============================================================================
# PROGRAM STRUCTURE
# ============================================================================

@dataclass
class Program(Node):
    """Root node representing a Fortran PROGRAM."""
    name: str = ""
    declarations: List[Declaration] = field(default_factory=list)
    statements: List[Statement] = field(default_factory=list)


@dataclass
class CompilationUnit(Node):
    """Complete compilation unit (program + optional subprograms)."""
    main_program: Optional[Program] = None
    subprograms: List[SubroutineDefinition | FunctionDefinition] = field(default_factory=list)


# ============================================================================
# DECLARATIONS
# ============================================================================

@dataclass
class Declaration(Node):
    """Base class for all declarations."""
    pass


@dataclass
class TypeDeclaration(Declaration):
    """Variable type declaration (INTEGER, REAL, etc.)."""
    dtype: str = ""
    ids: List[str | dict] = field(default_factory=list)  # Either plain str or {'name': str, 'dimensions': list}


@dataclass
class ParameterDeclaration(Declaration):
    """PARAMETER declaration."""
    assignments: List[AssignmentStatement] = field(default_factory=list)


# ============================================================================
# STATEMENTS
# ============================================================================

@dataclass
class Statement(Node):
    """Base class for all statements."""
    label: Optional[int] = None


@dataclass
class AssignmentStatement(Statement):
    """Variable or array assignment."""
    target: Optional[Expression] = None
    value: Optional[Expression] = None


@dataclass
class IfThenElse(Statement):
    """IF...THEN...ELSE...ENDIF block."""
    condition: Optional[Expression] = None
    then_body: List[Statement] = field(default_factory=list)
    else_body: Optional[List[Statement]] = None
    elseif_parts: List[tuple] = field(default_factory=list)


@dataclass
class DoLoop(Statement):
    """DO loop with optional step."""
    var: str = ""
    start: Optional[Expression] = None
    stop: Optional[Expression] = None
    step: Optional[Expression] = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class GotoStatement(Statement):
    """GOTO label statement."""
    target_label: int = 0


@dataclass
class CallStatement(Statement):
    """CALL subroutine_name(...) statement."""
    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class ReadStatement(Statement):
    """READ statement."""
    unit: Optional[Expression] = None
    format_spec: Optional[Any] = None
    variables: List[str] = field(default_factory=list)


@dataclass
class PrintStatement(Statement):
    """PRINT statement."""
    format_spec: Optional[Any] = None
    expressions: List[Expression] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    """RETURN statement."""
    pass


@dataclass
class ContinueStatement(Statement):
    """CONTINUE statement."""
    pass


# ============================================================================
# EXPRESSIONS
# ============================================================================

@dataclass
class Expression(Node):
    """Base class for all expressions."""
    pass


@dataclass
class BinaryOp(Expression):
    """Binary operation (arithmetic, logical, relational)."""
    op: str = ""
    left: Optional[Expression] = None
    right: Optional[Expression] = None


@dataclass
class UnaryOp(Expression):
    """Unary operation (negation, logical NOT)."""
    op: str = ""
    operand: Optional[Expression] = None


@dataclass
class Variable(Expression):
    """Variable reference."""
    name: str = ""


@dataclass
class ArrayAccess(Expression):
    """Array element access: arr(i)."""
    name: str = ""
    index: Optional[Expression] = None 


@dataclass
class FunctionCall(Expression):
    """Function call expression."""
    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class Literal(Expression):
    """Literal value (integer, real, string, boolean)."""
    value: Any = None
    kind: str = 'INTEGER'


@dataclass
class ParenthesizedExpression(Expression):
    """Expression enclosed in parentheses."""
    expr: Optional[Expression] = None


# ============================================================================
# SUBPROGRAMS
# ============================================================================

@dataclass
class SubroutineDefinition(Node):
    """SUBROUTINE definition."""
    name: str = ""
    parameters: List[str] = field(default_factory=list)
    declarations: List[Declaration] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)


@dataclass
class FunctionDefinition(Node):
    """FUNCTION definition."""
    name: str = ""
    return_type: str = ""
    parameters: List[str] = field(default_factory=list)
    declarations: List[Declaration] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)
