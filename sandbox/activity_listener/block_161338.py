",
                         SESSION_ID, None, thinking=False, search=False)
    except: pass'''
src = src.replace(old_chat, new_chat)
p.write_text(src)

print("Panel and listener now call stream_completion without redirect_stdout.")
PYEOF