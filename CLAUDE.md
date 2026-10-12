# Vibescape website

Static site for vibescapemedia.com, deployed by Netlify by manual zip upload (Netlify Drop). Build the zip with `tools/make_zip.py`.

- `site/` is the published site. `site/index.html` is the source of all pages (single page app, one hidden `<div class="page">` per route).
- `tools/build.py` regenerates per-page HTML files, sitemap, robots and netlify.toml. Run it after any content change.
- `tools/content.py` holds service and landing page copy. Journal articles are markdown files in `content/articles/`.
- `tools/audit.py` prints an on-page SEO report.
- Scheduled SEO runs follow `AUTOPILOT.md`.

Copy rules: no dashes as punctuation, no invented numbers or results, Roman Urdu only as seasoning.
