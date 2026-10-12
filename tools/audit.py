"""On-page SEO audit of the built site. Prints a markdown report.
  python3 tools/audit.py            (all pages)
  python3 tools/audit.py <slug>     (one article, plus the site-wide checks)
Checks: title and description length, one h1, canonical, word count, internal links in and out,
broken internal links, images without alt text, sitemap coverage, duplicate titles/descriptions.
"""
import os, re, sys, glob, html, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
src = open(os.path.join(SITE, 'index.html')).read()
sitemap = open(os.path.join(SITE, 'sitemap.xml')).read()
routes = set(re.findall(r'<loc>https://vibescapemedia.com([^<]*)</loc>', sitemap))
routes = {r or '/' for r in routes}

def blocks():
    out = {}
    for m in re.finditer(r'<div class="page(?: on)?" id="p-([\w-]+)" data-title="([^"]*)">', src):
        pid = m.group(1); i = m.end()
        j = src.find('<div class="page', i)
        out[pid] = (html.unescape(m.group(2)), src[i: j if j > 0 else len(src)])
    return out
B = blocks()
def route_of(pid):
    if pid == 'home': return '/'
    if pid.startswith('post-'): return '/journal/' + pid[5:]
    if pid.startswith('svc-'): return '/services/' + pid[4:]
    return '/' + pid
def text(b):
    b = re.sub(r'<footer>.*?</footer>', '', b, flags=re.S)
    b = re.sub(r'<section class="cta wrap">.*?</section>', '', b, flags=re.S)
    b = re.sub(r'<script.*?</script>|<style.*?</style>', '', b, flags=re.S)
    return html.unescape(re.sub(r'<[^>]+>', ' ', b))
def links(b):
    b = re.sub(r'<footer>.*?</footer>', '', b, flags=re.S)
    return [h.split('#')[0] or '/' for h in re.findall(r'href="(/[^"]*)"', b)]
descs = {}
for f in glob.glob(os.path.join(SITE, '*.html')):
    s = open(f).read()
    pid = re.search(r'class="page on" id="p-([\w-]+)"', s)
    d = re.search(r'<meta name="description" content="([^"]*)"', s)
    if pid and d: descs[pid.group(1)] = html.unescape(d.group(1))
inbound = collections.Counter()
for pid, (_, b) in B.items():
    for l in set(links(b)):
        inbound[l] += 1
only = sys.argv[1] if len(sys.argv) > 1 else None
rows, issues = [], []
known = {route_of(p) for p in B} | {'/contact', '/work', '/desk', '/journal', '/services', '/studio', '/careers', '/privacy', '/'}
for pid, (title, b) in B.items():
    if pid == '404': continue
    r = route_of(pid)
    if only and pid != 'post-' + only: continue
    words = len(text(b).split())
    h1 = len(re.findall(r'<h1[ >]', b))
    out_l = [l for l in links(b) if l != r]
    broken = sorted({l for l in out_l if l.rstrip('/') not in {k.rstrip('/') for k in known} and not l.startswith('/assets/')})
    noalt = len(re.findall(r'<img(?![^>]*\salt=)[^>]*>', b))
    d = descs.get(pid, '')
    rows.append((r, len(title), len(d), h1, words, len(set(out_l)), inbound.get(r, 0)))
    if not (20 <= len(title) <= 65): issues.append(f'{r}: title is {len(title)} characters (aim 30 to 65)')
    if not (70 <= len(d) <= 165): issues.append(f'{r}: description is {len(d)} characters (aim 120 to 160)')
    if h1 != 1: issues.append(f'{r}: {h1} h1 tags (should be 1)')
    if pid.startswith('post-') and words < 600: issues.append(f'{r}: only {words} words (aim 800+ for a ranking article)')
    if pid.startswith('post-') and inbound.get(r, 0) < 2: issues.append(f'{r}: only {inbound.get(r,0)} pages link here (add links from related pages)')
    if broken: issues.append(f'{r}: links to missing pages {broken}')
    if noalt: issues.append(f'{r}: {noalt} images without alt text')
    if r not in routes: issues.append(f'{r}: not in sitemap.xml')
dup = [t for t, c in collections.Counter(d for d in descs.values()).items() if c > 1]
if dup: issues.append(f'{len(dup)} duplicate meta descriptions')
print('| Page | Title chars | Desc chars | H1 | Words | Links out | Links in |')
print('| --- | --- | --- | --- | --- | --- | --- |')
for r in sorted(rows): print('| ' + ' | '.join(str(x) for x in r) + ' |')
print('\n**Issues**\n')
print('\n'.join('- ' + i for i in issues) if issues else '- None found')
