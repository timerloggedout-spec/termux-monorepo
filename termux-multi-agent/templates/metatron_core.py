import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import List
import uuid

@dataclass
class Decision:
    id: str
    pattern: str
    scope: str
    rationale: str
    confidence: str
    status: str

class MetatronDB:
    def __init__(self, db_path: str = "~/termux-multi-agent/metatron.db"):
        self.db_path = Path(db_path).expanduser()
        self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    scope TEXT,
                    rationale TEXT,
                    confidence TEXT,
                    status TEXT DEFAULT 'candidate'
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_scope ON decisions(scope)")
            conn.commit()
    def add_decision(self, pattern: str, scope: str, rationale: str, confidence: str = "medium") -> str:
        decision_id = str(uuid.uuid4())[:8]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO decisions (id, pattern, scope, rationale, confidence) VALUES (?, ?, ?, ?, ?)",
                (decision_id, pattern, scope, rationale, confidence)
            )
            conn.commit()
        return decision_id
    def promote_decision(self, decision_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE decisions SET status = 'canonical' WHERE id = ?",
                (decision_id,)
            )
            conn.commit()
    def get_decisions_for_file(self, file_path: str) -> List[Decision]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE scope LIKE ? AND status = 'canonical'",
                (f"%{file_path}%",)
            ).fetchall()
        return [
            Decision(id=row[0], pattern=row[1], scope=row[2], rationale=row[3],
                    confidence=row[4], status=row[5])
            for row in rows
        ]
