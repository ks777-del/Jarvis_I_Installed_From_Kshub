from __future__ import annotations

import difflib
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


@dataclass
class FilePatchResult:
    path: str
    backup: str
    diff: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class MultiFileEditor:
    def __init__(self, workspace: Path, backups_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.backups_dir = Path(backups_dir).resolve()
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    def apply_changes(self, changes: Dict[str, str]) -> List[FilePatchResult]:
        results: List[FilePatchResult] = []
        for rel, new_content in changes.items():
            target = (self.workspace / rel).resolve()
            if not str(target).startswith(str(self.workspace)):
                raise ValueError(f"Path escape blocked: {rel}")

            old = target.read_text(encoding="utf-8", errors="ignore") if target.exists() else ""
            backup = self._backup(target, old)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new_content, encoding="utf-8")
            diff = "\n".join(
                difflib.unified_diff(
                    old.splitlines(),
                    new_content.splitlines(),
                    fromfile=f"before/{rel}",
                    tofile=f"after/{rel}",
                    lineterm="",
                )
            )
            results.append(FilePatchResult(str(target), str(backup), diff))
        return results

    def rollback(self, patch_results: List[FilePatchResult]) -> None:
        for patch in patch_results:
            backup = Path(patch.backup)
            target = Path(patch.path)
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)

    def _backup(self, target: Path, content: str) -> Path:
        stamp = int(time.time() * 1000)
        b = self.backups_dir / f"{target.name}.{stamp}.bak"
        b.write_text(content, encoding="utf-8")
        return b
