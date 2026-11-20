#!/usr/bin/env python3
"""Chunk a large JSON file in parallel, adapting to free memory & CPU."""
import json, subprocess, gzip, sys, os, time
from pathlib import Path
from multiprocessing import Pool, cpu_count
from functools import partial

def get_free_mem_kb():
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemAvailable' in line:
                    return int(line.split()[1])
    except:
        return 999999  # assume unlimited

def write_chunk(key_clean, value, out_dir):
    """Write a single chunk (called by worker processes)."""
    chunk_path = out_dir / f'{key_clean}.json.gz'
    with gzip.open(chunk_path, 'wb') as gf:
        gf.write(json.dumps(value, indent=2).encode())
    return (key_clean, str(chunk_path), chunk_path.stat().st_size)

def safe_chunk_parallel(input_file, output_dir):
    input_path = Path(input_file).expanduser()
    out_dir = Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Stream all keys first (memory: only list of keys, not values)
    keys_proc = subprocess.run(
        ['jq', '-r', 'keys[]', str(input_path)],
        capture_output=True, text=True
    )
    all_keys = [k for k in keys_proc.stdout.strip().split('\n') if k]
    total = len(all_keys)
    print(f"Total keys: {total}")

    # Prepare arguments: we'll extract each key's value on the fly in workers
    # using jq to grab just that key. We'll pass (key, input_path, out_dir) to workers.
    tasks = [(key, str(input_path), str(out_dir)) for key in all_keys]

    # Determine initial pool size based on available memory
    free_mem = get_free_mem_kb()
    # Each worker may use ~50 MB peak; aim for 300 MB headroom
    max_workers = max(1, min(cpu_count(), (free_mem - 300000) // 50000))
    print(f"Starting with {max_workers} parallel workers (free mem: {free_mem//1024} MB)")

    manifest = {}
    count = 0
    # We'll submit tasks in chunks and adjust pool size dynamically
    pool = None
    try:
        for i in range(0, total, max_workers):
            batch = tasks[i:i+max_workers]
            # Re‑check memory before launching batch
            free_mem = get_free_mem_kb()
            desired_workers = max(1, min(cpu_count(), (free_mem - 200000) // 50000))
            if pool is None or desired_workers != max_workers:
                if pool:
                    pool.close()
                    pool.join()
                max_workers = desired_workers
                pool = Pool(processes=max_workers)
                print(f"  Adjusted to {max_workers} workers (free mem: {free_mem//1024} MB)")

            # Map jobs to pool
            results = []
            for key, inp, out in batch:
                # Extract value for this key with jq, write chunk
                # We'll do extraction inside a worker function
                r = pool.apply_async(_extract_and_write, (key, inp, out))
                results.append(r)

            for r in results:
                key_clean, path, sz = r.get()
                manifest[key_clean] = {"file": path, "size": sz}
                count += 1
                if count % 100 == 0:
                    print(f"  {count}/{total} chunks written …", end='\r')

    finally:
        if pool:
            pool.close()
            pool.join()

    with open(out_dir / 'chunks.idx.json', 'w') as mf:
        json.dump(manifest, mf, indent=2)
    print(f"\n✅ {count} chunks written to {out_dir}")

def _extract_and_write(key, input_path_str, out_dir_str):
    """Worker: extract one key with jq, compress, return stats."""
    import subprocess, gzip, json
    from pathlib import Path
    out_dir = Path(out_dir_str)
    key_clean = key.replace('/', '_').replace(' ', '_')[:80]
    chunk_path = out_dir / f'{key_clean}.json.gz'
    # Extract just this key
    val = subprocess.run(
        ['jq', '-c', '--arg', 'k', key, '.[$k]', input_path_str],
        capture_output=True, text=True
    )
    data = json.loads(val.stdout)
    with gzip.open(chunk_path, 'wb') as gf:
        gf.write(json.dumps(data, indent=2).encode())
    return (key, str(chunk_path), chunk_path.stat().st_size)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 safe_chunk_parallel.py <source.json> <output_dir>")
        sys.exit(1)
    safe_chunk_parallel(sys.argv[1], sys.argv[2])
