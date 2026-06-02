from __future__ import annotations

from typing import Callable, Dict, Optional

from .core.analyzer import PromptAnalyzer
from .core.asset_engine import AssetEngine
from .core.design_engine import DesignEngine
from .core.exporter import PresentationExporter
from .core.planner import PresentationPlanner
from .core.ppt_builder import PPTBuilder
from .core.slide_generator import SlideGenerator
from .core.ui_events import PPTUIEvents


ProgressCallback = Optional[Callable[[Dict[str, object]], None]]


class CanvaPPTGenerationEngine:
    def __init__(self) -> None:
        self.analyzer = PromptAnalyzer()
        self.planner = PresentationPlanner()
        self.slide_generator = SlideGenerator()
        self.design_engine = DesignEngine()
        self.asset_engine = AssetEngine()
        self.builder = PPTBuilder()
        self.exporter = PresentationExporter()

    def generate(self, query: str, progress_callback: ProgressCallback = None) -> Dict[str, object]:
        PPTUIEvents.emit(progress_callback, "analyzing", "Analyzing topic...", 10)
        brief = self.analyzer.analyze(query)

        PPTUIEvents.emit(progress_callback, "planning", "Planning presentation...", 28)
        slide_plan = self.planner.plan(brief)

        PPTUIEvents.emit(progress_callback, "generating", "Generating slides...", 50)
        slides = self.slide_generator.generate(brief, slide_plan)

        theme = self.design_engine.build_theme(brief, slides)
        enriched_assets = self.asset_engine.prepare_assets(brief, slides, theme)

        PPTUIEvents.emit(progress_callback, "building", "Building PowerPoint...", 76)
        presentation = self.builder.build(brief, slides, theme, enriched_assets)

        result = self.exporter.export(brief, presentation)
        if result.get("success"):
            PPTUIEvents.emit(progress_callback, "ready", "Presentation Ready", 100, file_path=result.get("file"))
        else:
            PPTUIEvents.emit(progress_callback, "error", result.get("message", "Presentation failed"), 100)
        return result
