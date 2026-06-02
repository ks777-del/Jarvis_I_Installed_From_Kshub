from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .build import OmegaBuildEngine
from .debugging import OmegaDebuggingEngine
from .generation import OmegaGenerationEngine
from .intelligence import ProjectIntelligenceEngine
from .multifile import OmegaMultiFileEngine
from .reasoning import OmegaReasoningEngine
from .runtime import OmegaRuntimeEngine
from .self_healing import OmegaSelfHealingEngine
from .ui import OmegaUIModel


@dataclass
class OmegaRequest:
    prompt: str
    runtime_command: Optional[List[str]] = None


class JarvisOmegaPlatform:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.root = Path(__file__).resolve().parent

        self.intelligence = ProjectIntelligenceEngine(self.workspace)
        self.reasoning = OmegaReasoningEngine(self.workspace)
        self.generation = OmegaGenerationEngine(self.workspace, self.root / "templates", self.root / "models")
        self.multifile = OmegaMultiFileEngine(self.workspace, self.root / "backups")
        self.debugging = OmegaDebuggingEngine(self.workspace, self.root / "logs")
        self.runtime = OmegaRuntimeEngine(self.workspace, self.root / "sandbox", self.root / "logs")
        self.build = OmegaBuildEngine(self.workspace, self.root / "logs")
        self.self_healing = OmegaSelfHealingEngine(self.workspace, self.root / "logs")
        self.ui = OmegaUIModel()

    def execute(self, request: OmegaRequest) -> Dict[str, object]:
        prompt = str(request.prompt or "").strip()
        if not prompt:
            return {"status": "error", "message": "Prompt is required."}

        snapshot = self.intelligence.build_snapshot().to_dict()
        plan = self.reasoning.reason(prompt).to_dict()
        generation = self.generation.generate(prompt)

        runtime = None
        if request.runtime_command:
            runtime = self.runtime.run_isolated(request.runtime_command)

        return {
            "status": "success",
            "intelligence": snapshot,
            "reasoning": plan,
            "generation": generation,
            "runtime": runtime,
            "ui_schema": self.ui.dashboard_schema(),
        }
