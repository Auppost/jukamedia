"""Страницы выхлопных систем iPE на четырёх языках: одна страница на машину /exhaust/<car>/ (все системы этой машины
секциями с id="<старый адрес системы>"), страницы марок /exhaust/<make>/ и каталог /exhaust/.

Источник: tools/shop_items.json (kind == 'exhaust'), выгрузка магазина дистрибьютора.
Цены в магазине за изделие с НДС Нидерландов 21%; показываем с эстонским НДС 24%.
Версии без катализатора (cat bypass, catless) не продаём: в Эстонии с ними не пройти техосмотр.
До 28.10.2026 у каждой системы была своя страница /exhaust/<system>/ (419 тонких страниц). Старые адреса
пишем в tools/redirects-exhaust.json: {"<system>": "<car>/#<system>"}, 301 настраивается в worker.js.
"""
import html, json, os, re, shutil, unicodedata, urllib.parse
import build_wheels as W

ROOT, SITE, LANGS, esc, V = W.ROOT, W.SITE, W.LANGS, W.esc, W.V
TOOLS = os.path.dirname(os.path.abspath(__file__))
SHOP = [i for i in W.SHOP if i['kind'] == 'exhaust']
MAKES = ['Porsche', 'Ferrari', 'Lamborghini', 'McLaren', 'Mercedes-AMG', 'Mercedes', 'BMW', 'Audi', 'Aston Martin', 'Bentley',
         'Rolls-Royce', 'Maserati', 'Toyota', 'Nissan', 'Ford', 'Chevrolet', 'Lexus', 'Honda', 'Hyundai', 'Volkswagen', 'VW', 'Tesla',
         'Alfa Romeo', 'Jaguar', 'Land Rover', 'Range Rover', 'Cadillac', 'Dodge', 'Mini', 'Subaru', 'Mazda', 'Volvo', 'Infiniti', 'Kia',
         'Genesis', 'Lotus', 'Cupra', 'Seat', 'Jeep', 'Ram', 'Corvette', 'Abarth', 'Fiat', 'Peugeot', 'Renault']
ALIAS = {'Mercedes': 'Mercedes-AMG', 'VW': 'Volkswagen', 'Range Rover': 'Land Rover', 'Corvette': 'Chevrolet'}
BAD = re.compile(r'bypass|catless|without cats|de-?cat|race pipe', re.I)
# (шаблон по названию в магазине, ru, et, en, ключ). Порядок важен: первый совпавший шаблон задаёт тип.
# Full F1 Sound / Full Evolution Exhaust тоже полные системы (раньше по ошибке попадали в «равнодлинный коллектор»).
TYPES = [
    (r'equal-?length header', 'Равнодлинный коллектор', 'Võrdse pikkusega kollektor', 'Equal-length headers', 'elheader'),
    (r'full (exhaust|system)|exhaust system|\bfull\b.*\bexhaust\b', 'Выхлопная система', 'Väljalaskesüsteem', 'Exhaust system', 'full'),
    (r'cat-?back', 'Выхлоп cat-back', 'Cat-back väljalaskesüsteem', 'Cat-back exhaust', 'catback'),
    (r'down ?pipe', 'Даунпайпы', 'Downpipe’id', 'Downpipes', 'downpipe'),
    (r'link pipe', 'Соединительные трубы', 'Ühendustorud', 'Link pipes', 'link'),
    (r'header', 'Выпускной коллектор', 'Väljalaskekollektor', 'Headers', 'header'),
    (r'x-?pipe', 'X-труба', 'X-toru', 'X-pipe', 'xpipe'),
    (r'cat (bypass )?pipe', 'Трубы с катализаторами', 'Katalüsaatoritega torud', 'Cat pipes', 'catpipe'),
    (r'front pipe|mid pipe', 'Передняя труба', 'Esitoru', 'Front pipe', 'front'),
    (r'muffler|rear section|back box', 'Глушитель', 'Summuti', 'Muffler', 'muffler'),
    (r'tip', 'Насадки', 'Otsikud', 'Tips', 'tips'),
]
TYPE_BY_KEY = {t[4]: t for t in TYPES}
# Клапаны есть только у полных систем, cat-back и задних глушителей iPE. У коллекторов, даунпайпов, труб и насадок их нет,
# поэтому «тихо в городе, громко по кнопке» пишем только этим трём типам.
VALVED = {'full', 'catback', 'muffler'}

# Короткие факты по типу системы (секция на странице машины). Про техосмотр: только «версии с катализатором, как требует
# техосмотр», без обещания, что машина его пройдёт.
_COMBO = {'ru': 'Сочетается с глушителем или полной системой iPE: подскажем, что подойдёт вашей машине',
          'et': 'Sobib kokku iPE summuti või tervikliku süsteemiga: ütleme, mis teie autole sobib',
          'en': 'Pairs with an iPE muffler or full system: we will tell you what works on your car',
          'fi': 'Sopii yhteen iPE:n äänenvaimentimen tai koko järjestelmän kanssa: kerromme, mikä sopii autoosi'}
_CATTED = {'ru': 'Только версии с катализатором, как требует техосмотр',
           'et': 'Ainult katalüsaatoriga versioonid, nagu nõuab tehnoülevaatus',
           'en': 'Catted versions only, as the inspection requires',
           'fi': 'Myymme vain katalysaattorillisia versioita, koska katsastus vaatii sen'}
