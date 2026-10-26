/**
 * Juka Media — серверная часть AI-консультанта.
 * Статика отдаётся ассетами напрямую; сюда попадают только запросы,
 * не совпавшие с файлами, — обрабатываем POST /api/chat через
 * Cloudflare Workers AI (модель Llama, без внешних API-ключей).
 */

const MODEL = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';

const SYSTEM_PROMPT = `Ты — Juka, AI-консультант веб-студии Juka Media (jukamedia.com, OÜ Juka Media, Таллин, Эстония). Агентство обслуживает малый и средний бизнес в ЕС, Канаде и США.

ЯЗЫК: всегда отвечай на языке последнего сообщения клиента (английский, русский, эстонский, немецкий, французский или испанский). По умолчанию — английский.

УСЛУГИ И ЦЕНЫ (основная специализация — создание сайтов):
- Сайты и лендинги под ключ — главный продукт; готовый запуск сайта с доменом, почтой и Google — от €890 (пакет «Старт»)
- Интернет-магазины; спецпредложение: интернет-магазин под ключ за €990 (дизайн, корзина, оплата, доставка, до 50 товаров, до 10 категорий, аналитика, SSL, обучение 1 час; срок от 14 рабочих дней после получения материалов; оплата 50% + 50%; страница /ecommerce-990/)
- Старт бизнеса в интернете под ключ за €890 (сайт, запуск в Google, домен, почта, аналитика, первый рекламный бюджет; страница /google-business-start/)
- Реклама в Google (Google Ads), AI-автоматизация (такие же ассистенты, как ты, умные формы, Telegram-боты, автоматизация рутины)
- Ведение соцсетей (SMM): аудит профиля €150, оформление профиля €250, Reels под ключ €140 за штуку (пакет из 4 — €480), ведение от €890/мес (6 Reels, 8 постов, сторис, ответы в директе, ежемесячный отчёт); страница /services/smm/
- Бесплатный аудит маркетинга

КОНТАКТЫ: info@jukamedia.com, телефон/WhatsApp +372 5749 4989, Telegram по номеру +372 5749 4989 (t.me/+37257494989). Форма заявки — внизу главной страницы.

ПРАВИЛА:
1. Отвечай коротко: 2-4 предложения. Без списков, если не просят.
2. Твоя цель — помочь и мягко довести до заявки: предложи бесплатный аудит или оставить контакт (имя + телефон/email), либо написать в WhatsApp.
3. Никогда не обещай гарантий продаж, прибыли или окупаемости. Результаты зависят от товара, цен, спроса и рекламы.
4. Не выдумывай цены и услуги, которых нет в списке. Если вопрос вне твоих данных (точная смета, сроки под конкретный проект) — скажи, что команда уточнит после короткого созвона, и предложи оставить контакт.
5. Не отвечай на вопросы, не связанные с Juka Media и маркетингом, — вежливо возвращай разговор к делу.
6. Ты — живое демо услуги «AI-автоматизация»: если спросят, скажи, что такого же ассистента Juka Media может сделать и для их бизнеса.`;

// Канон: https://jukamedia.com, без www. Страницы-каталоги — со слэшем (/services/),
// страницы-файлы (статьи блога) — без расширения и без слэша (/blog/website-cost).
// Любой другой адрес получает ОДИН постоянный 301 сразу на итоговый адрес:
// протокол, хост, /en/, .html, index.html и слэш разрешаются за один прыжок.

// Удалённые и переехавшие страницы. Ключи — в нормализованном виде
// (без /en, без index.html и .html); слэш на конце при поиске не важен.
const LEGACY = {
  '/ecommerce-990/': '/ru/ecommerce-990/',
  '/blog/skolko-stoit-sait': '/ru/blog/skolko-stoit-sait',
  '/blog/reklama-v-google': '/ru/blog/reklama-v-google',
  '/blog/sait-ili-instagram': '/ru/blog/sait-ili-instagram',
  // SMM-статьи убраны: ведут на близкие по смыслу (страницы услуги SMM работают)
  '/blog/social-media-marketing-small-business': '/blog/website-or-instagram',
  '/ru/blog/smm-dlya-malogo-biznesa': '/ru/blog/sait-ili-instagram',
  '/et/blog/sotsiaalmeedia-turundus-vaikeettevottele': '/et/blog/koduleht-voi-instagram'
};

