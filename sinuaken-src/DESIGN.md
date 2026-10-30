# SinuAken: design system (concept v2)

World: carbonless work order pad. The site is an order sheet a master fills in at your door.

## Palette
- paper #E6ECE2 (page ground, ruled form paper)
- sheet #F7F9F4 (order sheets, slips)
- rule #B3C4BC / rule-soft #D3DDD6 (form lines)
- ink #18221F / ink-2 #4C5B55 (print)
- carbon #1E3DA6, carbon-deep #132A78, carbon-tint #E2E8F8 (everything filled in: prices, links, actions)
- stamp #6B3AA4 (one rubber stamp "ЦЕНА ОКОНЧАТЕЛЬНАЯ", once per page)
- dark band #18221F for the order form block

## Type
- PT Sans Narrow 700: headings, buttons, form labels (printed form)
- PT Sans 400/700: body
- PT Mono: only sizes in mm and sums in EUR

## Components
- Order sheet: head with 2px ink rule, type picker strip, drawing beside line items, CLASSIC/PERFECT switch, total + stamp, action row
- Window drawings: SVG generated from real sizes, dimension lines in mm, opening sashes dashed; parts (sill, drip, reveals, install, inside, old window) light up from the line items
- Slips: price list rows separated by dashed tear lines
- Buttons: flat carbon fill or carbon outline, no radius
- Lists of services: rows with photo, not cards

## Build
React 18 + Vite + framer-motion (multi-page: /, /okna/, /narva/). Source in ~/jukamedia/sinuaken-src, build output copied into ~/jukamedia/sinuaken. Patterns after 21st.dev Tiered Price Configurator (CLASSIC/PERFECT with sliding highlight and rolling price) and Live Product Configurator (4-step order with live drawing and running total), rebuilt by hand because the 21st CLI needs an API key.

## Motion
One authored moment: the stamp lands and the price rolls when type, line or quantity changes. Step content slides in. Respects prefers-reduced-motion.

## Pages
- / : hero + 4-step order (Проём, Линейка, Количество, Заявка), works, process, services, KÜ, reviews, office
- /okna/ : price slips for 7 types with CLASSIC/PERFECT switch, what is included
- /narva/ : landing for Google Ads in Narva, districts, same order

## Photos
All photos are Unsplash stand-ins (hotlinked). Replace with SinuAken's own work: installed windows in Narva flats, balconies, the team, the office on Kreenholmi 10.
