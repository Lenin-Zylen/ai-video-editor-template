"""Step 1: transcribe every raw clip so you can pick takes.

    python tools/transcribe_clips.py projects/<slug>/edit.json

Writes work/<slug>/clips/<clip>.csv (word times) and prints, per clip, each phrase
with its start time, so you can fill the "takes" list in edit.json.
"""
import re
import subprocess
import sys

from common import ffmpeg, load_video, wav16k, whisper_words


def islands(wav, noise_db, min_gap):
    out = subprocess.run([ffmpeg(), "-i", str(wav), "-af", f"silencedetect=noise={noise_db}dB:d={min_gap}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    return re.findall(r"silence_(start|end): ([0-9.]+)", out)


def main():
    cfg = load_video(sys.argv[1])
    clips_dir = cfg["_work"] / "clips"
    clips = sorted(p for p in cfg["_raw"].iterdir() if p.suffix.lower() in (".mp4", ".mov", ".m4v"))
    for clip in clips:
        wav = wav16k(clip, clips_dir / f"{clip.stem}.wav")
        words = whisper_words(wav, clips_dir / clip.stem, cfg.get("whisper_prompt"))
        print(f"\n## {clip.stem}")
        line, start = [], None
        for s, e, w in words:
            if start is None:
                start = s
            line.append(w)
            if w.endswith((".", "?", "!")):
                print(f"  {start:7.2f}s  {' '.join(line)}")
                line, start = [], None
        if line:
            print(f"  {start:7.2f}s  {' '.join(line)}")


if __name__ == "__main__":
    main()
