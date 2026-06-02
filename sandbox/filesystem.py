from __future__ import annotations

from pathlib import Path


def ensure_within(base: Path, target: Path) -> Path:
    base_resolved = Path(base).resolve()
    target_resolved = Path(target).resolve()
    if not str(target_resolved).startswith(str(base_resolved)):
        raise ValueError(f"Path escape blocked: {target_resolved}")
    return target_resolved


def write_text_safe(base: Path, relative_path: str, content: str) -> Path:
    target = ensure_within(base, base / relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def read_text_safe(base: Path, relative_path: str) -> str:
    target = ensure_within(base, base / relative_path)
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8", errors="ignore")
