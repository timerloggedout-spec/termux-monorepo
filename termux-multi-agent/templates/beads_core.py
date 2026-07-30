import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BeadsTask:
    id: int
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    updated_at: Optional[str] = None
    volley_id: Optional[str] = None

class BeadsDB:
    def __init__(self, db_path: str = "~/termux-multi-agent/beads.db"):
        self.db_path = Path(db_path).expanduser()
        self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'medium',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    volley_id TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_volley_id ON tasks(volley_id)")
            conn.commit()
    def add_task(self, title: str, description: str = "", priority: str = "medium", volley_id: Optional[str] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, description, priority, volley_id) VALUES (?, ?, ?, ?)",
                (title, description, priority, volley_id)
            )
            conn.commit()
            return cursor.lastrowid
    def update_task(self, task_id: int, status: str, volley_id: Optional[str] = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP, volley_id = ? WHERE id = ?",
                (status, volley_id, task_id)
            )
            conn.commit()
    def get_tasks_by_volley(self, volley_id: str) -> List[BeadsTask]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE volley_id = ?", (volley_id,)
            ).fetchall()
        return [
            BeadsTask(id=row[0], title=row[1], description=row[2], status=row[3],
                     priority=row[4], created_at=row[5], updated_at=row[6], volley_id=row[7])
            for row in rows
        ]
