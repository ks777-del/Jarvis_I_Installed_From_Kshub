from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class UIPanel:
    id: str
    title: str
    features: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class OmegaUIModel:
    def dashboard_schema(self) -> Dict[str, object]:
        panels = [
            UIPanel("generation_stream", "Live Generation Stream", ["token stream", "phase logs", "context snippets"]),
            UIPanel("architecture_map", "Architecture Visualizer", ["module graph", "dependency graph", "entry points"]),
            UIPanel("runtime_console", "Runtime Console", ["stdout", "stderr", "event timeline"]),
            UIPanel("patch_review", "Patch Review", ["diff viewer", "rollback", "approval status"]),
            UIPanel("build_monitor", "Build Monitor", ["build queue", "artifacts", "validation status"]),
            UIPanel("perf_monitor", "Performance Monitor", ["cpu", "memory", "latency", "alerts"]),
        ]
        return {
            "platform": "JARVIS OMEGA",
            "panels": [p.to_dict() for p in panels],
            "required_interactions": [
                "start_generation",
                "view_reasoning",
                "inspect_patch",
                "run_validation",
                "download_executable",
            ],
        }
