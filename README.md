# PL-2526 - Fortran 77 Compiler

A compiler for **Fortran 77 (ANSI X3.9-1978)** targeting a course-provided Virtual Machine, built with Python and PLY.

## Project Structure

```
.
├── src/
│   ├── lexer.py          # Lexical analysis (PLY)
│   ├── parser.py         # Syntactic + semantic analysis
│   ├── ast_nodes.py      # AST node definitions
│   ├── symbol_table.py   # Symbol table implementation
│   └── codegen.py        # VM code generation
├── tests/
│   ├── hello.for         # Simple program
│   ├── fatorial.for      # DO loops
│   ├── primo.for         # IF/GOTO control flow
│   ├── somaarr.for       # 1D arrays
│   └── conversor.for    # Functions/subroutines
├── docs/
│   └── CFG.md           # Grammar specification (BNF)
└── README.md
```

## Building

```bash
python3 src/main.py tests/hello.for
# This generates tests/hello.vm
```

## Testing

Run the automated test suite against the 5 included Fortran programs:
```bash
python3 -m pytest tests/test_compiler.py
```

## Design Decisions

### Format: Fixed-Format Fortran 77
- Columns 1-5: Statement labels
- Column 6: Continuation marker
- Columns 7-72: Statement text
- Preprocessed by `FortranPreprocessor` before tokenization

### Keyword Normalization
All keywords and identifiers normalized to **uppercase** in the lexer for case-insensitivity.

### Arrays: 1D Only
Removed `DIMENSION` keyword and multidimensional arrays. Arrays declared inline:

```fortran
INTEGER NUMS(10)  ! 1D array only
```

### Semantic Analysis: Distributed
Semantic checks integrated directly into parser rules using `symbol_table.py`:

| Rule | Check |
|------|-------|
| `p_type_declaration` | Declares symbols (`declare()`) |
| `p_assignment_statement` | Verifies target exists (`lookup()`) |
| `p_array_access` | Verifies array subscript (`check_array_access()`) |
| `p_do_loop` | Verifies loop variable is scalar (`check_scalar_access()`) |

### Grammar
See `src/CFG.md` for complete BNF specification. Key features:
- Operator precedence encoded in grammar (LL(1) compatible)
- DO loops with label matching (`DO 10 I = 1,N ... 10 CONTINUE`)
- IF/THEN/ELSEIF/ENDIF blocks
- Subprograms: FUNCTION, SUBROUTINE, CALL

## Supported Constructs

### Declarations
- `INTEGER`, `REAL`, `LOGICAL`, `CHARACTER`
- `CHARACTER*N` for character strings
- `PARAMETER (NAME = value)`

### Statements
- Assignment: `VAR = expression`
- Arrays: `ARR(I) = value`
- DO loops: `DO 10 I = 1, N ... 10 CONTINUE`
- IF/THEN/ELSEIF/ENDIF
- GOTO label
- READ/PRINT
- CALL subroutine
- RETURN

### Expressions
- Arithmetic: `+`, `-`, `*`, `/`, `**`
- Relational: `.LT.`, `.LE.`, `.GT.`, `.GE.`, `.EQ.`, `.NE.`
- Logical: `.AND.`, `.OR.`, `.NOT.`, `.TRUE.`, `.FALSE.`

## Test Results

All 5 test programs parse successfully with semantic verification:
- `hello.for` - Basic I/O
- `fatorial.for` - DO loops and arithmetic
- `primo.for` - IF/GOTO control flow
- `somaarr.for` - 1D arrays
- `conversor.for` - Functions

## Dependencies

- Python 3.10+
- PLY (pip install ply)

## References

- Fortran 77 Standard: ISO/IEC 1539:1980
- PLY: https://www.dabeaz.com/ply/