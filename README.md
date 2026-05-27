# FLY Worship Camp

2026 FLY Worship Camp `RESET` 안내용 정적 웹페이지입니다.

## Project Structure

```text
.
├── index.html
├── assets/
│   ├── brand/
│   │   ├── logo.jpeg
│   │   ├── camp-logo.png
│   │   └── camp-logo-square.png
│   ├── images/
│   │   ├── hero-background.png
│   │   └── goods-preview.png
│   └── references/
│       ├── desktop-preview.png
│       └── mobile-preview.png
└── archives/
    ├── 2025/
    │   ├── poster.jpeg
    │   ├── poster-original.jpeg
    │   └── youth-logo.jpeg
    └── concepts/
```

## Active Page

- `index.html` is the production-facing page.
- The page uses Tailwind via CDN and Google Fonts.
- There is no package manager setup required for the current static version.

## Local Preview

Open `index.html` directly in a browser, or run:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Archive Policy

- `archives/2025/` stores last year's poster and duplicated legacy source images.
- `archives/concepts/` stores old design concepts and wireframes.
- Do not reference archive assets from `index.html` unless intentionally restoring a past design.

## Deployment Notes

The current site can be served as static files. If deploying to Vercel, the important files are:

- `index.html`
- `assets/**`

