from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.debugger import DebuggerEngine
from modules.code_engine.core.execution_engine import SafeExecutionEngine


class OmegaDebuggingEngine:
    def __init__(self, workspace: Path, logs_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = SafeExecutionEngine(self.workspace, logs_dir)
        self.debugger = DebuggerEngine(self.workspace, self.exec)

    def deep_debug(self, command: List[str]) -> Dict[str, object]:
        report = self.debugger.debug(command)
        report["workflow"] = [
            "Reproduce",
            "Capture Runtime Logs",
            "Trace Execution",
            "Build Failure Graph",
            "Identify Root Cause",
            "Generate Minimal Safe Fix",
            "Run Regression Tests",
        ]
        return report
