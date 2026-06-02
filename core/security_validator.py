from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


BLOCK_PATTERNS = [
    "rm -rf", "del /f", "format ", "shutdown", "reboot", "diskpart", "mkfs", "rmdir /s", "powershell -enc"
]


@dataclass
class SecurityCheckResult:
    safe: bool
    reasons: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class SecurityValidator:
    def validate_command(self, command: List[str]) -> SecurityCheckResult:
        text = " ".join(command).lower()
        reasons: List[str] = []
        for pattern in BLOCK_PATTERNS:
            if pattern in text:
                reasons.append(f"Blocked pattern detected: {pattern}")
        return SecurityCheckResult(safe=not reasons, reasons=reasons)

    def validate_code(self, code: str) -> SecurityCheckResult:
        text = str(code or "").lower()
        reasons: List[str] = []
        suspicious = ["os.system(", "subprocess.Popen(", "subprocess.run(", "shutil.rmtree("]
        for marker in suspicious:
            if marker.lower() in text:
                reasons.append(f"Potentially unsafe call requires review: {marker}")
        return SecurityCheckResult(safe=not reasons, reasons=reasons)
