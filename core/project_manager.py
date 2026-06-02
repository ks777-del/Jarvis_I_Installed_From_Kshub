from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Dict, List


class ProjectManager:
    def __init__(self, workspace: Path, cache_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.cache_dir = Path(cache_dir).resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in name).strip("_")
        if not safe:
            safe = f"project_{int(time.time())}"
        path = self.workspace / safe
        path.mkdir(parents=True, exist_ok=True)
        return path

    def backup_file(self, file_path: Path) -> Path:
        src = Path(file_path).resolve()
        if not src.exists():
            raise FileNotFoundError(src)
        backup_dir = self.cache_dir / "project_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        dst = backup_dir / f"{src.name}.{int(time.time() * 1000)}.bak"
        shutil.copy2(src, dst)
        return dst

    def cleanup(self, older_than_sec: int = 86400) -> List[str]:
        removed: List[str] = []
        threshold = time.time() - older_than_sec
        for f in self.cache_dir.rglob("*"):
            if f.is_file() and f.stat().st_mtime < threshold:
                f.unlink(missing_ok=True)
                removed.append(str(f))
        return removed

    def workspace_tree(self, depth: int = 2) -> Dict[str, object]:
        root = self.workspace
        nodes: List[str] = []
        for p in root.rglob("*"):
            rel = p.relative_to(root)
            if len(rel.parts) <= depth:
                nodes.append(str(rel))
        return {"root": str(root), "nodes": sorted(nodes)}
