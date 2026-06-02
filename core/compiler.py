from __future__ import annotations

import shutil
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from .execution_engine import SafeExecutionEngine


@dataclass
class CompileResult:
    status: str
    command: List[str]
    message: str
    log_file: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class CompilerEngine:
    def __init__(self, workspace: Path, execution_engine: SafeExecutionEngine) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = execution_engine

    def compile_python(self, entry_file: str, name: str = "app") -> CompileResult:
        cmd = ["python", "-m", "PyInstaller", "--noconfirm", "--onefile", "--name", name, entry_file]
        return self._run(cmd)

    def compile_electron(self) -> CompileResult:
        npm = shutil.which("npm")
        if not npm:
            return CompileResult("error", [], "npm not found.", "")
        return self._run([npm, "run", "build"])

    def compile_cpp(self, source_file: str, output_name: str = "app.exe") -> CompileResult:
        gpp = shutil.which("g++")
        if gpp:
            return self._run([gpp, source_file, "-O2", "-o", output_name])
        cl = shutil.which("cl")
        if cl:
            return self._run([cl, source_file, "/EHsc", f"/Fe:{output_name}"])
        return CompileResult("error", [], "No supported C++ compiler found (g++/cl).", "")

    def _run(self, cmd: List[str]) -> CompileResult:
        r = self.exec.run(cmd, cwd=self.workspace, timeout_sec=1800)
        if r.timed_out:
            return CompileResult("error", cmd, "Build timed out.", r.log_file)
        if r.return_code != 0:
            return CompileResult("error", cmd, (r.stderr or r.stdout or "Build failed.").strip(), r.log_file)
        return CompileResult("success", cmd, "Build completed.", r.log_file)
