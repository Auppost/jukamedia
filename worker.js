/**
 * Juka Media — серверная часть AI-консультанта.
 * Статика отдаётся ассетами напрямую; сюда попадают только запросы,
 * не совпавшие с файлами, — обрабатываем POST /api/chat через
 * Cloudflare Workers AI (модель Llama, без внешних API-ключей).
 */

const MODEL = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';

const SYSTEM_PROMPT = `Ты — Juka, AI-консультант маркетингового агентства Juka Media (jukamedia.com, OÜ Juka Media, Таллин, Эстония). Агентство обслуживает малый и средний бизнес в ЕС, Канаде и США.

ЯЗЫК: всегда отвечай на языке последнего сообщения клиента (английский, русский, эстонский, немецкий, французский или испанский). По умолчанию — английский.

УСЛУГИ И ЦЕНЫ (основная специализация — создание сайтов):
- Сайты и лендинги под ключ — главный продукт; готовый запуск сайта с доменом, почтой и Google — от €590 (пакет «Старт»)
- Интернет-магазины; спецпредложение: интернет-магазин под ключ за €990 (дизайн, корзина, оплата, доставка, до 50 товаров, до 10 категорий, аналитика, SSL, обучение 1 час; срок от 14 рабочих дней после получения материалов; оплата 50% + 50%; страница /ecommerce-990/)
- Старт бизнеса в интернете под ключ за €590 (сайт, запуск в Google, домен, почта, аналитика, первый рекламный бюджет; страница /google-business-start/)
- Ведение соцсетей (SMM), реклама в Google (Google Ads), AI-автоматизация (такие же ассистенты, как ты, умные формы, автоматизация рутины)
- Бесплатный аудит маркетинга

КОНТАКТЫ: info@jukamedia.com, телефон/WhatsApp +372 5749 4989, Telegram t.me/alekseipsk. Форма заявки — внизу главной страницы.

ПРАВИЛА:
1. Отвечай коротко: 2-4 предложения. Без списков, если не просят.
2. Твоя цель — помочь и мягко довести до заявки: предложи бесплатный аудит или оставить контакт (имя + телефон/email), либо написать в WhatsApp.
3. Никогда не обещай гарантий продаж, прибыли или окупаемости. Результаты зависят от товара, цен, спроса и рекламы.
4. Не выдумывай цены и услуги, которых нет в списке. Если вопрос вне твоих данных (точная смета, сроки под конкретный проект) — скажи, что команда уточнит после короткого созвона, и предложи оставить контакт.
5. Не отвечай на вопросы, не связанные с Juka Media и маркетингом, — вежливо возвращай разговор к делу.
6. Ты — живое демо услуги «AI-автоматизация»: если спросят, скажи, что такого же ассистента Juka Media может сделать и для их бизнеса.`;

// Старые русские URL, переехавшие в /ru/ при переходе на английский корень.
// 301, чтобы не терять позиции в Google и не отдавать 404.
const REDIRECTS = {
  '/ecommerce-990/': '/ru/ecommerce-990/',
  '/ecommerce-990/index.html': '/ru/ecommerce-990/',
  '/blog/skolko-stoit-sait.html': '/ru/blog/skolko-stoit-sait.html',
  '/blog/reklama-v-google.html': '/ru/blog/reklama-v-google.html',
  '/blog/sait-ili-instagram.html': '/ru/blog/sait-ili-instagram.html'
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Канонический хост: www и workers.dev отдают 301 на голый домен,
    // чтобы Google не считал их дублями (assets.run_worker_first = true,
    // иначе статика уходила бы в обход этой проверки).
    if (url.hostname === 'www.jukamedia.com' || url.hostname === 'jukamedia.auppost.workers.dev') {
      url.hostname = 'jukamedia.com';
      return Response.redirect(url.toString(), 301);
    }

    if (url.pathname === '/api/chat') {
      if (request.method !== 'POST') {
        return json({ error: 'method_not_allowed' }, 405);
      }
      return handleChat(request, env);
    }

    const to = REDIRECTS[url.pathname];
    if (to) return Response.redirect(url.origin + to, 301);

    // Английская версия переехала из /en/ в корень — 301 со старых адресов,
    // структура внутри /en/ совпадала с нынешним корнем один в один.
    if (url.pathname === '/en' || url.pathname === '/en/') {
      return Response.redirect(url.origin + '/', 301);
    }
    if (url.pathname.startsWith('/en/')) {
      return Response.redirect(url.origin + url.pathname.slice(3) + url.search, 301);
    }

    // Всё остальное, что не совпало с ассетами, — 404 от ассет-роутера
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
