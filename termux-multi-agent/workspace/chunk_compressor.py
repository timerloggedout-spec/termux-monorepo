#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batched 9‑gzip compression for large index files with streaming decompression.
Author: ArchWizard 🧙‍♂️
"""

import gzip
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Iterator, Any, Union, Optional
import struct

# ----------------------------------------------------------
--------------------
#  C H U N K   C O M P R E S S O R   (GZIP -9)
# ----------------------------------------------------------
--------------------

class ChunkedGzipWriter:
    """
    Streams a large JSON file (top‑level key by key) and compresses each value
    into a separate .gz chunk. Writes a binary .idx manifest mapping key → chunk.
    """
    def __init__(self, output_dir: Union[str, Path], chunk_size: int = 1024*1024):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_size = chunk_size
        self.manifest: Dict[str, Dict[str, Any]] = {}
        self._chunk_counter = 0

    def _next_chunk_name(self) -> str:
        self._chunk_counter += 1
        return f"chunk_{self._chunk_counter:06d}.gz"

    def compress_stream(self, json_path: Union[str, Path]) -> None:
        """
        Reads a large JSON file (top‑level object) and writes each key's data
        as a separate gzip‑9 chunk.
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        # First pass: lightweight key extraction without loading full value
        keys = self._extract_top_keys(json_path)
        total = len(keys)
        print(f"📦 Found {total} top‑level keys in {json_path.name}")

        # Second pass: stream each value and compress
        with open(json_path, 'rb') as f:
            # Move to first '{' after initial whitespace
            self._skip_to_first_object(f)
            
            for idx, key in enumerate(keys, 1):
                value_data = self._extract_value_for_key(f, key)
                if value_data is None:
                    print(f"⚠️  Key '{key}' not found, skipping")
                    continue
                
                chunk_name = self._next_chunk_name()
                chunk_path = self.output_dir / chunk_name
                
                # Compress with gzip -9
                with gzip.open(chunk_path, 'wb', compresslevel=9) as gz_out:
                    gz_out.write(value_data)
                
                # Record in manifest
                self.manifest[key] = {
                    "chunk": chunk_name,
                    "size_bytes": len(value_data),
                    "compressed_bytes": chunk_path.stat().st_size,
                    "offset": 0  # not used, full file per key
                }
                
                print(f"  [{idx}/{total}] {key} → {chunk_name} "
                      f"({len(value_data):,} B → {chunk_path.stat().st_size:,} B, "
                      f"ratio: {chunk_path.stat().st_size/len(value_data):.1%})")
        
        self._write_manifest()

    def _extract_top_keys(self, json_path: Path) -> list:
        """Extract top‑level keys without loading entire file."""
        keys = []
        with open(json_path, 'rb') as f:
            # Find first '{'
            self._skip_to_first_object(f)
            
            decoder = json.JSONDecoder()
            # Read incrementally to collect keys
            buf = b''
            in_string = False
            escape = False
            depth = 0
            key_mode = True  # True = expecting key, False = expecting value
            
            current_key = None
            
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                buf += chunk
                
                # Simple state machine to extract keys (not perfect for nested, but works for top-level)
                # Better: use ijson or manual parse. Here we use a robust approach with JSONDecoder
                # But for speed, we'll just use a streaming JSON parser trick
                pass
            
            # More reliable: reset and use raw JSON parsing with ijson if available
            # Fallback to reading whole file for key extraction (fast enough for 500MB)
            f.seek(0)
            self._skip_to_first_object(f)
            # Use a more direct method: parse first few bytes until we find keys
            # Actually, simplest: load just the keys with raw scanning
            f.seek(0)
            data = f.read(1024*1024)  # read first MB to get keys
            # Find keys with regex?
            import re
            # Extract keys from {"key": 
            pattern = rb'"([^\\"]+)"\s*:'
            keys_raw = re.findall(pattern, data)
            # Deduplicate and keep order
            seen = set()
            keys = []
            for k in keys_raw:
                k_str = k.decode('utf-8')
                if k_str not in seen:
                    seen.add(k_str)
                    keys.append(k_str)
            return keys

    def _skip_to_first_object(self, f):
        """Skip whitespace until finding '{'"""
        while True:
            ch = f.read(1)
            if not ch:
                raise EOFError("Empty file")
            if ch == b'{':
                break

    def _extract_value_for_key(self, f, key: str) -> Optional[bytes]:
        """
        Extract the JSON value for a specific top‑level key by streaming.
        Returns raw bytes of the value (excluding the key and colon).
        """
        # Reset to beginning of file
        f.seek(0)
        self._skip_to_first_object(f)
        
        # Search for key pattern: "key":
        key_pattern = f'"{key}"'.encode()
        while True:
            line = f.readline()
            if not line:
                break
            if key_pattern in line:
                # Found the key, now extract the value
                # Find colon after key
                colon_pos = line.find(b':', line.find(key_pattern))
                if colon_pos == -1:
                    # Value might be on next line
                    value_start = len(line)
                    value_parts = [line[colon_pos+1:]]
                    # Read until we have a complete JSON value
                    depth = 0
                    in_string = False
                    escape = False
                    value_data = b''
                    # Continue reading
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        value_parts.append(chunk)
                        # Simple validation: find matching brace/bracket
                        # But easier: use JSONDecoder to parse just this value
                        combined = b''.join(value_parts)
                        try:
                            decoder = json.JSONDecoder()
                            val, _ = decoder.raw_decode(combined.decode('utf-8'))
                            # Successfully parsed, now serialize it back to bytes
                            return json.dumps(val, separators=(',', ':')).encode('utf-8')
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            continue
                    return None
                else:
                    value_part = line[colon_pos+1:].lstrip()
                    # Try to parse this part
                    try:
                        decoder = json.JSONDecoder()
                        val, _ = decoder.raw_decode(value_part.decode('utf-8'))
                        return json.dumps(val, separators=(',', ':')).encode('utf-8')
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Value spans multiple lines
                        value_parts = [value_part]
                        while True:
                            next_line = f.readline()
                            if not next_line:
                                break
                            value_parts.append(next_line)
                            combined = b''.join(value_parts)
                            try:
                                decoder = json.JSONDecoder()
                                val, _ = decoder.raw_decode(combined.decode('utf-8'))
                                return json.dumps(val, separators=(',', ':')).encode('utf-8')
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                continue
                        return None
        return None

    def _write_manifest(self) -> None:
        """Write manifest as binary index file for fast lookup."""
        manifest_path = self.output_dir / "index.idx"
        with open(manifest_path, 'wb') as f:
            # Write header: magic number + version
            f.write(b'GZIX')  # magic
            f.write(struct.pack('<I', 1))  # version
            f.write(struct.pack('<Q', len(self.manifest)))  # num entries
            
            for key, info in self.manifest.items():
                key_bytes = key.encode('utf-8')
                f.write(struct.pack('<H', len(key_bytes)))  # key length
                f.write(key_bytes)
                # Write chunk filename
                chunk_bytes = info['chunk'].encode('utf-8')
                f.write(struct.pack('<H', len(chunk_bytes)))
                f.write(chunk_bytes)
                # Write metadata
                f.write(struct.pack('<QQQ', 
                                   info['size_bytes'],
                                   info['compressed_bytes'],
                                   info['offset']))
        
        # Also write human‑readable manifest
        readable_path = self.output_dir / "manifest.json"
        with open(readable_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        print(f"✅ Manifest written to {manifest_path} and {readable_path}")


# ----------------------------------------------------------
--------------------
#  S T R E A M I N G   D E C O M P R E S S O R
# ----------------------------------------------------------
--------------------

class StreamingDecompressor:
    """
    Streaming decompressor that yields key‑value pairs from chunked gzip files.
    """
    def __init__(self, index_dir: Union[str, Path]):
        self.index_dir = Path(index_dir)
        self.manifest = self._load_manifest()
        self.chunk_dir = self.index_dir

    def _load_manifest(self) -> Dict[str, Dict[str, Any]]:
        """Load binary or JSON manifest."""
        idx_path = self.index_dir / "index.idx"
        if idx_path.exists():
            return self._load_binary_manifest(idx_path)
        else:
            json_path = self.index_dir / "manifest.json"
            if json_path.exists():
                with open(json_path, 'r') as f:
                    return json.load(f)
            raise FileNotFoundError(f"No manifest found in {self.index_dir}")

    def _load_binary_manifest(self, idx_path: Path) -> Dict[str, Dict[str, Any]]:
        manifest = {}
        with open(idx_path, 'rb') as f:
            magic = f.read(4)
            if magic != b'GZIX':
                raise ValueError("Invalid index file format")
            version = struct.unpack('<I', f.read(4))[0]
            if version != 1:
                raise ValueError(f"Unsupported index version: {version}")
            num_entries = struct.unpack('<Q', f.read(8))[0]
            
            for _ in range(num_entries):
                key_len = struct.unpack('<H', f.read(2))[0]
                key = f.read(key_len).decode('utf-8')
                chunk_len = struct.unpack('<H', f.read(2))[0]
                chunk_name = f.read(chunk_len).decode('utf-8')
                size_bytes, compressed_bytes, offset = struct.unpack('<QQQ', f.read(24))
                manifest[key] = {
                    "chunk": chunk_name,
                    "size_bytes": size_bytes,
                    "compressed_bytes": compressed_bytes,
                    "offset": offset
                }
        return manifest

    def stream_all(self) -> Iterator[tuple[str, Any]]:
        """Stream all key‑value pairs in order."""
        for key, info in self.manifest.items():
            chunk_path = self.chunk_dir / info['chunk']
            with gzip.open(chunk_path, 'rb') as gz_f:
                data = gz_f.read()
                value = json.loads(data.decode('utf-8'))
                yield key, value

    def get(self, key: str) -> Any:
        """Retrieve a single key's value by decompressing its chunk."""
        if key not in self.manifest:
            raise KeyError(f"Key '{key}' not found in manifest")
        info = self.manifest[key]
        chunk_path = self.chunk_dir / info['chunk']
        with gzip.open(chunk_path, 'rb') as gz_f:
            data = gz_f.read()
            return json.loads(data.decode('utf-8'))

    def decompress_to_file(self, output_json_path: Union[str, Path]) -> None:
        """Reconstruct the original JSON file by streaming all chunks."""
        output_path = Path(output_json_path)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write('{\n')
            first = True
            for key, value in self.stream_all():
                if not first:
                    out_f.write(',\n')
                first = False
                json.dump(key, out_f)
                out_f.write(': ')
                json.dump(value, out_f, separators=(',', ':'))
            out_f.write('\n}')
        print(f"✅ Reconstructed JSON written to {output_path}")


# ----------------------------------------------------------
--------------------
#  M A I N   E X E C U T I O N   (BATCH MODE)
# ----------------------------------------------------------
--------------------

def compress_all_targets(target_dir: str = "compressed_chunks"):
    """
    Compress all three target JSON files into chunked gzip archives.
    """
    targets = [
        "correlation_index.json",
        "message_index.json",
        "versioned_provenance_full.json"
    ]
    
    for target in targets:
        if not os.path.exists(target):
            print(f"⚠️  Target file not found: {target}, skipping")
            continue
        
        print(f"\n🔨 Processing {target}...")
        output_subdir = os.path.join(target_dir, target.replace('.json', ''))
        writer = ChunkedGzipWriter(output_subdir)
        writer.compress_stream(target)
        print(f"✨ Done: {output_subdir}")


def interactive_demo():
    """
    Interactive demonstration: compress a sample file, then stream decompress.
    """
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        if not os.path.exists(json_file):
            print(f"File not found: {json_file}")
            return
        out_dir = sys.argv[2] if len(sys.argv) > 2 else "compressed_output"
        writer = ChunkedGzipWriter(out_dir)
        writer.compress_stream(json_file)
        
        # Demo decompression
        print("\n📖 Decompressing and streaming...")
        decomp = StreamingDecompressor(out_dir)
        for i, (key, value) in enumerate(decomp.stream_all()):
            print(f"  [{i+1}] {key}: {str(value)[:100]}...")
            if i >= 4:
                print("  ... (truncated)")
                break
        print("✅ Streaming demo complete")
    else:
        print("Usage: python chunk_compressor.py <large_json_file> [output_dir]")
        print("Or run compress_all_targets() to compress the three predefined files.")


if __name__ == "__main__":
    # Uncomment to compress all three targets:
    # compress_all_targets()
    
    # Or run with command line argument:
    interactive_demo()
