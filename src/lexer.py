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
tokens = keywords + operators + ['ID', 'NUMBER', 'STRING', 'LABEL', 'IDENTATION']

literals = ['+', '-', '*', '/', '(', ')', ',', '=', ':', '*']

def t_LABEL(t):
    r'^[ ]{0,5}\d+' # Fortran 77 labels occur in columns 1-5
    t.value = int(t.value)
    return t
def t_IDENTATION(t):
    r'^[ ]{6}' # Capture leading whitespace for indentation
    return t    

def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    # Check if the ID is actually a keyword
    if t.value.upper() in keywords:
        t.type = t.value.upper()
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([EDed][-+]?\d+)?'
    # This regex handles integers, reals, and scientific notation
    t.value = float(t.value) if '.' in t.value or 'E' in t.value.upper() else int(t.value)
    return t

def t_STRING(t):
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

t_ignore = '\t'
def t_WHITESPACE(t):
    r'[ \r]+'
    return None

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal: {t.value[0]} na linha {t.lineno}")
    t.lexer.skip(1)

# --- Execução ---

def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]}.py arquivo.for")
        return

    lexer = lex.lex(reflags=re.IGNORECASE| re.MULTILINE)
    
    with open(sys.argv[1], 'r') as file:
        data = file.read()
        lexer.input(data)
        
        # Loop para imprimir os tokens gerados
        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok)

if __name__ == "__main__":
    main()
