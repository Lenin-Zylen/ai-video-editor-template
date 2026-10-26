# Git: what to commit and what to keep local

Rule: do not commit a video file or an audio file. Commit instructions, code, analysis and small assets only.

## Commit (in git)

- `brand/`, `tools/`, `docs/`, `.claude/commands/`: code, rules and brand assets.
- `projects/<slug>/`: code and small assets. Examples: `edit.json`, `index.html`, `compositions/*.html`, `hyperframes.json`, `package.json`, fonts, logos, screenshots, the cover image.
- `references/<id>/<id>.info.json`: the metadata for each reference video (title, channel, counts).
- `references/_analysis/<id>/`: `cuts.txt`, `transcript.srt`, `words.srt`, `sheet.jpg`, `frames/*.jpg`.
- `examples/`: the example reel. Its sound effects are the one exception to the rule. They are small, licensed (see `CREDITS.md`), and the example does not play without them.
- `CLAUDE.md`, `.gitignore`.

## Keep local (see `.gitignore`)

- Video and audio: every `.mp4`, `.mp3` and `.wav` under `projects/*/assets/` (also in subfolders such as `sfx/`, `meme/` and `music/`), and under `references/`.
- Local folders: `raw-footages/`, `work/`, `exports/`, `renders/`.
- Generated files: `projects/*/assets/transcript.json`, `projects/*/cover/shot/`, `projects/*/boards/stills/redo/`, `*.log`.
- Caches: `.hyperframes/`, `.media/`, `.thumbnails/`, `.waveform-cache/`, `node_modules/`, `__pycache__/`, `*.pyc`.
- Per computer: `editor.config.json`, `.setup-done`.
- OS files: `.DS_Store`, `Thumbs.db`, `desktop.ini`.

## Notes from use

- Use `**` patterns for media, not one pattern per file. A rule such as `projects/*/assets/cut.mp4` misses `raw.mp4`, `edited.mp4` and the files in `sfx/` and `meme/`.
- Do not ignore a whole folder when part of it must go into git. Git cannot add back a file under an ignored folder. Ignore the media types in it instead, as `.gitignore` does for `references/`.
- A `.gitignore` rule does not remove a file that git already tracks. To stop tracking a file and keep it on disk, run `git rm --cached <file>` and commit.
- After `git rm --cached`, the next `git pull` on another computer deletes that file there. Copy the file back to that computer by hand.
- Before each commit, check for media that git can still see:

  ```bash
  git status --porcelain --untracked-files=all | grep -Ei '\.(mp4|mov|wav|mp3|m4a)$'
  git ls-files | grep -Ei '\.(mp4|mov|wav|mp3|m4a)$'
  ```

  The first command must print nothing. The second command must print only the files in `examples/`.
- Before each commit, check new files for API keys and tokens. Project folders that call an API (for example a Higgsfield demo) can hold one.
