python3 << 'PYEOF'
import pathlib
p = pathlib.Path.home() / 'archwiz/archwiz.py'
src = p.read_text()
# Replace the placeholder with a real call to the profile manager
old = '        elif choice == \'7\':\n            print(f"{Y}Profile management coming soon.{N}")'
new = '''        elif choice == '7':
            # Launch the interactive profile manager
            import readline, json, shutil
            prof_dir = os.path.expanduser('~/.config/llm_map/profiles')
            if not os.path.isdir(prof_dir):
                print(f"{Y}No profiles directory found.{N}")
            else:
                profiles = sorted(f.replace('.json', '') for f in os.listdir(prof_dir) if f.endswith('.json'))
                print(f"{Y}Available profiles:{N}")
                for p in profiles:
                    print(f"  {G}{p}{N}")
                choice = input(f"{C}Switch to profile (name, 'new', 'edit', or Enter to cancel): {N}").strip()
                if not choice or choice.lower() in ('back', 'cancel', 'q'):
                    pass
                elif choice == 'new':
                    name = input("Profile name: ").strip()
                    if name:
                        inc = input("Include dirs (comma): ").strip()
                        exc = input("Exclude dirs (optional, comma): ").strip()
                        cmd = ['python3', os.path.expanduser('~/workspace/llm_map/llm_mapper_pro.py'), 'profile-create', name, '--include', inc]
                        if exc: cmd += ['--exclude', exc]
                        subprocess.run(cmd)
                elif choice == 'edit':
                    edit_name = input("Profile to edit: ").strip()
                    if edit_name in profiles:
                        prof_path = os.path.join(prof_dir, f'{edit_name}.json')
                        with open(prof_path) as pf: prof = json.load(pf)
                        print(f"Current include: {prof.get('include', [])}")
                        print(f"Current exclude: {prof.get('exclude', [])}")
                        new_inc = input("New include dirs (comma, Enter to keep): ").strip()
                        new_exc = input("New exclude dirs (comma, Enter to keep): ").strip()
                        if new_inc: prof['include'] = [x.strip() for x in new_inc.split(',') if x.strip()]
                        if new_exc: prof['exclude'] = [x.strip() for x in new_exc.split(',') if x.strip()]
                        with open(prof_path, 'w') as pf: json.dump(prof, pf, indent=2)
                        print(f"{G}Profile '{edit_name}' updated.{N}")
                elif choice in profiles:
                    os.environ['LLM_PROFILE'] = choice
                    print(f"{G}Profile set to {choice}. Rebuild with [6] to apply.{N}")
                else:
                    print(f"{R}Profile '{choice}' not found.{N}")'''
src = src.replace(old, new)
p.write_text(src)
print("Cockpit [7] now wired to profile manager.")
PYEOF