from __future__ import annotations

import hashlib
import os
from io import BytesIO
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import requests
from matplotlib.patches import Circle, Rectangle
from PIL import Image


class AssetEngine:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[1]
        self.assets_dir = self.base_dir / "assets"
        self.cache_dir = self.assets_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
        self.pixabay_key = os.getenv("PIXABAY_API_KEY", "").strip()

    def prepare_assets(self, brief: Dict[str, object], slides: List[Dict[str, object]], theme: Dict[str, object]) -> Dict[str, Dict[str, str]]:
        assets: Dict[str, Dict[str, str]] = {}
        for index, slide in enumerate(slides):
            slide_id = f"slide_{index + 1}"
            if slide["type"] in {"visual", "title"}:
                image_path = self._resolve_image(
                    query=f"{brief['topic']} {slide.get('title', '')}",
                    slide_id=slide_id,
                    palette=theme["palette"],
                )
                if image_path:
                    assets[slide_id] = {"image": str(image_path)}
            elif slide["type"] == "comparison":
                icon_path = self._generate_badge(slide_id, theme["palette"]["accent"], "VS")
                assets[slide_id] = {"badge": str(icon_path)}
        return assets

    def _resolve_image(self, query: str, slide_id: str, palette: Dict[str, str]) -> Path:
        cache_name = hashlib.sha1(query.encode("utf-8")).hexdigest()[:16] + ".png"
        cached = self.cache_dir / cache_name
        if cached.exists():
            return cached

        fetched = self._fetch_unsplash(query, cached) or self._fetch_pixabay(query, cached)
        if fetched:
            return fetched
        return self._generate_fallback_image(query, slide_id, palette)

    def _fetch_unsplash(self, query: str, output_path: Path) -> Path | None:
        if not self.unsplash_key:
            return None
        try:
            response = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                timeout=12,
            )
            response.raise_for_status()
            image_url = response.json()["urls"]["regular"]
            return self._download_image(image_url, output_path)
        except Exception:
            return None

    def _fetch_pixabay(self, query: str, output_path: Path) -> Path | None:
        if not self.pixabay_key:
            return None
        try:
            response = requests.get(
                "https://pixabay.com/api/",
                params={"key": self.pixabay_key, "q": query, "image_type": "photo", "per_page": 3},
                timeout=12,
            )
            response.raise_for_status()
            hits = response.json().get("hits", [])
            if not hits:
                return None
            return self._download_image(hits[0]["largeImageURL"], output_path)
        except Exception:
            return None

    def _download_image(self, url: str, output_path: Path) -> Path | None:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image.thumbnail((1600, 900))
            image.save(output_path, format="PNG", optimize=True)
            return output_path
        except Exception:
            return None

    def _generate_fallback_image(self, query: str, slide_id: str, palette: Dict[str, str]) -> Path:
        path = self.cache_dir / f"{slide_id}_fallback.png"
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=160)
        fig.patch.set_facecolor(f"#{palette['background']}")
        ax.set_facecolor(f"#{palette['surface']}")
        ax.axis("off")

        ax.text(0.08, 0.75, query.title(), fontsize=22, weight="bold", color=f"#{palette['text_primary']}")
        ax.text(
            0.08,
            0.47,
            "Editorial visual placeholder generated locally.\nNetwork-safe fallback keeps the deck polished.",
            fontsize=11,
            color=f"#{palette['text_muted']}",
        )
        ax.add_patch(Rectangle((0.08, 0.18), 0.25, 0.07, color=f"#{palette['accent']}", alpha=0.85))
        ax.add_patch(Rectangle((0.36, 0.18), 0.16, 0.07, color=f"#{palette['secondary']}", alpha=0.75))
        ax.add_patch(Circle((0.84, 0.62), 0.13, color=f"#{palette['primary']}", alpha=0.18))
        ax.add_patch(Circle((0.74, 0.36), 0.08, color=f"#{palette['accent']}", alpha=0.25))
        fig.savefig(path, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        return path

    def _generate_badge(self, slide_id: str, color: str, label: str) -> Path:
        path = self.cache_dir / f"{slide_id}_badge.png"
        fig, ax = plt.subplots(figsize=(1.4, 1.4), dpi=150)
        ax.axis("off")
        ax.add_patch(Circle((0.5, 0.5), 0.42, color=f"#{color}", alpha=0.9))
        ax.text(0.5, 0.5, label, ha="center", va="center", fontsize=18, color="white", weight="bold")
        fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.0)
        plt.close(fig)
        return path
