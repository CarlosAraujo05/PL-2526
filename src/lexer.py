import ply.lex as lex
import re
import sys

#lexer.py - Analisador léxico para Fortran 77 usando PLY

# --- Definição dos tokens ---
keywords = [
    'PROGRAM', 'END', 'SUBROUTINE', 'FUNCTION', 'CALL', 'RETURN',
    'INTEGER', 'REAL', 'DOUBLE', 'COMPLEX', 'LOGICAL', 'CHARACTER',
    'DIMENSION', 'PARAMETER', 'DATA', 'COMMON', 'EQUIVALENCE', 'EXTERNAL', 'INTRINSIC',
    'IF', 'THEN', 'ELSE', 'ELSEIF', 'ENDIF', 'GOTO', 'ASSIGN', 'TO',
    'DO', 'CONTINUE', 'STOP', 'PAUSE',
    'READ', 'WRITE', 'PRINT', 'OPEN', 'CLOSE', 'INQUIRE', 'BACKSPACE', 'REWIND', 'ENDFILE',
    'FORMAT', 'SAVE', 'BLOCKDATA'
]
operators = [
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE', # .GT. , .LT. , etc.
    'AND', 'OR', 'NOT', 'XOR', 'EQV', 'NEQV', # .AND. , .OR. , etc.
    'TRUE', 'FALSE', # .TRUE. , .FALSE.
    'POW'
]
tokens = keywords + operators + ['ID','INTEGER_LIT', 'REAL_LIT', 'STRING_LIT','LABEL']

literals = ['+', '-', '*', '/', '(', ')', ',', '=', ':', '*']

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    # Check if the ID is actually a keyword
    if t.value.upper() in keywords:
        t.type = t.value.upper()
    return t

def t_INTEGER_LIT(t):
    r'\d+(?![.\dEDed])'  #digito sem decimais
    t.value = int(t.value)
    return t

def t_REAL_LIT(t):
    r'\d+\.\d+([EDed][-+]?\d+)?|\d+[EDed][-+]?\d+'
    t.value = float(t.value)
    return t

def t_STRING_LIT(t):
    r"'.*?'"
    t.value = t.value[1:-1]  # Remove the surrounding quotes
    return t


# Fortran logical and relational operators with dots
t_GT = r'\.GT\.'
t_LT = r'\.LT\.'
t_GE = r'\.GE\.'
t_LE = r'\.LE\.'
t_EQ = r'\.EQ\.'
t_NE = r'\.NE\.'
t_AND = r'\.AND\.'
t_OR = r'\.OR\.'
t_NOT = r'\.NOT\.'
t_TRUE = r'\.TRUE\.'
t_FALSE = r'\.FALSE\.'
t_POW = r'\*\*'

# Comments in Fortran 77 start with 'C', 'c', or '*' in the first column
def t_COMMENT(t):
    r'(^[Cc*].*)|(!.*)'
    t.lexer.lineno += 1
    return None

t_ignore = ' \t'

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
class LexerError(Exception):
    pass
def t_error(t):
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
