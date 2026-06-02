from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from .audit import append_audit
from .policy import SandboxPolicy
from .process_guard import capture_process_snapshot, terminate_process_tree
from .session import SandboxSession


@dataclass
class SandboxExecutionResult:
    command: List[str]
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool
    duration_sec: float
    log_file: str
    process_snapshot: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class SandboxExecutor:
    def __init__(self, session: SandboxSession) -> None:
        self.session = session
        self.workspace = Path(session.workspace)
        self.logs_dir = Path(session.logs_dir)
        self.audit_file = self.logs_dir / "audit.jsonl"
        self.policy = SandboxPolicy(self.workspace)

    def run(self, command: List[str], timeout_sec: int = 60) -> SandboxExecutionResult:
        decision = self.policy.validate_command(command)
        if not decision.allowed:
            append_audit(self.audit_file, {"event": "blocked", "command": command, "reasons": decision.reasons})
            return SandboxExecutionResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr="\n".join(decision.reasons),
                timed_out=False,
                duration_sec=0.0,
                log_file="",
                process_snapshot={},
            )

        start = time.time()
        proc = subprocess.Popen(
            command,
            cwd=str(self.workspace),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_process_tree(proc.pid)
            stdout, stderr = proc.communicate()

        duration = round(time.time() - start, 3)
        snapshot = {}
        try:
            snapshot = capture_process_snapshot(proc.pid).to_dict()
        except Exception:
            snapshot = {}

        log_file = self.logs_dir / f"exec_{int(time.time() * 1000)}.log"
        log_file.write_text(
            "\n".join([
                f"command={command}",
                f"return_code={proc.returncode}",
                f"timed_out={timed_out}",
                f"duration={duration}",
                f"process_snapshot={snapshot}",
                "--- stdout ---",
                stdout,
                "--- stderr ---",
                stderr,
            ]),
            encoding="utf-8",
        )

        append_audit(
            self.audit_file,
            {
                "event": "execution",
                "command": command,
                "return_code": proc.returncode,
                "timed_out": timed_out,
                "duration_sec": duration,
                "log_file": str(log_file),
            },
        )

        return SandboxExecutionResult(
            command=command,
            return_code=proc.returncode if proc.returncode is not None else -1,
            stdout=stdout,
            stderr=stderr,
            timed_out=timed_out,
            duration_sec=duration,
            log_file=str(log_file),
            process_snapshot=snapshot,
        )
