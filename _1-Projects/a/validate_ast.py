import ast, sys
ok = True
for path in sys.argv[1:]:
    try:
        with open(path, "r") as f:
            src = f.read()
        ast.parse(src, filename=path)
        print(f"✅ AST OK: {path}")
    except SyntaxError as e:
        print(f"❌ AST parse failed in {path}: {e}")
        ok = False
if not ok:
    sys.exit(1)
