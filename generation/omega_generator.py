from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from modules.code_engine.core.code_generator import CodeGeneratorEngine
from modules.code_engine.reasoning import OmegaReasoningEngine


class OmegaGenerationEngine:
    def __init__(self, workspace: Path, templates_dir: Path, models_dir: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.generator = CodeGeneratorEngine(self.workspace, templates_dir, models_dir)
        self.reasoner = OmegaReasoningEngine(self.workspace)

    def generate(self, request: str) -> Dict[str, object]:
        reasoning = self.reasoner.reason(request).to_dict()
        artifacts = self.generator.generate_from_request(request)
        written = self.generator.write_artifacts(artifacts)
        return {
            "reasoning": reasoning,
            "generated_files": written,
            "artifact_count": len(written),
        }
