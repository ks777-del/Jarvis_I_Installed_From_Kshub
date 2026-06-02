from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List


BLOCKED_PATTERNS = [
    "rm -rf",
    "del /f",
    "format ",
    "shutdown",
    "reboot",
    "diskpart",
    "mkfs",
    "rmdir /s",
    "bcdedit",
]


@dataclass
class SandboxPolicyResult:
    allowed: bool
    reasons: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class SandboxPolicy:
    def __init__(self, workspace: Path) -> None:
        self.workspace = Path(workspace).resolve()

    def validate_command(self, command: List[str]) -> SandboxPolicyResult:
        text = " ".join(command).lower()
        reasons: List[str] = []
        for pattern in BLOCKED_PATTERNS:
            if pattern in text:
                reasons.append(f"Blocked command pattern: {pattern}")
        return SandboxPolicyResult(allowed=not reasons, reasons=reasons)

    def validate_path(self, path: Path) -> SandboxPolicyResult:
        target = Path(path).resolve()
        reasons: List[str] = []
        if not str(target).startswith(str(self.workspace)):
            reasons.append("Path escapes workspace boundary.")
        return SandboxPolicyResult(allowed=not reasons, reasons=reasons)
