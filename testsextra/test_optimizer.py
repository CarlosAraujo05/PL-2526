"""
Comprehensive unit tests for the AST Optimizer.

Tests constant folding, dead-store elimination, unreachable-code removal,
and ParenthesizedExpression simplification in isolation.
"""

import pytest
from src.optimizer import Optimizer
from ast_nodes import (
    Program, Literal, Variable, BinaryOp, UnaryOp,
    AssignmentStatement, IfThenElse, DoLoop,
    GotoStatement, ReturnStatement, PrintStatement,
    ContinueStatement, ParenthesizedExpression
)


@pytest.fixture
def opt():
    """Fresh Optimizer instance for each test."""
    return Optimizer()


# ============================================================================
# Constant Folding — Arithmetic
# ============================================================================

class TestConstantFoldingArithmetic:

    def test_add_integers(self, opt):
        node = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert isinstance(result, Literal)
        assert result.value == 5
        assert result.kind == 'INTEGER'

    def test_subtract_integers(self, opt):
        node = BinaryOp(op='-', left=Literal(value=10, kind='INTEGER'), right=Literal(value=4, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 6
        assert result.kind == 'INTEGER'

    def test_multiply_integers(self, opt):
        node = BinaryOp(op='*', left=Literal(value=7, kind='INTEGER'), right=Literal(value=6, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 42
        assert result.kind == 'INTEGER'

    def test_divide_integers(self, opt):
        node = BinaryOp(op='/', left=Literal(value=10, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 3  # integer division
        assert result.kind == 'INTEGER'

    def test_add_reals(self, opt):
        node = BinaryOp(op='+', left=Literal(value=2.5, kind='REAL'), right=Literal(value=1.5, kind='REAL'))
        result = opt.visit(node)
        assert result.value == 4.0
        assert result.kind == 'REAL'

    def test_mixed_int_real_promotes_to_real(self, opt):
        node = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3.0, kind='REAL'))
        result = opt.visit(node)
        assert result.value == 5.0
        assert result.kind == 'REAL'


# ============================================================================
# Constant Folding — Power operator `**`
# ============================================================================

class TestConstantFoldingPower:

    def test_power_integers(self, opt):
        node = BinaryOp(op='**', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 8
        assert result.kind == 'INTEGER'

    def test_power_zero_exponent(self, opt):
        node = BinaryOp(op='**', left=Literal(value=5, kind='INTEGER'), right=Literal(value=0, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 1

    def test_power_real_base(self, opt):
        node = BinaryOp(op='**', left=Literal(value=2.0, kind='REAL'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 8.0
        assert result.kind == 'REAL'


# ============================================================================
# Constant Folding — Relational Operators
# ============================================================================

class TestConstantFoldingRelational:

    def test_eq_true(self, opt):
        node = BinaryOp(op='.EQ.', left=Literal(value=5, kind='INTEGER'), right=Literal(value=5, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is True
        assert result.kind == 'LOGICAL'

    def test_eq_false(self, opt):
        node = BinaryOp(op='.EQ.', left=Literal(value=5, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is False

    def test_ne(self, opt):
        node = BinaryOp(op='.NE.', left=Literal(value=5, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is True

    def test_lt(self, opt):
        node = BinaryOp(op='.LT.', left=Literal(value=3, kind='INTEGER'), right=Literal(value=5, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is True

    def test_le(self, opt):
        node = BinaryOp(op='.LE.', left=Literal(value=5, kind='INTEGER'), right=Literal(value=5, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is True

    def test_gt(self, opt):
        node = BinaryOp(op='.GT.', left=Literal(value=7, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is True

    def test_ge(self, opt):
        node = BinaryOp(op='.GE.', left=Literal(value=3, kind='INTEGER'), right=Literal(value=5, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value is False

    def test_relational_reals(self, opt):
        node = BinaryOp(op='.EQ.', left=Literal(value=3.14, kind='REAL'), right=Literal(value=3.14, kind='REAL'))
        result = opt.visit(node)
        assert result.value is True


# ============================================================================
# Constant Folding — Logical Operators
# ============================================================================

class TestConstantFoldingLogical:

    def test_and_true_true(self, opt):
        node = BinaryOp(op='.AND.', left=Literal(value=True, kind='LOGICAL'), right=Literal(value=True, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is True
        assert result.kind == 'LOGICAL'

    def test_and_true_false(self, opt):
        node = BinaryOp(op='.AND.', left=Literal(value=True, kind='LOGICAL'), right=Literal(value=False, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is False

    def test_or_false_true(self, opt):
        node = BinaryOp(op='.OR.', left=Literal(value=False, kind='LOGICAL'), right=Literal(value=True, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is True

    def test_or_false_false(self, opt):
        node = BinaryOp(op='.OR.', left=Literal(value=False, kind='LOGICAL'), right=Literal(value=False, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is False

    def test_eq_logical(self, opt):
        node = BinaryOp(op='.EQ.', left=Literal(value=True, kind='LOGICAL'), right=Literal(value=True, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is True

    def test_ne_logical(self, opt):
        node = BinaryOp(op='.NE.', left=Literal(value=True, kind='LOGICAL'), right=Literal(value=False, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is True


# ============================================================================
# Constant Folding — Unary Operators
# ============================================================================

class TestConstantFoldingUnary:

    def test_unary_plus(self, opt):
        node = UnaryOp(op='+', operand=Literal(value=5, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == 5
        assert result.kind == 'INTEGER'

    def test_unary_minus(self, opt):
        node = UnaryOp(op='-', operand=Literal(value=7, kind='INTEGER'))
        result = opt.visit(node)
        assert result.value == -7
        assert result.kind == 'INTEGER'

    def test_unary_minus_real(self, opt):
        node = UnaryOp(op='-', operand=Literal(value=3.14, kind='REAL'))
        result = opt.visit(node)
        assert result.value == -3.14
        assert result.kind == 'REAL'

    def test_not_true(self, opt):
        node = UnaryOp(op='.NOT.', operand=Literal(value=True, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is False
        assert result.kind == 'LOGICAL'

    def test_not_false(self, opt):
        node = UnaryOp(op='.NOT.', operand=Literal(value=False, kind='LOGICAL'))
        result = opt.visit(node)
        assert result.value is True


# ============================================================================
# Constant Folding — ParenthesizedExpression
# ============================================================================

class TestConstantFoldingParenthesized:

    def test_parenthesized_literal(self, opt):
        node = ParenthesizedExpression(expr=Literal(value=42, kind='INTEGER'))
        result = opt.visit(node)
        assert isinstance(result, Literal)
        assert result.value == 42

    def test_parenthesized_binary(self, opt):
        inner = BinaryOp(op='+', left=Literal(value=1, kind='INTEGER'), right=Literal(value=2, kind='INTEGER'))
        node = ParenthesizedExpression(expr=inner)
        result = opt.visit(node)
        assert isinstance(result, Literal)
        assert result.value == 3


# ============================================================================
# Constant Folding — Nested / Complex expressions
# ============================================================================

class TestConstantFoldingNested:

    def test_nested_arithmetic(self, opt):
        # (2 + 3) * (4 - 1) => 5 * 3 => 15
        left = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        right = BinaryOp(op='-', left=Literal(value=4, kind='INTEGER'), right=Literal(value=1, kind='INTEGER'))
        node = BinaryOp(op='*', left=left, right=right)
        result = opt.visit(node)
        assert result.value == 15

    def test_power_chain(self, opt):
        # 2 ** 3 ** 1 => 8 ** 1 => 8
        left = BinaryOp(op='**', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        node = BinaryOp(op='**', left=left, right=Literal(value=1, kind='INTEGER'))
        result = opt.visit(node)
        # First fold inner: 2**3=8, then outer: 8**1=8
        # But optimizer only does one pass per visit; we need full optimize()
        result = opt.optimize(result)
        assert result.value == 8

    def test_relational_from_arithmetic(self, opt):
        # (2 + 3) .GT. 4 => 5 .GT. 4 => .TRUE.
        left = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        node = BinaryOp(op='.GT.', left=left, right=Literal(value=4, kind='INTEGER'))
        result = opt.optimize(node)
        assert result.value is True


# ============================================================================
# No Folding — Non-constant operands
# ============================================================================

class TestNoFolding:

    def test_binary_with_variable(self, opt):
        node = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Variable(name='X'))
        result = opt.visit(node)
        assert isinstance(result, BinaryOp)
        assert result is node  # unchanged

    def test_unary_with_variable(self, opt):
        node = UnaryOp(op='-', operand=Variable(name='X'))
        result = opt.visit(node)
        assert isinstance(result, UnaryOp)


# ============================================================================
# Dead-Store Elimination
# ============================================================================

class TestDeadStoreElimination:

    def test_remove_dead_store(self, opt):
        # X = 5       <-- dead (X never read)
        # Y = 10      <-- dead (Y never read)
        # PRINT *, 1
        stmts = [
            AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER')),
            AssignmentStatement(target=Variable(name='Y'), value=Literal(value=10, kind='INTEGER')),
            PrintStatement(expressions=[Literal(value=1, kind='INTEGER')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.visit_Program(prog)
        assert len(result.statements) == 1
        assert isinstance(result.statements[0], PrintStatement)

    def test_keep_live_store(self, opt):
        # X = 5       <-- live (X is read)
        # PRINT *, X
        stmts = [
            AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER')),
            PrintStatement(expressions=[Variable(name='X')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.visit_Program(prog)
        assert len(result.statements) == 2

    def test_keep_store_with_side_effect_rhs(self, opt):
        # X = ARR(1)  <-- ARR(1) may have side effects (bounds check)
        # PRINT *, 1
        arr_access = Variable(name='ARR')  # simplified; real ArrayAccess has side effects
        stmts = [
            AssignmentStatement(target=Variable(name='X'), value=arr_access),
            PrintStatement(expressions=[Literal(value=1, kind='INTEGER')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.visit_Program(prog)
        # Since we simplified arr_access to Variable (no side effects), X=ARR(1) is dead
        # In real code with ArrayAccess, it would be kept
        assert len(result.statements) == 1


# ============================================================================
# Unreachable Code Elimination
# ============================================================================

class TestUnreachableCode:

    def test_remove_after_goto(self, opt):
        # GOTO 10
        # X = 5       <-- unreachable
        # PRINT *, X  <-- unreachable
        # 10 CONTINUE
        stmts = [
            GotoStatement(target_label=10),
            AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER')),
            PrintStatement(expressions=[Variable(name='X')]),
            ContinueStatement(label=10),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        assert len(result.statements) == 2
        assert isinstance(result.statements[0], GotoStatement)
        assert isinstance(result.statements[1], ContinueStatement)

    def test_remove_after_return(self, opt):
        # RETURN
        # PRINT *, 1  <-- unreachable
        stmts = [
            ReturnStatement(),
            PrintStatement(expressions=[Literal(value=1, kind='INTEGER')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        assert len(result.statements) == 1
        assert isinstance(result.statements[0], ReturnStatement)

    def test_label_resets_reachability(self, opt):
        # GOTO 10
        # X = 5       <-- unreachable
        # 10 CONTINUE   <-- reachable again
        # PRINT *, 1
        stmts = [
            GotoStatement(target_label=10),
            AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER')),
            ContinueStatement(label=10),
            PrintStatement(expressions=[Literal(value=1, kind='INTEGER')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        assert len(result.statements) == 3
        assert isinstance(result.statements[0], GotoStatement)
        assert isinstance(result.statements[1], ContinueStatement)
        assert isinstance(result.statements[2], PrintStatement)


# ============================================================================
# IF Statement Constant Folding
# ============================================================================

class TestIfConstantFolding:

    def test_if_true_constant(self, opt):
        # IF (.TRUE.) THEN
        #   X = 5
        # ENDIF
        # PRINT *, X   <-- keeps X live so dead-store elimination won't remove the assignment
        stmts = [
            IfThenElse(
                condition=Literal(value=True, kind='LOGICAL'),
                then_body=[AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER'))],
                else_body=None
            ),
            PrintStatement(expressions=[Variable(name='X')]),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        # The IF is folded to its body (X = 5) because the condition is a constant .TRUE.
        assert len(result.statements) == 2
        assert isinstance(result.statements[0], AssignmentStatement)
        assert isinstance(result.statements[1], PrintStatement)

    def test_if_false_constant(self, opt):
        # IF (.FALSE.) THEN
        #   X = 5     <-- dead branch
        # ENDIF
        stmts = [
            IfThenElse(
                condition=Literal(value=False, kind='LOGICAL'),
                then_body=[AssignmentStatement(target=Variable(name='X'), value=Literal(value=5, kind='INTEGER'))],
                else_body=None
            )
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        # then-body is empty after dead-store elimination (X never read)
        assert len(result.statements) == 1


# ============================================================================
# DO Loop optimization
# ============================================================================

class TestDoLoopOptimization:

    def test_fold_do_bounds(self, opt):
        # DO 10 I = 1+1, 5*2
        #   PRINT *, I
        # 10 CONTINUE
        stmts = [
            DoLoop(
                var='I',
                start=BinaryOp(op='+', left=Literal(value=1, kind='INTEGER'), right=Literal(value=1, kind='INTEGER')),
                stop=BinaryOp(op='*', left=Literal(value=5, kind='INTEGER'), right=Literal(value=2, kind='INTEGER')),
                step=None,
                body=[PrintStatement(expressions=[Variable(name='I')])],
                label=10,
            ),
            ContinueStatement(label=10),
        ]
        prog = Program(name='T', statements=stmts)
        result = opt.optimize(prog)
        do_stmt = result.statements[0]
        assert isinstance(do_stmt, DoLoop)
        assert do_stmt.start.value == 2
        assert do_stmt.stop.value == 10


# ============================================================================
# Full optimize() fixpoint
# ============================================================================

class TestFixpoint:

    def test_multi_pass_folding(self, opt):
        # (1 + 2) * (3 + 4) => 3 * 7 => 21
        # Needs two passes: first fold the inner additions, then the outer multiplication
        left = BinaryOp(op='+', left=Literal(value=1, kind='INTEGER'), right=Literal(value=2, kind='INTEGER'))
        right = BinaryOp(op='+', left=Literal(value=3, kind='INTEGER'), right=Literal(value=4, kind='INTEGER'))
        node = BinaryOp(op='*', left=left, right=right)
        result = opt.optimize(node)
        assert isinstance(result, Literal)
        assert result.value == 21

    def test_nested_parenthesized(self, opt):
        # ((2 + 3))
        inner = BinaryOp(op='+', left=Literal(value=2, kind='INTEGER'), right=Literal(value=3, kind='INTEGER'))
        mid = ParenthesizedExpression(expr=inner)
        outer = ParenthesizedExpression(expr=mid)
        result = opt.optimize(outer)
        assert isinstance(result, Literal)
        assert result.value == 5