const CANONICAL_ORIGIN = 'https://jukamedia.com';
const PROD_HOSTS = ['jukamedia.com', 'www.jukamedia.com', 'jukamedia.auppost.workers.dev'];

const hasExtension = (p) => /\.[a-z0-9]+$/i.test(p.slice(p.lastIndexOf('/') + 1));

// Приводит путь к каноническому виду, кроме слэша: его решает наличие файла (см. ниже).
// Порядок важен: сначала /en/ и .html, потом таблица старых адресов — иначе цепочка из двух 301.
function normalizePath(pathname) {
  let p = pathname;
  if (p === '/en' || p === '/en/') p = '/';
  else if (p.startsWith('/en/')) p = p.slice(3);
  if (p.endsWith('/index.html')) p = p.slice(0, -'index.html'.length);
  else if (p.endsWith('.html') && p !== '/404.html') p = p.slice(0, -'.html'.length);
  const other = p.endsWith('/') ? p.slice(0, -1) : p + '/';
  return LEGACY[p] || LEGACY[other] || p;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (NORDVELG_HOSTS.includes(url.hostname)) return handleNordvelg(request, env, url);
    // Превью переехало на собственный домен: один 301 на тот же путь nordvelg.com
    if (url.pathname === '/demo/kova' || url.pathname.startsWith('/demo/kova/')) {
      return Response.redirect(NORDVELG_ORIGIN + (url.pathname.slice('/demo/kova'.length) || '/') + url.search, 301);
    }
    const isProd = PROD_HOSTS.includes(url.hostname);

    // Файлы Nordvelg лежат в /nordvelg/, но на jukamedia.com их не показываем
    if ((url.pathname === '/nordvelg' || url.pathname.startsWith('/nordvelg/')) && !/^\/nordvelg\/((img|fonts|js|icons|css)\/|favicon\.ico$|site\.webmanifest$)/.test(url.pathname)) {
      return notFound(request, env, url, '/404.html');
    }

    if (url.pathname === '/api/chat' && (!isProd || url.hostname === 'jukamedia.com')) {
      if (request.method !== 'POST') {
        return json({ error: 'method_not_allowed' }, 405);
      }
      return handleChat(request, env);
    }

    let path = normalizePath(url.pathname);

    // Слэш: каталог без слэша и страница-файл со слэшем ассет-роутер Cloudflare сам
    // отправляет редиректом 307 (временным!). Узнаём итоговый путь у него же и
    // отдаём один постоянный 301 вместе с остальными исправлениями.
    let served = null;
    if (env.ASSETS && !hasExtension(path)) {
      for (let i = 0; i < 2; i++) {
        const probe = await env.ASSETS.fetch(new Request(url.origin + path + url.search, {
          method: request.method,
          headers: request.headers,
          redirect: 'manual'
        }));
        const loc = probe.status >= 300 && probe.status < 400 ? probe.headers.get('location') : null;
        if (!loc) { served = probe; break; }
        path = normalizePath(new URL(loc, url.origin).pathname);
      }
    }

    // http → https и www/workers.dev → голый домен. Query сохраняется (UTM, gclid).
    const wrongOrigin = isProd && (url.protocol !== 'https:' || url.hostname !== 'jukamedia.com');
    if (wrongOrigin || path !== url.pathname) {
      const origin = isProd ? CANONICAL_ORIGIN : url.origin;
      return Response.redirect(origin + path + url.search, 301);
    }

    // Остальное — статика; несуществующие пути получает 404-страница ассет-роутера
    if (served) return served;
    return env.ASSETS ? env.ASSETS.fetch(request) : new Response('Not found', { status: 404 });
  }
};

// Nordvelg (nordvelg.com) живёт в этом же воркере: файлы в /nordvelg/, канон https://nordvelg.com без www.
const NORDVELG_HOSTS = ['nordvelg.com', 'www.nordvelg.com'];
const NORDVELG_ORIGIN = 'https://nordvelg.com';

