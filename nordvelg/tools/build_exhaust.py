"""Страницы выхлопных систем iPE: /exhaust/<slug>/, каталог /exhaust/ и страницы марок /exhaust/<make>/ на трёх языках.

Источник: tools/shop_items.json (kind == 'exhaust'), выгрузка магазина Baan Velgen.
Цены у Baan за изделие с НДС Нидерландов 21%; показываем с эстонским НДС 24%.
Версии без катализатора (cat bypass, catless) не продаём: в Эстонии с ними не пройти техосмотр.
"""
import json, os, re, urllib.parse
import build_wheels as W

ROOT, SITE, LANGS, esc, V = W.ROOT, W.SITE, W.LANGS, W.esc, W.V
SHOP = [i for i in W.SHOP if i['kind'] == 'exhaust']
MAKES = ['Porsche', 'Ferrari', 'Lamborghini', 'McLaren', 'Mercedes-AMG', 'Mercedes', 'BMW', 'Audi', 'Aston Martin', 'Bentley',
         'Rolls-Royce', 'Maserati', 'Toyota', 'Nissan', 'Ford', 'Chevrolet', 'Lexus', 'Honda', 'Hyundai', 'Volkswagen', 'VW', 'Tesla',
         'Alfa Romeo', 'Jaguar', 'Land Rover', 'Range Rover', 'Cadillac', 'Dodge', 'Mini', 'Subaru', 'Mazda', 'Volvo', 'Infiniti', 'Kia',
         'Genesis', 'Lotus', 'Cupra', 'Seat', 'Jeep', 'Ram', 'Corvette', 'Abarth', 'Fiat', 'Peugeot', 'Renault']
