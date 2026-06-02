from __future__ import annotations

import difflib
import shutil
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict


@dataclass
class EditResult:
    path: str
    backup_path: str
    diff: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class SafeFileEditor:
    def __init__(self, workspace: Path, cache_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.cache_dir = Path(cache_dir).resolve()
        self.backup_dir = self.cache_dir / "file_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def edit_file(self, relative_path: str, new_content: str) -> EditResult:
        target = (self.workspace / relative_path).resolve()
        if not str(target).startswith(str(self.workspace)):
            raise ValueError("File edit outside workspace is blocked.")

        before = ""
        if target.exists():
            before = target.read_text(encoding="utf-8", errors="ignore")

        stamp = int(time.time() * 1000)
        backup = self.backup_dir / f"{target.name}.{stamp}.bak"
        if target.exists():
            shutil.copy2(target, backup)
        else:
            backup.write_text("", encoding="utf-8")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_content, encoding="utf-8")

        diff = "\n".join(
            difflib.unified_diff(
                before.splitlines(),
                new_content.splitlines(),
                fromfile=f"before/{relative_path}",
                tofile=f"after/{relative_path}",
                lineterm="",
            )
        )
        return EditResult(path=str(target), backup_path=str(backup), diff=diff)

    def rollback(self, backup_path: str, target_relative_path: str) -> str:
        backup = Path(backup_path).resolve()
        target = (self.workspace / target_relative_path).resolve()
        if not backup.exists():
            raise FileNotFoundError("Backup not found.")
        if not str(target).startswith(str(self.workspace)):
            raise ValueError("Rollback target outside workspace is blocked.")

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
        return str(target)
