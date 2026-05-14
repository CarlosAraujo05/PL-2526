"""
Symbol Table implementation for Fortran 77 Compiler.

Maintains symbol information with support for:
- Scoped symbol management (enter/exit scopes)
- Type tracking and compatibility checking
- Array dimension tracking
- Full symbol metadata (name, kind, type, dimensions, line number)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ============================================================================
# SYMBOL REPRESENTATION
# ============================================================================

@dataclass
class Symbol:
    """Represents a symbol (variable, array, function, parameter, etc.)."""
    name: str
    kind: str          # 'variable', 'array', 'function', 'subroutine', 'parameter'
    dtype: str         # 'INTEGER', 'REAL', 'LOGICAL', 'CHARACTER'
    dimensions: Optional[int] = None  # Unidimensional array length (None = scalar)
    lineno: int = 0    # Declaration line number for error reporting
    initialized: bool = False  # Whether variable has been assigned

    def is_array(self) -> bool:
        """Check if this symbol represents an array."""
        return self.dimensions is not None

    def is_scalar(self) -> bool:
        """Check if this symbol represents a scalar variable."""
        return self.dimensions is None

    def is_parameter(self) -> bool:
        """Check if this symbol is a parameter (constant)."""
        return self.kind == 'parameter'

    def __repr__(self) -> str:
        """String representation for debugging."""
        dims_str = f" [len={self.dimensions}]" if self.dimensions is not None else ""
        return f"Symbol({self.name}:{self.dtype}{dims_str}, kind={self.kind}, line={self.lineno})"


# ============================================================================
# SEMANTIC ERROR
# ============================================================================

class SemanticError(Exception):
    """Raised when a semantic analysis error occurs."""

    def __init__(self, message: str, lineno: int = 0):
        """
        Initialize semantic error.

        Args:
            message: Error description
            lineno: Line number where error occurred
        """
        self.message = message
        self.lineno = lineno
        full_msg = f"Semantic error at line {lineno}: {message}" if lineno else f"Semantic error: {message}"
        super().__init__(full_msg)


# ============================================================================
# SYMBOL TABLE
# ============================================================================

class SymbolTable:
    """
    Scoped symbol table for managing variable, function, and parameter declarations.

    Features:
    - Multiple scopes (for functions, subroutines)
    - Type tracking and compatibility checking
    - Array dimension tracking
    - Line number tracking for error reporting
    """

    def __init__(self):
        """Initialize the symbol table with a global scope."""
        self.scopes: List[Dict[str, Symbol]] = [{}]  # Stack of scopes
        self.current_scope_level = 0

    def enter_scope(self) -> None:
        """Enter a new scope (e.g., for a function or subroutine)."""
        self.scopes.append({})
        self.current_scope_level += 1

    def exit_scope(self) -> None:
        """Exit the current scope and return to the parent scope."""
        if self.current_scope_level == 0:
            raise SemanticError("Cannot exit global scope")
        self.scopes.pop()
        self.current_scope_level -= 1

    def declare(self, symbol: Symbol) -> None:
        """
        Declare a new symbol in the current scope.

        Args:
            symbol: Symbol object to declare

        Raises:
            SemanticError: If symbol already declared in current scope
        """
        current_table = self.scopes[self.current_scope_level]

        if symbol.name in current_table:
            raise SemanticError(
                f"Duplicate declaration of {symbol.kind} '{symbol.name}'",
                symbol.lineno
            )

        current_table[symbol.name] = symbol

    def lookup(self, name: str, lineno: int = 0) -> Symbol:
        """
        Look up a symbol by name (searches from current scope to global scope).

        Args:
            name: Symbol name to look up
            lineno: Line number for error reporting

        Returns:
            Symbol object with full metadata

        Raises:
            SemanticError: If symbol not found in any scope
        """
        # Search from current scope down to global scope
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i][name]

        raise SemanticError(f"Undeclared variable: '{name}'", lineno)

    def is_declared(self, name: str) -> bool:
        """
        Check if a symbol is declared without raising an error.

        Args:
            name: Symbol name to check

        Returns:
            True if declared in any scope, False otherwise
        """
        for i in range(self.current_scope_level, -1, -1):
            if name in self.scopes[i]:
                return True
        return False

    def initialize(self, name: str, lineno: int = 0) -> None:
        """
        Mark a variable as initialized (assigned a value).

        Args:
            name: Variable name to initialize
            lineno: Line number for error reporting

        Raises:
            SemanticError: If variable not declared
        """
        symbol = self.lookup(name, lineno)
        symbol.initialized = True

    def is_initialized(self, name: str) -> bool:
        """
        Check if a variable has been initialized.

        Args:
            name: Variable name to check

        Returns:
            True if initialized, False if declared but not initialized

        Raises:
            SemanticError: If variable not declared
        """
        symbol = self.lookup(name)
        return symbol.initialized

    # ========================================================================
    # TYPE CHECKING AND COMPATIBILITY
    # ========================================================================

    def is_type_compatible(self, source_type: str, target_type: str) -> bool:
        """
        Check if source_type can be assigned to target_type.

        This compiler enforces stricter type safety than standard Fortran 77:
        - INTEGER ← INTEGER, REAL (truncated)
        - REAL ← INTEGER, REAL
        - LOGICAL ← LOGICAL only
        - CHARACTER ← CHARACTER only

        LOGICAL → INTEGER/REAL and INTEGER/REAL → LOGICAL are explicitly
        rejected per AGENTS.md §Parser / Semantic checks point 3.

        Args:
            source_type: Type being assigned
            target_type: Type being assigned to

        Returns:
            True if compatible, False otherwise
        """
        if source_type == target_type:
            return True

        # INTEGER can accept REAL (with truncation)
        if target_type == 'INTEGER':
            return source_type == 'REAL'

        # REAL can accept INTEGER
        if target_type == 'REAL':
            return source_type == 'INTEGER'

        # LOGICAL only accepts LOGICAL (no implicit conversion from numeric)
        if target_type == 'LOGICAL':
            return False

        # CHARACTER can only accept CHARACTER
        if target_type == 'CHARACTER':
            return source_type == 'CHARACTER'

        return False

    def check_array_access(self, name: str, dimension_count: int, lineno: int = 0) -> None:
        """
        Check if array access has correct number of dimensions.

        Args:
            name: Array name
            dimension_count: Number of subscripts provided
            lineno: Line number for error reporting

        Raises:
            SemanticError: If dimension count mismatch or not an array
        """
        symbol = self.lookup(name, lineno)

        if not symbol.is_array():
            raise SemanticError(
                f"'{name}' is not an array, cannot subscript",
                lineno
            )

        if dimension_count != 1:
            raise SemanticError(
                f"Array '{name}' is unidimensional, expected 1 subscript "
                f"but {dimension_count} subscripts provided",
                lineno
            )

    def check_scalar_access(self, name: str, lineno: int = 0) -> None:
        """
        Check if scalar variable access is valid (not subscripted).

        Args:
            name: Variable name
            lineno: Line number for error reporting

        Raises:
            SemanticError: If variable is an array (should be subscripted)
        """
        symbol = self.lookup(name, lineno)

        if symbol.is_array():
            raise SemanticError(
                f"Array '{name}' must be subscripted",
                lineno
            )

    # ========================================================================
    # SYMBOL QUERIES
    # ========================================================================

    def get_all_symbols(self) -> Dict[str, Symbol]:
        """
        Get all symbols in current scope (not including parent scopes).

        Returns:
            Dictionary of symbol name -> Symbol
        """
        return self.scopes[self.current_scope_level].copy()

    def get_symbol_count(self) -> int:
        """Get number of symbols in current scope."""
        return len(self.scopes[self.current_scope_level])

    def get_scope_depth(self) -> int:
        """Get current scope depth (0 = global)."""
        return self.current_scope_level

    def __repr__(self) -> str:
        """String representation for debugging."""
        lines = [f"SymbolTable (scope depth: {self.current_scope_level})"]
        for i, scope in enumerate(self.scopes):
            lines.append(f"  Scope {i}:")
            for name, symbol in scope.items():
                lines.append(f"    {symbol}")
        return "\n".join(lines)
