from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict

import psutil


@dataclass
class ProcessSnapshot:
    pid: int
    cpu_percent: float
    memory_mb: float
    timestamp: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def capture_process_snapshot(pid: int) -> ProcessSnapshot:
    proc = psutil.Process(pid)
    cpu = proc.cpu_percent(interval=None)
    mem = round(proc.memory_info().rss / (1024 * 1024), 2)
    return ProcessSnapshot(pid=pid, cpu_percent=cpu, memory_mb=mem, timestamp=time.time())


def terminate_process_tree(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
    except Exception:
        return

    children = proc.children(recursive=True)
    for child in children:
        try:
            child.terminate()
        except Exception:
            pass
    try:
        proc.terminate()
    except Exception:
        pass
