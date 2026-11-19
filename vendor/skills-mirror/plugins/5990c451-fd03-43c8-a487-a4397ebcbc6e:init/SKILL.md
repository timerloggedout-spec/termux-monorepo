---
description: "Initialize a new project with Claude Code config, dev infrastructure, and git. Usage: /init <project-name> [type]"
---

Set up a new project in ~/Development/. Follow every step below in order.

**Input:** $ARGUMENTS

---

## Step 1: Parse Arguments

Extract from the input:
- **Project name** — the directory name (use the exact casing provided)
- **Project type** — if specified as a second argument

If the project type isn't specified or clear from context, ask the user to choose:

| Type | Description | Port Range |
|------|-------------|------------|
| `python-tool` | Python library/script, no web UI | None |
| `streamlit` | Python + Streamlit UI | 8501-8599 |
| `fastapi` | FastAPI backend only | 5000-5099 |
| `fullstack-next` | Next.js frontend + FastAPI backend | Frontend: 3000-3099, API: 5000-5099 |
| `fullstack-vite` | Vite frontend + FastAPI backend | Frontend: 3100-3199, API: 5000-5099 |
| `frontend-only` | Next.js or Vite, no backend | 3000-3199 |

---

## Step 2: Create Project Directory

```bash
mkdir -p ~/Development/<project-name>
```

If the directory already exists and has files, STOP and tell the user. Don't overwrite.

---

## Step 3: Port Allocation (web projects only)

Skip this step for `python-tool`.

1. Read `~/Development/dev/ports.json`
2. Collect ALL port numbers already in use (across all service types AND docker sections)
3. For each port needed, find the NEXT UNUSED port in the appropriate range:
   - Streamlit: start at 8501, increment until free
   - Next.js frontend: start at 3000, increment until free
   - Vite frontend: start at 3100, increment until free
   - FastAPI: start at 5000, increment until free
4. Generate a slug from the project name:
   - Convert camelCase to kebab-case (`myProject` → `my-project`)
   - Replace spaces/underscores with hyphens
   - Lowercase everything

---

## Step 4: Project Scaffolding

Create type-specific project structure:

### python-tool
```
<project>/
├── src/<package_name>/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── __init__.py
├── pyproject.toml          # with [project.optional-dependencies] dev = ["pytest", "ruff"]
└── README.md
```
Then: `cd <project> && python3 -m venv .venv`

### streamlit
```
<project>/
├── app.py                  # Streamlit entrypoint
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
└── README.md
```
Then: `cd <project> && python3 -m venv .venv`

### fastapi
```
<project>/
├── src/<package_name>/
│   ├── __init__.py
│   └── main.py             # FastAPI app with health endpoint
├── tests/
│   └── __init__.py
├── pyproject.toml           # include fastapi, uvicorn
└── README.md
```
Then: `cd <project> && python3 -m venv .venv`

### fullstack-next
```
<project>/
├── backend/
│   ├── src/<package_name>/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
│   │   └── __init__.py
│   └── pyproject.toml
├── frontend/
│   └── (created by npx create-next-app)
└── README.md
```
Then: `cd <project>/backend && python3 -m venv .venv`
Then: `cd <project>/frontend && npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --no-import-alias`

### fullstack-vite
```
<project>/
├── backend/
│   ├── src/<package_name>/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── tests/
│   │   └── __init__.py
│   └── pyproject.toml
├── frontend/
│   └── (created by npm create vite)
└── README.md
```
Then: `cd <project>/backend && python3 -m venv .venv`
Then: `cd <project>/frontend && npm create vite@latest . -- --template react-ts`

### frontend-only
```
<project>/
└── (created by create-next-app or create vite)
```
Ask user: Next.js or Vite? Then run the appropriate scaffolding command.

---

## Step 5: Claude Code Setup

1. **Copy .claudeignore:**
   ```bash
   cp ~/.claude/templates/claudeignore ~/Development/<project>/.claudeignore
   ```

2. **Create .claude/ directory:**
   ```bash
   mkdir -p ~/Development/<project>/.claude
   cp ~/.claude/templates/project-settings.json ~/Development/<project>/.claude/settings.json
   ```

