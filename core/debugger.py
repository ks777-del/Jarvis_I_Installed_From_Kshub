from __future__ import annotations

import ast
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from .execution_engine import SafeExecutionEngine


@dataclass
class DebugIssue:
    file: str
    issue_type: str
    message: str
    severity: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class DebuggerEngine:
    def __init__(self, workspace: Path, execution_engine: SafeExecutionEngine) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = execution_engine

    def scan_static(self) -> List[DebugIssue]:
        issues: List[DebugIssue] = []
        for py_file in self.workspace.rglob("*.py"):
            if any(part in {".git", "__pycache__", "build", "dist"} for part in py_file.parts):
                continue
            try:
                ast.parse(py_file.read_text(encoding="utf-8-sig", errors="ignore"))
            except SyntaxError as exc:
                issues.append(DebugIssue(str(py_file.relative_to(self.workspace)), "syntax_error", f"{exc.msg} at line {exc.lineno}", "high"))
        return issues

    def reproduce_runtime(self, command: List[str], timeout_sec: int = 90) -> Dict[str, object]:
        result = self.exec.run(command, timeout_sec=timeout_sec)
        status = "success" if result.return_code == 0 and not result.timed_out else "error"
        return {
            "status": status,
            "return_code": result.return_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": result.timed_out,
            "metrics": result.metrics,
            "log_file": result.log_file,
        }

    def debug(self, command: List[str]) -> Dict[str, object]:
        runtime = self.reproduce_runtime(command)
        static_issues = [i.to_dict() for i in self.scan_static()]
        root_cause = "Runtime command failed." if runtime.get("status") != "success" else "No runtime failure."
        return {
            "runtime": runtime,
            "static_issues": static_issues,
            "root_cause_summary": root_cause,
            "recommended_fix_strategy": "Apply minimal targeted patch, then rerun runtime and syntax validation.",
        }
