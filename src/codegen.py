from ast_nodes import *

class CodeGen:
    def __init__(self):
        self.instructions = []
        self._label_counter = 0
        self.var_map = {}
        self._var_counter = 0
        self.label_map = {} # Fortran label -> VM label
        self.in_function = False
        
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

    def _push_var(self, name: str):
        """Emit PUSHG or PUSHL depending on scope."""
        addr = self.get_var_addr(name)
        if self.in_function:
            self.emit(f"PUSHL {addr}")
        else:
            self.emit(f"PUSHG {addr}")

    def _store_var(self, name: str):
        """Emit STOREG or STOREL depending on scope."""
        addr = self.get_var_addr(name)
        if self.in_function:
            self.emit(f"STOREL {addr}")
        else:
            self.emit(f"STOREG {addr}")
        
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
        for decl in node.declarations:
            self.visit(decl)
        for stmt in node.statements:
            self.visit(stmt)
        self.emit("STOP")

    def visit_TypeDeclaration(self, node: TypeDeclaration):
        # For statically allocated vars, we might not need to emit instructions, just reserve addresses.
        for id_info in node.ids:
            if isinstance(id_info, dict):
                name = id_info['name']
                dimensions = id_info.get('dimensions')
                # Only allocate if dimensions is explicitly provided (array declaration)
                if dimensions is not None:
                    total_size = 1
                    if isinstance(dimensions, int):
                        total_size = dimensions
                    elif isinstance(dimensions, (list, tuple)):
                        for dim in dimensions:
                            if isinstance(dim, (list, tuple)) and len(dim) == 2:
                                lower, upper = dim
                                total_size *= (upper - lower + 1)
                            elif isinstance(dim, int):
                                total_size *= dim
                            else:
                                total_size *= 1
                    addr = self.get_var_addr(name)
                    self.emit(f"ALLOC {total_size}")
                    if self.in_function:
                        self.emit(f"STOREL {addr}")
                    else:
                        self.emit(f"STOREG {addr}")
                else:
                    # Scalar: just reserve an address
                    self.get_var_addr(name)
            else:
                # Scalar: just reserve an address
                self.get_var_addr(id_info)

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        if isinstance(node.target, Variable):
            self.visit(node.value)
            self._store_var(node.target.name)
        elif isinstance(node.target, ArrayAccess):
            # Array store: push base addr, push index (0-based), push value, STOREN
            self._push_var(node.target.name)      # address
            self.visit(node.target.indices)       # index (1-based in Fortran)
            self.emit("PUSHI 1")
            self.emit("SUB")                      # convert to 0-based
            self.visit(node.value)                # value
            self.emit("STOREN")
        elif isinstance(node.target, FunctionCall):
            # Assignment to function name (return value)
            self.visit(node.value)
            self._store_var(node.target.name)

    def visit_IfThenElse(self, node: IfThenElse):
        has_else = bool(node.else_body)
        has_elseif = bool(node.elseif_parts)
        
        # If there's no else and no elseif, we only need one label
        end_lbl = self.new_label()
        
        # Main IF condition
        self.visit(node.condition)
        if has_else or has_elseif:
            next_lbl = self.new_label()
        else:
            next_lbl = end_lbl
        self.emit(f"JZ {next_lbl}")
        
        for stmt in node.then_body:
            self.visit(stmt)
        self.emit(f"JUMP {end_lbl}")
        
        if has_else or has_elseif:
            self.emit(f"{next_lbl}:")
        
        # ELSEIF parts
        for part in node.elseif_parts:
            if isinstance(part, (list, tuple)) and len(part) == 2:
                condition, body = part
            else:
                continue
            self.visit(condition)
            next_lbl = self.new_label()
            self.emit(f"JZ {next_lbl}")
            
            for stmt in body:
                self.visit(stmt)
            self.emit(f"JUMP {end_lbl}")
            
            self.emit(f"{next_lbl}:")
        
        # ELSE body
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        self.emit(f"{end_lbl}:")

    def visit_DoLoop(self, node: DoLoop):
        loop_start = self.new_label()
        loop_end = self.new_label()
        
        # Init var
        self.visit(node.start)
        self._store_var(node.var)
        
        self.emit(f"{loop_start}:")
        
        # Condition: var <= stop
        self._push_var(node.var)
        self.visit(node.stop)
        self.emit("INFEQ")
        self.emit(f"JZ {loop_end}")
        
        # Body
        for stmt in node.body:
            self.visit(stmt)
            
        # Increment
        self._push_var(node.var)
        if node.step:
            self.visit(node.step)
        else:
            self.emit("PUSHI 1")
        self.emit("ADD")
        self._store_var(node.var)
        
        self.emit(f"JUMP {loop_start}")
        self.emit(f"{loop_end}:")

    def visit_GotoStatement(self, node: GotoStatement):
        self.emit(f"JUMP {self.get_user_label(node.target_label)}")

    def visit_ContinueStatement(self, node: ContinueStatement):
        pass

    def visit_ReturnStatement(self, node: ReturnStatement):
        self.emit("RETURN")

    def visit_ReadStatement(self, node: ReadStatement):
        for var in node.variables:
            if isinstance(var, Variable):
                self.emit("READ")
                self.emit("ATOI")  # READ returns string; convert to integer
                self._store_var(var.name)
            elif isinstance(var, ArrayAccess):
                # Array read: push base addr, push 0-based index, READ, ATOI, STOREN
                self._push_var(var.name)
                self.visit(var.indices)
                self.emit("PUSHI 1")
                self.emit("SUB")
                self.emit("READ")
                self.emit("ATOI")
                self.emit("STOREN")

    def _emit_write(self, expr):
        """Emit code to evaluate expr and print it with the correct WRITE* opcode."""
        if isinstance(expr, Literal):
            self.visit(expr)
            if expr.kind == 'STRING':
                self.emit("WRITES")
            elif expr.kind == 'REAL':
                self.emit("WRITEF")
            else:
                self.emit("WRITEI")
        else:
            self.visit(expr)
            # Default to integer write for non-literal expressions
            self.emit("WRITEI")

    def visit_PrintStatement(self, node: PrintStatement):
        for expr in node.expressions:
            self._emit_write(expr)
        self.emit("WRITELN")

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)
        ops = {
            '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
            '.EQ.': 'EQUAL',
            '.LT.': 'INF', '.LE.': 'INFEQ', 
            '.GT.': 'SUP', '.GE.': 'SUPEQ',
            '.AND.': 'AND', '.OR.': 'OR',
            'MOD': 'MOD'
        }
        if node.op == '.NE.':
            self.emit("EQUAL")
            self.emit("NOT")
        elif node.op in ops:
            self.emit(ops[node.op])

    def visit_UnaryOp(self, node: UnaryOp):
        self.visit(node.operand)
        if node.op == '.NOT.':
            self.emit("NOT")
        elif node.op == '-':
            self.emit("PUSHI 0")
            self.emit("SWAP")
            self.emit("SUB")

    def visit_ParenthesizedExpression(self, node: ParenthesizedExpression):
        self.visit(node.expr)

    def visit_ArrayAccess(self, node: ArrayAccess):
        # Array read: push base addr, push index (0-based), LOADN
        self._push_var(node.name)
        self.visit(node.indices)
        self.emit("PUSHI 1")
        self.emit("SUB")  # Fortran is 1-based, VM is 0-based
        self.emit("LOADN")

    def visit_Variable(self, node: Variable):
        self._push_var(node.name)

    def visit_Literal(self, node: Literal):
        if node.kind == 'INTEGER':
            self.emit(f"PUSHI {node.value}")
        elif node.kind == 'REAL':
            self.emit(f"PUSHF {node.value}")
        elif node.kind == 'STRING':
            self.emit(f"PUSHS \"{node.value}\"")
        elif node.kind == 'LOGICAL':
            self.emit(f"PUSHI {1 if node.value else 0}")

    def visit_FunctionCall(self, node: FunctionCall):
        # Handle intrinsic functions directly
        if node.name == 'MOD':
            # MOD(a, b) -> a mod b. Push args in normal order, then MOD.
            for arg in node.arguments:
                self.visit(arg)
            self.emit("MOD")
            return
        
        # Push arguments in reverse order so first param is at fp[1]
        for arg in reversed(node.arguments):
            self.visit(arg)
        self.emit(f"PUSHA FUNC{node.name}")
        self.emit("CALL")
        # Clean up arguments from stack, keeping return value on top
        for _ in node.arguments:
            self.emit("SWAP")
            self.emit("POP 1")

    def visit_CallStatement(self, node: CallStatement):
        for arg in reversed(node.arguments):
            self.visit(arg)
        self.emit(f"PUSHA SUBR{node.name}")
        self.emit("CALL")
        # Subroutine has no return value; just pop the arguments
        if node.arguments:
            self.emit(f"POP {len(node.arguments)}")

    def visit_FunctionDefinition(self, node: FunctionDefinition):
        func_label = f"FUNC{node.name}"
        self.emit(f"{func_label}:")
        
        old_var_map = self.var_map
        old_var_counter = self._var_counter
        old_in_function = self.in_function
        self.var_map = {}
        self._var_counter = 0
        self.in_function = True
        
        # Function name holds the return value at fp[0]
        self.var_map[node.name] = 0
        self._var_counter = 1
        
        # Parameters at fp[1], fp[2], ...
        for i, param in enumerate(node.parameters):
            self.var_map[param] = i + 1
        self._var_counter = len(node.parameters) + 1
        
        for decl in node.declarations:
            self.visit(decl)
        
        for stmt in node.body:
            self.visit(stmt)
        
        # Only emit implicit RETURN if the body doesn't end with an explicit one
        if not node.body or not isinstance(node.body[-1], ReturnStatement):
            self.emit("RETURN")
        
        self.var_map = old_var_map
        self._var_counter = old_var_counter
        self.in_function = old_in_function

    def visit_SubroutineDefinition(self, node: SubroutineDefinition):
        func_label = f"SUBR{node.name}"
        self.emit(f"{func_label}:")
        
        old_var_map = self.var_map
        old_var_counter = self._var_counter
        old_in_function = self.in_function
        self.var_map = {}
        self._var_counter = 0
        self.in_function = True
        
        # Parameters at fp[1], fp[2], ...
        for i, param in enumerate(node.parameters):
            self.var_map[param] = i + 1
        self._var_counter = len(node.parameters) + 1
        
        for decl in node.declarations:
            self.visit(decl)
        
        for stmt in node.body:
            self.visit(stmt)
        
        # Only emit implicit RETURN if the body doesn't end with an explicit one
        if not node.body or not isinstance(node.body[-1], ReturnStatement):
            self.emit("RETURN")
        
        self.var_map = old_var_map
        self._var_counter = old_var_counter
        self.in_function = old_in_function
