from __future__ import annotations

from pathlib import Path

from scripts.audio import build_audio


def test_from_qmd_builds_mp3_files(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "sample.qmd"
    source.write_text(
        """---\ntitle: Sample\n---\n\n::: {.audio-chunk #s1.1p1}\nFirst audio section.\n:::\n\n::: {.audio-chunk #s1.1p2}\nSecond audio section.\n:::\n""",
        encoding="utf-8",
    )
    output_root = tmp_path / "build" / "audio"
    calls: list[tuple[str, str, Path]] = []

    def fake_synthesize(text: str, voice: str, output_path: Path) -> Path:
        calls.append((text, voice, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake-mp3-data")
        return output_path

    monkeypatch.setattr(build_audio, "BUILD_DIR", tmp_path / "build")
    monkeypatch.setattr(build_audio, "synthesize", fake_synthesize)

    build_audio.from_qmd(source, voice="test-voice")

    expected_directory = output_root / "sample"
    expected_files = [expected_directory / "s1.1p1.mp3", expected_directory / "s1.1p2.mp3"]
    assert all(path.is_file() for path in expected_files)
    assert [path for _, _, path in calls] == expected_files
    assert [text for text, _, _ in calls] == ["First audio section.", "Second audio section."]
    assert all(voice == "test-voice" for _, voice, _ in calls)
