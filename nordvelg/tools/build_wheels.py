"""Генерирует страницы моделей дисков /wheels/<slug>/ и каталог /wheels/ на трёх языках.

Источник данных: блок «Модели» (.cat) и подбор по машине (var DATA) в index.html каждой языковой версии.
Запуск: python3 nordvelg/tools/build_wheels.py (после правок главных страниц).
"""
import html, json, os, re, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://nordvelg.com'
LANGS = {'ru': '', 'et': 'et/', 'en': 'en/'}
WA = '37257494989'
import hashlib
V = lambda p: hashlib.md5(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()[:8]
MAN = json.load(open(os.path.join(ROOT, 'tools/images-manifest.json')))['images']
for _f in ('tools/bc-manifest.json', 'tools/shop-manifest.json'):
    if os.path.exists(os.path.join(ROOT, _f)):
        MAN.update(json.load(open(os.path.join(ROOT, _f))))
SHOP = json.load(open(os.path.join(ROOT, 'tools/shop_items.json')))
bslug = lambda b: re.sub(r'[^a-z0-9]+', '-', b.lower()).strip('-')
BC = json.load(open(os.path.join(ROOT, 'tools/bc_models.json')))
PRICE = {'mono': {18: 960, 19: 960, 20: 1066, 21: 1188, 22: 1250, 23: 1390}, 'KX': {19: 1255, 20: 1376, 21: 1528, 22: 1630},
         'two': {18: 1216, 19: 1216, 20: 1322, 21: 1444, 22: 1506, 23: 1646}, 'HCX': {19: 1551, 20: 1667, 21: 1849, 22: 1911}}
setp = lambda p: int(round(p * 4 * 1.24 / 10) * 10)

T = {
 'ru': dict(
  catalog='Каталог', home='Главная', pick='Подбор по машине', faq='Вопросы',
  cat_title='Каталог кованых дисков: BC Forged, Brixton, BBS и другие | Nordvelg',
  cat_desc='Модели кованых дисков под заказ с доставкой в Таллинн: BC Forged, Brixton Forged, BBS, Novitec и другие. Цены с НДС, подбор под ваш автомобиль.',
  cat_h1='Каталог кованых дисков', cat_sub='Модели, которые чаще всего заказывают. Каждую делают под конкретную машину: диаметр, ширина, вылет и отделка на выбор',
  title='{name}: кованые диски под заказ в Таллинне | Nordvelg',
  desc='{name} под ваш автомобиль: подбор размера и вылета, эскиз до оплаты, доставка по Эстонии.{price}',
  price_from='от {p} €', set_note='за комплект из 4 дисков, с НДС и доставкой по Эстонии', est_note='ориентировочная цена, точную назовём после подбора',
  on_request='Цена по запросу', cta='Рассчитать для моей машины', wa='Спросить в WhatsApp',
  wa_text='Здравствуйте, интересуют диски {name}. Машина: ',
  fits='Подходит для', fits_note='Эти машины уже есть в нашем подборе. Для других моделей проверим посадку бесплатно',
  know='Что важно знать', how='Как проходит заказ', more='Другие модели {brand}', all='Весь каталог',
  zoom='Нажмите, чтобы увеличить', close='Закрыть',
  steps=['Вы присылаете марку, модель и год машины', 'Мы подбираем размер, вылет и отделку и присылаем эскиз', 'Вы вносите 50% предоплаты, завод изготавливает диски', 'Оплата остатка и доставка в Таллинн'],
  bc=['Кованая заготовка из алюминия 6061-T6, каждый диск фрезеруют под вашу машину: разболтовка, центральное отверстие и вылет', 'Диски проходят японские тесты прочности JWL и VIA', 'Около 40 вариантов отделки, можно сочетать две', 'Изготовление 4-6 недель, затем доставка в Таллинн'],
  brixton=['Американский бренд, каждый комплект собирают под конкретный автомобиль', 'Производство 7-10 недель', 'Цену считаем по вашей спецификации: размер, ширина, отделка'],
  other=['Заказываем через официального европейского дистрибьютора', 'Срок и точную цену подтверждаем после подбора под вашу машину', 'Доставка в Таллинн'],
  pay='Без предоплаты за подбор: сначала эскиз и точная цена, потом решение',
  per_wheel='', mono='моноблок', two='две части',
  foot='Кованые диски BC Forged, Brixton Forged и MV Forged под заказ в Таллинне', city='Таллинн, Эстония',
  credits='Фото дисков и автомобилей: BC Forged, Brixton Forged, Baan Velgen. Названия брендов принадлежат их владельцам',
  ptable='Цена комплекта по диаметру', col_d='Диаметр', col_w='Ширина', col_p='Комплект из 4', ptable_note='С НДС и доставкой по Эстонии. Опции оплачиваются отдельно: полированная полка, накатка, колпачки', series='Серия {s}', filt_all='Все', sizes_d='Размеры {a}-{b}″.',
  brand_title='Диски {b} под заказ в Таллинне: все модели и цены | Nordvelg', brand_desc='Все модели {b} под заказ с доставкой в Таллинн и по Эстонии. Подбор под ваш автомобиль, эскиз до оплаты.', brand_h1='Диски {b}', all_brand='Все модели {b}: {n}', on_req_note='Цену считаем под вашу машину и спецификацию',
  lang_name='Язык'),
 'et': dict(
  catalog='Kataloog', home='Avaleht', pick='Valik auto järgi', faq='Küsimused',
  cat_title='Sepistatud veljed: BC Forged, Brixton, BBS ja teised | Nordvelg',
  cat_desc='Tellimusel valmivad sepistatud veljed tarnega Tallinnasse: BC Forged, Brixton Forged, BBS, Novitec ja teised. Hinnad koos käibemaksuga, valik teie auto järgi.',
  cat_h1='Sepistatud velgede kataloog', cat_sub='Kõige sagedamini tellitud mudelid. Iga komplekt valmib konkreetsele autole: läbimõõt, laius, ET ja viimistlus teie valikul',
  title='{name}: sepistatud veljed tellimusel Tallinnas | Nordvelg',
  desc='{name} teie autole: mõõdu ja ET valik, eskiis enne makset, tarne üle Eesti.{price}',
  price_from='alates {p} €', set_note='4 velje komplekt koos käibemaksu ja tarnega Eestis', est_note='ligikaudne hind, täpse hinna ütleme pärast valikut',
  on_request='Hind päringu alusel', cta='Arvuta minu autole', wa='Küsi WhatsAppis',
  wa_text='Tere, mind huvitavad veljed {name}. Auto: ',
  fits='Sobib autodele', fits_note='Need autod on meie valikus juba olemas. Teiste mudelite puhul kontrollime sobivust tasuta',
  know='Mida on oluline teada', how='Kuidas tellimine käib', more='Teised {brand} mudelid', all='Kogu kataloog',
  zoom='Suurendamiseks klõpsake', close='Sulge',
  steps=['Saadate auto marga, mudeli ja aasta', 'Valime mõõdu, ET ja viimistluse ning saadame eskiisi', 'Tasute 50% ettemaksu, tehas valmistab veljed', 'Lõppmakse ja tarne Tallinnasse'],
  bc=['Sepistatud toorik alumiiniumist 6061-T6, iga velg freesitakse teie auto järgi: poldimuster, keskava ja ET', 'Veljed läbivad Jaapani tugevustestid JWL ja VIA', 'Umbes 40 viimistlust, kahte saab kombineerida', 'Valmistamine 4-6 nädalat, seejärel tarne Tallinnasse'],
  brixton=['Ameerika bränd, iga komplekt valmib konkreetsele autole', 'Tootmine 7-10 nädalat', 'Hinna arvutame teie spetsifikatsiooni järgi: mõõt, laius, viimistlus'],
  other=['Tellime ametliku Euroopa edasimüüja kaudu', 'Tähtaja ja täpse hinna kinnitame pärast valikut teie auto järgi', 'Tarne Tallinnasse'],
  pay='Valik on tasuta: kõigepealt eskiis ja täpne hind, siis otsus',
  per_wheel='', mono='monoblokk', two='kaheosaline',
  foot='BC Forged, Brixton Forged ja MV Forged sepistatud veljed tellimusel Tallinnas', city='Tallinn, Eesti',
  credits='Velgede ja autode fotod: BC Forged, Brixton Forged, Baan Velgen. Kaubamärgid kuuluvad nende omanikele',
  ptable='Komplekti hind läbimõõdu järgi', col_d='Läbimõõt', col_w='Laius', col_p='4 velje komplekt', ptable_note='Koos käibemaksu ja tarnega Eestis. Lisavalikud eraldi: poleeritud äär, rantimine, rummukatted', series='Seeria {s}', filt_all='Kõik', sizes_d='Mõõdud {a}-{b}″.',
  brand_title='{b} veljed tellimusel Tallinnas: kõik mudelid ja hinnad | Nordvelg', brand_desc='Kõik {b} mudelid tellimusel tarnega Tallinnasse ja üle Eesti. Valik teie auto järgi, eskiis enne makset.', brand_h1='{b} veljed', all_brand='Kõik {b} mudelid: {n}', on_req_note='Hinna arvutame teie auto ja spetsifikatsiooni järgi',
  lang_name='Keel'),
 'en': dict(
  catalog='Catalogue', home='Home', pick='Find by car', faq='Questions',
  cat_title='Forged Wheels Catalogue: BC Forged, Brixton, BBS and more | Nordvelg',
  cat_desc='Made-to-order forged wheels delivered to Tallinn: BC Forged, Brixton Forged, BBS, Novitec and more. Prices incl. VAT, fitment checked for your car.',
  cat_h1='Forged wheels catalogue', cat_sub='The models our customers order most. Each set is made for a specific car: diameter, width, offset and finish of your choice',
  title='{name}: custom forged wheels in Tallinn | Nordvelg',
  desc='{name} built for your car: size and offset check, a sketch before you pay, delivery across Estonia.{price}',
  price_from='from €{p}', set_note='per set of 4, incl. VAT and delivery in Estonia', est_note='indicative price, exact quote after the fitment check',
  on_request='Price on request', cta='Get a quote for my car', wa='Ask on WhatsApp',
  wa_text='Hello, I am interested in {name} wheels. My car: ',
  fits='Fits', fits_note='These cars are already in our fitment guide. For other models we check fitment for free',
  know='Good to know', how='How ordering works', more='More {brand} models', all='Full catalogue',
  zoom='Click to enlarge', close='Close',
  steps=['You send the make, model and year of your car', 'We choose size, offset and finish and send a sketch', 'You pay a 50% deposit, the factory makes the wheels', 'Balance payment and delivery to Tallinn'],
  bc=['Forged 6061-T6 aluminium billet, each wheel machined for your car: bolt pattern, centre bore and offset', 'Tested to the Japanese JWL and VIA strength standards', 'About 40 finishes, two can be combined', 'Made in 4-6 weeks, then delivered to Tallinn'],
  brixton=['American brand, each set is built for a specific car', 'Production takes 7-10 weeks', 'We price it from your specification: size, width, finish'],
  other=['Ordered through the official European distributor', 'Lead time and exact price confirmed after the fitment check', 'Delivery to Tallinn'],
  pay='The fitment check is free: first a sketch and an exact price, then you decide',
  per_wheel='', mono='monoblock', two='two-piece',
  foot='BC Forged, Brixton Forged and MV Forged wheels made to order in Tallinn', city='Tallinn, Estonia',
  credits='Wheel and car photos: BC Forged, Brixton Forged, Baan Velgen. Brand names belong to their owners',
  ptable='Set price by diameter', col_d='Diameter', col_w='Width', col_p='Set of 4', ptable_note='Incl. VAT and delivery in Estonia. Options are extra: polished lip, knurling, centre caps', series='{s} series', filt_all='All', sizes_d='Sizes {a}-{b}″.',
  brand_title='{b} wheels made to order in Tallinn: all models and prices | Nordvelg', brand_desc='All {b} models made to order with delivery to Tallinn and across Estonia. Fitment for your car, a sketch before you pay.', brand_h1='{b} wheels', all_brand='All {b} models: {n}', on_req_note='We price it for your car and specification',
  lang_name='Language'),
}

def slug(b, n):
    return re.sub(r'[^a-z0-9]+', '-', f'{b} {n}'.lower()).strip('-')

def esc(s):
    return html.escape(s, quote=True)

def fmt(p, lang):
    s = f'{p:,}'.replace(',', ' ' if lang != 'en' else ',')
    return T[lang]['price_from'].format(p=s)

def big(src):
    """Самая крупная версия той же картинки."""
    m = re.match(r'/img/(.+)-(\d+)\.webp$', src or '')
    if not m or m.group(1) not in MAN:
        return src
    return f'/img/{m.group(1)}-{MAN[m.group(1)]["sizes"][-1]}.webp'

def dims(src):
    m = re.match(r'/img/(.+)-(\d+)\.webp$', src or '')
    if not m or m.group(1) not in MAN:
        return 960, 960
    M = MAN[m.group(1)]; w = min(int(m.group(2)), M['w'])
    return w, round(M['h'] * w / M['w'])

def collect(lang):
    s = open(os.path.join(ROOT, LANGS[lang], 'index.html')).read()
    data = json.loads(re.search(r'var DATA=(\{.*?\});', s, re.S).group(1))
    wheels = {}
    # featured block
    cat = s[s.find('class="cat"'):]
    cat = cat[:cat.find('</section>')]
    fm = re.search(r'<div class="feature">.*?<img[^>]*src="([^"]+)" data-alt="([^"]+)".*?<div class="brand"[^>]*>([^<]+)</div>\s*<h3>([^<]+)</h3>\s*<div class="spec">(.*?)</div>', cat, re.S)
    items = []
    if fm:
        items.append((fm.group(3), fm.group(4), fm.group(1), fm.group(2), re.findall(r'<span>([^<]+)</span>', fm.group(5))))
    for a in re.finditer(r'<a class="w[^"]*"[^>]*><div class="stage"><img([^>]*)></div><span class="brand">([^<]+)</span><h3>([^<]+)</h3><div class="spec">(.*?)</div></a>', cat):
        src = re.search(r'\ssrc="([^"]+)"', a.group(1)).group(1)
        alt = re.search(r'data-alt="([^"]+)"', a.group(1))
        items.append((a.group(2), a.group(3), src, alt.group(1) if alt else None, re.findall(r'<span>([^<]+)</span>', a.group(4))))
    for b, n, src, alt, spec in items:
        wheels[slug(b, n)] = dict(b=b, n=n, imgs=[x for x in (src, alt) if x], spec=spec, cars=[], p=None, featured=True)
    for make, models in data.items():
        for model, lst in models.items():
            for w in lst:
                k = slug(w['b'], w['n'])
                d = wheels.setdefault(k, dict(b=w['b'], n=w['n'], imgs=[], spec=[w['c']] if w['c'] else [], cars=[], p=None, featured=False))
                if w['i'] and w['i'] not in d['imgs']:
                    d['imgs'].append(w['i'])
                car = f'{make} {model}'
                if car not in d['cars']:
                    d['cars'].append(car)
                if w.get('p') and (d['p'] is None or w['p'] < d['p']):
                    d['p'] = w['p']
                if not d['spec'] and w['c']:
                    d['spec'] = [w['c']]
    # full BC Forged catalogue (bcforged.com.tw)
    for m in BC:
        typ = 'mono' if m['cat'] == 1 else 'two'
        table = PRICE['KX'] if m['series'] == 'KX' else PRICE['HCX'] if m['series'] == 'HCX' else PRICE[typ]
        ds = sorted(int(x) for x in m['sizes'])
        ptab = [(dd, m['sizes'][str(dd)], setp(table[dd])) for dd in ds if dd in table]
        local = [f"/img/bc/{n}-960.webp" for n in m['local'] if ('bc/' + n) in MAN]
        k = m['slug']
        label = T[lang]['mono'] if typ == 'mono' else T[lang]['two']
        rng = f"{ds[0]}-{ds[-1]}″" if ds else ''
        d = wheels.get(k)
        if d is None:
            d = wheels[k] = dict(b='BC Forged', n=m['name'], imgs=local, spec=[label] + ([rng] if rng else []), cars=[], p=None, featured=False)
        else:
            for i in local:
                if i not in d['imgs']:
                    d['imgs'].append(i)
        d.update(series=m['series'], typ=typ, sizes=ds, ptab=ptab, src=m['url'])
        if ptab:
            d['p'] = min(x[2] for x in ptab)
    # other wheel brands from the Baan Velgen shop (prices there are per set incl. 21% NL VAT)
    PREFIX = ['brixton forged', 'brixton', 'hre', 'vorsteiner', 'bbs', 'anrky', 'apex', 'vossen', 'ipe magnesium wheels', 'ipe', 'brabus', 'novitec', 'manthey racing']
    existing = list(wheels.keys())
    for it in SHOP:
        if it['kind'] != 'wheel':
            continue
        n = it['title'].strip()
        for pf in PREFIX:
            if n.lower().startswith(pf + ' '):
                n = n[len(pf):].strip(' -–')
                break
        k = slug(it['brand'], n)
        if k in wheels or any(k.startswith(e + '-') for e in existing):
            continue
        local = [f"/img/shop/{x}-960.webp" for x in it['local'] if ('shop/' + x) in MAN]
        if not local:
            continue
        ds = sorted({int(x) for v, _ in it['variants'] for x in re.findall(r'(\d{2})\s*(?:inch|″|")', v + ' ' + it['title']) if 15 <= int(x) <= 24})
        spec = [f"{ds[0]}-{ds[-1]}″" if len(ds) > 1 else f"{ds[0]}″"] if ds else []
        prices = [float(p) for _, p in it['variants'] if p and float(p) > 0]
        p = setp(min(prices) / 1.21 / 4) if (it['brand'] == 'Brixton Forged' and prices) else None
        wheels[k] = dict(b=it['brand'], n=n, imgs=local, spec=spec, cars=[], p=p, featured=False, shop=True)
    # BC prices from the dealer list (set of 4, incl. VAT)
    for d in wheels.values():
        if d['b'] == 'BC Forged' and d['p'] is None:
            two = any(x in ' '.join(d['spec']).lower() for x in ('две', 'kahe', 'two'))
            d['p'] = 6030 if two else 4760
    return wheels, s

FONTCSS = None

def head_common(lang, title, desc, url, alts, og_img):
    hl = ''.join(f'<link rel="alternate" hreflang="{l}" href="{u}">\n' for l, u in alts.items())
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{hl}<link rel="alternate" hreflang="x-default" href="{alts['ru']}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Nordvelg">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#E9EAEC">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/geologica-{'cyrillic' if lang=='ru' else 'latin'}-shrp-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/wheel.css?v={V('css/wheel.css')}">
'''

EXH = {'ru': 'Выхлоп iPE', 'et': 'iPE väljalase', 'en': 'iPE exhausts'}

def header(lang, alts):
    t = T[lang]; p = '/' + LANGS[lang]
    langs = ''.join(f'<a href="{alts[l].replace(SITE, "")}" hreflang="{l}" lang="{l}"{" aria-current=\"page\"" if l == lang else ""}>{l.upper()}</a>' for l in ('ru', 'et', 'en'))
    return f'''<header class="top"><div class="wrap in">
<a class="mark" href="{p}">Nordvelg</a>
<nav><a href="{p}wheels/">{t['catalog']}</a><a href="{p}exhaust/">{EXH[lang]}</a><a href="{p}#cars">{t['pick']}</a><a href="{p}#faq">{t['faq']}</a></nav>
<nav class="lang" aria-label="{t['lang_name']}">{langs}</nav>
</div></header>
'''

def footer(lang):
    t = T[lang]
    return f'''<footer><div class="wrap foot">
<div><a class="mark" href="/{LANGS[lang]}">Nordvelg</a><p>{t['foot']}</p></div>
<div><a href="https://t.me/alekseipsk" target="_blank" rel="noopener noreferrer">Telegram @alekseipsk</a><br><a href="https://wa.me/{WA}" target="_blank" rel="noopener noreferrer">WhatsApp +372 5749 4989</a></div>
<div>Juka Media OÜ<br>{t['city']}</div>
</div><div class="wrap credits">{t['credits']}</div></footer>
'''

def card(d, lang):
    t = T[lang]; k = slug(d['b'], d['n'])
    src = d['imgs'][0] if d['imgs'] else ''
    w, h = dims(src)
    price = fmt(d['p'], lang) if d['p'] else t['on_request']
    spec = ''.join(f'<span>{esc(x)}</span>' for x in d['spec'][:2])
    da = f' data-type="{d.get("typ", "")}" data-series="{esc(d.get("series") or "")}"'
    return f'<a class="card"{da} href="/{LANGS[lang]}wheels/{k}/"><div class="stage"><img src="{src}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(d["b"] + " " + d["n"])}"></div><span class="brand">{esc(d["b"])}</span><h3>{esc(d["n"])}</h3><div class="spec">{spec}</div><div class="price">{price}</div></a>'

def page(k, d, lang, all_wheels):
    t = T[lang]; name = f"{d['b']} {d['n']}"
    alts = {l: f"{SITE}/{LANGS[l]}wheels/{k}/" for l in LANGS}
    url = alts[lang]
    price_txt = (' ' + fmt(d['p'], lang) + '.') if d['p'] else ''
    title = t['title'].format(name=name)
    desc = t['desc'].format(name=name, price=price_txt)
    if d.get('sizes'):
        desc = desc + ' ' + t['sizes_d'].format(a=d['sizes'][0], b=d['sizes'][-1])
    imgs = [i for i in d['imgs'] if i]
    og = SITE + (big(imgs[-1]) if imgs else '/img/og-nordvelg.jpg')
    out = head_common(lang, title, desc, url, alts, og)
    # JSON-LD
    prod = {"@type": "Product", "name": name, "brand": {"@type": "Brand", "name": d['b']},
            "image": [SITE + big(i) for i in imgs], "url": url, "description": desc}
    if d['p']:
        prod["offers"] = {"@type": "Offer", "priceCurrency": "EUR", "price": d['p'], "availability": "https://schema.org/PreOrder",
                          "url": url, "seller": {"@type": "Organization", "name": "Nordvelg", "url": SITE + "/"}}
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nordvelg", "item": f"{SITE}/{LANGS[lang]}"},
        {"@type": "ListItem", "position": 2, "name": t['catalog'], "item": f"{SITE}/{LANGS[lang]}wheels/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [prod, crumbs]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n</head>\n<body>\n'
    out += header(lang, alts)
    p = '/' + LANGS[lang]
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs"><a href="{p}">Nordvelg</a><span>/</span><a href="{p}wheels/">{t["catalog"]}</a><span>/</span><span aria-current="page">{esc(name)}</span></nav>\n'
    # gallery
    gal = ''
    for n, i in enumerate(imgs):
        w, h = dims(i)
        gal += f'<button type="button" class="shot{" on" if n == 0 else ""}" data-big="{big(i)}" aria-label="{t["zoom"]}"><img src="{i}" width="{w}" height="{h}" alt="{esc(name)}" {"fetchpriority=\"high\"" if n == 0 else "loading=\"lazy\""} decoding="async"></button>'
    thumbs = ''
    if len(imgs) > 1:
        thumbs = '<div class="thumbs">' + ''.join(f'<button type="button" data-i="{n}" aria-label="{n+1}"{" class=\"on\"" if n == 0 else ""}><img src="{i}" alt="" loading="lazy" decoding="async"></button>' for n, i in enumerate(imgs)) + '</div>'
    spec = ''.join(f'<span>{esc(x)}</span>' for x in d['spec'])
    if d['p']:
        note = t['set_note'] if d['b'] == 'BC Forged' else t['est_note']
        price = f'<div class="price">{fmt(d["p"], lang)}</div><p class="pnote">{note}</p>'
    else:
        price = f'<div class="price">{t["on_request"]}</div><p class="pnote">{t["on_req_note"]}</p>'
    q = urllib.parse.quote(name)
    wa = 'https://wa.me/' + WA + '?text=' + urllib.parse.quote(t['wa_text'].format(name=name))
    facts = t['bc'] if d['b'] == 'BC Forged' else t['brixton'] if d['b'] == 'Brixton Forged' else t['other']
    out += f'''<section class="prod">
<div class="gallery"><div class="main">{gal}</div>{thumbs}<p class="hint">{t['zoom']}</p></div>
<div class="info">
<div class="brand">{esc(d['b'])}</div>
<h1>{esc(d['n'])}</h1>
<div class="spec">{spec}</div>
{price}
<div class="ctas"><a class="btn" href="{p}?model={q}#quote">{t['cta']}</a><a class="btn ghost" href="{wa}" target="_blank" rel="noopener noreferrer">{t['wa']}</a></div>
<p class="pay">{t['pay']}</p>
<h2>{t['know']}</h2>
<ul class="facts">{''.join(f'<li>{x}</li>' for x in facts)}</ul>
</div>
</section>
'''
    if d.get('ptab'):
        rows = ''.join(f'<tr><td>{dd}″</td><td>{ws[0]}-{ws[-1]}J</td><td>{fmt(pp, lang)}</td></tr>' for dd, ws, pp in d['ptab'] if ws)
        out += f'<section class="ptab"><h2>{t["ptable"]}</h2><div class="tw"><table><thead><tr><th scope="col">{t["col_d"]}</th><th scope="col">{t["col_w"]}</th><th scope="col">{t["col_p"]}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="note">{t["ptable_note"]}</p></section>\n'
    if d['cars']:
        out += f'<section class="fits"><h2>{t["fits"]}</h2><div class="chips">{"".join(f"<span>{esc(c)}</span>" for c in d["cars"][:40])}</div><p class="note">{t["fits_note"]}</p></section>\n'
    out += f'<section class="how"><h2>{t["how"]}</h2><ol>{"".join(f"<li>{x}</li>" for x in t["steps"])}</ol></section>\n'
    rel = [w for kk, w in all_wheels.items() if kk != k and d.get('series') and w.get('series') == d.get('series')][:4]
    rel += [w for kk, w in all_wheels.items() if kk != k and w['b'] == d['b'] and w not in rel and w['featured']][:4 - len(rel)]
    rel += [w for kk, w in all_wheels.items() if kk != k and w['b'] == d['b'] and w not in rel][:4 - len(rel)]
    if len(rel) < 4:
        rel += [w for kk, w in all_wheels.items() if kk != k and w['b'] != d['b'] and w['featured']][:4 - len(rel)]
    out += f'<section class="rel"><div class="rh"><h2>{t["more"].format(brand=d["b"])}</h2><a href="{p}wheels/">{t["all"]}</a></div><div class="grid">{"".join(card(w, lang) for w in rel)}</div></section>\n</main>\n'
    out += f'<div class="lb" hidden><button type="button" class="x" aria-label="{t["close"]}">×</button></div>\n'
    out += footer(lang)
    out += f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return out

def catalog(lang, wheels, brand=None):
    t = T[lang]
    sub = f"wheels/brand/{bslug(brand)}/" if brand else "wheels/"
    alts = {l: f"{SITE}/{LANGS[l]}{sub}" for l in LANGS}
    sel = {k: w for k, w in wheels.items() if (brand is None or w['b'] == brand)}
    title = t['brand_title'].format(b=brand) if brand else t['cat_title']
    desc = t['brand_desc'].format(b=brand) if brand else t['cat_desc']
    h1 = t['brand_h1'].format(b=brand) if brand else t['cat_h1']
    out = head_common(lang, title, desc, alts[lang], alts, SITE + '/img/og-nordvelg.jpg')
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{LANGS[lang]}wheels/{k}/", "name": f"{w['b']} {w['n']}"} for i, (k, w) in enumerate(sel.items())]
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": h1, "itemListElement": items[:500]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n</head>\n<body>\n'
    out += header(lang, alts)
    p = '/' + LANGS[lang]
    crumbs = f'<a href="{p}">Nordvelg</a><span>/</span>'
    crumbs += (f'<a href="{p}wheels/">{t["catalog"]}</a><span>/</span><span aria-current="page">{esc(brand)}</span>' if brand else f'<span aria-current="page">{t["catalog"]}</span>')
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs">{crumbs}</nav>\n<section class="cathead"><h1>{esc(h1)}</h1><p>{t["cat_sub"]}</p></section>\n'
    brands = []
    for w in sel.values():
        if w['b'] not in brands:
            brands.append(w['b'])
    for b in brands:
        bw = [w for w in sel.values() if w['b'] == b]
        filt = ''
        if brand and b == 'BC Forged':
            series = sorted({w.get('series') for w in bw if w.get('series')})
            opts = ''.join(f'<option value="{esc(x)}">{esc(t["series"].format(s=x))}</option>' for x in series)
            filt = (f'<div class="filters" role="group"><button type="button" class="on" data-f="">{t["filt_all"]}</button>'
                    f'<button type="button" data-f="mono">{t["mono"]}</button><button type="button" data-f="two">{t["two"]}</button>'
                    f'<select aria-label="{t["series"].format(s="")}"><option value="">{t["filt_all"]}</option>{opts}</select></div>')
        show = bw if brand else bw[:8]
        more = '' if brand else f'<a href="{p}wheels/brand/{bslug(b)}/">{t["all_brand"].format(b=b, n=len(bw))}</a>'
        head = f'<h2>{esc(b)}</h2>' if brand else f'<div class="rh"><h2>{esc(b)}</h2>{more}</div>'
        out += f'<section class="rel" data-brand="{esc(b)}">{head}{filt}<div class="grid">{"".join(card(w, lang) for w in show)}</div>'
        if not brand and len(bw) > 8:
            out += f'<p style="margin-top:18px"><a class="btn ghost" href="{p}wheels/brand/{bslug(b)}/">{t["all_brand"].format(b=b, n=len(bw))}</a></p>'
        out += '</section>\n'
    out += '</main>\n' + footer(lang) + f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return out

def main():
    allpages = []
    for lang in LANGS:
        wheels, _ = collect(lang)
        # featured first, then by brand
        order = sorted(wheels.items(), key=lambda kv: (not kv[1]['featured'], kv[1]['b'] != 'BC Forged', kv[1]['b'], kv[1]['n']))
        wheels = dict((k, w) for k, w in order if w['imgs'])
        base = os.path.join(ROOT, LANGS[lang], 'wheels')
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, 'index.html'), 'w').write(catalog(lang, wheels))
        for b in sorted({w['b'] for w in wheels.values()}):
            os.makedirs(os.path.join(base, 'brand', bslug(b)), exist_ok=True)
            open(os.path.join(base, 'brand', bslug(b), 'index.html'), 'w').write(catalog(lang, wheels, b))
        for k, d in wheels.items():
            os.makedirs(os.path.join(base, k), exist_ok=True)
            open(os.path.join(base, k, 'index.html'), 'w').write(page(k, d, lang, wheels))
        allpages.append((lang, list(wheels.keys()) + ['brand/' + bslug(b) for b in sorted({w['b'] for w in wheels.values()})]))
        print(lang, len(wheels), 'models')
    json.dump({l: ks for l, ks in allpages}, open(os.path.join(ROOT, 'tools/wheels.json'), 'w'), indent=1)

if __name__ == '__main__':
    main()
