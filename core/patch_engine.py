from __future__ import annotations

import difflib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict


@dataclass
class PatchResult:
    file: str
    changed: bool
    diff: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class PatchEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()

    def apply_replace(self, relative_file: str, find_text: str, replace_text: str) -> PatchResult:
        path = (self.workspace / relative_file).resolve()
        if not str(path).startswith(str(self.workspace)) or not path.exists():
            return PatchResult(relative_file, False, "")

        old = path.read_text(encoding="utf-8", errors="ignore")
        new = old.replace(find_text, replace_text)
        changed = new != old
        if changed:
            path.write_text(new, encoding="utf-8")

        diff = "\n".join(
            difflib.unified_diff(
                old.splitlines(),
                new.splitlines(),
                fromfile=f"before/{relative_file}",
                tofile=f"after/{relative_file}",
                lineterm="",
            )
        )
        return PatchResult(relative_file, changed, diff)
