# Задача для Claude Code: публикация сайта Juka Media

## Что это
Готовый статический сайт (чистые HTML/CSS/JS, без сборки) маркетингового агентства Juka Media — jukamedia.com. Все файлы в этой папке — production-ready, ничего собирать или менять не нужно. Три языковые версии: русская в корне, английская в `en/`, эстонская в `et/`.

## Что нужно сделать

### 1. Запушить в GitHub
- Репозиторий: `Auppost/jukamedia` (если существует старый `Auppost/JukaMedia` с битой плоской структурой — можно очистить его force-push'ем, либо создать новый `jukamedia` через `gh repo create`)
- Ветка: `main`
- Запушить ВСЁ содержимое этой папки с сохранением структуры каталогов (папки `css/`, `js/`, `en/`, `et/`, `assets/`, `blog/`, `services/`, `cases/`, `about/`, `contact/`, `pages/`, `google-business-start/` + файлы корня, включая `wrangler.jsonc`)

### 2. Задеплоить в Cloudflare Workers
- Аккаунт: auppost@gmail.com, воркер называется `jukamedia` (URL: jukamedia.auppost.workers.dev)
- Конфиг `wrangler.jsonc` уже лежит в корне (static assets, directory `./`)
- Команда: `npx wrangler deploy` (при первом запуске — `npx wrangler login`)

### 3. Проверить результат
- Открыть https://jukamedia.auppost.workers.dev — в шапке меню должно вести на ОТДЕЛЬНЫЕ страницы: Услуги (`services/index.html`), Кейсы (`cases/index.html`), Блог, О нас (`about/index.html`), Старт за €590, Контакты (`contact/index.html`). Если ссылки меню — якоря вида `#services`, значит задеплоилась старая версия
- Проверить, что открываются `/services/`, `/cases/`, `/about/`, `/contact/`, `/en/`, `/et/`, `/blog/`
- 404: `/404.html` отдаётся на несуществующих путях (настроено в wrangler.jsonc через not_found_handling)

## Важно
- НЕ менять контент, стили и структуру файлов — сайт финальный
- В Cloudflare к воркеру уже может быть привязан старый GitHub-репозиторий (Settings → Build). Если он указывает на битый репозиторий — отвязать или перепривязать к актуальному
- Домен jukamedia.com в процессе переноса на Cloudflare (nameservers меняются у регистратора whois.com) — с доменом ничего делать не нужно
- Форма на сайте шлёт через Formspree, аналитика Google Analytics — всё уже вшито в HTML