FACTS = {
 'full': {'ru': ['Клапаны: тихо в городе, громко по кнопке', 'Система целиком: передняя часть и задний глушитель рассчитаны на совместную работу'],
          'et': ['Klappidega: linnas vaikne, nupuvajutusega vali', 'Terviklik süsteem: esiosa ja tagasummuti on loodud koos töötama'],
          'en': ['Valvetronic: quiet in town, loud at the press of a button', 'A complete system: front section and rear silencer designed to work together'],
          'fi': ['Venttiiliohjaus: kaupungissa hiljainen, napista saat lisää ääntä', 'Kokonainen järjestelmä: etuosa ja takaäänenvaimennin on suunniteltu toimimaan yhdessä']},
 'catback': {'ru': ['Звук на клапанах: тихо в городе, громко по кнопке', 'Ставится после штатных катализаторов, они остаются на месте'],
             'et': ['Klappidega heli: linnas vaikne, nupuvajutusega vali', 'Paigaldub tehase katalüsaatorite taha, katalüsaatorid jäävad alles'],
             'en': ['Valve-controlled sound: quiet in town, loud at the press of a button', 'Fits behind the factory catalytic converters, which stay in place'],
             'fi': ['Venttiiliohjattu ääni: kaupungissa hiljainen, napista saat lisää ääntä', 'Asennetaan tehtaan katalysaattorien perään, ja katalysaattorit jäävät paikalleen']},
 'muffler': {'ru': ['Задний глушитель с клапанами: тихо в городе, громко по кнопке', 'Меняется только задняя часть, штатные катализаторы остаются'],
             'et': ['Klappidega tagasummuti: linnas vaikne, nupuvajutusega vali', 'Vahetatakse ainult tagumine osa, tehase katalüsaatorid jäävad alles'],
             'en': ['Rear silencer with valves: quiet in town, loud at the press of a button', 'Replaces only the rear section, the factory catalytic converters stay'],
             'fi': ['Takaäänenvaimennin venttiileillä: kaupungissa hiljainen, napista saat lisää ääntä', 'Vain takaosa vaihtuu, ja tehtaan katalysaattorit jäävät paikalleen']},
 'elheader': {'ru': ['Трубы одинаковой длины: ровные импульсы выхлопа, больше мощности и более высокий, резкий звук'],
              'et': ['Võrdse pikkusega torud: ühtlased heitgaasiimpulsid, rohkem võimsust ning teravam ja kõrgem heli'],
              'en': ['Equal-length runners: evenly spaced exhaust pulses, more power and a sharper, higher-pitched sound'],
              'fi': ['Tasapituiset putket: tasaiset pakokaasupulssit, lisää tehoa ja terävämpi, korkeampi ääni']},
 'header': {'ru': ['Вместо штатных коллекторов: газы выходят свободнее, больше мощности и насыщеннее звук'],
            'et': ['Asendab tehase väljalaskekollektorid: vabam vool, rohkem võimsust ja täidlasem heli'],
            'en': ['Replaces the factory exhaust manifolds: freer flow, more power and a fuller sound'],
            'fi': ['Korvaa tehtaan pakosarjat: vapaampi virtaus, lisää tehoa ja täyteläisempi ääni']},
 'downpipe': {'ru': ['Трубы большего диаметра сразу после турбины: быстрее отклик и больше мощности'],
              'et': ['Laiemad torud kohe turbo järel: kiirem reaktsioon ja rohkem võimsust'],
              'en': ['Wider pipes straight after the turbo: quicker response and more power'],
              'fi': ['Väljemmät putket heti turbon jälkeen: nopeampi vaste ja lisää tehoa']},
 'catpipe': {'ru': ['Спортивные катализаторы вместо штатных: поток свободнее, звук громче'],
             'et': ['Sportkatalüsaatorid tehase omade asemel: vabam vool ja valjem heli'],
             'en': ['Sport catalytic converters in place of the factory ones: freer flow and a louder sound'],
             'fi': ['Urheilukatalysaattorit tehtaan omien tilalle: vapaampi virtaus ja voimakkaampi ääni']},
 'link': {'ru': ['Соединяют переднюю часть с задним глушителем вместо штатных труб'],
          'et': ['Ühendavad esiosa tagasummutiga tehase torude asemel'],
          'en': ['Connect the front section to the rear silencer in place of the factory pipes'],
          'fi': ['Yhdistävät etuosan takaäänenvaimentimeen tehtaan putkien tilalla']},
 'xpipe': {'ru': ['Объединяет две стороны выхлопа: звук ровнее и выше'],
           'et': ['Ühendab väljalaske kaks poolt: ühtlasem ja kõrgem heli'],
           'en': ['Joins the two sides of the exhaust: a smoother, higher-pitched sound'],
           'fi': ['Yhdistää pakoputkiston kaksi puolta: tasaisempi ja korkeampi ääni']},
 'front': {'ru': ['Заменяет штатные передние трубы, газы выходят свободнее'],
           'et': ['Asendab tehase esitorud, vool on vabam'],
           'en': ['Replaces the factory front pipes for freer flow'],
           'fi': ['Korvaa tehtaan etuputket, ja virtaus on vapaampi']},
 'tips': {'ru': ['Меняют вид сзади: форма и отделка на выбор, звук остаётся прежним'],
          'et': ['Muudavad auto tagaosa välimust: kuju ja viimistlus teie valikul, heli jääb samaks'],
          'en': ['Changes the look at the back: shape and finish of your choice, the sound stays as it is'],
          'fi': ['Muuttavat takaosan ilmettä: muoto ja viimeistely valintasi mukaan, ääni pysyy ennallaan']},
}
for _k in ('downpipe', 'catpipe'):
    for _l in _CATTED:
        FACTS[_k][_l].append(_CATTED[_l])
for _k in ('elheader', 'header', 'link', 'xpipe', 'front'):
    for _l in _COMBO:
        FACTS[_k][_l].append(_COMBO[_l])

