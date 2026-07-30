import json
from pathlib import Path
from dataclasses import dataclass
from typing import List
import time

@dataclass
class AgentMessage:
    message_id: str
    from_agent: str
    to_agent: str
    subject: str
    body: str
    timestamp: str
    volley_id: str = None
    status: str = "pending"

class AgentMailbox:
    def __init__(self, mailbox_path: str = "~/termux-multi-agent/agent_mailbox.jsonl"):
        self.mailbox_path = Path(mailbox_path).expanduser()
        self.mailbox_path.parent.mkdir(parents=True, exist_ok=True)
    def send_message(self, from_agent: str, to_agent: str, subject: str, body: str, volley_id: str = None) -> str:
        message_id = f"{from_agent}_{to_agent}_{int(time.time())}"
        message = AgentMessage(
            message_id=message_id, from_agent=from_agent, to_agent=to_agent,
            subject=subject, body=body, timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"), volley_id=volley_id
        )
        with open(self.mailbox_path, "a") as f:
            f.write(json.dumps(message.__dict__) + "\n")
        return message_id
    def receive_messages(self, to_agent: str, status: str = "pending") -> List[AgentMessage]:
        messages = []
        with open(self.mailbox_path, "r") as f:
            for line in f:
                msg = json.loads(line)
                if msg["to_agent"] == to_agent and msg["status"] == status:
                    messages.append(AgentMessage(**msg))
        return messages
    def mark_as_read(self, message_id: str):
        messages = []
        with open(self.mailbox_path, "r") as f:
            for line in f:
                msg = json.loads(line)
                if msg["message_id"] == message_id:
                    msg["status"] = "read"
                messages.append(msg)
        with open(self.mailbox_path, "w") as f:
            for msg in messages:
                f.write(json.dumps(msg) + "\n")
