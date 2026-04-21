import ply.lex as lex
import re
import sys

#lexer.py - Analisador léxico para Fortran 77 usando PLY

# --- Definição dos tokens ---
# Keywords from AGENTS.md specification (lines 48-49)
keywords = [
    'PROGRAM', 'END',
    'INTEGER', 'LOGICAL', 'REAL', 'CHARACTER',
    'DIMENSION', 'PARAMETER',
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

tokens = keywords + operators + ['ID', 'INTEGER_LIT', 'REAL_LIT', 'STRING_LIT', 'LABEL']

literals = ['+', '-', '*', '/', '(', ')', ',', '=', ':', '*']

# --- Keyword token definitions (one per keyword, case-insensitive via reflags) ---
def t_PROGRAM(t):
    r'PROGRAM'
    t.value = t.value.upper()
    return t

def t_END(t):
    r'END'
    t.value = t.value.upper()
    return t

def t_FUNCTION(t):
    r'FUNCTION'
    t.value = t.value.upper()
    return t

def t_RETURN(t):
    r'RETURN'
    t.value = t.value.upper()
    return t

def t_SUBROUTINE(t):
    r'SUBROUTINE'
    t.value = t.value.upper()
    return t

def t_CALL(t):
    r'CALL'
    t.value = t.value.upper()
    return t

def t_INTEGER(t):
    r'INTEGER'
    t.value = t.value.upper()
    return t

def t_REAL(t):
    r'REAL'
    t.value = t.value.upper()
    return t

def t_LOGICAL(t):
    r'LOGICAL'
    t.value = t.value.upper()
    return t

def t_DIMENSION(t):
    r'DIMENSION'
    t.value = t.value.upper()
    return t

def t_CHARACTER(t):
    r'CHARACTER'
    t.value = t.value.upper()
    return t

def t_PARAMETER(t):
    r'PARAMETER'
    t.value = t.value.upper()
    return t

def t_IF(t):
    r'IF'
    t.value = t.value.upper()
    return t

def t_THEN(t):
    r'THEN'
    t.value = t.value.upper()
    return t

def t_ELSE(t):
    r'ELSE'
    t.value = t.value.upper()
    return t

def t_ELSEIF(t):
    r'ELSEIF'
    t.value = t.value.upper()
    return t

def t_ENDIF(t):
    r'ENDIF'
    t.value = t.value.upper()
    return t

def t_GOTO(t):
    r'GOTO'
    t.value = t.value.upper()
    return t

def t_DO(t):
    r'DO'
    t.value = t.value.upper()
    return t

def t_CONTINUE(t):
    r'CONTINUE'
    t.value = t.value.upper()
    return t

def t_READ(t):
    r'READ'
    t.value = t.value.upper()
    return t

def t_PRINT(t):
    r'PRINT'
    t.value = t.value.upper()
    return t

# --- Comments (must come before t_ID to have priority) ---
# Free format Fortran: only ! comments are supported
def t_COMMENT(t):
    r'!.*'
    t.lexer.lineno += t.value.count('\n')
    return None

# --- Identifier (must come after all keywords and comments) ---
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]{0,5}'
    t.value = t.value.upper()
    return t

# --- Numeric and string literals ---
def t_REAL_LIT(t):
    r'\d+\.\d+([EDed][-+]?\d+)?|\d+[EDed][-+]?\d+'
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
    raise LexerError(f"Caractere ilegal: {t.value[0]} na linha {t.lineno}")

# --- Lexer Factory ---

def build_lexer(debug=False):
    """Build and return the lexer."""
    return lex.lex(reflags=re.IGNORECASE | re.MULTILINE, debug=debug)


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} arquivo.for")
        return

    lexer = build_lexer()
    try:
        with open(sys.argv[1], 'r') as file:
            data = file.read()
            
        lexer.input(data)
        
        # Loop para imprimir os tokens gerados
        for tok in lexer:
            print(tok)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{sys.argv[1]}' não foi encontrado.")
    except PermissionError:
        print(f"Erro: Permissão negada para ler o arquivo '{sys.argv[1]}'.")
    except LexerError as e:
        print(f"Erro Léxico: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()
