# AGENTS.md — Fortran 77 Compiler (PL2026)

## Project Overview

This project implements a compiler for **Fortran 77 (ANSI X3.9-1978)** targeting the course-provided
Virtual Machine (VM). The compiler is written in **Python 3** using the **PLY** library (`ply.lex` +
`ply.yacc`). The minimum passing deliverable (10/20) is a working pipeline from source to VM code.
Higher grades require an intermediate representation (IR), optimisation passes, and subprogram support.

---

## Repository Layout

```
.
├── src/
│   ├── lexer.py          # Lexical analysis — tokenises Fortran 77 source
│   ├── parser.py         # Syntactic + semantic analysis — builds the AST
│   ├── ast_nodes.py      # AST node class hierarchy
│   ├── symbol_table.py   # Symbol table implementation
│   └── codegen.py        # VM code emitter
├── tests/
│   ├── hello.for
│   ├── fatorial.for
│   ├── primo.for
│   ├── somaarr.for
│   └── conversor.for
├── docs/
│   └── main.typ / main.md   # Technical report (≤ 10 pages)
└── AGENTS.md
```

Respect this layout. Do not merge unrelated concerns into a single file.

---

## Module Responsibilities

### `lexer.py` — Lexical Analysis

**Input:** Raw Fortran 77 source text.  
**Output:** Token stream consumed by the parser.

#### Token categories to implement

| Category | Examples |
|---|---|
| Keywords (only these)| `PROGRAM`, `END`, `INTEGER`, `LOGICAL`, `REAL`, `PRINT`, `READ`, `DO`, `CONTINUE`, `IF`, `THEN`, `ELSE`,`ELSEIF`, `ENDIF`, `GOTO`,|
| |`FUNCTION`, `RETURN`, `DIMENSION`, `SUBROUTINE`, `CALL`, `PARAMETER`, `CHARACTER` |
| Logical literals | `.TRUE.`, `.FALSE.` |
| Relational operators | `.EQ.`, `.NE.`, `.LT.`, `.LE.`, `.GT.`, `.GE.` |
| Logical operators | `.AND.`, `.OR.`, `.NOT.` |
| Arithmetic operators | `+`, `-`, `*`, `/`, `**` |
| Identifiers | Up to 6 alphanumeric chars, starting with a letter |
| Integer literals | Sequence of digits |
| Real literals | Digits with decimal point and/or exponent (`E`) |
| String literals | Single-quoted character sequences |
| Punctuation | `(`, `)`, `,`, `=`, `:` |
| Labels | Integer in columns 1–5 (fixed format) or inline (free format) |

#### Format decision — make it explicit in this file

**Chosen format:  `Free`** 
- **Fixed format (columns 1–5 label, column 6 continuation, columns 7–72 statement):** requires the
  lexer to strip and interpret column positions. Use `t_newline` and track line offsets.
- **Free format:** simpler to implement; treat the source as plain text. Recommended if time is limited.

Whichever is chosen, document it in the report. The lexer **must not** silently accept both.

#### PLY-specific rules
use PLY's conventions for token definitions as much as possible. Don't write hardcoded python code to match tokens; instead, leverage PLY's regex-based token definitions.
```python
# Define tokens like this with uppercase names and raw docstrings for regexes. The docstring is the regex pattern.

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]{0,5}'
    t.value = t.value.upper()   # Fortran is case-insensitive; normalise early  all identifiers and keywords to **uppercase** in the lexer so the parser can assume it.
    return t
```

---

### `ast_nodes.py` — AST Node Hierarchy

Define a clean class hierarchy; do **not** use raw tuples or dicts as AST nodes.

```python
@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    name: str
    declarations: list
    body: list

@dataclass
class DoLoop(Node):
    label: int
    var: str
    start: Node
    stop: Node
    step: Node | None
    body: list

@dataclass
class IfThenElse(Node):
    condition: Node
    then_body: list
    else_body: list   # empty list if no ELSE branch

@dataclass
class GotoStmt(Node):
    label: int

@dataclass
class Assignment(Node):
    target: Node   # Var or ArrayRef
    value: Node

# ... etc.
```

