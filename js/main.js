/* Juka Media - main.js
   Нативные анимации без библиотек:
   построчный H1, счётчик цифр, параллакс карточки, умная шапка,
   деликатное появление блоков. Всё уважает prefers-reduced-motion. */

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ============================================================
   1. Построчное раскрытие заголовка hero
   Оборачиваем текст в строки и поднимаем их из-под маски.
   ============================================================ */
function initHeroTitle() {
  const title = document.querySelector('[data-split]');
  if (!title || reduceMotion) return;

  // Сохраняем разметку акцента: разбиваем по словам, но целыми узлами.
  const words = [];
  title.childNodes.forEach((node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      node.textContent.split(/(\s+)/).forEach((chunk) => {
        if (chunk.trim()) words.push({ text: chunk, cls: null });
        else if (chunk) words.push({ space: true });
      });
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      words.push({ text: node.textContent, cls: node.className });
    }
  });

  title.textContent = '';
  title.classList.add('is-split');

  words.forEach((w, i) => {
    if (w.space) {
      title.appendChild(document.createTextNode(' '));
      return;
    }
    const outer = document.createElement('span');
    outer.className = 'word';
    const inner = document.createElement('span');
    inner.className = 'word__in';
    if (w.cls) inner.classList.add(...w.cls.split(' ').filter(Boolean));
    inner.textContent = w.text;
    inner.style.transitionDelay = (i * 0.045) + 's';
    outer.appendChild(inner);
    title.appendChild(outer);
  });

  requestAnimationFrame(() => {
    requestAnimationFrame(() => title.classList.add('is-in'));
  });
  // Подстраховка на случай, если rAF придушен (фоновая вкладка/iframe)
  setTimeout(() => title.classList.add('is-in'), 120);
}

/* ============================================================
   2. Счётчик цифр в статистике и кейсах
   Анимируем число при попадании в экран, сохраняя префикс/суффикс.
   ============================================================ */
function animateCount(el) {
  const raw = el.textContent.trim();
  const match = raw.match(/([^\d]*)([\d]+(?:[.,]\d+)?)(.*)/);
  if (!match) return;

  const [, prefix, numStr, suffix] = match;
  const target = parseFloat(numStr.replace(',', '.'));
  const decimals = (numStr.split(/[.,]/)[1] || '').length;
  const duration = 1400;
  const start = performance.now();

  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    // easeOutExpo — быстрый старт, мягкая остановка.
    const eased = p === 1 ? 1 : 1 - Math.pow(2, -10 * p);
    const val = (target * eased).toFixed(decimals);
    el.textContent = prefix + val + suffix;
    if (p < 1) requestAnimationFrame(tick);
    else el.textContent = raw;
  }
  requestAnimationFrame(tick);
}

function initCounters() {
  const nums = document.querySelectorAll('[data-count]');
  if (!nums.length) return;

  if (reduceMotion || !('IntersectionObserver' in window)) return;

  const obs = new IntersectionObserver((entries, o) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        o.unobserve(entry.target);
      }
    });
  }, { threshold: 0.6 });

  nums.forEach((n) => obs.observe(n));
}

/* ============================================================
   3. Деликатное появление блоков при скролле
   Лёгкий подъём + снятие размытия. Стаггер внутри одной группы.
   ============================================================ */
function initReveal() {
  const selector = [
    '.promo__banner', '.section__title', '.section__subtitle',
    '.card', '.teamcard', '.stats', '.problem__card', '.problem__foot',
    '.solution__text', '.solution__item', '.case', '.cases__foot',
    '.process__step', '.contactcta__card', '.lead__inner'
  ].join(',');

  const items = document.querySelectorAll(selector);
  if (!items.length) return;

  items.forEach((el) => el.setAttribute('data-reveal', ''));

  const groups = new Map();
  items.forEach((el) => {
    const parent = el.parentElement;
    const i = groups.get(parent) || 0;
    if (i > 0) el.style.setProperty('--reveal-delay', Math.min(i * 0.06, 0.36) + 's');
    groups.set(parent, i + 1);
  });

  if (reduceMotion || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const obs = new IntersectionObserver((entries, o) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        o.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.15 });

  items.forEach((el) => obs.observe(el));
}

/* ============================================================
   4. Параллакс карточки в hero (реакция на курсор)
   Тонкий наклон в сторону движения мыши, без перегруза.
   ============================================================ */
function initParallax() {
  const card = document.querySelector('[data-parallax]');
  if (!card || reduceMotion || window.matchMedia('(pointer: coarse)').matches) return;

  const strength = 6; // максимальный наклон в градусах
  let raf = null;

  function onMove(e) {
    const r = card.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      card.style.transform =
        `perspective(900px) rotateX(${(-y * strength).toFixed(2)}deg) rotateY(${(x * strength).toFixed(2)}deg)`;
    });
  }

  function reset() {
    if (raf) cancelAnimationFrame(raf);
    card.style.transform = '';
  }

  const area = card.closest('.hero') || card;
  area.addEventListener('mousemove', onMove);
  area.addEventListener('mouseleave', reset);
}

/* ============================================================
   5. Умная шапка: тень при скролле, скрытие при движении вниз
   ============================================================ */
function initHeader() {
  const header = document.querySelector('.header');
  if (!header) return;

  let last = window.scrollY;
  let ticking = false;

  function update() {
    const y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 40);
    last = y;
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
}

/* ============================================================
   Мобильное меню
   ============================================================ */
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');

