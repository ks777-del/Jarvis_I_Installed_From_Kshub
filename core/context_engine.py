from __future__ import annotations

import ast
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class SymbolInfo:
    module: str
    name: str
    kind: str
    line: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ContextEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.symbols: List[SymbolInfo] = []
        self.module_dependencies: Dict[str, Set[str]] = {}

    def index(self) -> Dict[str, object]:
        self.symbols = []
        self.module_dependencies = {}
        for py_file in self.workspace.rglob("*.py"):
            if any(part in {".git", "__pycache__", "build", "dist"} for part in py_file.parts):
                continue
            self._index_python_file(py_file)

        return {
            "symbol_count": len(self.symbols),
            "modules": len(self.module_dependencies),
            "dependencies": {k: sorted(v) for k, v in self.module_dependencies.items()},
        }

    def trace_symbol(self, symbol_name: str) -> List[Dict[str, object]]:
        q = str(symbol_name or "").strip()
        return [s.to_dict() for s in self.symbols if s.name == q]

    def module_context(self, module_name: str) -> Dict[str, object]:
        key = str(module_name or "").strip()
        return {
            "module": key,
            "dependencies": sorted(self.module_dependencies.get(key, set())),
            "symbols": [s.to_dict() for s in self.symbols if s.module == key],
        }

    def _index_python_file(self, file_path: Path) -> None:
        rel = file_path.relative_to(self.workspace)
        module = ".".join(rel.with_suffix("").parts)
        self.module_dependencies[module] = set()

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8-sig", errors="ignore"))
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.symbols.append(SymbolInfo(module, node.name, "function", node.lineno))
            elif isinstance(node, ast.AsyncFunctionDef):
                self.symbols.append(SymbolInfo(module, node.name, "async_function", node.lineno))
            elif isinstance(node, ast.ClassDef):
                self.symbols.append(SymbolInfo(module, node.name, "class", node.lineno))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.module_dependencies[module].add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.module_dependencies[module].add(node.module)
