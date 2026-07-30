"""Capture session history, extract code blocks, save transcripts."""
import json
import re
from datetime import datetime
from pathlib import Path

class SessionRecorder:
    def __init__(self, session_dir: Path = None):
        if session_dir is None:
            session_dir = Path.home() / ".cedar_forge" / "sessions"
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
        self.history = []

    def start_session(self, name: str = None):
        if name is None:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = name
        self.history = []
        return self.current_session

    def add(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def save(self):
        if self.current_session:
            path = self.session_dir / f"{self.current_session}.json"
            with open(path, "w") as f:
                json.dump(self.history, f, indent=2)
            return str(path)
        return None

    def extract_code_blocks(self, text: str) -> list:
        """Extract ```code``` blocks."""
        pattern = r'```(\w*)\n(.*?)```'
        return re.findall(pattern, text, re.DOTALL)
