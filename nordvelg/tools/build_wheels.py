"""Генерирует страницы моделей дисков /wheels/<slug>/ и каталог /wheels/ на трёх языках.

Источник данных: блок «Модели» (.cat) и подбор по машине (var DATA) в index.html каждой языковой версии.
Запуск: python3 nordvelg/tools/build_wheels.py (после правок главных страниц).
"""
import html, json, os, re, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://nordvelg.com'
LANGS = {'en': '', 'et': 'et/', 'ru': 'ru/', 'fi': 'fi/'}
WA = '37257494989'
import hashlib
V = lambda p: hashlib.md5(open(os.path.join(ROOT, p), 'rb').read()).hexdigest()[:8]
MAN = json.load(open(os.path.join(ROOT, 'tools/images-manifest.json')))['images']
for _f in ('tools/bc-manifest.json', 'tools/shop-manifest.json'):
    if os.path.exists(os.path.join(ROOT, _f)):
        MAN.update(json.load(open(os.path.join(ROOT, _f))))
SHOP = json.load(open(os.path.join(ROOT, 'tools/shop_items.json')))
bslug = lambda b: re.sub(r'[^a-z0-9]+', '-', b.lower()).strip('-')
BRANDS = {'BC Forged', 'Brixton Forged', 'iPE'}  # остальные бренды сняты 16.10.2026: нет дилерской цены
BC = json.load(open(os.path.join(ROOT, 'tools/bc_models.json')))
# Откуда скачано каждое фото (имя в img/ -> исходный адрес). С 28.10.2026 дистрибьютор письменно разрешил фото
# с bcforged.com.tw и brixtonforged.com; на приоритетных моделях показываем только их, без фото поставщика
_J = lambda f: json.load(open(os.path.join(ROOT, 'tools', f)))
SRC = {k: v['download'] for k, v in _J('images.json').items()}
SRC.update({'bc/' + k: v for k, v in _J('bc_images.json').items()})
SRC.update({'shop/' + k: v for k, v in _J('shop_images.json').items()})
OFFICIAL = re.compile(r'https://(www\.)?(bcforged\.com\.tw|brixtonforged\.com)/')
PRIORITY = {'bc-forged-kl01', 'bc-forged-hca197', 'bc-forged-hca197s', 'bc-forged-th09', 'bc-forged-kl52', 'bc-forged-rz25',
            'bc-forged-af55', 'bc-forged-eh361', 'brixton-forged-fde11', 'brixton-forged-pf9-carbon'}
PRICE = {'mono': {18: 960, 19: 960, 20: 1066, 21: 1188, 22: 1250, 23: 1390}, 'KX': {19: 1255, 20: 1376, 21: 1528, 22: 1630},
         'two': {18: 1216, 19: 1216, 20: 1322, 21: 1444, 22: 1506, 23: 1646}, 'HCX': {19: 1551, 20: 1667, 21: 1849, 22: 1911}}
setp = lambda p: int(round(p * 4 * 1.24 / 10) * 10)

