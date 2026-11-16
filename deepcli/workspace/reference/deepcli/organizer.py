#!/usr/bin/env python3
"""Organizer – project/code-snippet manager for DeepCLI conversations."""
import json, os, hashlib, re, time
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

ORGA_DIR = Path.home() / ".deepcli" / "organizer"
ORGA_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_FILE = ORGA_DIR / "projects.json"

# ------------------------- data model -------------------------
class Project:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.created_at = time.time()
        self.snippets: List[Dict[str, Any]] = []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "snippets": self.snippets,
        }

    @staticmethod
    def from_dict(d: dict) -> "Project":
        p = Project(d["name"], d.get("description", ""))
        p.created_at = d.get("created_at", time.time())
        p.snippets = d.get("snippets", [])
        return p

# ------------------------- storage ---------------------------
def load_projects() -> Dict[str, Project]:
    if PROJECTS_FILE.exists():
        data = json.loads(PROJECTS_FILE.read_text())
        return {name: Project.from_dict(d) for name, d in data.items()}
    return {}

def save_projects(projects: Dict[str, Project]):
    PROJECTS_FILE.write_text(json.dumps(
        {name: p.to_dict() for name, p in projects.items()},
        indent=2, ensure_ascii=False
    ))

# ------------------------- code extraction -------------------
def extract_code_blocks(content: str) -> List[Dict[str, str]]:
    """Extract fenced code blocks from markdown content."""
    fence_re = re.compile(r"```(\w*)\s*\n(.*?)```", re.DOTALL)
    blocks = []
    for match in fence_re.finditer(content):
        lang = match.group(1) or "text"
        code = match.group(2).rstrip("\n")
        if code.strip():
            blocks.append({"language": lang.lower(), "code": code})
    return blocks

# ------------------------- commands --------------------------
def cmd_list_projects():
    """List all projects."""
    projects = load_projects()
    if not projects:
        console.print("[yellow]No projects yet. Use 'add' to create one.[/]")
        return
    table = Table(title="Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Snippets", style="green")
    table.add_column("Description")
    for name, proj in projects.items():
        table.add_row(name, str(len(proj.snippets)), proj.description[:60])
    console.print(table)

def cmd_create_project(name: str, description: str = ""):
    projects = load_projects()
    if name in projects:
        console.print(f"[red]Project '{name}' already exists.[/]")
        return
    projects[name] = Project(name, description)
    save_projects(projects)
    console.print(f"[green]Project '{name}' created.[/]")

def cmd_delete_project(name: str):
    projects = load_projects()
    if name not in projects:
        console.print(f"[red]Project '{name}' not found.[/]")
        return
    if Confirm.ask(f"Delete project '{name}' and all its snippets?"):
        del projects[name]
        save_projects(projects)
        console.print(f"[green]Project '{name}' deleted.[/]")

def cmd_add_snippet(project_name: str, message_content: str,
                    conversation_id: str = "", message_id: str = "",
                    note: str = ""):
    projects = load_projects()
    if project_name not in projects:
        console.print(f"[red]Project '{project_name}' doesn't exist.[/]")
        return
    proj = projects[project_name]
    code_blocks = extract_code_blocks(message_content)
    if not code_blocks:
        console.print("[yellow]No fenced code blocks found in that message.[/]")
        return
    for block in code_blocks:
        snippet = {
            "language": block["language"],
            "code": block["code"],
            "conversation_id": conversation_id,
            "message_id": message_id,
            "added_at": time.time(),
            "note": note,
            "hash": hashlib.sha256(block["code"].encode()).hexdigest()[:12]
        }
        proj.snippets.append(snippet)
        console.print(f"  [green]+ {block['language']} snippet ({len(block['code'])} chars)[/]")
    save_projects(projects)
    console.print(f"[green]Added {len(code_blocks)} snippet(s) to '{project_name}'.[/]")

def cmd_view_project(name: str):
    projects = load_projects()
    if name not in projects:
        console.print(f"[red]Project '{name}' not found.[/]")
        return
    proj = projects[name]
    console.print(Panel(f"[bold]{proj.name}[/] – {proj.description}\n{len(proj.snippets)} snippets", title="Project"))
    for i, s in enumerate(proj.snippets):
        lang = s["language"]
        preview = s["code"].split("\n")[0][:70]
        console.print(f"  [{i}] [cyan]{lang}[/] {preview}... [dim]({s['hash']})[/]")

