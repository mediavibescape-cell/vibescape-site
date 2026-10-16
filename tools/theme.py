"""Apply content/theme.json (editable in the CMS at /admin) to the site.
Rewrites the :root colour and font tokens at the top of site/assets/css/app.css,
the Google Fonts link and the theme-color meta in site/index.html.
Usage: python3 tools/theme.py   (build.py runs it first)
"""
import os, re, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
T = json.load(open(os.path.join(ROOT, 'content', 'theme.json'), encoding='utf-8'))

# Fonts offered in the CMS. All of them ship weights 400 to 700 on Google Fonts.
SERIF = {'Playfair Display', 'Fraunces', 'Lora'}
FONTS = {'Space Grotesk', 'Inter', 'Manrope', 'DM Sans', 'Plus Jakarta Sans', 'Sora', 'Outfit', 'Poppins',
         'Montserrat', 'Work Sans', 'Syne', 'Archivo', 'Instrument Sans'} | SERIF

def fail(msg):
    sys.exit('theme.json: ' + msg)

c = T['colors']
for k in ('background', 'surface', 'surface_raised', 'text', 'text_soft', 'text_muted', 'text_dim'):
    v = c.get(k, '')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', v or ''):
        fail(f'colour "{k}" must look like #1a2b3c, got {v!r}')
disp, body = T['fonts']['display'], T['fonts']['body']
for f in (disp, body):
    if f not in FONTS: fail(f'font {f!r} is not in the supported list')
maxw = int(T.get('max_width', 1600))
if not 900 <= maxw <= 2400: fail('max_width must be between 900 and 2400')

def rgb(h):
    return ','.join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
def stack(f):
    tail = "ui-serif,Georgia,serif" if f in SERIF else "ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif"
    return f"'{f}',{tail}"

root = (":root{\n"
        f"  --ink:{c['background']};--ink2:{c['surface']};--ink3:{c['surface_raised']};--paper:{c['text']};--stone:{c['text_soft']};--grey:{c['text_muted']};--dim:{c['text_dim']};\n"
        f"  --line:rgba({rgb(c['text'])},.1);--line2:rgba({rgb(c['text'])},.22);\n"
        "  --glass:rgba(255,255,255,.045);--glass2:rgba(255,255,255,.08);--gb:rgba(255,255,255,.12);--gb2:rgba(255,255,255,.2);\n"
        f"  --disp:{stack(disp)};\n"
        f"  --sans:{stack(body)};\n"
        f"  --g:clamp(20px,5vw,80px);--maxw:{maxw}px;\n"
        "  --e:cubic-bezier(.16,1,.3,1);--e2:cubic-bezier(.7,0,.2,1);\n"
        "}")

css_p = os.path.join(SITE, 'assets', 'css', 'app.css')
css = open(css_p, encoding='utf-8').read()
assert css.startswith(':root{'), 'app.css must start with the :root token block'
end = css.index('}') + 1
new_css = root + css[end:]
if new_css != css:
    open(css_p, 'w', encoding='utf-8').write(new_css)

def fam(f, w):
    return 'family=' + f.replace(' ', '+') + ':wght@' + w
fonts = fam(disp, '400;500;600;700') + ('&' + fam(body, '400;500') if body != disp else '')
idx_p = os.path.join(SITE, 'index.html')
s = open(idx_p, encoding='utf-8').read()
s2 = re.sub(r'(https://fonts\.googleapis\.com/css2\?)[^"]*?(&display=swap")', lambda m: m.group(1) + fonts + m.group(2), s)
s2 = re.sub(r'<meta name="theme-color" content="[^"]*">', f'<meta name="theme-color" content="{c["background"]}">', s2)
if s2 != s:
    open(idx_p, 'w', encoding='utf-8').write(s2)
print('theme ok:', disp, '/', body)
