// Prices and sizes taken from sinuaken.ee/ru/pvc-okna (October 2026)
// o: 0 fixed, 1 opens (handle right), 2 opens (handle left)
export const TYPES = [
  { n: 1, w: 1530, h: 1330, c: 470, p: 540, parts: [{ w: 0.47, o: 0 }, { w: 0.53, o: 1 }], label: 'двухстворчатое, одна створка открывается' },
  { n: 2, w: 1530, h: 1330, c: 520, p: 590, parts: [{ w: 0.5, o: 2 }, { w: 0.5, o: 1 }], label: 'двухстворчатое, обе створки открываются' },
  { n: 3, w: 2130, h: 1330, c: 600, p: 700, parts: [{ w: 600 / 2130, o: 0 }, { w: 930 / 2130, o: 1 }, { w: 600 / 2130, o: 0 }], label: 'трёхстворчатое, средняя открывается' },
  { n: 4, w: 2130, h: 1330, c: 680, p: 730, parts: [{ w: 600 / 2130, o: 2 }, { w: 930 / 2130, o: 1 }, { w: 600 / 2130, o: 1 }], label: 'трёхстворчатое, все открываются' },
  { n: 5, w: 2200, h: 2120, c: 750, p: 870, door: 750, win: [{ w: 1, o: 0 }], label: 'балконный блок: окно 1450 и дверь 750' },
  { n: 6, w: 2200, h: 2120, c: 810, p: 930, door: 750, win: [{ w: 900 / 1450, o: 0 }, { w: 550 / 1450, o: 1 }], label: 'балконный блок: окно со створкой 550 и дверь 750' },
  { n: 7, w: 3000, h: 1550, c: 740, p: 890, parts: [{ w: 0.24, o: 0 }, { w: 0.26, o: 2 }, { w: 0.26, o: 1 }, { w: 0.24, o: 0 }], label: 'четырёхстворчатое, средние открываются' },
]

export const LINES = {
  classic: { key: 'classic', name: 'CLASSIC', specs: ['Профиль [уточнить]', 'Стеклопакет [уточнить]', 'Фурнитура [уточнить]'] },
  perfect: { key: 'perfect', name: 'PERFECT', specs: ['Профиль [уточнить]', 'Стеклопакет [уточнить]', 'Фурнитура [уточнить]'] },
}

export const INCLUDED = [
  { part: 'window', title: 'Окно ПВХ', text: 'Профиль, стеклопакет и фурнитура выбранной линейки' },
  { part: 'install', title: 'Монтаж', text: 'Установка в проём' },
  { part: 'sill', title: 'Подоконник ПВХ', text: 'Под размер проёма' },
  { part: 'drip', title: 'Отлив снаружи', text: 'Чтобы вода уходила от стены' },
  { part: 'reveal', title: 'Боковые откосы', text: 'По бокам окна' },
  { part: 'inside', title: 'Внутренние работы', text: 'Отделка вокруг окна внутри' },
  { part: 'old', title: 'Демонтаж и вывоз старого окна', text: 'Разбираем, выносим, утилизируем' },
]

export const PHONE = '+372 552 5520'
export const PHONE_HREF = 'tel:+3725525520'

export const IMG = (id, w = 1200) => `https://images.unsplash.com/${id}?w=${w}&q=75&auto=format&fit=crop`
export const PHOTOS = {
  narva: 'photo-1724265663705-d12686fb0e48',
  panel5: 'photo-1689420749398-f5830de58a9a',
  panelOld: 'photo-1630257968172-569c373acfb1',
  panelWinter: 'photo-1761433072289-3a1d44f28ff7',
  newWindow: 'photo-1751486403820-7cf45ebec080',
  sealing: 'photo-1607400201515-c2c41c07d307',
  repair: 'photo-1783587616528-a37972228563',
  sill: 'photo-1783587354617-66b8b7c6a0cb',
  handles: 'photo-1655399558741-cb223ace32c3',
  balcony: 'photo-1785240825091-192585287a11',
  door: 'photo-1691517534724-3732c7621407',
  net: 'photo-1761052056661-05a554df6ff4',
}
