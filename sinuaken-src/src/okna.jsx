import { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { motion } from 'framer-motion'
import './styles.css'
import { Header, Footer, Price, Ph, ReviewsBadge } from './components/Shell'
import Drawing from './components/Drawing'
import { Office, SecTitle } from './components/Sections'
import { TYPES, INCLUDED, IMG, PHOTOS } from './data'

function Okna() {
  const [line, setLine] = useState('classic')
  const [lit, setLit] = useState(null)
  return (
    <>
      <Header root="../" current="okna" />
      <main>
        <section className="ph-head">
          <div className="wrap">
            <div>
              <p className="crumbs"><a href="../">Главная</a> / Окна ПВХ</p>
              <h1>Пластиковые окна: цены под ключ</h1>
              <p className="lead">Семь самых частых проёмов. В каждой цене окно, монтаж, подоконник, отлив, откосы, отделка внутри и вывоз старого окна.</p>
            </div>
            <div className="seg" role="radiogroup" aria-label="Линейка">
              {['classic', 'perfect'].map((k) => (
                <button key={k} type="button" role="radio" aria-checked={line === k} onClick={() => setLine(k)}>
                  {line === k && <motion.span layoutId="seg-bg" className="seg-bg" transition={{ type: 'spring', stiffness: 500, damping: 38 }} />}
                  <span>{k.toUpperCase()}</span>
                </button>
              ))}
            </div>
          </div>
        </section>
        <section className="pad-sec">
          <div className="wrap">
            <div className="pad">
              {TYPES.map((t) => (
                <div className="slip" key={t.n}>
                  <div className="pic"><Drawing t={t} height={210} /></div>
                  <div className="info"><h2>{t.w} × {t.h}</h2><p className="desc">Тип {t.n}: {t.label}</p></div>
                  <div className="pr"><Price value={line === 'classic' ? t.c : t.p} /><small>{line === 'classic' ? `PERFECT ${t.p} €` : `CLASSIC ${t.c} €`}</small></div>
                  <div className="act"><a className="btn" href={`../#naryad`}>Заказать</a></div>
                </div>
              ))}
            </div>
            <p className="note">Чем PERFECT отличается от CLASSIC: <Ph>[профиль, стеклопакет, фурнитура: уточнить у клиента]</Ph>. Высота с подставочным профилем +30 мм.</p>
          </div>
        </section>
        <section className="band">
          <div className="wrap">
            <SecTitle title="Что входит в цену">Наведите на строку, и на чертеже подсветится, о чём речь. Отдельно ничего доплачивать не нужно.</SecTitle>
            <div className="incl">
              <div className="big"><Drawing t={TYPES[0]} lit={lit} height={330} /></div>
              <ul className="legend">
                {INCLUDED.map((it, i) => (
                  <li key={it.part} tabIndex={0} className={lit === it.part ? 'on' : ''} onMouseEnter={() => setLit(it.part)} onMouseLeave={() => setLit(null)} onFocus={() => setLit(it.part)} onBlur={() => setLit(null)}>
                    <span className="key">{i + 1}</span><div><b>{it.title}</b>{it.text}</div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>
        <section className="band tight">
          <div className="wrap">
            <div className="custom">
              <div className="txt">
                <h2>Ваш размер не из списка?</h2>
                <p>Частный дом, нестандартный проём или сразу несколько окон. Мастер приедет, замерит и посчитает в тот же день. Выезд бесплатный.</p>
                <a className="btn big" href="../#naryad">Вызвать замерщика</a>
                <ReviewsBadge dark />
              </div>
              <img src={IMG(PHOTOS.newWindow)} alt="Новое окно в защитной плёнке после монтажа" loading="lazy" />
            </div>
          </div>
        </section>
        <Office />
      </main>
      <Footer />
    </>
  )
}
createRoot(document.getElementById('root')).render(<Okna />)
