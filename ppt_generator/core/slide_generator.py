from __future__ import annotations

import datetime as _dt
from typing import Dict, List


class SlideGenerator:
    def generate(self, brief: Dict[str, object], plan: List[Dict[str, object]]) -> List[Dict[str, object]]:
        topic = str(brief["topic"])
        audience = str(brief["audience"])
        tone = str(brief["tone"])
        slides: List[Dict[str, object]] = []

        agenda_titles = [item["title"] for item in plan[2:-2]]
        for index, item in enumerate(plan):
            slide_type = item["type"]
            title = item["title"]

            if slide_type == "title":
                slides.append(
                    {
                        "type": "title",
                        "title": title,
                        "subtitle": f"{tone.title()} overview for {audience}",
                        "date": _dt.datetime.now().strftime("%d %B %Y"),
                        "author": "Jarvis AI Presentation Engine",
                    }
                )
            elif slide_type == "agenda":
                slides.append(
                    {
                        "type": "agenda",
                        "title": title,
                        "bullets": self._limit_bullets(agenda_titles[:5]),
                        "paragraph": "A clear roadmap keeps the story focused and easy to follow.",
                    }
                )
            elif slide_type in {"introduction", "core", "future", "summary"}:
                bullets = self._concept_bullets(topic, title, tone, audience)
                paragraph = self._supporting_paragraph(topic, title, tone)
                slides.append(
                    {
                        "type": slide_type,
                        "title": title,
                        "bullets": bullets,
                        "paragraph": paragraph,
                    }
                )
            elif slide_type == "visual":
                slides.append(
                    {
                        "type": "visual",
                        "title": title,
                        "caption": f"A visual narrative showing how {topic.lower()} shapes outcomes.",
                        "visual_description": f"Modern editorial illustration around {topic.lower()} with layered depth.",
                        "keywords": [topic, title, tone],
                    }
                )
            elif slide_type == "data":
                metrics = self._data_points(topic, tone)
                slides.append(
                    {
                        "type": "data",
                        "title": title,
                        "metrics": metrics,
                        "chart_type": "bar" if tone != "creative" else "line",
                        "insight": f"Momentum around {topic.lower()} is strongest where clarity, adoption, and trust align.",
                    }
                )
            elif slide_type == "comparison":
                slides.append(
                    {
                        "type": "comparison",
                        "title": title,
                        "left_title": "Current State",
                        "right_title": "Preferred Direction",
                        "left_points": self._limit_bullets(
                            [
                                f"{topic} handled inconsistently",
                                "Manual effort slows decision cycles",
                                "Limited visibility across stakeholders",
                                "Reactive improvements only",
                            ]
                        ),
                        "right_points": self._limit_bullets(
                            [
                                f"{topic} managed strategically",
                                "Clear workflows accelerate delivery",
                                "Shared metrics improve alignment",
                                "Proactive decisions raise confidence",
                            ]
                        ),
                    }
                )
            else:
                slides.append({"type": "content", "title": title, "bullets": [], "paragraph": ""})

        if slides and slides[-1]["type"] != "thank_you":
            slides.append(
                {
                    "type": "thank_you",
                    "title": "Thank You",
                    "subtitle": f"Questions on {topic} are welcome.",
                }
            )
        else:
            slides[-1] = {
                "type": "thank_you",
                "title": "Thank You",
                "subtitle": f"Questions on {topic} are welcome.",
            }
        return slides

    def _concept_bullets(self, topic: str, title: str, tone: str, audience: str) -> List[str]:
        phrases = [
            f"{topic} creates clearer decisions across teams",
            f"{title} connects strategy with practical execution",
            f"{audience.title()} benefit from simple, structured framing",
            f"Strong fundamentals improve confidence and adoption",
            f"Focused examples make {topic.lower()} easier to apply",
        ]
        if tone == "technical":
            phrases = [
                f"{topic} depends on reliable architecture choices",
                "Clear interfaces reduce integration friction",
                "Observability improves performance and resilience",
                "Trade-offs should be explicit and measurable",
                "Scalable patterns support long-term maintainability",
            ]
        elif tone == "business":
            phrases = [
                f"{topic} influences revenue, efficiency, and trust",
                "Decision quality rises with shared visibility",
                "Prioritized execution reduces wasted effort",
                "Differentiation grows through better experience",
                "Clear ownership accelerates measurable progress",
            ]
        elif tone == "educational":
            phrases = [
                f"{topic} becomes easier through familiar examples",
                "Start with concepts before advanced detail",
                "Patterns help learners remember core ideas",
                "Questions deepen understanding and curiosity",
                "Simple comparisons reveal how systems behave",
            ]
        elif tone == "creative":
            phrases = [
                f"{topic} gains energy through visual storytelling",
                "Strong mood and hierarchy guide attention",
                "Contrast creates memorable narrative moments",
                "A clear point of view sharpens impact",
                "Originality works best with disciplined structure",
            ]
        return self._limit_bullets(phrases)

    def _supporting_paragraph(self, topic: str, title: str, tone: str) -> str:
        paragraph = (
            f"{title} frames {topic} as a practical, high-value capability. "
            "The goal is to move from awareness to action with confident, understandable decisions."
        )
        if tone == "technical":
            paragraph = (
                f"{title} explains how {topic} behaves in real systems, where architecture, data flow, "
                "and operational reliability matter as much as the concept itself."
            )
        elif tone == "educational":
            paragraph = (
                f"{title} introduces {topic} in approachable language so learners can connect ideas, "
                "remember the essentials, and build toward deeper understanding."
            )
        return paragraph

    def _data_points(self, topic: str, tone: str) -> List[Dict[str, object]]:
        labels = ["Awareness", "Adoption", "Efficiency", "Confidence"]
        base_values = [58, 64, 71, 67]
        if tone == "business":
            base_values = [61, 74, 79, 70]
        elif tone == "technical":
            base_values = [52, 69, 76, 65]
        elif tone == "education":
            base_values = [66, 62, 68, 72]
        return [
            {"label": label, "value": value, "note": f"{label} in {topic}"}
            for label, value in zip(labels, base_values)
        ]

    def _limit_bullets(self, bullets: List[str]) -> List[str]:
        cleaned: List[str] = []
        for bullet in bullets[:5]:
            words = bullet.split()
            if len(words) > 12:
                bullet = " ".join(words[:12])
            cleaned.append(bullet)
        return cleaned