Every node must store a `lineno` field for error reporting.

---

### `symbol_table.py` — Symbol Table

Implement a scoped symbol table. At minimum, each entry must hold:

```python
@dataclass
class Symbol:
    name: str
    kind: str          # 'variable', 'array', 'function', 'subroutine', 'parameter'
    dtype: str         # 'INTEGER', 'REAL', 'LOGICAL', 'CHARACTER'
    dimensions: list   # empty for scalars; list of (lower, upper) for arrays
    lineno: int        # declaration line, for error messages
```

Provide `declare(symbol)`, `lookup(name)`, `enter_scope()`, and `exit_scope()` methods.
Raise a descriptive `SemanticError` (not a bare `Exception`) on conflicts or undeclared usage.

---

### `parser.py` — Syntactic and Semantic Analysis

**Input:** Token stream from `lexer.py`.  
**Output:** AST root node and a populated symbol table.

#### Grammar conventions

- Use PLY's `p_` function naming convention strictly.
- Every grammar rule must have a docstring that is the BNF/EBNF production.
- Group related rules together (declarations, expressions, statements, control flow).

```python
#like this, with clear docstrings and consistent naming:
def p_program(p):
    '''
    program : PROGRAM ID declarations body END
    '''
    # Do semantic checks, build AST node, etc.
```

#### Semantic checks to perform during parsing

These must raise a `SemanticError` with a meaningful message and line number:

1. **Variable declared before use** — look up every `ID` reference in the symbol table.
2. **No duplicate declarations** — `declare()` must detect re-declarations in the same scope.
3. **Type compatibility in assignments** — assigning `REAL` to `INTEGER` requires implicit truncation
   (Fortran 77 allows it); assigning `LOGICAL` to `INTEGER` is illegal.
4. **DO loop label consistency** — the label on `DO <label> var = ...` must match the label of the
   closing `CONTINUE` statement. Track open loops in a stack.
5. **Array bounds** — subscript count must match the declaration's dimension count.
6. **GOTO targets** — collect all `GOTO <label>` calls and verify the labels exist after the full
   program is parsed (two-pass or forward-reference table).
7. **FUNCTION return type** — the function name must be assigned at least once inside the function body.

---

### `codegen.py` — VM Code Generation

**Input:** AST root.  
**Output:** String of VM assembly instructions written to stdout or a `.vm` file.

Study the VM instruction set provided by the professor before implementing this module.
Map each AST node type to one or more VM instructions. Use a `CodeGen` class with an `emit(instr)`
method that appends to an internal list; flush to a file at the end.

#### Suggested mapping (adapt to your VM's actual ISA)

| Fortran construct | VM pattern |
|---|---|
| Integer/Real literal | `PUSHI n` / `PUSHF f` |
| Variable read | `PUSHG addr` or `PUSHL addr` |
| Assignment | evaluate RHS, then `STOREG addr` / `STOREL addr` |
| Arithmetic `+` | `ADD` |
| `IF condition THEN ... ELSE ... ENDIF` | evaluate cond, `JZ else_label`, then-block, `JUMP end_label`, `else_label:`, else-block, `end_label:` |
| `DO label var = s, e, step` | init var, `loop_label:`, check condition, `JZ end_label`, body, increment, `JUMP loop_label`, `end_label:` |
| `GOTO label` | `JUMP vm_label` |
| `PRINT *` | push each arg, `WRITEI` / `WRITEF` / `WRITES` per type |
| `READ *` | `READ`, store result |
| `CALL sub(args)` | push args, `PUSHA sub_label`, `CALL`, clean up stack |

Keep a **label counter** (`self._label_counter`) to generate unique VM labels (`L0`, `L1`, …).