T = {
 'ru': dict(
  catalog='Каталог', home='Главная', pick='Подбор по машине', faq='Вопросы',
  cat_title='Каталог кованых дисков BC Forged и Brixton под заказ | Nordvelg',
  cat_desc='Кованые диски BC Forged и Brixton Forged под заказ с доставкой в Эстонию, Латвию, Литву и Финляндию. Цены с НДС, подбор под вашу машину.',
  cat_h1='Каталог кованых дисков', cat_sub='Наша подборка моделей. Любую из них делают под вашу машину: диаметр, ширина, вылет и отделка на выбор',
  title='{name}: кованые диски под заказ в Таллинне | Nordvelg',
  desc='{name} под ваш автомобиль: подбор размера и вылета, эскиз до оплаты, доставка в Эстонию, Латвию, Литву и Финляндию.{price}',
  price_from='от {p} €', set_note='за комплект из 4 дисков, с НДС и доставкой в Эстонию, Латвию, Литву или Финляндию', est_note='ориентировочная цена, точную назовём после подбора',
  on_request='Цена по запросу', cta='Рассчитать для моей машины', wa='Спросить в WhatsApp',
  wa_text='Здравствуйте, интересуют диски {name}. Машина: ',
  fits='Подходит для', fits_note='Эти машины уже есть в нашем подборе. Для других моделей проверим посадку бесплатно',
  know='Что важно знать', how='Как проходит заказ', more='Другие модели {brand}', all='Весь каталог',
  zoom='Нажмите, чтобы увеличить', close='Закрыть',
  steps=['Вы присылаете марку, модель и год машины', 'Мы подбираем размер, вылет и отделку и присылаем эскиз', 'Вы вносите 50% предоплаты, завод изготавливает диски', 'Вы оплачиваете остаток, и диски едут к вам в Эстонию, Латвию, Литву или Финляндию'],
  bc=['Кованая заготовка из алюминия 6061-T6, каждый диск фрезеруют под вашу машину: разболтовка, центральное отверстие и вылет', 'Диски прошли японские испытания на прочность JWL и VIA', 'Около 40 вариантов отделки, можно сочетать две', 'Изготовление 4-6 недель, затем доставка в Эстонию, Латвию, Литву или Финляндию'],
  brixton=['Американский бренд, каждый комплект собирают под конкретный автомобиль', 'Производство 7-10 недель', 'Цену считаем по вашей спецификации: размер, ширина, отделка', 'Доставка в Эстонию, Латвию, Литву и Финляндию входит в цену'],
  other=['Заказываем через европейского дистрибьютора', 'Срок и точную цену подтверждаем после подбора под вашу машину', 'Доставка в Эстонию, Латвию, Литву и Финляндию входит в цену'],
  pay='Подбор бесплатный: сначала эскиз и точная цена, потом решение',
  per_wheel='', mono='моноблок', two='двухсоставной',
  foot='Кованые диски BC Forged, Brixton Forged и MV Forged под заказ в Таллинне', city='Таллинн, Эстония',
  credits='Фото дисков и автомобилей: BC Forged, Brixton Forged и их дистрибьюторы. Названия брендов принадлежат их владельцам',
  ptable='Цена комплекта по диаметру', col_d='Диаметр', col_w='Ширина', col_p='Комплект из 4', ptable_note='С НДС и доставкой в Эстонию, Латвию, Литву или Финляндию. Опции оплачиваются отдельно: полированная полка, накатка. Фрезерованный центральный колпачок в комплекте', series='Серия {s}', filt_all='Все', sizes_d='Размеры {a}-{b}″.',
  brand_title='Диски {b} под заказ в Таллинне: все модели и цены | Nordvelg', brand_desc='Все модели {b} под заказ с доставкой в Эстонию, Латвию, Литву и Финляндию. Подбор под ваш автомобиль, эскиз до оплаты.', brand_h1='Диски {b}', all_brand='Все модели {b}: {n}', on_req_note='Цену считаем под вашу машину и спецификацию',
  lang_name='Язык', variants='Варианты модели', variants_note='Один дизайн в нескольких исполнениях. Какой вариант подойдёт вашей машине, подскажем при подборе'),
 'et': dict(
  catalog='Kataloog', home='Avaleht', pick='Valik auto järgi', faq='Küsimused',
  cat_title='BC Forged ja Brixton sepistatud veljed tellimusel | Nordvelg',
  cat_desc='Tellimusel valmivad sepistatud veljed tarnega Eestisse, Lätti, Leetu ja Soome: BC Forged ja Brixton Forged. Hinnad koos käibemaksuga, valik teie auto järgi.',
  cat_h1='Sepistatud velgede kataloog', cat_sub='Meie valitud mudelid. Iga komplekt valmib just teie autole: läbimõõt, laius, ET ja viimistlus teie valikul',
  title='{name}: sepistatud veljed tellimusel Tallinnas | Nordvelg',
  desc='{name} teie autole: mõõdu ja ET valik, eskiis enne makset, tarne Eestisse, Lätti, Leetu ja Soome.{price}',
  price_from='alates {p} €', set_note='4 velje komplekt koos käibemaksu ja tarnega Eestisse, Lätti, Leetu või Soome', est_note='ligikaudne hind, täpse hinna ütleme pärast valikut',
  on_request='Hind päringu alusel', cta='Küsi hinda minu autole', wa='Küsi WhatsAppis',
  wa_text='Tere, mind huvitavad {name} veljed. Auto: ',
  fits='Sobib autodele', fits_note='Need autod on meie valikus juba olemas. Teiste mudelite puhul kontrollime sobivust tasuta',
  know='Mida on oluline teada', how='Kuidas tellimine käib', more='Teised {brand} mudelid', all='Kogu kataloog',
  zoom='Suurendamiseks klõpsake', close='Sulge',
  steps=['Saadate auto marga, mudeli ja aasta', 'Valime mõõdu, ET ja viimistluse ning saadame eskiisi', 'Tasute 50% ettemaksu, tehas valmistab veljed', 'Tasute ülejäänud summa ja veljed saadetakse teile Eestisse, Lätti, Leetu või Soome'],
  bc=['Sepistatud toorik alumiiniumisulamist 6061-T6, iga velg freesitakse teie auto järgi: poldimuster, tsentriava ja ET', 'Veljed on läbinud Jaapani tugevustestid JWL ja VIA', 'Umbes 40 viimistlust, kahte saab kombineerida', 'Valmistamine 4-6 nädalat, seejärel tarne Eestisse, Lätti, Leetu või Soome'],
  brixton=['Ameerika bränd, iga komplekt valmib konkreetsele autole', 'Tootmine 7-10 nädalat', 'Hinna arvutame teie spetsifikatsiooni järgi: mõõt, laius, viimistlus', 'Tarne Eestisse, Lätti, Leetu ja Soome on hinna sees'],
  other=['Tellime Euroopa turustaja kaudu', 'Tähtaja ja täpse hinna kinnitame pärast valikut teie auto järgi', 'Tarne Eestisse, Lätti, Leetu ja Soome on hinna sees'],
  pay='Valik on tasuta: kõigepealt eskiis ja täpne hind, siis otsus',
  per_wheel='', mono='monoblokk', two='kaheosaline',
  foot='BC Forged, Brixton Forged ja MV Forged sepistatud veljed tellimusel Tallinnas', city='Tallinn, Eesti',
  credits='Velgede ja autode fotod: BC Forged, Brixton Forged ja nende turustajad. Kaubamärgid kuuluvad nende omanikele',
  ptable='Komplekti hind läbimõõdu järgi', col_d='Läbimõõt', col_w='Laius', col_p='4 velje komplekt', ptable_note='Koos käibemaksu ja tarnega Eestisse, Lätti, Leetu või Soome. Lisavalikud eraldi: poleeritud äär, rihveldus. Freesitud rummukate on komplektis', series='Seeria {s}', filt_all='Kõik', sizes_d='Mõõdud {a}-{b}″.',
  brand_title='{b} veljed tellimusel Tallinnas: kõik mudelid ja hinnad | Nordvelg', brand_desc='Kõik {b} mudelid tellimusel tarnega Eestisse, Lätti, Leetu ja Soome. Valik teie auto järgi, eskiis enne makset.', brand_h1='{b} veljed', all_brand='Kõik {b} mudelid: {n}', on_req_note='Hinna arvutame teie auto ja spetsifikatsiooni järgi',
  lang_name='Keel', variants='Mudeli variandid', variants_note='Üks disain mitmes teostuses. Millise variandi teie autole valida, ütleme valiku käigus'),
 'en': dict(
  catalog='Catalogue', home='Home', pick='Find by car', faq='Questions',
  cat_title='BC Forged and Brixton Forged Wheels Catalogue | Nordvelg',
  cat_desc='Made-to-order forged wheels delivered to Estonia, Latvia, Lithuania and Finland: BC Forged and Brixton Forged. Prices incl. VAT, fitment checked for your car.',
  cat_h1='Forged wheels catalogue', cat_sub='Our pick of models. Each set is made for your car: diameter, width, offset and finish of your choice',
  title='{name}: custom forged wheels in Tallinn | Nordvelg',
  desc='{name} built for your car: size and offset check, a sketch before you pay, delivery to Estonia, Latvia, Lithuania and Finland.{price}',
  price_from='from €{p}', set_note='per set of 4, incl. VAT and delivery to Estonia, Latvia, Lithuania or Finland', est_note='indicative price, exact quote after the fitment check',
  on_request='Price on request', cta='Get a quote for my car', wa='Ask on WhatsApp',
  wa_text='Hello, I am interested in {name} wheels. My car: ',
  fits='Fits', fits_note='These cars are already in our fitment guide. For other models we check fitment for free',
  know='Good to know', how='How ordering works', more='More {brand} models', all='Full catalogue',
  zoom='Click to enlarge', close='Close',
  steps=['You send the make, model and year of your car', 'We choose size, offset and finish and send a sketch', 'You pay a 50% deposit, the factory makes the wheels', 'You pay the balance and the wheels ship to you in Estonia, Latvia, Lithuania or Finland'],
  bc=['Forged 6061-T6 aluminium billet, each wheel machined for your car: bolt pattern, centre bore and offset', 'Tested to the Japanese JWL and VIA strength standards', 'About 40 finishes, two can be combined', 'Made in 4-6 weeks, then delivered to Estonia, Latvia, Lithuania or Finland'],
  brixton=['American brand, each set is built for a specific car', 'Production takes 7-10 weeks', 'We price it from your specification: size, width, finish', 'Delivery to Estonia, Latvia, Lithuania and Finland is included in the price'],
  other=['Ordered through a European distributor', 'Lead time and exact price confirmed after the fitment check', 'Delivery to Estonia, Latvia, Lithuania and Finland is included in the price'],
  pay='The fitment check is free: first a sketch and an exact price, then you decide',
  per_wheel='', mono='monoblock', two='two-piece',
  foot='BC Forged, Brixton Forged and MV Forged wheels made to order in Tallinn', city='Tallinn, Estonia',
  credits='Wheel and car photos: BC Forged, Brixton Forged and their distributors. Brand names belong to their owners',
  ptable='Set price by diameter', col_d='Diameter', col_w='Width', col_p='Set of 4', ptable_note='Incl. VAT and delivery to Estonia, Latvia, Lithuania or Finland. Options are extra: polished lip, knurling. A machined centre cap is included', series='{s} series', filt_all='All', sizes_d='Sizes {a}-{b}″.',
  brand_title='{b} wheels made to order in Tallinn: all models and prices | Nordvelg', brand_desc='All {b} models made to order with delivery to Estonia, Latvia, Lithuania and Finland. Fitment for your car, a sketch before you pay.', brand_h1='{b} wheels', all_brand='All {b} models: {n}', on_req_note='We price it for your car and specification',
  lang_name='Language', variants='Versions of this design', variants_note='One design in several versions. We will tell you which one suits your car during the fitment check'),
}
# Suomi (fi), lisätty 28.10.2026: Suomi on oma kohdemarkkina, vannesarjojen toimitus Suomeen sisältyy hintaan
T['fi'] = dict(
  catalog='Mallisto', home='Etusivu', pick='Auton mukaan', faq='UKK',
  cat_title='Taotut BC Forged- ja Brixton-vanteet tilauksesta | Nordvelg',
  cat_desc='Tilauksesta valmistettavat taotut BC Forged- ja Brixton Forged -vanteet. Toimitus Suomeen, Viroon, Latviaan ja Liettuaan sisältyy hintaan, hinnat sis. ALV:n ja sopivuus tarkistetaan autoosi.',
  cat_h1='Taottujen vanteiden mallisto', cat_sub='Valikoimamme malleja. Jokainen sarja tehdään sinun autoosi: halkaisija, leveys, ET ja viimeistely valintasi mukaan',
  title='{name}: taotut vanteet tilauksesta | Nordvelg',
  desc='{name} sinun autoosi: koon ja ET:n valinta, havainnekuva ennen maksua ja toimitus Suomeen, Viroon, Latviaan tai Liettuaan.{price}',
  price_from='alkaen {p} €', set_note='4 vanteen sarja, sis. ALV:n ja toimituksen Suomeen, Viroon, Latviaan tai Liettuaan', est_note='suuntaa-antava hinta, tarkan hinnan kerromme sopivuuden tarkistuksen jälkeen',
  on_request='Hinta pyynnöstä', cta='Pyydä tarjous autooni', wa='Kysy WhatsAppissa',
  wa_text='Hei, olen kiinnostunut tuotteesta {name}. Autoni: ',
  fits='Sopii autoihin', fits_note='Nämä autot löytyvät jo sovitusoppaastamme. Muihin malleihin tarkistamme sopivuuden maksutta',
  know='Hyvä tietää', how='Näin tilaus etenee', more='Muita {brand} -malleja', all='Koko mallisto',
  zoom='Suurenna klikkaamalla', close='Sulje',
  steps=['Lähetät meille autosi merkin, mallin ja vuosimallin', 'Valitsemme koon, ET:n ja viimeistelyn ja lähetämme havainnekuvan', 'Maksat 50 % ennakkoa, ja tehdas valmistaa vanteet', 'Maksat loppusumman, ja vanteet toimitetaan sinulle Suomeen, Viroon, Latviaan tai Liettuaan'],
  bc=['Taottu aihio alumiinia 6061-T6, ja jokainen vanne jyrsitään autosi mukaan: pulttijako, keskireikä ja ET', 'Läpäisee japanilaiset JWL- ja VIA-lujuustestit', 'Noin 40 viimeistelyä, kahta voi yhdistää', 'Valmistus 4-6 viikkoa, sen jälkeen toimitus Suomeen, Viroon, Latviaan tai Liettuaan'],
  brixton=['Yhdysvaltalainen merkki, jokainen sarja tehdään tiettyyn autoon', 'Valmistus kestää 7-10 viikkoa', 'Hinta lasketaan määrittelysi mukaan: koko, leveys ja viimeistely', 'Toimitus Suomeen, Viroon, Latviaan ja Liettuaan sisältyy hintaan'],
  other=['Tilaamme eurooppalaisen jakelijan kautta', 'Toimitusajan ja tarkan hinnan vahvistamme, kun sopivuus autoosi on tarkistettu', 'Toimitus Suomeen, Viroon, Latviaan ja Liettuaan sisältyy hintaan'],
  pay='Sopivuuden tarkistus on maksuton: ensin havainnekuva ja tarkka hinta, sitten päätät',
  per_wheel='', mono='yksiosainen', two='kaksiosainen',
  foot='Taotut BC Forged-, Brixton Forged- ja MV Forged -vanteet tilauksesta, toimitus myös Suomeen', city='Tallinna, Viro',
  credits='Vanteiden ja autojen kuvat: BC Forged, Brixton Forged ja niiden jakelijat. Tuotemerkit kuuluvat omistajilleen',
  ptable='Sarjan hinta halkaisijan mukaan', col_d='Halkaisija', col_w='Leveys', col_p='4 vanteen sarja', ptable_note='Sis. ALV:n ja toimituksen Suomeen, Viroon, Latviaan tai Liettuaan. Lisävarusteet maksavat erikseen: kiillotettu lippa ja karhennettu olake. Jyrsityt keskikapselit kuuluvat sarjaan', series='Sarja {s}', filt_all='Kaikki', sizes_d='Koot {a}-{b}″.',
  brand_title='{b} -vanteet tilauksesta: kaikki mallit ja hinnat | Nordvelg', brand_desc='Kaikki {b} -mallit tilauksesta, toimitus Suomeen, Viroon, Latviaan ja Liettuaan sisältyy hintaan. Sopivuus autosi mukaan ja havainnekuva ennen maksua.', brand_h1='{b} -vanteet', all_brand='Kaikki {b} -mallit: {n}', on_req_note='Hinta lasketaan autosi ja määrittelysi mukaan',
  lang_name='Kieli', variants='Mallin versiot', variants_note='Sama muotoilu useana versiona. Kerromme sopivuuden tarkistuksessa, mikä niistä sopii autoosi')

