/* Juka Media — виджет AI-консультанта.
   Чистый JS без библиотек. Общается с /api/chat (Cloudflare Workers AI).
   Локализация по <html lang>. Если API недоступен — мягкий фолбэк
   с предложением написать в WhatsApp. */

(function () {
  'use strict';

  var lang = (document.documentElement.lang || 'ru').slice(0, 2);
  var I18N = {
    ru: {
      launcher: 'Спросить AI',
      title: 'Juka · AI-консультант',
      status: 'Онлайн · отвечает сразу',
      hello: 'Здравствуйте! Я Juka, AI-сотрудник Juka Media. Подскажу по услугам, ценам и срокам — например, про сайт, магазин за €990 или рекламу в Google. Что вас интересует?',
      placeholder: 'Ваш вопрос…',
      send: 'Отправить',
      error: 'Не получилось связаться с сервером. Напишите нам в WhatsApp — ответим быстро:',
      wa: 'Открыть WhatsApp',
      close: 'Закрыть чат',
      demo: 'Такого же AI-сотрудника сделаем и для вашего бизнеса — спросите как.'
    },
    en: {
      launcher: 'Ask AI',
      title: 'Juka · AI assistant',
      status: 'Online · instant replies',
      hello: "Hi! I'm Juka, the AI assistant at Juka Media. Ask me about services, prices and timelines — websites, the €990 online store or Google ads. How can I help?",
      placeholder: 'Your question…',
      send: 'Send',
      error: "Couldn't reach the server. Message us on WhatsApp — we reply fast:",
      wa: 'Open WhatsApp',
      close: 'Close chat',
      demo: 'We can build the same AI assistant for your business — ask me how.'
    },
    et: {
      launcher: 'Küsi AI-lt',
      title: 'Juka · AI-assistent',
      status: 'Võrgus · vastab kohe',
      hello: 'Tere! Olen Juka, Juka Media AI-assistent. Küsige teenuste, hindade ja tähtaegade kohta — koduleht, e-pood €990 eest või Google\'i reklaam. Kuidas saan aidata?',
      placeholder: 'Teie küsimus…',
      send: 'Saada',
      error: 'Serveriga ei õnnestunud ühendust saada. Kirjutage meile WhatsAppis — vastame kiiresti:',
      wa: 'Ava WhatsApp',
      close: 'Sulge vestlus',
      demo: 'Sama AI-assistendi teeme ka teie ettevõttele — küsige, kuidas.'
    },
    de: {
      launcher: 'KI fragen',
      title: 'Juka · KI-Assistent',
      status: 'Online · antwortet sofort',
      hello: 'Hallo! Ich bin Juka, der KI-Assistent von Juka Media. Fragen Sie mich zu Leistungen, Preisen und Terminen — Webseite, Onlineshop ab €990 oder Google Ads. Wie kann ich helfen?',
      placeholder: 'Ihre Frage…',
      send: 'Senden',
      error: 'Verbindung zum Server fehlgeschlagen. Schreiben Sie uns per WhatsApp — wir antworten schnell:',
      wa: 'WhatsApp öffnen',
      close: 'Chat schließen',
      demo: 'Denselben KI-Assistenten bauen wir auch für Ihr Unternehmen — fragen Sie wie.'
    },
    fr: {
      launcher: 'Demander à l’IA',
      title: 'Juka · assistant IA',
      status: 'En ligne · réponse immédiate',
      hello: 'Bonjour ! Je suis Juka, l’assistant IA de Juka Media. Posez-moi vos questions sur les services, les prix et les délais — site web, boutique en ligne dès 590 € ou Google Ads. Comment puis-je aider ?',
      placeholder: 'Votre question…',
      send: 'Envoyer',
      error: 'Impossible de joindre le serveur. Écrivez-nous sur WhatsApp — nous répondons vite :',
      wa: 'Ouvrir WhatsApp',
      close: 'Fermer le chat',
      demo: 'Nous pouvons créer le même assistant IA pour votre entreprise — demandez comment.'
    },
    es: {
      launcher: 'Preguntar a la IA',
      title: 'Juka · asistente IA',
      status: 'En línea · responde al instante',
      hello: '¡Hola! Soy Juka, el asistente de IA de Juka Media. Pregúntame sobre servicios, precios y plazos — sitio web, tienda online desde 590 € o Google Ads. ¿En qué puedo ayudarte?',
      placeholder: 'Tu pregunta…',
      send: 'Enviar',
      error: 'No se pudo conectar con el servidor. Escríbenos por WhatsApp — respondemos rápido:',
      wa: 'Abrir WhatsApp',
      close: 'Cerrar chat',
      demo: 'Podemos crear el mismo asistente de IA para tu negocio — pregunta cómo.'
    }
  };
  var t = I18N[lang] || I18N.en;

  var history = []; // {role, content}
  var busy = false;

  // ---------- DOM ----------
  var root = document.createElement('div');
  root.className = 'aichat';
  root.innerHTML =
    '<button class="aichat__launcher" type="button" aria-haspopup="dialog" aria-expanded="false">' +
      '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5c-1.5 0-3-.4-4.2-1.1L3 20l1.1-5.3A8.5 8.5 0 1 1 21 11.5z"/><path d="M8 10h8M8 13.5h5"/></svg>' +
      '<span>' + t.launcher + '</span>' +
    '</button>' +
    '<section class="aichat__panel" role="dialog" aria-label="' + t.title + '" hidden>' +
      '<header class="aichat__head">' +
        '<div>' +
          '<p class="aichat__title">' + t.title + '</p>' +
          '<p class="aichat__status"><span class="aichat__dot"></span>' + t.status + '</p>' +
        '</div>' +
        '<button class="aichat__close" type="button" aria-label="' + t.close + '">✕</button>' +
      '</header>' +
      '<div class="aichat__log" aria-live="polite"></div>' +
      '<form class="aichat__form">' +
        '<input class="aichat__input" type="text" maxlength="500" placeholder="' + t.placeholder + '" aria-label="' + t.placeholder + '">' +
        '<button class="aichat__send btn btn--primary" type="submit">' + t.send + '</button>' +
      '</form>' +
    '</section>';
  document.body.appendChild(root);

  var launcher = root.querySelector('.aichat__launcher');
  var panel = root.querySelector('.aichat__panel');
  var log = root.querySelector('.aichat__log');
  var form = root.querySelector('.aichat__form');
  var input = root.querySelector('.aichat__input');

  function addMsg(role, text, extraHtml) {
    var el = document.createElement('div');
    el.className = 'aichat__msg aichat__msg--' + role;
    el.textContent = text;
    if (extraHtml) {
      var extra = document.createElement('div');
      extra.className = 'aichat__extra';
      extra.innerHTML = extraHtml;
      el.appendChild(extra);
    }
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
    return el;
  }

  function setTyping(on) {
    var cur = log.querySelector('.aichat__typing');
    if (on && !cur) {
      var el = document.createElement('div');
      el.className = 'aichat__msg aichat__msg--assistant aichat__typing';
      el.innerHTML = '<span></span><span></span><span></span>';
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
    } else if (!on && cur) {
      cur.remove();
    }
  }

  function toggle(open) {
    var willOpen = open !== undefined ? open : panel.hidden;
    panel.hidden = !willOpen;
    launcher.setAttribute('aria-expanded', String(willOpen));
    root.classList.toggle('aichat--open', willOpen);
    if (willOpen) {
      if (!log.children.length) addMsg('assistant', t.hello);
      input.focus();
      track('aichat_open');
    }
  }

  launcher.addEventListener('click', function () { toggle(); });
  root.querySelector('.aichat__close').addEventListener('click', function () { toggle(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !panel.hidden) toggle(false);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text || busy) return;
    input.value = '';
    addMsg('user', text);
    history.push({ role: 'user', content: text });
    send();
  });

  function send() {
    busy = true;
    setTyping(true);
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history.slice(-10) })
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error(r.status)); })
      .then(function (data) {
        setTyping(false);
        busy = false;
        if (!data.reply) throw new Error('empty');
        history.push({ role: 'assistant', content: data.reply });
        addMsg('assistant', data.reply);
        track('aichat_reply');
      })
      .catch(function () {
        setTyping(false);
        busy = false;
        addMsg('assistant', t.error,
          '<a class="btn btn--primary aichat__wa" href="https://wa.me/37257494989" target="_blank" rel="noopener">' + t.wa + '</a>');
        track('aichat_error');
      });
    track('aichat_message');
  }

  function track(name) {
    if (typeof window.gtag === 'function') window.gtag('event', name);
  }
})();
