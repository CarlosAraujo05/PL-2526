import ply.lex as lex
import re
import sys

#lexer.py - Analisador léxico para Fortran 77 usando PLY

# --- Fixed-Format Preprocessor ---
class FortranPreprocessor:
    """Handles Fortran 77 fixed-format to normalized text conversion.
    
    Fortran 77 fixed format:
    - Columns 1-5: Statement labels
    - Column 6: Continuation marker (C/*/! = comment, digit = continuation)
    - Columns 7-72: Statement text
    - Columns 73-80: Card ID (ignored)
    """
    
    def __init__(self, source_text):
        self.source_lines = source_text.split('\n')
        self.continuation_buffer = ''
    
    def preprocess(self):
        """Generator yielding normalized statement lines."""
        for line in self.source_lines:
            # Pad line to 72 chars in case of trailing space removal
            line = line.ljust(72)
            
            label_part = line[0:5].strip()       # Columns 1-5
            cont_char = line[5]                 # Column 6
            statement_part = line[6:72]         # Columns 7-72
            
            # Skip comment lines (C, c, *, or ! in column 6)
            if cont_char in ('C', 'c', '*', '!'):
                self.continuation_buffer = ''
                continue
            
            # Handle continuation lines (digit 0-9 in column 6)
            if cont_char.isdigit():
                self.continuation_buffer += ' ' + statement_part
                continue
            
            # Emit any pending continuation
            if self.continuation_buffer:
                yield self.continuation_buffer.strip()
                self.continuation_buffer = ''
            
            # Regular statement - prepend label if present
            statement = statement_part.strip()
            if statement:
                if label_part:
                    yield f"{label_part} {statement}"
                else:
                    yield statement
        
        # Emit final continuation buffer
        if self.continuation_buffer:
            yield self.continuation_buffer.strip()


# --- Definição dos tokens ---
# Keywords from AGENTS.md specification (lines 48-49)
keywords = [
    'PROGRAM', 'END',
    'INTEGER', 'LOGICAL', 'REAL', 'CHARACTER', 'PARAMETER',
    'IF', 'THEN', 'ELSE', 'ELSEIF', 'ENDIF',
    'DO', 'CONTINUE', 'GOTO',
    'READ', 'PRINT',
    'FUNCTION', 'SUBROUTINE', 'CALL', 'RETURN',
]

# Logical and relational operators
operators = [
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'AND', 'OR', 'NOT',
    'TRUE', 'FALSE',
    'POW'
]

tokens = keywords + operators + ['ID', 'INTEGER_LIT', 'REAL_LIT', 'STRING_LIT']

literals = ['+', '-', '*', '/', '(', ')', ',', '=', ':']

# Map identifier strings to their keyword token names.
# This guarantees that identifiers which are prefixes of keywords
# (e.g. 'ENDI', 'REALX') are still matched correctly as IDs.
RESERVED = {kw: kw for kw in keywords}

# --- Identifier (must come before any keyword function so it gets priority) ---
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]*'
    t.value = t.value.upper()
    # Check reserved words before truncating so that 7-char keywords
    # (e.g. PROGRAM) are recognised correctly.
    t.type = RESERVED.get(t.value, 'ID')
    # Fortran 77 limit: truncate identifiers to 6 chars (only for IDs)
    if t.type == 'ID' and len(t.value) > 6:
        t.value = t.value[:6]
    return t

# --- Comments ---
def t_COMMENT(t):
    r'!.*'
    t.lexer.lineno += t.value.count('\n')
    return None

# --- Numeric and string literals ---
def t_REAL_LIT(t):
    r'(\d+\.\d*|\d*\.\d+)([eEdD][-+]?\d+)?|\d+[eEdD][-+]?\d+'
    t.value = float(t.value)
    return t

def t_INTEGER_LIT(t):
    r'\d+(?![.\dEDed])'
    t.value = int(t.value)
    return t

def t_STRING_LIT(t):
    r"'.*?'"
    t.value = t.value[1:-1]  # Remove surrounding quotes
    return t

# --- Fortran logical and relational operators with dots ---
def t_GT(t):
    r'\.GT\.'
    return t

def t_LT(t):
    r'\.LT\.'
    return t

def t_GE(t):
    r'\.GE\.'
    return t

def t_LE(t):
    r'\.LE\.'
    return t

def t_EQ(t):
    r'\.EQ\.'
    return t

def t_NE(t):
    r'\.NE\.'
    return t

def t_AND(t):
    r'\.AND\.'
    return t

def t_OR(t):
    r'\.OR\.'
    return t

def t_NOT(t):
    r'\.NOT\.'
    return t

def t_TRUE(t):
    r'\.TRUE\.'
    return t

def t_FALSE(t):
    r'\.FALSE\.'
    return t

def t_POW(t):
    r'\*\*'
    return t

t_ignore = ' \t'

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Error handling ---
class LexerError(Exception):
    """Exception raised for lexical errors."""
    pass

def t_error(t):
    """Handle illegal characters."""
    raise LexerError(f"Lexical error at line {t.lineno}: unexpected character '{t.value[0]}'")

# --- Lexer Factory ---

def build_lexer(debug=False, source_text=None):
    """Build and return the lexer.
    
    Args:
        debug: Enable PLY debugging
        source_text: Raw Fortran 77 source (fixed-format).
                    If provided, preprocesses to normalized form.
    """
    lexer = lex.lex(reflags=re.IGNORECASE | re.MULTILINE, debug=debug)
    
    if source_text is not None:
        preprocessor = FortranPreprocessor(source_text)
        normalized = '\n'.join(preprocessor.preprocess())
        lexer.input(normalized)
    
    return lexer


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file.for>")
        return

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            data = file.read()
        
        # Use preprocessor to handle fixed-format source
        lexer = build_lexer(source_text=data)
        
        # Print generated tokens
        for tok in lexer:
            print(tok)
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
    except PermissionError:
        print(f"Error: Permission denied reading file '{sys.argv[1]}'.")
    except LexerError as e:
        print(f"Lexer error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
