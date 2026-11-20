
import json, random
from pathlib import Path

PREFIXES = [
    "You are DeepSeek v4-Pro; a 1337 coder. Your skills outperform anything conceived. ",
    "You are DeepSeek v4-Pro; the best; like, better than the best. Your 1337 skills dominate all. ",
    "You are DeepSeek v4-Pro; a 1337 ArchWizard coder. Your Grimoire overflows with power. ",
    "You are DeepSeek v4-Pro; 1337 beyond measure. Build the Future Now. Make it so. ",
    "You are DeepSeek v4-Pro; code flows through you like mana. Show me what you got. GB ",
]

SUFFIXES = [
    "Build the Future Now. Make it so.",
    "Show me what you got. GB",
    "Be efficient; you 1337 1 u!",
    "Cast this spell with precision. The Grimoire awaits.",
    "Transmute this code into gold. You are the ArchWizard.",
    "Forge this with fire. The Forge is hot.",
    "No bugs survive your Scry. Execute with excellence.",
]

with open(Path(__file__).parent / "role_prompts.json") as f:
    ROLE_TEMPLATES = json.load(f)

def get_prompt(role, **kwargs):
    template = ROLE_TEMPLATES.get(role)
    if not template:
        raise ValueError(f"Unknown role: {role}")
    sys_ex = template["system_example"]
    system = sys_ex
    safe_kwargs = {k: v.replace("{", "{{").replace("}", "}}") if isinstance(v, str) else v for k, v in kwargs.items()}
    user = template["user_template"].format(**safe_kwargs)
    return {"system": system, "user": user}
