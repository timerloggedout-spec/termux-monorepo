#!/usr/bin/env python3
"""Split a large JSON dict by key, gzip each chunk, write a manifest."""
import json, gzip, sys, hashlib
from pathlib import Path

def safe_filename(key):
    safe = key.replace('/', '_').replace('\\', '_')
    if len(safe.encode('utf-8')) > 200:
        safe = hashlib.sha256(key.encode()).hexdigest()[:16]
    return safe

def chunk_by_key_streaming(source_path, output_dir):
    import ijson
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}

    print(f"Streaming {source_path} …")
    with open(source_path, 'rb') as f:
        for key, value_iter in ijson.kvitems(f, ''):
            chunk_path = output_dir / f"{safe_filename(key)}.json.gz"

            # value_iter may be a fully‑parsed small dict, or a generator
            if isinstance(value_iter, dict):
                # small dict – write directly
                with gzip.open(chunk_path, 'wt', compresslevel=9) as out:
                    json.dump(value_iter, out)
                sz = chunk_path.stat().st_size
                manifest[key] = {"file": str(chunk_path), "size": sz, "count": len(value_iter)}
                print(f"  {key}: {len(value_iter)} entries (dict) → {chunk_path} ({sz} bytes)")
                continue

            # It's a generator – stream items
            items = []
            is_dict = False
            count = 0
            try:
                first = next(iter(value_iter))   # may be a dict, list, or scalar
            except StopIteration:
                # empty iterator – write empty JSON array
                with gzip.open(chunk_path, 'wt', compresslevel=9) as out:
                    out.write('[]')
                manifest[key] = {"file": str(chunk_path), "size": chunk_path.stat().st_size, "count": 0}
                continue
            except TypeError:
                # value_iter is a list or scalar – wrap and write directly
                count = len(value_iter) if isinstance(value_iter, (list, tuple)) else 1
                out_data = {key: value_iter}
                gz_path = out_dir / f'{clean_key}.json.gz'
                with gzip.open(gz_path, 'wb') as gf:
                    gf.write(json.dumps(out_data, indent=2).encode())
                manifest[key] = {"file": str(gz_path), "size": gz_path.stat().st_size, "count": count}
                continue
            except StopIteration:
                with gzip.open(chunk_path, 'wt', compresslevel=9) as out:
                    out.write('[]')
                manifest[key] = {"file": str(chunk_path), "size": chunk_path.stat().st_size, "count": 0}
                print(f"  {key}: empty → {chunk_path}")
                continue

            if isinstance(first, (tuple, list)) and len(first) == 2 and isinstance(first[0], str):
                is_dict = True
                items.append(first)
            else:
                items.append(first)

            for item in value_iter:
                items.append(item)
                count += 1
            count += 1   # include first

            if is_dict:
                data = dict(items)
                with gzip.open(chunk_path, 'wt', compresslevel=9) as out:
                    json.dump(data, out)
            else:
                with gzip.open(chunk_path, 'wt', compresslevel=9) as out:
                    json.dump(items, out)

            sz = chunk_path.stat().st_size
            manifest[key] = {"file": str(chunk_path), "size": sz, "count": count}
            print(f"  {key}: {count} entries → {chunk_path} ({sz} bytes)")

    manifest_path = output_dir / 'chunks.idx.json'
    with open(manifest_path, 'w') as mf:
        json.dump(manifest, mf, indent=2)
    print(f"Manifest: {manifest_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 chunk_json.py <source.json> <output_dir>")
        sys.exit(1)
    chunk_by_key_streaming(sys.argv[1], sys.argv[2])
