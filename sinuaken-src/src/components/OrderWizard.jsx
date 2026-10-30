import { useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { TYPES, LINES, INCLUDED, PHONE, PHONE_HREF } from '../data'
import Drawing, { Mini } from './Drawing'
import { Price, Stamp, ReviewsBadge, Ph } from './Shell'

const STEPS = ['Проём', 'Линейка', 'Количество', 'Заявка']

export default function OrderWizard({ city = '' }) {
  const reduce = useReducedMotion()
  const [step, setStep] = useState(0)
  const [dir, setDir] = useState(1)
  const [ti, setTi] = useState(0)
  const [custom, setCustom] = useState(false)
  const [line, setLine] = useState('classic')
  const [qty, setQty] = useState(1)
  const [net, setNet] = useState(false)
  const [lit, setLit] = useState(null)
  const [sent, setSent] = useState(false)
  const [phone, setPhone] = useState('')
  const [err, setErr] = useState('')

  const t = TYPES[ti]
  const unit = line === 'classic' ? t.c : t.p
  const total = unit * qty
  const go = (n) => { setDir(n > step ? 1 : -1); setStep(n) }

  const submit = (e) => {
    e.preventDefault()
    if (phone.replace(/\D/g, '').length < 7) { setErr('Укажите телефон, по нему перезвонит мастер'); return }
    setErr(''); setSent(true)
  }

  const slide = {
    enter: (d) => (reduce ? { opacity: 0 } : { x: d * 40, opacity: 0 }),
    center: { x: 0, opacity: 1 },
    exit: (d) => (reduce ? { opacity: 0 } : { x: d * -40, opacity: 0 }),
  }

  return (
    <div className="sheet wizard" id="naryad">
      <div className="sheet-head">
        <h2>Наряд на окно{city ? `, ${city}` : ''}</h2>
        <ol className="stepper" aria-label="Шаги">
          {STEPS.map((s, i) => (
            <li key={s}>
              <button type="button" onClick={() => go(i)} aria-current={i === step ? 'step' : undefined} className={i < step ? 'done' : ''} disabled={sent}>
                <span className="box" aria-hidden="true">{i < step ? '✓' : i + 1}</span>{s}
              </button>
            </li>
          ))}
        </ol>
      </div>

      <div className="wz-body">
        <div className="wz-step">
          <motion.div key={sent ? 'sent' : step} custom={dir} variants={slide} initial="enter" animate="center" transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}>
              {sent ? (
                <div className="done-note">
                  <h3>Наряд отправлен</h3>
                  <p>Мастер перезвонит в рабочее время, пн–пт 10–18, и договорится о бесплатном замере.</p>
                  <p className="mono">{custom ? 'Окно по замеру' : `Тип ${t.n}, ${t.w}×${t.h}, ${LINES[line].name}, ${qty} шт., ${total} €`}{net ? ', с москитной сеткой' : ''}</p>
                  <a className="btn ghost" href={PHONE_HREF}>Или позвонить сейчас: {PHONE}</a>
                </div>
              ) : step === 0 ? (
                <div>
                  <p className="q">Какой у вас проём? Размеры в мм, высота с подставочным профилем.</p>
                  <div className="types">
                    {TYPES.map((x, i) => (
                      <button key={x.n} type="button" aria-pressed={!custom && i === ti} onClick={() => { setTi(i); setCustom(false) }}>
                        <Mini t={x} />
                        <span className="sz">{x.w}×{x.h}</span>
                        <span className="from">от {x.c} €</span>
                      </button>
                    ))}
                    <button type="button" className="other" aria-pressed={custom} onClick={() => { setCustom(true); go(3) }}>
                      <span className="sz">Другой размер</span>
                      <span className="from">замер бесплатно</span>
                    </button>
                  </div>
                </div>
              ) : step === 1 ? (
                <div>
                  <p className="q">Выберите линейку окна. Всё, что входит в цену, одинаково в обеих.</p>
                  <div className="tiers" role="radiogroup" aria-label="Линейка">
                    {Object.values(LINES).map((l) => {
                      const on = line === l.key
                      return (
                        <button key={l.key} type="button" role="radio" aria-checked={on} className="tier" onClick={() => setLine(l.key)}>
                          {on && <motion.span layoutId="tier-bg" className="tier-bg" transition={{ type: 'spring', stiffness: 500, damping: 38 }} />}
                          <span className="tier-name">{l.name}</span>
                          <Price value={l.key === 'classic' ? t.c : t.p} className="tier-price" />
                          <ul className="tier-specs">{l.specs.map((s) => <li key={s}><Ph>{s}</Ph></li>)}</ul>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ) : step === 2 ? (
                <div>
                  <p className="q">Сколько таких окон? Цена считается за каждое.</p>
                  <div className="qty">
                    <button type="button" aria-label="Меньше" onClick={() => setQty(Math.max(1, qty - 1))} disabled={qty <= 1}>−</button>
                    <output aria-live="polite">{qty}</output>
                    <button type="button" aria-label="Больше" onClick={() => setQty(Math.min(30, qty + 1))}>+</button>
                    <span>шт.</span>
                  </div>
                  <label className="check">
                    <input type="checkbox" checked={net} onChange={(e) => setNet(e.target.checked)} />
                    <span>Москитная сетка <small>цену скажет мастер на замере</small></span>
                  </label>
                  <p className="hint">Нужны окна разных типов? Отметьте одно, остальные посчитаем на замере.</p>
                </div>
              ) : (
                <form onSubmit={submit} noValidate>
                  <p className="q">{custom ? 'Оставьте телефон, мастер приедет и замерит бесплатно.' : 'Оставьте телефон, мастер приедет, проверит размеры и подтвердит цену.'}</p>
                  <label>Имя<input name="name" autoComplete="name" placeholder="Как к вам обращаться" /></label>
                  <label>Телефон<input name="phone" type="tel" autoComplete="tel" placeholder="+372" value={phone} onChange={(e) => setPhone(e.target.value)} aria-invalid={!!err} aria-describedby="perr" /></label>
                  {err && <p className="err" id="perr">{err}</p>}
                  <label>Город
                    <select defaultValue={city || 'Нарва'}>
                      {['Нарва', 'Нарва-Йыэсуу', 'Силламяэ', 'Йыхви', 'Кохтла-Ярве', 'Кивиыли', 'Другой'].map((c) => <option key={c}>{c}</option>)}
                    </select>
                  </label>
                  <button className="btn big" type="submit">Отправить наряд</button>
                  <ReviewsBadge />
                  <p className="fine">Нажимая кнопку, вы соглашаетесь на обработку данных <Ph>[ссылка на политику]</Ph></p>
                </form>
              )}
            </motion.div>
          {!sent && (
            <div className="wz-nav">
              {step > 0 ? <button type="button" className="link" onClick={() => go(step - 1)}>Назад</button> : <span />}
              {step < 3 && <button type="button" className="btn" onClick={() => go(step + 1)}>{step === 2 ? 'К заявке' : 'Дальше'}</button>}
            </div>
          )}
        </div>

        <aside className="wz-sum" aria-label="Итог наряда">
          {custom ? (
            <div className="custom-note"><h3>Размер по замеру</h3><p>Мастер приедет, замерит проём и посчитает цену в тот же день. Выезд бесплатный.</p></div>
          ) : (
            <>
              <Drawing t={t} lit={lit} height={250} />
              <p className="caption">Тип {t.n}: {t.label}</p>
            </>
          )}
          <ul className="lines">
            {INCLUDED.map((it) => (
              <li key={it.part} onMouseEnter={() => setLit(it.part)} onMouseLeave={() => setLit(null)} onFocus={() => setLit(it.part)} onBlur={() => setLit(null)} tabIndex={0} className={lit === it.part ? 'on' : ''}>
                <span>{it.part === 'window' && !custom ? `Окно ${LINES[line].name}` : it.title}</span><span>включено</span>
              </li>
            ))}
            {net && <li><span>Москитная сетка</span><span>на замере</span></li>}
          </ul>
          <div className="total">
            {!custom && <Stamp trigger={`${ti}-${line}-${qty}`} />}
            <div className="sum-right">
              <small>{custom ? 'итого' : qty > 1 ? `итого за ${qty} шт.` : 'итого'}</small>
              {custom ? <span className="price-roll">по замеру</span> : <Price value={total} />}
            </div>
          </div>
        </aside>
      </div>

      {!sent && (
        <div className="mbar" aria-hidden={step === 3}>
          <span>{custom ? 'по замеру' : `${total} €`}</span>
          {step < 3 ? <button type="button" className="btn" onClick={() => go(step + 1)}>{step === 2 ? 'К заявке' : 'Дальше'}</button> : null}
        </div>
      )}
    </div>
  )
}
