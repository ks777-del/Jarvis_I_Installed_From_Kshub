from __future__ import annotations

from pathlib import Path
from typing import Dict

from modules.code_engine.core.build_validator import BuildValidator
from modules.code_engine.core.compiler import CompilerEngine
from modules.code_engine.core.execution_engine import SafeExecutionEngine


class OmegaBuildEngine:
    def __init__(self, workspace: Path, logs_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = SafeExecutionEngine(self.workspace, logs_dir)
        self.compiler = CompilerEngine(self.workspace, self.exec)
        self.validator = BuildValidator(self.workspace, self.exec)

    def build_python(self, entry_file: str, name: str = "omega_app") -> Dict[str, object]:
        build = self.compiler.compile_python(entry_file, name=name).to_dict()
        return {"build": build}

    def validate_bundle(self, build_dir: str) -> Dict[str, object]:
        return self.validator.validate_asset_bundle(build_dir)
