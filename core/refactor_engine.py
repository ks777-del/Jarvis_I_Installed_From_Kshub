from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List


class RefactorEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()

    def find_dead_functions(self, target_file: str) -> List[str]:
        path = (self.workspace / target_file).resolve()
        if not path.exists() or not str(path).startswith(str(self.workspace)):
            return []
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        tree = ast.parse(text)
        defs: List[str] = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        dead: List[str] = []
        for name in defs:
            if text.count(name) == 1:
                dead.append(name)
        return dead

    def optimize_imports(self, target_file: str) -> Dict[str, object]:
        path = (self.workspace / target_file).resolve()
        if not path.exists() or not str(path).startswith(str(self.workspace)):
            return {"status": "error", "message": "Invalid target file."}

        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        lines = text.splitlines()
        seen = set()
        out: List[str] = []
        removed = 0
        for line in lines:
            s = line.strip()
            if s.startswith("import ") or s.startswith("from "):
                if s in seen:
                    removed += 1
                    continue
                seen.add(s)
            out.append(line)

        new_text = "\n".join(out) + ("\n" if text.endswith("\n") else "")
        path.write_text(new_text, encoding="utf-8")
        return {"status": "success", "removed_duplicate_imports": removed, "file": str(path)}
