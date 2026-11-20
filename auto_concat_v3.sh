#!/usr/bin/env bash
# ============================================================
#  auto_concat_v3.sh
#  - Copies files to local work dir
#  - Finds overlaps using numpy/scipy (no audio-offset-finder)
#  - Creates smooth crossfaded mp4s
#  - Moves results back to the source folder
#  - Prints everything to console + log
# ============================================================

# ---------- CONFIG ----------
SOURCE_DIR="/data/data/com.termux/files/home/storage/downloads"
WORK_BASE="$HOME/concat_work"
FADE_DURATION="0.5"   # seconds
# ----------------------------

# Create timestamped work directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORK_DIR="${WORK_BASE}_${TIMESTAMP}"
mkdir -p "$WORK_DIR" || { echo "Cannot create $WORK_DIR"; exit 1; }
LOG="$WORK_DIR/auto_concat.log"

# Log everything to console and file
exec > >(tee -a "$LOG") 2>&1
echo "=== Started at $(date) ==="
echo "Work directory: $WORK_DIR"

# Install required system packages if missing
echo "Checking dependencies..."
pkg install -y python python-numpy python-scipy ffmpeg 2>/dev/null

# ---------- FILE SETS (filenames only) ----------
SET1_ReAlign=(
  "ReAli(gn)z{N}action Begins - Rap Version, hard fast. (1).mp4"
  "ReAli(gn)z{N}action Begins - Rap Version, hard fast. (2).mp4"
)
SET2_Reticular=(
  "Reticular Crown (1).mp4"
  "Reticular Crown (3).mp4"
  "Reticular Crown (5).mp4"
  "Reticular Crown (6).mp4"
  "Reticular Crown (7).mp4"
  "Reticular Crown (8).mp4"
  "Reticular Crown.mp4"
)
SET3_Legendary=(
  "S'Legendary  (1).mp4"
  "S'Legendary  (2).mp4"
  "S'Legendary  (3).mp4"
  "S'Legendary .mp4"
)
SET4_Glass=(
  "Glass Light 432Hz (1).mp4"
  "Glass Light 432Hz (2).mp4"
  "Glass Light 432Hz (3).mp4"
  "Glass Light 432Hz (4).mp4"
  "Glass Light 432Hz (5).mp4"
  "Glass Light 432Hz (6).mp4"
  "Glass Light 432Hz (7).mp4"
  "Glass Light 432Hz (8).mp4"
  "Glass Light 432Hz (9).mp4"
  "Glass Light 432Hz (10).mp4"
)

ALL_FILES=("${SET1_ReAlign[@]}" "${SET2_Reticular[@]}" "${SET3_Legendary[@]}" "${SET4_Glass[@]}")

# ---------- COPY FILES TO WORK DIR ----------
echo "Copying ${#ALL_FILES[@]} files to $WORK_DIR ..."
for f in "${ALL_FILES[@]}"; do
  src="$SOURCE_DIR/$f"
  if [ -f "$src" ]; then
    cp "$src" "$WORK_DIR/" && echo "  ✅ $f"
  else
    echo "  ❌ MISSING: $f"
    exit 1
  fi
done
echo "All files copied successfully."
cd "$WORK_DIR" || exit 1

# ---------- PYTHON PROCESSING SCRIPT ----------
PY_FILE="$WORK_DIR/process_sets.py"

cat > "$PY_FILE" << 'PYEOF'
import subprocess, os, sys, tempfile, numpy as np
from scipy import signal

# ----- SETS DEFINITION -----
sets = {
    "ReAli(gn)z_action": [
        "ReAli(gn)z{N}action Begins - Rap Version, hard fast. (1).mp4",
        "ReAli(gn)z{N}action Begins - Rap Version, hard fast. (2).mp4"
    ],
    "Reticular_Crown": [
        "Reticular Crown (1).mp4",
        "Reticular Crown (3).mp4",
        "Reticular Crown (5).mp4",
        "Reticular Crown (6).mp4",
        "Reticular Crown (7).mp4",
        "Reticular Crown (8).mp4",
        "Reticular Crown.mp4"
    ],
    "S_Legendary": [
        "S'Legendary  (1).mp4",
        "S'Legendary  (2).mp4",
        "S'Legendary  (3).mp4",
        "S'Legendary .mp4"
    ],
    "Glass_Light_432Hz": [
        "Glass Light 432Hz (1).mp4",
        "Glass Light 432Hz (2).mp4",
        "Glass Light 432Hz (3).mp4",
        "Glass Light 432Hz (4).mp4",
        "Glass Light 432Hz (5).mp4",
        "Glass Light 432Hz (6).mp4",
        "Glass Light 432Hz (7).mp4",
        "Glass Light 432Hz (8).mp4",
        "Glass Light 432Hz (9).mp4",
        "Glass Light 432Hz (10).mp4"
    ]
}

FADE_DURATION = 0.5
OUTPUT_DIR = "./joined_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_duration(file):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def load_audio_mono(file, duration, sample_rate=8000):
    """Extract mono audio from file as 32-bit float numpy array."""
    cmd = ['ffmpeg', '-y', '-i', file, '-t', str(duration),
           '-f', 'f32le', '-acodec', 'pcm_f32le', '-ac', '1', '-ar', str(sample_rate), '-']
    proc = subprocess.run(cmd, capture_output=True)
    return np.frombuffer(proc.stdout, dtype=np.float32)

