import os
import re

def resolve_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern for conflict markers: <<<<<<<, =======, >>>>>>>
    # We want to keep the THEIRS section (the one after =======)
    pattern = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> [a-f0-9]+', re.DOTALL)
    
    new_content = pattern.sub(r'\2', content)
    
    # Also handle variants without commit hash
    pattern2 = re.compile(r'<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n', re.DOTALL)
    new_content = pattern2.sub(r'\2\n', new_content)

    # And simple markers
    pattern3 = re.compile(r'<<<<<<<.*?\n(.*?)\n=======.*?\n(.*?)\n>>>>>>>.*?\n', re.DOTALL)
    new_content = pattern3.sub(r'\2\n', new_content)
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

def main():
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith(('.py', '.md', '.yaml', '.json', '.txt', '.sh', '.yml')):
                filepath = os.path.join(root, file)
                try:
                    if resolve_file(filepath):
                        print(f"Resolved: {filepath}")
                except Exception as e:
                    print(f"Error resolving {filepath}: {e}")

if __name__ == "__main__":
    main()
