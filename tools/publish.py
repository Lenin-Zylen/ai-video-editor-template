"""Step 4: render, master and export one video for every platform.

    python tools/publish.py projects/<slug>/edit.json            # render + cover + exports
    python tools/publish.py projects/<slug>/edit.json --no-render  # reuse work/<slug>/final_raw.mp4

1. Renders the HyperFrames project (npx hyperframes render) to work/<slug>/final_raw.mp4.
2. Renders the cover (projects/<slug>/cover/index.html) to cover.png.
3. Masters the audio to the target loudness (two-pass loudnorm, -1 dBTP), video copied.
4. Writes exports/<slug>/<platform>/ with the video (cover embedded as cover art),
   the cover image, and captions.srt where the platform takes subtitles.
"""
import json
import re
import shutil
import subprocess
import sys

from common import ROOT, ffmpeg, load_video, run

PLATFORMS = {
    # name: (subtitle file?, note written to README)
    "instagram": (False, "Reel. Upload the MP4, then 'Edit cover' > 'Add from camera roll' > cover.jpg. "
                         "Grid shows the centre 3:4 (cover-grid-preview.jpg)."),
    "youtube": (True, "Short (vertical, under 3 min). Upload the MP4; add captions.srt under Subtitles. "
                      "Pick the cover frame in YouTube Studio or set cover.jpg as the thumbnail if available."),
    "facebook": (True, "Reel. Upload the MP4; add cover.jpg as the thumbnail and captions.srt as captions (English)."),
    "x": (True, "Vertical video (under 2:20, under 512 MB). Upload the MP4; attach captions.srt in the media editor."),
    "youtube-long": (True, "Long-form video (16:9). Upload the MP4, set thumbnail.jpg (1280 x 720) as the thumbnail, "
                           "add captions.srt, and paste the chapters from the description draft if any."),
}


def npx():
    return shutil.which("npx.cmd") or shutil.which("npx") or "npx"


def master(src, dst, lufs):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(src), "-af",
                          f"loudnorm=I={lufs}:TP=-1:LRA=7:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", out, re.S).group(0))
    af = (f"loudnorm=I={lufs}:TP=-1:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          "aresample=48000")
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-c:v", "copy", "-af", af,
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dst)])


def loudness(path):
    out = subprocess.run([ffmpeg(), "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[0-9.]+) LUFS", out)
    p = re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", out)
    return (i[-1] if i else "?"), (p[-1] if p else "?")


def main():
    cfg = load_video(sys.argv[1])
    pub = cfg.get("publish", {})
    project, work, slug = cfg["_project"], cfg["_work"], cfg["slug"]
    raw = work / "final_raw.mp4"

    if "--no-render" not in sys.argv:
        run([npx(), "hyperframes", "render", "-o", str(raw)], cwd=project)
    cover_dir = project / "cover"
    cover_png = project / pub.get("cover", "cover/cover.png")
    if (cover_dir / "index.html").exists() and "--no-render" not in sys.argv:
        run([npx(), "hyperframes", "snapshot", "--at", "0", "--no-end", "--describe", "false", "-o", "shot"], cwd=cover_dir)
        shutil.copy(cover_dir / "shot" / "frame-00-at-0s.png", cover_png)

    mastered = work / f"{slug}_master.mp4"
    master(raw, mastered, pub.get("loudness_lufs", -14))
    cover_jpg = work / "cover.jpg"
    run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(cover_png), "-q:v", "2", str(cover_jpg)])
    grid = work / "cover-grid-preview.jpg"
    if cfg.get("height", 1920) > cfg.get("width", 1080):   # 3:4 profile-grid crop of a vertical cover
        run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(cover_png), "-vf", "crop=iw:iw*4/3:0:(ih-iw*4/3)/2",
             "-q:v", "2", str(grid)])
    else:
        shutil.copy(cover_jpg, grid)

    out_root = ROOT / "exports" / slug
    srt = work / "captions.srt"
    for name in pub.get("platforms", list(PLATFORMS)):
        wants_srt, note = PLATFORMS[name]
        d = out_root / name
        d.mkdir(parents=True, exist_ok=True)
        video = d / f"{slug}_{name}.mp4"
        # embed the cover as cover art (players that read it show it before play)
        run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(mastered), "-i", str(cover_jpg),
             "-map", "0", "-map", "1", "-c", "copy", "-disposition:v:1", "attached_pic",
             "-movflags", "+faststart", str(video)])
        shutil.copy(cover_jpg, d / "cover.jpg")
        if name == "instagram":
            shutil.copy(grid, d / "cover-grid-preview.jpg")
        if name == "youtube-long":
            # 1280 x 720 thumbnail from the cover (design the cover 16:9 for long-form videos)
            run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(cover_png), "-vf",
                 "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720", "-q:v", "2", str(d / "thumbnail.jpg")])
        if wants_srt and srt.exists():
            shutil.copy(srt, d / "captions.srt")
        (d / "README.txt").write_text(f"{cfg.get('title', slug)}\n\n{note}\n", encoding="utf-8")
    i, p = loudness(mastered)
    print(f"exports -> {out_root}  ({', '.join(pub.get('platforms', list(PLATFORMS)))}); loudness {i} LUFS, peak {p} dBFS")


if __name__ == "__main__":
    main()