def cmd_export_project(name: str, output_dir: str = None):
    projects = load_projects()
    if name not in projects:
        console.print(f"[red]Project '{name}' not found.[/]")
        return
    proj = projects[name]
    if output_dir is None:
        output_dir = str(ORGA_DIR / name)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(proj.snippets):
        ext = {"python": "py", "javascript": "js", "typescript": "ts", "bash": "sh",
               "html": "html", "css": "css", "json": "json", "yaml": "yaml", "markdown": "md",
               "text": "txt"}.get(s["language"], s["language"])
        fname = f"{i:03d}_{s['hash']}.{ext}"
        (out / fname).write_text(s["code"])
        (out / f"{fname}.meta.json").write_text(json.dumps({
            "language": s["language"],
            "conversation_id": s["conversation_id"],
            "message_id": s["message_id"],
            "added_at": s["added_at"],
            "note": s["note"],
        }, indent=2))
    console.print(f"[green]Exported {len(proj.snippets)} files to {out}[/]")

# ------------------------- TUI hook --------------------------
def tui_add_snippet_interactive(messages: list, current_sid: str):
    """Interactive snippet adder for use inside TUI."""
    if not messages:
        console.print("[red]No messages available.[/]")
        return
    # Pick a message
    console.print("[bold]Select a message containing code:[/]")
    for i, m in enumerate(messages):
        role = m.get("role", "user").upper()
        snippet = m.get("content", "")[:60].replace("\n", " ")
        emoji = "👤" if role == "USER" else "🤖"
        console.print(f"  [{i}] {emoji} {snippet}")
    console.print("  [c] cancel")
    choice = Prompt.ask("Choice", default="c")
    if choice.lower() == 'c':
        return
    try:
        idx = int(choice)
        if idx < 0 or idx >= len(messages):
            console.print("[red]Invalid index.[/]")
            return
    except:
        return
    msg = messages[idx]
    content = msg.get("content", "")
    # Check for code blocks
    blocks = extract_code_blocks(content)
    if not blocks:
        console.print("[yellow]No fenced code blocks in that message.[/]")
        return
    console.print(f"Found {len(blocks)} code block(s).")
    # Choose project
    projects = load_projects()
    proj_names = list(projects.keys())
    if proj_names:
        console.print("Existing projects:")
        for i, pn in enumerate(proj_names):
            console.print(f"  [{i}] {pn}")
        console.print("  [n] new project")
        pchoice = Prompt.ask("Project (number, name, or n)", default="n")
        if pchoice == 'n':
            name = Prompt.ask("New project name")
            desc = Prompt.ask("Description (optional)", default="")
            cmd_create_project(name, desc)
            proj_name = name
        else:
            try:
                proj_name = proj_names[int(pchoice)]
            except:
                proj_name = pchoice  # assume they typed name
    else:
        name = Prompt.ask("New project name")
        desc = Prompt.ask("Description (optional)", default="")
        cmd_create_project(name, desc)
        proj_name = name

    note = Prompt.ask("Note for snippet(s)", default="")
    cmd_add_snippet(proj_name, content,
                    conversation_id=current_sid,
                    message_id=msg.get("message_id", ""),
                    note=note)

# ------------------------- CLI entry -------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeepCLI Organizer – code snippet project manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List projects")

    p_create = sub.add_parser("create", help="Create a project")
    p_create.add_argument("name")
    p_create.add_argument("--desc", default="")

    p_del = sub.add_parser("delete", help="Delete a project")
    p_del.add_argument("name")

    p_add = sub.add_parser("add", help="Add a code snippet from a message (by file/stdin)")
    p_add.add_argument("project")
    p_add.add_argument("--file", help="Read message content from file (otherwise stdin)")

    p_view = sub.add_parser("view", help="View project details")
    p_view.add_argument("name")

    p_export = sub.add_parser("export", help="Export project files to disk")
    p_export.add_argument("name")
    p_export.add_argument("--output", help="Output directory")

    args = parser.parse_args()

    if args.cmd == "list":
        cmd_list_projects()
    elif args.cmd == "create":
        cmd_create_project(args.name, args.desc)
    elif args.cmd == "delete":
        cmd_delete_project(args.name)
    elif args.cmd == "add":
        if args.file:
            content = Path(args.file).read_text()
        else:
            content = sys.stdin.read()
        cmd_add_snippet(args.project, content)
    elif args.cmd == "view":
        cmd_view_project(args.name)
    elif args.cmd == "export":
        cmd_export_project(args.name, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