def fi_fix(s):
    """Suomen yhdyssanat: monisanainen merkki + väliviiva ja välilyönti (BC Forged -vanteet), yksisanainen ilman välilyöntiä (iPE-vanteet)."""
    s = s.replace('. alkaen ', '. Alkaen ')  # hinta kuvauksen lopussa alkaa uuden virkkeen
    return re.sub(r'\biPE -(?=\w)', 'iPE-', s)

def slug(b, n):
    return re.sub(r'[^a-z0-9]+', '-', f'{b} {n}'.lower()).strip('-')

def esc(s):
    return html.escape(s, quote=True)

def fmt(p, lang):
    s = f'{p:,}'.replace(',', ' ' if lang != 'en' else ',')
    return T[lang]['price_from'].format(p=s)

_AH = {}
def _ahash(src):
    """Грубый перцептивный хеш 16x16: одинаковые фото из разных источников дают почти один хеш."""
    if src not in _AH:
        try:
            from PIL import Image
            im = Image.open(os.path.join(ROOT, big(src).lstrip('/'))).convert('L').resize((16, 16))
            px = list(im.tobytes()); m = sum(px) / len(px)
            _AH[src] = [x > m for x in px]
        except Exception:
            _AH[src] = None
    return _AH[src]

def uniq_imgs(imgs):
    """Убирает из галереи повторы одного и того же фото, оставляя версию с большим разрешением."""
    out = []
    for i in imgs:
        h = _ahash(i); dup = None
        for n, o in enumerate(out):
            ho = _ahash(o)
            if h and ho and sum(a != b for a, b in zip(h, ho)) <= 12:
                dup = n; break
        if dup is None:
            out.append(i)
        elif dims(i)[0] > dims(out[dup])[0]:
            out[dup] = i
    return out

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

