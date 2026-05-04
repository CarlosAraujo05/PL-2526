from lexer import build_lexer, LexerError
from parser import build_parser, SyntaxError, SemanticError, validate_goto_labels
from optimizer import Optimizer
from codegen import CodeGen
import sys
import os

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

            # Validate GOTO labels after parsing (allows forward references)
            validate_goto_labels(parser)
            # Optimize AST
            opt = Optimizer()
            ast = opt.optimize(ast)
            
            # Generate Code
            cg = CodeGen()
            cg.generate(ast)
            
            output = cg.output()
            
            # Write to .vm file
            base_name = os.path.splitext(source_file)[0]
            with open(base_name + '.vm', 'w') as f:
                f.write(output)
            print(f"Compilation successful. Output written to {base_name}.vm")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except LexerError as e:
        print(f"Lexer Error: {e}")
        return 1
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        return 1
    except SemanticError as e:
        print(f"Semantic Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
