#!/usr/bin/env python3
"""Transcribe video with faster-whisper, word-level timestamps, Hebrew."""
import sys
import json
import os
from pathlib import Path

def transcribe(video_path: str, output_path: str = None):
    from faster_whisper import WhisperModel

    video = Path(video_path)
    if not video.exists():
        print(f"ERROR: file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        output_path = str(video.parent / (video.stem + "_words.json"))

    print(f"Loading Whisper large-v3 (CPU int8)...", file=sys.stderr)
    model = WhisperModel("large-v3", device="cpu", compute_type="int8")

    print(f"Transcribing: {video_path}", file=sys.stderr)
    segments, info = model.transcribe(
        video_path,
        language="he",
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
    )

    words = []
    for segment in segments:
        if segment.words:
            for word in segment.words:
                words.append({
                    "text": word.word.strip(),
                    "start": round(word.start, 3),
                    "end": round(word.end, 3),
                })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(words)} words → {output_path}", file=sys.stderr)
    print(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <video_file> [output.json]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    transcribe(sys.argv[1], out)
