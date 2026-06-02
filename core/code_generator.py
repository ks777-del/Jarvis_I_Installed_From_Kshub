from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class GeneratedArtifact:
    path: str
    content: str


class CodeGeneratorEngine:
    def __init__(self, workspace: Path, templates_dir: Path, models_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.templates_dir = Path(templates_dir).resolve()
        self.models_dir = Path(models_dir).resolve()

    def generate_from_request(self, request: str) -> List[GeneratedArtifact]:
        low = str(request or "").lower()
        template_name = "python_project.json"
        if any(k in low for k in ["electron", "desktop app"]):
            template_name = "electron_app.json"
        elif any(k in low for k in ["game", "3d", "pygame", "godot", "three"]):
            template_name = "game_engine.json"
        elif any(k in low for k in ["web", "frontend", "html", "site"]):
            template_name = "web_app.json"
        elif any(k in low for k in ["tool", "utility", "automation"]):
            template_name = "desktop_tool.json"

        template = self._load_json(self.templates_dir / template_name)
        artifacts: List[GeneratedArtifact] = []
        for item in template.get("files", []):
            path = str(item.get("path", "")).strip()
            content = str(item.get("content", ""))
            if path:
                artifacts.append(GeneratedArtifact(path=path, content=content))
        return artifacts

    def write_artifacts(self, artifacts: List[GeneratedArtifact]) -> List[str]:
        written: List[str] = []
        for artifact in artifacts:
            target = (self.workspace / artifact.path).resolve()
            if not str(target).startswith(str(self.workspace)):
                raise ValueError(f"Path escape blocked: {artifact.path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(artifact.content, encoding="utf-8")
            written.append(str(target))
        return written

    def _load_json(self, path: Path) -> Dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))
