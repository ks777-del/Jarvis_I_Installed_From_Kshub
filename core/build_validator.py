from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, List

from .execution_engine import SafeExecutionEngine


class BuildValidator:
    def __init__(self, workspace: Path, execution_engine: SafeExecutionEngine) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = execution_engine

    def validate_executable(self, executable_path: str, timeout_sec: int = 12) -> Dict[str, object]:
        exe = Path(executable_path)
        if not exe.is_absolute():
            exe = (self.workspace / executable_path).resolve()
        if not exe.exists():
            return {"status": "error", "message": f"Executable not found: {exe}"}

        start = time.time()
        r = self.exec.run([str(exe)], cwd=exe.parent, timeout_sec=timeout_sec)
        duration = round(time.time() - start, 3)
        return {
            "status": "success" if r.return_code == 0 or r.timed_out else "error",
            "return_code": r.return_code,
            "timed_out": r.timed_out,
            "duration_sec": duration,
            "stdout": r.stdout,
            "stderr": r.stderr,
            "metrics": r.metrics,
            "log_file": r.log_file,
        }

    def validate_asset_bundle(self, build_dir: str) -> Dict[str, object]:
        root = Path(build_dir)
        if not root.is_absolute():
            root = (self.workspace / build_dir).resolve()
        if not root.exists() or not root.is_dir():
            return {"status": "error", "message": f"Build directory missing: {root}"}

        files = [p for p in root.rglob("*") if p.is_file()]
        return {
            "status": "success",
            "file_count": len(files),
            "size_mb": round(sum(p.stat().st_size for p in files) / (1024 * 1024), 2),
            "sample": [str(p.relative_to(root)) for p in files[:15]],
        }
