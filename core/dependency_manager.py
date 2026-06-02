from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

from .execution_engine import SafeExecutionEngine


class DependencyManager:
    def __init__(self, workspace: Path, execution_engine: SafeExecutionEngine) -> None:
        self.workspace = Path(workspace).resolve()
        self.exec = execution_engine

    def detect_missing_python_modules(self, modules: List[str]) -> List[str]:
        missing: List[str] = []
        for mod in modules:
            r = self.exec.run(["python", "-c", f"import {mod}"], timeout_sec=20)
            if r.return_code != 0:
                missing.append(mod)
        return missing

    def install_python(self, packages: List[str]) -> Dict[str, object]:
        if not packages:
            return {"status": "success", "message": "No packages requested."}
        r = self.exec.run(["python", "-m", "pip", "install", *packages], timeout_sec=1200)
        return {"status": "success" if r.return_code == 0 else "error", "stdout": r.stdout, "stderr": r.stderr, "log_file": r.log_file}

    def node_dependencies(self) -> Tuple[List[str], List[str]]:
        pkg = self.workspace / "package.json"
        if not pkg.exists():
            return [], []
        data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
        deps = sorted((data.get("dependencies") or {}).keys())
        dev = sorted((data.get("devDependencies") or {}).keys())
        return deps, dev

    def install_node(self) -> Dict[str, object]:
        npm = shutil.which("npm")
        if not npm:
            return {"status": "error", "message": "npm not found"}
        r = self.exec.run([npm, "install"], cwd=self.workspace, timeout_sec=1800)
        return {"status": "success" if r.return_code == 0 else "error", "stdout": r.stdout, "stderr": r.stderr, "log_file": r.log_file}

    def compiler_support(self) -> Dict[str, bool]:
        return {"g++": bool(shutil.which("g++")), "cl": bool(shutil.which("cl"))}
