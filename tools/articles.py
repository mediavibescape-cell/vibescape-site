"""Load journal articles from content/articles/*.md.

File format:
---
slug: url-slug
title: Article title
cat: Content
mins: 5
date: Oct 2026        (shown on the page)
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

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    def link(m):
        txt, url = m.group(1), m.group(2)
        if url.startswith('/'):
            return f'<a class="tlink" href="{url}" data-link>{txt}</a>'
        return f'<a class="tlink" href="{url}" target="_blank" rel="noopener">{txt}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, t)

def md_to_blocks(md):
    blocks, lst = [], []
    def flush():
        if lst:
            blocks.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in lst) + '</ul>'); lst.clear()
    for para in re.split(r'\n\s*\n', md.strip()):
        lines = [l.rstrip() for l in para.strip().split('\n') if l.strip()]
        if not lines: continue
        if all(l.startswith('- ') for l in lines):
            lst.extend(l[2:] for l in lines); flush(); continue
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
        else:
            blocks.append('<p>' + inline(' '.join(lines)) + '</p>')
    flush()
    return blocks

def load_articles():
    arts = []
    for f in glob.glob(os.path.join(DIR, '*.md')):
        raw = open(f, encoding='utf-8').read()
        m = re.match(r'---\n(.*?)\n---\n(.*)', raw, re.S)
        if not m: raise ValueError('missing front matter: ' + f)
        meta = {}
        for line in m.group(1).split('\n'):
            if ':' in line:
                k, v = line.split(':', 1); meta[k.strip()] = v.strip()
        for k in ('slug', 'title', 'cat', 'mins', 'date', 'iso', 'excerpt'):
            if not meta.get(k): raise ValueError(f'{f}: missing {k}')
        meta['body'] = md_to_blocks(m.group(2))
        im = re.search(r'!\[[^\]]*\]\((/assets/[^)\s]+)\)', m.group(2))
        meta.setdefault('image', im.group(1) if im else '')
        if not meta['image'] and im: meta['image'] = im.group(1)
        arts.append(meta)
    arts.sort(key=lambda a: (a['iso'], a['slug']), reverse=True)
    return arts