if (burger && nav) {
  burger.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.classList.toggle('is-active', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  });

  nav.addEventListener('click', (e) => {
    if (e.target.closest('a')) {
      nav.classList.remove('is-open');
      burger.classList.remove('is-active');
      burger.setAttribute('aria-expanded', 'false');
    }
  });
}

/* ============================================================
   Баннер cookies (согласие на аналитику, GDPR)
   Выбор хранится в localStorage. Аналитика подключается
   только после согласия: добавьте её загрузку в enableAnalytics().
   ============================================================ */
function initCookieBanner() {
  const KEY = 'jm-cookie-consent';
  const saved = localStorage.getItem(KEY);

  function enableAnalytics() {
    // Google Analytics 4: грузится только после согласия на cookies (GDPR)
    if (window.__jmGaLoaded) return;
    window.__jmGaLoaded = true;
    const GA_ID = 'G-1ZDKBX94P9';
    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID, { anonymize_ip: true });
  }

  if (saved === 'accepted') { enableAnalytics(); return; }
  if (saved === 'declined') return;

  // Локализация по языку страницы
  const lang = (document.documentElement.lang || 'ru').slice(0, 2);
  const i18n = {
    ru: {
      text: 'Мы используем cookies для анализа посещаемости. Это помогает делать сайт лучше.',
      more: 'Подробнее',
      accept: 'Принять', decline: 'Отклонить', settings: 'Настроить',
      necessary: 'Необходимые (всегда включены)', analytics: 'Аналитика (посещаемость страниц)',
      save: 'Сохранить выбор', label: 'Согласие на использование cookies'
    },
    en: {
      text: 'We use cookies to analyse site traffic. This helps us make the site better.',
      more: 'Learn more',
      accept: 'Accept', decline: 'Decline', settings: 'Customise',
      necessary: 'Necessary (always on)', analytics: 'Analytics (page visits)',
      save: 'Save choice', label: 'Cookie consent'
    },
    et: {
      text: 'Kasutame küpsiseid külastatavuse analüüsiks. See aitab meil lehte paremaks teha.',
      more: 'Loe lähemalt',
      accept: 'Nõustun', decline: 'Keeldun', settings: 'Seadista',
      necessary: 'Vajalikud (alati sees)', analytics: 'Analüütika (lehekülgede külastused)',
      save: 'Salvesta valik', label: 'Küpsiste nõusolek'
    }
  };
  const t = i18n[lang] || i18n.ru;

  // Путь к корню сайта: берём из относительной ссылки на manifest
  const mf = document.querySelector('link[rel="manifest"]');
  const root = mf ? mf.getAttribute('href').replace('manifest.webmanifest', '') : '';
  // Локализованная политика для en/et
  const privacyHref = (lang === 'en' || lang === 'et')
    ? root + lang + '/pages/privacy.html'
    : root + 'pages/privacy.html';

  const bar = document.createElement('div');
  bar.className = 'cookiebar';
  bar.setAttribute('role', 'dialog');
  bar.setAttribute('aria-label', t.label);
  bar.innerHTML =
    '<p class="cookiebar__text">' + t.text + ' <a href="' + privacyHref + '">' + t.more + '</a></p>' +
    '<div class="cookiebar__settings" hidden>' +
      '<label class="cookiebar__opt"><input type="checkbox" checked disabled> ' + t.necessary + '</label>' +
      '<label class="cookiebar__opt"><input type="checkbox" id="jm-cookie-analytics" checked> ' + t.analytics + '</label>' +
      '<button class="btn btn--primary cookiebar__btn" type="button" data-cookie-save>' + t.save + '</button>' +
    '</div>' +
    '<div class="cookiebar__actions">' +
      '<button class="btn btn--primary cookiebar__btn" type="button" data-cookie="accepted">' + t.accept + '</button>' +
      '<button class="btn btn--ghost cookiebar__btn" type="button" data-cookie="declined">' + t.decline + '</button>' +
      '<button class="cookiebar__link" type="button" data-cookie-settings>' + t.settings + '</button>' +
    '</div>';

  bar.addEventListener('click', (e) => {
    if (e.target.closest('[data-cookie-settings]')) {
      const s = bar.querySelector('.cookiebar__settings');
      s.hidden = !s.hidden;
      return;
    }
    if (e.target.closest('[data-cookie-save]')) {
      const ok = bar.querySelector('#jm-cookie-analytics').checked;
      localStorage.setItem(KEY, ok ? 'accepted' : 'declined');
      bar.remove();
      if (ok) enableAnalytics();
      return;
    }
    const btn = e.target.closest('[data-cookie]');
    if (!btn) return;
    localStorage.setItem(KEY, btn.dataset.cookie);
    bar.remove();
    if (btn.dataset.cookie === 'accepted') enableAnalytics();
  });

  document.body.appendChild(bar);
}

/* ============================================================
   Кнопка «Наверх» на длинных страницах
   ============================================================ */
function initToTop() {
  if (document.body.scrollHeight < window.innerHeight * 2.5) return;

  const btn = document.createElement('button');
  btn.className = 'totop';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Наверх');
  btn.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>';
  btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' }));
  document.body.appendChild(btn);

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      btn.classList.toggle('is-visible', window.scrollY > window.innerHeight * 1.5);
      ticking = false;
    });
  }, { passive: true });
}

/* ---------- Запуск ---------- */
function boot() {
  initToTop();
  initHeroTitle();
  initCounters();
  initReveal();
  initParallax();
  initHeader();
  initCookieBanner();
}

if (document.readyState !== 'loading') boot();
else document.addEventListener('DOMContentLoaded', boot);
