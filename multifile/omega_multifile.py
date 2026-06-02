from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.multi_file_editor import MultiFileEditor
from modules.code_engine.core.patch_engine import PatchEngine


class OmegaMultiFileEngine:
    def __init__(self, workspace: Path, backups_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.editor = MultiFileEditor(self.workspace, backups_dir)
        self.patcher = PatchEngine(self.workspace)

    def apply_change_set(self, changes: Dict[str, str]) -> Dict[str, object]:
        results = self.editor.apply_changes(changes)
        return {
            "status": "success",
            "files_changed": len(results),
            "patches": [r.to_dict() for r in results],
        }

    def semantic_replace(self, file_path: str, source: str, target: str) -> Dict[str, object]:
        result = self.patcher.apply_replace(file_path, source, target)
        return result.to_dict()
