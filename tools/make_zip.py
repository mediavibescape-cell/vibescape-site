"""Build a Netlify drag-and-drop zip of site/ with the lite films (stays under ~30MB).
Usage: python3 tools/make_zip.py [out_dir]   -> <out_dir>/vibescape-netlify-YYYY-MM-DD.zip
Files sit at the zip root (index.html at top level), which is what Netlify Drop needs.
"""
import os, sys, zipfile, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(REPO, 'site')
LITE = os.path.join(REPO, 'tools', 'lite')
out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, 'dist')
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f'vibescape-netlify-{datetime.date.today().isoformat()}.zip')

SKIP = {'assets/videos/hero-reel.mp4'}
HERO_FULL = 'data-hsrc="/assets/videos/hero-reel.mp4"'
HERO_LITE = 'data-hsrc="/assets/pv/hero-m.mp4"'

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(SITE):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, SITE).replace(os.sep, '/')
            if rel in SKIP:
                continue
            lite = os.path.join(LITE, rel.replace('assets/', '', 1))
            if rel.endswith('.mp4') and os.path.exists(lite):
                z.write(lite, rel, compress_type=zipfile.ZIP_STORED)
            elif rel.endswith('.html'):
                z.writestr(rel, open(full, encoding='utf-8').read().replace(HERO_FULL, HERO_LITE))
            elif rel.endswith(('.mp4', '.jpg', '.png', '.webp', '.woff2')):
                z.write(full, rel, compress_type=zipfile.ZIP_STORED)
            else:
                z.write(full, rel)

print(out, round(os.path.getsize(out) / 1e6, 1), 'MB')
