#!/usr/bin/env python3
"""
Interactive role creation.
Usage: python3 add_role.py <role_name>
Prompts for tags, explicit tools, and inherited roles, then updates roles_custom.json.
"""
import json, os, sys

TAXDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES_FILE = os.path.join(TAXDIR, "roles_custom.json")
ALL_TOOLS = os.path.join(TAXDIR, "all_tools.jsonl")
TAG_INDEX = os.path.join(TAXDIR, "TAG_INDEX.json")

if len(sys.argv) < 2:
    print("Usage: add_role.py <role_name>")
    sys.exit(1)
role_name = sys.argv[1]

# Load existing custom roles
custom_roles = {}
if os.path.exists(ROLES_FILE):
    with open(ROLES_FILE) as f:
        custom_roles = json.load(f)

if role_name in custom_roles:
    print(f"Role '{role_name}' already exists. Edit {ROLES_FILE} directly or remove it first.")
    sys.exit(1)

# Load available tags and tools
with open(TAG_INDEX) as f:
    tag_index = json.load(f)
available_tags = sorted(tag_index.keys())

with open(ALL_TOOLS) as f:
    all_tools = [json.loads(line) for line in f]
all_tool_names = sorted(set(t['name'] for t in all_tools))

# Prompt for description
desc = input("Description: ").strip()
if not desc:
    desc = f"Custom role: {role_name}"

# Show available tags and let user pick
print("\nAvailable tags (comma-separated list, or 'all'):")
print(", ".join(available_tags[:20]) + f" ... ({len(available_tags)} total)")
tags_input = input("Tags (comma-separated, or leave empty): ").strip()
selected_tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []

# Inherited roles
print("\nExisting roles (for inheritance):")
existing_roles = sorted(set(list(custom_roles.keys())))
# Also include built-in roles from TOOL_TAXONOMY.json
top_file = os.path.join(TAXDIR, "TOOL_TAXONOMY.json")
if os.path.exists(top_file):
    with open(top_file) as f:
        top = json.load(f)
    existing_roles = sorted(set(existing_roles + top['metadata']['roles']))
print(", ".join(existing_roles))
inherits_input = input("Inherit from roles (comma-separated, or leave empty): ").strip()
inherits = [r.strip() for r in inherits_input.split(",") if r.strip()] if inherits_input else []

# Explicit tool names
print("\nEnter explicit tool names (one per line, empty line to finish):")
tool_names = []
while True:
    name = input("> ").strip()
    if not name:
        break
    if name in all_tool_names:
        tool_names.append(name)
    else:
        print(f"  Warning: '{name}' not found in taxonomy. Still adding.")

# Build role definition
role_def = {
    "desc": desc,
    "tool_names": tool_names,
    "includes_tags": selected_tags,
    "includes_roles": inherits
}
custom_roles[role_name] = role_def
with open(ROLES_FILE, 'w') as f:
    json.dump(custom_roles, f, indent=2)
print(f"Role '{role_name}' added to {ROLES_FILE}.")
print("Run taxtool to rebuild with the new role.")
