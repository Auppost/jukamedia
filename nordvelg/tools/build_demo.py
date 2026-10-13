"""Собирает превью Nordvelg для jukamedia.com/demo/kova/ из nordvelg/ (ресурсы берутся из /nordvelg/)."""
import os, re, shutil
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(os.path.dirname(root), 'demo', 'kova')
for page in ['index.html', 'et/index.html', 'en/index.html', '3d/index.html']:
    s = open(os.path.join(root, page)).read()
    s = re.sub(r'(?<=[\s"\'(,])/(img|fonts|js|icons)/', r'/nordvelg/\1/', s)
    s = re.sub(r'(?<=[\s"\'(,])/(favicon\.ico|site\.webmanifest)', r'/nordvelg/\1', s)
    s = re.sub(r'href="/(et/|en/|3d/)?(#[^"]*)?"', lambda m: f'href="/demo/kova/{m.group(1) or ""}{m.group(2) or ""}"', s)
    s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)
    dst = os.path.join(out, page); os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w').write(s)
print('demo built')
