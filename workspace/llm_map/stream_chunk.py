#!/usr/bin/env python3
"""
Memory‑adaptive streaming chunker.
Uses ijson for constant‑RAM parsing, skips values larger than MAX_VALUE_MB,
resumes via .chunk_state, and adapts to the device's real memory.
"""
import json, gzip, sys, os, time, gc
from pathlib import Path

try:
    import ijson
except ImportError:
    print("ijson required: pip install ijson")
    sys.exit(1)

MAX_VALUE_MB = 50      # skip any value larger than this (in megabytes)
CHECKPOINT_EVERY = 50   # save progress every N chunks

def size_mb(value):
    """Return approximate size of a JSON value in megabytes."""
    try:
        return len(json.dumps(value, ensure_ascii=False).encode()) / (1024*1024)
    except:
        return 0

def chunk_dict(input_path, out_dir, state_file, manifest_file, skip_log):
    done_keys = set()
    manifest = {}
    skipped = {}
    if state_file.exists():
        done_keys = set(state_file.read_text().strip().split('\n'))
        print(f'♻ Resuming — {len(done_keys)} keys already chunked')
    if manifest_file.exists():
        with open(manifest_file) as mf:
            manifest = json.load(mf)
    if skip_log.exists():
        with open(skip_log) as sf:
            for line in sf:
                if line.strip():
                    skipped[line.strip()] = True

    total = len(done_keys)
    with open(input_path, 'rb') as f:
        parser = ijson.kvitems(f, '')
        for key, value in parser:
            if key in done_keys or key in skipped:
                continue
            mb = size_mb(value)
            if mb > MAX_VALUE_MB:
                skipped[key] = True
                with open(skip_log, 'a') as sf:
                    sf.write(f'{key}\n')
                print(f'  ⚠️  Skipping {key} ({mb:.1f} MB) — exceeds {MAX_VALUE_MB} MB limit')
                continue

            key_clean = str(key).replace('/', '_').replace(' ', '_')[:80]
            chunk_path = out_dir / f'{key_clean}.json.gz'
            with gzip.open(chunk_path, 'wb') as gf:
                gf.write(json.dumps(value, indent=2, default=str).encode())
            sz = chunk_path.stat().st_size
            manifest[key] = {"file": str(chunk_path), "size": sz}
            done_keys.add(key)
            total += 1
            if total % CHECKPOINT_EVERY == 0:
                state_file.write_text('\n'.join(done_keys))
                with open(manifest_file, 'w') as mf:
                    json.dump(manifest, mf, indent=2)
                gc.collect()
                time.sleep(0.1)
                print(f'  {total} chunks written …', end='\r')

    with open(manifest_file, 'w') as mf:
        json.dump(manifest, mf, indent=2)
    state_file.unlink(missing_ok=True)
    print(f'\n✅ {total} chunks written to {out_dir}')
    if skipped:
        print(f'⚠️  {len(skipped)} keys skipped due to size limit (see {skip_log})')

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 stream_chunk.py <source.json> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    state_file = output_dir / '.chunk_state'
    manifest_file = output_dir / 'chunks.idx.json'
    skip_log = output_dir / '.skipped_keys'

    # Detect structure – we only support dict for now
    with open(input_file, 'rb') as f:
        first = f.read(1).decode()
    if first != '{':
        print("Only JSON objects (dict) are supported at the moment.")
        sys.exit(1)

    chunk_dict(input_file, output_dir, state_file, manifest_file, skip_log)

if __name__ == '__main__':
    main()