ALIAS = {'Mercedes': 'Mercedes-AMG', 'VW': 'Volkswagen', 'Range Rover': 'Land Rover', 'Corvette': 'Chevrolet'}
BAD = re.compile(r'bypass|catless|without cats|de-?cat|race pipe', re.I)
TYPES = [  # (pattern, ru, et, en)
    (r'equal-?length header', 'Равнодлинный коллектор', 'Võrdse pikkusega kollektor', 'Equal-length headers'),
    (r'full (exhaust|system)|exhaust system', 'Выхлопная система', 'Väljalaskesüsteem', 'Exhaust system'),
    (r'cat-?back', 'Выхлоп cat-back', 'Cat-back väljalaskesüsteem', 'Cat-back exhaust'),
    (r'down ?pipe', 'Даунпайпы', 'Downpipe’id', 'Downpipes'),
    (r'link pipe', 'Соединительные трубы', 'Ühendustorud', 'Link pipes'),
    (r'header', 'Выпускной коллектор', 'Väljalaskekollektor', 'Headers'),
    (r'x-?pipe', 'X-труба', 'X-toru', 'X-pipe'),
    (r'cat (bypass )?pipe', 'Трубы с катализаторами', 'Katalüsaatoritega torud', 'Cat pipes'),
    (r'front pipe|mid pipe', 'Передняя труба', 'Esitoru', 'Front pipe'),
    (r'muffler|rear section|back box', 'Глушитель', 'Summuti', 'Muffler'),
    (r'tip', 'Насадки', 'Otsikud', 'Tips'),
]
T = {
 'ru': dict(sec='Выхлоп iPE', cat_title='Выхлопные системы iPE в Таллинне: цены | Nordvelg',
            cat_desc='Титановые и стальные выхлопные системы iPE с клапанным управлением под заказ: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Цены с НДС, доставка по Эстонии, в Латвию, Литву и Финляндию.',
            cat_h1='Выхлопные системы iPE', cat_sub='Оригинальные системы iPE через европейского дистрибьютора. Продаём только версии с катализатором: без катализатора машину в Эстонии на техосмотре не пропустят',
            make_title='Выхлоп iPE для {m}: все системы и цены | Nordvelg', make_desc='Выхлопные системы iPE для {m} под заказ с доставкой по Эстонии, в Латвию, Литву и Финляндию. Цены с НДС, только версии с катализатором.', make_h1='Выхлоп iPE для {m}',
            h1='{t} iPE для {car}', title='{t} iPE для {car}: цена в Таллинне | Nordvelg', desc='{t} iPE для {car}, {mat}. Клапанное управление звуком, доставка по Эстонии, в Латвию, Литву и Финляндию.{price}',
            mat_ti='титан', mat_ss='нержавеющая сталь', finishes='Отделка насадок', all='Все системы iPE', more='Другие системы для {m}', all_make='Все системы для {m}: {n}',
            facts=['Клапанная система: тихо в городе, громко по кнопке', 'Только версии с катализатором, как требует техосмотр', 'Точную комплектацию, срок и цену подтверждаем до оплаты', 'Доставляем по Эстонии, в Латвию, Литву и Финляндию, с установкой подскажем'],
            note='цена с НДС и доставкой по Эстонии, точную сумму подтвердим под вашу комплектацию. Доставку в Латвию, Литву и Финляндию посчитаем вместе с ценой', req='Версию с катализатором считаем по запросу', other='Другие', filt='Марка',
            vid='Как звучит iPE: видео производителя', play='Смотреть видео', vnote='Ролик с YouTube-канала iPE. Плеер YouTube загрузится, только когда вы нажмёте на видео.'),
 'et': dict(sec='iPE väljalaskesüsteemid', cat_title='iPE väljalaskesüsteemid Tallinnas: hinnad | Nordvelg',
            cat_desc='iPE klappidega väljalaskesüsteemid titaanist ja roostevabast terasest, tellimusel: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Hinnad koos käibemaksuga, tarne Eestis ning Lätti, Leetu ja Soome.',
            cat_h1='iPE väljalaskesüsteemid', cat_sub='Originaalsed iPE süsteemid Euroopa turustaja kaudu. Müüme ainult katalüsaatoriga versioone: ilma katalüsaatorita ei läbi auto Eestis tehnoülevaatust',
            make_title='iPE väljalase {m} autodele: kõik süsteemid ja hinnad | Nordvelg', make_desc='iPE väljalaskesüsteemid {m} autodele tellimusel tarnega Eestis ning Lätti, Leetu ja Soome. Hinnad koos käibemaksuga, ainult katalüsaatoriga versioonid.', make_h1='iPE väljalaskesüsteemid {m} autodele',
            h1='{t} iPE autole {car}', title='{t} iPE autole {car}: hind Tallinnas | Nordvelg', desc='{t} iPE autole {car}, {mat}. Klappidega helijuhtimine, tarne Eestis ning Lätti, Leetu ja Soome.{price}',
            mat_ti='titaan', mat_ss='roostevaba teras', finishes='Otsikute viimistlus', all='Kõik iPE süsteemid', more='Teised süsteemid: {m}', all_make='Kõik {m} süsteemid: {n}',
            facts=['Klappidega süsteem: linnas vaikne, nupuvajutusega vali', 'Ainult katalüsaatoriga versioonid, nagu nõuab tehnoülevaatus', 'Täpse komplekti, tähtaja ja hinna kinnitame enne makset', 'Tarne Eestis ning Lätti, Leetu ja Soome, paigalduse osas aitame nõuga'],
            note='hind koos käibemaksu ja tarnega Eestis, täpse summa kinnitame teie komplekti järgi. Tarne hinna Lätti, Leetu ja Soome ütleme koos pakkumisega', req='Katalüsaatoriga versiooni hind päringu alusel', other='Muud', filt='Mark',
            vid='Kuidas iPE kõlab: tootja video', play='Vaata videot', vnote='Video iPE YouTube’i kanalilt. YouTube’i mängija laaditakse alles siis, kui video peale vajutate.'),
 'en': dict(sec='iPE exhausts', cat_title='iPE Exhaust Systems in Tallinn: Prices | Nordvelg',
            cat_desc='Titanium and stainless iPE valvetronic exhaust systems made to order: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Prices incl. VAT, delivery to Estonia, Latvia, Lithuania and Finland.',
            cat_h1='iPE exhaust systems', cat_sub='Genuine iPE systems through a European distributor. We sell catted versions only: without catalytic converters a car fails the Estonian inspection',
            make_title='iPE exhaust for {m}: all systems and prices | Nordvelg', make_desc='iPE exhaust systems for {m} made to order with delivery to Estonia, Latvia, Lithuania and Finland. Prices incl. VAT, catted versions only.', make_h1='iPE exhaust for {m}',
            h1='iPE {t} for {car}', title='iPE {t} for {car}: price in Tallinn | Nordvelg', desc='iPE {t} for {car}, {mat}. Valve-controlled sound, delivery to Estonia, Latvia, Lithuania and Finland.{price}',
            mat_ti='titanium', mat_ss='stainless steel', finishes='Tip finishes', all='All iPE systems', more='More systems for {m}', all_make='All {m} systems: {n}',
            facts=['Valvetronic system: quiet in town, loud at the press of a button', 'Catted versions only, as the Estonian inspection requires', 'Exact configuration, lead time and price confirmed before you pay', 'Delivery to Estonia, Latvia, Lithuania and Finland; we can advise on fitting'],
            note='incl. VAT and delivery within Estonia, exact total confirmed for your configuration. Delivery to Latvia, Lithuania or Finland is quoted with the price', req='Catted version priced on request', other='Other', filt='Make',
            vid='How iPE sounds: a video from the maker', play='Play video', vnote='From the iPE YouTube channel. The YouTube player loads only when you press play.'),
}