T = {
 'ru': dict(sec='Выхлоп iPE', cat_title='Выхлопные системы iPE в Таллинне: цены | Nordvelg',
            cat_desc='Выхлопные системы iPE из титана и нержавеющей стали под заказ: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Цены с НДС и доставкой по Эстонии, доставку в другие страны посчитаем вместе с ценой.',
            cat_h1='Выхлопные системы iPE', cat_sub='Оригинальные системы iPE через европейского дистрибьютора. Продаём только версии с катализатором: без катализатора машину в Эстонии на техосмотре не пропустят',
            make_title='Выхлоп iPE для {m}: все системы и цены | Nordvelg', make_desc='Выхлопные системы iPE для {m} под заказ, только версии с катализатором. Цены с НДС и доставкой по Эстонии, доставку в другие страны посчитаем вместе с ценой.', make_h1='Выхлоп iPE для {m}',
            h1='Выхлопные системы iPE для {car}', title='Выхлоп iPE для {car}: цены в Таллинне | Nordvelg', short='Выхлоп iPE для {car}',
            desc='Выхлоп iPE для {car}: {types}, материал: {mats}. Цены с НДС и доставкой по Эстонии, доставку в другие страны посчитаем вместе с ценой.{price}',
            sys='{t} iPE для {car}', sys_desc='{t} iPE для {car}, материал: {mat}.',
            intro='Для этой машины есть: {types}. Материал: {mats}.', intro_v='Звук на клапанах (тихо в городе, громко по кнопке): {types}.', conj='и', mat_or='или',
            mat_ti='титан', mat_ss='нержавеющая сталь', finishes='Отделка насадок', all='Все системы iPE', more='Другие выхлопы iPE для {m}', all_make='Все модели {m}: {n}',
            fits='Подходит: {car}', used='б/у', jump='Системы на этой странице',
            facts=['Точную комплектацию, срок и цену подтверждаем до оплаты', 'Доставка по Эстонии входит в цену. Доставку в Латвию, Литву или Финляндию посчитаем вместе с ценой', 'С установкой подскажем'],
            note='с НДС и доставкой по Эстонии', req='Версию с катализатором считаем по запросу', other='Другие', filt='Марка',
            wa='Здравствуйте, интересует {name}. Машина: ',
            vid='Как звучит iPE: видео производителя', play='Смотреть видео', vnote='Ролик с YouTube-канала iPE. Плеер YouTube загрузится, только когда вы нажмёте на видео.'),
 'et': dict(sec='iPE väljalaskesüsteemid', cat_title='iPE väljalaskesüsteemid Tallinnas: hinnad | Nordvelg',
            cat_desc='iPE väljalaskesüsteemid titaanist ja roostevabast terasest tellimusel: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Hinnad koos käibemaksu ja tarnega Eestis, teistesse riikidesse tarne hinna ütleme pakkumises.',
            cat_h1='iPE väljalaskesüsteemid', cat_sub='Originaalsed iPE süsteemid Euroopa turustaja kaudu. Müüme ainult katalüsaatoriga versioone: ilma katalüsaatorita ei läbi auto Eestis tehnoülevaatust',
            make_title='iPE väljalase {m} autodele: kõik süsteemid ja hinnad | Nordvelg', make_desc='iPE väljalaskesüsteemid {m} autodele tellimusel, ainult katalüsaatoriga versioonid. Hinnad koos käibemaksu ja tarnega Eestis, teistesse riikidesse tarne hinna ütleme pakkumises.', make_h1='iPE väljalaskesüsteemid {m} autodele',
            h1='iPE väljalaskesüsteemid: {car}', title='iPE väljalaskesüsteemid: {car}, hinnad | Nordvelg', short='iPE väljalase: {car}',
            desc='iPE {types} autole {car}, materjal: {mats}. Hinnad koos käibemaksu ja tarnega Eestis, teistesse riikidesse tarne hinna ütleme pakkumises.{price}',
            sys='{t} iPE autole {car}', sys_desc='{t} iPE autole {car}, materjal: {mat}.',
            intro='Sellele autole on iPE-lt saadaval: {types}. Materjal: {mats}.', intro_v='Klappidega heli (linnas vaikne, nupuvajutusega vali): {types}.', conj='ja', mat_or='või',
            mat_ti='titaan', mat_ss='roostevaba teras', finishes='Otsikute viimistlus', all='Kõik iPE süsteemid', more='Teised iPE süsteemid: {m}', all_make='Kõik {m} mudelid: {n}',
            fits='Sobib: {car}', used='kasutatud', jump='Süsteemid sellel lehel',
            facts=['Täpse komplekti, tähtaja ja hinna kinnitame enne makset', 'Tarne Eestis on hinna sees. Tarne hinna Lätti, Leetu või Soome ütleme koos pakkumisega', 'Paigalduse osas aitame nõuga'],
            note='koos käibemaksu ja tarnega Eestis', req='Katalüsaatoriga versiooni hind päringu alusel', other='Muud', filt='Mark',
            wa='Tere, mind huvitab {name}. Auto: ',
            vid='Kuidas iPE kõlab: tootja video', play='Vaata videot', vnote='Video iPE YouTube’i kanalilt. YouTube’i mängija laaditakse alles siis, kui video peale vajutate.'),
 'en': dict(sec='iPE exhausts', cat_title='iPE Exhaust Systems in Tallinn: Prices | Nordvelg',
            cat_desc='iPE exhaust systems in titanium and stainless steel, made to order: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Prices incl. VAT and delivery within Estonia, other countries quoted with the price.',
            cat_h1='iPE exhaust systems', cat_sub='Genuine iPE systems through a European distributor. We sell catted versions only: without catalytic converters a car fails the Estonian inspection',
            make_title='iPE exhaust for {m}: all systems and prices | Nordvelg', make_desc='iPE exhaust systems for {m} made to order, catted versions only. Prices incl. VAT and delivery within Estonia, other countries quoted with the price.', make_h1='iPE exhaust for {m}',
            h1='iPE exhaust systems for {car}', title='iPE exhaust for {car}: prices in Tallinn | Nordvelg', short='iPE exhaust for {car}',
            desc='iPE {types} for {car}, in {mats}. Prices incl. VAT and delivery within Estonia, other countries quoted with the price.{price}',
            sys='iPE {t} for {car}', sys_desc='iPE {t} for {car}, {mat}.',
            intro='Available for this car: {types}. Material: {mats}.', intro_v='Valve-controlled sound (quiet in town, loud at the press of a button): {types}.', conj='and', mat_or='or',
            mat_ti='titanium', mat_ss='stainless steel', finishes='Tip finishes', all='All iPE systems', more='More iPE exhausts for {m}', all_make='All {m} models: {n}',
            fits='Fits: {car}', used='pre-owned', jump='Systems on this page',
            facts=['Exact configuration, lead time and price confirmed before you pay', 'Delivery within Estonia is included. Delivery to Latvia, Lithuania or Finland is quoted with the price', 'We can advise on fitting'],
            note='incl. VAT and delivery within Estonia', req='Catted version priced on request', other='Other', filt='Make',
            wa='Hello, I am interested in the {name}. My car: ',
            vid='How iPE sounds: a video from the maker', play='Play video', vnote='From the iPE YouTube channel. The YouTube player loads only when you press play.'),
}

# Suomi (fi): nimet erikseen tavallisena ja titaanisena, jotta adjektiivi taipuu oikein (titaaninen pakoputkisto, titaaniset downpipet)
TYPES_FI = {
    'elheader': ('tasapituiset pakosarjat', 'titaaniset tasapituiset pakosarjat'),
    'full': ('pakoputkisto', 'titaaninen pakoputkisto'),
    'catback': ('cat-back-pakoputkisto', 'titaaninen cat-back-pakoputkisto'),
    'downpipe': ('downpipet', 'titaaniset downpipet'),
    'link': ('liitosputket', 'titaaniset liitosputket'),
    'header': ('pakosarjat', 'titaaniset pakosarjat'),
    'xpipe': ('X-putki', 'titaaninen X-putki'),
    'catpipe': ('katalysaattoriputket', 'titaaniset katalysaattoriputket'),
    'front': ('etuputki', 'titaaninen etuputki'),
    'muffler': ('äänenvaimennin', 'titaaninen äänenvaimennin'),
    'tips': ('pakoputken päätteet', 'titaaniset pakoputken päätteet'),
}
# Automallin nimeä ei taivuteta (Purosangueen, 911:lle (992) menisivät helposti pieleen): sija on aina yleisnimessä
# (malliin {car}) tai nimi seisoo kaksoispisteen edessä ({car}: iPE-pakoputkistot). {ma} = merkki + autoihin oikealla yhdysmerkillä.
T['fi'] = dict(sec='iPE-pakoputkistot', cat_title='iPE-pakoputkistot tilauksesta: hinnat ja toimitus Suomeen | Nordvelg',
            cat_desc='iPE-pakoputkistot titaanista ja ruostumattomasta teräksestä tilauksesta: Porsche, Ferrari, Lamborghini, McLaren, BMW M, AMG. Hinnat sisältävät ALV:n, ja toimituskulut Suomeen kerromme tarjouksessa.',
            cat_h1='iPE-pakoputkistot', cat_sub='Aidot iPE-tuotteet eurooppalaisen jakelijan kautta. Myymme vain versioita, joissa on katalysaattori, koska ilman sitä auto ei mene katsastuksesta läpi',
            make_title='iPE-pakoputkistot {ma}: hinnat | Nordvelg', make_desc='iPE-pakoputkistot {ma} tilauksesta, vain katalysaattorilliset versiot. Hinnat sisältävät ALV:n, ja toimituskulut Suomeen kerromme tarjouksessa.', make_h1='iPE-pakoputkistot {ma}',
            h1='{car}: iPE-pakoputkistot', title='{car}: iPE-pakoputkistot ja hinnat | Nordvelg', short='{car}: iPE-pakoputkistot',
            desc='{car}: iPE:n {types}, materiaalina {mats}. Hinnat sisältävät ALV:n, ja toimituskulut Suomeen kerromme tarjouksessa.{price}',
            sys='{car}: iPE:n {t}', sys_desc='iPE:n {t} malliin {car}, materiaalina {mat}.',
            intro='Tähän autoon on saatavilla: {types}. Materiaali: {mats}.', intro_v='Venttiiliohjattu ääni (kaupungissa hiljainen, napista lisää ääntä): {types}.', conj='ja', mat_or='tai',
            mat_ti='titaani', mat_ss='ruostumaton teräs', finishes='Pakoputken päätteiden viimeistely', all='Kaikki iPE-pakoputkistot', more='Muut iPE-pakoputkistot {ma}', all_make='{m}: kaikki mallit ({n})',
            fits='Sopii: {car}', used='käytetty', jump='Järjestelmät tällä sivulla',
            facts=['Tarkan kokoonpanon, toimitusajan ja hinnan vahvistamme ennen maksua', 'Hinta sisältää toimituksen Viron sisällä. Toimituskulut Suomeen, Latviaan ja Liettuaan kerromme tarjouksessa', 'Neuvomme asennuksessa'],
            note='sisältää ALV:n ja toimituksen Viron sisällä', req='Katalysaattorillisen version hinta pyynnöstä', other='Muut', filt='Merkki',
            wa='Hei! Kysyisin tuotteesta {name}. Autoni: ',
            vid='Miltä iPE kuulostaa: valmistajan video', play='Katso video', vnote='Video on iPE:n omalta YouTube-kanavalta. YouTube-soitin latautuu vasta, kun painat videota.')

