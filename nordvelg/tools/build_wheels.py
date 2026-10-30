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
  cat_desc='Кованые диски BC Forged и Brixton Forged под заказ, подбор под вашу машину. Цены с НДС и доставкой по Эстонии, доставку в Латвию, Литву и Финляндию посчитаем вместе с ценой.',
  cat_h1='Каталог кованых дисков', cat_sub='Наша подборка моделей. Любую из них делают под вашу машину: диаметр, ширина, вылет и отделка на выбор',
  title='{name}: кованые диски под заказ в Таллинне | Nordvelg',
  desc='{name} под ваш автомобиль: подбор размера и вылета, эскиз до оплаты. Доставка по Эстонии в цене, в Латвию, Литву и Финляндию посчитаем вместе с ценой.{price}',
  price_from='от {p} €', set_note='за комплект из 4 дисков, с НДС и доставкой по Эстонии', est_note='ориентировочная цена, точную назовём после подбора',
  on_request='Цена по запросу', cta='Рассчитать для моей машины', wa='Спросить в WhatsApp',
  wa_text='Здравствуйте, интересуют диски {name}. Машина: ',
  fits='Подходит для', fits_note='Эти машины уже есть в нашем подборе. Для других моделей проверим посадку бесплатно',
  know='Что важно знать', how='Как проходит заказ', more='Другие модели {brand}', all='Весь каталог',
  zoom='Нажмите, чтобы увеличить', close='Закрыть',
  steps=['Вы присылаете марку, модель и год машины', 'Мы подбираем размер, вылет и отделку и присылаем эскиз', 'Вы вносите 50% предоплаты, завод изготавливает диски', 'Вы оплачиваете остаток, и диски едут к вам в Эстонию, Латвию, Литву или Финляндию'],
  bc=['Кованая заготовка из алюминия 6061-T6, каждый диск фрезеруют под вашу машину: разболтовка, центральное отверстие и вылет', 'Диски прошли японские испытания на прочность JWL и VIA', 'Около 40 вариантов отделки, можно сочетать две', 'Изготовление 4-6 недель. Доставка по Эстонии входит в цену, в Латвию, Литву и Финляндию посчитаем вместе с ценой'],
  brixton=['Американский бренд, каждый комплект собирают под конкретный автомобиль', 'Производство 7-10 недель', 'Цену считаем по вашей спецификации: размер, ширина, отделка', 'Доставка по Эстонии входит в цену. Отправляем и в Латвию, Литву и Финляндию, доставку туда посчитаем вместе с ценой'],
  other=['Заказываем через европейского дистрибьютора', 'Срок и точную цену подтверждаем после подбора под вашу машину', 'Доставка по Эстонии входит в цену. Отправляем и в Латвию, Литву и Финляндию, доставку туда посчитаем вместе с ценой'],
  pay='Подбор бесплатный: сначала эскиз и точная цена, потом решение',
  per_wheel='', mono='моноблок', two='двухсоставной',
  foot='Кованые диски BC Forged и Brixton Forged под заказ в Таллинне', city='Таллинн, Эстония',
  credits='Фото дисков и автомобилей: BC Forged, Brixton Forged и их дистрибьюторы. Названия брендов принадлежат их владельцам',
  ptable='Цена комплекта по диаметру', col_d='Диаметр', col_w='Ширина', col_p='Комплект из 4', ptable_note='С НДС и доставкой по Эстонии, доставку в Латвию, Литву и Финляндию посчитаем вместе с ценой. Опции оплачиваются отдельно: полированная полка, накатка. Фрезерованный центральный колпачок в комплекте', series='Серия {s}', filt_all='Все', sizes_d='Размеры {a}-{b}″.',
  brand_title='Диски {b} под заказ в Таллинне: все модели и цены | Nordvelg', brand_desc='Все модели {b} под заказ: подбор под ваш автомобиль, эскиз до оплаты. Доставка по Эстонии в цене, в Латвию, Литву и Финляндию посчитаем вместе с ценой.', brand_h1='Диски {b}', all_brand='Все модели {b}: {n}', on_req_note='Цену считаем под вашу машину и спецификацию',
  lang_name='Язык', variants='Варианты модели', variants_note='Один дизайн в нескольких исполнениях. Какой вариант подойдёт вашей машине, подскажем при подборе'),
 'et': dict(
  catalog='Kataloog', home='Avaleht', pick='Valik auto järgi', faq='Küsimused',
  cat_title='BC Forged ja Brixton sepistatud veljed tellimusel | Nordvelg',
  cat_desc='Tellimusel valmivad sepistatud veljed BC Forged ja Brixton Forged, valik teie auto järgi. Hinnad koos käibemaksu ja tarnega Eestis. Lätti, Leetu ja Soome tarne hinna ütleme koos pakkumisega.',
  cat_h1='Sepistatud velgede kataloog', cat_sub='Meie valitud mudelid. Iga komplekt valmib just teie autole: läbimõõt, laius, ET ja viimistlus teie valikul',
  title='{name}: sepistatud veljed tellimusel Tallinnas | Nordvelg',
  desc='{name} teie autole: mõõdu ja ET valik, eskiis enne makset. Tarne Eestis on hinna sees, Lätti, Leetu ja Soome tarne hinna ütleme koos pakkumisega.{price}',
  price_from='alates {p} €', set_note='4 velje komplekt koos käibemaksu ja tarnega Eestis', est_note='ligikaudne hind, täpse hinna ütleme pärast valikut',
  on_request='Hind päringu alusel', cta='Küsi hinda minu autole', wa='Küsi WhatsAppis',
  wa_text='Tere, mind huvitavad {name} veljed. Auto: ',
  fits='Sobib autodele', fits_note='Need autod on meie valikus juba olemas. Teiste mudelite puhul kontrollime sobivust tasuta',
  know='Mida on oluline teada', how='Kuidas tellimine käib', more='Teised {brand} mudelid', all='Kogu kataloog',
  zoom='Suurendamiseks klõpsake', close='Sulge',
  steps=['Saadate auto marga, mudeli ja aasta', 'Valime mõõdu, ET ja viimistluse ning saadame eskiisi', 'Tasute 50% ettemaksu, tehas valmistab veljed', 'Tasute ülejäänud summa ja veljed saadetakse teile Eestisse, Lätti, Leetu või Soome'],
  bc=['Sepistatud toorik alumiiniumisulamist 6061-T6, iga velg freesitakse teie auto järgi: poldimuster, tsentriava ja ET', 'Veljed on läbinud Jaapani tugevustestid JWL ja VIA', 'Umbes 40 viimistlust, kahte saab kombineerida', 'Valmistamine 4-6 nädalat. Tarne Eestis on hinna sees, Lätti, Leetu ja Soome tarne hinna ütleme koos pakkumisega'],
  brixton=['Ameerika bränd, iga komplekt valmib konkreetsele autole', 'Tootmine 7-10 nädalat', 'Hinna arvutame teie spetsifikatsiooni järgi: mõõt, laius, viimistlus', 'Tarne Eestis on hinna sees. Saadame ka Lätti, Leetu ja Soome, tarne hinna ütleme koos pakkumisega'],
  other=['Tellime Euroopa turustaja kaudu', 'Tähtaja ja täpse hinna kinnitame pärast valikut teie auto järgi', 'Tarne Eestis on hinna sees. Saadame ka Lätti, Leetu ja Soome, tarne hinna ütleme koos pakkumisega'],
  pay='Valik on tasuta: kõigepealt eskiis ja täpne hind, siis otsus',
  per_wheel='', mono='monoblokk', two='kaheosaline',
  foot='BC Forged ja Brixton Forged sepistatud veljed tellimusel Tallinnas', city='Tallinn, Eesti',
  credits='Velgede ja autode fotod: BC Forged, Brixton Forged ja nende turustajad. Kaubamärgid kuuluvad nende omanikele',
  ptable='Komplekti hind läbimõõdu järgi', col_d='Läbimõõt', col_w='Laius', col_p='4 velje komplekt', ptable_note='Koos käibemaksu ja tarnega Eestis. Lätti, Leetu ja Soome tarne hinna ütleme koos pakkumisega. Lisavalikud eraldi: poleeritud äär, rihveldus. Freesitud rummukate on komplektis', series='Seeria {s}', filt_all='Kõik', sizes_d='Mõõdud {a}-{b}″.',
  brand_title='{b} veljed tellimusel Tallinnas: kõik mudelid ja hinnad | Nordvelg', brand_desc='Kõik {b} mudelid tellimusel, valik teie auto järgi ja eskiis enne makset. Tarne Eestis on hinna sees, Lätti, Leetu ja Soome tarne hinna ütleme koos pakkumisega.', brand_h1='{b} veljed', all_brand='Kõik {b} mudelid: {n}', on_req_note='Hinna arvutame teie auto ja spetsifikatsiooni järgi',
  lang_name='Keel', variants='Mudeli variandid', variants_note='Üks disain mitmes teostuses. Millise variandi teie autole valida, ütleme valiku käigus'),
 'en': dict(
  catalog='Catalogue', home='Home', pick='Find by car', faq='Questions',
  cat_title='BC Forged and Brixton Forged Wheels Catalogue | Nordvelg',
  cat_desc='Made-to-order BC Forged and Brixton Forged wheels, fitment checked for your car. Prices incl. VAT and delivery within Estonia, delivery to Latvia, Lithuania and Finland quoted with the price.',
  cat_h1='Forged wheels catalogue', cat_sub='Our pick of models. Each set is made for your car: diameter, width, offset and finish of your choice',
  title='{name}: custom forged wheels in Tallinn | Nordvelg',
  desc='{name} built for your car: size and offset check, a sketch before you pay. Delivery within Estonia included, to Latvia, Lithuania and Finland quoted with the price.{price}',
  price_from='from €{p}', set_note='per set of 4, incl. VAT and delivery within Estonia', est_note='indicative price, exact quote after the fitment check',
  on_request='Price on request', cta='Get a quote for my car', wa='Ask on WhatsApp',
  wa_text='Hello, I am interested in {name} wheels. My car: ',
  fits='Fits', fits_note='These cars are already in our fitment guide. For other models we check fitment for free',
  know='Good to know', how='How ordering works', more='More {brand} models', all='Full catalogue',
  zoom='Click to enlarge', close='Close',
  steps=['You send the make, model and year of your car', 'We choose size, offset and finish and send a sketch', 'You pay a 50% deposit, the factory makes the wheels', 'You pay the balance and the wheels ship to you in Estonia, Latvia, Lithuania or Finland'],
  bc=['Forged 6061-T6 aluminium billet, each wheel machined for your car: bolt pattern, centre bore and offset', 'Tested to the Japanese JWL and VIA strength standards', 'About 40 finishes, two can be combined', 'Made in 4-6 weeks. Delivery within Estonia is included, delivery to Latvia, Lithuania or Finland is quoted with the price'],
  brixton=['American brand, each set is built for a specific car', 'Production takes 7-10 weeks', 'We price it from your specification: size, width, finish', 'Delivery within Estonia is included. We ship to Latvia, Lithuania and Finland too and quote delivery with the price'],
  other=['Ordered through a European distributor', 'Lead time and exact price confirmed after the fitment check', 'Delivery within Estonia is included. We ship to Latvia, Lithuania and Finland too and quote delivery with the price'],
  pay='The fitment check is free: first a sketch and an exact price, then you decide',
  per_wheel='', mono='monoblock', two='two-piece',
  foot='BC Forged and Brixton Forged wheels made to order in Tallinn', city='Tallinn, Estonia',
  credits='Wheel and car photos: BC Forged, Brixton Forged and their distributors. Brand names belong to their owners',
  ptable='Set price by diameter', col_d='Diameter', col_w='Width', col_p='Set of 4', ptable_note='Incl. VAT and delivery within Estonia, delivery to Latvia, Lithuania or Finland quoted with the price. Options are extra: polished lip, knurling. A machined centre cap is included', series='{s} series', filt_all='All', sizes_d='Sizes {a}-{b}″.',
  brand_title='{b} wheels made to order in Tallinn: all models and prices | Nordvelg', brand_desc='All {b} models made to order, fitment for your car and a sketch before you pay. Delivery within Estonia included, to Latvia, Lithuania and Finland quoted with the price.', brand_h1='{b} wheels', all_brand='All {b} models: {n}', on_req_note='We price it for your car and specification',
  lang_name='Language', variants='Versions of this design', variants_note='One design in several versions. We will tell you which one suits your car during the fitment check'),
}
# Suomi (fi), lisätty 28.10.2026: Suomi on oma kohdemarkkina. Vannesarjan hintaan sisältyy toimitus vain Virossa (päätös 28.10.2026), toimituskulut Suomeen kerrotaan tarjouksessa
T['fi'] = dict(
  catalog='Mallisto', home='Etusivu', pick='Auton mukaan', faq='UKK',
  cat_title='Taotut BC Forged- ja Brixton-vanteet tilauksesta | Nordvelg',
  cat_desc='Taotut BC Forged- ja Brixton Forged -vanteet tilauksesta. Tarkistamme sopivuuden autoosi. Hinnat sisältävät ALV:n ja toimituksen Virossa. Toimitamme myös Suomeen, Latviaan ja Liettuaan, ja toimituskulut kerromme tarjouksessa.',
  cat_h1='Taottujen vanteiden mallisto', cat_sub='Poimintoja mallistosta. Jokainen sarja tehdään sinun autoosi, ja halkaisijan, leveyden, ET:n ja viimeistelyn valitset itse',
  title='{name}: taotut vanteet tilauksesta | Nordvelg',
  desc='{name} -vanteet sinun autoosi: valitsemme koon ja ET:n, ja näet vanteet kuvassa autossasi ennen maksua. Toimituskulut Suomeen kerromme tarjouksessa.{price}',
  price_from='alkaen {p} €', set_note='4 vanteen sarja, hinta sisältää ALV:n ja toimituksen Virossa. Toimituskulut Suomeen kerromme tarjouksessa', est_note='suuntaa-antava hinta, tarkan hinnan kerromme sopivuuden tarkistuksen jälkeen',
  on_request='Hinta pyynnöstä', cta='Pyydä tarjous autooni', wa='Kysy WhatsAppissa',
  wa_text='Hei! Kysyisin tuotteesta {name}. Autoni: ',
  fits='Sopii autoihin', fits_note='Näihin autoihin olemme jo valinneet sopivat mitat. Muihin malleihin tarkistamme sopivuuden maksutta',
  know='Hyvä tietää', how='Näin tilaus etenee', more='Muita {brand} -malleja', all='Koko mallisto',
  zoom='Suurenna kuva klikkaamalla', close='Sulje',
  steps=['Kerrot autosi merkin, mallin ja vuosimallin', 'Valitsemme koon, ET:n ja viimeistelyn ja lähetämme kuvan vanteista autossasi', 'Maksat 50 % ennakkoa, ja tehdas valmistaa vanteet', 'Maksat loppusumman, ja vanteet toimitetaan sinulle Suomeen, Viroon, Latviaan tai Liettuaan'],
  bc=['Taottu aihio on 6061-T6-alumiinia, ja jokainen vanne jyrsitään autosi mukaan: pulttijako, keskireikä ja ET', 'Testattu japanilaisten JWL- ja VIA-lujuusvaatimusten mukaan', 'Noin 40 viimeistelyä, ja kaksi niistä voi yhdistää', 'Valmistus kestää 4-6 viikkoa. Toimitus Virossa sisältyy hintaan, ja toimituskulut Suomeen, Latviaan ja Liettuaan kerromme tarjouksessa'],
  brixton=['Yhdysvaltalainen merkki, jokainen sarja tehdään tiettyyn autoon', 'Valmistus kestää 7-10 viikkoa', 'Hinta lasketaan toiveidesi mukaan: koko, leveys ja viimeistely', 'Toimitus Virossa sisältyy hintaan. Toimitamme myös Suomeen, Latviaan ja Liettuaan, ja toimituskulut kerromme tarjouksessa'],
  other=['Tilaamme eurooppalaisen jakelijan kautta', 'Toimitusajan ja tarkan hinnan vahvistamme, kun sopivuus autoosi on tarkistettu', 'Toimitus Virossa sisältyy hintaan. Toimitamme myös Suomeen, Latviaan ja Liettuaan, ja toimituskulut kerromme tarjouksessa'],
  pay='Sopivuuden tarkistus on maksuton: ensin näet kuvan ja tarkan hinnan, sitten päätät',
  per_wheel='', mono='yksiosainen', two='kaksiosainen',
  foot='Taotut BC Forged- ja Brixton Forged -vanteet tilauksesta, toimitus myös Suomeen', city='Tallinna, Viro',
  credits='Vanteiden ja autojen kuvat: BC Forged, Brixton Forged ja niiden jakelijat. Tuotemerkit kuuluvat omistajilleen',
  ptable='Sarjan hinta halkaisijan mukaan', col_d='Halkaisija', col_w='Leveys', col_p='4 vanteen sarja', ptable_note='Sisältää ALV:n ja toimituksen Virossa. Toimituskulut Suomeen, Latviaan ja Liettuaan kerromme tarjouksessa. Lisävarusteet maksavat erikseen: kiillotettu lippa ja pyälletty olake. Jyrsityt keskikapselit kuuluvat sarjaan', series='Sarja {s}', filt_all='Kaikki', sizes_d='Koot {a}-{b}″.',
  brand_title='{b} -vanteet tilauksesta: kaikki mallit ja hinnat | Nordvelg', brand_desc='Kaikki {b} -mallit tilauksesta. Tarkistamme sopivuuden ja näytämme vanteet kuvassa autossasi ennen maksua. Toimituskulut Suomeen kerromme tarjouksessa.', brand_h1='{b} -vanteet', all_brand='Kaikki {b} -mallit: {n}', on_req_note='Hinta lasketaan autosi ja toiveidesi mukaan',
  lang_name='Kieli', variants='Mallin versiot', variants_note='Sama muotoilu useana versiona. Kerromme sopivuuden tarkistuksessa, mikä niistä sopii autoosi')

