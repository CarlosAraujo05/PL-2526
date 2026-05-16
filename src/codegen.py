from ast_nodes import *

class CodeGen:
    def __init__(self, emit_comments: bool = False):
        self.instructions = []
        self._label_counter = 0
        self.var_map = {}
        self._var_counter = 0
        self.label_map = {} # Fortran label -> VM label
        self.in_function = False
        self._needs_pow_helper = False
        self._needs_mod_helper = False
        self.var_types = {}   # name -> dtype (for type inference)
        self.func_types = {}  # func_name -> return_dtype
        self._emit_comments = emit_comments
        self._num_locals = 0  # locals allocated in current function scope
        
    def new_label(self):
        l = f"L{self._label_counter}"
        self._label_counter += 1
        return l

    def new_if_false_label(self):
        l = f"IFFALSE{self._label_counter}"
        self._label_counter += 1
        return l

    def new_if_end_label(self):
        l = f"IFEND{self._label_counter}"
        self._label_counter += 1
        return l

    def new_do_start_label(self):
        l = f"DOLOOP{self._label_counter}"
        self._label_counter += 1
        return l

    def new_do_end_label(self):
        l = f"DOEND{self._label_counter}"
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
            self.emit(f"PUSHL {addr}", f"push local {name}")
        else:
            self.emit(f"PUSHG {addr}", f"push global {name}")

    def _store_var(self, name: str):
        """Emit STOREG or STOREL depending on scope."""
        addr = self.get_var_addr(name)
        if self.in_function:
            self.emit(f"STOREL {addr}", f"store local {name}")
        else:
            self.emit(f"STOREG {addr}", f"store global {name}")
        
    def emit(self, instr: str, comment: str = ""):
        if self._emit_comments and comment:
            self.instructions.append(f"{instr}  // {comment}")
        else:
            self.instructions.append(instr)
        
    def generate(self, node: Node):
        self.visit(node)
        
    def output(self) -> str:
        return "\n".join(self.instructions) + "\n"
        
    def visit(self, node):
        if node is None: return
        
        # If statement has a label, emit it
        if isinstance(node, Statement) and getattr(node, 'label', None):
            self.emit(f"{self.get_user_label(node.label)}:", f"Fortran label {node.label}")
            
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node):
        pass # Optional: log unimplemented nodes

    # ========================================================================
    # TYPE INFERENCE & CONVERSION HELPERS
    # ========================================================================

    def _normalize_type(self, dtype):
        """Normalize a dtype string for comparison (e.g., CHARACTER*10 -> STRING)."""
        if dtype and isinstance(dtype, str) and dtype.startswith('CHARACTER'):
            return 'STRING'
        return dtype

    def _infer_expr_type(self, expr):
        """Infer the VM type of an expression node."""
        if isinstance(expr, Literal):
            return expr.kind
        if isinstance(expr, Variable):
            return self._normalize_type(self.var_types.get(expr.name, 'INTEGER'))
        if isinstance(expr, ArrayAccess):
            return self._normalize_type(self.var_types.get(expr.name, 'INTEGER'))
        if isinstance(expr, BinaryOp):
            if expr.op in ('+', '-', '*', '/'):
                left = self._infer_expr_type(expr.left)
                right = self._infer_expr_type(expr.right)
                return 'REAL' if (left == 'REAL' or right == 'REAL') else 'INTEGER'
            if expr.op == '**':
                left = self._infer_expr_type(expr.left)
                right = self._infer_expr_type(expr.right)
                return 'REAL' if (left == 'REAL' or right == 'REAL') else 'INTEGER'
            if expr.op in ('.EQ.', '.NE.', '.LT.', '.LE.', '.GT.', '.GE.'):
                return 'LOGICAL'
            if expr.op in ('.AND.', '.OR.'):
                return 'LOGICAL'
        if isinstance(expr, UnaryOp):
            if expr.op == '.NOT.':
                return 'LOGICAL'
            return self._infer_expr_type(expr.operand)
        if isinstance(expr, ParenthesizedExpression):
            return self._infer_expr_type(expr.expr)
        if isinstance(expr, FunctionCall):
            if expr.name == 'MOD':
                return 'INTEGER'
            return self._normalize_type(self.func_types.get(expr.name, 'INTEGER'))
        return 'INTEGER'

    def _emit_conversion(self, from_type, to_type):
        """Emit ITOF or FTOI if a conversion between numeric types is required."""
        if from_type == to_type:
            return
        if from_type == 'INTEGER' and to_type == 'REAL':
            self.emit("ITOF", "convert integer to real")
        elif from_type == 'REAL' and to_type == 'INTEGER':
            self.emit("FTOI", "convert real to integer (truncate)")

    def visit_CompilationUnit(self, node: CompilationUnit):
        if node.main_program:
            self.visit(node.main_program)
        for sub in node.subprograms:
            self.visit(sub)
        if self._needs_pow_helper:
            self._emit_pow_helper()
        if self._needs_mod_helper:
            self._emit_mod_helper()

    def visit_Program(self, node: Program):
        self.emit("START", "program entry")
        for decl in node.declarations:
            self.visit(decl)
        for stmt in node.statements:
            self.visit(stmt)
        self.emit("STOP", "program exit")

    def visit_TypeDeclaration(self, node: TypeDeclaration):
        """Reserve addresses for declared variables; allocate arrays on the heap."""
        for id_info in node.ids:
            name = id_info['name']
            self.var_types[name] = node.dtype
            dimensions = id_info.get('dimensions')
            if dimensions is not None:
                # Unidimensional array: dimensions is an int (size)
                addr = self.get_var_addr(name)
                self.emit(f"ALLOC {dimensions}", f"allocate array {name}[{dimensions}]")
                if self.in_function:
                    self.emit(f"STOREL {addr}", f"store array base addr for {name}")
                else:
                    self.emit(f"STOREG {addr}", f"store array base addr for {name}")
            else:
                # Scalar: reserve address and explicitly zero-initialize
                addr = self.get_var_addr(name)
                if not self.in_function:
                    self.emit("PUSHI 0", f"zero-init global {name}")
                    self.emit(f"STOREG {addr}", f"store global {name}")
                # Locals are bulk-zeroed by PUSHN in visit_FunctionDefinition

    def visit_AssignmentStatement(self, node: AssignmentStatement):
        target_type = 'INTEGER'
        if isinstance(node.target, Variable):
            target_type = self._normalize_type(self.var_types.get(node.target.name, 'INTEGER'))
        elif isinstance(node.target, ArrayAccess):
            target_type = self._normalize_type(self.var_types.get(node.target.name, 'INTEGER'))
        elif isinstance(node.target, FunctionCall):
            target_type = self._normalize_type(self.func_types.get(node.target.name, 'INTEGER'))

        value_type = self._infer_expr_type(node.value)

        if isinstance(node.target, Variable):
            self.visit(node.value)
            if value_type == 'REAL' and target_type != 'REAL':
                self._emit_conversion('REAL', target_type)
            elif value_type != 'REAL' and target_type == 'REAL':
                self._emit_conversion(value_type, 'REAL')
            self._store_var(node.target.name)
        elif isinstance(node.target, ArrayAccess):
            # Array store: push base addr, push index (0-based), push value, STOREN
            self._push_var(node.target.name)      # address
            self.visit(node.target.index)         # index (1-based in Fortran)
            self.emit("PUSHI 1", "Fortran index is 1-based")
            self.emit("SUB", "convert to 0-based index")
            self.visit(node.value)
            if value_type == 'REAL' and target_type != 'REAL':
                self._emit_conversion('REAL', target_type)
            elif value_type != 'REAL' and target_type == 'REAL':
                self._emit_conversion(value_type, 'REAL')
            self.emit("STOREN", f"store into array {node.target.name}")
        elif isinstance(node.target, FunctionCall):
            # Assignment to function name (return value)
            self.visit(node.value)
            if value_type == 'REAL' and target_type != 'REAL':
                self._emit_conversion('REAL', target_type)
            elif value_type != 'REAL' and target_type == 'REAL':
                self._emit_conversion(value_type, 'REAL')
            self._store_var(node.target.name)

    def visit_IfThenElse(self, node: IfThenElse):
        has_else = bool(node.else_body)
        has_elseif = bool(node.elseif_parts)
        
        end_lbl = self.new_if_end_label()
        
        # Main IF condition
        self.visit(node.condition)
        if has_else or has_elseif:
            next_lbl = self.new_if_false_label()
        else:
            next_lbl = end_lbl
        self.emit(f"JZ {next_lbl}", "jump to else/elseif if false")
        
        for stmt in node.then_body:
            self.visit(stmt)
        if has_else or has_elseif:
            self.emit(f"JUMP {end_lbl}", "skip else/elseif")
            self.emit(f"{next_lbl}:")
        
        # ELSEIF parts
        for part in node.elseif_parts:
            if isinstance(part, (list, tuple)) and len(part) == 2:
                condition, body = part
            else:
                continue
            self.visit(condition)
            next_lbl = self.new_if_false_label()
            self.emit(f"JZ {next_lbl}", "jump to next elseif/else if false")
            
            for stmt in body:
                self.visit(stmt)
            self.emit(f"JUMP {end_lbl}", "skip remaining branches")
            
            self.emit(f"{next_lbl}:")
        
        # ELSE body
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        self.emit(f"{end_lbl}:", "end if")

    def visit_DoLoop(self, node: DoLoop):
        loop_start = self.new_do_start_label()
        loop_end = self.new_do_end_label()
        
        # Init loop variable
        self.visit(node.start)
        self._store_var(node.var)
        
        self.emit(f"{loop_start}:", f"DO loop start for {node.var}")
        
        # Condition: var <= stop
        self._push_var(node.var)
        self.visit(node.stop)
        self.emit("INFEQ", f"{node.var} <= stop?")
        self.emit(f"JZ {loop_end}", "exit loop if false")
        
        # Body
        for stmt in node.body:
            self.visit(stmt)
            
        # Increment
        self._push_var(node.var)
        if node.step:
            self.visit(node.step)
        else:
            self.emit("PUSHI 1", "default step = 1")
        self.emit("ADD", f"increment {node.var}")
        self._store_var(node.var)
        
        self.emit(f"JUMP {loop_start}", "repeat loop")
        self.emit(f"{loop_end}:", f"DO loop end for {node.var}")

    def visit_GotoStatement(self, node: GotoStatement):
        self.emit(f"JUMP {self.get_user_label(node.target_label)}", f"goto {node.target_label}")

    def visit_ContinueStatement(self, node: ContinueStatement):
        pass

    def visit_ReturnStatement(self, node: ReturnStatement):
        if self.in_function and self._num_locals > 0:
            self.emit(f"POP {self._num_locals}", f"clean up {self._num_locals} local(s)")
        self.emit("RETURN", "return to caller")

    def visit_ReadStatement(self, node: ReadStatement):
        for var in node.variables:
            var_type = 'INTEGER'
            if isinstance(var, Variable):
                var_type = self._normalize_type(self.var_types.get(var.name, 'INTEGER'))
            elif isinstance(var, ArrayAccess):
                var_type = self._normalize_type(self.var_types.get(var.name, 'INTEGER'))

            if isinstance(var, Variable):
                self.emit("READ", f"read {var.name}")
                if var_type == 'REAL':
                    self.emit("ATOF", "convert string to real")
                else:
                    self.emit("ATOI", "convert string to integer")
                self._store_var(var.name)
            elif isinstance(var, ArrayAccess):
                self._push_var(var.name)
                self.visit(var.index)
                self.emit("PUSHI 1", "Fortran index is 1-based")
                self.emit("SUB", "convert to 0-based")
                self.emit("READ", f"read {var.name}[index]")
                if var_type == 'REAL':
                    self.emit("ATOF", "convert string to real")
                else:
                    self.emit("ATOI", "convert string to integer")
                self.emit("STOREN", f"store into array {var.name}")

    def _emit_write(self, expr):
        """Emit code to evaluate expr and print it with the correct WRITE* opcode."""
        self.visit(expr)
        expr_type = self._infer_expr_type(expr)
        if expr_type == 'STRING':
            self.emit("WRITES", "print string")
        elif expr_type == 'REAL':
            self.emit("WRITEF", "print real")
        else:
            self.emit("WRITEI", "print integer")

    def visit_PrintStatement(self, node: PrintStatement):
        for expr in node.expressions:
            self._emit_write(expr)
        self.emit("WRITELN", "newline")

    def visit_BinaryOp(self, node: BinaryOp):
        if node.op == '**':
            self._needs_pow_helper = True
            self.emit("PUSHI 0", "reserve return slot for POW")
            self.visit(node.right)
            self.visit(node.left)
            self.emit("PUSHA POW", "call POW helper")
            self.emit("CALL")
            self.emit("POP 2", "clean up arguments")
            return

        left_type = self._infer_expr_type(node.left)
        right_type = self._infer_expr_type(node.right)

        needs_real = False
        if node.op in ('+', '-', '*', '/'):
            needs_real = (left_type == 'REAL' or right_type == 'REAL')
        elif node.op in ('.LT.', '.LE.', '.GT.', '.GE.', '.EQ.', '.NE.'):
            needs_real = (left_type == 'REAL' or right_type == 'REAL')

        self.visit(node.left)
        if needs_real and left_type != 'REAL':
            self._emit_conversion(left_type, 'REAL')

        self.visit(node.right)
        if needs_real and right_type != 'REAL':
            self._emit_conversion(right_type, 'REAL')

        if node.op == '.NE.':
            self.emit("EQUAL", "==")
            self.emit("NOT", "!=")
        elif node.op == '.EQ.':
            self.emit("EQUAL", "operator .EQ.")
        elif node.op in ('.LT.', '.LE.', '.GT.', '.GE.'):
            ops = {'.LT.': 'INF', '.LE.': 'INFEQ', '.GT.': 'SUP', '.GE.': 'SUPEQ'}
            fops = {'.LT.': 'FINF', '.LE.': 'FINFEQ', '.GT.': 'FSUP', '.GE.': 'FSUPEQ'}
            self.emit(fops[node.op] if needs_real else ops[node.op], f"operator {node.op}")
        elif node.op in ('+', '-', '*', '/'):
            ops = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}
            fops = {'+': 'FADD', '-': 'FSUB', '*': 'FMUL', '/': 'FDIV'}
            self.emit(fops[node.op] if needs_real else ops[node.op], f"operator {node.op}")
        elif node.op in ('.AND.', '.OR.'):
            self.emit({'.AND.': 'AND', '.OR.': 'OR'}[node.op], f"operator {node.op}")

    def visit_UnaryOp(self, node: UnaryOp):
        self.visit(node.operand)
        if node.op == '.NOT.':
            self.emit("NOT", "logical not")
        elif node.op == '-':
            op_type = self._infer_expr_type(node.operand)
            if op_type == 'REAL':
                self.emit("PUSHF 0.0", "push 0.0 for negation")
                self.emit("SWAP", "swap 0.0 and operand")
                self.emit("FSUB", "negate real")
            else:
                self.emit("PUSHI 0", "push 0 for negation")
                self.emit("SWAP", "swap 0 and operand")
                self.emit("SUB", "negate")
        elif node.op == '+':
            # Unary plus is a no-op
            pass

    def visit_ParenthesizedExpression(self, node: ParenthesizedExpression):
        self.visit(node.expr)

    def visit_ArrayAccess(self, node: ArrayAccess):
        self._push_var(node.name)
        self.visit(node.index)
        self.emit("PUSHI 1", "Fortran index is 1-based")
        self.emit("SUB", "convert to 0-based")
        self.emit("LOADN", f"load array element {node.name}")

    def visit_Variable(self, node: Variable):
        self._push_var(node.name)

    def visit_Literal(self, node: Literal):
        if node.kind == 'INTEGER':
            self.emit(f"PUSHI {node.value}", f"push integer {node.value}")
        elif node.kind == 'REAL':
            self.emit(f"PUSHF {node.value}", f"push real {node.value}")
        elif node.kind == 'STRING':
            self.emit(f"PUSHS \"{node.value}\"", f"push string '{node.value}'")
        elif node.kind == 'LOGICAL':
            self.emit(f"PUSHI {1 if node.value else 0}", f"push logical {node.value}")

    def visit_FunctionCall(self, node: FunctionCall):
        if node.name == 'MOD':
            self._needs_mod_helper = True
            self.emit("PUSHI 0", "reserve return slot for MOD")
            for arg in reversed(node.arguments):
                self.visit(arg)
            self.emit("PUSHA MOD", "call MOD helper")
            self.emit("CALL")
            if node.arguments:
                self.emit(f"POP {len(node.arguments)}", "clean up arguments")
            return

        self.emit("PUSHI 0", "reserve return slot")
        for arg in reversed(node.arguments):
            self.visit(arg)
        self.emit(f"PUSHA FUNC{node.name}", f"call function {node.name}")
        self.emit("CALL")
        if node.arguments:
            self.emit(f"POP {len(node.arguments)}", "clean up arguments")

    def visit_CallStatement(self, node: CallStatement):
        for arg in reversed(node.arguments):
            self.visit(arg)
        self.emit(f"PUSHA SUBR{node.name}", f"call subroutine {node.name}")
        self.emit("CALL")
        if node.arguments:
            self.emit(f"POP {len(node.arguments)}", "clean up arguments")

    def visit_FunctionDefinition(self, node: FunctionDefinition):
        func_label = f"FUNC{node.name}"
        self.emit(f"{func_label}:")
        self.func_types[node.name] = node.return_type

        old_var_map = self.var_map
        old_var_counter = self._var_counter
        old_in_function = self.in_function
        old_function_name = getattr(self, '_current_function_name', None)
        old_var_types = self.var_types
        old_num_locals = self._num_locals
        self.var_map = {}
        self._var_counter = 0
        self.in_function = True
        self._current_function_name = node.name
        self.var_types = {}
        self._num_locals = 0

        num_params = len(node.parameters)
        # Caller pushes: ret_slot, argN, ..., arg2, arg1, addr
        # After CALL (addr popped), fp points to the empty slot above arg1.
        # fp[-1] = arg1, fp[-2] = arg2, ..., fp[-num_params] = argN
        # fp[-(num_params+1)] = ret_slot
        for i, param in enumerate(node.parameters):
            self.var_map[param] = -(i + 1)  # -1, -2, -3, ...

        self.var_map[node.name] = -(num_params + 1)
        self.var_types[node.name] = node.return_type
        self._var_counter = 0  # locals start at fp[0]

        for decl in node.declarations:
            self.visit(decl)

        self._num_locals = self._var_counter
        if self._num_locals > 0:
            self.emit(f"PUSHN {self._num_locals}", f"allocate {self._num_locals} local(s)")

        for stmt in node.body:
            self.visit(stmt)

        if not node.body or not isinstance(node.body[-1], ReturnStatement):
            if self._num_locals > 0:
                self.emit(f"POP {self._num_locals}", f"clean up {self._num_locals} local(s)")
            self.emit("RETURN", f"implicit return from {node.name}")

        self.var_map = old_var_map
        self._var_counter = old_var_counter
        self.in_function = old_in_function
        self._current_function_name = old_function_name
        self.var_types = old_var_types
        self._num_locals = old_num_locals

    def visit_SubroutineDefinition(self, node: SubroutineDefinition):
        func_label = f"SUBR{node.name}"
        self.emit(f"{func_label}:", f"subroutine {node.name}")

        old_var_map = self.var_map
        old_var_counter = self._var_counter
        old_in_function = self.in_function
        old_var_types = self.var_types
        old_num_locals = self._num_locals
        self.var_map = {}
        self._var_counter = 0
        self.in_function = True
        self.var_types = {}
        self._num_locals = 0

        for i, param in enumerate(node.parameters):
            self.var_map[param] = -(i + 1)  # -1, -2, -3, ...

        for decl in node.declarations:
            self.visit(decl)

        self._num_locals = self._var_counter
        if self._num_locals > 0:
            self.emit(f"PUSHN {self._num_locals}", f"allocate {self._num_locals} local(s)")

        for stmt in node.body:
            self.visit(stmt)

        if not node.body or not isinstance(node.body[-1], ReturnStatement):
            if self._num_locals > 0:
                self.emit(f"POP {self._num_locals}", f"clean up {self._num_locals} local(s)")
            self.emit("RETURN", f"implicit return from {node.name}")

        self.var_map = old_var_map
        self._var_counter = old_var_counter
        self.in_function = old_in_function
        self.var_types = old_var_types
        self._num_locals = old_num_locals

    # ========================================================================
    # RUNTIME HELPERS
    # ========================================================================

    def _emit_mod_helper(self):
        """Emit MOD runtime helper: MOD(base, exp) -> base mod exp."""
        self.emit("MOD:", "MOD helper")
        self.emit("PUSHL -1", "base arg")
        self.emit("PUSHL -2", "exp arg")
        self.emit("MOD", "base mod exp")
        self.emit("STOREL -3", "store result in return slot")
        self.emit("RETURN", "return to caller")

    def _emit_pow_helper(self):
        """Emit POW runtime helper: POW(base, exp) -> base ** exp (integer only)."""
        loop_lbl = self.new_label()
        done_lbl = self.new_label()
        self.emit("POW:", "POW helper")
        self.emit("PUSHN 3", "allocate 3 locals: base_copy, exp_copy, result")
        self.emit("PUSHL -1", "base arg")
        self.emit("STOREL 0", "base_copy = base")
        self.emit("PUSHL -2", "exp arg")
        self.emit("STOREL 1", "exp_copy = exp")
        self.emit("PUSHI 1", "init result = 1")
        self.emit("STOREL 2", "result = 1")
        self.emit(f"{loop_lbl}:", "power loop")
        self.emit("PUSHL 1", "exp_copy")
        self.emit("PUSHI 0")
        self.emit("SUP", "exp_copy > 0?")
        self.emit(f"JZ {done_lbl}", "done if exp <= 0")
        self.emit("PUSHL 2", "result")
        self.emit("PUSHL 0", "base_copy")
        self.emit("MUL", "result *= base")
        self.emit("STOREL 2", "update result")
        self.emit("PUSHL 1", "exp_copy")
        self.emit("PUSHI 1")
        self.emit("SUB", "exp_copy -= 1")
        self.emit("STOREL 1", "update exp_copy")
        self.emit(f"JUMP {loop_lbl}", "repeat")
        self.emit(f"{done_lbl}:", "power done")
        self.emit("PUSHL 2", "result")
        self.emit("STOREL -3", "store result in return slot")
        self.emit("RETURN", "return to caller")
