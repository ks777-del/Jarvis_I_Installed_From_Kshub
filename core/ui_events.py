from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Optional


@dataclass
class UIEvent:
    stage: str
    message: str
    progress: int
    data: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class UIEventStream:
    def __init__(self, callback: Optional[Callable[[Dict[str, object]], None]] = None) -> None:
        self.callback = callback
        self.events: List[UIEvent] = []

    def emit(self, stage: str, message: str, progress: int, **data: object) -> Dict[str, object]:
        event = UIEvent(stage=stage, message=message, progress=max(0, min(progress, 100)), data=data)
        self.events.append(event)
        payload = {"stage": event.stage, "message": event.message, "progress": event.progress, **event.data}
        if self.callback:
            self.callback(payload)
        return payload

    def engineering_flow(self) -> List[Dict[str, object]]:
        steps = [
            ("analyzing", "Analyzing request...", 10),
            ("planning", "Planning architecture...", 24),
            ("generating", "Generating systems...", 42),
            ("dependencies", "Installing dependencies...", 60),
            ("compiling", "Compiling project...", 78),
            ("validating", "Running validation...", 90),
            ("complete", "Build Complete", 100),
        ]
        return [self.emit(s, m, p) for s, m, p in steps]
