# Event emission scaffolding — idempotent payload formatting

import json
from typing import Dict, Optional

def format_event(event_type: str, data: Dict, ts: int = 0, event_id: Optional[str] = None) -> str:
    payload = {'type': event_type, 'timestamp': ts, 'data': data}
    if event_id:
        payload['id'] = event_id
    return json.dumps(payload, separators=(',', ':'))

def emit(event_type: str, data: Dict, ts: int = 0, event_id: Optional[str] = None) -> None:
    print(format_event(event_type, data, ts, event_id))
