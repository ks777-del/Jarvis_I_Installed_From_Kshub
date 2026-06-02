from __future__ import annotations

import ast
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


LANG_EXTENSIONS = {
    "python": {".py"},
    "javascript": {".js", ".mjs", ".cjs"},
    "typescript": {".ts", ".tsx"},
    "cpp": {".cpp", ".cc", ".cxx", ".hpp", ".h"},
    "html_css": {".html", ".css"},
    "scratch": {".sb3"},
    "json": {".json"},
}

STDLIB_PREFIXES = {
    "os", "sys", "json", "time", "typing", "pathlib", "subprocess", "threading",
    "re", "math", "random", "collections", "dataclasses", "traceback", "asyncio", "functools",
}


@dataclass
class ProjectAnalysis:
    language: str
    framework: str
    architecture: str
    entry_points: List[str]
    dependencies: List[str]
    runtime_risks: List[str]
    optimization_targets: List[str]
    module_relationships: Dict[str, List[str]]
    build_systems: List[str]
    duplicated_logic_candidates: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ProjectAnalyzer:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()

    def analyze(self) -> ProjectAnalysis:
        files = self._scan_files()
        language = self._primary_language(files)
        framework = self._detect_framework(files)
        architecture = self._detect_architecture(files)
        entry_points = self._detect_entry_points(files)
        dependencies = sorted(self._detect_dependencies(files))
        build_systems = self._detect_build_systems(files)

        module_graph, async_counts = self._python_module_graph(files)
        circular = self._find_cycles(module_graph)
        duplicate_candidates = self._duplicate_logic_candidates(files)
        runtime_risks = self._runtime_risks(circular, files, async_counts)
        optimization_targets = self._optimization_targets(files, async_counts)

        relationships = {
            module: sorted(deps)
            for module, deps in sorted(module_graph.items())
            if deps
        }

        return ProjectAnalysis(
            language=language,
            framework=framework,
            architecture=architecture,
            entry_points=entry_points,
            dependencies=dependencies,
            runtime_risks=runtime_risks,
            optimization_targets=optimization_targets,
            module_relationships=relationships,
            build_systems=build_systems,
            duplicated_logic_candidates=duplicate_candidates,
        )

    def _scan_files(self) -> List[Path]:
        ignored = {".git", "__pycache__", "node_modules", "dist", "build"}
        return [
            p for p in self.workspace.rglob("*")
            if p.is_file() and not any(part in ignored for part in p.parts)
        ]

    def _primary_language(self, files: List[Path]) -> str:
        counter = Counter()
        for f in files:
            for lang, exts in LANG_EXTENSIONS.items():
                if f.suffix.lower() in exts:
                    counter[lang] += 1
        return counter.most_common(1)[0][0] if counter else "unknown"

    def _detect_framework(self, files: List[Path]) -> str:
        names = {f.name.lower() for f in files}
        req_text = self._requirements_text().lower()

        if "manage.py" in names:
            return "django"
        if "fastapi" in req_text:
            return "fastapi"
        if "flask" in req_text:
            return "flask"
        if "package.json" in names:
            pkg = self._read_json(self.workspace / "package.json")
            deps = set((pkg.get("dependencies") or {}).keys()) | set((pkg.get("devDependencies") or {}).keys())
            if "electron" in deps:
                return "electron"
            if "@tauri-apps/api" in deps:
                return "tauri"
            if "three" in deps:
                return "threejs"
            if "react" in deps:
                return "react"
            return "node"
        return "custom"

    def _detect_architecture(self, files: List[Path]) -> str:
        paths = [str(f.relative_to(self.workspace)).lower() for f in files]
        if any("/core/" in p or "\\core\\" in p for p in paths):
            return "modular"
        if any("controller" in p for p in paths) and any("service" in p for p in paths):
            return "layered"
        return "monolithic"

    def _detect_entry_points(self, files: List[Path]) -> List[str]:
        candidates = [
            "main.py", "app.py", "index.js", "main.js", "src/main.ts", "main.cpp", "index.html"
        ]
        found: List[str] = []
        for c in candidates:
            p = self.workspace / c
            if p.exists():
                found.append(str(p.relative_to(self.workspace)))
        return found

    def _detect_dependencies(self, files: List[Path]) -> Set[str]:
        deps: Set[str] = set()
        req = self.workspace / "requirements.txt"
        if req.exists():
            for line in req.read_text(encoding="utf-8", errors="ignore").splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                deps.add(s.split("==", 1)[0].split(">=", 1)[0].strip())

        package_json = self.workspace / "package.json"
        if package_json.exists():
            data = self._read_json(package_json)
            for bucket in ("dependencies", "devDependencies"):
                deps.update((data.get(bucket) or {}).keys())
        return deps

    def _detect_build_systems(self, files: List[Path]) -> List[str]:
        names = {f.name.lower() for f in files}
        systems: List[str] = []
        if "pyproject.toml" in names or "setup.py" in names:
            systems.append("python_build")
        if any(name.endswith(".spec") for name in names):
            systems.append("pyinstaller")
        if "package.json" in names:
            systems.append("npm")
        if "cmakelists.txt" in names:
            systems.append("cmake")
        if "makefile" in names:
            systems.append("make")
        if "installer.iss" in names:
            systems.append("inno_setup")
        return systems

    def _python_module_graph(self, files: List[Path]) -> Tuple[Dict[str, Set[str]], Dict[str, int]]:
        py_files = [f for f in files if f.suffix.lower() == ".py"]
        graph: Dict[str, Set[str]] = {}
        async_counts: Dict[str, int] = defaultdict(int)

        for file_path in py_files:
            rel = file_path.relative_to(self.workspace)
            module = ".".join(rel.with_suffix("").parts)
            graph[module] = set()
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8-sig", errors="ignore"))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        graph[module].add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    graph[module].add(node.module)
                elif isinstance(node, ast.AsyncFunctionDef):
                    async_counts[module] += 1

        return graph, async_counts

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        visited: Set[str] = set()
        stack: Set[str] = set()
        route: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str) -> None:
            visited.add(node)
            stack.add(node)
            route.append(node)
            for dep in graph.get(node, set()):
                if dep not in graph:
                    continue
                if dep not in visited:
                    dfs(dep)
                elif dep in stack:
                    idx = route.index(dep)
                    cycles.append(route[idx:] + [dep])
            stack.remove(node)
            route.pop()

        for node in graph:
            if node not in visited:
                dfs(node)
        return cycles

    def _runtime_risks(self, cycles: List[List[str]], files: List[Path], async_counts: Dict[str, int]) -> List[str]:
        risks: List[str] = []
        for cycle in cycles:
            risks.append("Circular dependency: " + " -> ".join(cycle))

        large_files = [f for f in files if f.suffix.lower() == ".py" and self._line_count(f) > 900]
        for f in large_files:
            risks.append(f"Large module risk: {f.relative_to(self.workspace)}")

        if not async_counts:
            risks.append("No async workflows detected; long tasks may block UI/runtime.")
        return risks

    def _optimization_targets(self, files: List[Path], async_counts: Dict[str, int]) -> List[str]:
        targets: List[str] = []
        for f in files:
            if f.suffix.lower() == ".py" and self._line_count(f) > 700:
                targets.append(f"Split heavy module: {f.relative_to(self.workspace)}")
        for module, count in async_counts.items():
            if count > 20:
                targets.append(f"High async complexity review: {module}")
        return targets

    def _duplicate_logic_candidates(self, files: List[Path]) -> List[str]:
        signatures: Dict[str, List[str]] = defaultdict(list)
        for f in files:
            if f.suffix.lower() != ".py":
                continue
            text = f.read_text(encoding="utf-8-sig", errors="ignore")
            sample = "\n".join([line.strip() for line in text.splitlines() if line.strip()][:30])
            if sample:
                signatures[sample].append(str(f.relative_to(self.workspace)))
        return [", ".join(v) for v in signatures.values() if len(v) > 1]

    def _line_count(self, path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8-sig", errors="ignore").splitlines())
        except Exception:
            return 0

    def _requirements_text(self) -> str:
        req = self.workspace / "requirements.txt"
        return req.read_text(encoding="utf-8", errors="ignore") if req.exists() else ""

    def _read_json(self, path: Path) -> Dict[str, object]:
        try:
            return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return {}
