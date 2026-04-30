from ast_nodes import *

class CodeGen:
    def __init__(self):
        self.instructions = []
        self._label_counter = 0
        self.var_map = {}
        self._var_counter = 0
        self.label_map = {} # Fortran label -> VM label
        
    def new_label(self):
        l = f"L{self._label_counter}"
        self._label_counter += 1
        return l
        
    def get_user_label(self, ulabel: int):
        if ulabel not in self.label_map:
            self.label_map[ulabel] = self.new_label()
        return self.label_map[ulabel]
        
    def get_var_addr(self, name: str):
        # We allocate a new address if it doesn't exist
        if name not in self.var_map:
            self.var_map[name] = self._var_counter
            self._var_counter += 1
        return self.var_map[name]
        
    def emit(self, instr: str):
        self.instructions.append(instr)
        
    def generate(self, node: Node):
        self.visit(node)
        
    def output(self) -> str:
        return "\n".join(self.instructions) + "\n"
        
    def visit(self, node):
        if node is None: return
        
        # If statement has a label, emit it
        if isinstance(node, Statement) and getattr(node, 'label', None):
            self.emit(f"{self.get_user_label(node.label)}:")
            
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        pass # Optional: log unimplemented nodes

    def visit_CompilationUnit(self, node: CompilationUnit):
        if node.main_program:
            self.visit(node.main_program)
        for sub in node.subprograms:
            self.visit(sub)

    def visit_Program(self, node: Program):
        self.emit("START")
        # Pre-allocate variables by scanning declarations?
        # A simple stack machine just addresses by index. We just let them allocate as they appear.
        for stmt in node.statements:
            self.visit(stmt)
        self.emit("STOP")

    def visit_TypeDeclaration(self, node: TypeDeclaration):
        # For statically allocated vars, we might not need to emit instructions, just reserve addresses.
        pass

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        self.visit(node.value)
        if isinstance(node.target, Variable):
            addr = self.get_var_addr(node.target.name)
            self.emit(f"STOREG {addr}")
        elif isinstance(node.target, ArrayAccess):
            self.visit(node.target.indices)
            addr = self.get_var_addr(node.target.name)
            # Depending on VM, arrays might be STOREA base_addr or similar.
            # Using basic STOREA if standard
            self.emit(f"STOREA {addr}")

    def visit_IfThenElse(self, node: IfThenElse):
        else_lbl = self.new_label()
        end_lbl = self.new_label()
        
        self.visit(node.condition)
        self.emit(f"JZ {else_lbl}")
        
        for stmt in node.then_body:
            self.visit(stmt)
        self.emit(f"JUMP {end_lbl}")
        
        self.emit(f"{else_lbl}:")
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        self.emit(f"{end_lbl}:")

    def visit_DoLoop(self, node: DoLoop):
        loop_start = self.new_label()
        loop_end = self.new_label()
        var_addr = self.get_var_addr(node.var)
        
        # Init var
        self.visit(node.start)
        self.emit(f"STOREG {var_addr}")
        
        self.emit(f"{loop_start}:")
        
        # Condition
        self.emit(f"PUSHG {var_addr}")
        self.visit(node.stop)
        self.emit("INFEQ")
        self.emit(f"JZ {loop_end}")
        
        # Body
        for stmt in node.body:
            self.visit(stmt)
            
        # Increment
        self.emit(f"PUSHG {var_addr}")
        if node.step:
            self.visit(node.step)
        else:
            self.emit("PUSHI 1")
        self.emit("ADD")
        self.emit(f"STOREG {var_addr}")
        
        self.emit(f"JUMP {loop_start}")
        self.emit(f"{loop_end}:")

    def visit_GotoStatement(self, node: GotoStatement):
        self.emit(f"JUMP {self.get_user_label(node.target_label)}")

    def visit_ContinueStatement(self, node: ContinueStatement):
        pass

    def visit_ReadStatement(self, node: ReadStatement):
        for var in node.variables:
            self.emit("READ")
            if isinstance(var, Variable):
                addr = self.get_var_addr(var.name)
                self.emit(f"STOREG {addr}")
            elif isinstance(var, ArrayAccess):
                self.visit(var.indices)
                addr = self.get_var_addr(var.name)
                self.emit(f"STOREA {addr}")

    def visit_PrintStatement(self, node: PrintStatement):
        for expr in node.expressions:
            if isinstance(expr, Literal) and expr.kind == 'STRING':
                self.emit(f"PUSHS {expr.value}")
                self.emit("WRITES")
            else:
                self.visit(expr)
                # Guessing type based on AST could improve this, generic WRITEI
                self.emit("WRITEI")
        self.emit("WRITELN") # new line

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)
        ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            '.EQ.': 'EQUAL', '.NE.': 'NOTEQUAL', 
            '.LT.': 'INF', '.LE.': 'INFEQ', 
            '.GT.': 'SUP', '.GE.': 'SUPEQ'
        }
        if node.op in ops:
            self.emit(ops[node.op])

    def visit_Variable(self, node: Variable):
        addr = self.get_var_addr(node.name)
        self.emit(f"PUSHG {addr}")

    def visit_Literal(self, node: Literal):
        if node.kind == 'INTEGER':
            self.emit(f"PUSHI {node.value}")
        elif node.kind == 'REAL':
            self.emit(f"PUSHF {node.value}")
        elif node.kind == 'STRING':
            self.emit(f"PUSHS '{node.value}'")
        elif node.kind == 'LOGICAL':
            self.emit(f"PUSHI {1 if node.value else 0}")
