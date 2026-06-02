from __future__ import annotations

from typing import Dict


class DesignEngine:
    """Generates coherent design systems (palette, typography, spacing)."""

    STYLE_PRESETS = {
        "bright": {
            "background": "FFF8EE",
            "surface": "FFFFFF",
            "primary": "FF7A00",
            "secondary": "0077B6",
            "accent": "06D6A0",
            "text_primary": "1A1A1A",
            "text_muted": "5F6368",
        },
        "dark": {
            "background": "121826",
            "surface": "1D2433",
            "primary": "66E3FF",
            "secondary": "8A7DFF",
            "accent": "FFB703",
            "text_primary": "F5F7FA",
            "text_muted": "B6BEC9",
        },
        "professional": {
            "background": "F4F7FB",
            "surface": "FFFFFF",
            "primary": "0A4DA3",
            "secondary": "147DF5",
            "accent": "11A579",
            "text_primary": "1F2937",
            "text_muted": "64748B",
        },
    }

    def create_theme(self, style: str, topic: str) -> Dict[str, object]:
        preset = self.STYLE_PRESETS.get(style, self.STYLE_PRESETS["professional"])

        return {
            "topic": topic,
            "style": style,
            "palette": preset,
            "fonts": {
                "title": "Aptos Display",
                "subtitle": "Calibri",
                "body": "Calibri",
                "highlight": "Aptos",
            },
            "font_sizes": {
                "title": 42,
                "subtitle": 22,
                "section_title": 32,
                "body": 20,
                "bullet": 19,
                "highlight": 24,
                "small": 16,
            },
            "spacing": {
                "xs": 0.1,
                "sm": 0.15,
                "md": 0.25,
                "lg": 0.4,
                "xl": 0.7,
            },
            "shape_style": {
                "corner_radius": 0.08,
                "line_width": 1,
            },
        }
