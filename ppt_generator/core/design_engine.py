from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List


class DesignEngine:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[1]
        self.templates_dir = self.base_dir / "templates"
        self.themes_dir = self.base_dir / "themes"

    def build_theme(self, brief: Dict[str, object], slides: List[Dict[str, object]]) -> Dict[str, object]:
        style = str(brief.get("style", "modern")).lower()
        template = self._load_template(style)
        colors = self._palette_for(style)
        fonts = self._load_json(self.themes_dir / "fonts.json")
        layouts = self._load_json(self.themes_dir / "layouts.json")

        return {
            "style": style,
            "template": template,
            "palette": colors,
            "fonts": fonts.get(style, fonts["modern"]),
            "layouts": layouts,
            "slide_surface": template.get("surface", "elevated"),
            "chart_style": template.get("chart_style", "clean"),
            "slide_count": len(slides),
        }

    def _palette_for(self, style: str) -> Dict[str, str]:
        palettes = self._load_json(self.themes_dir / "colors.json")
        return palettes.get(style, palettes["modern"])

    def _load_template(self, style: str) -> Dict[str, object]:
        path = self.templates_dir / f"{style}.json"
        if not path.exists():
            path = self.templates_dir / "modern.json"
        return self._load_json(path)

    @lru_cache(maxsize=12)
    def _load_json(self, path: Path) -> Dict[str, object]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
