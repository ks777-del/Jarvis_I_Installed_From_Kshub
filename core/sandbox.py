from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict


@dataclass
class SandboxSession:
    root: str
    input_dir: str
    output_dir: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class SandboxEngine:
    def __init__(self, sandbox_root: Path) -> None:
        self.sandbox_root = Path(sandbox_root).resolve()
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> SandboxSession:
        root = Path(tempfile.mkdtemp(prefix="jarvis_sandbox_", dir=str(self.sandbox_root)))
        input_dir = root / "input"
        output_dir = root / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        return SandboxSession(str(root), str(input_dir), str(output_dir))

    def copy_in(self, session: SandboxSession, source: Path, relative_target: str) -> Path:
        src = Path(source).resolve()
        target = (Path(session.input_dir) / relative_target).resolve()
        if not str(target).startswith(str(Path(session.input_dir).resolve())):
            raise ValueError("Sandbox target path escape blocked.")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        return target

    def cleanup(self, session: SandboxSession) -> None:
        root = Path(session.root)
        if root.exists():
            shutil.rmtree(root, ignore_errors=True)
