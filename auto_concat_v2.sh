#!/usr/bin/env bash
# ============================================================
#  auto_concat_v2.sh
#  Copy files to local work dir, then join with auto overlap
#  detection & smooth crossfade.
#  Prints all output to console + saves log file.
# ============================================================

# ---------- CONFIG ----------
SOURCE_DIR="/data/data/com.termux/files/home/storage/downloads"
WORK_BASE="$HOME/concat_work"
# ----------------------------

# --- Create a timestamped work directory ---
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
WORK_DIR="${WORK_BASE}_${TIMESTAMP}"
mkdir -p "$WORK_DIR" || { echo "Cannot create work dir $WORK_DIR"; exit 1; }
LOG="$WORK_DIR/auto_concat.log"

# --- Start logging to both terminal and file ---
exec > >(tee -a "$LOG") 2>&1
echo "=== Started at $(date) ==="
echo "Work directory: $WORK_DIR"
echo "Source directory: $SOURCE_DIR"

# --- Check required tools ---
command -v ffmpeg >/dev/null 2>&1 || { echo "❌ ffmpeg not found. Install: pkg install ffmpeg"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 not found. Install: pkg install python"; exit 1; }
if ! python3 -c "import audio_offset_finder" 2>/dev/null; then
  echo "Installing audio-offset-finder..."
  pip install audio-offset-finder
fi

# ---------- DEFINE YOUR FOUR SETS (filenames only) ----------
# (the files will be copied and used with these exact names)
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

# --- Collect ALL filenames needed ---
ALL_FILES=(
  "${SET1_ReAlign[@]}"
  "${SET2_Reticular[@]}"
  "${SET3_Legendary[@]}"
  "${SET4_Glass[@]}"
)

# ---------- COPY FILES TO WORK DIRECTORY ----------
echo "Copying ${#ALL_FILES[@]} files to $WORK_DIR ..."
for f in "${ALL_FILES[@]}"; do
  src="$SOURCE_DIR/$f"
  if [ -f "$src" ]; then
    cp "$src" "$WORK_DIR/" && echo "  ✅ $f"
  else
    echo "  ❌ MISSING: $f (aborting)"
    exit 1
  fi
done
echo "All files copied successfully."
echo ""

# ---------- EMBEDDED PYTHON PROCESSING ----------
cd "$WORK_DIR" || exit 1

python3 -c <<'PYEOF'
import subprocess, os, tempfile

# Work inside the current directory (where files were copied)
# Define sets exactly as above, using basenames
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

def find_offset(file1, file2):
    with tempfile.TemporaryDirectory() as tmpdir:
        end_clip = os.path.join(tmpdir, "end.wav")
        start_clip = os.path.join(tmpdir, "start.wav")
        dur1 = get_duration(file1)
        # Use 20s to catch larger overlaps safely
        subprocess.run(['ffmpeg', '-y', '-ss', str(max(0, dur1-20)), '-i', file1,
                        '-t', '20', '-vn', end_clip], capture_output=True)
        subprocess.run(['ffmpeg', '-y', '-i', file2, '-t', '20', '-vn', start_clip],
                       capture_output=True)
        cmd = ['audio-offset-finder', '--find-offset-of', start_clip,
               '--within', end_clip]
        res = subprocess.run(cmd, capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if 'Offset:' in line:
                return float(line.split()[1])
    return 0.0

for set_name, files in sets.items():
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        print(f"\n⚠️  Skipping set '{set_name}' – missing files: {missing}")
        continue

    print(f"\n========== Processing set: {set_name} ({len(files)} files) ==========")
    cmd = ['ffmpeg']
    for f in files:
        cmd.extend(['-i', f])

    filter_complex = ""
    last_video = "0:v"
    last_audio = "0:a"
    current_offset = 0.0
    dur_prev = get_duration(files[0])

    for i in range(1, len(files)):
        print(f"  Analyzing overlap: {files[i-1]}  <->  {files[i]}")
        overlap = find_offset(files[i-1], files[i])
        print(f"    Detected overlap: {overlap:.3f} seconds")

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
    print(f"  Encoding → {out_file} (this will take a while)...")
    subprocess.run(cmd)
    print(f"  ✅ Finished: {out_file}")

print("\n=== All sets processed ===")
PYEOF

echo ""
echo "=== Script finished at $(date) ==="
echo "Log saved to: $LOG"
echo "Joined videos are in: $WORK_DIR/joined_videos/"
# (The log is already printed to console in real time; no need to cat again)
