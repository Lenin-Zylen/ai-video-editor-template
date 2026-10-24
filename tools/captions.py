"""Step 3: write projects/<slug>/compositions/captions.html from the cut's word times.

    python tools/captions.py projects/<slug>/edit.json

edit.json "captions":
  groups        list of word lists in transcript order. "*word" = the one accent word,
                "a+b" = one caption word the transcript splits in two,
                "-" = a transcript word that is not shown.
  hook_end      no captions before this time (the hook title carries the words)
  full_windows  [[in, out], ...] full-screen graphics: captions drop low (no split line)
  drop          how far they drop, in px
  position      "split" (short form: pill on the split line, default for 9:16)
                or "bottom" (long form 16:9: 100 px above the bottom edge)
edit.json "brand" (optional) overrides the caption colours and font.
"""
import html
import json
import sys

from common import duration, load_video

BRAND = {"ink": "#0d1117", "line": "#2a313c", "text": "#ffffff", "accent": "#c8f04a",
         "font": "Archivo", "font_file": "assets/fonts/Archivo-var.ttf"}


def snapped_words(work, segs):
    """Whisper word times from the full cut. The first word of each script line is moved
    onto that line's measured speech onset (segment start + pad) when they are close."""
    import csv
    rows = list(csv.reader(open(work / "cut_words.csv", encoding="utf-8")))[1:]
    words = [[int(r[0]) / 1000, int(r[1]) / 1000, r[2].strip()] for r in rows if r[2].strip()]
    onsets, seen = [], set()
    for s in segs:
        if s["line"] not in seen:
            seen.add(s["line"])
            onsets.append(s["cut_start"] + 0.03)
    for o in onsets:
        i = min(range(len(words)), key=lambda k: abs(words[k][0] - o))
        if abs(words[i][0] - o) <= 0.3:
            words[i][0] = o
    (work / "words_snapped.json").write_text(json.dumps(words))
    return words


def main():
    cfg = load_video(sys.argv[1])
    cap = cfg["captions"]
    brand = {**BRAND, **cfg.get("brand", {})}
    work = cfg["_work"]
    segs = json.loads((work / "cut_segments.json").read_text())
    end = round(duration(work / "cut.mp4") - 0.005, 2)
    words = snapped_words(work, segs)

    size = lambda g: sum(w.count("+") + 1 for w in g)
    groups = cap["groups"]
    flat_n = sum(size(g) for g in groups)
    if len(words) != flat_n:
        print("transcript words:", " ".join(w[2] for w in words))
        sys.exit(f"word count mismatch: transcript {len(words)} vs groups {flat_n}")

    i, items = 0, []
    for g in groups:
        ws = words[i:i + size(g)]
        i += size(g)
        start, stop = ws[0][0], ws[-1][1]
        if stop <= cap.get("hook_end", 0):
            continue
        items.append({"start": max(start, cap.get("hook_end", 0)), "end": stop,
                      "words": [w.replace("+", "") for w in g if w != "-"]})
    # Each group holds until the next one opens (no gaps, no overlap); the last holds to the end.
    for a, b in zip(items, items[1:]):
        a["end"] = b["start"]
    items[-1]["end"] = end

    groups_html, js = [], []
    for n, it in enumerate(items):
        spans = [f'<span class="k">{html.escape(w[1:])}</span>' if w.startswith("*") else html.escape(w)
                 for w in it["words"]]
        gid = f"cap-{n}"
        groups_html.append(f'      <div class="cap-row" id="{gid}"><span class="cap-pill">{" ".join(spans)}</span></div>')
        js.append(f'    [{json.dumps("#" + gid)}, {it["start"]:.3f}, {it["end"]:.3f}],')
    drop = cap.get("drop", 250)
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)
    position = cap.get("position", "split" if H > W else "bottom")
    top = H // 2 - 48 if position == "split" else H - 100 - 96
    full = "\n".join(
        f'    tl.to("#cap-wrap", {{ y: {drop}, duration: 0.4, ease: "power3.inOut" }}, {a});\n'
        f'    tl.to("#cap-wrap", {{ y: 0, duration: 0.4, ease: "power3.inOut" }}, {b});'
        for a, b in cap.get("full_windows", []))

    out = TEMPLATE
    for k, v in {"%GROUPS%": "\n".join(groups_html), "%TIMES%": "\n".join(js), "%FULL%": full,
                 "%INK%": brand["ink"], "%LINE%": brand["line"], "%TEXT%": brand["text"],
                 "%ACCENT%": brand["accent"], "%FONT%": brand["font"], "%FONT_FILE%": brand["font_file"],
                 "%W%": str(W), "%H%": str(H), "%TOP%": str(top)}.items():
        out = out.replace(k, v)
    dst = cfg["_project"] / "compositions" / "captions.html"
    dst.write_text(out, encoding="utf-8")

    # Sidecar subtitles for YouTube / Facebook / X: every group, the hook included.
    i, srt = 0, []
    for g in groups:
        ws = words[i:i + size(g)]
        i += size(g)
        text = " ".join(w.replace("+", "").lstrip("*") for w in g if w != "-")
        srt.append([ws[0][0], ws[-1][1], text])
    for a, b in zip(srt, srt[1:]):
        a[1] = b[0]
    srt[-1][1] = end
    ts = lambda t: f"{int(t // 3600):02}:{int(t % 3600 // 60):02}:{int(t % 60):02},{int(round(t % 1 * 1000)) % 1000:03}"
    (work / "captions.srt").write_text(
        "\n".join(f"{n}\n{ts(s)} --> {ts(e)}\n{t}\n" for n, (s, e, t) in enumerate(srt, 1)), encoding="utf-8")
    print(f"{len(items)} caption groups, film end {end}s -> {dst} (+ work/{cfg['slug']}/captions.srt)")


TEMPLATE = """<template>
  <style>
    @font-face { font-family: "%FONT%"; src: url("%FONT_FILE%") format("truetype"); font-weight: 100 900; font-stretch: 62% 125%; }
    #root { position: absolute; inset: 0; pointer-events: none; }
    #cap-wrap { position: absolute; inset: 0; }
    /* Brand: pill on the split line (short form) or near the bottom (long form), 800 weight, 64 px */
    .cap-row { position: absolute; left: 0; top: %TOP%px; width: %W%px; height: 96px; text-align: center; opacity: 0; overflow: visible; }
    .cap-pill { display: inline-block; height: 96px; line-height: 96px; padding: 0 30px; border-radius: 16px; background: %INK%; border: 2px solid %LINE%; font-family: "%FONT%", sans-serif; font-weight: 800; font-stretch: 112%; font-size: 64px; color: %TEXT%; white-space: nowrap; }
    .cap-pill .k { color: %ACCENT%; }
  </style>
  <div id="root" data-composition-id="captions" data-width="%W%" data-height="%H%">
    <div id="cap-wrap">
%GROUPS%
    </div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    const groups = [
%TIMES%
    ];
    groups.forEach(([id, start, end]) => {
      const pill = id + " .cap-pill";
      tl.set(id, { opacity: 1, visibility: "visible" }, start);
      tl.fromTo(pill, { scale: 0.9 }, { scale: 1, duration: 0.12, ease: "power3.out" }, start);
      tl.set(id, { opacity: 0, visibility: "hidden" }, end);
    });
    // Full-screen graphics windows: there is no split line, so captions sit low in the safe band.
    tl.set("#cap-wrap", { y: 0 }, 0);
%FULL%
    window.__timelines["captions"] = tl;
  </script>
</template>
"""

if __name__ == "__main__":
    main()
