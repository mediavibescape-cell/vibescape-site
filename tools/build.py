"""Rebuild the site after any content change.
  python3 tools/build.py
0. theme.py   : applies content/theme.json (colours, fonts) to app.css and index.html
1. inject.py  : writes service pages, landing pages and articles into site/index.html
2. seo.py     : writes one HTML file per page, sitemap.xml, robots.txt, site/netlify.toml
3. cache-busts css/js by content hash, and writes the root netlify.toml used by git deploys
"""
import os, re, subprocess, hashlib, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
T = os.path.join(ROOT, 'tools')
subprocess.run([sys.executable, os.path.join(T, 'theme.py')], check=True)
for step in ('inject.py', 'seo.py'):
    subprocess.run([sys.executable, os.path.join(T, step), SITE], check=True)
h = hashlib.sha1()
for f in ('assets/css/app.css', 'assets/css/desk.css', 'assets/js/app.js'):
    h.update(open(os.path.join(SITE, f), 'rb').read())
ver = h.hexdigest()[:8]
for f in glob.glob(os.path.join(SITE, '*.html')):
    s = open(f).read()
    s2 = re.sub(r'\?v=[0-9a-z]+', '?v=' + ver, s)
    if s2 != s: open(f, 'w').write(s2)
toml = open(os.path.join(SITE, 'netlify.toml')).read()
open(os.path.join(ROOT, 'netlify.toml'), 'w').write('[build]\n  publish = "site"\n  command = "python3 tools/build.py"\n\n' + toml)
print('build ok, asset version', ver)
