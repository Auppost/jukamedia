#!/usr/bin/env python3
"""Политика конфиденциальности Nordvelg: /privacy/, /et/privacy/, /en/privacy/ (noindex)."""
import os
import build_wheels as W

ROOT, SITE, LANGS = W.ROOT, W.SITE, W.LANGS

P = {
 'ru': dict(title='Политика конфиденциальности | Nordvelg', h1='Политика конфиденциальности', desc='Как Nordvelg обрабатывает данные из заявок.', body='''
<p>Здесь коротко и честно о том, какие данные вы нам передаёте через сайт nordvelg.com и что мы с ними делаем.</p>
<h2>Кто обрабатывает данные</h2>
<p>Juka Media OÜ, регистрационный код 17495980, Таллинн, Эстония. Связь по вопросам данных: <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>.</p>
<h2>Какие данные мы получаем</h2>
<p>Только то, что вы сами указали в форме расчёта: имя, телефон или e-mail, марка, модель и год машины, пожелания по дискам и комментарий. Сайт не ставит рекламных cookies и не ведёт аналитику посетителей.</p>
<h2>Как данные к нам попадают</h2>
<ul>
<li>Когда вы нажимаете «Отправить в Telegram» или «Отправить в WhatsApp», текст заявки открывается в выбранном мессенджере. Там действуют правила этого мессенджера.</li>
<li>В тот же момент копия заявки приходит нам на e-mail через сервис Formspree (Formspree, Inc., США). Это нужно, чтобы заявка не потерялась, если сообщение в мессенджере не отправится. Передача в США идёт на условиях стандартных договорных положений ЕС.</li>
</ul>
<h2>Видео с YouTube</h2>
<p>На страницах выхлопных систем есть ролики iPE с YouTube. Пока вы не нажали на видео, с серверов YouTube загружается только картинка-превью. Сам плеер подключается после нажатия, через youtube-nocookie.com, и дальше действуют правила Google (<a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>).</p>
<h2>Зачем</h2>
<p>Только чтобы ответить на ваш запрос: подобрать диски, рассчитать цену и подготовить эскиз. Правовое основание: ваш запрос и подготовка договора (статья 6(1)(b) GDPR). Мы не продаём данные и не используем их для рассылок без вашего согласия.</p>
<h2>Сколько храним</h2>
<p>Переписку по заявке храним до 12 месяцев. Если вы стали клиентом, данные заказа храним столько, сколько требует бухгалтерский учёт в Эстонии (7 лет).</p>
<h2>Ваши права</h2>
<p>Вы можете попросить показать, исправить или удалить ваши данные, а также возразить против обработки. Напишите на <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>, ответим в течение месяца. Если считаете, что ваши права нарушены, можно обратиться в Инспекцию по защите данных Эстонии (Andmekaitse Inspektsioon, <a href="https://www.aki.ee" target="_blank" rel="noopener noreferrer">aki.ee</a>).</p>
<p class="upd">Обновлено 28 октября 2026 года</p>
'''),
 'et': dict(title='Privaatsuspoliitika | Nordvelg', h1='Privaatsuspoliitika', desc='Kuidas Nordvelg päringute andmeid töötleb.', body='''
<p>Lühidalt ja ausalt sellest, milliseid andmeid te meile nordvelg.com kaudu edastate ja mida me nendega teeme.</p>
<h2>Vastutav töötleja</h2>
<p>Juka Media OÜ, registrikood 17495980, Tallinn, Eesti. Andmetega seotud küsimused: <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>.</p>
<h2>Milliseid andmeid saame</h2>
<p>Ainult need, mille te ise hinnapäringu vormis sisestate: nimi, telefon või e-post, auto mark, mudel ja aasta, soovid velgede kohta ja kommentaar. Sait ei kasuta reklaamiküpsiseid ega külastajate analüütikat.</p>
<h2>Kuidas andmed meieni jõuavad</h2>
<ul>
<li>Kui vajutate „Saada Telegrami“ või „Saada WhatsAppi“, avaneb päringu tekst valitud sõnumirakenduses. Seal kehtivad selle rakenduse reeglid.</li>
<li>Samal hetkel saadetakse päringu koopia meie e-postile teenuse Formspree (Formspree, Inc., USA) kaudu, et päring ei kaoks. Andmete edastamine USA-sse toimub ELi tüüptingimuste alusel.</li>
</ul>
<h2>YouTube’i videod</h2>
<p>Väljalaskesüsteemide lehtedel on iPE videod YouTube’ist. Enne video peale vajutamist laaditakse YouTube’i serveritest ainult eelvaate pilt. Mängija ühendatakse alles pärast vajutamist, youtube-nocookie.com kaudu, ja edasi kehtivad Google’i reeglid (<a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>).</p>
<h2>Milleks</h2>
<p>Ainult teie päringule vastamiseks: velgede valik, hinnapakkumine ja eskiis. Õiguslik alus: teie taotlus ja lepingu ettevalmistamine (IKÜM artikkel 6 lõige 1 punkt b). Me ei müü andmeid ega saada uudiskirju ilma teie nõusolekuta.</p>
<h2>Kui kaua säilitame</h2>
<p>Päringu kirjavahetust säilitame kuni 12 kuud. Kui teist saab klient, säilitame tellimuse andmeid nii kaua, kui nõuab Eesti raamatupidamisseadus (7 aastat).</p>
<h2>Teie õigused</h2>
<p>Võite paluda oma andmeid näha, parandada või kustutada ning esitada vastuväite töötlemisele. Kirjutage <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>, vastame kuu aja jooksul. Kui leiate, et teie õigusi on rikutud, võite pöörduda Andmekaitse Inspektsiooni poole (<a href="https://www.aki.ee" target="_blank" rel="noopener noreferrer">aki.ee</a>).</p>
<p class="upd">Uuendatud 28. oktoobril 2026</p>
'''),
 'en': dict(title='Privacy Policy | Nordvelg', h1='Privacy policy', desc='How Nordvelg handles the data in quote requests.', body='''
<p>A short, plain account of what data you send us through nordvelg.com and what we do with it.</p>
<h2>Who processes the data</h2>
<p>Juka Media OÜ, registry code 17495980, Tallinn, Estonia. Data questions: <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>.</p>
<h2>What we receive</h2>
<p>Only what you enter in the quote form: name, phone or e-mail, your car's make, model and year, wheel preferences and a comment. The site uses no advertising cookies and no visitor analytics.</p>
<h2>How it reaches us</h2>
<ul>
<li>When you press "Send via Telegram" or "Send via WhatsApp", the request text opens in that messenger, and its own terms apply there.</li>
<li>At the same moment a copy of the request is sent to our e-mail through Formspree (Formspree, Inc., USA), so the request is not lost. Transfers to the USA rely on the EU standard contractual clauses.</li>
</ul>
<h2>YouTube videos</h2>
<p>The exhaust pages show iPE videos from YouTube. Until you press play, only the preview image loads from YouTube's servers. The player itself connects after you press play, through youtube-nocookie.com, and Google's terms apply from then on (<a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>).</p>
<h2>Why</h2>
<p>Only to answer your request: choose wheels, price them and prepare a sketch. Legal basis: your request and steps before a contract (GDPR Article 6(1)(b)). We do not sell data or send newsletters without your consent.</p>
<h2>How long we keep it</h2>
<p>We keep request correspondence for up to 12 months. If you become a customer, order data is kept as long as Estonian accounting law requires (7 years).</p>
<h2>Your rights</h2>
<p>You can ask to see, correct or delete your data and object to its processing. Write to <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>; we reply within a month. If you believe your rights were breached, you can contact the Estonian Data Protection Inspectorate (<a href="https://www.aki.ee" target="_blank" rel="noopener noreferrer">aki.ee</a>).</p>
<p class="upd">Updated 28 October 2026</p>
'''),
}
P['fi'] = dict(title='Tietosuojaseloste | Nordvelg', h1='Tietosuojaseloste', desc='Miten Nordvelg käsittelee tarjouspyyntöjen tietoja.', body='''
<p>Lyhyesti ja suoraan: mitä tietoja lähetät meille nordvelg.com-sivuston kautta ja mitä niillä teemme.</p>
<h2>Rekisterinpitäjä</h2>
<p>Juka Media OÜ, rekisterikoodi 17495980, Tallinna, Viro. Tietosuojaa koskevat kysymykset: <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>.</p>
<h2>Mitä tietoja saamme</h2>
<p>Vain sen, minkä itse kirjoitat tarjouslomakkeeseen: nimen, puhelinnumeron tai sähköpostin, auton merkin, mallin ja vuosimallin, toiveesi vanteista sekä kommentin. Sivusto ei käytä mainosevästeitä eikä kävijäanalytiikkaa.</p>
<h2>Miten tiedot tulevat meille</h2>
<ul>
<li>Kun painat ”Lähetä Telegramissa” tai ”Lähetä WhatsAppissa”, pyyntösi teksti avautuu valitsemassasi viestisovelluksessa. Siellä noudatetaan kyseisen sovelluksen ehtoja.</li>
<li>Samalla hetkellä pyynnöstä lähtee kopio sähköpostiimme Formspree-palvelun (Formspree, Inc., Yhdysvallat) kautta, jottei pyyntö katoa. Tietojen siirto Yhdysvaltoihin perustuu EU:n vakiosopimuslausekkeisiin.</li>
</ul>
<h2>YouTube-videot</h2>
<p>Pakoputkistojen sivuilla on iPE:n videoita YouTubesta. Ennen kuin painat videota, YouTuben palvelimilta latautuu vain esikatselukuva. Itse soitin yhdistetään vasta painalluksen jälkeen youtube-nocookie.com-osoitteen kautta, ja siitä eteenpäin noudatetaan Googlen ehtoja (<a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">policies.google.com/privacy</a>).</p>
<h2>Mihin tietoja käytetään</h2>
<p>Vain pyyntöösi vastaamiseen: vanteiden valintaan, hinnan laskemiseen ja havainnekuvan tekemiseen. Oikeusperuste: pyyntösi ja sopimusta edeltävät toimet (tietosuoja-asetuksen 6 artiklan 1 kohdan b alakohta). Emme myy tietoja emmekä lähetä uutiskirjeitä ilman suostumustasi.</p>
<h2>Kuinka kauan säilytämme tietoja</h2>
<p>Tarjouspyyntöön liittyvää viestinvaihtoa säilytämme enintään 12 kuukautta. Jos sinusta tulee asiakas, tilauksen tietoja säilytetään niin kauan kuin Viron kirjanpitolaki edellyttää (7 vuotta).</p>
<h2>Oikeutesi</h2>
<p>Voit pyytää nähdä, korjata tai poistaa tietosi ja vastustaa niiden käsittelyä. Kirjoita osoitteeseen <a href="mailto:info@jukamedia.com">info@jukamedia.com</a>, vastaamme kuukauden kuluessa. Jos katsot, että oikeuksiasi on loukattu, voit kääntyä Viron tietosuojaviranomaisen (Andmekaitse Inspektsioon, <a href="https://www.aki.ee" target="_blank" rel="noopener noreferrer">aki.ee</a>) tai Suomen tietosuojavaltuutetun toimiston (<a href="https://tietosuoja.fi" target="_blank" rel="noopener noreferrer">tietosuoja.fi</a>) puoleen.</p>
<p class="upd">Päivitetty 28.10.2026</p>
''')

