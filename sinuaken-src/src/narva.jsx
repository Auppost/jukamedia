import { createRoot } from 'react-dom/client'
import './styles.css'
import { Header, Footer, ReviewsBadge, Ph } from './components/Shell'
import OrderWizard from './components/OrderWizard'
import { Process, Works, Reviews, Office, SecTitle } from './components/Sections'
import { IMG, PHOTOS, PHONE, PHONE_HREF } from './data'

function Narva() {
  return (
    <>
      <Header root="../" current="narva" />
      <main>
        <section className="city-hero">
          <img src={IMG(PHOTOS.narva, 1800)} alt="Нарва, вид на крепость и реку" />
          <div className="wrap">
            <div className="city-card">
              <h1>Окна в Нарве под ключ</h1>
              <p>Офис на Kreenholmi 10, мастер приезжает по Нарве бесплатно и считает цену в день заявки.</p>
              <div className="city-actions">
                <a className="btn big" href="#naryad">Собрать наряд</a>
                <a className="call small" href={PHONE_HREF}>{PHONE}</a>
              </div>
              <ReviewsBadge />
            </div>
          </div>
        </section>
        <section className="band tight">
          <div className="wrap">
            <SecTitle title="Цена за окно, а не «от»">Выберите проём своей квартиры. Если размер другой, жмите «Другой размер», замер бесплатный.</SecTitle>
            <OrderWizard city="Нарва" />
          </div>
        </section>
        <section className="band">
          <div className="wrap">
            <SecTitle title="Работаем во всех районах">Кренгольм, Пяхклимяэ, Калеви, Солдино, Сийвертси, Кулгу, частный сектор и Нарва-Йыэсуу. Сроки по районам <Ph>[уточнить]</Ph>.</SecTitle>
            <div className="districts">
              {['Кренгольм', 'Пяхклимяэ', 'Калеви', 'Солдино', 'Сийвертси', 'Кулгу', 'Йоала', 'Нарва-Йыэсуу'].map((d) => <span key={d}>{d}</span>)}
            </div>
          </div>
        </section>
        <Works />
        <Process />
        <Reviews />
        <Office />
      </main>
      <Footer />
    </>
  )
}
createRoot(document.getElementById('root')).render(<Narva />)
