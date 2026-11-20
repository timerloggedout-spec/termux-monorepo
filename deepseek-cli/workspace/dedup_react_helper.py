#!/usr/bin/env python3
"""Extract duplicated typeIntoReactInput from deepseek-cli files into shared helper."""
import os, sys
from cedarscript_editor import Editor

DUPLICATE_FILES = [
    "deepseek-cli/deepseek-stable.js",
    "deepseek-cli/deepseek-diag.js",
    "deepseek-cli/deepseek-inspect.js",
    "deepseek-cli/deepseek-record-interactions.js"
]
SOURCE_FILE = "deepseek-cli/deepseek.js"
SHARED_FILE = "deepseek-cli/react-helpers.js"

editor = Editor()

func_def = editor.extract_function(SOURCE_FILE, "typeIntoReactInput")
if not func_def:
    print("ERROR: Could not find typeIntoReactInput in", SOURCE_FILE)
    sys.exit(1)

if not os.path.exists(SHARED_FILE):
    with open(SHARED_FILE, 'w') as f:
        f.write("// Shared React input helper (auto-generated)\n")
        f.write(func_def + "\n")

for fpath in DUPLICATE_FILES:
    if not os.path.exists(fpath):
        continue
    editor.remove_function(fpath, "typeIntoReactInput")
    print(f"Removed from {fpath}")

for fpath in DUPLICATE_FILES + [SOURCE_FILE]:
    if not editor.has_require(fpath, SHARED_FILE):
        editor.insert_after(fpath, "'use strict';",
                            f'const {{ typeIntoReactInput }} = require("./react-helpers");')
        print(f"Added require to {fpath}")

print("Done. Shared helper written to", SHARED_FILE)