def systems_n(n, lang):
    if lang == 'en':
        return f'{n} system' + ('' if n == 1 else 's')
    if lang == 'et':
        return f'{n} süsteem' + ('' if n == 1 else 'i')
    if lang == 'fi':
        return f'{n} järjestelmä' + ('' if n == 1 else 'ä')
    w = 'система' if n % 10 == 1 and n % 100 != 11 else 'системы' if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else 'систем'
    return f'{n} {w}'

def fi_autoihin(m):
    """Porsche-autoihin, Mercedes-AMG-autoihin, mutta Aston Martin -autoihin (monisanainen nimi: välilyönti ja yhdysmerkki)."""
    return m + (' -autoihin' if ' ' in m else '-autoihin')

# --- Названия машин -----------------------------------------------------------------------------------------------
# Названия машин берутся из заголовков магазина и местами грязные («Pipe BMW F32 420i / 428i», «Ferrari 296 - Catback Exhaust»,
# «W463 (, )», «G80 G81 M3 G82 G83 M4»). Чистим здесь, один раз и для всех языков.
ROMAN = {'VIII': '8', 'VII': '7', 'VI': '6', 'V': '5'}
# Точечные исправления после общей чистки: «что подходит» (название машины у конкретной системы)
FIX = {
    'Porsche 911 Turbo S (992.2)': 'Porsche 992.2 Turbo S',
    'Porsche 970.2 Panamera (4)': 'Porsche 970.2 Panamera / 4',
    'Porsche 971 Panamera (4)': 'Porsche 971 Panamera / 4',
    'Porsche 991 Turbo (S)': 'Porsche 991 Turbo / Turbo S',
    'Porsche 991 / 991.2 GT3 (RS)': 'Porsche 991 / 991.2 GT3 / GT3 RS',
    'Porsche 992 GT3 (RS)': 'Porsche 992 GT3 / GT3 RS',
    'Porsche 992.2 GTS': 'Porsche 992.2 Carrera GTS',
    'Porsche Macan 2.0': 'Porsche Macan 2.0T',
    'Mercedes W176 A45 AMG': 'Mercedes A45 AMG W176',
    'Mercedes W204 C63 AMG': 'Mercedes C63 AMG W204',
    'Mercedes G500 W463 W464': 'Mercedes G500 W463 / W464',
    'Mercedes G63 AMG W463A W464': 'Mercedes G63 AMG W463A / W464',
    'Mercedes-Benz E63 AMG (W212)': 'Mercedes E63 AMG W212',
    'Mercedes E63 AMG (W212) M157': 'Mercedes E63 AMG W212 (M157)',
    'Mercedes-AMG GTR': 'Mercedes-AMG GT R',
    'BMW G80 G81 M3 G82 G83 M4': 'BMW M3 / M4 (G80 / G81 / G82 / G83)',
    'BMW G05 X5 40i X6 G06': 'BMW G05 X5 40i / G06 X6 40i',
    'BMW M2 F87': 'BMW F87 M2',
    'BMW M2 G87': 'BMW G87 M2',
    'BMW M2 Competition': 'BMW F87 M2 Competition',
    'BMW M5 F90': 'BMW F90 M5',
    'BMW M5 G90 / G99': 'BMW G90 / G99 M5',
    'BMW M6 F12 / F13 / F06': 'BMW F12 / F13 / F06 M6',
    'Audi C8 A7 3.0T 55tfsi': 'Audi C8 A7 3.0T 55 TFSI',
    'Audi A7 C8 3.0T': 'Audi C8 A7 3.0T',
    'Audi R8 RWD Coupe / Spyder 5.2FSI V10': 'Audi R8 RWD Coupe / Spyder V10 5.2 FSI',
    'Volkswagen Golf 7 GTI Mk7': 'Volkswagen Golf GTI Mk7',
    'Lamborghini Aventador LP750-4 SV': 'Lamborghini Aventador SV LP750-4',
    'Maserati Ghibli (S)': 'Maserati Ghibli / Ghibli S',
    'Maserati Levante (S)': 'Maserati Levante / Levante S',
}
# Какие машины показываем на одной странице: системы для близких модификаций (GT3 и GT3 RS, CLA250 и CLA250 C117)
GROUP = {
    'Porsche 992 GT3': 'Porsche 992 GT3 / GT3 RS',
    'Porsche 992 GT3 RS': 'Porsche 992 GT3 / GT3 RS',
    'Mercedes E63 AMG W212 (M157)': 'Mercedes E63 AMG W212',
    'Mercedes CLA250': 'Mercedes CLA250 C117',
    'Mercedes-AMG GT S': 'Mercedes-AMG GT / GT S / GT C',
    'BMW G05 X5 40i': 'BMW G05 X5 40i / G06 X6 40i',
    'Audi C8 A7 3.0T': 'Audi C8 A7 3.0T 55 TFSI',
    'Maserati Ghibli / Ghibli S': 'Maserati Ghibli',
}

def clean_car(c):
    c = html.unescape(c)
    c = re.sub(r'^(Pipe|s)\s+', '', c)                       # «Cat Pipes for Pipe BMW ...», «Downpipes for s Mercedes ...»
    c = re.sub(r'\s*-\s*(Catback Exhaust|Downpipes)$|\s+Catback$|\s*\(,\s*\)$', '', c)
    c = re.sub(r'\s+&\s+', ' / ', c)
    c = re.sub(r'(\w)\(', r'\1 (', c)                         # M440i(B58)
    c = re.sub(r'\s*/\s*', ' / ', c)                          # G90/G99, Coupe/Spyder
    c = re.sub(r'\bMk(VIII|VII|VI|V)\b', lambda m: 'Mk' + ROMAN[m.group(1)], c)
    c = re.sub(r'\s+', ' ', c).strip()
    return FIX.get(c, c)

