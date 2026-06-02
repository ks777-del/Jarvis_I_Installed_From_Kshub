from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class PlannedTask:
    id: str
    title: str
    priority: int
    depends_on: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass
class PlanResult:
    goal: str
    tasks: List[PlannedTask]

    def to_dict(self) -> Dict[str, object]:
        return {"goal": self.goal, "tasks": [task.to_dict() for task in self.tasks]}


class EngineeringPlanner:
    def create_plan(self, request: str) -> PlanResult:
        text = str(request or "").strip()
        if not text:
            return PlanResult(goal="", tasks=[])

        low = text.lower()
        tasks: List[PlannedTask] = [
            PlannedTask("analyze", "Analyze architecture and runtime constraints", 1, [], "Prevent unsafe edits by understanding context first."),
            PlannedTask("context", "Build project context graph", 2, ["analyze"], "Enable multi-file reasoning and tracing."),
            PlannedTask("design", "Design safe implementation strategy", 3, ["context"], "Preserve stable systems and avoid regressions."),
        ]

        if any(k in low for k in ["game", "3d", "physics", "npc", "multiplayer"]):
            tasks.extend([
                PlannedTask("systems", "Generate gameplay systems", 4, ["design"], "Implement runtime game loop, input, and domain systems."),
                PlannedTask("assets", "Wire asset and dependency setup", 5, ["systems"], "Prevent runtime asset/dependency failures."),
            ])
        else:
            tasks.append(
                PlannedTask("implementation", "Implement requested feature set", 4, ["design"], "Deliver production-grade modular implementation.")
            )

        tasks.extend([
            PlannedTask("patch", "Apply dependency-aware multi-file patch", 6, ["implementation" if not any(k in low for k in ["game", "3d", "physics", "npc", "multiplayer"]) else "assets"], "Atomic edits with backups and rollback path."),
            PlannedTask("deps", "Validate and install dependencies", 7, ["patch"], "Runtime stability requires dependency consistency."),
            PlannedTask("build", "Compile/build artifacts", 8, ["deps"], "Ensure distributable output quality."),
            PlannedTask("test", "Run runtime and regression validation", 9, ["build"], "Verify behavior and prevent regressions."),
            PlannedTask("report", "Publish build/debug report", 10, ["test"], "Developer experience and traceability."),
        ])

        tasks = sorted(tasks, key=lambda x: x.priority)
        return PlanResult(goal=text, tasks=tasks)