# Suomi (fi): nimet erikseen tavallisena ja titaanisena, jotta adjektiivi taipuu oikein (titaaninen pakoputkisto, titaaniset downpipet)
TYPES_FI = {
    r'equal-?length header': ('tasapituiset pakosarjat', 'titaaniset tasapituiset pakosarjat'),
    r'full (exhaust|system)|exhaust system': ('pakoputkisto', 'titaaninen pakoputkisto'),
    r'cat-?back': ('cat-back-pakoputkisto', 'titaaninen cat-back-pakoputkisto'),
    r'down ?pipe': ('downpipet', 'titaaniset downpipet'),
    r'link pipe': ('liitosputket', 'titaaniset liitosputket'),
    r'header': ('pakosarjat', 'titaaniset pakosarjat'),
    r'x-?pipe': ('X-putki', 'titaaninen X-putki'),
    r'cat (bypass )?pipe': ('katalysaattoriputket', 'titaaniset katalysaattoriputket'),
    r'front pipe|mid pipe': ('etuputki', 'titaaninen etuputki'),
    r'muffler|rear section|back box': ('äänenvaimennin', 'titaaninen äänenvaimennin'),
    r'tip': ('pakoputken päätteet', 'titaaniset pakoputken päätteet'),
}
T['fi'] = dict(sec='iPE-pakoputkistot', cat_title='iPE-pakoputkistot tilauksesta: hinnat ja toimitus Suomeen | Nordvelg',
            cat_desc='Titaaniset ja ruostumattomat iPE-pakoputkistot venttiiliohjauksella tilauksesta: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Hinnat sis. ALV:n, toimitus myös Suomeen.',
            cat_h1='iPE-pakoputkistot', cat_sub='Aidot iPE-tuotteet eurooppalaisen jakelijan kautta. Myymme vain katalysaattorillisia versioita: ilman katalysaattoria auto ei mene katsastuksesta läpi',
            make_title='iPE-pakoputkistot, {m}: kaikki järjestelmät ja hinnat | Nordvelg', make_desc='iPE-pakoputkistot tilauksesta, merkki {m}. Hinnat sis. ALV:n, vain katalysaattorilliset versiot, toimitus myös Suomeen.', make_h1='iPE-pakoputkistot: {m}',
            h1='iPE {t}, {car}', title='iPE {t}, {car}: hinta | Nordvelg', desc='iPE {t}, {car}, {mat}. Venttiiliohjattu ääni, toimitus Suomeen, Viroon, Latviaan ja Liettuaan.{price}',
            mat_ti='titaani', mat_ss='ruostumaton teräs', finishes='Pakoputken päätteiden viimeistely', all='Kaikki iPE-järjestelmät', more='Muut järjestelmät: {m}', all_make='{m}: kaikki järjestelmät ({n})',
            facts=['Venttiiliohjattu pakoputkisto: hiljainen kaupungissa, äänekäs napin painalluksella', 'Vain katalysaattorilliset versiot, kuten katsastus edellyttää', 'Tarkan kokoonpanon, toimitusajan ja hinnan vahvistamme ennen maksua', 'Toimitus Suomeen, Viroon, Latviaan ja Liettuaan, ja neuvomme myös asennuksessa'],
            note='hinta sis. ALV:n ja toimituksen Virossa, tarkan summan vahvistamme kokoonpanosi mukaan. Toimituksen Suomeen, Latviaan tai Liettuaan hinnoittelemme tarjouksen yhteydessä', req='Katalysaattorillisen version hinta pyynnöstä', other='Muut', filt='Merkki',
            vid='Kuuntele iPE:n ääni', play='Katso video', vnote='Video on iPE:n omalta YouTube-kanavalta. YouTube-soitin latautuu vasta, kun painat videota.')

