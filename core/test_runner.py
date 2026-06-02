from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List

from .execution_engine import SafeExecutionEngine


class TestRunner:
    def __init__(self, workspace: Path, execution_engine: SafeExecutionEngine) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = execution_engine

    def syntax_test(self) -> Dict[str, object]:
        errors: List[str] = []
        for py in self.workspace.rglob("*.py"):
            if any(part in {".git", "__pycache__", "build", "dist"} for part in py.parts):
                continue
            try:
                ast.parse(py.read_text(encoding="utf-8-sig", errors="ignore"))
            except SyntaxError as exc:
                errors.append(f"{py.relative_to(self.workspace)}:{exc.lineno}:{exc.msg}")
        return {"status": "success" if not errors else "error", "errors": errors}

    def import_test(self, modules: List[str]) -> Dict[str, object]:
        failed: List[str] = []
        for m in modules:
            r = self.exec.run(["python", "-c", f"import {m}"], timeout_sec=20)
            if r.return_code != 0:
                failed.append(m)
        return {"status": "success" if not failed else "error", "failed": failed}

    def runtime_test(self, command: List[str], timeout_sec: int = 90) -> Dict[str, object]:
        r = self.exec.run(command, cwd=self.workspace, timeout_sec=timeout_sec)
        return {
            "status": "success" if r.return_code == 0 and not r.timed_out else "error",
            "return_code": r.return_code,
            "timed_out": r.timed_out,
            "stdout": r.stdout,
            "stderr": r.stderr,
            "metrics": r.metrics,
            "log_file": r.log_file,
        }

    def build_test(self, command: List[str], timeout_sec: int = 1800) -> Dict[str, object]:
        return self.runtime_test(command, timeout_sec=timeout_sec)
