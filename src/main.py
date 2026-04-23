from lexer import build_lexer, LexerError
from parser import build_parser, SyntaxError ,SemanticError
import sys




def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file.for>")
        return 1

    source_file = sys.argv[1]
    try:
        with open(source_file, 'r') as f:
            source_code = f.read()
            lexer = build_lexer(source_text=source_code)
            parser = build_parser()
            ast = parser.parse(lexer=lexer)

            if ast is not None:
                print("Parsing successful!")
                print(ast)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except LexerError as e:
        print(f"Lexer Error: {e}")
        return 1
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
    except SemanticError as e:
        print(f"Semantic Error: {e}")

if __name__ == "__main__":
    main()
