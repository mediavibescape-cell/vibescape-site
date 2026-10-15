"""Insert SEO service pages, the Dubai page and new articles into index.html (idempotent).
Usage: python3 inject.py /path/to/site
"""
import sys, os, re, html
sys.path.insert(0, os.path.dirname(__file__))
from content import SERVICES, DUBAI, ARTICLES, LANDINGS
ROOT = sys.argv[1]
p = os.path.join(ROOT, 'index.html')
s = open(p).read()
e = lambda x: html.escape(x, quote=False)
WA = "https://wa.me/923390116056"

# strip previous injection
s = re.sub(r'<!--SEO-START-->.*?<!--SEO-END-->', '', s, flags=re.S)
s = re.sub(r'<!--SEOPOST-->.*?<!--/SEOPOST-->', '', s, flags=re.S)
s = re.sub(r'<!--SVCLINK-->.*?<!--/SVCLINK-->', '', s, flags=re.S)
s = re.sub(r'<!--KEEPREAD-->.*?<!--/KEEPREAD-->', '', s, flags=re.S)

# reuse the page tail (CTA + footer) from an existing article page
i = s.find('<div class="page" id="p-post-logo-badalna-rebrand-nahi"')
j = s.find('<div class="page"', i + 10)
blk = s[i:j]
tail = blk[blk.find('</article>') + len('</article>'):blk.rfind('</div>')]

def faq_html(items):
    return ('<section class="wrap sp-faq"><h2 class="h-m" data-split>Questions.</h2><div class="faqs">' +
            ''.join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in items) +
            '</div></section>')

def work_rows(items):
    out = []
    for kind, name, note in items:
        if kind in ('nord', 'enchante', 'neobiotics', 'rahat', 'padel', 'franke'):
            key = 'neobiotics' if kind == 'neobiotics' else kind
            out.append(f'<a href="/work#branding" data-project="{key}"><h3>{e(name)}</h3><span class="d">{e(note)}</span><span class="u"><span>Open deck</span><i>&rsaquo;</i></span></a>')
        elif kind == 'film':
            out.append(f'<a href="/work#films" data-link><h3>{e(name)}</h3><span class="d">{e(note)}</span><span class="u"><span>Watch films</span><i>&rsaquo;</i></span></a>')
        elif kind == 'web':
            out.append(f'<a href="/work#web" data-link><h3>{e(name)}</h3><span class="d">{e(note)}</span><span class="u"><span>See sites</span><i>&rsaquo;</i></span></a>')
        elif kind == 'desk':
            out.append(f'<a href="/desk" data-link><h3>{e(name)}</h3><span class="d">{e(note)}</span><span class="u"><span>See the Desk</span><i>&rsaquo;</i></span></a>')
        else:
            out.append(f'<a href="https://padelelitedesk.netlify.app" target="_blank" rel="noopener"><h3>{e(name)}</h3><span class="d">{e(note)}</span><span class="u"><span>Visit</span><i>&nearr;</i></span></a>')
    return '<div class="wl">' + ''.join(out) + '</div>'

READ = {a['slug']: a['title'] for a in ARTICLES}
READ.update({'logo-badalna-rebrand-nahi': 'Logo badalna rebrand nahi hota',
             'dont-look-pakistani-be-pakistani': "Don't look Pakistani. Be Pakistani.",
             'premium-bola-tha-beige-nahi': 'Premium bola tha. Beige nahi.'})
RELATED = {
    'branding': ['logo-badalna-rebrand-nahi', 'premium-bola-tha-beige-nahi', 'dont-look-pakistani-be-pakistani'],
    'video-production': ['product-video-production-cost', 'how-to-brief-a-product-video', 'furniture-brand-video-shoot'],
    'performance-marketing': ['boost-post-vs-meta-ads', 'how-to-brief-a-product-video'],
    'web-development': ['shopify-vs-custom-website', 'offshore-creative-team-vs-in-house', 'dont-look-pakistani-be-pakistani'],
    'web-apps': ['shopify-vs-custom-website', 'offshore-creative-team-vs-in-house'],
    'dubai': ['dont-look-pakistani-be-pakistani', 'offshore-creative-team-vs-in-house'],
    'global': ['offshore-creative-team-vs-in-house', 'white-label-video-editing-for-agencies', 'product-video-production-cost', 'dont-look-pakistani-be-pakistani'],
    'for-agencies': ['white-label-video-editing-for-agencies', 'offshore-creative-team-vs-in-house', 'how-to-brief-a-product-video'],
    'for-ecommerce-brands': ['shopify-vs-custom-website', 'product-video-production-cost', 'how-to-brief-a-product-video', 'furniture-brand-video-shoot', 'boost-post-vs-meta-ads'],
}
NEXT = {
    'shopify-vs-custom-website': ['product-video-production-cost', 'boost-post-vs-meta-ads'],
    'boost-post-vs-meta-ads': ['shopify-vs-custom-website', 'product-video-production-cost'],
    'product-video-production-cost': ['how-to-brief-a-product-video', 'shopify-vs-custom-website'],
    'white-label-video-editing-for-agencies': ['offshore-creative-team-vs-in-house', 'how-to-brief-a-product-video'],
    'furniture-brand-video-shoot': ['how-to-brief-a-product-video', 'boost-post-vs-meta-ads'],
    'how-to-brief-a-product-video': ['product-video-production-cost', 'furniture-brand-video-shoot'],
    'offshore-creative-team-vs-in-house': ['white-label-video-editing-for-agencies', 'how-to-brief-a-product-video'],
    'logo-badalna-rebrand-nahi': ['premium-bola-tha-beige-nahi', 'dont-look-pakistani-be-pakistani'],
    'dont-look-pakistani-be-pakistani': ['logo-badalna-rebrand-nahi', 'premium-bola-tha-beige-nahi'],
    'premium-bola-tha-beige-nahi': ['logo-badalna-rebrand-nahi', 'dont-look-pakistani-be-pakistani'],
}
def related(key):
    sl = [x for x in RELATED.get(key, []) if x in READ]
    if not sl: return ''
    return ('<section class="wrap sp-more"><span class="small">From the journal</span><div class="sp-chips">' +
            ''.join(f'<a href="/journal/{x}" data-link>{e(READ[x])}</a>' for x in sl) + '</div></section>')
