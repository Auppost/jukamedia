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
- Ведение соцсетей (SMM) агентство НЕ делает. Если спрашивают про соцсети, честно скажи, что этим не занимаемся, и предложи сайт, Google Ads или автоматизацию ответов клиентам
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
  // SMM убран из услуг: страницы и статьи ведут на близкие по смыслу
  '/services/smm/': '/services/',
  '/ru/services/smm/': '/ru/services/',
  '/et/services/smm/': '/et/services/',
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
    const isProd = PROD_HOSTS.includes(url.hostname);

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
