from __future__ import annotations

from typing import Callable, Dict, Optional


ProgressCallback = Optional[Callable[[Dict[str, object]], None]]


class PPTUIEvents:
    STEPS = [
        ("analyzing", "Analyzing topic...", 10),
        ("planning", "Planning presentation...", 28),
        ("generating", "Generating slides...", 50),
        ("building", "Building PowerPoint...", 76),
        ("ready", "Presentation Ready", 100),
    ]

    @staticmethod
    def emit(
        callback: ProgressCallback,
        stage: str,
        message: str,
        progress: int,
        file_path: str = "",
    ) -> None:
        if not callback:
            return
        callback(
            {
                "stage": stage,
                "message": message,
                "progress": progress,
                "file_path": file_path,
            }
        )