def clean_name(title, fits, used):
    """Название системы для заявки, WhatsApp и JSON-LD (английское, как у производителя): без «iPE iPE», «for Pipe BMW», «- Downpipes»."""
    t = re.sub(r'^\s*(pre-?owned\s+)?ipe\s+', '', html.unescape(title), flags=re.I).strip()
    m = re.search(r'\s+for\s+', t, re.I) or re.search(r'\s+[–-]\s+', t)
    kind = t[:m.start()] if m else t
    kind = re.sub(r'^Catted or Catless\s+', 'Catted ', kind, flags=re.I).replace('Cat Bypass Pipes', 'Cat Pipes')
    return ('Pre-owned ' if used else '') + f'iPE {kind} for {fits}'

def car(d, lang=None):
    """Название машины на странице (одинаковое для всех языков, суффиксы языка не нужны)."""
    return d['car']

# Päätteiden viimeistelyt kaupan englanninkielisistä nimistä (Red Mamba ja Black Mamba ovat iPE:n tuotenimiä)
FIN_FI = {
    '3D Carbon Tips - Satin Black': '3D-hiilikuitupäätteet, satiinimusta', '3D Carbon Tips - Satin Gold': '3D-hiilikuitupäätteet, satiinikulta',
    '3D Carbon Tips - Satin Silver': '3D-hiilikuitupäätteet, satiinihopea', '89mm Red Mamba Tips (carbon & titanium)': '89 mm Red Mamba -päätteet (hiilikuitu ja titaani)',
    'Black': 'musta', 'Black Chrome': 'musta kromi', 'Black chrome': 'musta kromi', 'Black Mamba carbon tailpipes': 'Black Mamba -hiilikuitupäätteet',
    'Black mamba carbon': 'Black Mamba, hiilikuitu', 'Carbon': 'hiilikuitu', 'Carbon Fiber': 'hiilikuitu', 'Carbon and black': 'hiilikuitu ja musta',
    'Carbon and gold': 'hiilikuitu ja kulta', 'Chrome': 'kromi', 'Chrome Black': 'musta kromi', 'Chrome Black - new design': 'musta kromi, uusi malli',
    'Chrome Black Dual Out': 'musta kromi, kaksoispäätteet', 'Chrome Black Tips': 'mustat kromipäätteet', 'Chrome Black Triple-out': 'musta kromi, kolmoispäätteet',
    'Chrome Polished': 'kiillotettu kromi', 'Chrome Silver Dual Out': 'hopeinen kromi, kaksoispäätteet', 'Chrome Silver Triple-out': 'hopeinen kromi, kolmoispäätteet',
    'Chrome black': 'musta kromi', 'Chrome polished': 'kiillotettu kromi', 'Chrome silver': 'hopeinen kromi',
    'Dual-Out Chrome Black': 'kaksoispäätteet, musta kromi', 'Dual-Out Chrome Polished': 'kaksoispäätteet, kiillotettu kromi', 'Dual-Out Gold': 'kaksoispäätteet, kulta',
    'Gold': 'kulta', 'Matt Black with forged carbon': 'mattamusta ja taottu hiilikuitu', 'Matt Gold with forged carbon': 'mattakulta ja taottu hiilikuitu',
    'Optional Black Chrome': 'lisävarusteena musta kromi', 'Optional Chrome black': 'lisävarusteena musta kromi',
    'Oval Chrome Black': 'soikeat, musta kromi', 'Oval Chrome polished': 'soikeat, kiillotettu kromi', 'Oval Titanium Blue': 'soikeat, sininen titaani',
    'Polished Chrome': 'kiillotettu kromi', 'Standard Chrome Silver': 'vakiona hopeinen kromi', 'Standard polished chrome': 'vakiona kiillotettu kromi',
    'Tailpipes Carbon': 'hiilikuitupäätteet', 'Tailpipes Chrome black': 'mustat kromipäätteet', 'Tailpipes Titanium blue': 'siniset titaanipäätteet',
    'Tailpipes carbon fiber': 'hiilikuitupäätteet', 'Tailpipes chrome silver': 'hopeiset kromipäätteet',
    'Tips (Chrome Black)': 'päätteet: musta kromi', 'Tips (Satin Gold)': 'päätteet: satiinikulta', 'Tips (Satin Silver)': 'päätteet: satiinihopea',
    'Titanium (Chrome, Gold or Blue)': 'titaani (kromi, kulta tai sininen)', 'Titanium Blue': 'sininen titaani', 'Titanium Blue - NEW': 'sininen titaani, uutuus',
    'Titanium Blue - new design': 'sininen titaani, uusi malli', 'Titanium Blue Dual Out': 'sininen titaani, kaksoispäätteet',
    'Titanium Blue Triple-out': 'sininen titaani, kolmoispäätteet', 'Titanium Chrome': 'titaani, kromi', 'Titanium Chrome Black': 'titaani, musta kromi',
    'Titanium Chrome Polished': 'titaani, kiillotettu kromi', 'Titanium Gold': 'kultainen titaani', 'Titanium Polished Silver': 'titaani, kiillotettu hopea',
    'Titanium blue': 'sininen titaani', 'Titanium gold': 'kultainen titaani', 'Triple-Out Chrome Polished': 'kolmoispäätteet, kiillotettu kromi',
    'Triple-Out Titanium Blue': 'kolmoispäätteet, sininen titaani'}

def fin_name(x, lang):
    if lang != 'fi':
        return re.sub(r'\s+[–—-]\s+', ', ', x)  # «Titanium Blue - NEW»: без тире в видимом тексте
    f = FIN_FI.get(x, x)
    return f[:1].upper() + f[1:]

