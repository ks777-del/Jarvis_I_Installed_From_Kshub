from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class PresentationBrief:
    topic: str
    audience: str
    tone: str
    slide_count: int
    style: str
    keywords: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class PromptAnalyzer:
    EDUCATIONAL = ("students", "student", "school", "college", "classroom", "teacher")
    BUSINESS = ("investors", "startup", "meeting", "board", "sales", "client", "business")
    TECHNICAL = ("coding", "architecture", "engineering", "software", "system", "api", "technical")
    CREATIVE = ("design", "futuristic", "innovation", "creative", "brand", "vision")

    STYLE_HINTS = {
        "modern": ("modern", "clean", "minimal"),
        "business": ("business", "corporate", "board", "investor"),
        "education": ("students", "education", "school", "college", "learning"),
        "futuristic": ("futuristic", "innovation", "future", "visionary"),
        "dark": ("dark", "bold", "sleek"),
    }

    def analyze(self, prompt: str) -> Dict[str, object]:
        raw = str(prompt or "").strip()
        lowered = raw.lower()

        topic = self._extract_topic(raw)
        audience = self._detect_audience(lowered)
        tone = self._detect_tone(lowered)
        style = self._detect_style(lowered, tone)
        slide_count = self._estimate_slide_count(lowered, topic)
        keywords = self._keywords(topic, lowered)

        return PresentationBrief(
            topic=topic,
            audience=audience,
            tone=tone,
            slide_count=slide_count,
            style=style,
            keywords=keywords,
        ).to_dict()

    def _extract_topic(self, prompt: str) -> str:
        cleaned = prompt.strip()
        patterns = [
            r"(?:on|about|for|regarding)\s+(.+?)(?:\s+for\s+.+)?$",
            r"(?:ppt|presentation|slides)\s+(?:on|about|for)?\s*(.+?)(?:\s+for\s+.+)?$",
        ]
        for pattern in patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE)
            if match:
                topic = match.group(1).strip(" .,:;!?")
                if topic:
                    return topic.title()
        fallback = re.sub(
            r"\b(?:generate|create|make|design|build|ppt|powerpoint|presentation|slides)\b",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        fallback = re.sub(r"\s+", " ", fallback).strip(" .,:;!?")
        return fallback.title() or "General Topic"

    def _detect_audience(self, lowered: str) -> str:
        audience_map = {
            "students": self.EDUCATIONAL,
            "investors": self.BUSINESS,
            "engineers": self.TECHNICAL,
            "creators": self.CREATIVE,
        }
        for audience, hints in audience_map.items():
            if any(hint in lowered for hint in hints):
                return audience
        return "general audience"

    def _detect_tone(self, lowered: str) -> str:
        if any(hint in lowered for hint in self.EDUCATIONAL):
            return "educational"
        if any(hint in lowered for hint in self.BUSINESS):
            return "business"
        if any(hint in lowered for hint in self.TECHNICAL):
            return "technical"
        if any(hint in lowered for hint in self.CREATIVE):
            return "creative"
        return "professional"

    def _detect_style(self, lowered: str, tone: str) -> str:
        for style, hints in self.STYLE_HINTS.items():
            if any(hint in lowered for hint in hints):
                return style
        defaults = {
            "educational": "education",
            "business": "business",
            "technical": "modern",
            "creative": "futuristic",
            "professional": "modern",
        }
        return defaults.get(tone, "modern")

    def _estimate_slide_count(self, lowered: str, topic: str) -> int:
        explicit = re.search(r"(\d+)\s*(?:slides?|pages?)", lowered)
        if explicit:
            return max(8, min(int(explicit.group(1)), 14))

        complexity_terms = sum(
            1
            for hint in ("impact", "future", "comparison", "strategy", "architecture", "data", "market")
            if hint in lowered
        )
        topic_weight = min(max(len(topic.split()), 2), 5)
        return max(8, min(10 + complexity_terms + topic_weight // 2, 14))

    def _keywords(self, topic: str, lowered: str) -> List[str]:
        words = [word.strip(".,!?") for word in topic.split() if len(word) > 2]
        context_words = [
            token
            for token in re.findall(r"[a-zA-Z]{4,}", lowered)
            if token not in {"generate", "create", "presentation", "slides", "topic"}
        ]
        unique: List[str] = []
        for item in words + context_words[:6]:
            token = item.lower()
            if token not in unique:
                unique.append(token)
        return unique[:8]