def mk(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def parse(it):
    title = re.sub(r'^\s*ipe\s+', '', it['title'], flags=re.I).strip()
    m = re.search(r'\bfor\s+(.+)$', title, re.I) or re.search(r'[–-]\s+(.+)$', title)
    car = (m.group(1) if m else title).strip()
    car = re.sub(r'\s+(in|with)$', '', car)
    make = next((ALIAS.get(x, x) for x in MAKES if re.search(r'\b' + re.escape(x) + r'\b', car, re.I)), None)
    tlow = it['title'].lower()
    typ = next((tt for tt in TYPES if re.search(tt[0], tlow)), TYPES[0])
    mat = 'ti' if 'titanium' in tlow else 'ss'
    good = [float(p) for v, p in it['variants'] if p and float(p) > 0 and not BAD.search(v)]
    price = W.setp(min(good) / 1.21 / 4) if good else None
    fin = []
    for v, _ in it['variants']:
        for part in re.split(r'\s*/\s*|\s*\|\s*', v):
            part = re.sub(r'\s*\(standard\)', '', part).strip()
            if re.search(r'chrome|titanium (blue|gold|polished|chrome)|carbon|satin|gold|black', part, re.I) and len(part) < 40 and part not in fin:
                fin.append(part)
    return dict(car=car, make=make or T['en']['other'], typ=typ, mat=mat, p=price, fin=fin[:8])

_best = {}
for it in SHOP:  # в магазине есть дубли с одинаковым названием: оставляем вариант с большим числом опций
    k = it['title'].strip().lower()
    if k not in _best or len(it['variants']) > len(_best[k]['variants']):
        _best[k] = it
SHOP = [it for it in SHOP if _best[it['title'].strip().lower()] is it]
ITEMS = []
for it in SHOP:
    local = [f"/img/shop/{x}-960.webp" for x in it['local'] if ('shop/' + x) in W.MAN]
    if not local:
        continue
    d = parse(it); d.update(slug=mk(re.sub(r'-\d+$', '', it['handle'].replace('ipe-', '', 1))), imgs=local, title=it['title'])
    d['slug'] = d['slug'].replace('cat-bypass-pipes', 'cat-pipes').replace('bypass-', '')
    ed = re.search(r'\b(F1 Sound|Evolution)\b', it['title'])
    d['ed'] = ed.group(1) if ed else ''
    ITEMS.append(d)
_seen = set()
for d in ITEMS:  # уникальные адреса
    base, n = d['slug'], 2
    while d['slug'] in _seen:
        d['slug'] = f"{base}-{n}"; n += 1
    _seen.add(d['slug'])
ITEMS.sort(key=lambda d: (MAKES.index(d['make']) if d['make'] in MAKES else 99, d['car']))

def names(d, lang):
    t = T[lang]
    if lang == 'fi':
        tl = TYPES_FI[d['typ'][0]][1 if d['mat'] == 'ti' else 0] + (' ' + d['ed'] if d['ed'] else '')
        return t['h1'].format(t=tl, car=d['car']), tl
    tl = {'ru': d['typ'][1], 'et': d['typ'][2], 'en': d['typ'][3].lower()}[lang]
    if d['ed']:
        tl += ' ' + d['ed']
    if d['mat'] == 'ti':
        tl = {'ru': tl + ' из титана', 'et': 'Titaanist ' + tl[0].lower() + tl[1:], 'en': 'titanium ' + tl}[lang]
    return t['h1'].format(t=tl, car=d['car']), tl

header = W.header

# Официальные ролики iPE с YouTube (tools/ipe_videos.json). Встраиваем только с YouTube, сами ролики не загружаем.
# До клика грузится только превью с i.ytimg.com, плеер youtube-nocookie.com подключается по нажатию.
VIDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ipe_videos.json')))
VID_BY_ID = {v['id']: v for v in VIDS['videos']}

def video_for(d):
    return next((v for v in VIDS['videos'] if re.search(v['match'], d['car'], re.I)), None)

VID_CSS = ('<style>.vid{padding-block:8px 48px;max-width:880px}.vid h2{font-size:clamp(22px,2.4vw,28px);margin-bottom:14px}'
           '.yt{position:relative;aspect-ratio:16/9;border-radius:20px;overflow:hidden;background:var(--ink)}'
           '.yt a,.yt iframe{position:absolute;inset:0;width:100%;height:100%;border:0;display:block}'
           '.yt img{width:100%;height:100%;object-fit:cover;opacity:.92;transition:opacity .2s}.yt a:hover img,.yt a:focus-visible img{opacity:1}'
           '.yt .pl{position:absolute;left:50%;top:50%;width:76px;height:76px;margin:-38px 0 0 -38px;border-radius:50%;background:rgba(18,20,23,.78);display:grid;place-items:center;transition:background .2s}'
           '.yt a:hover .pl,.yt a:focus-visible .pl{background:var(--bronze)}.yt .pl svg{width:28px;height:28px;margin-left:4px;fill:var(--alloy)}'
           '.yt a:focus-visible{outline:3px solid var(--bronze-l);outline-offset:-3px}'
           '.vcap{font-size:14px;color:var(--machined);margin-top:10px}.vcap b{font-weight:500;color:var(--graphite)}'
           '@media (prefers-reduced-motion:reduce){.yt img,.yt .pl{transition:none}}</style>\n')
VID_JS = ("<script>document.querySelectorAll('.yt a[data-id]').forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();"
          "var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+a.dataset.id+'?autoplay=1&rel=0&playsinline=1';"
          "f.title=a.dataset.t;f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen';f.allowFullscreen=true;"
          "f.referrerPolicy='strict-origin-when-cross-origin';a.replaceWith(f);f.focus()})})</script>\n")

def video_block(v, lang):
    t = T[lang]
    vid, ttl = v['id'], esc(v['title'])
    return (f'<section class="vid" aria-labelledby="vid-h"><h2 id="vid-h">{t["vid"]}</h2>'
            f'<div class="yt"><a href="https://www.youtube.com/watch?v={vid}" data-id="{vid}" data-t="{ttl}" target="_blank" rel="noopener noreferrer" aria-label="{t["play"]}: {ttl}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" width="480" height="360" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            f'<span class="pl" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span></a></div>'
            f'<p class="vcap"><b>{ttl}</b> · YouTube, iPE</p><p class="vcap">{t["vnote"]}</p></section>\n')

def card(d, lang):
    h1, _ = names(d, lang)
    w, hgt = W.dims(d['imgs'][0])
    price = W.fmt(d['p'], lang) if d['p'] else W.T[lang]['on_request']
    return (f'<a class="card" data-make="{esc(d["make"])}" href="/{LANGS[lang]}exhaust/{d["slug"]}/"><div class="stage"><img src="{d["imgs"][0]}" width="{w}" height="{hgt}" loading="lazy" decoding="async" alt="{esc(h1)}"></div>'
            f'<span class="brand">iPE</span><h3>{esc(d["car"])}</h3><div class="spec"><span>{esc(names(d, lang)[1])}</span></div><div class="price">{price}</div></a>')

def page(d, lang):
    t, wt = T[lang], W.T[lang]
    h1, tl = names(d, lang)
    alts = {l: f"{SITE}/{LANGS[l]}exhaust/{d['slug']}/" for l in LANGS}
    url = alts[lang]
    mat = t['mat_ti'] if d['mat'] == 'ti' else t['mat_ss']
    car_t = d['car'].replace(' / ', '/')
    h1t = t['h1'].format(t=tl, car=car_t)
    title = W.fit(t['title'].format(t=tl, car=car_t), h1t if len(h1t) <= 65 else f"iPE {car_t}: {tl[0].lower() + tl[1:] if lang not in ('en', 'fi') else tl}")
    desc = t['desc'].format(t=tl, car=d['car'], mat=mat, price=(' ' + W.fmt(d['p'], lang)[:1].upper() + W.fmt(d['p'], lang)[1:] + '.') if d['p'] else '')
    og = SITE + W.big(d['imgs'][0])
    out = W.head_common(lang, title, desc, url, alts, og)
    prod = {"@type": "Product", "name": f"iPE {d['title']}", "brand": {"@type": "Brand", "name": "iPE"}, "image": [SITE + W.big(i) for i in d['imgs']], "url": url, "description": desc}
    if d['p']:
        prod['offers'] = W.offer(d['p'], url, 'iPE', W.SHIP_EXHAUST)
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nordvelg", "item": f"{SITE}/{LANGS[lang]}"},
        {"@type": "ListItem", "position": 2, "name": t['sec'], "item": f"{SITE}/{LANGS[lang]}exhaust/"},
        {"@type": "ListItem", "position": 3, "name": h1, "item": url}]}
    v = video_for(d)
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": ([prod] if d['p'] else []) + [crumbs]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n' + (VID_CSS if v else '') + '</head>\n<body>\n'
    out += header(lang, alts)
    p = '/' + LANGS[lang]
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs"><a href="{p}">Nordvelg</a><span>/</span><a href="{p}exhaust/">{t["sec"]}</a><span>/</span><span aria-current="page">{esc(d["car"])}</span></nav>\n'
    gal = ''.join(f'<button type="button" class="shot{" on" if n == 0 else ""}" data-big="{W.big(i)}" aria-label="{wt["zoom"]}"><img src="{i}" width="{W.dims(i)[0]}" height="{W.dims(i)[1]}" alt="{esc(h1)}" {"fetchpriority=\"high\"" if n == 0 else "loading=\"lazy\""} decoding="async"></button>' for n, i in enumerate(d['imgs']))
    thumbs = ('<div class="thumbs">' + ''.join(f'<button type="button" data-i="{n}" aria-label="{n+1}"{" class=\"on\"" if n == 0 else ""}><img src="{i}" alt="" loading="lazy" decoding="async"></button>' for n, i in enumerate(d['imgs'])) + '</div>') if len(d['imgs']) > 1 else ''
    price = (f'<div class="price">{W.fmt(d["p"], lang)}</div><p class="pnote">{t["note"]}</p>' if d['p'] else f'<div class="price">{wt["on_request"]}</div><p class="pnote">{t["req"]}</p>')
    name = f"iPE {d['title']}"
    wa = 'https://wa.me/' + W.WA + '?text=' + urllib.parse.quote(wt['wa_text'].format(name=name))
    fin = f'<h2>{t["finishes"]}</h2><div class="chips">{"".join(f"<span>{esc(x)}</span>" for x in d["fin"])}</div>' if d['fin'] else ''
    out += f'''<section class="prod">
<div class="gallery"><div class="main">{gal}</div>{thumbs}<p class="hint">{wt['zoom']}</p></div>
<div class="info">
<div class="brand">iPE</div>
<h1>{esc(h1)}</h1>
<div class="spec"><span>{esc(tl)}</span><span>{esc(mat)}</span></div>
{price}
<div class="ctas"><a class="btn" href="{p}?model={urllib.parse.quote(name[:60])}#quote">{wt['cta']}</a><a class="btn ghost" href="{wa}" target="_blank" rel="noopener noreferrer">{wt['wa']}</a></div>
<h2>{wt['know']}</h2>
<ul class="facts">{''.join(f'<li>{x}</li>' for x in t['facts'])}</ul>
{fin}
</div>
</section>
''' + (video_block(v, lang) if v else '')
    rel = [x for x in ITEMS if x['make'] == d['make'] and x is not d][:4]
    out += f'<section class="rel"><div class="rh"><h2>{t["more"].format(m=d["make"])}</h2><a href="{p}exhaust/{mk(d["make"])}/">{t["all"]}</a></div><div class="grid">{"".join(card(x, lang) for x in rel)}</div></section>\n</main>\n' if rel else '</main>\n'
    out += f'<div class="lb" hidden><button type="button" class="x" aria-label="{wt["close"]}">×</button></div>\n' + W.footer(lang) + (VID_JS if v else '')
    out += f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return W.fi_fix(out) if lang == 'fi' else out

