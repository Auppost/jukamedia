"""Скачивает фото моделей BC Forged (tools/shop_images.json) в img/bc/ как webp 480 и 960."""
import json, os, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(root, 'tools/shop_images.json')))
out = os.path.join(root, 'img/shop'); os.makedirs(out, exist_ok=True)
def job(item):
    name, url = item
    if os.path.exists(os.path.join(out, f'{name}-960.webp')):
        return name, 'skip'
    src = f'/tmp/{name}.src'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Nordvelg catalog sync)'})
        with urllib.request.urlopen(req, timeout=60) as r, open(src, 'wb') as f:
            f.write(r.read())
        for w in (480, 960):
            subprocess.check_call(['convert', src + '[0]', '-trim', '+repage', '-resize', f'{w}x{w}>', '-strip', '-quality', '80', os.path.join(out, f'{name}-{w}.webp')])
        return name, 'ok'
    except Exception as e:
        return name, f'FAIL {e}'
with ThreadPoolExecutor(12) as ex:
    res = list(ex.map(job, data.items()))
bad = [r for r in res if r[1].startswith('FAIL')]
print(len(res), 'done,', len(bad), 'failed'); [print(*b) for b in bad]