def keep(slug):
    sl = [x for x in NEXT.get(slug, []) if x in READ]
    if not sl: return ''
    return ('<!--KEEPREAD--><div class="keep"><span class="small">Keep reading</span>' +
            ''.join(f'<a href="/journal/{x}" data-link class="tlink">{e(READ[x])}</a>' for x in sl) + '</div><!--/KEEPREAD-->')

pages = []
for sv in SERVICES:
    others = ''.join(f'<a href="/services/{o["slug"]}" data-link>{e(o["nav"])}</a>' for o in SERVICES if o is not sv)
    steps = ''.join(f'<div class="pst"><span class="pn">Step {k+1}</span><h4>{e(a)}</h4><p>{e(b)}</p></div>' for k, (a, b) in enumerate(sv['steps']))
    pages.append(
        f'<div class="page" id="p-svc-{sv["slug"]}" data-title="{html.escape(sv["title"], quote=True)}">'
        f'<section class="phero wrap"><a href="/services" data-link class="sp-crumb">Services</a><h1 class="h-l" data-split>{e(sv["h1"])}</h1>'
        f'<p class="lead" data-fade>{e(sv["lead"])}</p>'
        f'<div class="cta-r" data-fade style="margin-top:30px"><a href="/contact" data-link class="btn" data-magnet>Start a project <span class="ar">&rsaquo;</span></a><a href="{WA}" target="_blank" rel="noopener" class="btn ghost">WhatsApp karein</a></div></section>'
        f'<section class="wrap sp-get"><h2 class="h-m" data-split>What you get.</h2><ul class="how" data-fade>' +
        ''.join(f'<li>{e(g)}</li>' for g in sv['get']) + '</ul></section>'
        f'<section class="proc wrap"><h2 class="h-m" data-split>How it works.</h2><div class="pline"><span class="fill"></span>{steps}</div></section>'
        f'<section class="wrap sp-work"><h2 class="h-m" data-split style="margin-bottom:clamp(28px,3vw,44px)">Work.</h2>{work_rows(sv["work"])}</section>' +
        faq_html(sv['faq']) + related(sv['slug']) +
        f'<section class="wrap sp-more"><span class="small">Other services</span><div class="sp-chips">{others}<a href="/dubai" data-link>Dubai</a></div></section>' +
        tail + '</div>')

d = DUBAI
pts = ''.join(f'<a href="{u}" data-link><h3>{e(a)}</h3><span class="d">{e(b)}</span><span class="u"><span>More</span><i>&rsaquo;</i></span></a>' for a, b, u in d['points'])
pages.append(
    f'<div class="page" id="p-dubai" data-title="{html.escape(d["title"], quote=True)}">'
    f'<section class="phero wrap"><h1 class="h-l" data-split>{e(d["h1"])}</h1><p class="lead" data-fade>{e(d["lead"])}</p>'
    f'<div class="cta-r" data-fade style="margin-top:30px"><a href="/contact" data-link class="btn" data-magnet>Start a project <span class="ar">&rsaquo;</span></a><a href="{WA}" target="_blank" rel="noopener" class="btn ghost">WhatsApp karein</a></div></section>'
    f'<section class="wrap sp-work"><h2 class="h-m" data-split style="margin-bottom:clamp(28px,3vw,44px)">What we do in the UAE.</h2><div class="wl">{pts}</div></section>'
    f'<section class="wrap sp-get"><h2 class="h-m" data-split>Visit us.</h2><p class="lead" data-fade>Business Bay, Aswar Building, M Floor, Dubai. Production studio in C Block, Model Town, Lahore.</p></section>' +
    faq_html(d['faq']) + related('dubai') + tail + '</div>')