---
#### Minimum optimisation passes for valorização

1. **Constant folding** — evaluate `2 + 3` at compile time.
2. **Dead code elimination** — remove assignments whose result is never read.
3. **Common subexpression elimination** — reuse already-computed temporaries.
4. **Loop-invariant code motion** (global, harder) — move invariant computations outside DO loops.

Implement passes as separate functions; do not interleave them with code generation.

---

## Entry Point

`src/main.py` (create this) should wire the pipeline:

```python
# Usage: python3 src/main.py <source.for>
import sys
from lexer import build_lexer
from parser import build_parser
from codegen import CodeGen

def main():
    source = open(sys.argv[1]).read()
    lexer  = build_lexer()
    parser = build_parser()
    ast    = parser.parse(source, lexer=lexer)
    cg     = CodeGen()
    cg.generate(ast)
    print(cg.output())

if __name__ == '__main__':
    main()
```

---

## Workflow Commands

```bash
# Run the full pipeline on a Fortran source file
python3 src/main.py tests/fatorial.for

# Pipe output directly into the VM (adjust vm command to match your setup)
python3 src/main.py tests/fatorial.for | ./vm

# Debug the lexer in isolation
python3 src/lexer.py  tests/file.for
# Debug the parser / inspect AST
python3 src/parser.py  tests/file.for
# Run all tests (once a test harness exists)
python3 -m pytest tests/

# Compile the technical report into PDF using Typst
typst compile docs/main.typ docs/PL-G52.pdf    
```

---

## Error Handling Conventions

- **Lexical error:** print `Lexical error at line <n>: unexpected character '<c>'` and continue tokenising.
- **Syntax error:** PLY calls `p_error(p)`; print `Syntax error at line <n>: unexpected token '<t>'` and
  attempt recovery with `parser.restart()`.
- **Semantic error:** raise `SemanticError(message, lineno)` and catch it in `main.py` to print a clean
  message and exit with code 1.
- **Never** let the compiler crash with a raw Python traceback on valid or mildly invalid Fortran input.

---

## Code Quality Standards

- Every public function and class must have a **docstring**.
- Keep functions under 40 lines. If a function is growing, extract a helper.
- No magic numbers — use named constants or enums for opcodes, types, and error codes.
- The grammar file (`parser.py`) must be readable: group rules, add comments for non-obvious productions.
- Run `pylint src/` before committing; target a score ≥ 8/10.

---

## Evaluation Criteria (from the project sheet)

| Criterion | What to demonstrate |
|---|---|
| **Correctness** | All five example programs compile and produce correct output on the VM |
| **Structure** | Modular, well-documented code; each module has a single responsibility |
| **Functionality** | Full coverage of required Fortran 77 constructs |
| **Efficiency** | Generated VM code is not naively redundant (at minimum, no dead pushes) |
| **Defence** | Every group member can explain every design decision and line of code |

The defence grade is **individual** — the professor grades your understanding, not just the code.
Ensure all members can walk through the lexer, parser, and codegen independently.

---

## Agent Guidance

When working on tasks in this repository:

1. **Before touching any file**, identify which module layer the task belongs to (lexer / parser / codegen / IR / tests) and edit only that module.
2. **After any change to the grammar**, re-run all five test programs end-to-end to detect regressions.
3. **Do not** add PLY debug output (`debug=True`, `errorlog`) in committed code — gate it behind a `--debug` flag.
4. **Prefer explicit over implicit** — Fortran implicit typing (undeclared variables starting with I–N are INTEGER) is a known pitfall; decide whether to support it and document the decision.
5. **Label management** — Fortran labels are global to a program unit. Maintain a single `label_map: dict[int, str]` that maps Fortran statement labels to VM jump targets.
6. When generating code for `IF` / `DO` / `GOTO`, always resolve labels **after** the full AST is built, not inline during parsing, to handle forward references cleanly.