def fi_fix(s):
    """Suomen yhdyssanat: monisanainen merkki + väliviiva ja välilyönti (BC Forged -vanteet), yksisanainen ilman välilyöntiä (iPE-vanteet)."""
    s = s.replace('. alkaen ', '. Alkaen ')  # hinta kuvauksen lopussa alkaa uuden virkkeen
    # sivuston sääntö: ei pitkiä viivoja. Kaupan ja YouTuben englanninkielisissä nimissä niitä on («GTR (C190) – iPE ...»)
    s = re.sub(r'\s+[–—]\s+', ': ', s).replace('–', '-').replace('—', '-')
    s = re.sub(r'\biPE (?:iPE|IPE)\b', 'iPE', s)  # tuotenimi = «iPE » + kaupan otsikko, joka voi jo alkaa sanalla iPE
    return re.sub(r'\biPE -(?=\w)', 'iPE-', s)

def jw(w, lang):
    """Vanneleveys: suomeksi desimaalipilkku ja ilman turhaa nollaa (8-13J, 8,5J), muut kielet ennallaan (8.0J)."""
    if lang != 'fi':
        return w
    s = str(w)
    return (s[:-2] if s.endswith('.0') else s).replace('.', ',')

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
# Куда доставка включена в цену (решение от 28.10.2026). Диски: только по Эстонии. В Латвию, Литву и Финляндию
# отправляем, но стоимость доставки называем вместе с ценой. iPE: доставка не включена нигде, даже по Эстонии.
# Германию не добавлять: диски под заказ туда не продаём (нет TÜV).
SHIP_WHEELS = ['EE']
SHIP_EXHAUST = []
# Куда продаём (для hasMerchantReturnPolicy.applicableCountry), независимо от того, включена ли доставка
SELL_COUNTRIES = ['EE', 'LV', 'LT', 'FI']

