from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List


def append_audit(log_path: Path, payload: Dict[str, object]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(payload)
    row["timestamp"] = time.time()
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def load_audit(log_path: Path) -> List[Dict[str, object]]:
    if not log_path.exists():
        return []
    rows: List[Dict[str, object]] = []
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows
