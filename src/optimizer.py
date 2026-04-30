from ast_nodes import *

class Optimizer:
    """AST Optimizer to perform constant folding, dead code elimination, and simple CSE."""
    
    def __init__(self):
        self.modified = False

    def optimize(self, node: Node) -> Node:
        self.modified = True
        while self.modified:
            self.modified = False
            node = self.visit(node)
        return node
        
    def visit(self, node):
        if node is None: return None
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
        
    def optimize_block(self, statements):
        if not statements: return statements
        optimized = []
        reachable = True
        for stmt in statements:
            if getattr(stmt, 'label', None) is not None:
                reachable = True
            if reachable:
                optimized.append(self.visit(stmt))
            else:
                self.modified = True
            if isinstance(stmt, (GotoStatement, ReturnStatement)):
                reachable = False
        return [s for s in optimized if s is not None]

    def generic_visit(self, node):
        if isinstance(node, Program):
            node.statements = self.optimize_block(node.statements)
        elif isinstance(node, CompilationUnit):
            if node.main_program:
                node.main_program = self.visit(node.main_program)
            node.subprograms = [self.visit(s) for s in node.subprograms]
        elif isinstance(node, SubroutineDefinition) or isinstance(node, FunctionDefinition):
            node.body = self.optimize_block(node.body)
        elif isinstance(node, IfThenElse):
            node.condition = self.visit(node.condition)
            node.then_body = self.optimize_block(node.then_body)
            if node.else_body:
                node.else_body = self.optimize_block(node.else_body)
        elif isinstance(node, DoLoop):
            node.start = self.visit(node.start)
            node.stop = self.visit(node.stop)
            if node.step: node.step = self.visit(node.step)
            node.body = self.optimize_block(node.body)
        elif isinstance(node, AssignmentStatement):
            node.value = self.visit(node.value)
        elif isinstance(node, PrintStatement):
            node.expressions = [self.visit(e) for e in node.expressions]
        elif isinstance(node, BinaryOp):
            node.left = self.visit(node.left)
            node.right = self.visit(node.right)
            
            # Constant Folding
            if isinstance(node.left, Literal) and isinstance(node.right, Literal):
                if node.left.kind in ('INTEGER', 'REAL') and node.right.kind in ('INTEGER', 'REAL'):
                    v_left, v_right = node.left.value, node.right.value
                    if node.op == '+': val = v_left + v_right
                    elif node.op == '-': val = v_left - v_right
                    elif node.op == '*': val = v_left * v_right
                    elif node.op == '/': 
                        val = v_left // v_right if node.left.kind == 'INTEGER' else v_left / v_right
                    else: return node
                    self.modified = True
                    return Literal(value=val, kind=node.left.kind)
        return node
