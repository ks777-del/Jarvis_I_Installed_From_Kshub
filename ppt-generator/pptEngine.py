from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from designEngine import DesignEngine
from exportService import ExportService
from templateEngine import TemplateEngine


@dataclass
class SlideContent:
    slide_type: str
    title: str
    subtitle: str = ""
    bullets: List[str] | None = None
    highlight: str = ""
    left_items: List[str] | None = None
    right_items: List[str] | None = None


class PPTGenerationEngine:
    """Autonomous orchestrator for structured, styled PPT generation."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.design_engine = DesignEngine()
        self.template_engine = TemplateEngine()
        self.export_service = ExportService()

    def generate_presentation(self, topic: str, style: str = "professional", slide_count: int = 6) -> Dict[str, str]:
        topic = (topic or "Untitled Topic").strip()
        style = (style or "professional").strip().lower()
        slide_count = max(5, min(int(slide_count or 6), 12))

        self.logger.info("Generating presentation for topic='%s', style='%s', slides=%s", topic, style, slide_count)

        theme = self.design_engine.create_theme(style=style, topic=topic)
        content_flow = self._build_content_flow(topic=topic, style=style, slide_count=slide_count)
        slide_specs = self.template_engine.compose_slide_specs(content_flow=content_flow, theme=theme)

        output_dir = Path("outputs") / "presentations"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{self._safe_filename(topic)}.pptx"
        self.export_service.export(slide_specs=slide_specs, theme=theme, output_path=output_file)

        return {
            "status": "success",
            "topic": topic,
            "style": style,
            "slide_count": str(len(slide_specs)),
            "file_path": str(output_file.resolve()),
        }

    def _build_content_flow(self, topic: str, style: str, slide_count: int) -> List[SlideContent]:
        flow: List[SlideContent] = [
            SlideContent(
                slide_type="title",
                title=topic,
                subtitle=f"A {style.title()} overview",
            ),
            SlideContent(
                slide_type="content",
                title=f"What is {topic}?",
                bullets=self._bullets_for("definition", topic),
            ),
            SlideContent(
                slide_type="bullet",
                title=f"How {topic} Works",
                bullets=self._bullets_for("process", topic),
            ),
            SlideContent(
                slide_type="highlight",
                title=f"Why {topic} Matters",
                highlight=self._highlight_for(topic),
                bullets=self._bullets_for("importance", topic),
            ),
            SlideContent(
                slide_type="comparison",
                title=f"Traditional vs Modern View of {topic}",
                left_items=self._comparison_for(topic, modern=False),
                right_items=self._comparison_for(topic, modern=True),
            ),
            SlideContent(
                slide_type="content",
                title="Conclusion",
                bullets=self._bullets_for("conclusion", topic),
            ),
        ]

        if slide_count > len(flow):
            extra = slide_count - len(flow)
            for i in range(extra):
                flow.insert(
                    -1,
                    SlideContent(
                        slide_type="bullet",
                        title=f"Key Insight {i + 1}: {topic}",
                        bullets=self._bullets_for("insight", topic, seed=i + 1),
                    ),
                )

        return flow[:slide_count]

    def _safe_filename(self, topic: str) -> str:
        value = re.sub(r"[^A-Za-z0-9_-]+", "_", topic.strip())
        return value.strip("_") or "presentation"

    def _bullets_for(self, section: str, topic: str, seed: int = 0) -> List[str]:
        bank = {
            "definition": [
                f"{topic} is a natural or conceptual system with measurable patterns.",
                "It can be explained through causes, behavior, and outcomes.",
                "Understanding the fundamentals builds confidence for deeper analysis.",
            ],
            "process": [
                f"{topic} follows a sequence of inputs, transitions, and outputs.",
                "External factors shape the speed and quality of each stage.",
                "Monitoring change over time helps reveal reliable trends.",
            ],
            "importance": [
                f"{topic} affects society, environment, and future planning.",
                "Better awareness supports smarter personal and policy decisions.",
                "Its impact grows when connected with technology and education.",
            ],
            "conclusion": [
                f"{topic} is best understood through both facts and context.",
                "Clear models and examples make complex ideas accessible.",
                "The next step is applying this understanding to real-world cases.",
            ],
            "insight": [
                f"Insight {seed}: small changes in {topic} can create large outcomes.",
                "Cross-discipline thinking reveals opportunities often missed.",
                "Data-backed storytelling improves decision quality and action speed.",
            ],
        }
        return bank.get(section, bank["definition"])

    def _highlight_for(self, topic: str) -> str:
        return (
            f"{topic} is not just a concept. It is a practical lens for understanding "
            "change, predicting outcomes, and making better decisions."
        )

    def _comparison_for(self, topic: str, modern: bool) -> List[str]:
        if modern:
            return [
                "Data-rich and model-driven interpretation",
                "Visual tools for rapid communication",
                f"Action-focused decisions tied to {topic}",
            ]
        return [
            "Observation-led and manually interpreted",
            "Limited scale for tracking complex variables",
            f"Reactive decisions with delayed insight on {topic}",
        ]
