# Vibescape website

Static site for vibescapemedia.com, deployed by Netlify by manual zip upload (Netlify Drop). Build the zip with `tools/make_zip.py`.

- `site/` is the published site. `site/index.html` is the source of all pages (single page app, one hidden `<div class="page">` per route).
- `tools/build.py` regenerates per-page HTML files, sitemap, robots and netlify.toml. Run it after any content change.
- Content lives in `content/`: journal articles are markdown in `content/articles/`, service, landing and Dubai page copy is JSON in `content/pages/` (loaded by `tools/content.py`), colours and fonts are in `content/theme.json` (applied by `tools/theme.py`).
- `site/admin/` is the visual editor (Sveltia CMS, config in `site/admin/config.yml`). It commits to `main` with messages starting `CMS:`. Keep its fields in sync with the content files if you change their shape.
- Home, work, studio, careers and desk copy is still hardcoded in `site/index.html`.
- `tools/audit.py` prints an on-page SEO report.
- Scheduled SEO runs follow `AUTOPILOT.md`.

Copy rules: no dashes as punctuation, no invented numbers or results, Roman Urdu only as seasoning.
