#!/usr/bin/env python3
"""Эстонский фид Google Merchant Center для rehvo.ee.

Сайт rehvo.ee отдаёт только русский фид (google-feed-ru.xml), а у 187 товаров
ID длиннее 50 символов, и Google их не принимает. Этот скрипт берёт русский фид,
переводит шаблонные тексты на эстонский, меняет ссылки на эстонские страницы
(/ru/product/x -> /product/x) и укорачивает длинные ID. Результат:
rehvo/feed/google-feed-et.xml (jukamedia.com/rehvo/feed/google-feed-et.xml).

Запуск: python3 rehvo/tools/build_feed_et.py [путь_к_ru.xml]
Без аргумента скачивает https://rehvo.ee/google-feed-ru.xml.
"""
import hashlib
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

SRC_URL = 'https://rehvo.ee/google-feed-ru.xml'
OUT = os.path.join(os.path.dirname(__file__), '..', 'feed', 'google-feed-et.xml')
G = 'http://base.google.com/ns/1.0'
MIN_ITEMS = 1000  # защита: если фид пришёл битый, старый файл не трогаем

# Порядок важен: длинные фразы раньше коротких.
TITLE_RU_ET = [
    ('шина для внедорожника и фургона', 'maasturi- ja kaubikurehv'),
    ('всесезонная шина', 'aastaringne rehv'),
    ('летняя шина', 'suverehv'),
    ('зимняя шина', 'talverehv'),
    ('литой диск', 'valuvelg'),
]
DESC_RU_ET = [
    ('Новый диск, цена за один диск.', 'Uus velg, hind ühe velje kohta koos käibemaksuga.'),
    ('Новая шина, цена за одну шину.', 'Uus rehv, hind ühe rehvi kohta koos käibemaksuga.'),
    ('Бесплатный самовывоз в Таллинне, курьер по Эстонии от',
     'Tasuta järeletulemine Tallinnas, kulleriga üle Eesti alates'),
    ('шина для внедорожника и фургона, размер', 'maasturi- ja kaubikurehv, mõõt'),
    ('всесезонная шина, размер', 'aastaringne rehv, mõõt'),
    ('летняя шина, размер', 'suverehv, mõõt'),
    ('зимняя шина, размер', 'talverehv, mõõt'),
    ('Литой диск', 'Valuvelg'),
    ('разболтовка', 'poldimuster'),
    ('цвет', 'värv'),
]
CYR = re.compile('[А-Яа-яЁё]')


def short_id(i):
    """ID не длиннее 50 символов; одинаковый при каждом запуске."""
    if len(i) <= 50:
        return i
    return i[:41].rstrip('-') + '-' + hashlib.sha1(i.encode()).hexdigest()[:8]


def tr(text, pairs):
    for ru, et in pairs:
        text = text.replace(ru, et)
    return text


def load(src):
    if src:
        return open(src, 'rb').read()
    req = urllib.request.Request(SRC_URL, headers={'User-Agent': 'Mozilla/5.0 (Rehvo feed sync)'})
    return urllib.request.urlopen(req, timeout=120).read()


def main():
    ET.register_namespace('g', G)
    root = ET.fromstring(load(sys.argv[1] if len(sys.argv) > 1 else None))
    ch = root.find('channel')
    ch.find('title').text = 'Rehvo'
    ch.find('description').text = 'Rehvid ja veljed Rehvo'
    ch.find('link').text = 'https://rehvo.ee/'

    seen, skipped, shortened = set(), [], 0
    for it in list(ch.findall('item')):
        gid = it.find(f'{{{G}}}id')
        nid = short_id(gid.text.strip())
        shortened += nid != gid.text.strip()
        gid.text = nid
        link = it.find(f'{{{G}}}link')
        link.text = re.sub(r'^https://rehvo\.ee/ru/product/', 'https://rehvo.ee/product/', link.text.strip())
        it.find(f'{{{G}}}title').text = tr(it.find(f'{{{G}}}title').text, TITLE_RU_ET)
        d = it.find(f'{{{G}}}description')
        d.text = tr(d.text, DESC_RU_ET)
        texts = [it.find(f'{{{G}}}title').text, d.text, link.text]
        if any(CYR.search(t or '') for t in texts) or '/ru/' in link.text or nid in seen:
            skipped.append(nid)
            ch.remove(it)
            continue
        seen.add(nid)

    n = len(ch.findall('item'))
    print(f'items: {n}, shortened ids: {shortened}, skipped: {len(skipped)} {skipped[:5]}')
    if n < MIN_ITEMS:
        sys.exit(f'too few items ({n}), keeping the old feed')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ET.ElementTree(root).write(OUT, encoding='utf-8', xml_declaration=True)
    print('written', os.path.normpath(OUT))


if __name__ == '__main__':
    main()
