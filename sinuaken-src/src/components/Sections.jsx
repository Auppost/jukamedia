import { IMG, PHOTOS, PHONE, PHONE_HREF } from '../data'
import { Ph, ReviewsBadge } from './Shell'

export function SecTitle({ title, children }) {
  return (
    <div className="sec-title">
      <h2>{title}</h2>
      {children ? <p>{children}</p> : null}
    </div>
  )
}

export function Process() {
  const steps = [
    ['Звонок или наряд', 'Выбираете тип проёма на сайте или просто называете адрес. Перезваниваем в рабочее время.'],
    ['Выезд и замер', 'Мастер приезжает бесплатно, замеряет проём и подтверждает цену в тот же день.'],
    ['Монтаж', <>Ставим окно, подоконник, отлив и откосы, делаем отделку внутри. Срок монтажа <Ph>[уточнить]</Ph>.</>],
    ['Уборка и вывоз', <>Старое окно разбираем и увозим на утилизацию. Гарантия <Ph>[срок]</Ph>.</>],
  ]
  return (
    <section className="band">
      <div className="wrap">
        <SecTitle title="Как это происходит">От звонка до нового окна. Старое окно увозим сами.</SecTitle>
        <ol className="steps">
          {steps.map(([h, p]) => (
            <li key={h}><div className="box" aria-hidden="true">✓</div><h3>{h}</h3><p>{p}</p></li>
          ))}
        </ol>
      </div>
    </section>
  )
}

export function Works() {
  const slots = [PHOTOS.newWindow, PHOTOS.sill, PHOTOS.sealing, PHOTOS.handles]
  return (
    <section className="band">
      <div className="wrap">
        <SecTitle title="Наши работы">Здесь будут фото ваших объектов: до и после, с адресом района. Это сильнее любых слов про качество.</SecTitle>
        <div className="works">
          {slots.map((id, i) => (
            <figure key={id}>
              <img src={IMG(id, 800)} alt="" loading="lazy" />
              <figcaption><Ph>[фото объекта {i + 1}: район, тип окна]</Ph></figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}

export function Services() {
  const rows = [
    [PHOTOS.balcony, 'Остекление балконов', 'Тёплое и холодное, защита от ветра, шума и пыли. Балкон становится ещё одной комнатой.'],
    [PHOTOS.handles, 'Глухое окно сделать открывающимся', 'Поворотная или поворотно-откидная створка в существующем окне, без замены всего блока.'],
    [PHOTOS.repair, 'Ремонт окон', 'Замена уплотнителей, регулировка, новые стеклопакеты. Часто дешевле, чем новое окно.'],
    [PHOTOS.door, 'Входные двери', 'Для квартиры, частного дома и офиса. Тёплые, с хорошим уплотнением.'],
    [PHOTOS.net, 'Москитные сетки', 'Обычные, антиаллергенные и усиленные «антикошка». Ставятся без инструментов.'],
    [PHOTOS.sill, 'Деревянные окна и натяжные потолки', <>Окна из клееного бруса с тройным стеклопакетом. Натяжные потолки под ключ <Ph>[срок]</Ph>.</>],
  ]
  return (
    <section className="band" id="uslugi">
      <div className="wrap">
        <SecTitle title="Кроме окон">Всё, что связано с окнами, балконом и дверью, одной бригадой.</SecTitle>
        <div className="svc">
          {rows.map(([id, h, p]) => (
            <a key={h} href="#naryad">
              <img src={IMG(id, 500)} alt="" loading="lazy" />
              <div><h3>{h}</h3><p>{p}</p></div>
              <span className="go">Рассчитать</span>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}

export function KY() {
  return (
    <section className="band" id="ky">
      <div className="wrap ky">
        <img src={IMG(PHOTOS.panelWinter)} alt="Панельные дома" loading="lazy" />
        <div>
          <h2>Замена окон во всём доме для квартирных товариществ</h2>
          <p>Проекты «под ключ» для КÜ в программах реновации: замер всех квартир, смета, монтаж по графику, сдача в срок.</p>
          <ul>
            {['Раквере', 'Йыхви', 'Винни', 'Вока'].map((c) => <li key={c}>{c}<span><Ph>[год, кол-во окон]</Ph></span></li>)}
          </ul>
          <a className="btn ghost" href={PHONE_HREF}>Запросить смету для КÜ</a>
        </div>
      </div>
    </section>
  )
}

export function Reviews() {
  return (
    <section className="band">
      <div className="wrap reviews">
        <div className="score">4.8<small>21 отзыв в Google</small></div>
        <div className="quotes">
          {[1, 2, 3, 4].map((i) => (
            <blockquote key={i}><Ph>[Отзыв из Google, дословно]</Ph><cite><Ph>[Имя, район]</Ph></cite></blockquote>
          ))}
        </div>
      </div>
    </section>
  )
}

export function Office() {
  return (
    <section className="office">
      <div className="wrap">
        <div className="txt">
          <h2>Приходите или звоните</h2>
          <p>Офис в Нарве, пн–пт 10:00–18:00. Покажем образцы профиля и подоконников.</p>
          <a className="call" href={PHONE_HREF}>{PHONE}</a>
          <div className="alt">
            <a href="#">WhatsApp <Ph>[номер]</Ph></a>
            <a href="#">Viber <Ph>[номер]</Ph></a>
            <a href="mailto:info@sinuaken.ee">info@sinuaken.ee</a>
          </div>
          <ReviewsBadge dark />
        </div>
        <div className="photo">
          <img src={IMG(PHOTOS.narva, 1400)} alt="Нарвская крепость и Ивангород через реку" loading="lazy" />
          <div className="addr"><b>Kreenholmi 10, Нарва</b>пн–пт 10:00–18:00</div>
        </div>
      </div>
    </section>
  )
}
