"""sitemap.xml из всех индексируемых самоканонических страниц, с hreflang-альтернативами."""
import os, re, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://nordvelg.com'
SKIP = {'tools', 'img', 'css', 'js', 'fonts', 'icons'}
today = datetime.date.today().isoformat()
pages = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = sorted(x for x in dirs if not (d == ROOT and x in SKIP))
    if 'index.html' not in files:
        continue
    h = open(os.path.join(d, 'index.html'), encoding='utf-8').read()
    rel = os.path.relpath(d, ROOT).replace(os.sep, '/')
    url = SITE + '/' + ('' if rel == '.' else rel + '/')
    can = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    if 'noindex' in h[:6000] or not can or can.group(1) != url:
        continue
    alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', h)
    pages.append((url, alts))
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
for url, alts in sorted(pages, key=lambda p: (p[0].count('/'), p[0])):
    out.append(f'<url><loc>{url}</loc><lastmod>{today}</lastmod>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>' for l, u in alts) + '</url>')
out.append('</urlset>')
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write('\n'.join(out) + '\n')
print(len(pages), 'urls')
