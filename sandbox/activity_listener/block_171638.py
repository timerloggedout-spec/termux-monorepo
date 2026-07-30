"], timeout=30)
    except: pass'''
src = src.replace(old2, new2)
p.write_text(src)

print("Panel and listener now use deepapi.py (Node bridge).")
PYEOF