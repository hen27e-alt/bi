#!/usr/bin/env python3
"""Convert word-level JSON to Remotion caption frames."""
import sys
import json
import argparse
from pathlib import Path

def build_captions(words_json: str, style: str = "reels", fps: int = 30):
    with open(words_json, encoding="utf-8") as f:
        words = json.load(f)

    captions = []

    if style == "reels":
        # 1-3 words per caption, punchy
        chunk_size = 3
        i = 0
        while i < len(words):
            chunk = words[i:i + chunk_size]
            if not chunk:
                break
            start_sec = chunk[0]["start"]
            end_sec = chunk[-1]["end"]
            # enforce minimum 1.2s duration
            if end_sec - start_sec < 1.2:
                end_sec = start_sec + 1.2
            captions.append({
                "text": " ".join(w["text"] for w in chunk),
                "startFrame": int(start_sec * fps),
                "endFrame": int(end_sec * fps),
            })
            i += chunk_size
    else:
        # youtube: group by sentence breaks or max 38 chars
        MAX_CHARS = 38
        MAX_SEC = 6.0
        MIN_SEC = 1.2
        current_words = []
        current_start = None

        for word in words:
            if current_start is None:
                current_start = word["start"]

            current_words.append(word)
            current_text = " ".join(w["text"] for w in current_words)
            duration = word["end"] - current_start

            should_flush = (
                len(current_text) > MAX_CHARS
                or duration >= MAX_SEC
                or word["text"].endswith((".", "!", "?", "...", "،"))
            )

            if should_flush and current_words:
                end_sec = current_words[-1]["end"]
                if end_sec - current_start < MIN_SEC:
                    end_sec = current_start + MIN_SEC
                captions.append({
                    "text": " ".join(w["text"] for w in current_words),
                    "startFrame": int(current_start * fps),
                    "endFrame": int(end_sec * fps),
                })
                current_words = []
                current_start = None

        # flush remainder
        if current_words:
            end_sec = current_words[-1]["end"]
            if end_sec - current_start < MIN_SEC:
                end_sec = current_start + MIN_SEC
            captions.append({
                "text": " ".join(w["text"] for w in current_words),
                "startFrame": int(current_start * fps),
                "endFrame": int(end_sec * fps),
            })

    return captions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("words_json")
    parser.add_argument("--style", choices=["reels", "youtube"], default="reels")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--output", "-o", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    captions = build_captions(args.words_json, args.style, args.fps)

    result = json.dumps(captions, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved {len(captions)} captions → {args.output}", file=sys.stderr)
    else:
        print(result)
