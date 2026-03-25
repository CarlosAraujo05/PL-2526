import ply.lex as lex
import sys
tokens = [
    'PROGRAM', 'END', 'INTEGER', 'REAL', 'DO', 'CONTINUE', 'IF', 'THEN', 'GOTO', 'RETURN', 'MOD',
    'ID', 'NUMBER',
    'GT', 'LT', 'GE', 'LE', 'EQ', 'NE',
    'DOT'
]

literals = ['+', '-', '*', '/', '(', ')', ',', '=', ':']

t_ignore = ' \t'
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t
def t_error(t):
    print(f"Illegal character: {t.value[0]}")
    t.lexer.skip(1)
def main():
    argv = sys.argv
    lexer = lex.lex()
    with open(argv[1]) as file:
        lexer.input(file)
    print()
if __name__ == "__main__":
    main()
