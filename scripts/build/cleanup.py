"""Clean Quarto staging and optionally all generated outputs."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils.logging import get_logger
from scripts.utils.paths import BUILD_DIR, STAGING_DIR, ensure_dir

logger = get_logger(__name__)


def _clear_directory(directory: Path, preserve_gitkeep: bool) -> None:
    ensure_dir(directory)
    for child in directory.iterdir():
        if preserve_gitkeep and child.name == ".gitkeep":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main(all: bool = typer.Option(False, "--all", help="Also remove final build outputs.")) -> None:
    """Delete staging contents, preserving the staging directory itself."""
    _clear_directory(STAGING_DIR, preserve_gitkeep=False)
    logger.info("Cleaned %s", STAGING_DIR)
    if all:
        for name in ("pdf", "html", "docx", "audio"):
            target = BUILD_DIR / name
            _clear_directory(target, preserve_gitkeep=True)
            logger.info("Cleaned %s", target)


if __name__ == "__main__":
    typer.run(main)
