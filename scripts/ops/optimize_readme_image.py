#!/usr/bin/env python3
"""Optimize images for README / docs embedding — fail-closed on corrupt inputs.

Repeatable agent path for termux-monorepo (and similar). Validates the source
before any transform; refuses to emit a broken asset.

Usage:
  python3 scripts/ops/optimize_readme_image.py INPUT.png -o docs/assets/foo.png
  python3 scripts/ops/optimize_readme_image.py INPUT.png --max-width 720 --max-bytes 400000
  python3 scripts/ops/optimize_readme_image.py INPUT.png --format jpeg --quality 85

Exit codes:
  0 success
  1 usage / arg error
  2 source missing or unreadable
  3 source corrupt / fails load (do not embed)
  4 could not meet max-bytes after attempts
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    print("ERROR: Pillow required (pip install Pillow)", file=sys.stderr)
    sys.exit(1)


def validate_load(path: Path) -> Image.Image:
    """Open and fully decode. Raises on truncation / bad IDAT / filter errors."""
    if not path.is_file():
        raise FileNotFoundError(path)
    data = path.read_bytes()
    if len(data) < 24:
        raise ValueError(f"file too small ({len(data)} bytes)")
    # quick PNG magic check when applicable
    if path.suffix.lower() == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("PNG signature missing")
    im = Image.open(path)
    im.load()  # force full decode — catches truncated IDAT
    if im.width < 1 or im.height < 1:
        raise ValueError(f"invalid dimensions {im.size}")
    return im


def md5_of(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def has_useful_alpha(im: Image.Image) -> bool:
    if im.mode != "RGBA":
        return False
    extrema = im.getchannel("A").getextrema()
    return not (extrema[0] == 255 and extrema[1] == 255)


def optimize(
    src: Path,
    dst: Path,
    max_width: int,
    max_bytes: int,
    fmt: str,
    quality: int,
) -> dict:
    im = validate_load(src)
    report = {
        "src": str(src),
        "src_bytes": src.stat().st_size,
        "src_md5": md5_of(src),
        "src_size": list(im.size),
        "src_mode": im.mode,
    }

    # RGB for JPEG; keep alpha for PNG when present
    work = im
    if fmt.lower() in ("jpeg", "jpg") and work.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", work.size, (255, 255, 255))
        if work.mode == "P":
            work = work.convert("RGBA")
        bg.paste(work, mask=work.split()[-1] if work.mode in ("RGBA", "LA") else None)
        work = bg
    elif work.mode not in ("RGB", "RGBA", "L"):
        work = work.convert("RGBA" if "A" in work.mode else "RGB")

    if work.width > max_width:
        ratio = max_width / work.width
        new_size = (max_width, max(1, int(work.height * ratio)))
        work = work.resize(new_size, Image.Resampling.LANCZOS)
        report["resized_to"] = list(work.size)

    dst.parent.mkdir(parents=True, exist_ok=True)
    q = quality
    last_bytes = None
    for attempt in range(8):
        save_kw: dict = {"optimize": True}
        out_fmt = "JPEG" if fmt.lower() in ("jpeg", "jpg") else "PNG"
        if out_fmt == "JPEG":
            save_kw["quality"] = q
            save_kw["progressive"] = True
        else:
            to_save = work
            if to_save.mode == "RGBA" and not has_useful_alpha(to_save):
                to_save = to_save.convert("RGB")
            work = to_save
        work.save(dst, format=out_fmt, **save_kw)
        last_bytes = dst.stat().st_size
        # re-validate output
        validate_load(dst)
        if last_bytes <= max_bytes:
            report.update(
                {
                    "dst": str(dst),
                    "dst_bytes": last_bytes,
                    "dst_md5": md5_of(dst),
                    "dst_size": list(Image.open(dst).size),
                    "format": out_fmt,
                    "quality": q if out_fmt == "JPEG" else None,
                    "attempts": attempt + 1,
                }
            )
            return report
        if out_fmt == "JPEG":
            q = max(40, q - 8)
        else:
            if work.width <= 480:
                break
            nw = int(work.width * 0.85)
            nh = max(1, int(work.height * 0.85))
            work = work.resize((nw, nh), Image.Resampling.LANCZOS)

    raise RuntimeError(
        f"could not meet max-bytes={max_bytes} (last={last_bytes}). "
        "Raise --max-bytes or lower --max-width / --quality."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="Source image path")
    p.add_argument("-o", "--output", type=Path, required=True, help="Output path")
    p.add_argument("--max-width", type=int, default=720, help="Max width px (default 720)")
    p.add_argument("--max-bytes", type=int, default=400_000, help="Max output size bytes (default 400000)")
    p.add_argument("--format", choices=("png", "jpeg", "jpg"), default="png")
    p.add_argument("--quality", type=int, default=85, help="JPEG quality (default 85)")
    p.add_argument("--json", action="store_true", help="Print report as JSON")
    args = p.parse_args(argv)

    try:
        report = optimize(
            args.input,
            args.output,
            max_width=args.max_width,
            max_bytes=args.max_bytes,
            fmt=args.format,
            quality=args.quality,
        )
    except FileNotFoundError as e:
        print(f"ERROR: source missing: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        msg = str(e).lower()
        if any(x in msg for x in ("unrecognized data stream", "truncated", "bad adaptive filter", "cannot identify")):
            print(f"ERROR: source corrupt — do not embed: {e}", file=sys.stderr)
            return 3
        if "could not meet max-bytes" in str(e):
            print(f"ERROR: {e}", file=sys.stderr)
            return 4
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.json:
        import json
        print(json.dumps(report, indent=2))
    else:
        print(
            f"OK {report['src_bytes']}B {report['src_size']} → "
            f"{report['dst_bytes']}B {report.get('dst_size')} "
            f"md5={report['dst_md5'][:12]}… attempts={report['attempts']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
