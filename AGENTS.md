# Agent Guide

## Project Overview

This repo is a static landing page for the 2026 FLY Worship Camp `RESET`.

The active user-facing page is `index.html`. The project is not currently a Next.js app despite the presence of ignored `.next/` output from earlier local work.

## Current Tech

- Static HTML
- Tailwind CSS loaded via CDN
- Google Fonts loaded from CDN
- Inline CSS and vanilla JavaScript inside `index.html`

There is no `package.json` and no required install step.

## Important Paths

- `index.html`: production-facing page
- `assets/brand/`: current logos and brand marks
- `assets/images/`: current page imagery
- `assets/references/`: visual references, not used by the live page unless explicitly wired in
- `archives/2025/`: last year's poster and legacy duplicated assets
- `archives/concepts/`: old concept HTML files and wireframes

## Working Rules

- Treat `index.html` as the only live page unless the user says otherwise.
- Do not use assets from `archives/` on the live page without an explicit reason.
- Keep filenames used by the live page ASCII and URL-safe.
- Preserve the existing single-file static approach unless the user asks to migrate to a framework.
- Keep visible Korean copy practical for real participants. Avoid placeholder text such as "등록된 내용이 없습니다" or "상세 내용이 입력되는 영역입니다".
- For unknown operational details, use clear pending/leader-announcement language instead of fake final values.

## Verification

For a local preview:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

Before finishing frontend edits, check:

- Hero image and logo load correctly.
- Mobile menu opens and closes.
- Schedule day tabs switch content.
- Announcement and FAQ accordions open correctly.
- No live page references `poster.jpeg`, `작년포스터.jpeg`, or files in `archives/`.

