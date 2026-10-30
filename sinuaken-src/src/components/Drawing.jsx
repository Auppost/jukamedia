import { useId } from 'react'
import { motion } from 'framer-motion'

function Sash({ x, y, w, h, o }) {
  const i = 7
  const hx = o === 1 ? x + w - 10 : x + 10
  const tip = o === 1 ? x + i : x + w - i
  const base = o === 1 ? x + w - i : x + i
  return (
    <g>
      <rect className="glass" x={x + i} y={y + i} width={w - 2 * i} height={h - 2 * i} />
      {o ? (
        <>
          <rect className="sash" x={x + 3} y={y + 3} width={w - 6} height={h - 6} />
          <line className="handle" x1={hx} y1={y + h / 2 - 9} x2={hx} y2={y + h / 2 + 9} />
          <polyline className="open" points={`${base},${y + i} ${tip},${y + h / 2} ${base},${y + h - i}`} />
        </>
      ) : null}
      <rect className="sash" x={x} y={y} width={w} height={h} />
    </g>
  )
}

function Dim({ x1, x2, y, v }) {
  return (
    <g>
      <line className="dim" x1={x1} y1={y} x2={x2} y2={y} />
      <line className="dim" x1={x1} y1={y - 5} x2={x1} y2={y + 5} />
      <line className="dim" x1={x2} y1={y - 5} x2={x2} y2={y + 5} />
      <text className="dimt" x={(x1 + x2) / 2} y={y + 17} textAnchor="middle">{v}</text>
    </g>
  )
}
function VDim({ x, y1, y2, v }) {
  const cy = (y1 + y2) / 2
  return (
    <g>
      <line className="dim" x1={x} y1={y1} x2={x} y2={y2} />
      <line className="dim" x1={x - 5} y1={y1} x2={x + 5} y2={y1} />
      <line className="dim" x1={x - 5} y1={y2} x2={x + 5} y2={y2} />
      <text className="dimt" x={x + 4} y={cy} dy={-6} textAnchor="middle" transform={`rotate(90 ${x + 4} ${cy})`}>{v}</text>
    </g>
  )
}

