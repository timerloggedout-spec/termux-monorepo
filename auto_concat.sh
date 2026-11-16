#!/usr/bin/env bash
# ============================================================
#  auto_concat_sets.sh
#  Automatically detect overlap & crossfade four sets of .mp4
#  files. Uses audio-offset-finder + ffmpeg.
# ============================================================

# --- Where your files live ---
cd /data/data/com.termux/files/home/storage/downloads || exit 1

# --- Required tools ---
command -v ffmpeg >/dev/null 2>&1 || { echo "Install ffmpeg first: pkg install ffmpeg"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Install python3 first: pkg install python"; exit 1; }

if ! python3 -c "import audio_offset_finder" 2>/dev/null; then
  echo "Installing audio-offset-finder..."
  pip install audio-offset-finder
fi

# --- The embedded Python script (runs the whole job) ---
PYTHON_SCRIPT=$(cat <<'PYEOF'
import subprocess, sys, tempfile, os, json, re

# ---------- YOUR FOUR SETS (ordered exactly as you want them joined) ----------
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

FADE_DURATION = 0.5      # length of crossfade in seconds
OUTPUT_DIR = "./joined_videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_duration(file):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', file]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return float(res.stdout.strip())

def find_offset(file1, file2):
    """Return seconds of overlap between end of file1 and start of file2."""
    with tempfile.TemporaryDirectory() as tmpdir:
        end_clip = os.path.join(tmpdir, "end.wav")
        start_clip = os.path.join(tmpdir, "start.wav")
        dur1 = get_duration(file1)
        # 20 seconds from the end of file1
        subprocess.run(['ffmpeg', '-y', '-ss', str(max(0, dur1-20)), '-i', file1,
                        '-t', '20', '-vn', end_clip], capture_output=True)
        # 20 seconds from the beginning of file2
        subprocess.run(['ffmpeg', '-y', '-i', file2, '-t', '20', '-vn', start_clip],
                       capture_output=True)
        # find offset
        cmd = ['audio-offset-finder', '--find-offset-of', start_clip,
               '--within', end_clip]
        res = subprocess.run(cmd, capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if 'Offset:' in line:
                return float(line.split()[1])
    return 0.0   # fallback

for set_name, files in sets.items():
    # Check all files exist
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        print(f"Skipping '{set_name}' – missing: {missing}")
        continue

    print(f"\n=== Processing set: {set_name} ({len(files)} files) ===")
    # Build ffmpeg command
    cmd = ['ffmpeg']
    for f in files:
        cmd.extend(['-i', f])

    filter_complex = ""
    last_video = "0:v"
    last_audio = "0:a"
    current_offset = 0.0
    dur_prev = get_duration(files[0])

    for i in range(1, len(files)):
        print(f"  Finding overlap: {files[i-1]}  <->  {files[i]}")
        overlap = find_offset(files[i-1], files[i])
        print(f"    Detected overlap: {overlap:.3f} s")

        # xfade offset = start time of transition in output
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
    print("  Encoding... (this may take a while)")
    subprocess.run(cmd)
    print(f"  Done -> {out_file}")

print("\nAll sets finished. Videos saved in", OUTPUT_DIR)
PYEOF
)

# Run the embedded Python script
python3 -c "$PYTHON_SCRIPT"
