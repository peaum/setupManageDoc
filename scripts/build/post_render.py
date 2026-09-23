"""Copy Quarto outputs from staging into stable build directories."""
from __future__ import annotations

import shutil
import sys
import os
from pathlib import Path

import typer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.utils.logging import get_logger
from scripts.utils.paths import BUILD_DIR, STAGING_DIR, ensure_dir, find_active_qmd

app = typer.Typer(no_args_is_help=True)
logger = get_logger(__name__)


def _source_stem(source: Path) -> str:
    return source.stem


def _find_output(stem: str, suffix: str) -> Path:
    candidates = sorted(STAGING_DIR.rglob(f"{stem}{suffix}"))
    if not candidates:
        raise typer.BadParameter(
            f"No {suffix} output for '{stem}' was found in {STAGING_DIR}. Render the source first."
        )
    return candidates[0]


def _copy(source: Path, suffix: str, destination: Path) -> None:
    output = _find_output(_source_stem(source), suffix)
    ensure_dir(destination.parent)
    shutil.copy2(output, destination)
    logger.info("Copied %s -> %s", output, destination)


def _validate_source(source: Path) -> Path:
    if not source.is_file():
        raise typer.BadParameter(f"Source file does not exist: {source}")
    return source


def _clean_source_artifacts(source: Path) -> None:
    """Remove debug and resource artifacts that Quarto leaves beside a QMD."""
    typst_output = source.with_suffix(".typ")
    resource_directory = source.with_name(f"{source.stem}_files")
    for artifact in (typst_output, resource_directory):
        if artifact.is_dir():
            shutil.rmtree(artifact)
            logger.info("Removed %s", artifact)
        elif artifact.is_file():
            artifact.unlink()
            logger.info("Removed %s", artifact)


@app.command("auto")
def auto(source: Path | None = typer.Option(None, "--source", exists=False)) -> None:
    """Copy the rendered HTML output during Quarto's post-render hook."""
    active_source = source or find_active_qmd()
    if active_source is None:
        logger.warning("No active QMD source found; nothing to copy.")
        return
    active_source = _validate_source(active_source)
    _clean_source_artifacts(active_source)
    if os.getenv("QUARTO_FORMAT", "").lower() not in ("", "html"):
        return
    try:
        _copy(active_source, ".html", BUILD_DIR / "html" / active_source.stem / "index.html")
    except typer.BadParameter:
        logger.info("No HTML output found for %s; nothing to copy.", active_source.stem)


@app.command()
def pdf(source: Path = typer.Option(..., "--source", exists=False)) -> None:
    """Copy a rendered PDF to build/pdf."""
    source = _validate_source(source)
    _copy(source, ".pdf", BUILD_DIR / "pdf" / f"{source.stem}.pdf")


@app.command()
def html(source: Path = typer.Option(..., "--source", exists=False)) -> None:
    """Copy a rendered HTML document to build/html/<stem>/index.html."""
    source = _validate_source(source)
    _copy(source, ".html", BUILD_DIR / "html" / source.stem / "index.html")


@app.command()
def docx(source: Path = typer.Option(..., "--source", exists=False)) -> None:
    """Copy a rendered DOCX to build/docx."""
    source = _validate_source(source)
    _copy(source, ".docx", BUILD_DIR / "docx" / f"{source.stem}.docx")


@app.command("all")
def all_outputs(source: Path = typer.Option(..., "--source", exists=False)) -> None:
    """Copy PDF, HTML, and DOCX outputs for one source document."""
    source = _validate_source(source)
    pdf(source)
    html(source)
    docx(source)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
