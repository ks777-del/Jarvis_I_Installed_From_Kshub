from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

from .analyzer import ProjectAnalyzer
from .context_engine import ContextEngine
from .planner import EngineeringPlanner


@dataclass
class ReasoningResult:
    intent: str
    context_summary: Dict[str, object]
    plan: Dict[str, object]
    dependency_risks: List[str]
    execution_risks: List[str]
    safe_execution_plan: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ReasoningEngine:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()
        self.analyzer = ProjectAnalyzer(self.workspace)
        self.context = ContextEngine(self.workspace)
        self.planner = EngineeringPlanner()

    def reason(self, request: str) -> ReasoningResult:
        analysis = self.analyzer.analyze().to_dict()
        context_map = self.context.index()
        plan = self.planner.create_plan(request).to_dict()

        dep_risks: List[str] = []
        if not analysis.get("dependencies"):
            dep_risks.append("No explicit dependency manifest detected; environment drift risk is high.")

        exec_risks = list(analysis.get("runtime_risks") or [])
        if context_map.get("modules", 0) > 120:
            exec_risks.append("Large project index detected; prioritize incremental patch strategy.")

        safe_steps = [
            "Parse intent with architecture preservation constraints.",
            "Use context graph and module dependency map for targeted edits.",
            "Run security validation before any command execution.",
            "Apply patch atomically with backup and rollback metadata.",
            "Validate syntax, runtime, and build outputs before finalization.",
        ]

        summary = dict(analysis)
        summary["context_index"] = context_map

        return ReasoningResult(
            intent=str(request or "").strip(),
            context_summary=summary,
            plan=plan,
            dependency_risks=dep_risks,
            execution_risks=exec_risks,
            safe_execution_plan=safe_steps,
        )
