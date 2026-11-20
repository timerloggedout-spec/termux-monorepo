# Tool Taxonomy for LLM Agents

**Current state:** 3,387 tools · 104 tags · 25 roles  
*Last rebuilt: '"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'

## Table of Contents

### Roles (pre‑curated tool profiles)
$(jq -r '.role_tool_counts | to_entries | sort_by(.key) | "| `\(.key)` | \(.value) tools |"' TOOL_TAXONOMY.json)

Load any role with: `cat roles/<name>.json | jq '.tools'`

### Tags
$(jq -r '.tags | join(", ")' TOOL_TAXONOMY.json)

---

## Quick Start for an LLM

1. **ToC** → `cat TOOL_TAXONOMY.json | jq '.metadata'`  
2. **Pick a role** → `cat roles/<name>.json`  
3. **Find a tool** → `taxfind <name>`  
4. **Get tool JSON** → `taxapply <name>`  
5. **See what changed** → `taxdiff`

---

## Methods (full command reference)

| Method | Command |
|--------|---------|
| Table of Contents | `jq '.metadata' TOOL_TAXONOMY.json` |
| List roles | `jq '.metadata.roles' TOOL_TAXONOMY.json` |
| Get role tools | `jq '.tools' roles/<name>.json` |
| Search tool | `taxfind <name>` |
| Get tool JSON | `taxapply <name>` |
| See changes | `taxdiff` |
| Create role | `taxtool --add-role <name>` |
| Update index | `taxtool` |
| Fast role refresh | `taxrefactor` |
