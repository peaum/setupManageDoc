"""Shared project paths and file discovery helpers."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = PROJECT_ROOT / "build"
STAGING_DIR = BUILD_DIR / "_staging"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CONTENT_DIR = PROJECT_ROOT / "content"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def ensure_dir(path: Path) -> Path:
    """Create path and its parents when necessary, then return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_active_qmd() -> Path | None:
    """Return the active QMD from the environment or the newest source QMD."""
    active = os.getenv("QUARTO_ACTIVE_FILE")
    if active:
        candidate = Path(active).expanduser()
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if candidate.is_file():
            return candidate.resolve()
    candidates = sorted((PROJECT_ROOT / "src" / "quarto").glob("*.qmd"), key=lambda p: p.stat().st_mtime)
    return candidates[-1].resolve() if candidates else None
