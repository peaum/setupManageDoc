"""Build per-section and concatenated audio assets."""
from __future__ import annotations

import sys
from pathlib import Path

import typer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.audio.extract_audio_chunks import extract_from_html, extract_from_qmd
from scripts.audio.tts_engine import DEFAULT_VOICE, synthesize
from scripts.utils.logging import get_logger
from scripts.utils.paths import BUILD_DIR, ensure_dir

app = typer.Typer(no_args_is_help=True)
logger = get_logger(__name__)


def _build(chunks: list[tuple[str, str]], stem: str, voice: str, output_root: Path | None) -> None:
    root = output_root or BUILD_DIR / "audio"
    output_dir = ensure_dir(root / stem)
    for identifier, text in chunks:
        destination = output_dir / f"{identifier}.mp3"
        synthesize(text, voice, destination)
        logger.info("Created %s", destination)


@app.command("from-qmd")
def from_qmd(
    path: Path,
    voice: str = typer.Option(DEFAULT_VOICE, "--voice"),
    output_dir: Path | None = None,
) -> None:
    """Extract and synthesize chunks from a QMD source file."""
    if not path.is_file():
        raise typer.BadParameter(f"QMD file does not exist: {path}")
    _build(extract_from_qmd(path), path.stem, voice, output_dir)


@app.command("from-html")
def from_html(
    path: Path,
    voice: str = typer.Option(DEFAULT_VOICE, "--voice"),
    output_dir: Path | None = None,
) -> None:
    """Extract and synthesize chunks from rendered HTML."""
    if not path.is_file():
        raise typer.BadParameter(f"HTML file does not exist: {path}")
    _build(extract_from_html(path), path.stem, voice, output_dir)


@app.command()
def concat(
    qmd_stem: str,
    output_dir: Path | None = None,
) -> None:
    """Concatenate ordered MP3 chunks into full.mp3."""
    import subprocess
    import tempfile

    from imageio_ffmpeg import get_ffmpeg_exe


    root = output_dir or BUILD_DIR / "audio"
    directory = root / qmd_stem
    files = sorted(directory.glob("*.mp3"), key=lambda path: path.stem)
    if not files:
        raise typer.BadParameter(f"No MP3 chunks found in {directory}")
    files = [file for file in files if file.name != "full.mp3"]
    destination = directory / "full.mp3"
    with tempfile.TemporaryDirectory() as temporary_dir:
        list_file = Path(temporary_dir) / "concat.txt"
        list_file.write_text(
            "\n".join(f"file '{file.resolve().as_posix()}'" for file in files),
            encoding="utf-8",
        )
        subprocess.run(
            [
                get_ffmpeg_exe(),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_file),
                "-c",
                "copy",
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    logger.info("Created %s", destination)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
