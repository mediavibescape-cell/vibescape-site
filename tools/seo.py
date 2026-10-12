"""Generate one static HTML file per route from index.html, plus sitemap.xml and robots.txt.
Each file gets its own title, description, canonical, Open Graph tags and the right page marked visible,
so Google indexes every page and every journal article separately.
Usage: python3 seo.py /path/to/site
"""
import re, sys, json, html, os, datetime
ROOT = sys.argv[1]
SITE = "https://vibescapemedia.com"
TODAY = datetime.date.today().isoformat()
src = open(os.path.join(ROOT, 'index.html')).read()
OG_IMG = SITE + "/assets/hero-poster.jpg"

PAGES = [
    # path, page id, title, description, priority
    ("/", "home", "Vibescape · Impossible to ignore.",
     "Creative company in Lahore and Dubai. Branding, video production, performance marketing and web for brands that would rather be remembered than seen.", "1.0"),
    ("/services", "services", "Services · Branding, Content, Performance & Web · Vibescape",
     "Four services, one engine. Brand strategy and identity, film and content production, Meta and Google ads, and fast websites and custom web apps. Lahore and Dubai.", "0.9"),
    ("/work", "work", "Work · Branding, Films & Websites · Vibescape",
     "Brand identities, 25 films across furniture, beauty, food, footwear and 3D, and live websites built by Vibescape in Lahore and Dubai.", "0.9"),
    ("/desk", "desk", "The Desk · Client portal & real time tracking · Vibescape",
     "Every Vibescape client gets a portal into the same Desk our team works in. Tasks, deliveries, live updates and monthly reports in one place.", "0.8"),
    ("/journal", "journal", "Journal · Notes on brands, content and design · Vibescape",
     "How Vibescape thinks about branding, content and design. Written by the team in Lahore.", "0.8"),
    ("/studio", "studio", "Studio · About Vibescape",
     "An independent creative company from Lahore and Dubai. We take the work seriously, not ourselves.", "0.6"),
    ("/careers", "careers", "Careers at Vibescape · Lahore Creative Jobs",
     "Open roles at Vibescape in Lahore: video, motion, performance marketing, frontend and social. Send your work first.", "0.5"),
    ("/contact", "contact", "Contact · Start a project · Vibescape",
     "Tell us what you are building. Vibescape replies within a day. Lahore and Dubai.", "0.7"),
    ("/privacy", "privacy", "Privacy policy · Vibescape",
     "What happens to your information when you visit vibescapemedia.com or contact Vibescape Media.", "0.2"),
]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import SERVICES, DUBAI, ARTICLES
for sv in SERVICES:
    PAGES.append(("/services/" + sv["slug"], "svc-" + sv["slug"], sv["title"], sv["desc"], "0.9"))
PAGES.append(("/dubai", "dubai", DUBAI["title"], DUBAI["desc"], "0.8"))
from content import LANDINGS
for L in LANDINGS:
    PAGES.append((L["path"], L["slug"], L["title"], L["desc"], "0.9"))
POST_DATES = {a["slug"]: a["iso"] for a in ARTICLES}
POST_DATES.update({"logo-badalna-rebrand-nahi": "2026-02-10", "dont-look-pakistani-be-pakistani": "2026-01-15",
              "premium-bola-tha-beige-nahi": "2025-12-12"})

# journal posts are discovered from the markup, so a new post only needs its page block
for m in re.finditer(r'<a class="post" href="/journal/([\w-]+)" data-link>.*?<h2>(.*?)</h2><p>(.*?)</p>', src, re.S):
    slug, title, excerpt = m.group(1), html.unescape(m.group(2)), html.unescape(m.group(3))
    PAGES.append(("/journal/" + slug, "post-" + slug, title + " · Vibescape", excerpt, "0.7"))

def page_block(pid):
    i = src.find(f'id="p-{pid}"')
    if i < 0: return ""
    j = src.find('<div class="page"', i)
    return src[i: j if j > 0 else len(src)]

