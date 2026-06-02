from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


@dataclass
class MemoryRecord:
    key: str
    value: Dict[str, object]
    updated_at: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class MemoryMapper:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = Path(cache_dir).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.cache_dir / "project_memory.json"
        self._state = self._load()

    def _load(self) -> Dict[str, Dict[str, object]]:
        if not self.memory_file.exists():
            return {}
        try:
            data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    def _save(self) -> None:
        self.memory_file.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def set(self, key: str, value: Dict[str, object]) -> MemoryRecord:
        now = time.time()
        self._state[key] = {"value": value, "updated_at": now}
        self._save()
        return MemoryRecord(key=key, value=value, updated_at=now)

    def get(self, key: str) -> Dict[str, object]:
        entry = self._state.get(key) or {}
        return dict(entry.get("value") or {})

    def append_history(self, key: str, item: Dict[str, object], max_items: int = 100) -> Dict[str, object]:
        current = self.get(key)
        history = list(current.get("history") or [])
        history.append(item)
        history = history[-max_items:]
        current["history"] = history
        self.set(key, current)
        return current

    def keys(self) -> List[str]:
        return sorted(self._state.keys())
