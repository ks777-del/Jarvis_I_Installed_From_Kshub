from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.patch_engine import PatchEngine
from modules.code_engine.core.test_runner import TestRunner
from modules.code_engine.core.execution_engine import SafeExecutionEngine


class OmegaSelfHealingEngine:
    def __init__(self, workspace: Path, logs_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = SafeExecutionEngine(self.workspace, logs_dir)
        self.tests = TestRunner(self.workspace, self.exec)
        self.patcher = PatchEngine(self.workspace)

    def heal_import_failure(self, file_path: str, bad_import: str, fixed_import: str) -> Dict[str, object]:
        patch = self.patcher.apply_replace(file_path, bad_import, fixed_import).to_dict()
        syntax = self.tests.syntax_test()
        return {
            "patch": patch,
            "syntax_validation": syntax,
            "status": "success" if patch.get("changed") and syntax.get("status") == "success" else "error",
        }

    def heal_and_retest(self, command: List[str]) -> Dict[str, object]:
        runtime = self.tests.runtime_test(command)
        if runtime.get("status") == "success":
            return {"status": "success", "runtime": runtime}
        syntax = self.tests.syntax_test()
        return {"status": "error", "runtime": runtime, "syntax": syntax}