def mk(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()  # Huracán -> huracan
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def parse(it):
    title = re.sub(r'^\s*(pre-?owned\s+)?ipe\s+', '', it['title'], flags=re.I).strip()
    m = re.search(r'\bfor\s+(.+)$', title, re.I) or re.search(r'[–-]\s+(.+)$', title)
    raw = (m.group(1) if m else title).strip()
    raw = re.sub(r'\s+(in|with)$', '', raw)
    fits = clean_car(raw)
    used = bool(re.match(r'\s*pre-?owned', it['title'], re.I))
    make = next((ALIAS.get(x, x) for x in MAKES if re.search(r'\b' + re.escape(x) + r'\b', fits, re.I)), None)
    tlow = it['title'].lower()
    typ = next((tt for tt in TYPES if re.search(tt[0], tlow)), TYPE_BY_KEY['full'])
    mat = 'ti' if 'titanium' in tlow else 'ss'
    good = [float(p) for v, p in it['variants'] if p and float(p) > 0 and not BAD.search(v)]
    price = W.setp(min(good) / 1.21 / 4) if good else None
    fin = []
    for v, _ in it['variants']:
        for part in re.split(r'\s*/\s*|\s*\|\s*', v):
            part = re.sub(r'\s*\(standard\)', '', part).strip()
            if re.search(r'chrome|titanium (blue|gold|polished|chrome)|carbon|satin|gold|black', part, re.I) and len(part) < 40 and part not in fin:
                fin.append(part)
    return dict(raw=raw, fits=fits, car=GROUP.get(fits, fits), used=used, make=make or T['en']['other'], typ=typ, mat=mat, p=price, fin=fin[:8],
                name=clean_name(it['title'], fits, used))

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
for d in ITEMS:  # уникальные адреса систем (теперь это id секций и ключи редиректов)
    base, n = d['slug'], 2
    while d['slug'] in _seen:
        d['slug'] = f"{base}-{n}"; n += 1
    _seen.add(d['slug'])
# Порядок секций на странице машины: сначала полные системы и клапанные части, потом передняя часть выхлопа
TYPE_IDX = {k: i for i, k in enumerate(['full', 'catback', 'muffler', 'elheader', 'header', 'downpipe', 'catpipe', 'link', 'xpipe', 'front', 'tips'])}
ITEMS.sort(key=lambda d: (MAKES.index(d['make']) if d['make'] in MAKES else 99, d['car'], TYPE_IDX[d['typ'][4]], d['mat'] != 'ti', d['used'], d['p'] or 0))

# Машины: одна страница на машину
CARS, CAR_BY = [], {}
for d in ITEMS:
    if d['car'] not in CAR_BY:
        CAR_BY[d['car']] = dict(car=d['car'], make=d['make'], slug=mk(d['car']), items=[])
        CARS.append(CAR_BY[d['car']])
    CAR_BY[d['car']]['items'].append(d)
    d['cslug'] = CAR_BY[d['car']]['slug']
for c in CARS:
    _k = [(x['typ'][4], x['mat'], x['ed'], x['used'], x['fits']) for x in c['items']]
    for x, k in zip(c['items'], _k):
        x['dup'] = _k.count(k) > 1  # две похожие системы для одной машины: показываем точное название и цену в оглавлении
    pr = [x['p'] for x in c['items'] if x['p']]
    c['p'] = min(pr) if pr else None
    c['imgs'] = c['items'][0]['imgs']
_MAKE_SLUGS = {mk(d['make']) for d in ITEMS}
_cs = [c['slug'] for c in CARS]
assert len(set(_cs)) == len(_cs), 'две машины с одинаковым адресом'
assert not set(_cs) & _MAKE_SLUGS, 'адрес машины совпадает с адресом марки'
assert not set(_cs) & _seen, 'адрес машины совпадает со старым адресом системы'

def tlabel(d, lang, cap=False):
    """Тип системы на нужном языке, с материалом и исполнением (F1 Sound, Evolution), б/у в скобках."""
    t = T[lang]
    if lang == 'fi':
        tl = TYPES_FI[d['typ'][4]][1 if d['mat'] == 'ti' else 0] + (' ' + d['ed'] if d['ed'] else '')
    else:
        tl = {'ru': d['typ'][1], 'et': d['typ'][2], 'en': d['typ'][3].lower()}[lang]
        if d['ed']:
            tl += ' ' + d['ed']
        if d['mat'] == 'ti':
            tl = {'ru': tl + ' из титана', 'et': 'Titaanist ' + tl[0].lower() + tl[1:], 'en': 'titanium ' + tl}[lang]
    if d['used']:
        tl += f" ({t['used']})"
    return (tl[:1].upper() + tl[1:]) if cap else tl

def names(d, lang):
    """(полное название системы с машиной, тип системы)."""
    tl = tlabel(d, lang)
    return T[lang]['sys'].format(t=tl, car=d['fits']), tl

def lower1(s):
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1].islower() else s

def join(xs, lang):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + f" {T[lang]['conj']} " + xs[-1]

def type_names(items, lang, only=None):
    out = []
    for d in items:
        k = d['typ'][4]
        if only is not None and k not in only:
            continue
        n = TYPES_FI[k][0] if lang == 'fi' else lower1({'ru': d['typ'][1], 'et': d['typ'][2], 'en': d['typ'][3]}[lang])
        if n not in out:
            out.append(n)
    return out

def mats(items, lang):
    t = T[lang]
    ms = [m for m in ('ti', 'ss') if any(d['mat'] == m for d in items)]
    return f" {t['mat_or']} ".join(t['mat_' + m] for m in ms)

def nodash(s):
    """Правило сайта: без длинных тире. В английских названиях с YouTube они есть («Macan (95B.2) – iPE ...»)."""
    return re.sub(r'\s+[–—]\s+', ': ', s).replace('–', '-').replace('—', '-')

def finish(out, lang):
    out = nodash(out)
    return W.fi_fix(out) if lang == 'fi' else out

header = W.header

# Официальные ролики iPE с YouTube (tools/ipe_videos.json). Встраиваем только с YouTube, сами ролики не загружаем.
# До клика грузится только превью с i.ytimg.com, плеер youtube-nocookie.com подключается по нажатию.
VIDS = json.load(open(os.path.join(TOOLS, 'ipe_videos.json')))
VID_BY_ID = {v['id']: v for v in VIDS['videos']}

def video_for(d):
    """Ролик для машины: первый ролик, чей шаблон подходит к названию машины или к названию любой её системы (чистому и исходному)."""
    c = CAR_BY.get(d['car'], d) if isinstance(d, dict) else d
    nm = [c['car']] + [x for it in c.get('items', [d]) for x in (it['fits'], it['raw'])]
    return next((v for v in VIDS['videos'] if any(re.search(v['match'], n, re.I) for n in nm)), None)

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

# Страница машины: несколько галерей на странице. Миниатюры переключаем внутри своей секции (.xg), а не по всей странице,
# поэтому класс миниатюр свой (.xth), а не .thumbs из wheel.js. Увеличение (.shot -> .lb) работает через wheel.js.
CAR_CSS = ('<style>.xhead{padding-block:12px 8px}.xhead h1{font-size:clamp(30px,6vw,56px);text-wrap:balance;overflow-wrap:anywhere}'
           '.xhead p{max-width:66ch;color:var(--graphite);margin-top:14px}.xhead .facts{max-width:66ch;margin-top:18px}'
           '.xhead .chips a{scroll-margin-top:96px}.xjump{font-size:14px;color:var(--machined);margin-top:22px}.xjump+.chips{margin-top:8px}'
           '.xs{border-top:1px solid var(--steel);padding-top:40px;margin-top:24px;scroll-margin-top:72px}'
           '.xs .info h2.xn{font-size:clamp(26px,2.8vw,38px);margin-top:6px;overflow-wrap:anywhere;hyphens:auto;text-wrap:balance}'
           '.xs .fitl{color:var(--graphite);margin-top:8px}.xs .info h3{font-size:18px;margin-top:28px}'
           '.xth{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}.xth button{width:84px;height:84px;border-radius:12px;background:var(--white);border:2px solid transparent;padding:6px;cursor:pointer}'
           '.xth button.on{border-color:var(--ink)}.xth img{width:100%;height:100%;object-fit:contain}@media (max-width:520px){.xth button{width:64px;height:64px}}</style>\n')
