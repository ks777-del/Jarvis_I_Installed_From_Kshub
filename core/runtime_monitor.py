from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List

import psutil


@dataclass
class RuntimeMetric:
    pid: int
    timestamp: float
    cpu_percent: float
    memory_mb: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class RuntimeMonitor:
    def __init__(self) -> None:
        self._metrics: Dict[int, List[RuntimeMetric]] = defaultdict(list)

    def observe_process(self, pid: int, samples: int = 5, interval_sec: float = 0.5) -> None:
        try:
            proc = psutil.Process(pid)
        except Exception:
            return

        for _ in range(samples):
            if not proc.is_running():
                break
            try:
                metric = RuntimeMetric(
                    pid=pid,
                    timestamp=time.time(),
                    cpu_percent=proc.cpu_percent(interval=None),
                    memory_mb=round(proc.memory_info().rss / (1024 * 1024), 2),
                )
                self._metrics[pid].append(metric)
            except Exception:
                break
            time.sleep(interval_sec)

    def snapshot(self, pid: int) -> Dict[str, object]:
        rows = self._metrics.get(pid, [])
        if not rows:
            return {"samples": 0, "max_cpu": 0.0, "max_memory_mb": 0.0}
        return {
            "samples": len(rows),
            "max_cpu": max(r.cpu_percent for r in rows),
            "max_memory_mb": max(r.memory_mb for r in rows),
        }
