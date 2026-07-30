# validate_ast.py
import ast, sys

for path in sys.argv[1:]:
    try:
        with open(path, "r") as f:
            src = f.read()
        ast.parse(src, filename=path)
    except SyntaxError as e:
        print(f"❌ AST parse failed in {path}: {e}")
        sys.exit(1)
    else:
        print(f"✅ AST OK: {path}")
