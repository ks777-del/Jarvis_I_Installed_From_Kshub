from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.analyzer import ProjectAnalyzer
from modules.code_engine.core.context_engine import ContextEngine


@dataclass
class IntelligenceSnapshot:
    analysis: Dict[str, object]
    context_index: Dict[str, object]
    async_hotspots: List[str]
    communication_paths: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ProjectIntelligenceEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.analyzer = ProjectAnalyzer(self.workspace)
        self.context = ContextEngine(self.workspace)

    def build_snapshot(self) -> IntelligenceSnapshot:
        analysis = self.analyzer.analyze().to_dict()
        context_index = self.context.index()

        async_hotspots: List[str] = []
        for module, deps in (context_index.get("dependencies") or {}).items():
            if any("asyncio" in dep for dep in deps):
                async_hotspots.append(module)

        communication_paths = self._detect_renderer_backend_paths()

        return IntelligenceSnapshot(
            analysis=analysis,
            context_index=context_index,
            async_hotspots=sorted(async_hotspots),
            communication_paths=communication_paths,
        )

    def _detect_renderer_backend_paths(self) -> List[str]:
        paths: List[str] = []
        for py in self.workspace.rglob("*.py"):
            if any(part in {".git", "__pycache__", "build", "dist"} for part in py.parts):
                continue
            text = py.read_text(encoding="utf-8-sig", errors="ignore").lower()
            if "qwebchannel" in text or "webengine" in text or "bridge" in text:
                paths.append(str(py.relative_to(self.workspace)))
        return sorted(paths)

    def export_snapshot(self, out_file: Path) -> Path:
        snap = self.build_snapshot().to_dict()
        out = Path(out_file).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snap, indent=2), encoding="utf-8")
        return out
