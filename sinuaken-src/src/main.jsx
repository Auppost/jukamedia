import { createRoot } from 'react-dom/client'
import './styles.css'
import { Header, Footer } from './components/Shell'
import OrderWizard from './components/OrderWizard'
import { Process, Works, Services, KY, Reviews, Office } from './components/Sections'
import { PHONE, PHONE_HREF } from './data'

function Home() {
  return (
    <>
      <Header root="./" />
      <main>
        <section className="hero">
          <div className="wrap">
            <div className="pitch">
              <h1>Новое окно в Нарве. Цена сразу под ключ</h1>
              <p className="lead">Выберите свой проём: в цену уже входят монтаж, подоконник, отлив, откосы и вывоз старого окна. Доплат на месте нет.</p>
              <div className="facts">
                <div><span>Выезд мастера и замер</span><b>бесплатно</b></div>
                <div><span>Расчёт стоимости</span><b>в день заявки</b></div>
                <div><span>Работаем</span><b>Нарва, Силламяэ, Йыхви, Кохтла-Ярве, Кивиыли</b></div>
              </div>
              <a className="call" href={PHONE_HREF}>{PHONE} <small>пн–пт 10–18</small></a>
            </div>
            <OrderWizard />
          </div>
        </section>
        <Works />
        <Process />
        <Services />
        <KY />
        <Reviews />
        <Office />
      </main>
      <Footer />
    </>
  )
}
createRoot(document.getElementById('root')).render(<Home />)
