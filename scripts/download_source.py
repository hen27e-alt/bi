#!/usr/bin/env python3
"""
yt-dlp wrapper for "חזרה לעבר" channel.
Downloads best-quality video from YouTube search to temp/ or input/.
"""
import sys, subprocess, re
from pathlib import Path

VENV_YT = Path(__file__).parent.parent / ".venv/bin/yt-dlp"
TEMP_DIR = Path(__file__).parent.parent / "temp"


def _slug(text: str) -> str:
    return re.sub(r"[^\w\-]", "_", text)[:60]


def download(artist: str, song: str, out_dir: Path = TEMP_DIR, max_duration: int = 600) -> Path | None:
    """
    Try to download artist+song from YouTube. Returns local path or None.
    max_duration: skip videos longer than this (seconds), to avoid full albums.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(f"{artist}_{song}")
    # Check if already downloaded
    for ext in ("mp4", "mkv", "webm"):
        existing = out_dir / f"{slug}.{ext}"
        if existing.exists():
            print(f"[download] Already exists: {existing}", file=sys.stderr)
            return existing

    query = f"ytsearch1:{artist} {song} official music video"
    out_tmpl = str(out_dir / f"{slug}.%(ext)s")

    cmd = [
        str(VENV_YT),
        query,
        "--output", out_tmpl,
        "--format", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
        "--merge-output-format", "mp4",
        "--no-playlist",
        "--match-filter", f"duration<={max_duration}",
        "--socket-timeout", "20",
        "--retries", "3",
        "--fragment-retries", "3",
        "--no-warnings",
        "--print", "after_move:filepath",
    ]

    print(f"[download] Searching: {artist} - {song}", file=sys.stderr)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            # Last line of stdout is the final filepath (from --print)
            filepath = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else None
            if filepath and Path(filepath).exists():
                print(f"[download] OK: {filepath}", file=sys.stderr)
                return Path(filepath)
            # Fallback: glob for the slug
            matches = list(out_dir.glob(f"{slug}.*"))
            if matches:
                return matches[0]
        # Report the actual error
        err = (result.stderr or "").strip()
        if "HTTP Error 429" in err or "Too Many Requests" in err:
            print("[download] BLOCKED: YouTube rate-limited (429). Use a local file.", file=sys.stderr)
        elif "Sign in" in err or "bot" in err.lower():
            print("[download] BLOCKED: YouTube bot-detection. Use a local file.", file=sys.stderr)
        elif "is not available" in err or "unavailable" in err.lower():
            print("[download] NOT FOUND: Video not available in this region/account.", file=sys.stderr)
        else:
            snippet = err[-300:] if len(err) > 300 else err
            print(f"[download] FAILED: {snippet}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("[download] TIMEOUT: yt-dlp took too long. Network may be blocked.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[download] ERROR: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--artist", required=True)
    p.add_argument("--song",   required=True)
    p.add_argument("--out-dir", default=str(TEMP_DIR))
    args = p.parse_args()
    path = download(args.artist, args.song, Path(args.out_dir))
    if path:
        print(path)
        sys.exit(0)
    else:
        sys.exit(1)