export default function Drawing({ t, lit = null, height = 300 }) {
  const hatch = useId().replace(/:/g, '')
  const W = 420, H = height
  const sc = Math.min((W - 90) / t.w, (H - 80) / t.h)
  const fw = t.w * sc, fh = t.h * sc
  const x0 = 52 + (W - 90 - fw) / 2, y0 = 22
  const winH = t.door ? 1330 * sc : fh
  const winW = t.door ? (t.w - t.door) * sc : fw
  const on = (p) => (lit === p ? 'lit' : '')
  let sashes = []
  if (t.door) {
    const dw = t.door * sc
    let x = x0
    t.win.forEach((p, k) => { const w = winW * p.w; sashes.push(<Sash key={'w' + k} x={x + 3} y={y0 + 3} w={w - 6} h={winH - 6} o={p.o} />); x += w })
    sashes.push(<rect key="fw" className="frame" x={x0} y={y0} width={winW} height={winH} />)
    sashes.push(<rect key="fd" className="frame" x={x0 + winW} y={y0} width={dw} height={fh} />)
    sashes.push(<Sash key="d" x={x0 + winW + 3} y={y0 + 3} w={dw - 6} h={fh - 6} o={1} />)
  } else {
    sashes.push(<rect key="f" className="frame" x={x0} y={y0} width={fw} height={fh} />)
    let x = x0
    t.parts.forEach((p, k) => { const w = fw * p.w; sashes.push(<Sash key={k} x={x + 3} y={y0 + 3} w={w - 6} h={fh - 6} o={p.o} />); x += w })
  }
  return (
    <motion.svg
      key={t.n}
      className="dw"
      viewBox={`0 0 ${W} ${y0 + fh + 64}`}
      role="img"
      aria-label={`Чертёж окна тип ${t.n}, ${t.w} на ${t.h} мм`}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
    >
      <defs>
        <pattern id={hatch} width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="8" stroke="#1E3DA6" strokeWidth="2" />
        </pattern>
      </defs>
      <rect className={`part fill ${on('window')}`} x={x0} y={y0} width={fw} height={fh} />
      <rect className={`part fill ${on('reveal')}`} x={x0 - 14} y={y0 - 6} width="10" height={fh + 12} />
      <rect className={`part fill ${on('reveal')}`} x={x0 + fw + 4} y={y0 - 6} width="10" height={fh + 12} />
      <line className={`part-line ${on('sill')}`} x1={x0 - 14} y1={y0 + winH + 7} x2={x0 + winW + (t.door ? 0 : 14)} y2={y0 + winH + 7} />
      <line className={`part-line dashed ${on('drip')}`} x1={x0 - 18} y1={y0 + winH + 13} x2={x0 + winW + (t.door ? 0 : 18)} y2={y0 + winH + 13} />
      {sashes}
      <rect className={`part stroke ${on('install')}`} x={x0 - 4} y={y0 - 4} width={fw + 8} height={fh + 8} />
      <rect className={`part stroke dashed ${on('inside')}`} x={x0 - 24} y={y0 - 14} width={fw + 48} height={fh + 40} />
      <rect className={`part ${on('old')}`} x={x0} y={y0} width={fw} height={fh} fill={`url(#${hatch})`} />
      {t.door ? (
        <>
          <Dim x1={x0} x2={x0 + winW} y={y0 + fh + 34} v={t.w - t.door} />
          <Dim x1={x0 + winW} x2={x0 + fw} y={y0 + fh + 34} v={t.door} />
          <VDim x={x0 + fw + 30} y1={y0} y2={y0 + fh} v={t.h} />
          <VDim x={x0 - 36} y1={y0} y2={y0 + winH} v={1330} />
        </>
      ) : (
        <>
          <Dim x1={x0} x2={x0 + fw} y={y0 + fh + 34} v={t.w} />
          <VDim x={x0 + fw + 30} y1={y0} y2={y0 + fh} v={t.h} />
        </>
      )}
    </motion.svg>
  )
}

export function Mini({ t }) {
  const w = 54, ar = t.h / t.w, h = Math.min(36, w * ar)
  const ww = w * (t.door ? (t.w - t.door) / t.w : 1)
  const op = (a, b, top, bot, k) => <polyline key={k} points={`${a},${top} ${b},${(top + bot) / 2} ${a},${bot}`} strokeWidth="1" strokeDasharray="2 2" />
  const els = []
  if (t.door) {
    const wh = h * 1330 / t.h
    els.push(<rect key="a" x="3" y="2" width={ww} height={wh} />, <rect key="b" x={3 + ww} y="2" width={w - ww} height={h} />, op(3 + w - 2, 3 + ww + 2, 4, h, 'c'))
    if (t.win.length > 1) { const sx = 3 + ww * t.win[0].w; els.push(<line key="d" x1={sx} y1="2" x2={sx} y2={2 + wh} />, op(3 + ww - 2, sx + 2, 4, wh, 'e')) }
  } else {
    els.push(<rect key="r" x="3" y="2" width={w} height={h} />)
    let x = 3
    t.parts.forEach((p, k) => {
      const pw = w * p.w
      if (p.o) els.push(op(p.o === 1 ? x + pw - 2 : x + 2, p.o === 1 ? x + 2 : x + pw - 2, 4, h, 'o' + k))
      x += pw
      if (k < t.parts.length - 1) els.push(<line key={'l' + k} x1={x} y1="2" x2={x} y2={2 + h} />)
    })
  }
  return <svg className="mini" viewBox="0 0 60 40" aria-hidden="true"><g fill="none" strokeWidth="1.6">{els}</g></svg>
}