def find_offset(file1, file2):
    """Return positive offset (seconds) that best aligns end of file1 with start of file2."""
    dur1 = get_duration(file1)
    # Take up to 30 seconds from the end of file1 (or less if file is shorter)
    end_len = min(30, dur1)
    # And first 30 seconds of file2 (or its total length if shorter)
    start_len = min(30, get_duration(file2))

    a = load_audio_mono(file1, duration=end_len, sample_rate=8000)
    b = load_audio_mono(file2, duration=start_len, sample_rate=8000)

    # Cross-correlation: correlate a (reference) and b (target), find lag where correlation is max
    corr = signal.correlate(a, b, mode='full')
    lag = np.argmax(np.abs(corr)) - len(a)  # shift of b relative to a
    # lag in samples; if lag is negative, b starts later (overlap = len(a)/sr + lag/sr)
    # We want overlap in seconds: how much of the end of file1 matches the start of file2
    # Overlap = (len(a) + lag) / sample_rate if lag is negative, else (len(a) - lag)/sr? Wait.
    # Standard: if lag is negative, b is shifted later; we look for overlap = end_len - (|lag|/sr)
    # But let's calculate correctly: alignment point: a's index i aligns with b's index i+lag.
    # If lag is negative, the beginning of b aligns with a's sample at -lag.
    # For maximum overlap, we assume the shared segment ends at the end of a.
    # The length of the overlapping segment = (len(a) - (-lag)) / sr = (len(a) + lag) / sr
    # If lag is positive, b starts before a, but we only have the end of a; we'll assume the overlap is (len(b)-lag)/sr, but simpler:
    # We'll use: overlap = (len(a) + lag) / sample_rate   if lag is negative, else (len(b) - lag) / sample_rate? This can get messy.
    # Better: use 'valid' mode and shift for offset.
    # Let's use a reliable method: compute correlation for all lags, then find lag where b best matches a.
    # Then offset = (len(a) + lag) / sr   (if lag negative, shift b forward)
    # But we want positive overlap seconds. Overlap = (len(a) + lag) / sr if lag negative, else (len(b) - lag) / sr if lag positive.
    # For simplicity, we'll just compute the absolute lag and adjust.
    # We'll use the correlation result from 'same' mode and find shift relative to a.
    # Let's do it this way: the correlation array index corresponds to lag = index - (len(a) - 1).
    lag = np.argmax(np.abs(corr)) - (len(a) - 1)
    # Now lag in samples: if negative, b is delayed; overlap = (len(a) + lag) / sr (since lag is negative, this reduces length)
    # If positive, b is early; overlap = (len(b) - lag) / sr.
    if lag <= 0:
        overlap_samples = len(a) + lag  # because lag is negative
    else:
        overlap_samples = len(b) - lag
    overlap = max(0, overlap_samples / 8000.0)
    return overlap

# Process sets
for set_name, files in sets.items():
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        print(f"\n⚠️  Skipping '{set_name}' – missing: {missing}")
        continue

    print(f"\n========== Processing: {set_name} ({len(files)} files) ==========")
    cmd = ['ffmpeg']
    for f in files:
        cmd.extend(['-i', f])

    filter_complex = ""
    last_video = "0:v"
    last_audio = "0:a"
    current_offset = 0.0
    dur_prev = get_duration(files[0])

    for i in range(1, len(files)):
        print(f"  Overlap detection: {files[i-1]} ←→ {files[i]}")
        overlap = find_offset(files[i-1], files[i])
        print(f"    Overlap = {overlap:.3f} seconds")

        current_offset += dur_prev - overlap
        dur_prev = get_duration(files[i])

        next_video = f"v{i-1}{i}"
        next_audio = f"a{i-1}{i}"
        filter_complex += (f"[{last_video}][{i}:v]xfade=transition=fade:"
                           f"duration={FADE_DURATION}:offset={current_offset:.3f}"
                           f"[{next_video}];")
        filter_complex += (f"[{last_audio}][{i}:a]acrossfade=d={FADE_DURATION}"
                           f"[{next_audio}];")
        last_video = next_video
        last_audio = next_audio

    out_file = os.path.join(OUTPUT_DIR, f"{set_name}_crossfaded.mp4")
    cmd.extend(['-filter_complex', filter_complex])
    cmd.extend(['-map', f'[{last_video}]', '-map', f'[{last_audio}]'])
    cmd.extend(['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                '-c:a', 'aac', '-b:a', '192k'])
    cmd.extend(['-y', out_file])
    print(f"  Encoding → {out_file}")
    subprocess.run(cmd)
    print(f"  ✅ Done: {out_file}")

print("\n=== All sets processed ===")
PYEOF

# Run the Python script
python3 "$PY_FILE"

# ---------- COPY RESULTS BACK TO SOURCE ----------
echo ""
echo "Moving finished files back to $SOURCE_DIR ..."
cp -v "$WORK_DIR/joined_videos/"*.mp4 "$SOURCE_DIR/" 2>/dev/null || echo "No output files to move."

echo ""
echo "=== Script finished at $(date) ==="
echo "Log: $LOG"
echo "Final videos copied to: $SOURCE_DIR"
echo "Work folder (can be deleted): $WORK_DIR"
