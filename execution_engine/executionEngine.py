from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class UniversalExecutionEngine:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir or Path(__file__).resolve().parents[2]).resolve()
        self.executables_dir = self.base_dir / "executables"
        self.executables_dir.mkdir(parents=True, exist_ok=True)

    def clean_project(self, project_path: Path) -> Dict[str, str]:
        project_path = Path(project_path)
        removed = []
        for folder in ("node_modules", ".git", "The-Ultimate-HTML-Course-main"):
            target = project_path / folder
            if target.exists() and target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                removed.append(str(target))
        return {"status": "success", "removed": json.dumps(removed)}

    def build_executable(self, source_path: Path, project_name: Optional[str] = None) -> Dict[str, str]:
        source_path = Path(source_path)
        if not source_path.exists():
            return {"status": "error", "message": f"Source file not found: {source_path}"}

        name = (project_name or source_path.stem).strip().replace(" ", "_")
        output_path = self.executables_dir / f"{name}.exe"

        suffix = source_path.suffix.lower()
        if suffix == ".py":
            return self._build_python(source_path, name, output_path)
        if suffix == ".js":
            return self._build_javascript(source_path, name, output_path)
        if suffix in {".sb3", ".scratch"}:
            return {
                "status": "error",
                "message": "Scratch export build is not automated yet. Please provide a packaged runtime executable.",
            }
        return {"status": "error", "message": f"Unsupported source type: {suffix}"}

    def run_executable(self, project_name: str) -> Dict[str, str]:
        name = str(project_name or "").strip().replace(" ", "_")
        if not name:
            return {"status": "error", "message": "Project name is required."}
        exe_path = (self.executables_dir / f"{name}.exe").resolve()
        if not exe_path.exists():
            # Defensive fallback for callers using relative base paths.
            alt = (Path.cwd() / "executables" / f"{name}.exe").resolve()
            if alt.exists():
                exe_path = alt
            else:
                return {"status": "error", "message": f"Executable not found: {exe_path}"}

        try:
            proc = subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent), shell=False)
            try:
                code = proc.wait(timeout=2)
                if code != 0:
                    return {"status": "error", "message": f"Execution failed for {name}. Exit code {code}."}
            except subprocess.TimeoutExpired:
                pass
            return {"status": "success", "message": f"Running {name}", "path": str(exe_path)}
        except Exception as exc:
            return {"status": "error", "message": f"Failed to run {name}: {exc}"}

    def _build_python(self, source_path: Path, name: str, output_path: Path) -> Dict[str, str]:
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--onefile",
            "--name",
            name,
            str(source_path),
            "--distpath",
            str(self.executables_dir),
            "--workpath",
            str(self.base_dir / "build" / f"exec_{name}"),
            "--specpath",
            str(self.base_dir / "build" / "exec_specs"),
        ]
        return self._run_build(cmd, output_path)

    def _build_javascript(self, source_path: Path, name: str, output_path: Path) -> Dict[str, str]:
        pkg = shutil.which("pkg")
        nexe = shutil.which("nexe")

        if pkg:
            cmd = [pkg, str(source_path), "--targets", "node18-win-x64", "--output", str(output_path)]
            return self._run_build(cmd, output_path)

        if nexe:
            cmd = [nexe, str(source_path), "-o", str(output_path)]
            return self._run_build(cmd, output_path)

        return {
            "status": "error",
            "message": "No JavaScript packager found. Install pkg or nexe.",
        }

    def _run_build(self, cmd, output_path: Path) -> Dict[str, str]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": (result.stderr or result.stdout or "Build failed").strip(),
                }
            if not output_path.exists():
                return {"status": "error", "message": f"Build finished but missing file: {output_path}"}
            return {"status": "success", "message": "Build completed", "path": str(output_path)}
        except Exception as exc:
            return {"status": "error", "message": f"Build exception: {exc}"}