def official(src):
    m = re.match(r'/img/(.+)-\d+\.webp$', src or '')
    return bool(m and OFFICIAL.match(SRC.get(m.group(1), '')))

def official_only(k, d):
    """Приоритетная модель: только фото с сайта производителя (BC: bc_models.json local, Brixton: shop_images.json <slug>-N).
    Пока Action не скачал официальные фото и их нет в манифесте, страница остаётся как была."""
    if k not in PRIORITY:
        return
    extra = [f'/img/{n}-960.webp' for n in SRC if re.fullmatch(r'shop/' + re.escape(k) + r'-\d+', n) and n in MAN]
    imgs = [i for i in d['imgs'] + extra if official(i)]
    if imgs:
        d['imgs'] = list(dict.fromkeys(imgs))

MERGED = {}  # старый адрес модели-варианта -> адрес объединённой страницы (для 301 в worker.js)
TWIN_SUFFIX = ('S', 'A', '-CX', '-BL')
COPY = json.load(open(os.path.join(ROOT, 'tools/wheel_copy.json'))) if os.path.exists(os.path.join(ROOT, 'tools/wheel_copy.json')) else {}

def merge_twins(wheels):
    """С 26.10.2026 варианты одного дизайна BC Forged (HCA162 и HCA162S, GW03 и GW03-CX, TR01 и TR01A, RD01 и RD01-BL)
    живут на одной странице: Google склеивал почти одинаковые карточки как копии."""
    byname = {d['n']: k for k, d in wheels.items() if d['b'] == 'BC Forged' and d.get('series')}
    groups = {}
    for n, k in byname.items():
        base = next((n[:-len(s)] for s in TWIN_SUFFIX if n.endswith(s) and n[:-len(s)] in byname), None)
        if base:
            groups.setdefault(byname[base], [byname[base]]).append(k)
    for k, d in wheels.items():  # ручные записи вида «HCA196 / HCA196S»
        if d['b'] == 'BC Forged' and ' / ' in d['n']:
            first = d['n'].split(' / ')[0]
            if first in byname:
                groups.setdefault(byname[first], [byname[first]]).append(k)
    for base, members in groups.items():
        members = list(dict.fromkeys(members))
        prim = next((m for m in members if wheels[m]['featured']), None) or next((m for m in members if wheels[m]['cars']), None) or base
        real = [m for m in members if wheels[m].get('series')]  # варианты из каталога завода
        d = wheels[prim]
        names = [wheels[m]['n'] for m in real]
        d['variants'] = [dict(n=wheels[m]['n'], imgs=uniq_imgs(wheels[m]['imgs'])[:2], sizes=wheels[m].get('sizes'),
                              ptab=wheels[m].get('ptab'), p=wheels[m].get('p')) for m in real]
        for m in members:
            if m == prim:
                continue
            o = wheels[m]
            d['imgs'] += [i for i in o['imgs'] if i not in d['imgs']]
            d['cars'] += [c for c in o['cars'] if c not in d['cars']]
            for f in ('series', 'typ', 'sizes', 'ptab', 'src'):
                if not d.get(f) and o.get(f):
                    d[f] = o[f]
            if o.get('p') and (not d.get('p') or o['p'] < d['p']):
                d['p'] = o['p']
            d['featured'] = d['featured'] or o['featured']
            MERGED[m] = prim
            del wheels[m]
        d['n'] = ' / '.join(names)
        d['sizes'] = sorted({s for v in d['variants'] for s in (v['sizes'] or [])}) or d.get('sizes')
    for k, d in wheels.items():
        d['key'] = k

