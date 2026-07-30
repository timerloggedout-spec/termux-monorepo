python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/archwiz.py'
src = p.read_text()

# Replace the [11] handler to offer restoring from staging
old_11 = """        elif choice == '11':
            target = input(f"{C}File to restore: {N}").strip()
            if target:
                subprocess.run(['python3', os.path.expanduser('~/archwiz/restore_version.py'), target])"""

new_11 = """        elif choice == '11':
            # Check if there are staged blocks from forensic toolchain
            staging = os.path.expanduser('~/archwiz/staging_blocks.json')
            if os.path.exists(staging):
                print(f"{Y}Staged blocks from forensic toolchain:{N}")
                import json as _json
                blocks = _json.loads(open(staging).read_text())
                for i, b in enumerate(blocks[-5:]):
                    print(f"  {G}{i}{N}: {b.get('search_term','?')} #{b.get('index','?')} ({b.get('session','?')[:16]}...)")
                use_staged = input(f"{C}Restore from staged block? Enter number or 'n' for manual path: {N}").strip()
                if use_staged.isdigit() and 0 <= int(use_staged) < len(blocks):
                    b = blocks[int(use_staged)]
                    target = input(f"{C}Target file path (e.g., deepcli/deepcli/core.py): {N}").strip()
                    if target:
                        # Write the staged code directly to the target file
                        import pathlib as _pl
                        dest = _pl.Path.home() / target
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        # Backup original
                        if dest.exists():
                            _pl.Path(str(dest) + '.bak').write_text(dest.read_text())
                        dest.write_text(b['code'])
                        print(f"{G}✅ Restored staged block to {target}. Backup saved to {target}.bak{N}")
                    return
            target = input(f"{C}File to restore (relative path): {N}").strip()
            if target:
                subprocess.run(['python3', os.path.expanduser('~/archwiz/restore_version.py'), target])"""

src = src.replace(old_11, new_11)
p.write_text(src)
print("[11] now integrates with staged forensic blocks.")
PYEOF