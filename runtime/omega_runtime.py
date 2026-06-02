from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.execution_engine import SafeExecutionEngine
from modules.code_engine.core.sandbox import SandboxEngine


class OmegaRuntimeEngine:
    def __init__(self, workspace: Path, sandbox_dir: Path, logs_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.sandbox = SandboxEngine(sandbox_dir)
        self.exec = SafeExecutionEngine(self.workspace, logs_dir)

    def run_isolated(self, command: List[str], timeout_sec: int = 120) -> Dict[str, object]:
        session = self.sandbox.create_session()
        try:
            result = self.exec.run(command, timeout_sec=timeout_sec)
            data = result.to_dict()
            data["sandbox_session"] = session.to_dict()
            return data
        finally:
            self.sandbox.cleanup(session)
