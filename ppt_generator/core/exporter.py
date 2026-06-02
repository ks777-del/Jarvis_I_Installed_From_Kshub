from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import Dict


class PresentationExporter:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[3]
        self.output_dir = self.base_dir / "outputs" / "presentations"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, brief: Dict[str, object], presentation) -> Dict[str, object]:
        topic = str(brief["topic"])
        year = _dt.datetime.now().year
        filename = f"{self._slugify(topic)}_{year}.pptx"
        path = self.output_dir / filename
        try:
            presentation.save(str(path))
            return {
                "success": True,
                "file": str(path.resolve()),
                "download_url": f"/download/{filename}",
                "message": "Presentation ready",
            }
        except Exception as exc:
            return {
                "success": False,
                "file": "",
                "download_url": "",
                "message": f"Export failed: {exc}",
            }

    def _slugify(self, text: str) -> str:
        value = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
        value = re.sub(r"_+", "_", value).strip("_")
        return value.lower() or "presentation"
