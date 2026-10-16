"""Load journal articles from content/articles/*.md.

File format:
---
slug: url-slug
title: Article title
cat: Content
mins: 5               (optional, worked out from the word count if missing)
date: Oct 2026        (shown on the page; optional, worked out from iso if missing)
iso: 2026-10-12       (publish date, used for sorting, schema and sitemap)
excerpt: One or two sentences for the journal list and Google description.
keyword: main search phrase this article targets
---
Optional: image: /assets/x.jpg (social card; defaults to the first image in the body).
Body in simple markdown: paragraphs, "![caption](/assets/x.jpg)" images on their own line, "## " headings, "- " lists, **bold**, [links](/internal-or-https).
"""
import os, re, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'content', 'articles')

ESC = '\x00'
def inline(t):
    # markdown backslash escapes (the CMS editor writes these): keep the character, skip formatting
    t = re.sub(r'\\([\\`*_{}\[\]()#+\-.!>])', lambda m: ESC + str(ord(m.group(1))) + ESC, t)
    t = html.escape(t, quote=False)
    t = re.sub(r'(\*\*|__)(.+?)\1', r'<b>\2</b>', t)
    t = re.sub(r'(?<![\w*])[*_](?![\s*_])(.+?)(?<![\s*_])[*_](?![\w*])', r'<i>\1</i>', t)
    def link(m):
        txt, url = m.group(1), m.group(2)
        if url.startswith('/'):
            return f'<a class="tlink" href="{url}" data-link>{txt}</a>'
        return f'<a class="tlink" href="{url}" target="_blank" rel="noopener">{txt}</a>'
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, t)
    return re.sub(ESC + r'(\d+)' + ESC, lambda m: html.escape(chr(int(m.group(1))), quote=False), t)

def md_to_blocks(md):
    blocks, lst = [], []
    def flush():
        if lst:
            blocks.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in lst) + '</ul>'); lst.clear()
    for para in re.split(r'\n\s*\n', md.strip()):
        lines = [l.rstrip() for l in para.strip().split('\n') if l.strip()]
        if not lines: continue
        if all(re.match(r'[-*+] ', l) for l in lines):
            lst.extend(l[2:] for l in lines); flush(); continue
        if len(lines) > 1 and all(re.match(r'\d+[.)] ', l) for l in lines):
            flush()
            items = [re.sub(r'^\d+[.)] ', '', x) for x in lines]
            blocks.append('<ol>' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</ol>')
            continue
        flush()
        mi = re.fullmatch(r'!\[([^\]]*)\]\((/assets/[^)\s]+)\)', ' '.join(lines))
        if mi:
            alt = html.escape(mi.group(1), quote=True)
            blocks.append(f'<figure class="aimg"><img src="{mi.group(2)}" alt="{alt}" loading="lazy" decoding="async"><figcaption>{html.escape(mi.group(1), quote=False)}</figcaption></figure>')
            continue
        if lines[0].startswith('## '):
            blocks.append('<h2>' + inline(lines[0][3:]) + '</h2>')
            rest = ' '.join(lines[1:])
            if rest: blocks.append('<p>' + inline(rest) + '</p>')
        elif lines[0].startswith('### '):
            blocks.append('<h3>' + inline(lines[0][4:]) + '</h3>')
            rest = ' '.join(lines[1:])
            if rest: blocks.append('<p>' + inline(rest) + '</p>')
        else:
            blocks.append('<p>' + inline(' '.join(lines)) + '</p>')
    flush()
    return blocks

def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        import json
        try: return json.loads(v)
        except ValueError: return v[1:-1]
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v

def parse_front(text):
    """Small YAML subset: key: value, quoted values, folded (>) and literal (|) blocks,
    and plain values continued on indented lines. Enough for what the CMS writes."""
    meta, key, block, buf = {}, None, None, []
    def done():
        if key is None: return
        if block:
            meta[key] = ('\n' if block == '|' else ' ').join(x.strip() for x in buf).strip()
        else:
            meta[key] = _unquote(' '.join(x.strip() for x in buf))
    for line in text.split('\n'):
        if key is not None and (line.startswith((' ', '\t')) or not line.strip()):
            buf.append(line); continue
        if ':' not in line: continue
        done()
        k, v = line.split(':', 1)
        key, v = k.strip(), v.strip()
        if v[:1] in ('>', '|') and v.rstrip('-+') in ('>', '|'):
            block, buf = v[0], []
        else:
            block, buf = None, [v]
    done()
    return meta

def load_articles():
    arts = []
    for f in sorted(glob.glob(os.path.join(DIR, '*.md'))):
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
        if not m: raise ValueError('missing front matter: ' + f)
        meta = parse_front(m.group(1))
        meta['iso'] = str(meta.get('iso', ''))[:10]
        if not meta.get('date') and re.fullmatch(r'\d{4}-\d{2}-\d{2}', meta['iso']):
            import datetime
            meta['date'] = datetime.date.fromisoformat(meta['iso']).strftime('%b %Y')
        if not str(meta.get('mins', '')).strip():
            meta['mins'] = str(max(1, round(len(re.findall(r'\w+', m.group(2))) / 200)))
        for k in ('slug', 'title', 'cat', 'mins', 'date', 'iso', 'excerpt'):
            if not meta.get(k): raise ValueError(f'{f}: missing {k}')
        meta['body'] = md_to_blocks(m.group(2))
        im = re.search(r'!\[[^\]]*\]\((/assets/[^)\s]+)\)', m.group(2))
        meta.setdefault('image', im.group(1) if im else '')
        if not meta['image'] and im: meta['image'] = im.group(1)
        arts.append(meta)
    arts.sort(key=lambda a: (a['iso'], a['slug']), reverse=True)
    return arts
