"""Собирает превью Nordvelg для jukamedia.com/demo/kova/ из nordvelg/ (ресурсы берутся из /nordvelg/)."""
import os, re
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(os.path.dirname(root), 'demo', 'kova')
n = 0
for dp, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in ('tools', 'img', 'fonts', 'js', 'css', 'icons')]
    for fn in files:
        if not fn.endswith('.html') or fn == '404.html':
            continue
        rel = os.path.relpath(os.path.join(dp, fn), root)
        s = open(os.path.join(dp, fn)).read()
        s = re.sub(r'(?<=[\s"\'(,])/(img|fonts|js|icons|css)/', r'/nordvelg/\1/', s)
        s = re.sub(r'(?<=[\s"\'(,])/(favicon\.ico|site\.webmanifest)', r'/nordvelg/\1', s)
        s = re.sub(r'href="/(?!nordvelg/|demo/)([^"]*)"', r'href="/demo/kova/\1"', s)
        s = re.sub(r'a\.href="/', 'a.href="/demo/kova/', s)
        s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
        dst = os.path.join(out, rel); os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w').write(s); n += 1
print('demo built', n, 'pages')
