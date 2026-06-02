from __future__ import annotations

import logging
from typing import Dict, List


class TemplateEngine:
    """Maps structured content to concrete slide template specs."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def compose_slide_specs(self, content_flow: List[object], theme: Dict[str, object]) -> List[Dict[str, object]]:
        specs: List[Dict[str, object]] = []
        for idx, item in enumerate(content_flow, start=1):
            slide_type = self._auto_select_template(item)
            spec = {
                "index": idx,
                "slide_type": slide_type,
                "title": getattr(item, "title", ""),
                "subtitle": getattr(item, "subtitle", ""),
                "bullets": getattr(item, "bullets", []) or [],
                "highlight": getattr(item, "highlight", ""),
                "left_items": getattr(item, "left_items", []) or [],
                "right_items": getattr(item, "right_items", []) or [],
                "layout": self._layout_for(slide_type, theme),
            }
            specs.append(spec)

        self.logger.info("Built %s slide specs", len(specs))
        return specs

    def _auto_select_template(self, content: object) -> str:
        requested_type = str(getattr(content, "slide_type", "content")).lower()
        supported = {"title", "content", "bullet", "highlight", "comparison"}
        if requested_type in supported:
            return requested_type

        bullets = getattr(content, "bullets", []) or []
        if len(bullets) >= 4:
            return "bullet"
        if getattr(content, "highlight", ""):
            return "highlight"
        return "content"

    def _layout_for(self, slide_type: str, theme: Dict[str, object]) -> Dict[str, object]:
        spacing = theme["spacing"]
        layout_map = {
            "title": {"padding": spacing["xl"], "title_box": (0.8, 1.8, 11.7, 1.2), "subtitle_box": (0.8, 3.2, 11.7, 0.8)},
            "content": {"padding": spacing["lg"], "title_box": (0.7, 0.5, 12.0, 0.9), "body_box": (0.9, 1.7, 11.4, 4.8)},
            "bullet": {"padding": spacing["lg"], "title_box": (0.7, 0.5, 12.0, 0.9), "body_box": (0.9, 1.6, 11.1, 5.0)},
            "highlight": {"padding": spacing["lg"], "title_box": (0.7, 0.5, 12.0, 0.9), "highlight_box": (0.9, 1.6, 11.4, 2.0), "body_box": (0.9, 3.8, 11.0, 2.8)},
            "comparison": {"padding": spacing["lg"], "title_box": (0.7, 0.5, 12.0, 0.9), "left_box": (0.7, 1.8, 5.8, 4.8), "right_box": (6.8, 1.8, 5.8, 4.8)},
        }
        return layout_map.get(slide_type, layout_map["content"])
