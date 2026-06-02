from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict


@dataclass
class SandboxSession:
    id: str
    root: str
    workspace: str
    logs_dir: str
    artifacts_dir: str
    created_at: float

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class SandboxManager:
    def __init__(self, sandbox_root: Path) -> None:
        self.sandbox_root = Path(sandbox_root).resolve()
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    def create(self) -> SandboxSession:
        stamp = int(time.time() * 1000)
        sid = f"sandbox_{stamp}"
        root = Path(tempfile.mkdtemp(prefix=f"{sid}_", dir=str(self.sandbox_root)))
        workspace = root / "workspace"
        logs = root / "logs"
        artifacts = root / "artifacts"
        workspace.mkdir(parents=True, exist_ok=True)
        logs.mkdir(parents=True, exist_ok=True)
        artifacts.mkdir(parents=True, exist_ok=True)
        return SandboxSession(
            id=sid,
            root=str(root),
            workspace=str(workspace),
            logs_dir=str(logs),
            artifacts_dir=str(artifacts),
            created_at=time.time(),
        )

    def cleanup(self, session: SandboxSession) -> None:
        root = Path(session.root)
        if root.exists():
            for p in sorted(root.rglob("*"), reverse=True):
                if p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    try:
                        p.rmdir()
                    except OSError:
                        pass
            try:
                root.rmdir()
            except OSError:
                pass
