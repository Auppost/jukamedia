#!/usr/bin/env python3
"""Фиды Google Merchant Center для rehvo.ee, собранные из русского фида сайта.

Сайт rehvo.ee отдаёт только google-feed-ru.xml, и у 187 товаров там ID длиннее
50 символов: Google их не принимает. Эстонский язык Merchant Center не
поддерживает, поэтому для эстонцев делаем английский фид.

Скрипт пишет два файла в rehvo/feed/ (на сайте: jukamedia.com/rehvo/feed/...):
  google-feed-ru.xml  тот же русский фид, только длинные ID укорочены до 50
  google-feed-en.xml  английские тексты, ссылки на эстонские страницы
                      (/ru/product/x -> /product/x), короткие ID

Запуск: python3 rehvo/tools/build_feeds.py [путь_к_ru.xml]
Без аргумента скачивает https://rehvo.ee/google-feed-ru.xml.
"""
import copy
import hashlib
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

SRC_URL = 'https://rehvo.ee/google-feed-ru.xml'
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'feed')
G = 'http://base.google.com/ns/1.0'
MIN_ITEMS = 1000  # защита: если фид пришёл битый, старые файлы не трогаем

# Порядок важен: длинные фразы раньше коротких.
TITLE_RU_EN = [
    ('шина для внедорожника и фургона', 'SUV and van tyre'),
    ('всесезонная шина', 'all-season tyre'),
    ('летняя шина', 'summer tyre'),
    ('зимняя шина', 'winter tyre'),
    ('литой диск', 'alloy wheel'),
]
DESC_RU_EN = [
    ('Новый диск, цена за один диск.', 'New wheel, price per wheel incl. VAT.'),
    ('Новая шина, цена за одну шину.', 'New tyre, price per tyre incl. VAT.'),
    ('Бесплатный самовывоз в Таллинне, курьер по Эстонии от',
     'Free pickup in Tallinn, courier delivery across Estonia from'),
    ('шина для внедорожника и фургона, размер', 'SUV and van tyre, size'),
    ('всесезонная шина, размер', 'all-season tyre, size'),
    ('летняя шина, размер', 'summer tyre, size'),
    ('зимняя шина, размер', 'winter tyre, size'),
    ('Литой диск', 'Alloy wheel'),
    ('разболтовка', 'bolt pattern'),
    ('цвет', 'colour'),
]
CYR = re.compile('[А-Яа-яЁё]')


def short_id(i):
    """ID не длиннее 50 символов; одинаковый при каждом запуске."""
    if len(i) <= 50:
        return i
    return i[:41].rstrip('-') + '-' + hashlib.sha1(i.encode()).hexdigest()[:8]


def tr(text, pairs):
    for ru, en in pairs:
        text = text.replace(ru, en)
    return text


def load(src):
    if src:
        return open(src, 'rb').read()
    req = urllib.request.Request(SRC_URL, headers={'User-Agent': 'Mozilla/5.0 (Rehvo feed sync)'})
    return urllib.request.urlopen(req, timeout=120).read()


def build(root, lang):
    root = copy.deepcopy(root)
    ch = root.find('channel')
    if lang == 'en':
        ch.find('title').text = 'Rehvo'
        ch.find('description').text = 'Tyres and wheels from Rehvo'
        ch.find('link').text = 'https://rehvo.ee/'
    seen, skipped, shortened = set(), [], 0
    for it in list(ch.findall('item')):
        gid = it.find(f'{{{G}}}id')
        nid = short_id(gid.text.strip())
        shortened += nid != gid.text.strip()
        gid.text = nid
        link = it.find(f'{{{G}}}link')
        title = it.find(f'{{{G}}}title')
        desc = it.find(f'{{{G}}}description')
        ok = nid not in seen
        if lang == 'en':
            link.text = re.sub(r'^https://rehvo\.ee/ru/product/', 'https://rehvo.ee/product/', link.text.strip())
            title.text = tr(title.text, TITLE_RU_EN)
            desc.text = tr(desc.text, DESC_RU_EN)
            ok = ok and '/ru/' not in link.text and not any(CYR.search(t or '') for t in (title.text, desc.text))
        if not ok:
            skipped.append(nid)
            ch.remove(it)
            continue
        seen.add(nid)
    n = len(ch.findall('item'))
    print(f'{lang}: items {n}, shortened ids {shortened}, skipped {len(skipped)} {skipped[:5]}')
    if n < MIN_ITEMS:
        sys.exit(f'{lang}: too few items ({n}), keeping the old feeds')
    return root


def main():
    ET.register_namespace('g', G)
    src = ET.fromstring(load(sys.argv[1] if len(sys.argv) > 1 else None))
    feeds = {lang: build(src, lang) for lang in ('ru', 'en')}
    os.makedirs(OUT_DIR, exist_ok=True)
    for lang, root in feeds.items():
        out = os.path.join(OUT_DIR, f'google-feed-{lang}.xml')
        ET.ElementTree(root).write(out, encoding='utf-8', xml_declaration=True)
        print('written', os.path.normpath(out))


if __name__ == '__main__':
    main()
