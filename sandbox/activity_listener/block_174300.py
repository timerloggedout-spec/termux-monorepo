")
                except Exception as send_err:
                    with open(HOME/'archwiz/autoexec.log','a') as f:
                        f.write(f"[Send failed: {send_err}]\\n")'''

src = src.replace(old, new)
p.write_text(src)
print("Listener now sends results to this chat in real time.")
PYEOF