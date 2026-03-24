"""TTS generation using edge-tts (free Microsoft Neural voices)"""
import os
import sys
import subprocess

from config import OUTPUT_DIR


def get_duration(filepath):
    """Get media file duration in seconds using ffprobe"""
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", filepath
    ], capture_output=True, text=True)
    return float(result.stdout.strip())


def generate(text, voice="vi-VN-NamMinhNeural", rate="0"):
    """Generate TTS audio file. Returns (filepath, duration_seconds)."""
    voiceover_path = os.path.join(OUTPUT_DIR, "voiceover.mp3")
    text_file = os.path.join(OUTPUT_DIR, "narration.txt")

    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)

    cmd = [
        sys.executable, "-m", "edge_tts",
        "--voice", voice,
        "--file", text_file,
        "--write-media", voiceover_path,
    ]
    if rate and rate != "0":
        cmd.extend(["--rate", rate])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"TTS failed: {result.stderr[:300]}")

    dur = get_duration(voiceover_path)
    return voiceover_path, dur