for L in LANDINGS:
    pts = ''.join(f'<div class="lp-pt" data-fade style="--d:{k*0.06:.2f}s"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for k, (a, b) in enumerate(L['points']))
    lks = ''.join(f'<a href="{u}" data-link><h3>{e(a)}</h3><span class="d">{e(b)}</span><span class="u"><span>More</span><i>&rsaquo;</i></span></a>' for a, b, u in L['links'])
    pages.append(
        f'<div class="page" id="p-{L["slug"]}" data-title="{html.escape(L["title"], quote=True)}">'
        f'<section class="phero wrap"><h1 class="h-l" data-split>{e(L["h1"])}</h1><p class="lead" data-fade>{e(L["lead"])}</p>'
        f'<div class="cta-r" data-fade style="margin-top:30px"><a href="/contact" data-link class="btn" data-magnet>Book a call <span class="ar">&rsaquo;</span></a><a href="/desk" data-link class="btn ghost">See the client portal</a></div></section>'
        f'<section class="wrap sp-get"><div class="lp-pts">{pts}</div></section>'
        f'<section class="wrap sp-work"><h2 class="h-m" data-split style="margin-bottom:clamp(28px,3vw,44px)">What we take on.</h2><div class="wl">{lks}</div></section>' +
        faq_html(L['faq']) + related(L['slug']) +
        '<section class="wrap sp-more"><span class="small">Also</span><div class="sp-chips">' +
        ''.join(f'<a href="{o["path"]}" data-link>{e(o["h1"].rstrip("."))}</a>' for o in LANDINGS if o is not L) +
        '<a href="/work" data-link>Our work</a></div></section>' + tail + '</div>')

for a in ARTICLES:
    pages.append(
        f'<div class="page" id="p-post-{a["slug"]}" data-title="{html.escape(a["title"], quote=True)} · Vibescape"><article class="art">'
        f'<div class="pm">{a["cat"]}, {a["mins"]} min read, {a["date"]}</div><h1 data-split>{e(a["title"])}</h1>'
        f'<div class="body" data-fade>' + ''.join(x if x.startswith('<') else f'<p>{x}</p>' for x in a['body']) +
        '</div>' + keep(a['slug']) + '<a href="/journal" data-link class="tlink back">Back to the journal</a></article>' + tail + '</div>')

anchor = '<div class="page" id="p-studio"'
assert anchor in s
s = s.replace(anchor, '<!--SEO-START-->' + ''.join(pages) + '<!--SEO-END-->' + anchor, 1)

# journal list: newest first
cards = ''.join(f'<!--SEOPOST--><a class="post" href="/journal/{a["slug"]}" data-link><div class="pm">{a["cat"]}<br>{a["mins"]} min read, {a["date"]}</div><div><h2>{e(a["title"])}</h2><p>{e(a["excerpt"])}</p></div><span class="rd">Read &rsaquo;</span></a><!--/SEOPOST-->' for a in ARTICLES)
s = s.replace('<div class="posts">', '<div class="posts">' + cards, 1)

# services page: link each service card to its own page
links = {'Branding': 'branding', 'Content': 'video-production', 'Performance': 'performance-marketing', 'Web': 'web-development'}
for h2, slug in links.items():
    pat = f'<h2>{h2}</h2><p class="hook">'
    k = s.find(pat)
    assert k > 0, h2
    end = s.find('</p>', s.find('<p class="sv-p">', k)) + 4
    s = s[:end] + f'<!--SVCLINK--><a href="/services/{slug}" data-link class="tlink sv-more">More on {h2.lower()}</a><!--/SVCLINK-->' + s[end:]
k = s.find('Apps, not just websites.')
if k > 0:
    end = s.find('</p>', k) + 4
    s = s[:end] + '<!--SVCLINK--><a href="/services/web-apps" data-link class="tlink sv-more">More on web apps</a><!--/SVCLINK-->' + s[end:]

# original hardcoded posts: keep reading links
for sl in ('logo-badalna-rebrand-nahi', 'dont-look-pakistani-be-pakistani', 'premium-bola-tha-beige-nahi'):
    i = s.find(f'<div class="page" id="p-post-{sl}"')
    k = s.find('<a href="/journal" data-link class="tlink back">', i)
    assert i > 0 and k > 0, sl
    s = s[:k] + keep(sl) + s[k:]

# footer: Dubai studio links to the Dubai page
s = re.sub(r'<!--FTLINKS-->.*?<!--/FTLINKS-->', '', s, flags=re.S)
s = s.replace('<a href="/careers" data-link>Careers</a><a href="/contact" data-link>Contact</a></div>',
              '<a href="/careers" data-link>Careers</a><a href="/contact" data-link>Contact</a><!--FTLINKS--><a href="/global" data-link>Work with us worldwide</a><a href="/for-agencies" data-link>For agencies</a><!--/FTLINKS--></div>')
s = s.replace('<p>Business Bay<br>Dubai</p>', '<a href="/dubai" data-link>Business Bay<br>Dubai</a>')
open(p, 'w').write(s)
print('pages', len(pages))
