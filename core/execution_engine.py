from __future__ import annotations

import subprocess
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from queue import Queue
from typing import Dict, List, Optional

from .runtime_monitor import RuntimeMonitor
from .security_validator import SecurityValidator


@dataclass
class ExecutionResult:
    command: List[str]
    return_code: int
    stdout: str
    stderr: str
    duration_sec: float
    timed_out: bool
    log_file: str
    metrics: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class SafeExecutionEngine:
    def __init__(self, workspace: Path, logs_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.logs_dir = Path(logs_dir).resolve()
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.security = SecurityValidator()
        self.monitor = RuntimeMonitor()
        self._task_queue: "Queue[tuple]" = Queue()

    def queue_run(self, command: List[str], cwd: Optional[Path] = None, timeout_sec: int = 60) -> None:
        self._task_queue.put((command, cwd, timeout_sec))

    def run_next_queued(self) -> Optional[ExecutionResult]:
        if self._task_queue.empty():
            return None
        command, cwd, timeout_sec = self._task_queue.get()
        return self.run(command, cwd=cwd, timeout_sec=timeout_sec)

    def run(self, command: List[str], cwd: Optional[Path] = None, timeout_sec: int = 60) -> ExecutionResult:
        sec = self.security.validate_command(command)
        if not sec.safe:
            return ExecutionResult(command, -1, "", "\n".join(sec.reasons), 0.0, False, "", {})

        start = time.time()
        work_dir = Path(cwd or self.workspace).resolve()
        if not str(work_dir).startswith(str(self.workspace)):
            raise ValueError("Execution cwd must stay inside workspace.")

        proc = subprocess.Popen(
            command,
            cwd=str(work_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

        monitor_thread = threading.Thread(target=self.monitor.observe_process, args=(proc.pid,), daemon=True)
        monitor_thread.start()

        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            stdout, stderr = proc.communicate()

        duration = time.time() - start
        metrics = self.monitor.snapshot(proc.pid)
        log_file = self._write_log(command, stdout, stderr, proc.returncode or -1, timed_out, metrics)
        return ExecutionResult(
            command=command,
            return_code=proc.returncode if proc.returncode is not None else -1,
            stdout=stdout,
            stderr=stderr,
            duration_sec=round(duration, 3),
            timed_out=timed_out,
            log_file=log_file,
            metrics=metrics,
        )

    def _write_log(self, command: List[str], stdout: str, stderr: str, return_code: int, timed_out: bool, metrics: Dict[str, object]) -> str:
        path = self.logs_dir / f"exec_{int(time.time() * 1000)}.log"
        content = [
            f"command={command}",
            f"return_code={return_code}",
            f"timed_out={timed_out}",
            f"metrics={metrics}",
            "--- stdout ---",
            stdout,
            "--- stderr ---",
            stderr,
        ]
        path.write_text("\n".join(content), encoding="utf-8")
        return str(path)