def head_for(path, title, desc, pid):
    url = SITE + (path if path != "/" else "/")
    e = lambda x: html.escape(x, quote=True)
    extra = ""
    if pid.startswith("post-"):
        slug = pid[5:]
        d = POST_DATES.get(slug, TODAY)
        extra = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": title.split(" · ")[0],
            "description": desc, "datePublished": d, "dateModified": d, "url": url, "image": OG_IMG,
            "inLanguage": "en", "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": "Vibescape Media"},
            "publisher": {"@type": "Organization", "name": "Vibescape Media", "url": SITE}}) + '</script>'
    blk = page_block(pid)
    qa = re.findall(r'<details class="faq"><summary>(.*?)</summary><p>(.*?)</p></details>', blk)
    if qa:
        extra += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}} for q, a in qa]}) + '</script>'
    if pid == "home":
        extra += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [
            {"@type": "Organization", "@id": SITE + "/#org", "name": "Vibescape Media", "url": SITE, "logo": SITE + "/assets/desk/logo.png",
             "email": "mediavibescape@gmail.com", "telephone": "+923390116056"},
            {"@type": "ProfessionalService", "name": "Vibescape Media Lahore", "url": SITE, "parentOrganization": {"@id": SITE + "/#org"},
             "telephone": "+923390116056", "image": OG_IMG,
             "address": {"@type": "PostalAddress", "streetAddress": "C Block, Model Town", "addressLocality": "Lahore", "addressCountry": "PK"}},
            {"@type": "ProfessionalService", "name": "Vibescape Media Dubai", "url": SITE + "/dubai", "parentOrganization": {"@id": SITE + "/#org"}, "image": OG_IMG,
             "address": {"@type": "PostalAddress", "streetAddress": "Aswar Building, M Floor, Business Bay", "addressLocality": "Dubai", "addressCountry": "AE"}}]}) + '</script>'
    return (f'<title>{e(title)}</title>\n<meta name="description" content="{e(desc)}">\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="{"article" if pid.startswith("post-") else "website"}">'
            f'<meta property="og:site_name" content="Vibescape">'
            f'<meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}">'
            f'<meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{OG_IMG}">'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="robots" content="index,follow,max-image-preview:large">\n'
            '<meta name="google-site-verification" content="-yxTkUTixwVhEAfmCnkYXdPDKd4X3sohkHDC34hcvL8">\n' + extra)

def build(path, pid, title, desc):
    s = src
    s = re.sub(r'<title>.*?</title>\s*<meta name="description"[^>]*>', '__HEAD__', s, count=1, flags=re.S)
    s = re.sub(r'<link rel="canonical"[^>]*>\s*', '', s)
    s = re.sub(r'<meta property="og:[^>]*>\s*', '', s)
    s = re.sub(r'<meta name="(twitter:card|robots|google-site-verification)"[^>]*>\s*', '', s)
    s = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "BlogPosting".*?</script>', '', s, flags=re.S)
    s = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "(@type": "FAQPage|@graph)".*?</script>', '', s, flags=re.S)
    s = s.replace('__HEAD__', head_for(path, title, desc, pid), 1)
    s = re.sub(r'class="page on"', 'class="page"', s)
    s = s.replace(f'class="page" id="p-{pid}"', f'class="page on" id="p-{pid}"', 1)
    return s

for path, pid, title, desc, pr in PAGES:
    src = re.sub(r'(class="page(?: on)?" id="p-' + re.escape(pid) + r'" data-title=")[^"]*"', lambda m: m.group(1) + html.escape(title, quote=True) + '"', src, count=1)
out = []
for path, pid, title, desc, pr in PAGES:
    f = "index.html" if path == "/" else path.lstrip("/").replace("/", "-") + ".html"
    fp = os.path.join(ROOT, f); os.makedirs(os.path.dirname(fp), exist_ok=True)
    html_out = build(path, pid, title, desc)
    assert f'class="page on" id="p-{pid}"' in html_out, pid
    open(fp, "w").write(html_out)
    out.append((path, pr))

# 404 keeps the page id 404 and is noindex
nf = build("/404", "404", "Page not found · Vibescape", "This page moved or never existed.").replace(
    '<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
nf = re.sub(r'<link rel="canonical"[^>]*>\n?', '', nf)
open(os.path.join(ROOT, "404.html"), "w").write(nf)

sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, pr in out:
    sm.append(f'  <url><loc>{SITE}{path}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>')
sm.append('</urlset>')
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
toml = ['[[headers]]\n  for = "/assets/*"\n  [headers.values]\n    Cache-Control = "public, max-age=31536000, immutable"\n',
        '[[headers]]\n  for = "/*.html"\n  [headers.values]\n    Cache-Control = "public, max-age=0, must-revalidate"\n    X-Content-Type-Options = "nosniff"\n    Referrer-Policy = "strict-origin-when-cross-origin"\n',
        '[[headers]]\n  for = "/"\n  [headers.values]\n    Cache-Control = "public, max-age=0, must-revalidate"\n',
        '[[redirects]]\n  from = "/portfolio"\n  to = "/work"\n  status = 301\n',
        '[[redirects]]\n  from = "/blog"\n  to = "/journal"\n  status = 301\n',
        '[[redirects]]\n  from = "/index.html"\n  to = "/"\n  status = 301\n']
for path, pr in out:
    if path == "/": continue
    toml.append(f'[[redirects]]\n  from = "{path}"\n  to = "/{path.lstrip("/").replace("/", "-")}.html"\n  status = 200\n')
toml.append('[[redirects]]\n  from = "/*"\n  to = "/404.html"\n  status = 404\n')
open(os.path.join(ROOT, "netlify.toml"), "w").write("\n".join(toml))
print(len(out), "pages, sitemap, robots, netlify.toml written")