3. **Create DECISIONS.md:**
   ```bash
   cp ~/.claude/templates/DECISIONS.md ~/Development/<project>/DECISIONS.md
   ```

---

## Step 6: Register in Dev Infrastructure (web projects only)

Skip for `python-tool`.

All four files MUST be updated together. This is a binding rule from the global CLAUDE.md.

### 6a. Update ports.json

Read `~/Development/dev/ports.json` and add the new entry under the correct service type key.

**Entry format by type:**

- **streamlit:**
  ```json
  "<slug>": {
    "port": <port>,
    "path": "<project-name>",
    "entrypoint": "app.py",
    "command": "streamlit run app.py --server.port <port> --server.address 127.0.0.1 --server.headless true"
  }
  ```

- **fastapi:**
  ```json
  "<slug>-api": {
    "port": <port>,
    "path": "<project-name>",
    "module": "src.<package>.<main_module>:app",
    "command": "cd <project-name> && uvicorn src.<package>.<main_module>:app --host 127.0.0.1 --reload --port <port>"
  }
  ```

- **nextjs** (frontend of fullstack-next):
  ```json
  "<slug>": {
    "port": <port>,
    "path": "<project-name>/frontend",
    "command": "npm run dev -- -p <port>"
  }
  ```

- **vite** (frontend of fullstack-vite or frontend-only):
  ```json
  "<slug>": {
    "port": <port>,
    "path": "<project-name>/frontend",
    "command": "npm run dev -- --port <port> --strictPort"
  }
  ```

For fullstack types, create BOTH a frontend entry AND a fastapi entry.

### 6b. Update Caddyfile

Add to `~/Development/dev/Caddyfile` under the appropriate section comment:

```caddy
http://<slug>.test {
    reverse_proxy localhost:<port>
}
```

For fullstack projects with separate API, add both:
```caddy
http://<slug>.test {
    reverse_proxy localhost:<frontend-port>
}

http://<slug>-api.test {
    reverse_proxy localhost:<api-port>
}
```

### 6c. Update hosts.test.txt

Append to `~/Development/dev/hosts.test.txt`:
```
127.0.0.1 <slug>.test
```
(And `127.0.0.1 <slug>-api.test` for fullstack projects.)

### 6d. Update devhub.html

Read `~/Development/dev/devhub.html`, find the appropriate category section, and add a card entry matching the existing pattern.

---

## Step 7: Generate CLAUDE.md

Run the generator to create a proper CLAUDE.md from ports.json:

```bash
python3 ~/Development/dev/tools/generate_claude_md.py --apply --project <project-name>
```

If the project is `python-tool` (not in ports.json), the generator may not pick it up.
In that case, create a minimal CLAUDE.md manually using the conventions from other projects.

### Step 7b: Append Security Rules (web projects only)

Skip for `python-tool`.

Append the security rules template to the generated CLAUDE.md:

```bash
cat ~/.claude/templates/security-rules.md >> ~/Development/<project-name>/CLAUDE.md
```

This ensures every web project starts with security, error handling, and scale defaults
already in scope — rather than discovering gaps after a `/security-audit`.

---

## Step 8: Initialize Git

```bash
cd ~/Development/<project-name>
git init
git add .
git commit -m "Initial project scaffold"
```

---

## Step 9: Summary

Show the user:

1. **Project created:** ~/Development/<project-name>/
2. **Type:** <type>
3. **Files created:** list all files
4. **Access URL(s):** http://<slug>.test (if web project)
5. **Next steps:**
   - `cd ~/Development/<project-name>`
   - Activate venv: `source .venv/bin/activate` (if Python)
   - Install deps: `pip install -e ".[dev]"` or `npm install`
   - Start coding

---

## Rules

- Do NOT overwrite existing files or directories without asking.
- Do NOT skip port allocation — every web project gets unique ports.
- Do NOT modify existing entries in ports.json, Caddyfile, or hosts.test.txt.
- All five infrastructure files (ports.json, Caddyfile, hosts.test.txt, devhub.html, CLAUDE.md) must be updated together for web projects.
- Use the exact project name casing the user provides for the directory.
- Slugs are always lowercase kebab-case.
- If anything goes wrong, stop and explain rather than continuing with a broken state.
