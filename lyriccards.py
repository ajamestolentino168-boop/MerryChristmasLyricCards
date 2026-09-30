import json
import os
import subprocess
import re

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

WIDTH = config["width"]
HEIGHT = config["height"]
FPS = config["fps"]
AUDIO = config["audio"]
OUTPUT = config["output"]

with open("lyrics.txt", "r", encoding="utf-8") as f:
    lines = []

    for line in f:
        line = line.strip()

        if not line or "|" not in line:
            continue

        timestamp, lyric = line.split("|", 1)

        m = re.match(r"(\d+):(\d+(?:\.\d+)?)", timestamp)

        if not m:
            continue

        minutes = int(m.group(1))
        seconds = float(m.group(2))

        start = minutes * 60 + seconds

        lines.append((start, lyric))

if not lines:
    raise SystemExit("Walang lyrics sa lyrics.txt")

duration_cmd = [
    "ffprobe",
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    AUDIO
]

duration = float(
    subprocess.check_output(duration_cmd).decode().strip()
)

filters = []

for i, (start, lyric) in enumerate(lines):

    if i + 1 < len(lines):
        end = lines[i + 1][0]
    else:
        end = duration

    length = max(0.1, end - start)

    safe = (
        lyric.replace("\\", "\\\\")
             .replace(":", "\\:")
             .replace("'", "\\'")
    )

    x = "(w-text_w)/2"

    if i % 2 == 0:
        y = "h*0.62"
    else:
        y = "h*0.72"

    draw = (
        f"drawtext="
        f"fontcolor=white:"
        f"fontsize=58:"
        f"borderw=4:"
        f"bordercolor=black:"
        f"text='{safe}':"
        f"x={x}:"
        f"y={y}:"
        f"enable='between(t,{start},{end})'"
    )

    filters.append(draw)

vf = ",".join(filters)

cmd = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i",
    f"color=c=black:s={WIDTH}x{HEIGHT}:r={FPS}",
    "-i", AUDIO,
    "-vf", vf,
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "20",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    OUTPUT
]

print("Generating video...")

subprocess.run(cmd, check=True)

print()
print("DONE!")
print(f"Output: {OUTPUT}")