def catalog(lang, make=None):
    t = T[lang]
    sub = f"exhaust/{mk(make)}/" if make else "exhaust/"
    alts = {l: f"{SITE}/{LANGS[l]}{sub}" for l in LANGS}
    sel = [d for d in ITEMS if make is None or d['make'] == make]
    title = W.fit(t['make_title'].format(m=make) if make else t['cat_title'])
    desc = t['make_desc'].format(m=make) if make else t['cat_desc']
    h1 = t['make_h1'].format(m=make) if make else t['cat_h1']
    out = W.head_common(lang, title, desc, alts[lang], alts, SITE + W.big(sel[0]['imgs'][0]))
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{LANGS[lang]}exhaust/{d['slug']}/", "name": names(d, lang)[0]} for i, d in enumerate(sel)]
    v = VID_BY_ID.get(VIDS['makes'].get(make) if make else VIDS['brand'])
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": h1, "itemListElement": items}, ensure_ascii=False, separators=(',', ':')) + '</script>\n' + (VID_CSS if v else '') + '</head>\n<body>\n'
    out += header(lang, alts)
    p = '/' + LANGS[lang]
    crumbs = f'<a href="{p}">Nordvelg</a><span>/</span>' + (f'<a href="{p}exhaust/">{t["sec"]}</a><span>/</span><span aria-current="page">{esc(make)}</span>' if make else f'<span aria-current="page">{t["sec"]}</span>')
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs">{crumbs}</nav>\n<section class="cathead"><h1>{esc(h1)}</h1><p>{t["cat_sub"]}</p></section>\n'
    makes = []
    for d in sel:
        if d['make'] not in makes:
            makes.append(d['make'])
    if not make:
        out += '<div class="chips makes">' + ''.join(f'<a href="{p}exhaust/{mk(m)}/">{esc(m)} <b>{sum(1 for d in ITEMS if d["make"] == m)}</b></a>' for m in makes) + '</div>\n'
    for m in makes:
        mm = [d for d in sel if d['make'] == m]
        show = mm if make else mm[:8]
        head = '' if make else f'<div class="rh"><h2>{esc(m)}</h2><a href="{p}exhaust/{mk(m)}/">{t["all_make"].format(m=m, n=len(mm))}</a></div>'
        out += f'<section class="rel">{head}<div class="grid">{"".join(card(d, lang) for d in show)}</div></section>\n'
    if v:
        out += video_block(v, lang)
    out += '</main>\n' + W.footer(lang) + (VID_JS if v else '') + f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return W.fi_fix(out) if lang == 'fi' else out

def main():
    paths = ['exhaust/']
    for lang in LANGS:
        base = os.path.join(ROOT, LANGS[lang], 'exhaust')
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, 'index.html'), 'w').write(catalog(lang))
        for m in sorted({d['make'] for d in ITEMS}):
            os.makedirs(os.path.join(base, mk(m)), exist_ok=True)
            open(os.path.join(base, mk(m), 'index.html'), 'w').write(catalog(lang, m))
            if LANGS[lang] == '':
                paths.append(f'exhaust/{mk(m)}/')
        for d in ITEMS:
            os.makedirs(os.path.join(base, d['slug']), exist_ok=True)
            open(os.path.join(base, d['slug'], 'index.html'), 'w').write(page(d, lang))
            if LANGS[lang] == '':
                paths.append(f'exhaust/{d["slug"]}/')
    json.dump(paths, open(os.path.join(ROOT, 'tools/exhaust.json'), 'w'), indent=0)
    print(len(ITEMS), 'exhaust items,', len(paths), 'paths per language,', sum(1 for d in ITEMS if video_for(d)), 'system pages with an iPE video')

if __name__ == '__main__':
    main()
