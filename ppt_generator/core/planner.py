from __future__ import annotations

from typing import Dict, List


class PresentationPlanner:
    def plan(self, brief: Dict[str, object]) -> List[Dict[str, object]]:
        topic = str(brief["topic"])
        slide_count = int(brief["slide_count"])

        plan: List[Dict[str, object]] = [
            {"type": "title", "title": topic, "purpose": "opening"},
            {"type": "agenda", "title": "Agenda", "purpose": "roadmap"},
            {"type": "introduction", "title": f"Why {topic} Matters", "purpose": "context"},
        ]

        core_titles = self._core_sections(topic, brief)
        visual_title = f"{topic} in Focus"
        data_title = f"{topic} by the Numbers"
        comparison_title = f"Comparing Approaches in {topic}"
        future_title = f"The Future of {topic}"

        remaining = max(slide_count - 7, 1)
        for index in range(remaining):
            title = core_titles[index % len(core_titles)]
            plan.append({"type": "core", "title": title, "purpose": "concept"})

        insert_at = min(5, len(plan))
        plan.insert(insert_at, {"type": "visual", "title": visual_title, "purpose": "visual"})
        plan.insert(min(insert_at + 2, len(plan)), {"type": "data", "title": data_title, "purpose": "evidence"})
        plan.insert(min(insert_at + 4, len(plan)), {"type": "comparison", "title": comparison_title, "purpose": "contrast"})
        plan.append({"type": "future", "title": future_title, "purpose": "forward"})
        plan.append({"type": "summary", "title": "Key Takeaways", "purpose": "summary"})
        plan.append({"type": "thank_you", "title": "Thank You", "purpose": "closing"})

        return self._normalize_plan(plan, slide_count)

    def _core_sections(self, topic: str, brief: Dict[str, object]) -> List[str]:
        tone = str(brief.get("tone", "professional"))
        base = [
            f"Understanding {topic}",
            f"How {topic} Works",
            f"Applications of {topic}",
            f"Benefits of {topic}",
            f"Challenges in {topic}",
        ]
        if tone == "business":
            base = [
                f"{topic} Market Landscape",
                f"{topic} Value Proposition",
                f"Operational Impact of {topic}",
                f"Growth Opportunities in {topic}",
                f"Risks and Mitigation in {topic}",
            ]
        elif tone == "educational":
            base = [
                f"Introducing {topic}",
                f"Core Principles of {topic}",
                f"Real-World Examples of {topic}",
                f"Why Learners Care About {topic}",
                f"Common Misunderstandings About {topic}",
            ]
        elif tone == "technical":
            base = [
                f"{topic} System Overview",
                f"{topic} Architecture and Flow",
                f"{topic} Components and Interfaces",
                f"{topic} Performance Considerations",
                f"{topic} Implementation Challenges",
            ]
        elif tone == "creative":
            base = [
                f"{topic} Inspiration and Vision",
                f"{topic} Visual Language",
                f"{topic} Experience Design",
                f"{topic} Differentiation",
                f"{topic} Creative Potential",
            ]
        return base

    def _normalize_plan(self, plan: List[Dict[str, object]], slide_count: int) -> List[Dict[str, object]]:
        ordered: List[Dict[str, object]] = []
        seen = set()
        for slide in plan:
            key = (slide["type"], slide["title"])
            if key in seen:
                continue
            ordered.append(slide)
            seen.add(key)

        if len(ordered) > slide_count:
            protected = {"title", "agenda", "introduction", "visual", "data", "comparison", "future", "summary", "thank_you"}
            trimmed = []
            extra_core = []
            for slide in ordered:
                if slide["type"] in protected:
                    trimmed.append(slide)
                else:
                    extra_core.append(slide)
            while len(trimmed) + len(extra_core) > slide_count and extra_core:
                extra_core.pop()
            ordered = trimmed[:3] + extra_core + trimmed[3:]

        return ordered[:slide_count]
