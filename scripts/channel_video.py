#!/usr/bin/env python3
"""
Automated TikTok pipeline for channel "חזרה לעבר".

Usage:
  python3 scripts/channel_video.py \\
      --artist "Michael Jackson" --song "Thriller" --year 1982 --genre "Pop/Funk"

  # With local file (skips download):
  python3 scripts/channel_video.py \\
      --artist "ABBA" --song "Dancing Queen" --year 1976 --genre "disco" \\
      --source input/abba_dancing_queen.mp4

  # Custom clip range (seconds):
  python3 scripts/channel_video.py \\
      --artist "Queen" --song "Bohemian Rhapsody" --year 1975 --genre "rock" \\
      --clip-start 60 --clip-duration 30
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

BASE        = Path(__file__).parent.parent
VENV        = BASE / ".venv"
VENV_PY     = VENV / "bin/python"
VENV_AE     = VENV / "bin/auto-editor"
INPUT_DIR   = BASE / "input"
TEMP_DIR    = BASE / "temp"
OUTPUT_DIR  = BASE / "output"
STUDIO_DIR  = BASE / "video-studio"


# ── Genre → Remotion theme key ───────────────────────────────────────────────
GENRE_MAP = {
    "jazz": "jazz", "blues": "blues",
    "rock": "rock", "classic rock": "rock", "classic_rock": "rock",
    "funk": "funk", "soul": "funk",
    "disco": "disco",
    "pop": "pop_80s", "pop/funk": "funk", "synth": "synth",
    "new wave": "new_wave", "new_wave": "new_wave",
    "hip hop": "hip_hop", "hip-hop": "hip_hop", "rap": "hip_hop",
    "r&b": "rnb", "rnb": "rnb",
    "grunge": "grunge", "alternative": "grunge",
    "country": "country", "folk": "folk",
    "reggae": "reggae",
}

def map_genre(genre: str) -> str:
    return GENRE_MAP.get(genre.lower().strip(), "default")


# ── Helpers ──────────────────────────────────────────────────────────────────
def run(cmd: list, label: str, cwd=None, timeout=300) -> str:
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
    elapsed = time.time() - t0
    if r.returncode != 0:
        print(f"\n[{label}] FAILED (exit {r.returncode}):", file=sys.stderr)
        print(r.stderr[-600:], file=sys.stderr)
        raise RuntimeError(f"{label} failed")
    print(f"  [{label}] done in {elapsed:.1f}s")
    return r.stdout.strip()


def probe_duration(path: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", str(path)
    ]).decode()
    data = json.loads(out)
    for s in data["streams"]:
        if "duration" in s:
            return float(s["duration"])
    return 30.0


def slug(text: str) -> str:
    return re.sub(r"[^\w\-]", "_", text)[:60]


# ── Pipeline steps ────────────────────────────────────────────────────────────
def step_find_or_download(args) -> Path:
    """Return a local video path."""
    # 1. --source flag
    if args.source:
        p = Path(args.source)
        if not p.exists():
            p = BASE / args.source
        if not p.exists():
            sys.exit(f"ERROR: --source file not found: {args.source}")
        print(f"  [source] Using provided file: {p}")
        return p

    # 2. Already in input/
    s = slug(f"{args.artist}_{args.song}")
    for ext in ("mp4", "mkv", "webm", "mov"):
        p = INPUT_DIR / f"{s}.{ext}"
        if p.exists():
            print(f"  [source] Found in input/: {p}")
            return p

    # 3. Attempt yt-dlp
    print(f"  [source] No local file — attempting yt-dlp download...")
    from download_source import download
    p = download(args.artist, args.song, TEMP_DIR)
    if p:
        return p

    # 4. Give up gracefully
    print("\n────────────────────────────────────────────────")
    print("yt-dlp לא הצליח להוריד. אפשרויות:")
    print(f"  א) שים קובץ וידאו ב-  input/{s}.mp4")
    print(f"  ב) הרץ שוב עם:  --source input/YOUR_FILE.mp4")
    print("────────────────────────────────────────────────\n")
    sys.exit(1)


def step_clip(src: Path, start: float, duration: float) -> Path:
    """Trim clip with FFmpeg (fast seek, copy streams)."""
    out = TEMP_DIR / f"{src.stem}_clip.mp4"
    if out.exists():
        print(f"  [clip] Already exists: {out.name}")
        return out
    run([
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(duration),
        "-i", str(src),
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ], "clip")
    return out


def step_silence_cut(src: Path) -> Path:
    out = TEMP_DIR / f"{src.stem}_cut.mp4"
    if out.exists():
        print(f"  [silence-cut] Already exists: {out.name}")
        return out
    run([
        str(VENV_AE), str(src),
        "--edit", "audio:threshold=4%",
        "--output-file", str(out),
        "--no-open",
    ], "silence-cut", timeout=600)
    return out


def step_normalize(src: Path) -> Path:
    out = TEMP_DIR / f"{src.stem}_norm.mp4"
    if out.exists():
        print(f"  [normalize] Already exists: {out.name}")
        return out

    # Pass 1: measure
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
        "-f", "null", "-",
    ], capture_output=True, text=True)
    # Extract JSON block from stderr
    stderr = r.stderr
    start = stderr.rfind("{")
    end   = stderr.rfind("}") + 1
    meas  = json.loads(stderr[start:end])

    # Pass 2: apply
    af = (
        f"loudnorm=I=-14:TP=-1:LRA=11"
        f":measured_I={meas['input_i']}"
        f":measured_TP={meas['input_tp']}"
        f":measured_LRA={meas['input_lra']}"
        f":measured_thresh={meas['input_thresh']}"
        f":offset={meas['target_offset']}"
        ":linear=true"
    )
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-af", af, "-c:v", "copy", str(out),
    ], "normalize")
    return out


def step_render(norm_path: Path, args, duration: float) -> Path:
    out_name = f"{slug(args.artist)}_{slug(args.song)}_final.mp4"
    out_path  = OUTPUT_DIR / out_name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    theme_key = map_genre(args.genre)
    frames    = int(duration * 30)

    # Remotion expects paths relative to video-studio/
    rel_src = "../" + str(norm_path.relative_to(BASE))

    props = json.dumps({
        "src":             rel_src,
        "artist":          args.artist,
        "song":            args.song,
        "year":            str(args.year),
        "genre":           args.genre,
        "themeKey":        theme_key,
        "durationInFrames": frames,
    }, ensure_ascii=False)

    out_rel = "../" + str(out_path.relative_to(BASE))

    run([
        "npx", "remotion", "render",
        "src/index.ts",
        "ChannelBranding",
        out_rel,
        "--props", props,
    ], "remotion-render", cwd=str(STUDIO_DIR), timeout=1200)

    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="חזרה לעבר — TikTok video pipeline")
    p.add_argument("--artist",        required=True,          help="Artist / band name")
    p.add_argument("--song",          required=True,          help="Song title")
    p.add_argument("--year",          required=True, type=int, help="Release year")
    p.add_argument("--genre",         required=True,          help="Genre / mood (e.g. rock, disco, synth)")
    p.add_argument("--source",        default=None,           help="Local file path (skips download)")
    p.add_argument("--clip-start",    type=float, default=0,  help="Clip start in seconds (default: 0)")
    p.add_argument("--clip-duration", type=float, default=30, help="Clip length in seconds (default: 30)")
    p.add_argument("--skip-cut",      action="store_true",    help="Skip auto-editor silence cut")
    p.add_argument("--skip-normalize",action="store_true",    help="Skip audio normalization")
    args = p.parse_args()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n━━━ חזרה לעבר ━━━  {args.artist} — {args.song} ({args.year})  [{args.genre}]")

    print("\n[1/5] מקור וידאו")
    src = step_find_or_download(args)

    print("\n[2/5] חיתוך קטע")
    total_dur = probe_duration(src)
    # If clip-start > 0 or clip-duration < full video, trim
    effective_dur = min(args.clip_duration, total_dur - args.clip_start)
    if args.clip_start > 0 or effective_dur < total_dur - 1:
        src = step_clip(src, args.clip_start, effective_dur)
    else:
        print(f"  [clip] No trim needed ({total_dur:.1f}s)")

    print("\n[3/5] ניקוי שתיקות")
    if args.skip_cut:
        print("  [silence-cut] Skipped (--skip-cut)")
        cut = src
    else:
        try:
            cut = step_silence_cut(src)
        except RuntimeError:
            print("  [silence-cut] Warning: auto-editor failed, using original clip")
            cut = src

    print("\n[4/5] נרמול אודיו (-14 LUFS)")
    if args.skip_normalize:
        print("  [normalize] Skipped (--skip-normalize)")
        norm = cut
    else:
        norm = step_normalize(cut)

    print("\n[5/5] Remotion render")
    final_dur = probe_duration(norm)
    out = step_render(norm, args, final_dur)

    size_mb = out.stat().st_size / 1_048_576
    print(f"\n━━━ מוכן ━━━  {out.name}  ({size_mb:.1f} MB)  /{out.relative_to(BASE)}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    main()
