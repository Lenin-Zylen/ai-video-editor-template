"""Step 2: build the cut from the chosen takes, removing every pause longer than max_pause.

    python tools/cut.py projects/<slug>/edit.json

Reads "takes" (line, clip, start, end) from edit.json. Writes work/<slug>/cut.mp4,
cut_segments.json (where each piece lands in the cut) and cut_words.csv (word times),
copies the cut to projects/<slug>/assets/cut.mp4, and reports any pause still over the limit.
"""
import json
import re
import subprocess
import sys

from common import duration, ffmpeg, load_video, run, wav16k, whisper_words


def speech_islands(wav, a, b, noise_db, max_pause, pad, fps):
    out = subprocess.run(
        [ffmpeg(), "-ss", str(a), "-to", str(b), "-i", str(wav),
         "-af", f"silencedetect=noise={noise_db}dB:d={max_pause}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    events = re.findall(r"silence_(start|end): ([0-9.]+)", out)
    islands, s, in_silence = [], 0.0, False
    for kind, t in events:
        t = float(t)
        if kind == "start":
            if t - s > 0.03:
                islands.append([s, t])
            in_silence = True
        else:
            s, in_silence = t, False
    if not in_silence and (b - a) - s > 0.03:
        islands.append([s, b - a])
    # pad, clamp, and merge islands; a cut leaves 2*pad of air, so merge only
    # when the kept silence (gap plus both pads) stays <= max_pause
    merged = []
    for s, e in islands:
        s, e = max(0.0, s - pad) + a, min(b - a, e + pad) + a
        # snap to the frame grid so video and audio pieces have the same length
        # (otherwise concat pads audio per piece and the cut times drift)
        s, e = round(s * fps) / fps, round(e * fps) / fps
        if merged and s - merged[-1][1] <= max_pause - 2 * pad:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged


def main():
    cfg = load_video(sys.argv[1])
    fps, w, h = cfg.get("fps", 30), cfg.get("width", 1080), cfg.get("height", 1920)
    noise_db, max_pause, pad = cfg.get("noise_db", -35), cfg.get("max_pause", 0.1), cfg.get("pad", 0.03)
    work = cfg["_work"]

    inputs, segs = [], []
    for t in cfg["takes"]:
        clip = cfg["_raw"] / f"{t['clip']}.mp4"
        if t["clip"] not in inputs:
            inputs.append(t["clip"])
        wav = wav16k(clip, work / "clips" / f"{t['clip']}.wav")
        for s, e in speech_islands(wav, t["start"], t["end"], noise_db, max_pause, pad, fps):
            segs.append({"line": t["line"], "clip": t["clip"], "in": s, "out": e})

    parts, labels = [], []
    for i, sg in enumerate(segs):
        k = inputs.index(sg["clip"])
        d = sg["out"] - sg["in"]
        parts.append(f"[{k}:v]trim={sg['in']}:{sg['out']},setpts=PTS-STARTPTS,"
                     f"scale={w}:{h},setsar=1,fps={fps}[v{i}]")
        parts.append(f"[{k}:a]atrim={sg['in']}:{sg['out']},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - 0.008):.3f}:d=0.008[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    parts.append("".join(labels) + f"concat=n={len(segs)}:v=1:a=1[v][a]")
    (work / "cut.filter").write_text(";\n".join(parts))

    cut = work / "cut.mp4"
    cmd = [ffmpeg(), "-y", "-loglevel", "error"]
    for c in inputs:
        cmd += ["-i", str(cfg["_raw"] / f"{c}.mp4")]
    cmd += ["-filter_complex_script", str(work / "cut.filter"), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-g", str(fps), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(cut)]
    run(cmd)

    t = 0.0
    for sg in segs:
        sg["cut_start"] = round(t, 4)
        t += sg["out"] - sg["in"]
        sg["cut_end"] = round(t, 4)
    (work / "cut_segments.json").write_text(json.dumps(segs, indent=1))

    assets = cfg["_project"] / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "cut.mp4").write_bytes(cut.read_bytes())

    cut_wav = work / "cut16k.wav"
    if cut_wav.exists():
        cut_wav.unlink()
    wav16k(cut, cut_wav)
    whisper_words(cut_wav, work / "cut_words", cfg.get("whisper_prompt"))

    out = subprocess.run([ffmpeg(), "-i", str(cut), "-af", f"silencedetect=noise={noise_db}dB:d={max_pause}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    left = re.findall(r"silence_duration: ([0-9.]+)", out)
    raw = sum(t["end"] - t["start"] for t in cfg["takes"])
    print(f"{len(segs)} segments, takes {raw:.2f}s -> cut {duration(cut):.2f}s")
    first = {}
    for sg in segs:
        first.setdefault(sg["line"], sg["cut_start"])
    print("line starts: " + ", ".join(f"{k} {v:.3f}" for k, v in first.items()))
    print(f"pauses over {max_pause}s left: {len(left)}" + (f" {left}" if left else ""))


if __name__ == "__main__":
    main()
