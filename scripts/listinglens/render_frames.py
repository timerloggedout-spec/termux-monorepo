#!/usr/bin/env python3
"""Render beats-manifest frames and assemble the ListingLens demo MP4.

Frames are ffmpeg lavfi color cards + drawtext (text via textfile, so
no drawtext escaping hazards). Fixed geometry/fps of record:
1280x720 @ 30fps, each beat held FRAME_SECONDS. The renderer consumes
ONLY the beats manifest derived from the real demo run
(derive_manifest.py) — it adds no content of its own beyond layout.

Usage:
  python3 scripts/listinglens/render_frames.py \
      --beats beats.json --workdir frames/ --out listinglens-demo.mp4
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

WIDTH, HEIGHT, FPS = 1280, 720, 30
FRAME_SECONDS = 3
BG = "0x14100d"
FG = "0xf2e9dc"
FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def fontfile():
    for cand in FONT_CANDIDATES:
        if Path(cand).exists():
            return cand
    return None


def _run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr[-800:]}")
    return proc


def render_beat(beat, accent_hex, workdir, font):
    idx = beat["beat"]
    accent = "0x" + accent_hex.lstrip("#")
    texts = []
    heading_file = workdir / f"beat{idx}-heading.txt"
    heading_file.write_text(beat["heading"])
    texts.append((heading_file, 64, accent, 96))
    for i, line in enumerate(beat["lines"]):
        f = workdir / f"beat{idx}-line{i}.txt"
        f.write_text(line)
        texts.append((f, 34, FG, 220 + i * 52))
    filters = []
    for f, size, color, y in texts:
        filters.append(
            f"drawtext=fontfile={font}:textfile={f}:fontsize={size}"
            f":fontcolor={color}:x=80:y={y}")
    out = workdir / f"frame-{idx}.mp4"
    _run(["ffmpeg", "-y", "-f", "lavfi",
          "-i", f"color=c={BG}:s={WIDTH}x{HEIGHT}:d={FRAME_SECONDS}:r={FPS}",
          "-vf", ",".join(filters),
          "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])
    return out


def assemble(frames, out_path):
    # Segments share codec/geometry/fps, so stream-copy concat is
    # exact: total duration = beats x FRAME_SECONDS, no demuxer
    # duration-line edge cases.
    listfile = Path(out_path).with_suffix(".concat.txt")
    with open(listfile, "w") as fh:
        for fr in frames:
            fh.write(f"file '{Path(fr).resolve()}'\n")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
          "-c", "copy", str(out_path)])
    listfile.unlink()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    font = fontfile()
    if not font:
        raise RuntimeError("no DejaVu font found for drawtext")
    workdir = Path(a.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(a.beats).read_text())
    frames = [render_beat(b, manifest.get("accent", "#b5542d"), workdir, font)
              for b in manifest["beats"]]
    assemble(frames, a.out)
    print(f"assembled {a.out}: {len(frames)} frames x {FRAME_SECONDS}s "
          f"@ {WIDTH}x{HEIGHT}/{FPS}fps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