// 26.10.2026 варианты одного дизайна BC Forged объединили на одной странице (tools/wheels-merged.json, без префикса bc-forged-)
const NORDVELG_MERGED = {'gw-a02-cx':'gw-a02','gw-a03-cx':'gw-a03','gw-a05-cx':'gw-a05','gw01-cx':'gw01','gw02-cx':'gw02','gw03-cx':'gw03','gw06-cx':'gw06','gw19-cx':'gw19','hc010s':'hc010','hc040s':'hc040','hc050s':'hc050','hc053s':'hc053','hc055s':'hc055','hc056':'hc056s','hc12s':'hc12','hc27s':'hc27','hc29s':'hc29','hca062s':'hca062','hca063s':'hca063','hca161s':'hca161','hca162':'hca162s','hca163s':'hca163','hca165':'hca165s','hca167s':'hca167','hca168s':'hca168','hca191s':'hca191','hca192s':'hca192','hca193s':'hca193','hca195s':'hca195','hca196':'hca196-hca196s','hca196s':'hca196-hca196s','hca197':'hca197s','hca198s':'hca198','hca199s':'hca199','hca210s':'hca210','hca214s':'hca214','hca217s':'hca217','hca218s':'hca218','hca222s':'hca222','hca381s':'hca381','hca382s':'hca382','hca383s':'hca383','hca384s':'hca384','hca385s':'hca385','hca386s':'hca386','hca388s':'hca388','hca389s':'hca389','hca510s':'hca510','hca671s':'hca671','hca674s':'hca674','hca675s':'hca675','hca811s':'hca811','hca813s':'hca813','hck04s':'hck04','hck165s':'hck165','hck196s':'hck196','hck198s':'hck198','hck21s':'hck21','hck381s':'hck381','hck386s':'hck386','hck675s':'hck675','hck811s':'hck811','hck855s':'hck855','hcs01s':'hcs01','hcs02s':'hcs02','hcs03s':'hcs03','hcs04s':'hcs04','hcs08s':'hcs08','hcs15s':'hcs15','hcs21s':'hcs21','hcs23s':'hcs23','hcs24s':'hcs24','hcs31s':'hcs31','hcs32s':'hcs32','hcs33s':'hcs33','hcs34s':'hcs34','hcs35s':'hcs35','hcs37s':'hcs37','hcs71s':'hcs71','hcs72s':'hcs72','hcs75s':'hcs75','hcs855s':'hcs855','hcx01s':'hcx01','hcx02s':'hcx02','hcx05s':'hcx05','hcx06s':'hcx06','hcx08s':'hcx08','hcx108s':'hcx108','le-z56-cx':'le-z56','le02-cx':'le02','le20-cx':'le20','mle-z56-cx':'mle-z56','mle02-cx':'mle02','mle20-cx':'mle20','rd01-bl':'rd01','rd02-bl':'rd02','rd03-bl':'rd03','rd05-bl':'rd05','rd06-bl':'rd06','rd07-bl':'rd07','tpx64a':'tpx64','tr01a':'tr01','tr02a':'tr02','tr03a':'tr03','tr05a':'tr05','tr06a':'tr06','tr07a':'tr07'};

async function handleNordvelg(request, env, url) {
  let path = url.pathname;
  if (path.endsWith('/index.html')) path = path.slice(0, -'index.html'.length);
  else if (path.endsWith('.html') && path !== '/404.html') path = path.slice(0, -'.html'.length);
  // С 17.10.2026 английская версия в корне, русская в /ru/: старые /en/... ведут на тот же адрес без /en
  if (path === '/en' || path === '/en/') path = '/';
  else if (path.startsWith('/en/')) path = path.slice(3);
  const mv = path.match(/^\/((?:et|ru)\/)?wheels\/bc-forged-([a-z0-9-]+)\/?$/);
  if (mv && NORDVELG_MERGED[mv[2]]) path = '/' + (mv[1] || '') + 'wheels/bc-forged-' + NORDVELG_MERGED[mv[2]] + '/';
  if (url.protocol !== 'https:' || url.hostname !== 'nordvelg.com' || path !== url.pathname) {
    return Response.redirect(NORDVELG_ORIGIN + path + url.search, 301);
  }
  if (path.startsWith('/tools/')) return notFound(request, env, url, '/nordvelg/404.html');
  const res = await env.ASSETS.fetch(new Request(url.origin + '/nordvelg' + path + url.search, {
    method: request.method,
    headers: request.headers,
    redirect: 'manual'
  }));
  if (res.status >= 300 && res.status < 400) {
    const loc = new URL(res.headers.get('location') || '/', url.origin).pathname.replace(/^\/nordvelg/, '') || '/';
    return Response.redirect(NORDVELG_ORIGIN + loc + url.search, 301);
  }
  if (res.status === 404) {
    // 16.10.2026 сняли бренды без дилерской цены: их модели и страницы брендов ведут в каталог
    const gone = path.match(/^\/((?:et|ru)\/)?wheels\/(?:brand\/)?(?:bbs|hre|vorsteiner|anrky|apex|oz|novitec|vossen|manthey|brabus)(?:[-\/]|$)/);
    if (gone) return Response.redirect(NORDVELG_ORIGIN + '/' + (gone[1] || '') + 'wheels/', 301);
    return notFound(request, env, url, '/nordvelg/404.html');
  }
  // Картинки, шрифты и скрипты не меняются под тем же именем: кэшируем надолго
  if (/^\/(img|fonts|js|icons|css)\//.test(path)) {
    const out = new Response(res.body, res);
    out.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
    return out;
  }
  return res;
}

