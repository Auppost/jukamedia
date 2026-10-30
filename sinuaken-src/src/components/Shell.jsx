import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { PHONE, PHONE_HREF } from '../data'

export function Logo({ href = './' }) {
  return (
    <a className="logo" href={href} aria-label="SinuAken, на главную">
      <svg width="30" height="30" viewBox="0 0 30 30" aria-hidden="true">
        <rect x="3" y="2" width="24" height="26" fill="none" stroke="#1E3DA6" strokeWidth="2.5" />
        <line x1="15" y1="2" x2="15" y2="28" stroke="#1E3DA6" strokeWidth="2" />
        <line x1="18.5" y1="13" x2="18.5" y2="18" stroke="#1E3DA6" strokeWidth="2" />
      </svg>
      SinuAken
    </a>
  )
}

export function Header({ root = './', current }) {
  const links = [
    ['okna', 'Окна и цены', `${root}okna/`],
    ['narva', 'Окна в Нарве', `${root}narva/`],
    ['uslugi', 'Балконы и двери', `${root}#uslugi`],
    ['ky', 'Для КÜ', `${root}#ky`],
  ]
  return (
    <header className="bar">
      <div className="wrap">
        <Logo href={root} />
        <nav className="nav" aria-label="Разделы">
          {links.map(([k, t, h]) => (
            <a key={k} href={h} aria-current={current === k ? 'page' : undefined}>{t}</a>
          ))}
        </nav>
        <div className="lang" aria-label="Язык"><a href="#">ET</a><a href="#" aria-current="true">RU</a><a href="#">EN</a></div>
        <a className="tel" href={PHONE_HREF}>{PHONE}</a>
      </div>
    </header>
  )
}

export function Footer() {
  return (
    <footer>
      <div className="wrap">
        <span>Buono Invest OÜ, рег. код 12615988, Kreenholmi 10, Нарва</span>
        <span><a href="#">Политика конфиденциальности</a> <i className="ph">[нужна]</i></span>
        <span>Фото иллюстративные, заменить на работы SinuAken</span>
      </div>
    </footer>
  )
}

export function Ph({ children }) { return <i className="ph">{children}</i> }

// Price that rolls when it changes
export function Price({ value, className = '' }) {
  const reduce = useReducedMotion()
  return (
    <span className={`price-roll ${className}`} aria-live="polite">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={value}
          initial={reduce ? false : { y: '60%', opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={reduce ? { opacity: 0 } : { y: '-60%', opacity: 0 }}
          transition={{ type: 'spring', stiffness: 420, damping: 32 }}
        >
          {value.toLocaleString('ru-RU')} €
        </motion.span>
      </AnimatePresence>
    </span>
  )
}

export function Stamp({ trigger }) {
  const reduce = useReducedMotion()
  return (
    <motion.div
      key={trigger}
      className="stamp"
      aria-hidden="true"
      initial={reduce ? false : { scale: 1.7, opacity: 0, rotate: -14 }}
      animate={{ scale: 1, opacity: 0.85, rotate: -8 }}
      transition={{ type: 'spring', stiffness: 520, damping: 22 }}
    >
      ЦЕНА<br />ОКОНЧАТЕЛЬНАЯ
    </motion.div>
  )
}

export function ReviewsBadge({ dark = false }) {
  return (
    <div className={`badge ${dark ? 'dark' : ''}`}>
      <span className="stars" aria-hidden="true">★★★★★</span>
      <b>4.8</b>
      <span>21 отзыв в Google</span>
    </div>
  )
}
