"""Скачивает картинки из tools/images.json и кладёт webp в img/ (480, 960, 1600 px)."""
import json, os, subprocess, sys, urllib.request
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(root, 'tools/images.json')))
imgdir = os.path.join(root, 'img'); os.makedirs(imgdir, exist_ok=True)
manifest, failed = {}, []
for name, info in data.items():
    src = os.path.join('/tmp', name + '.src')
    try:
        req = urllib.request.Request(info['download'], headers={'User-Agent': 'Mozilla/5.0 (Nordvelg asset sync)'})
        with urllib.request.urlopen(req, timeout=60) as r, open(src, 'wb') as f:
            f.write(r.read())
        w, h = map(int, subprocess.check_output(['identify', '-format', '%w %h', src + '[0]']).split())
        sizes = []
        for target in (480, 960, 1600):
            tw = min(target, w)
            if sizes and tw == sizes[-1]:
                continue
            subprocess.check_call(['convert', src + '[0]', '-resize', f'{tw}x', '-strip', '-quality', '80',
                                   os.path.join(imgdir, f'{name}-{tw}.webp')])
            sizes.append(tw)
        manifest[name] = {'w': w, 'h': h, 'sizes': sizes}
        print('ok', name, w, h, sizes)
    except Exception as e:
        failed.append(name); print('FAIL', name, info['download'], e, file=sys.stderr)
json.dump({'images': manifest, 'failed': failed}, open(os.path.join(root, 'tools/images-manifest.json'), 'w'), indent=1)
print(len(manifest), 'ok,', len(failed), 'failed')
