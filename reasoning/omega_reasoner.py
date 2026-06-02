from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from modules.code_engine.intelligence import ProjectIntelligenceEngine
from modules.code_engine.core.planner import EngineeringPlanner


@dataclass
class ReasoningPlan:
    intent: str
    architecture_risks: List[str]
    predicted_regressions: List[str]
    execution_plan: List[str]
    tasks: List[Dict[str, object]]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class OmegaReasoningEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.intelligence = ProjectIntelligenceEngine(self.workspace)
        self.planner = EngineeringPlanner()

    def reason(self, request: str) -> ReasoningPlan:
        req = str(request or "").strip()
        snapshot = self.intelligence.build_snapshot().to_dict()
        analysis = snapshot.get("analysis") or {}
        runtime_risks = list(analysis.get("runtime_risks") or [])

        regressions: List[str] = []
        if any("main.py" in ep for ep in analysis.get("entry_points", [])):
            regressions.append("Primary entrypoint changes may impact startup behavior.")
        if snapshot.get("communication_paths"):
            regressions.append("UI bridge modules detected; verify frontend-backend messaging after edits.")

        plan = self.planner.create_plan(req).to_dict()
        execution_plan = [
            "Analyze architecture and context graph.",
            "Generate dependency-aware change set.",
            "Apply patches with backup + rollback metadata.",
            "Run syntax/runtime/build validation.",
            "Run regression checks on impacted pathways.",
        ]

        return ReasoningPlan(
            intent=req,
            architecture_risks=runtime_risks,
            predicted_regressions=regressions,
            execution_plan=execution_plan,
            tasks=plan.get("tasks", []),
        )
