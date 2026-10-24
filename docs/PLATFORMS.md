# Platform specs

One master file serves all four platforms: 1080 × 1920, 30 fps, H.264 + AAC 48 kHz, -14 LUFS, -1 dBTP.
`tools/publish.py` writes one folder per platform with the video, `cover.jpg` and, where useful, `captions.srt`.

| Platform | Format | Length | Cover | Captions file |
|---|---|---|---|---|
| Instagram Reels | 9:16, 1080 × 1920 | up to 3 min (keep 30–60 s) | Upload `cover.jpg` in "Edit cover". The profile grid shows the centre 3:4 (`cover-grid-preview.jpg`). | Not needed (captions are burned in) |
| YouTube Shorts | 9:16 | up to 3 min | Choose a frame in YouTube Studio, or set `cover.jpg` as the thumbnail where offered | `captions.srt` (Subtitles) |
| Facebook Reels | 9:16 | up to 90 s for Reels | Add `cover.jpg` as the thumbnail | `captions.srt` |
| X (Twitter) | 9:16 accepted | up to 2 min 20 s, 512 MB | X shows the first frame; the hook frame is designed for that | `captions.srt` (media editor) |

## Safe areas (1080 × 1920)
- Nothing important in the top 168 px (app status and search bar).
- Words and the product stay between 168 px and 1330 px; below 1330 px the app shows the caption, handle and buttons.
- Keep text away from the right edge in the lower half (like, comment and share buttons).
- Cover: everything that must read sits inside y 240–1680 (the 3:4 grid crop).

Platform limits change. Check each platform's help pages before a big launch.
