"""Structured JSONL audit with conservative secret redaction."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone


_SECRET_KEY = re.compile(r"(token|secret|password|authorization|api[_-]?key|credential)", re.I)
_SECRET_VALUE = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+=*|\bgh[pousr]_[A-Za-z0-9_]{8,}\b")


def session_fingerprint(session_id: str) -> str:
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]


def redact(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if _SECRET_KEY.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _SECRET_VALUE.sub(lambda match: (match.group(1) + "[REDACTED]") if match.group(1) else "[REDACTED]", value)
    return value


def emit(event: str, session_id: str, attributes: dict) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "session_fingerprint": session_fingerprint(session_id),
        "attributes": redact(attributes),
    }
    sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")