def collect(lang):
    s = open(os.path.join(ROOT, LANGS[lang], 'index.html')).read()
    data = json.load(open(os.path.join(ROOT, 'tools', f'fitment-{lang}.json')))  # подборки «под машину», ручные
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
        ptab = [(dd, m['sizes'][str(dd)], setp(table[dd]) if dd in table else None) for dd in ds]
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
        if any(x[2] for x in ptab):
            d['p'] = min(x[2] for x in ptab if x[2])
    # other wheel brands from the Baan Velgen shop (prices there are per set incl. 21% NL VAT)
    PREFIX = ['brixton forged', 'brixton', 'hre', 'vorsteiner', 'bbs', 'anrky', 'apex', 'vossen', 'ipe magnesium wheels', 'ipe', 'brabus', 'novitec', 'manthey racing']
    existing = list(wheels.keys())
    for it in SHOP:
        if it['kind'] != 'wheel':
            continue
        n = it['title'].strip()
        if re.search(r'center caps?|wheel bolts?|lug nuts?|spacers?|tpms', n, re.I):
            continue  # аксессуары, не диски
        for pf in PREFIX:
            if n.lower().startswith(pf + ' '):
                n = n[len(pf):].strip(' -–')
                n = n[:1].upper() + n[1:]
                break
        n = re.sub(r'\s*//\s*', ', ', n)
        n = re.sub(r'"([^"]+)"', lambda m: m.group(1)[:1].upper() + m.group(1)[1:], n)
        n = re.sub(r'\s{2,}', ' ', n).strip(' ,')
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
        wheels[k] = dict(b=it['brand'], n=n, imgs=local, spec=spec, cars=[], p=p, featured=False, shop=True, title=it['title'])
    for k, d in wheels.items():
        official_only(k, d)
    merge_twins(wheels)
    # BC prices from the dealer list (set of 4, incl. VAT)
    for d in wheels.values():
        if d['b'] == 'BC Forged' and d['p'] is None:
            two = any(x in ' '.join(d['spec']).lower() for x in ('две', 'двух', 'kahe', 'two', 'kaksi'))
            d['p'] = 6030 if two else 4760
    # только бренды, на которые у нас есть дилерские условия у дистрибьютора
    wheels = {k: d for k, d in wheels.items() if d['b'] in BRANDS}
    return wheels, s

