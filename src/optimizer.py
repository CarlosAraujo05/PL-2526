"""
AST Optimizer for Fortran 77 Compiler.

Performs constant folding, unreachable code elimination, and basic dead-store
elimination at the AST level.
"""

try:
    from ast_nodes import (
        Node, Program, CompilationUnit, SubroutineDefinition, FunctionDefinition,
        IfThenElse, DoLoop, AssignmentStatement, GotoStatement, ReturnStatement,
        ContinueStatement, PrintStatement, ReadStatement, CallStatement,
        BinaryOp, UnaryOp, Literal, Variable, ArrayAccess, ParenthesizedExpression,
        FunctionCall
    )
except ImportError:
    from src.ast_nodes import (
        Node, Program, CompilationUnit, SubroutineDefinition, FunctionDefinition,
        IfThenElse, DoLoop, AssignmentStatement, GotoStatement, ReturnStatement,
        ContinueStatement, PrintStatement, ReadStatement, CallStatement,
        BinaryOp, UnaryOp, Literal, Variable, ArrayAccess, ParenthesizedExpression,
        FunctionCall
    )


class Optimizer:
    """AST Optimizer for constant folding and dead code elimination."""

    def __init__(self):
        self.modified = False
        self._function_name = None  # Track current function for dead-store protection
        self._nested_depth = 0      # Track nesting level; dead-store only at depth 0

    def optimize(self, node: Node) -> Node:
        """Run optimization passes until fixpoint."""
        self.modified = True
        while self.modified:
            self.modified = False
            node = self.visit(node)
        return node

    # -------------------------------------------------------------------------
    # Visitor dispatch
    # -------------------------------------------------------------------------

    def visit(self, node):
        if node is None:
            return None
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Default visitor for unhandled node types."""
        return node

    # -------------------------------------------------------------------------
    # Block-level optimizations
    # -------------------------------------------------------------------------

    def optimize_block(self, statements):
        """
        Optimize a list of statements (basic block).
        Removes unreachable statements and dead stores.
        """
        if not statements:
            return statements

        # Pass 1: remove unreachable statements (after GOTO / RETURN)
        reachable = True
        filtered = []
        for stmt in statements:
            if getattr(stmt, 'label', None) is not None:
                reachable = True
            if reachable:
                filtered.append(stmt)
            else:
                self.modified = True
            if isinstance(stmt, (GotoStatement, ReturnStatement)):
                reachable = False

        # Pass 2: dead-store elimination (only at top-level blocks)
        if self._nested_depth == 0:
            # Collect all variables read in this block
            read_vars = set()
            for stmt in filtered:
                read_vars.update(self._collect_reads(stmt))

            # Keep assignments whose target is read later or has side effects
            result = []
            for stmt in filtered:
                if isinstance(stmt, AssignmentStatement):
                    target_name = self._assignment_target_name(stmt.target)
                    if target_name is not None and target_name not in read_vars:
                        # Protect function return value assignments
                        if target_name == self._function_name:
                            result.append(self.visit(stmt))
                            continue
                        # Dead store — skip it unless RHS has side effects
                        if not self._has_side_effects(stmt.value):
                            self.modified = True
                            continue
                result.append(self.visit(stmt))

            return [s for s in result if s is not None]
        else:
            # Inside nested block — skip dead-store elimination to avoid
            # removing stores whose target is live in an outer scope.
            return [self.visit(s) for s in filtered if s is not None]

    def _collect_reads(self, node):
        """Collect all variable names read by a node."""
        reads = set()
        self._collect_reads_recursive(node, reads)
        return reads

    def _collect_reads_recursive(self, node, reads):
        if node is None:
            return
        if isinstance(node, Variable):
            reads.add(node.name)
        elif isinstance(node, ArrayAccess):
            reads.add(node.name)
            self._collect_reads_recursive(node.index, reads)
        elif isinstance(node, BinaryOp):
            self._collect_reads_recursive(node.left, reads)
            self._collect_reads_recursive(node.right, reads)
        elif isinstance(node, UnaryOp):
            self._collect_reads_recursive(node.operand, reads)
        elif isinstance(node, ParenthesizedExpression):
            self._collect_reads_recursive(node.expr, reads)
        elif isinstance(node, AssignmentStatement):
            self._collect_reads_recursive(node.value, reads)
        elif isinstance(node, PrintStatement):
            for expr in node.expressions:
                self._collect_reads_recursive(expr, reads)
        elif isinstance(node, IfThenElse):
            self._collect_reads_recursive(node.condition, reads)
            for stmt in (node.then_body or []):
                self._collect_reads_recursive(stmt, reads)
            for stmt in (node.else_body or []):
                self._collect_reads_recursive(stmt, reads)
        elif isinstance(node, DoLoop):
            self._collect_reads_recursive(node.start, reads)
            self._collect_reads_recursive(node.stop, reads)
            if node.step:
                self._collect_reads_recursive(node.step, reads)
            for stmt in node.body:
                self._collect_reads_recursive(stmt, reads)
        elif isinstance(node, (Literal, GotoStatement, ReturnStatement,
                               ContinueStatement)):
            pass

    def _assignment_target_name(self, node):
        """Return variable name for an assignment target, or None."""
        if isinstance(node, Variable):
            return node.name
        if isinstance(node, ArrayAccess):
            return node.name
        return None

    def _has_side_effects(self, node):
        """Check if an expression may have side effects (conservative)."""
        if node is None:
            return False
        if isinstance(node, (Literal, Variable)):
            return False
        if isinstance(node, ArrayAccess):
            return True  # could be out of bounds; conservative
        if isinstance(node, FunctionCall):
            return True
        if isinstance(node, ParenthesizedExpression):
            return self._has_side_effects(node.expr)
        if isinstance(node, BinaryOp):
            return (self._has_side_effects(node.left) or
                    self._has_side_effects(node.right))
        if isinstance(node, UnaryOp):
            return self._has_side_effects(node.operand)
        return True

    # -------------------------------------------------------------------------
    # Node visitors
    # -------------------------------------------------------------------------

    def visit_Program(self, node):
        node.statements = self.optimize_block(node.statements)
        return node

    def visit_CompilationUnit(self, node):
        if node.main_program:
            node.main_program = self.visit(node.main_program)
        node.subprograms = [self.visit(s) for s in node.subprograms]
        return node

    def visit_SubroutineDefinition(self, node):
        node.body = self.optimize_block(node.body)
        return node

    def visit_FunctionDefinition(self, node):
        old_name = self._function_name
        self._function_name = node.name
        node.body = self.optimize_block(node.body)
        self._function_name = old_name
        return node

    def visit_IfThenElse(self, node):
        node.condition = self.visit(node.condition)
        self._nested_depth += 1
        node.then_body = self.optimize_block(node.then_body)
        if node.else_body:
            node.else_body = self.optimize_block(node.else_body)
        self._nested_depth -= 1
        # If condition is a constant literal, fold to single branch
        if isinstance(node.condition, Literal) and node.condition.kind == 'LOGICAL':
            if node.condition.value:
                if len(node.then_body) == 1:
                    self.modified = True
                    return node.then_body[0]
            else:
                if node.else_body and len(node.else_body) == 1:
                    self.modified = True
                    return node.else_body[0]
        return node

    def visit_DoLoop(self, node):
        node.start = self.visit(node.start)
        node.stop = self.visit(node.stop)
        if node.step:
            node.step = self.visit(node.step)
        self._nested_depth += 1
        node.body = self.optimize_block(node.body)
        self._nested_depth -= 1
        return node

    def visit_AssignmentStatement(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_PrintStatement(self, node):
        node.expressions = [self.visit(e) for e in node.expressions]
        return node

    def visit_ReadStatement(self, node):
        return node

    def visit_CallStatement(self, node):
        node.arguments = [self.visit(a) for a in node.arguments]
        return node

    def visit_ParenthesizedExpression(self, node):
        node.expr = self.visit(node.expr)
        if isinstance(node.expr, Literal):
            self.modified = True
            return node.expr
        return node

    def visit_UnaryOp(self, node):
        node.operand = self.visit(node.operand)
        if isinstance(node.operand, Literal):
            val = node.operand.value
            kind = node.operand.kind
            if kind in ('INTEGER', 'REAL'):
                if node.op == '+':
                    self.modified = True
                    return Literal(value=+val, kind=kind)
                if node.op == '-':
                    self.modified = True
                    return Literal(value=-val, kind=kind)
            if kind == 'LOGICAL' and node.op == '.NOT.':
                self.modified = True
                return Literal(value=not val, kind='LOGICAL')
        return node

    def visit_BinaryOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # Constant folding for numeric, relational, and logical ops
        if isinstance(node.left, Literal) and isinstance(node.right, Literal):
            return self._fold_binary_literal(node, node.left, node.right)
        return node

    def _fold_binary_literal(self, node, left, right):
        """Fold a BinaryOp when both operands are literals."""
        op = node.op
        v_l, v_r = left.value, right.value
        k_l, k_r = left.kind, right.kind

        # Both numeric
        if k_l in ('INTEGER', 'REAL') and k_r in ('INTEGER', 'REAL'):
            if op == '+':
                val = v_l + v_r
            elif op == '-':
                val = v_l - v_r
            elif op == '*':
                val = v_l * v_r
            elif op == '/':
                if k_l == 'INTEGER' and k_r == 'INTEGER':
                    val = v_l // v_r
                else:
                    val = v_l / v_r
            elif op == '**':
                val = v_l ** v_r
            elif op == '.EQ.':
                val = v_l == v_r
                return Literal(value=val, kind='LOGICAL')
            elif op == '.NE.':
                val = v_l != v_r
                return Literal(value=val, kind='LOGICAL')
            elif op == '.LT.':
                val = v_l < v_r
                return Literal(value=val, kind='LOGICAL')
            elif op == '.LE.':
                val = v_l <= v_r
                return Literal(value=val, kind='LOGICAL')
            elif op == '.GT.':
                val = v_l > v_r
                return Literal(value=val, kind='LOGICAL')
            elif op == '.GE.':
                val = v_l >= v_r
                return Literal(value=val, kind='LOGICAL')
            else:
                return node

            self.modified = True
            result_kind = 'REAL' if (k_l == 'REAL' or k_r == 'REAL') else 'INTEGER'
            return Literal(value=val, kind=result_kind)

        # Both logical
        if k_l == 'LOGICAL' and k_r == 'LOGICAL':
            if op == '.AND.':
                val = v_l and v_r
            elif op == '.OR.':
                val = v_l or v_r
            elif op == '.EQ.':
                val = v_l == v_r
            elif op == '.NE.':
                val = v_l != v_r
            else:
                return node
            self.modified = True
            return Literal(value=val, kind='LOGICAL')

        # Mixed logical comparison (e.g. .EQ. between LOGICAL and something)
        if op == '.EQ.':
            val = v_l == v_r
        elif op == '.NE.':
            val = v_l != v_r
        else:
            return node
        self.modified = True
        return Literal(value=val, kind='LOGICAL')
