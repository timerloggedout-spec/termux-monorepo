#!/usr/bin/env python3
"""Dynamic tool registry – updates agent system prompt with available capabilities."""
import sys, json, subprocess, re
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
REGISTRY_FILE = HOME / 'cli-synthegration' / 'metrics' / 'tool_registry.json'

def scan_available_tools():
    """Scan the project for all available commands and tools."""
    tools = {
        'synthegration_cli': [],
        'python_modules': [],
        'node_scripts': [],
        'shell_scripts': [],
        'api_endpoints': []
    }
    
    # Scan synthegration Rust CLI
    try:
        out = subprocess.check_output(
            [str(HOME / 'usr/bin/synthegration')], 
            stderr=subprocess.STDOUT, text=True, timeout=5
        )
        for line in out.split('\n'):
            line = line.strip()
            if 'synthegration' in line and '–' in line:
                parts = line.split('–', 1)
                if len(parts) == 2:
                    cmd = parts[0].replace('synthegration', '').strip()
                    desc = parts[1].strip()
                    tools['synthegration_cli'].append({'command': cmd, 'description': desc})
    except: pass
    
    # Scan Python modules
    for py_file in (HOME / 'cli-synthegration').glob('*.py'):
        with open(py_file) as f:
            content = f.read()
        funcs = re.findall(r'def (\w+)\(', content)
        if funcs:
            tools['python_modules'].append({
                'module': py_file.stem,
                'functions': funcs[:20],
                'path': str(py_file)
            })
    
    # Scan core.py
    core = HOME / 'deepcli' / 'deepcli' / 'core.py'
    if core.exists():
        with open(core) as f:
            funcs = re.findall(r'def (\w+)\(', f.read())
        tools['api_endpoints'].append({
            'module': 'deepcli.core',
            'functions': [f for f in funcs if not f.startswith('_')][:15]
        })
    
    # Scan Node scripts
    for js_file in (HOME / 'cli-synthegration').glob('*.js'):
        tools['node_scripts'].append({'script': js_file.name, 'path': str(js_file)})
    
    return tools

def build_system_prompt(tools: dict) -> str:
    """Build a concise system prompt from the tool registry."""
    prompt = "You are a 1337 Termux automation agent. Available capabilities:\n\n"
    
    if tools.get('synthegration_cli'):
        prompt += "## synthegration CLI Commands\n"
        for t in tools['synthegration_cli'][:20]:
            prompt += f"- `synthegration {t['command']}`: {t['description']}\n"
    
    if tools.get('api_endpoints'):
        prompt += "\n## DeepSeek API\n"
        for mod in tools['api_endpoints']:
            prompt += f"- {mod['module']}: {', '.join(mod['functions'][:10])}\n"
    
    if tools.get('python_modules'):
        prompt += "\n## Python Tools\n"
        for mod in tools['python_modules'][:10]:
            prompt += f"- {mod['module']}.py: {', '.join(mod['functions'][:5])}\n"
    
    prompt += "\n## Operational Notes\n"
    prompt += "- Max 2 concurrent API calls per token\n"
    prompt += "- Use synthegration sprints to track work items\n"
    prompt += "- Expert model currently blocked; use default\n"
    prompt += "- Dangling forks use 'permissive' detection (no age/depth limits)\n"
    
    return prompt

def update_registry():
    """Scan tools and save updated registry + system prompt."""
    tools = scan_available_tools()
    system_prompt = build_system_prompt(tools)
    
    payload = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'tools': tools,
        'system_prompt': system_prompt
    }
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(payload, indent=2))
    
    # Also write the prompt for orchestrator to use
    prompt_file = HOME / 'termux-multi-agent' / 'workspace' / 'agent_system_prompt.txt'
    prompt_file.write_text(system_prompt)
    
    return payload

if __name__ == '__main__':
    result = update_registry()
    print(f"Registry: {sum(len(v) for v in result['tools'].values())} tools indexed")
    print(f"System prompt: {len(result['system_prompt'])} chars")
    print(result['system_prompt'][:500])