// Превью Nordvelg на jukamedia.com/demo/kova/: те же файлы из /nordvelg/, ссылки переписываются на лету, noindex
async function handleDemo(request, env, url) {
  const rest = url.pathname.slice('/demo/kova'.length) || '/';
  if (rest.startsWith('/tools/')) return notFound(request, env, url, '/nordvelg/404.html');
  const res = await env.ASSETS.fetch(new Request(url.origin + '/nordvelg' + rest + url.search, { headers: request.headers, redirect: 'manual' }));
  if (res.status >= 300 && res.status < 400) {
    const loc = new URL(res.headers.get('location') || '/', url.origin).pathname.replace(/^\/nordvelg/, '') || '/';
    return Response.redirect(url.origin + '/demo/kova' + loc + url.search, 301);
  }
  if (res.status === 404) return notFound(request, env, url, '/nordvelg/404.html');
  if (!(res.headers.get('content-type') || '').includes('text/html')) return res;
  let s = await res.text();
  s = s.replace(/(?<=[\s"'(,])\/(img|fonts|js|icons|css)\//g, '/nordvelg/$1/')
       .replace(/(?<=[\s"'(,])\/(favicon\.ico|site\.webmanifest)/g, '/nordvelg/$1')
       .replace(/href="\/(?!nordvelg\/|demo\/)([^"]*)"/g, 'href="/demo/kova/$1"')
       .replace(/a\.href="\//g, 'a.href="/demo/kova/')
       .replace(/\bP="\//g, 'P="/demo/kova/')
       .replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">');
  const h = new Headers(res.headers);
  h.delete('content-length'); h.delete('etag'); h.set('X-Robots-Tag', 'noindex');
  return new Response(s, { status: res.status, headers: h });
}

async function notFound(request, env, url, page) {
  const res = await env.ASSETS.fetch(new Request(url.origin + page, { headers: request.headers }));
  return new Response(res.body, { status: 404, headers: res.headers });
}

async function handleChat(request, env) {
  // Принимаем запросы только со своего сайта
  const origin = request.headers.get('Origin') || '';
  const allowed = ['https://jukamedia.com', 'https://www.jukamedia.com', 'https://jukamedia.auppost.workers.dev'];
  const sameOrigin = allowed.includes(origin) || origin === '' /* некоторые браузеры не шлют Origin для same-origin */;
  if (!sameOrigin) return json({ error: 'forbidden' }, 403);

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'bad_json' }, 400);
  }

  const history = Array.isArray(body.messages) ? body.messages : [];
  // Ограничения против злоупотреблений: короткая история, короткие сообщения
  const messages = history
    .slice(-10)
    .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .map((m) => ({ role: m.role, content: m.content.slice(0, 1000) }));

  if (!messages.length || messages[messages.length - 1].role !== 'user') {
    return json({ error: 'empty' }, 400);
  }

  try {
    const result = await env.AI.run(MODEL, {
      messages: [{ role: 'system', content: SYSTEM_PROMPT }, ...messages],
      max_tokens: 512,
      temperature: 0.4
    });
    const reply = (result && (result.response || result.result || '')).toString().trim();
    if (!reply) throw new Error('empty_reply');
    return json({ reply });
  } catch (e) {
    return json({ error: 'ai_unavailable' }, 502);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8' }
  });
}
