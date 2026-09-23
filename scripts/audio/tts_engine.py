"""Piper TTS adapter with WAV and optional MP3 output."""
from __future__ import annotations

import tempfile
import wave
from pathlib import Path

from scripts.utils.paths import DATA_RAW_DIR, ensure_dir

DEFAULT_VOICE = "en_US-lessac-medium"


def _model_path(voice: str) -> Path:
    candidate = Path(voice).expanduser()
    if candidate.is_file():
        return candidate
    return DATA_RAW_DIR / f"{voice}.onnx"


def synthesize(text: str, voice: str, output_path: Path) -> Path:
    """Synthesize text with Piper and write a WAV or MP3 file."""
    try:
        from piper import PiperVoice
    except ImportError as error:
        raise RuntimeError("Install dependencies with 'pip install -r requirements.txt' to use TTS.") from error

    model = _model_path(voice)
    if not model.is_file():
        raise FileNotFoundError(
            f"Piper voice model not found: {model}. Download '{voice}.onnx' and place it in "
            f"{DATA_RAW_DIR}, or pass a model path as the voice argument."
        )

    import soundfile as sf

    ensure_dir(output_path.parent)
    with tempfile.TemporaryDirectory() as temporary_dir:
        wav_path = Path(temporary_dir) / "speech.wav"
        with wave.open(str(wav_path), "wb") as wav_file:
            PiperVoice.load(str(model)).synthesize_wav(text, wav_file)
        samples, sample_rate = sf.read(wav_path)
        wav_output = output_path.with_suffix(".wav") if output_path.suffix.lower() == ".mp3" else output_path
        sf.write(wav_output, samples, sample_rate)
        if output_path.suffix.lower() == ".mp3":
            from pydub import AudioSegment
            from imageio_ffmpeg import get_ffmpeg_exe

            AudioSegment.converter = get_ffmpeg_exe()
            AudioSegment.from_wav(wav_output).export(output_path, format="mp3")
            wav_output.unlink()
    return output_path
