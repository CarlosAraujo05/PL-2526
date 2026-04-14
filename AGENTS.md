# AGENTS.md - Fortran 77 Compiler Project (PL2026)

## 🎯 Project Overview
[cite_start]The goal is to develop a compiler for the **Fortran 77 standard (ANSI X3.9-1978)** that targets a specific Virtual Machine (VM)[cite: 7, 8]. [cite_start]The project is implemented in **Python** using the **PLY (Python Lex-Yacc)** library[cite: 13, 18, 134].

## 🛠️ Technical Stack
- [cite_start]**Language:** Python 3.x [cite: 134]
- [cite_start]**Tools:** `ply.lex` (Lexical Analysis) and `ply.yacc` (Syntactic Analysis) 
- [cite_start]**Target:** Provided Virtual Machine (VM) code [cite: 8, 137]
- [cite_start]**Documentation:** LaTeX or Markdown [cite: 135]

## 📜 Coding Standards & Rules
### 1. Lexical Analysis (`lexer.py`)
- [cite_start]Define tokens for keywords: `PROGRAM`, `INTEGER`, `REAL`, `LOGICAL`, `IF`, `DO`, `GOTO`, `READ`, `PRINT`, etc[cite: 14, 122].
- [cite_start]Handle Fortran 77 specific operators (e.g., `.EQ.`, `.LE.`, `.AND.`, `.TRUE.`)[cite: 14, 56, 57].
- [cite_start]**Decision Required:** The group must choose between fixed-column format or free-form; notify the user if this choice is not yet clear[cite: 15].

### 2. Syntactic & Semantic Analysis (`parser.py`)
- [cite_start]Validate the grammatical structure of the code[cite: 17].
- [cite_start]**Semantic Checks:** Validate data types, variable declarations, and ensure `DO` loop labels match their corresponding `CONTINUE` commands.

### 3. Code Generation
- [cite_start]**Standard Path:** Convert Fortran directly to VM code for a base grade (10/20)[cite: 10, 22].
- [cite_start]**Valorização (High Grade) Path:** Generate an intermediate representation (IR), apply local/global optimizations, and then convert the IR to VM code[cite: 24, 28, 29].
- [cite_start]Support subprograms (`SUBROUTINE` and `FUNCTION`) for extra credit[cite: 124].

## 🏃 Workflow Commands
- **Lex/Yacc Debugging:** Use `python3 parser.py < input.f` to test the grammar.
- [cite_start]**Testing:** Run the suite of test programs (e.g., Hello World, Factorial, Prime) found in the `/tests` directory[cite: 31, 32].
- [cite_start]**Formatting:** Ensure the report does not exceed 10 pages[cite: 135].

## 📅 Key Deadlines
- [cite_start]**Group Registration:** April 5, 2026[cite: 130].
- [cite_start]**Final Submission:** May 17, 2026, at 23:59 (GitHub commit)[cite: 132].
- [cite_start]**Project Defense:** Week of June 1–5, 2026[cite: 138].

## ⚠️ Important Notes
- [cite_start]All code must be submitted via the designated GitHub repository[cite: 127].
- [cite_start]The generated VM code must be efficient and minimally optimized for better evaluation[cite: 143].
- [cite_start]Ensure every commit is meaningful, as the last commit before the deadline determines the submission[cite: 132].