FONTCSS = None

# Срок изготовления на заводе (дни) по бренду, для shippingDetails
MAKE_DAYS = {'BC Forged': (28, 42), 'Brixton Forged': (49, 70)}
# Куда доставка включена в цену. Диски: завод шлёт комплект в LV, LT и FI за ту же сумму, что в Таллинн.
# iPE: включена только по Эстонии, в другие страны стоимость называем вместе с ценой.
# Германию не добавлять: диски под заказ туда не продаём (нет TÜV).
SHIP_WHEELS = ['EE', 'LV', 'LT', 'FI']
SHIP_EXHAUST = ['EE']

def offer(price, url, brand=None, countries=None):
    """Offer для JSON-LD: доставка включена (по умолчанию диски: EE, LV, LT, FI; выхлоп передаёт SHIP_EXHAUST), возврата нет (товар под заказ по спецификации клиента)."""
    countries = countries or SHIP_WHEELS
    ship = {"@type": "OfferShippingDetails",
            "shippingRate": {"@type": "MonetaryAmount", "value": 0, "currency": "EUR"},
            "shippingDestination": [{"@type": "DefinedRegion", "addressCountry": c} for c in countries]}
    if len(countries) == 1:
        ship["shippingDestination"] = ship["shippingDestination"][0]
    if brand in MAKE_DAYS:
        a, b = MAKE_DAYS[brand]
        ship["deliveryTime"] = {"@type": "ShippingDeliveryTime",
            "handlingTime": {"@type": "QuantitativeValue", "minValue": a, "maxValue": b, "unitCode": "DAY"},
            "transitTime": {"@type": "QuantitativeValue", "minValue": 2, "maxValue": 7, "unitCode": "DAY"}}
    return {"@type": "Offer", "priceCurrency": "EUR", "price": price, "availability": "https://schema.org/PreOrder",
            "url": url, "seller": {"@type": "Organization", "name": "Nordvelg", "url": SITE + "/"},
            "shippingDetails": ship,
            "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": countries if len(countries) > 1 else countries[0],
                "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted"}}

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
{hl}<link rel="alternate" hreflang="x-default" href="{alts['en']}">
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