CAR_JS = ("<script>document.querySelectorAll('.xg').forEach(function(g){var s=g.querySelectorAll('.shot'),t=g.querySelectorAll('.xth button');"
          "t.forEach(function(b,i){b.addEventListener('click',function(){s.forEach(function(x,n){x.classList.toggle('on',n===i)});t.forEach(function(x,n){x.classList.toggle('on',n===i)})})})})</script>\n")

def video_block(v, lang):
    t = T[lang]
    vid, ttl = v['id'], esc(v['title'])
    return (f'<section class="vid" aria-labelledby="vid-h"><h2 id="vid-h">{t["vid"]}</h2>'
            f'<div class="yt"><a href="https://www.youtube.com/watch?v={vid}" data-id="{vid}" data-t="{ttl}" target="_blank" rel="noopener noreferrer" aria-label="{t["play"]}: {ttl}">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" width="480" height="360" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            f'<span class="pl" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span></a></div>'
            f'<p class="vcap"><b>{ttl}</b> · YouTube, iPE</p><p class="vcap">{t["vnote"]}</p></section>\n')

def card(c, lang):
    """Карточка машины в каталоге: сколько систем и цена «от»."""
    w, hgt = W.dims(c['imgs'][0])
    price = W.fmt(c['p'], lang) if c['p'] else W.T[lang]['on_request']
    return (f'<a class="card" data-make="{esc(c["make"])}" href="/{LANGS[lang]}exhaust/{c["slug"]}/"><div class="stage"><img src="{c["imgs"][0]}" width="{w}" height="{hgt}" loading="lazy" decoding="async" alt="{esc(T[lang]["h1"].format(car=c["car"]))}"></div>'
            f'<span class="brand">iPE</span><h3>{esc(c["car"])}</h3><div class="spec"><span>{systems_n(len(c["items"]), lang)}</span></div><div class="price">{price}</div></a>')

def section(d, lang, url, first):
    t, wt = T[lang], W.T[lang]
    full, tl = names(d, lang)
    head = tlabel(d, lang, cap=True)
    p = '/' + LANGS[lang]
    mat = t['mat_ti'] if d['mat'] == 'ti' else t['mat_ss']
    gal = ''.join(f'<button type="button" class="shot{" on" if n == 0 else ""}" data-big="{W.big(i)}" aria-label="{wt["zoom"]}"><img src="{i}" width="{W.dims(i)[0]}" height="{W.dims(i)[1]}" alt="{esc(full)}" {"fetchpriority=\"high\"" if first and n == 0 else "loading=\"lazy\""} decoding="async"></button>' for n, i in enumerate(d['imgs']))
    thumbs = ('<div class="xth">' + ''.join(f'<button type="button" aria-label="{n+1}"{" class=\"on\"" if n == 0 else ""}><img src="{i}" alt="" loading="lazy" decoding="async"></button>' for n, i in enumerate(d['imgs'])) + '</div>') if len(d['imgs']) > 1 else ''
    price = (f'<div class="price">{W.fmt(d["p"], lang)}</div><p class="pnote">{t["note"]}</p>' if d['p'] else f'<div class="price">{wt["on_request"]}</div><p class="pnote">{t["req"]}</p>')
    name = d['name']
    if lang == 'fi':  # WhatsApp-viesti ja ?model= ovat URL-koodattuja, joten fi_fix ei näe niitä koko sivusta
        name = W.fi_fix(name)
    wa = 'https://wa.me/' + W.WA + '?text=' + urllib.parse.quote(t['wa'].format(name=name))
    fits = f'<p class="fitl">{esc(t["fits"].format(car=d["fits"]))}</p>' if d['fits'] != d['car'] else ''
    if d['dup']:
        fits += f'<p class="fitl">{esc(d["name"])}</p>'
    fin = f'<h3>{t["finishes"]}</h3><div class="chips">{"".join(f"<span>{esc(fin_name(x, lang))}</span>" for x in d["fin"])}</div>' if d['fin'] else ''
    facts = ''.join(f'<li>{x}</li>' for x in FACTS[d['typ'][4]][lang])
    return f'''<section class="prod xs" id="{d['slug']}">
<div class="gallery xg"><div class="main">{gal}</div>{thumbs}<p class="hint">{wt['zoom']}</p></div>
<div class="info">
<div class="brand">iPE</div>
<h2 class="xn">{esc(head)}</h2>
{fits}<div class="spec"><span>{esc(mat)}</span></div>
{price}
<div class="ctas"><a class="btn" href="{p}?model={urllib.parse.quote(name[:60])}#quote">{wt['cta']}</a><a class="btn ghost" href="{wa}" target="_blank" rel="noopener noreferrer">{wt['wa']}</a></div>
<ul class="facts">{facts}</ul>
{fin}
</div>
</section>
'''

def jlabel(d, c, lang):
    s = tlabel(d, lang, cap=True) + ('' if d['fits'] == c['car'] else ', ' + d['fits'])
    return s + (', ' + W.fmt(d['p'], lang) if d['dup'] and d['p'] else '')

