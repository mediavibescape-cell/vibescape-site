"""SEO content: service pages, the Dubai page and international landing pages.
The copy lives in JSON files under content/pages/ (editable in the CMS at /admin).
This module loads them into the shapes inject.py and seo.py expect.
Style rules: no dashes in copy, Roman Urdu as seasoning only, no invented numbers.
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, 'content', 'pages')

# Page order (and therefore URLs) is structural, so it stays in code.
SERVICE_ORDER = ['branding', 'video-production', 'performance-marketing', 'web-development', 'web-apps']
LANDING_ORDER = ['global', 'for-agencies', 'for-ecommerce-brands']

def _load(path, slug):
    d = json.load(open(path, encoding='utf-8'))
    out = {'slug': slug}
    for k, v in d.items():
        if k == 'steps':
            v = [(x['title'], x['text']) for x in v]
        elif k == 'points' and v and 'url' not in v[0]:
            v = [(x['title'], x['text']) for x in v]
        elif k in ('points', 'links'):
            v = [(x['title'], x['text'], x['url']) for x in v]
        elif k == 'work':
            v = [(x['type'], x['name'], x['note']) for x in v]
        elif k == 'faq':
            v = [(x['q'], x['a']) for x in v]
        out[k] = v
    return out

SERVICES = [_load(os.path.join(PAGES, 'services', s + '.json'), s) for s in SERVICE_ORDER]
DUBAI = _load(os.path.join(PAGES, 'dubai.json'), 'dubai')
LANDINGS = []
for s in LANDING_ORDER:
    L = _load(os.path.join(PAGES, 'landings', s + '.json'), s)
    L['path'] = '/' + s
    LANDINGS.append(L)

# Journal articles live in content/articles/*.md (one file each)
from articles import load_articles
ARTICLES = load_articles()