def fit(t, short=None, n=65):
    """Укорачивает title: убираем бренд сайта, потом длинное уточнение. Текст не обрезаем, чтобы заголовки оставались уникальными."""
    for c in (t, t.replace(' | Nordvelg', ''), short):
        if c and len(c) <= n:
            return c
    return short or t.replace(' | Nordvelg', '')

SHORT = {'ru': '{}: кованые диски', 'et': '{}: sepistatud veljed', 'en': '{}: forged wheels'}
SHORT['fi'] = '{}: taotut vanteet'

PRIV = {'ru': 'Политика конфиденциальности', 'et': 'Privaatsuspoliitika', 'en': 'Privacy policy'}
PRIV['fi'] = 'Tietosuojaseloste'

EXH = {'ru': 'Выхлоп iPE', 'et': 'iPE väljalaskesüsteemid', 'en': 'iPE exhausts'}
EXH['fi'] = 'iPE-pakoputkistot'

def header(lang, alts):
    t = T[lang]; p = '/' + LANGS[lang]
    langs = ''.join(f'<a href="{alts[l].replace(SITE, "")}" hreflang="{l}" lang="{l}"{" aria-current=\"page\"" if l == lang else ""}>{l.upper()}</a>' for l in ('en', 'et', 'ru', 'fi'))
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
</div><div class="wrap credits">{t['credits']}. <a href="/{LANGS[lang]}privacy/">{PRIV[lang]}</a></div></footer>
'''

def card(d, lang):
    t = T[lang]; k = d.get('key') or slug(d['b'], d['n'])
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
    price_txt = (' ' + fmt(d['p'], lang)[:1].upper() + fmt(d['p'], lang)[1:] + '.') if d['p'] else ''
    title = fit(t['title'].format(name=name), SHORT[lang].format(name))
    desc = t['desc'].format(name=name, price=price_txt)
    cp = COPY.get(k, {}).get(lang)
    if cp and cp.get('desc'):
        desc = cp['desc'] + ((' ' + price_txt.strip()[:1].upper() + price_txt.strip()[1:]) if price_txt else '')
    elif d.get('sizes'):
        desc = desc + ' ' + t['sizes_d'].format(a=d['sizes'][0], b=d['sizes'][-1])
    imgs = uniq_imgs([i for i in d['imgs'] if i])
    og = SITE + (big(imgs[-1]) if imgs else '/img/og-nordvelg.jpg')
    out = head_common(lang, title, desc, url, alts, og)
    # JSON-LD
    prod = {"@type": "Product", "name": name, "brand": {"@type": "Brand", "name": d['b']},
            "image": [SITE + big(i) for i in imgs], "url": url, "description": desc}
    if d['p']:
        prod["offers"] = offer(d['p'], url, d['b'])
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nordvelg", "item": f"{SITE}/{LANGS[lang]}"},
        {"@type": "ListItem", "position": 2, "name": t['catalog'], "item": f"{SITE}/{LANGS[lang]}wheels/"},
        {"@type": "ListItem", "position": 3, "name": name, "item": url}]}
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": ([prod] if d['p'] else []) + [crumbs]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n</head>\n<body>\n'
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
    if cp:
        out += f'<section class="about"><h2>{esc(cp["h2"])}</h2>' + ''.join(f'<p>{esc(x)}</p>' for x in cp['p']) + '</section>\n'
    if len(d.get('variants') or []) > 1:
        vs = ''
        for v in d['variants']:
            vi = v['imgs'][0] if v['imgs'] else ''
            vw, vh = dims(vi)
            rng = f"{v['sizes'][0]}-{v['sizes'][-1]}″" if v.get('sizes') else ''
            vs += (f'<div class="card"><div class="stage"><img src="{vi}" width="{vw}" height="{vh}" loading="lazy" decoding="async" alt="{esc(d["b"] + " " + v["n"])}"></div>'
                   f'<span class="brand">{esc(d["b"])}</span><h3>{esc(v["n"])}</h3><div class="spec">{"<span>" + rng + "</span>" if rng else ""}</div>'
                   f'<div class="price">{fmt(v["p"], lang) if v.get("p") else t["on_request"]}</div></div>')
        out += f'<section class="rel variants"><h2>{t["variants"]}</h2><p class="note">{t["variants_note"]}</p><div class="grid">{vs}</div></section>\n'
    if d.get('ptab'):
        rows = ''.join(f'<tr><td>{dd}″</td><td>{ws[0]}-{ws[-1]}J</td><td>{fmt(pp, lang) if pp else t["on_request"]}</td></tr>' for dd, ws, pp in d['ptab'] if ws)
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
    return fi_fix(out) if lang == 'fi' else out

def catalog(lang, wheels, brand=None):
    t = T[lang]
    sub = f"wheels/brand/{bslug(brand)}/" if brand else "wheels/"
    alts = {l: f"{SITE}/{LANGS[l]}{sub}" for l in LANGS}
    sel = {k: w for k, w in wheels.items() if (brand is None or w['b'] == brand)}
    title = fit(t['brand_title'].format(b=brand) if brand else t['cat_title'])
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
    return fi_fix(out) if lang == 'fi' else out

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
    for lang, ks in allpages:  # убрать страницы моделей, которых больше нет
        base = os.path.join(ROOT, LANGS[lang], 'wheels'); keep = set(ks)
        for root, dirs, files in os.walk(base, topdown=False):
            rel = os.path.relpath(root, base)
            if rel != '.' and 'index.html' in files and rel not in keep:
                os.remove(os.path.join(root, 'index.html'))
            if rel != '.' and not os.listdir(root):
                os.rmdir(root)
    json.dump({l: ks for l, ks in allpages}, open(os.path.join(ROOT, 'tools/wheels.json'), 'w'), indent=1)
    json.dump(dict(sorted(MERGED.items())), open(os.path.join(ROOT, 'tools/wheels-merged.json'), 'w'), indent=1)
    print('merged', len(MERGED))

if __name__ == '__main__':
    main()