def page(c, lang):
    t, wt = T[lang], W.T[lang]
    items = c['items']
    alts = {l: f"{SITE}/{LANGS[l]}exhaust/{c['slug']}/" for l in LANGS}
    url = alts[lang]
    h1 = t['h1'].format(car=c['car'])
    title = W.fit(t['title'].format(car=c['car']), t['short'].format(car=c['car']))
    tn = type_names(items, lang)
    ms = mats(items, lang)
    pr = W.fmt(c['p'], lang) if c['p'] else ''
    types_d = join(tn, lang)
    desc = t['desc'].format(types=types_d, car=c['car'], mats=ms, price=(' ' + pr[:1].upper() + pr[1:] + '.') if pr else '')
    og = SITE + W.big(c['imgs'][0])
    out = W.head_common(lang, title, desc, url, alts, og)
    graph = []
    for d in items:
        if not d['p']:
            continue  # Product без цены Google не принимает: показываем систему, но без разметки
        u = f"{url}#{d['slug']}"
        mat = t['mat_ti'] if d['mat'] == 'ti' else t['mat_ss']
        graph.append({"@type": "Product", "@id": u, "name": d['name'], "brand": {"@type": "Brand", "name": "iPE"},
                      "image": [SITE + W.big(i) for i in d['imgs']], "url": u,
                      "description": t['sys_desc'].format(t=tlabel(d, lang), car=d['fits'], mat=mat),
                      "offers": W.offer(d['p'], u, 'iPE', W.SHIP_EXHAUST)})
    p = '/' + LANGS[lang]
    graph.append({"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nordvelg", "item": f"{SITE}{p}"},
        {"@type": "ListItem", "position": 2, "name": t['sec'], "item": f"{SITE}{p}exhaust/"},
        {"@type": "ListItem", "position": 3, "name": c['make'], "item": f"{SITE}{p}exhaust/{mk(c['make'])}/"},
        {"@type": "ListItem", "position": 4, "name": c['car'], "item": url}]})
    v = video_for(c)
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':')) + '</script>\n' + CAR_CSS + (VID_CSS if v else '') + '</head>\n<body>\n'
    out += header(lang, alts)
    out += (f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs"><a href="{p}">Nordvelg</a><span>/</span><a href="{p}exhaust/">{t["sec"]}</a>'
            f'<span>/</span><a href="{p}exhaust/{mk(c["make"])}/">{esc(c["make"])}</a><span>/</span><span aria-current="page">{esc(c["car"])}</span></nav>\n')
    vt = type_names(items, lang, VALVED)
    intro = t['intro'].format(types=join(tn, lang), mats=ms) + ((' ' + t['intro_v'].format(types=join(vt, lang))) if vt else '')
    jump = ''
    if len(items) > 1:
        jump = (f'<p class="xjump">{t["jump"]}</p><div class="chips">' +
                ''.join(f'<a href="#{d["slug"]}">{esc(jlabel(d, c, lang))}</a>' for d in items) + '</div>')
    out += (f'<section class="xhead"><div class="brand">iPE</div><h1>{esc(h1)}</h1><p>{esc(intro)}</p>{jump}'
            f'<h2 class="xjump">{wt["know"]}</h2><ul class="facts">{"".join(f"<li>{x}</li>" for x in t["facts"])}</ul></section>\n')
    for n, d in enumerate(items):
        out += section(d, lang, url, n == 0)
    if v:
        out += video_block(v, lang)
    rel = [x for x in CARS if x['make'] == c['make'] and x is not c][:4]
    out += f'<section class="rel"><div class="rh"><h2>{t["more"].format(m=c["make"], ma=fi_autoihin(c["make"]))}</h2><a href="{p}exhaust/{mk(c["make"])}/">{t["all"]}</a></div><div class="grid">{"".join(card(x, lang) for x in rel)}</div></section>\n</main>\n' if rel else '</main>\n'
    out += f'<div class="lb" hidden><button type="button" class="x" aria-label="{wt["close"]}">×</button></div>\n' + W.footer(lang) + CAR_JS + (VID_JS if v else '')
    out += f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return finish(out, lang)

def catalog(lang, make=None):
    t = T[lang]
    sub = f"exhaust/{mk(make)}/" if make else "exhaust/"
    alts = {l: f"{SITE}/{LANGS[l]}{sub}" for l in LANGS}
    sel = [c for c in CARS if make is None or c['make'] == make]
    ma = fi_autoihin(make) if make else ''
    title = W.fit(t['make_title'].format(m=make, ma=ma) if make else t['cat_title'])
    desc = t['make_desc'].format(m=make, ma=ma) if make else t['cat_desc']
    h1 = t['make_h1'].format(m=make, ma=ma) if make else t['cat_h1']
    out = W.head_common(lang, title, desc, alts[lang], alts, SITE + W.big(sel[0]['imgs'][0]))
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{LANGS[lang]}exhaust/{c['slug']}/", "name": t['h1'].format(car=c['car'])} for i, c in enumerate(sel)]
    v = VID_BY_ID.get(VIDS['makes'].get(make) if make else VIDS['brand'])
    out += '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": h1, "itemListElement": items}, ensure_ascii=False, separators=(',', ':')) + '</script>\n' + (VID_CSS if v else '') + '</head>\n<body>\n'
    out += header(lang, alts)
    p = '/' + LANGS[lang]
    crumbs = f'<a href="{p}">Nordvelg</a><span>/</span>' + (f'<a href="{p}exhaust/">{t["sec"]}</a><span>/</span><span aria-current="page">{esc(make)}</span>' if make else f'<span aria-current="page">{t["sec"]}</span>')
    out += f'<main class="wrap">\n<nav class="crumbs" aria-label="breadcrumbs">{crumbs}</nav>\n<section class="cathead"><h1>{esc(h1)}</h1><p>{t["cat_sub"]}</p></section>\n'
    makes = []
    for c in sel:
        if c['make'] not in makes:
            makes.append(c['make'])
    if not make:
        out += '<div class="chips makes">' + ''.join(f'<a href="{p}exhaust/{mk(m)}/">{esc(m)} <b>{sum(1 for c in CARS if c["make"] == m)}</b></a>' for m in makes) + '</div>\n'
    for m in makes:
        mm = [c for c in sel if c['make'] == m]
        show = mm if make else mm[:8]
        head = '' if make else f'<div class="rh"><h2>{esc(m)}</h2><a href="{p}exhaust/{mk(m)}/">{t["all_make"].format(m=m, n=len(mm))}</a></div>'
        out += f'<section class="rel">{head}<div class="grid">{"".join(card(c, lang) for c in show)}</div></section>\n'
    if v:
        out += video_block(v, lang)
    out += '</main>\n' + W.footer(lang) + (VID_JS if v else '') + f'<script src="/js/wheel.js?v={V("js/wheel.js")}" defer></script>\n</body>\n</html>\n'
    return finish(out, lang)

REDIRECTS = {d['slug']: f"{d['cslug']}/#{d['slug']}" for d in ITEMS}

def main():
    paths = ['exhaust/']
    keep = {mk(m) for m in {d['make'] for d in ITEMS}} | {c['slug'] for c in CARS}
    for lang in LANGS:
        base = os.path.join(ROOT, LANGS[lang], 'exhaust')
        os.makedirs(base, exist_ok=True)
        # старые сгенерированные страницы систем (в папке только index.html) убираем, иначе они попадут в sitemap
        for x in os.listdir(base):
            dp = os.path.join(base, x)
            if os.path.isdir(dp) and x not in keep and os.listdir(dp) == ['index.html']:
                shutil.rmtree(dp)
        open(os.path.join(base, 'index.html'), 'w').write(catalog(lang))
        for m in sorted({d['make'] for d in ITEMS}):
            os.makedirs(os.path.join(base, mk(m)), exist_ok=True)
            open(os.path.join(base, mk(m), 'index.html'), 'w').write(catalog(lang, m))
            if LANGS[lang] == '':
                paths.append(f'exhaust/{mk(m)}/')
        for c in CARS:
            os.makedirs(os.path.join(base, c['slug']), exist_ok=True)
            open(os.path.join(base, c['slug'], 'index.html'), 'w').write(page(c, lang))
            if LANGS[lang] == '':
                paths.append(f'exhaust/{c["slug"]}/')
    json.dump(paths, open(os.path.join(TOOLS, 'exhaust.json'), 'w'), indent=0)
    json.dump(dict(sorted(REDIRECTS.items())), open(os.path.join(TOOLS, 'redirects-exhaust.json'), 'w'), indent=1)
    print(len(ITEMS), 'exhaust systems on', len(CARS), 'car pages,', len(paths), 'paths per language,', len(REDIRECTS), 'redirects,',
          sum(1 for c in CARS if video_for(c)), 'car pages with an iPE video')

if __name__ == '__main__':
    main()