def offer(price, url, brand=None, countries=None):
    """Offer для JSON-LD. countries: где доставка включена в цену (по умолчанию диски, SHIP_WHEELS = EE).
    Пустой список (выхлоп, SHIP_EXHAUST) = shippingDetails не выводим: стоимость доставки называем с ценой.
    Возврата нет (товар под заказ по спецификации клиента)."""
    countries = SHIP_WHEELS if countries is None else countries
    o = {"@type": "Offer", "priceCurrency": "EUR", "price": price, "availability": "https://schema.org/PreOrder",
         "url": url, "seller": {"@type": "Organization", "name": "Nordvelg", "url": SITE + "/"}}
    if countries:
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
        o["shippingDetails"] = ship
    o["hasMerchantReturnPolicy"] = {"@type": "MerchantReturnPolicy", "applicableCountry": SELL_COUNTRIES,
        "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted"}
    return o

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
<div>OÜ Juka Media<br>reg. 17495980, KMKR EE103041500<br>{t['city']}</div>
</div><div class="wrap credits">{t['credits']}. <a href="/{LANGS[lang]}privacy/">{PRIV[lang]}</a></div></footer>
'''

def card(d, lang):
    t = T[lang]; k = d.get('key') or slug(d['b'], d['n'])
    src = d['imgs'][0] if d['imgs'] else ''
    w, h = dims(src)
    price = fmt(d['p'], lang) if d['p'] else t['on_request']
    spec = ''.join(f'<span>{esc(x)}</span>' for x in d['spec'][:2])
    ser = d['series'] if d.get('is_series') else (prefix(k, d) if d['b'] == 'BC Forged' else '')
    da = f' data-type="{d.get("typ", "")}" data-series="{esc(ser or "")}"'
    href = f'{k}/' if d.get('is_series') else HREF.get(k, f'{k}/')
    return f'<a class="card"{da} href="/{LANGS[lang]}wheels/{href}"><div class="stage"><img src="{src}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(d.get("alt") or d["b"] + " " + d["n"])}"></div><span class="brand">{esc(d["b"])}</span><h3>{esc(d["n"])}</h3><div class="spec">{spec}</div><div class="price">{price}</div></a>'

def page(k, d, lang, all_wheels, series=None):
    series = series or {}
    S = series.get(GROUP_OF.get(k))
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
        {"@type": "ListItem", "position": 2, "name": t['catalog'], "item": f"{SITE}/{LANGS[lang]}wheels/"}]}
    p = '/' + LANGS[lang]
    sh1 = G[lang]['h1'].format(b=S['b'], s=S['s']) if S else None
    scrumb = ''
    if S:  # модель с отдельной страницей внутри серии: в крошках есть серия
        crumbs["itemListElement"].append({"@type": "ListItem", "position": 3, "name": sh1, "item": f"{SITE}/{LANGS[lang]}wheels/{S['slug']}/"})
        scrumb = f'<a href="{p}wheels/{S["slug"]}/">{esc(sh1)}</a><span>/</span>'
    crumbs["itemListElement"].append({"@type": "ListItem", "position": len(crumbs["itemListElement"]) + 1, "name": name, "item": url})
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": ([prod] if d['p'] else []) + [crumbs]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n</head>\n<body>\n'
    out += header(lang, alts)
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs"><a href="{p}">Nordvelg</a><span>/</span><a href="{p}wheels/">{t["catalog"]}</a><span>/</span>{scrumb}<span aria-current="page">{esc(name)}</span></nav>\n'
    # gallery
    gal = ''
    for n, i in enumerate(imgs):
        w, h = dims(i)
        gal += f'<button type="button" class="shot{" on" if n == 0 else ""}" data-big="{big(i)}" aria-label="{t["zoom"]}"><img src="{i}" width="{w}" height="{h}" alt="{esc(name) if n == 0 else esc(name) + f" ({n + 1}/{len(imgs)})"}" {"fetchpriority=\"high\"" if n == 0 else "loading=\"lazy\""} decoding="async"></button>'
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
<h1><span class="brand">{esc(d['b'])}</span> {esc(d['n'])}</h1>
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
        rows = ''.join(f'<tr><td>{dd}″</td><td>{jw(ws[0], lang)}-{jw(ws[-1], lang)}J</td><td>{fmt(pp, lang) if pp else t["on_request"]}</td></tr>' for dd, ws, pp in d['ptab'] if ws)
        out += f'<section class="ptab"><h2>{t["ptable"]}</h2><div class="tw"><table><thead><tr><th scope="col">{t["col_d"]}</th><th scope="col">{t["col_w"]}</th><th scope="col">{t["col_p"]}</th></tr></thead><tbody>{rows}</tbody></table></div><p class="note">{t["ptable_note"]}</p></section>\n'
    if d['cars']:
        out += f'<section class="fits"><h2>{t["fits"]}</h2><div class="chips">{"".join(f"<span>{esc(c)}</span>" for c in d["cars"][:40])}</div><p class="note">{t["fits_note"]}</p></section>\n'
    out += f'<section class="how"><h2>{t["how"]}</h2><ol>{"".join(f"<li>{x}</li>" for x in t["steps"])}</ol></section>\n'
    # рядом: своя серия, другие отдельные страницы той же серии и бренда, затем другие серии бренда
    own = [w for kk, w in all_wheels.items() if kk != k and HREF.get(kk) == f'{kk}/']
    rel = [series_card(S, all_wheels, lang)] if S else []
    rel += [w for w in own if S and GROUP_OF.get(w['key']) == S['slug']][:4 - len(rel)]
    rel += [w for w in own if w['b'] == d['b'] and w not in rel and w['featured']][:4 - len(rel)]
    others = sorted((x for x in series.values() if x['b'] == d['b'] and x is not S), key=lambda x: -len(x['models']))
    rel += [series_card(x, all_wheels, lang) for x in others][:4 - len(rel)]
    rel += [w for w in own if w['b'] == d['b'] and w not in rel][:4 - len(rel)]
    if len(rel) < 4:
        rel += [w for w in own if w['b'] != d['b'] and w['featured']][:4 - len(rel)]
    out += f'<section class="rel"><div class="rh"><h2>{t["more"].format(brand=d["b"])}</h2><a href="{p}wheels/">{t["all"]}</a></div><div class="grid">{"".join(card(w, lang) for w in rel)}</div></section>\n</main>\n'
    out += f'<div class="lb" hidden><button type="button" class="x" aria-label="{t["close"]}">×</button></div>\n'
    out += footer(lang)
    out += f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return fi_fix(out) if lang == 'fi' else out

def catalog(lang, wheels, brand=None, series=None):
    t = T[lang]
    sub = f"wheels/brand/{bslug(brand)}/" if brand else "wheels/"
    alts = {l: f"{SITE}/{LANGS[l]}{sub}" for l in LANGS}
    # карточки: отдельные страницы моделей и страницы серий (модели серий внутри них)
    sel = {e['key']: e for e in entries(wheels, series or {}, lang) if brand is None or e['b'] == brand}
    title = fit(t['brand_title'].format(b=brand) if brand else t['cat_title'])
    desc = t['brand_desc'].format(b=brand) if brand else t['cat_desc']
    h1 = t['brand_h1'].format(b=brand) if brand else t['cat_h1']
    out = head_common(lang, title, desc, alts[lang], alts, SITE + '/img/og-nordvelg.jpg')
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{LANGS[lang]}wheels/{k}/", "name": w.get('alt') or f"{w['b']} {w['n']}"} for i, (k, w) in enumerate(sel.items())]
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
            sers = sorted({w['series'] if w.get('is_series') else prefix(w['key'], w) for w in bw})
            opts = ''.join(f'<option value="{esc(x)}">{esc(G[lang]["card"].format(s=x))}</option>' for x in sers)
            filt = (f'<div class="filters" role="group"><button type="button" class="on" data-f="">{t["filt_all"]}</button>'
                    f'<button type="button" data-f="mono">{t["mono"]}</button><button type="button" data-f="two">{t["two"]}</button>'
                    f'<select aria-label="{G[lang]["series_l"]}"><option value="">{t["filt_all"]}</option>{opts}</select></div>')
        show = bw if brand else bw[:8]
        nb = brand_models(b, wheels)
        more = '' if brand else f'<a href="{p}wheels/brand/{bslug(b)}/">{t["all_brand"].format(b=b, n=nb)}</a>'
        head = f'<h2>{esc(b)}</h2>' if brand else f'<div class="rh"><h2>{esc(b)}</h2>{more}</div>'
        out += f'<section class="rel" data-brand="{esc(b)}">{head}{filt}<div class="grid">{"".join(card(w, lang) for w in show)}</div>'
        if not brand and len(bw) > 8:
            out += f'<p style="margin-top:18px"><a class="btn ghost" href="{p}wheels/brand/{bslug(b)}/">{t["all_brand"].format(b=b, n=nb)}</a></p>'
        out += '</section>\n'
    out += '</main>\n' + footer(lang) + f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return fi_fix(out) if lang == 'fi' else out

# ---- Серии и семейства (с 28.10.2026) --------------------------------------------------------------
# Google не индексировал ~1 150 тонких страниц моделей. Отдельные страницы остались только у моделей с
# авторским текстом (wheel_copy.json), приоритетных (PRIORITY) и моделей с главной; остальные модели BC Forged
# собраны на странице серии (буквенный префикс: bc-forged-kl-series), модели Brixton на странице семейства
# (brixton-forged-pf-series), у каждой модели свой раздел с id. Старые адреса: tools/redirects-wheels.json.
G = {
 'en': dict(h1='{b} {s} series', card='{s} series', title='{h1}: forged wheels made to order | Nordvelg', short='{h1}: forged wheels',
            nav='Models in the series', own='Models with their own page', vers='Versions', own_link='own page',
            more='More {b} series', series_l='Series', mono='monoblock', two='two-piece', a='and'),
 'et': dict(h1='{b} {s} seeria', card='{s} seeria', title='{h1}: sepistatud veljed tellimusel | Nordvelg', short='{h1}: sepistatud veljed',
            nav='Seeria mudelid', own='Mudelid, millel on oma leht', vers='Versioonid', own_link='oma leht',
            more='Teised {b} seeriad', series_l='Seeria', mono='monoblokk', two='kaheosaline', a='ja'),
 'ru': dict(h1='Серия {b} {s}', card='Серия {s}', title='{h1}: кованые диски под заказ | Nordvelg', short='{h1}: кованые диски',
            nav='Модели серии', own='Модели с отдельной страницей', vers='Исполнения', own_link='отдельная страница',
            more='Другие серии {b}', series_l='Серия', mono='моноблок', two='двухсоставной', a='и'),
 'fi': dict(h1='{b} {s} -sarja', card='{s}-sarja', title='{h1}: taotut vanteet tilauksesta | Nordvelg', short='{h1}: taotut vanteet',
            nav='Sarjan mallit', own='Mallit, joilla on oma sivu', vers='Versiot', own_link='oma sivu',
            more='Muut {b} -sarjat', series_l='Sarja', mono='yksiosainen', two='kaksiosainen', a='ja'),
}

def ru_pl(n, one, few, many):
    return one if n % 10 == 1 and n % 100 != 11 else few if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else many

def models_n(n, lang):
    """«17 моделей» на нужном языке."""
    return {'en': f'{n} model' + ('' if n == 1 else 's'), 'et': f'{n} mudel' + ('' if n == 1 else 'it'),
            'ru': f'{n} ' + ru_pl(n, 'модель', 'модели', 'моделей'), 'fi': f'{n} malli' + ('' if n == 1 else 'a')}[lang]

def join(xs, lang):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + f" {G[lang]['a']} " + xs[-1]

def num(p, lang):
    s = f'{p:,}'.replace(',', ' ' if lang != 'en' else ',')
    return f'€{s}' if lang == 'en' else f'{s} €'

def wnum(w, lang):
    s = f'{float(w):g}'
    return s.replace('.', ',') if lang == 'fi' else s

BX_RX = re.compile(r'^([A-Z]+\d+(?:\.\d+)?[A-Z]?(?:-R(?!S))?)(?:[\s-]+(.*))?$')
BX_ORDER = ['Duo Series', 'Targa Series', 'UltraSport+', 'RS', 'Carbon+', 'Circuit+', 'Monoblock', 'Magnesium+']

def bx_split(n):
    """«CM5-R ULTRASPORT+» -> ('CM5-R', 'UltraSport+'), «PF14-RS» -> ('PF14', 'RS'), «WR3 wheel UltraSport+ forged» -> ('WR3', 'UltraSport+')."""
    m = BX_RX.match(n)
    if not m:
        return n, ''
    v = (m.group(2) or '').strip()
    v = re.sub(r'(?i)^(?:wheel\s+)?ultrasport\+(?:\s+forged)?', 'UltraSport+', v)
    v = re.sub(r'^(Carbon\+|Circuit\+) Series$', r'\1', v)
    return m.group(1), v

def natkey(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]

def prefix(k, d):
    """Серия BC Forged по буквам модели (EH, EH⁺ и EH-T вместе), семейство Brixton по буквам модели."""
    if d['b'] == 'BC Forged':
        return re.match(r'bc-forged-([a-z]+)', k).group(1).upper()
    if d['b'] == 'Brixton Forged':
        return re.match(r'[A-Z]+', bx_split(d['n'])[0]).group(0)
    return None

HREF = {}  # ключ модели -> адрес относительно wheels/ («bc-forged-kl01/» или «bc-forged-kl-series/#kl05»)
GROUP_OF = {}  # ключ модели -> адрес серии, в которую она входит (для отдельных страниц тоже)

def widths(ptabs):
    ws = sorted({float(w) for pt in ptabs for _, wl, _ in (pt or []) for w in wl})
    return (ws[0], ws[-1]) if ws else None

def layout(wheels):
    """Делит модели на отдельные страницы и серии. Возвращает (элементы каталога, серии); заполняет HREF и GROUP_OF."""
    stand = set(COPY) | PRIORITY
    groups = {}
    for k, d in wheels.items():
        pf = prefix(k, d)
        if pf:
            groups.setdefault((d['b'], pf), []).append(k)
    series = {}
    for (b, pf), ks in groups.items():
        sl = f"{bslug(b)}-{pf.lower()}-series"
        own = [k for k in ks if k in stand or wheels[k]['featured']]
        rest = [k for k in ks if k not in own]
        if b == 'Brixton Forged':
            mods = {}
            for k in rest:
                mods.setdefault(bx_split(wheels[k]['n'])[0], []).append(k)
            if len(rest) == 1 and len(mods) == 1 and not own:  # одиночная модель без вариантов: своя страница, серия не нужна
                own, rest, mods = rest, [], {}
        if not rest:
            for k in ks:
                HREF[k] = f'{k}/'
            continue
        S = dict(slug=sl, b=b, s=pf, own=sorted(own, key=lambda k: natkey(wheels[k]['n'])), models=[])
        if b == 'BC Forged':
            for k in sorted(rest, key=lambda k: natkey(wheels[k]['n'])):
                d = wheels[k]
                S['models'].append(dict(a=k[len('bc-forged-'):], n=d['n'], keys=[k], d=d))
        else:
            for mn in sorted(mods, key=natkey):
                ks2 = sorted(mods[mn], key=lambda k: (BX_ORDER.index(bx_split(wheels[k]['n'])[1]) if bx_split(wheels[k]['n'])[1] in BX_ORDER else 99, wheels[k]['n']))
                S['models'].append(dict(a=slug('', mn), n=mn, keys=ks2, d=None))
        for m in S['models']:
            for k in m['keys']:
                HREF[k] = f"{sl}/#{m['a']}"
                GROUP_OF[k] = sl
        for k in own:
            HREF[k] = f'{k}/'
            GROUP_OF[k] = sl
        series[sl] = S
    for k in wheels:
        HREF.setdefault(k, f'{k}/')
    return series

def series_info(S, wheels, lang):
    """Факты для вступления и карточки серии: число моделей, конструкция, диаметры, ширины, цена «от»."""
    ks = [k for m in S['models'] for k in m['keys']] + S['own']
    ws = [wheels[k] for k in ks]
    ds = sorted({x for w in ws for x in (w.get('sizes') or [])})
    pt = [w.get('ptab') for w in ws] + [v.get('ptab') for w in ws for v in (w.get('variants') or [])]
    ps = [w['p'] for w in ws if w.get('p')]
    if S['b'] == 'Brixton Forged':
        names = sorted({bx_split(w['n'])[0] for w in ws}, key=natkey)
        vers = sorted({bx_split(w['n'])[1] for w in ws if bx_split(w['n'])[1]}, key=lambda v: (BX_ORDER.index(v) if v in BX_ORDER else 99, v))
    else:
        names = [m['n'] for m in S['models']] + [wheels[k]['n'] for k in S['own']]
        vers = []
    subs = []
    if S['b'] == 'BC Forged':
        for w in ws:
            if w.get('series') and w['series'] not in subs:
                subs.append(w['series'])
    typs = {w.get('typ') for w in ws if w.get('typ')}
    return dict(n=len(names), names=names, vers=vers, ds=ds, w=widths(pt), p=min(ps) if ps else None,
                typ=typs.pop() if len(typs) == 1 else None, subs=sorted(subs, key=len) if len(subs) > 1 else [],
                own=[wheels[k]['n'] for k in S['own']])

def intro(S, I, lang):
    """2-4 предложения из данных серии, без придуманных свойств."""
    b, s, n, p = S['b'], S['s'], I['n'], I['p']
    out = []
    if b == 'BC Forged':
        a, z = I['ds'][0], I['ds'][-1]
        wa, wb = (wnum(I['w'][0], lang), wnum(I['w'][1], lang)) if I['w'] else (None, None)
        mono = I['typ'] == 'mono'
        if lang == 'en':
            out.append(f"The {b} {s} series has {'one' if n == 1 else n} {'monoblock' if mono else 'two-piece'} design{'' if n == 1 else 's'}.")
            if I['subs']:
                out.append(f"It includes the {join(I['subs'], lang)} lines.")
            out.append(f"Diameters run from {a} to {z}″" + (f" and widths from {wa} to {wb}J" if wa else '') + ", and every wheel is machined to your car's bolt pattern, centre bore and offset.")
            if p:
                out.append(f"A set of four costs from {num(p, lang)} incl. VAT and delivery within Estonia.")
        elif lang == 'et':
            out.append(f"{b} {s} seerias on {models_n(n, lang)}, " + ('kõik monoblokkveljed.' if mono else 'kõik kaheosalised veljed.') if n > 1 else
                       f"{b} {s} seerias on 1 mudel, " + ('monoblokkvelg.' if mono else 'kaheosaline velg.'))
            if I['subs']:
                out.append(f"Seeriasse kuuluvad alaseeriad {join(I['subs'], lang)}.")
            out.append(f"Läbimõõdud on {a}-{z}″" + (f" ja laiused {wa}-{wb}J" if wa else '') + ". Iga velg freesitakse teie auto poldimustri, tsentriava ja ET järgi.")
            if p:
                out.append(f"Nelja velje komplekt maksab alates {num(p, lang)}, hinnas on käibemaks ja tarne Eestis.")
        elif lang == 'ru':
            out.append(f"В серии {b} {s} {models_n(n, lang)}, " + ('все моноблоки.' if mono else 'все двухсоставные.') if n > 1 else
                       f"В серии {b} {s} одна модель, " + ('моноблок.' if mono else 'двухсоставная.'))
            if I['subs']:
                out.append(f"В неё входят линейки {join(I['subs'], lang)}.")
            out.append(f"Диаметры от {a} до {z}″" + (f", ширина от {wa} до {wb}J" if wa else '') + ". Каждый диск фрезеруют под разболтовку, центральное отверстие и вылет вашей машины.")
            if p:
                out.append(f"Комплект из 4 дисков стоит от {num(p, lang)} с НДС и доставкой по Эстонии.")
        else:
            out.append(f"{b} {s} -sarjassa on {models_n(n, lang)}, ja " + ('kaikki ovat yksiosaisia.' if mono else 'kaikki ovat kaksiosaisia.') if n > 1 else
                       f"{b} {s} -sarjassa on 1 malli, joka on " + ('yksiosainen.' if mono else 'kaksiosainen.'))
            if I['subs']:
                out.append(f"Sarjaan kuuluvat alasarjat {join(I['subs'], lang)}.")
            out.append(f"Halkaisijat ovat {a}-{z}″" + (f" ja leveydet {wa}-{wb}J" if wa else '') + ". Jokainen vanne jyrsitään autosi pulttijaon, keskireiän ja ET:n mukaan.")
            if p:
                out.append(f"4 vanteen sarja maksaa alkaen {num(p, lang)}, ja hinta sisältää ALV:n. Toimituskulut Suomeen kerromme tarjouksessa.")
    else:
        names, vers = join(I['names'], lang), join(I['vers'], lang) if I['vers'] else ''
        if n == 1 and vers:  # одна модель в нескольких исполнениях
            out.append({'en': f"The {b} {s} series is one design, {names}, available as {vers}.",
                        'et': f"{b} {s} seerias on üks mudel, {names}, ja selle versioonid on {vers}.",
                        'ru': f"В серии {b} {s} одна модель, {names}, в исполнениях {vers}.",
                        'fi': f"{b} {s} -sarjassa on yksi malli, {names}, ja sen versiot ovat {vers}."}[lang])
            names = vers = ''
        if not names:
            pass
        elif lang == 'en':
            out.append(f"The {b} {s} series has {models_n(n, lang).replace('model', 'design')}: {names}.")
        elif lang == 'et':
            out.append(f"{b} {s} seerias on {models_n(n, lang)}: {names}.")
        elif lang == 'ru':
            out.append(f"В серии {b} {s} {models_n(n, lang)}: {names}.")
        else:
            out.append(f"{b} {s} -sarjassa on {models_n(n, lang)}: {names}.")
        if len(I['vers']) == 1 and vers:  # все модели в одном исполнении
            out.append({'en': f"All of them come as {vers}.", 'et': f"Kõik mudelid on saadaval {vers} versioonis.",
                        'ru': f"Все в исполнении {vers}.", 'fi': f"Kaikista malleista on saatavana versio {vers}."}[lang])
            vers = ''
        if lang == 'en':
            if vers:
                out.append(f"Versions: {vers}.")
            if p:
                out.append(f"An indicative price for a set of four starts from {num(p, lang)} incl. VAT and delivery within Estonia, and we confirm the exact price for your specification.")
        elif lang == 'et':
            if vers:
                out.append(f"Versioonid: {vers}.")
            if p:
                out.append(f"Nelja velje komplekti ligikaudne hind on alates {num(p, lang)}, hinnas on käibemaks ja tarne Eestis. Täpse hinna arvutame teie spetsifikatsiooni järgi.")
        elif lang == 'ru':
            if vers:
                out.append(f"Исполнения: {vers}.")
            if p:
                out.append(f"Ориентировочная цена комплекта из 4 дисков от {num(p, lang)} с НДС и доставкой по Эстонии, точную посчитаем по вашей спецификации.")
        else:
            if vers:
                out.append(f"Versiot: {vers}.")
            if p:
                out.append(f"4 vanteen sarjan suuntaa-antava hinta on alkaen {num(p, lang)}, ja hinta sisältää ALV:n. Tarkan hinnan laskemme toiveidesi mukaan, ja toimituskulut Suomeen kerromme samalla.")
    if I['own']:
        o, many = join(I['own'], lang), len(I['own']) > 1
        out.append({'en': f"{o} {'have their own pages' if many else 'has its own page'}.",
                    'et': f"{'Mudelitel' if many else 'Mudelil'} {o} on {'omad lehed' if many else 'oma leht'}.",
                    'ru': f"У {o} есть {'отдельные страницы' if many else 'отдельная страница'}.",
                    'fi': f"{'Malleilla' if many else 'Mallilla'} {o} on {'omat sivut' if many else 'oma sivu'}."}[lang])
    return ' '.join(out)

def series_desc(S, I, lang, h1):
    n, p = I['n'], I['p']
    pr = num(p, lang) if p else ''
    if S['b'] == 'BC Forged':
        rng = f"{I['ds'][0]}-{I['ds'][-1]}″"
        mono = I['typ'] == 'mono'
        return {'en': f"{h1}: {n} {'monoblock' if mono else 'two-piece'} designs, {rng}, from {pr} per set incl. VAT and delivery within Estonia. Fitment for your car, a sketch before you pay.",
                'et': f"{h1}: {models_n(n, lang)}, {'monoblokkveljed' if mono else 'kaheosalised veljed'}, {rng}, komplekt alates {pr} koos käibemaksu ja tarnega Eestis. Valik teie auto järgi, eskiis enne makset.",
                'ru': f"{h1}: {models_n(n, lang)}, {'моноблоки' if mono else 'двухсоставные'}, {rng}, комплект от {pr} с НДС и доставкой по Эстонии. Подбор под вашу машину, эскиз до оплаты.",
                'fi': f"{h1}: {n} {'yksiosaista' if mono else 'kaksiosaista'} mallia, {rng}, sarja alkaen {pr} sis. ALV:n, toimituskulut Suomeen erikseen. Tarkistamme sopivuuden ja näytämme kuvan ennen maksua."}[lang]
    for v in ([join(I['vers'], lang)] if len(I['vers']) > 1 else []) + ['']:  # список исполнений, только если описание не слишком длинное
        d = bx_desc(h1, n, v, pr, lang)
        if len(d) <= 165:
            break
    return d

def bx_desc(h1, n, v, pr, lang):
    return {'en': f"{h1}: {models_n(n, lang).replace('model', 'design')}" + (f" in {v} versions" if v else '') + f", indicative price from {pr} per set incl. VAT and delivery within Estonia. A sketch before you pay.",
            'et': f"{h1}: {models_n(n, lang)}" + (f", versioonid {v}" if v else '') + f", komplekt alates {pr} koos käibemaksu ja tarnega Eestis (ligikaudne hind). Eskiis enne makset.",
            'ru': f"{h1}: {models_n(n, lang)}" + (f", исполнения {v}" if v else '') + f", комплект от {pr} с НДС и доставкой по Эстонии (ориентировочно). Эскиз до оплаты.",
            'fi': f"{h1}: {models_n(n, lang)}" + (f", versiot {v}" if v else '') + f", sarja alkaen {pr} sis. ALV:n (suuntaa-antava hinta), toimituskulut Suomeen erikseen. Näet kuvan ennen maksua."}[lang]

def series_card(S, wheels, lang):
    """Карточка серии для каталога и блока «Другие серии»."""
    I = series_info(S, wheels, lang)
    first = wheels[S['models'][0]['keys'][0]]
    typ = I['typ'] or ''
    spec = ([G[lang][typ]] if typ else []) + [models_n(I['n'], lang)]
    return dict(key=S['slug'], b=S['b'], n=G[lang]['card'].format(s=S['s']), imgs=uniq_imgs(first['imgs'])[:1], spec=spec,
                p=I['p'], typ=typ, series=S['s'], featured=False, cars=[], is_series=True, alt=G[lang]['h1'].format(b=S['b'], s=S['s']))

SERIES_CSS = ('<style>.snav{padding-block:28px 8px}.snav h2{font-size:22px}.mdl{display:grid;grid-template-columns:minmax(0,6fr) minmax(0,5fr);gap:32px;'
              'padding-block:36px;border-top:1px solid var(--steel)}.mimg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;align-content:start}'
              '.mimg.one{grid-template-columns:minmax(0,1fr);max-width:460px}.mimg div{background:var(--white);border-radius:14px;aspect-ratio:1;padding:6%;display:grid;place-items:center}'
              '.mimg img{width:100%;height:100%;object-fit:contain}.mtx h2{margin-top:4px}.mtx .price{font-family:var(--display);font-size:26px;font-weight:500;margin-top:20px;font-variant-numeric:tabular-nums}'
              '.vl{list-style:none;margin-top:16px;max-width:520px}.vl li{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--steel)}'
              '.vl b{font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}.vl a{color:var(--bronze);font-weight:600}.mtx .chips span{font-size:13px;padding:5px 11px}'
              '.sfacts{padding-block:40px;border-top:1px solid var(--steel)}.sfacts .facts{max-width:760px}'
              '@media (max-width:980px){.mdl{grid-template-columns:minmax(0,1fr);gap:18px}}</style>\n')

def model_section(S, m, wheels, lang, url):
    """Раздел модели на странице серии: фото, ключевые характеристики, цена «от», кнопки заявки. Возвращает (html, Product)."""
    t = T[lang]; g = G[lang]; p = '/' + LANGS[lang]
    ws = [wheels[k] for k in m['keys']]
    name = f"{S['b']} {m['n']}"
    imgs = uniq_imgs([i for w in ws for i in w['imgs'] if i])
    imgs = imgs[:2] if len(imgs) == 3 else imgs[:4]
    spec, rows = [], []
    if S['b'] == 'BC Forged':
        d = m['d']
        if d.get('typ'):
            spec.append(t[d['typ']])
        if d.get('sizes'):
            spec.append(f"{d['sizes'][0]}-{d['sizes'][-1]}″")
        wr = widths([d.get('ptab')] + [v.get('ptab') for v in (d.get('variants') or [])])
        if wr:
            spec.append(f"{wnum(wr[0], lang)}-{wnum(wr[1], lang)}J")
        if not spec:
            spec = list(d['spec'][:2])
        if len(d.get('variants') or []) > 1:
            for v in d['variants']:
                rng = f"{v['sizes'][0]}-{v['sizes'][-1]}″" if v.get('sizes') else ''
                rows.append((esc(v['n']) + (f' <span class="spec" style="display:inline;margin:0">{rng}</span>' if rng else ''), fmt(v['p'], lang) if v.get('p') else t['on_request']))
        price = d['p']
    else:
        for w in ws:
            rows.append((esc(bx_split(w['n'])[1] or w['n']), fmt(w['p'], lang) if w.get('p') else t['on_request']))
        for k in S['own']:  # отдельная страница той же модели (PF9 Carbon+)
            mn, v = bx_split(wheels[k]['n'])
            if mn == m['n']:
                rows.append((esc(v or wheels[k]['n']), f'<a href="{p}wheels/{k}/">{g["own_link"]}</a>'))
        ps = [w['p'] for w in ws if w.get('p')]
        price = min(ps) if ps else None
    cars = list(dict.fromkeys(c for w in ws for c in w['cars']))
    q = urllib.parse.quote(name)
    wa = 'https://wa.me/' + WA + '?text=' + urllib.parse.quote(t['wa_text'].format(name=name))
    note = t['set_note'] if S['b'] == 'BC Forged' else t['est_note']
    pic = ''.join(f'<div><img src="{i}" width="{dims(i)[0]}" height="{dims(i)[1]}" loading="lazy" decoding="async" alt="{esc(name)}"></div>' for i in imgs)
    h = (f'<section class="mdl" id="{m["a"]}">\n<div class="mimg{" one" if len(imgs) == 1 else ""}">{pic}</div>\n<div class="mtx">'
         f'<span class="brand">{esc(S["b"])}</span><h2>{esc(m["n"])}</h2>'
         + (f'<div class="spec">{"".join(f"<span>{esc(x)}</span>" for x in spec)}</div>' if spec else '')
         + (f'<ul class="vl" aria-label="{g["vers"]}">' + ''.join(f'<li><span>{a}</span><b>{b}</b></li>' for a, b in rows) + '</ul>' if rows else '')
         + (f'<div class="price">{fmt(price, lang)}</div><p class="pnote">{note}</p>' if price else f'<div class="price">{t["on_request"]}</div><p class="pnote">{t["on_req_note"]}</p>')
         + (f'<div class="chips" aria-label="{t["fits"]}">{"".join(f"<span>{esc(c)}</span>" for c in cars[:12])}</div>' if cars else '')
         + f'<div class="ctas"><a class="btn" href="{p}?model={q}#quote">{t["cta"]}</a><a class="btn ghost" href="{wa}" target="_blank" rel="noopener noreferrer">{t["wa"]}</a></div>'
         '</div>\n</section>\n')
    prod = {"@type": "Product", "name": name, "brand": {"@type": "Brand", "name": S['b']}, "url": f"{url}#{m['a']}",
            "image": [SITE + big(i) for i in imgs]}
    if spec:
        prod["description"] = f"{name}: {', '.join(spec)}"
    if price:
        prod["offers"] = offer(price, f"{url}#{m['a']}", S['b'])
    return h, prod

def series_page(S, wheels, series, lang):
    t = T[lang]; g = G[lang]; p = '/' + LANGS[lang]
    alts = {l: f"{SITE}/{LANGS[l]}wheels/{S['slug']}/" for l in LANGS}
    url = alts[lang]
    I = series_info(S, wheels, lang)
    h1 = g['h1'].format(b=S['b'], s=S['s'])
    title = fit(g['title'].format(h1=h1), g['short'].format(h1=h1))
    desc = series_desc(S, I, lang, h1)
    first = wheels[S['models'][0]['keys'][0]]
    og = SITE + (big(uniq_imgs(first['imgs'])[0]) if first['imgs'] else '/img/og-nordvelg.jpg')
    out = head_common(lang, title, desc, url, alts, og) + SERIES_CSS
    secs, prods = '', []
    for m in S['models']:
        h, pr = model_section(S, m, wheels, lang, url)
        secs += h; prods.append(pr)
    brand_url = f"{SITE}/{LANGS[lang]}wheels/brand/{bslug(S['b'])}/"
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nordvelg", "item": f"{SITE}/{LANGS[lang]}"},
        {"@type": "ListItem", "position": 2, "name": t['catalog'], "item": f"{SITE}/{LANGS[lang]}wheels/"},
        {"@type": "ListItem", "position": 3, "name": S['b'], "item": brand_url},
        {"@type": "ListItem", "position": 4, "name": h1, "item": url}]}
    il = {"@type": "ItemList", "name": h1, "url": url, "numberOfItems": len(prods),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": pr} for i, pr in enumerate(prods)]}
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [il, crumbs]}, ensure_ascii=False, separators=(',', ':')) + '</script>\n</head>\n<body>\n'
    out += header(lang, alts)
    out += (f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs"><a href="{p}">Nordvelg</a><span>/</span><a href="{p}wheels/">{t["catalog"]}</a><span>/</span>'
            f'<a href="{p}wheels/brand/{bslug(S["b"])}/">{esc(S["b"])}</a><span>/</span><span aria-current="page">{esc(h1)}</span></nav>\n'
            f'<section class="cathead"><span class="brand">{esc(S["b"])}</span><h1>{esc(h1)}</h1><p>{esc(intro(S, I, lang))}</p></section>\n')
    chips = [(f'#{m["a"]}', m['n']) for m in S['models']] + [(f'{p}wheels/{k}/', wheels[k]['n']) for k in S['own']]
    chips.sort(key=lambda c: natkey(c[1]))
    out += f'<nav class="snav" aria-label="{g["nav"]}"><h2>{g["nav"]}</h2><div class="chips">' + ''.join(f'<a href="{h}">{esc(n)}</a>' for h, n in chips) + '</div></nav>\n'
    if S['own']:
        out += f'<section class="rel"><h2>{g["own"]}</h2><div class="grid">{"".join(card(wheels[k], lang) for k in S["own"])}</div></section>\n'
    out += secs
    facts = t['bc'] if S['b'] == 'BC Forged' else t['brixton']
    out += f'<section class="sfacts"><h2>{t["know"]}</h2><ul class="facts">{"".join(f"<li>{x}</li>" for x in facts)}</ul><p class="pay">{t["pay"]}</p></section>\n'
    out += f'<section class="how"><h2>{t["how"]}</h2><ol>{"".join(f"<li>{x}</li>" for x in t["steps"])}</ol></section>\n'
    other = [x for x in series.values() if x['b'] == S['b'] and x['slug'] != S['slug']]
    other.sort(key=lambda x: -len(x['models']))
    if other:
        out += (f'<section class="rel"><div class="rh"><h2>{g["more"].format(b=S["b"])}</h2><a href="{p}wheels/brand/{bslug(S["b"])}/">{t["all_brand"].format(b=S["b"], n=brand_models(S["b"], wheels))}</a></div>'
                f'<div class="grid">{"".join(card(series_card(x, wheels, lang), lang) for x in other[:4])}</div></section>\n')
    out += '</main>\n' + footer(lang) + '</body>\n</html>\n'
    return fi_fix(out) if lang == 'fi' else out

def brand_models(b, wheels):
    """Число моделей бренда: у BC каждая страница или раздел, у Brixton каждый дизайн (варианты Duo, Targa и т.д. вместе)."""
    ws = [w for w in wheels.values() if w['b'] == b]
    return len({bx_split(w['n'])[0] for w in ws}) if b == 'Brixton Forged' else len(ws)

def entries(wheels, series, lang):
    """Элементы каталога: приоритетные отдельные страницы, затем серии, затем остальные отдельные страницы."""
    own = [k for k in wheels if HREF[k] == f'{k}/']
    first = [wheels[k] for k in own if wheels[k]['featured']]
    ser = [series_card(S, wheels, lang) for S in sorted(series.values(), key=lambda S: (-len(S['models']), S['s']))]
    rest = [wheels[k] for k in own if not wheels[k]['featured']]
    return first + ser + rest

def redirects(pages_before):
    """tools/redirects-wheels.json: старая папка модели -> новый адрес (одним переходом). Копится между запусками."""
    path = os.path.join(ROOT, 'tools/redirects-wheels.json')
    old = json.load(open(path)) if os.path.exists(path) else {}
    merged = dict(MERGED)
    mp = os.path.join(ROOT, 'tools/wheels-merged.json')
    if os.path.exists(mp):
        for a, b in json.load(open(mp)).items():
            merged.setdefault(a, b)
    live = {h.split('/')[0] for h in HREF.values()}
    out = {}
    for s in sorted(set(pages_before) | set(old) | set(merged)):
        if s.startswith('brand/') or s in live:
            continue
        k = s
        for _ in range(5):
            k = merged.get(k, k)
        if k in HREF:
            out[s] = HREF[k]
        elif s in old and old[s].split('/')[0] in live:
            out[s] = old[s]
        else:
            b = 'brixton-forged' if s.startswith('brixton-') else 'ipe' if s.startswith('ipe-') else 'bc-forged'
            out[s] = f'brand/{b}/'
    json.dump(out, open(path, 'w'), indent=1, ensure_ascii=False)
    return out

def main():
    allpages = []
    wj = os.path.join(ROOT, 'tools/wheels.json')
    before = sorted({k for ks in json.load(open(wj)).values() for k in ks}) if os.path.exists(wj) else []
    for lang in LANGS:
        wheels, _ = collect(lang)
        # featured first, then by brand
        order = sorted(wheels.items(), key=lambda kv: (not kv[1]['featured'], kv[1]['b'] != 'BC Forged', kv[1]['b'], kv[1]['n']))
        wheels = dict((k, w) for k, w in order if w['imgs'])
        series = layout(wheels)
        base = os.path.join(ROOT, LANGS[lang], 'wheels')
        os.makedirs(base, exist_ok=True)
        open(os.path.join(base, 'index.html'), 'w').write(catalog(lang, wheels, series=series))
        for b in sorted({w['b'] for w in wheels.values()}):
            os.makedirs(os.path.join(base, 'brand', bslug(b)), exist_ok=True)
            open(os.path.join(base, 'brand', bslug(b), 'index.html'), 'w').write(catalog(lang, wheels, b, series))
        own = [k for k in wheels if HREF[k] == f'{k}/']
        for k in own:
            os.makedirs(os.path.join(base, k), exist_ok=True)
            open(os.path.join(base, k, 'index.html'), 'w').write(page(k, wheels[k], lang, wheels, series))
        for sl, S in series.items():
            os.makedirs(os.path.join(base, sl), exist_ok=True)
            open(os.path.join(base, sl, 'index.html'), 'w').write(series_page(S, wheels, series, lang))
        allpages.append((lang, own + sorted(series) + ['brand/' + bslug(b) for b in sorted({w['b'] for w in wheels.values()})]))
        print(lang, len(wheels), 'models,', len(own), 'model pages,', len(series), 'series pages,',
              sum(brand_models(b, wheels) for b in {w['b'] for w in wheels.values()}), 'designs')
    assert all(sorted(ks) == sorted(allpages[0][1]) for _, ks in allpages), 'разные адреса в языковых версиях'
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
    print('redirects', len(redirects(before)))

if __name__ == '__main__':
    main()