CSS = '<style>.legal{max-width:68ch;padding-block:48px 72px}.legal h1{font-family:var(--display);font-size:clamp(30px,5vw,46px);font-weight:600;letter-spacing:-.02em;margin:18px 0 18px}.legal h2{font-family:var(--display);font-size:22px;font-weight:600;margin:32px 0 10px}.legal p,.legal li{line-height:1.6}.legal ul{padding-left:20px;display:grid;gap:8px}.legal a{color:var(--bronze)}.legal .upd{color:var(--machined);margin-top:32px;font-size:14px}</style>\n'

def main():
    alts = {l: f'{SITE}/{LANGS[l]}privacy/' for l in LANGS}
    for lang, d in P.items():
        url = alts[lang]
        h = W.head_common(lang, d['title'], d['desc'], url, alts, f'{SITE}/img/og-nordvelg.jpg')
        h = h.replace('<link rel="canonical"', '<meta name="robots" content="noindex, follow">\n<link rel="canonical"', 1)
        h += CSS + '</head>\n<body>\n' + W.header(lang, alts)
        h += f'<main class="wrap legal"><h1>{d["h1"]}</h1>{d["body"]}</main>\n' + W.footer(lang) + '</body>\n</html>\n'
        out = os.path.join(ROOT, LANGS[lang], 'privacy')
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'index.html'), 'w').write(h)
        print('ok', url)

if __name__ == '__main__':
    main()
