"""Подбор по машине: марка → модель (поколение) → диски и выхлопы, которые на неё подходят.

Пишет /js/cars-<lang>.json (данные, грузятся по требованию) и встраивает в главные страницы
список марок и моделей (var CARS) и скрипт подборщика.
Модели и правила сопоставления задаются здесь вручную: (название, regex «подходит», regex «исключить»).
"""
import json, os, re
import build_wheels as W
import build_exhaust as E

ROOT, LANGS = W.ROOT, W.LANGS

M = {
 'Porsche': [
  ('911 Carrera (992)', r'\b992\b', r'GT3|Turbo|GT2|Sport Classic|S/T'), ('911 Turbo / Turbo S (992)', r'\b992\b.*Turbo|Turbo.*\b992\b', ''),
  ('911 GT3 / GT3 RS (992)', r'\b992\b.*GT3|GT3.*\b992\b', ''), ('911 Carrera (991)', r'\b991\b', r'GT3|Turbo|GT2|R\b'),
  ('911 Turbo / Turbo S (991)', r'\b991\b.*Turbo|Turbo.*\b991\b', ''), ('911 GT3 / GT3 RS (991)', r'\b991\b.*GT3|GT3.*\b991\b', ''),
  ('911 GT2 RS (991)', r'GT2', ''), ('911 (997)', r'\b997\b', ''),
  ('718 Cayman / Boxster (982)', r'\b718\b|\b982\b', r'GT4|Spyder'), ('718 Cayman GT4 / GT4 RS / Spyder', r'GT4|718 Spyder', ''),
  ('Cayman / Boxster (981)', r'\b981\b', ''), ('Cayenne', r'Cayenne', ''), ('Macan', r'Macan', ''),
  ('Panamera', r'Panamera', ''), ('Taycan', r'Taycan', '')],
 'BMW': [
  ('M2 (G87)', r'\bG87\b', ''), ('M2 (F87)', r'\bF87\b', ''), ('M3 / M4 (G80 / G82)', r'\bG8[0-3]\b', ''),
  ('M3 / M4 (F80 / F82)', r'\bF8[0-3]\b', ''), ('M3 (E90 / E92)', r'\bE9[0-3]\b', r'335|330'), ('M5 (G90)', r'\bG9[09]\b', ''),
  ('M5 (F90)', r'\bF90\b', ''), ('M5 (F10)', r'\bF10\b.*M5|M5.*\bF10\b', ''), ('M6 (F12 / F13 / F06)', r'\bM6\b', ''),
  ('M8 (F91 / F92)', r'\bF9[123]\b|\bM8\b', ''), ('X5 M / X6 M (F95 / F96)', r'\bF9[56]\b', ''),
  ('X5 / X6 (G05 / G06)', r'\bG0[56]\b', r'\bF9[56]\b'), ('X7 (G07)', r'\bG07\b', ''), ('XM (G09)', r'\bG09\b|\bXM\b', ''),
  ('3 Series (G20)', r'\bG2[01]\b', ''), ('3 Series (F30)', r'\bF3[01]\b', ''), ('5 Series (G30)', r'\bG3[01]\b', ''),
  ('M240i / 2 Series (G42)', r'\bG42\b|M240', ''), ('Z4 / M40i (G29)', r'\bG29\b|\bZ4\b', ''), ('M135i / 1 Series (F40)', r'\bF40\b|M135', '')],
 'Mercedes-Benz / AMG': [
  ('G63 (W463A / W465)', r'G ?63|W46[345]|G-Class|G-Wagon', ''), ('C63 (W205)', r'\bW205\b|C ?63(?!.*W206)', r'W206|C ?43|C ?4[05]0'),
  ('C63 (W206)', r'\bW206\b', ''), ('C43 / C450 (W205)', r'C ?43|C ?4[05]0', ''), ('E63 (W213)', r'E ?63|\bW213\b|\bS213\b', ''),
  ('GLE 63 (C167 / V167)', r'GLE|\b[CV]167\b', ''), ('GLS 63 (X167)', r'GLS|\bX167\b', ''), ('S63 / S-Class (W223 / C217)', r'S ?63|\bW223\b|\bC217\b|S-Class', ''),
  ('SL63 (R232)', r'SL ?63|\bR232\b', ''), ('AMG GT', r'AMG GT|GT ?63|\bC190\b|\bX290\b|GT ?[RS]\b', r'GLE|GLS'),
  ('A-Class / CLA / GLA (W176 / W177)', r'A ?45|CLA ?45|GLA ?45|\bW17[67]\b|\bC11[78]\b|\bX156\b', '')],
 'Audi': [
  ('RS3 (8V / 8Y)', r'RS ?3\b|\b8[VY]\b', ''), ('RS4 / RS5 (B9)', r'RS ?[45]|\bB9\b', r'\bB8\b'), ('A5 / S5 / RS5 (B8)', r'\bB8\b', ''),
  ('RS6 / RS7 (C8)', r'\bC8\b|RS ?[67](?!.*C7)', r'C7'), ('RS6 / RS7 / A6 / A7 (C7)', r'\bC7\b', ''), ('R8', r'\bR8\b', ''),
  ('RSQ8 / SQ8 / Q8', r'Q8', ''), ('Q5 / SQ5', r'Q5', ''), ('RSQ3', r'Q3', ''), ('TT RS', r'\bTT', ''), ('e-tron GT', r'e-?tron', '')],
 'Ferrari': [
  ('296 GTB / GTS', r'\b296\b', ''), ('F8 Tributo / Spider', r'\bF8\b', ''), ('488 GTB / Spider', r'\b488\b', r'Pista'),
  ('488 Pista', r'Pista', ''), ('458 Italia / Spider', r'\b458\b', r'Speciale'), ('458 Speciale', r'Speciale', ''), ('SF90', r'SF90', ''),
  ('812 Superfast / GTS', r'\b812\b', ''), ('F12 Berlinetta / TdF', r'\bF12\b', ''), ('12Cilindri', r'12 ?Cilindri', ''),
  ('Purosangue', r'Purosangue', ''), ('Roma', r'\bRoma\b', ''), ('Portofino', r'Portofino', ''), ('California', r'California', ''),
  ('GTC4Lusso / FF', r'GTC4|Lusso|\bFF\b', '')],
 'Lamborghini': [
  ('Urus', r'Urus', ''), ('Huracán', r'Hurac', ''), ('Aventador', r'Aventador', ''), ('Revuelto', r'Revuelto', ''),
  ('Temerario', r'Temerario', ''), ('Gallardo', r'Gallardo', '')],
 'McLaren': [
  ('750S', r'\b750', ''), ('720S / 765LT', r'\b720|\b765', ''), ('Artura', r'Artura', ''), ('570S / 600LT / 540C', r'\b570|600 ?LT|\b540', ''),
  ('650S / MP4-12C / 675LT', r'\b650|12C|MP4|\b675', ''), ('McLaren GT', r'McLaren GT\b', '')],
 'Maserati': [
  ('MC20', r'MC20', ''), ('GranTurismo / GranCabrio', r'Gran ?(Turismo|Cabrio)', ''), ('Quattroporte', r'Quattroporte', ''),
  ('Ghibli', r'Ghibli', ''), ('Levante', r'Levante', ''), ('Grecale', r'Grecale', '')],
 'Bentley': [('Bentayga', r'Bentayga', ''), ('Continental GT', r'Continental', ''), ('Flying Spur', r'Flying Spur', '')],
 'Rolls-Royce': [('Cullinan', r'Cullinan', ''), ('Ghost', r'Ghost', ''), ('Wraith / Dawn', r'Wraith|Dawn', ''), ('Spectre', r'Spectre', '')],
 'Land Rover': [('Range Rover (L460)', r'L460|Range Rover(?! Sport)', r'Sport'), ('Range Rover Sport', r'Range Rover Sport', ''), ('Defender', r'Defender', '')],
 'Tesla': [('Model 3', r'Model 3', ''), ('Model Y', r'Model Y', ''), ('Model S', r'Model S', ''), ('Model X', r'Model X', '')],
 'Volkswagen': [('Golf R / GTI (Mk7)', r'Mk ?VII\b|Mk ?7\b', ''), ('Golf R / GTI (Mk8)', r'Mk ?VIII|Mk ?8\b', ''), ('Arteon R', r'Arteon', ''), ('Touareg', r'Touareg', '')],
 'Mini': [('Cooper S / JCW (F56)', r'\bF5[4-7]\b', ''), ('Cooper S / JCW (R56)', r'\bR5[6-9]\b', '')],
 'Nissan': [('GT-R (R35)', r'GT-?R', ''), ('370Z / Z', r'370Z|Nissan Z\b', '')],
 'Ford': [('Mustang', r'Mustang', ''), ('F-150 / Raptor', r'F-?150|Raptor', ''), ('Focus RS', r'Focus', '')],
 'Toyota': [('GR Supra', r'Supra', ''), ('GR Yaris', r'Yaris', ''), ('Land Cruiser', r'Land Cruiser', '')],
 'Lexus': [('LC 500', r'\bLC\b', ''), ('RC F', r'\bRC ?F\b', ''), ('LX / GX', r'\b[LG]X\b', '')],
 'Volvo': [('XC90', r'XC90', ''), ('XC60', r'XC60', '')],
}
MAKE_RX = {'Mercedes-Benz / AMG': r'Mercedes|AMG|\bW46|\bG ?63', 'Land Rover': r'Land Rover|Range Rover|Defender',
           'Volkswagen': r'Volkswagen|\bVW\b|Golf', 'Mini': r'Mini', 'BMW': r'BMW|\bM[2-8]\b'}
OLD = {'Mercedes-AMG': 'Mercedes-Benz / AMG'}  # ключи марок в ручных подборках
S = {
 'ru': dict(other='Другая', other_model='Другая модель', model='Модель', wheels='Диски', exh='Выхлоп iPE для этой машины',
            exh_all='Все системы iPE для {m}', none='Моделей именно под эту машину пока нет, но BC Forged и Brixton делают диски под любую машину: подберём посадку и покажем эскиз',
            gen='под любую машину'),
 'et': dict(other='Muu', other_model='Muu mudel', model='Mudel', wheels='Veljed', exh='iPE väljalaskesüsteemid sellele autole',
            exh_all='Kõik iPE süsteemid: {m}', none='Just sellele autole tehtud mudeleid veel pole, kuid BC Forged ja Brixton valmistavad velgi igale autole: kontrollime sobivust ja näitame eskiisi',
            gen='igale autole'),
 'en': dict(other='Other', other_model='Other model', model='Model', wheels='Wheels', exh='iPE exhaust for this car',
            exh_all='All iPE systems for {m}', none='No models made specifically for this car yet, but BC Forged and Brixton build wheels for any car: we check fitment and show you a sketch',
            gen='fits any car'),
}
TYPE_ORDER = [t[0] for t in E.TYPES]

def small(src):
    return re.sub(r'-960\.webp$', '-480.webp', src) if re.search(r'/img/(bc|shop)/', src) else src

def match(text, inc, exc):
    return re.search(inc, text, re.I) and not (exc and re.search(exc, text, re.I))

def build(lang):
    s = S[lang]
    wheels, _ = W.collect(lang)
    wheels = {k: w for k, w in wheels.items() if w['imgs']}
    curated = json.load(open(os.path.join(ROOT, 'tools', f'fitment-{lang}.json')))
    items, idx = [], {}

    def add(key, it):
        if key not in idx:
            idx[key] = len(items); items.append(it)
        return idx[key]

    def wheel(k, specific):
        w = wheels[k]
        return add('w:' + k + (':s' if specific else ''), dict(u=f'wheels/{k}/', i=small(w['imgs'][0]), b=w['b'], n=w['n'],
                   s=(w['spec'][0] if w['spec'] else '') if not specific else (w['spec'][0] if w['spec'] else ''), p=w['p'], f=1 if specific else 0))

    general = [k for k, w in wheels.items() if w['featured'] and w['p']][:4]
    out, exmk = {}, {}
    for make, models in M.items():
        mrx = MAKE_RX.get(make, re.escape(make))
        exs = [d for d in E.ITEMS if re.search(mrx, d['car'] + ' ' + d['make'], re.I)]
        sw = {k: w for k, w in wheels.items() if w.get('title') and re.search(mrx, w['title'], re.I)}
        out[make] = {}
        if exs:
            exmk[make] = E.mk(max({d['make'] for d in exs}, key=lambda m: sum(1 for d in exs if d['make'] == m)))
        for label, inc, exc in models:
            wl = []
            for om, lst in curated.get(next((o for o, n in OLD.items() if n == make), make), {}).items():
                if match(f'{make} {om}', inc, exc) or match(om, inc, exc):
                    for x in lst:
                        k = W.slug(x['b'], x['n']); k = W.MERGED.get(k, k)
                        if k in wheels:
                            wl.append(wheel(k, x['b'] not in ('BC Forged', 'Brixton Forged', 'Brixton')))
            for k, w in sw.items():
                if match(w['title'], inc, exc):
                    wl.append(wheel(k, True))
            wl = list(dict.fromkeys(wl))[:12]
            xl = [d for d in exs if match(d['car'], inc, exc)]
            xl.sort(key=lambda d: (next((i for i, t in enumerate(E.TYPES) if t is d['typ']), 99), d['mat'] != 'ti'))
            xi = []
            for d in xl[:8]:
                h1, tl = E.names(d, lang)
                xi.append(add('x:' + d['slug'], dict(u=f'exhaust/{d["slug"]}/', i=small(d['imgs'][0]), b='iPE', n=tl, s=d['car'], p=d['p'], f=1)))
            if len(wl) < 4:
                wl += [wheel(k, False) for k in general][:4 - len(wl)]
            out[make][label] = [wl, xi]
    data = dict(items=items, cars=out, ex=exmk)
    return data

JS = r'''/* by-car picker */
(function(){
  var CARS=__CARS__,L=__L__,P="__P__",IB="/img/",data=null,want=null;
  var makesEl=document.getElementById("makes"),modelsEl=document.getElementById("models2"),fit=document.getElementById("fit");
  var cur={make:null,model:null};
  function fmt(p){__FMT__}
  function load(cb){if(data){cb();return}want=cb;if(load.busy)return;load.busy=1;fetch("/js/cars-__LANG__.json?v=__V__").then(function(r){return r.json()}).then(function(d){data=d;if(want){var w=want;want=null;w()}}).catch(function(){load.busy=0})}
  function card(it){
    var a=document.createElement("a");a.className="w";a.href=P+it.u;
    a.innerHTML='<div class="stage"><img loading="lazy" decoding="async" alt=""></div>'+(it.f?'<span class="tag"></span>':'')+'<span class="brand"></span><h3></h3><div class="spec"></div><div class="price"></div>';
    var im=a.querySelector("img");im.src=IB+it.i.replace(/^\/img\//,"");im.alt=it.b+" "+it.n;im.addEventListener("error",function(){im.classList.add("gone")});
    if(it.f)a.querySelector(".tag").textContent=L.tag;
    a.querySelector(".brand").textContent=it.b;a.querySelector("h3").textContent=it.n;a.querySelector(".spec").textContent=it.s||"";a.querySelector(".price").textContent=fmt(it.p);
    return a;
  }
  function head(t,link,href){var h=document.createElement("div");h.className="fit-h";var b=document.createElement("h3");b.textContent=t;h.appendChild(b);if(link){var a=document.createElement("a");a.href=href;a.textContent=link;h.appendChild(a)}return h}
  var hashFix=location.hash&&location.hash!=="#cars"?location.hash:null,t0=Date.now();
  function render(){
    load(function(){
      var row=(data.cars[cur.make]||{})[cur.model]||[[],[]];
      fit.innerHTML="";
      var g1=document.createElement("div");g1.className="fit-g";
      row[0].forEach(function(i){var it=data.items[i];var a=card(it);a.addEventListener("click",function(){document.getElementById("fWheel").value=it.b+" "+it.n;setCar();});g1.appendChild(a)});
      var spec=row[0].some(function(i){return data.items[i].f});
      fit.appendChild(head(L.wheels));
      if(!spec){var n=document.createElement("p");n.className="fit-note";n.textContent=L.none;fit.appendChild(n)}
      fit.appendChild(g1);
      if(row[1].length){
        fit.appendChild(head(L.exh,L.exh_all.replace("{m}",cur.make),P+"exhaust/"+data.ex[cur.make]+"/"));
        var g2=document.createElement("div");g2.className="fit-g";
        row[1].forEach(function(i){var it=data.items[i];var a=card(it);a.addEventListener("click",function(){document.getElementById("fWheel").value="iPE "+it.n+" "+it.s;setCar();});g2.appendChild(a)});
        fit.appendChild(g2);
      }
      if(hashFix){var tg=document.querySelector(hashFix);if(tg&&Date.now()-t0<4000)tg.scrollIntoView();hashFix=null}
    });
    document.getElementById("fitCar").textContent=cur.make+" "+cur.model;
  }
  function setCar(){
    var mk=document.getElementById("fMake"),found=false;
    for(var i=0;i<mk.options.length;i++){if(mk.options[i].text===cur.make){mk.selectedIndex=i;found=true;}}
    if(!found)mk.value=L.other;
    if(window.__fillF)window.__fillF(cur.model);else{document.getElementById("fModel").value=cur.model;document.getElementById("fModel").dispatchEvent(new Event("input"));}
  }
  function reveal(box,b){if(b&&box.scrollWidth>box.clientWidth)box.scrollLeft=b.offsetLeft-box.offsetLeft-(box.clientWidth-b.offsetWidth)/2}
  function pickModel(m){cur.model=m;modelsEl.querySelectorAll("button").forEach(function(b){var on=b.textContent===m;b.setAttribute("aria-pressed",String(on));if(on)reveal(modelsEl,b)});render();}
  function pickMake(mk,model){
    cur.make=mk;
    makesEl.querySelectorAll("button").forEach(function(b){var on=b.textContent===mk;b.setAttribute("aria-selected",String(on));if(on)reveal(makesEl,b)});
    modelsEl.innerHTML="";
    CARS[mk].forEach(function(m){var b=document.createElement("button");b.type="button";b.textContent=m;b.addEventListener("click",function(){pickModel(m);});modelsEl.appendChild(b);});
    pickModel(model&&CARS[mk].indexOf(model)>-1?model:CARS[mk][0]);
  }
  Object.keys(CARS).forEach(function(mk){var b=document.createElement("button");b.type="button";b.setAttribute("role","tab");b.textContent=mk;b.addEventListener("click",function(){pickMake(mk);});makesEl.appendChild(b);});
  document.getElementById("fitGo").addEventListener("click",setCar);
  /* hero and form: model list depends on make */
  function fillModels(sel,mk){
    var keep=sel.value;sel.innerHTML="";
    var o=document.createElement("option");o.value="";o.textContent=L.model;sel.appendChild(o);
    (CARS[mk]||[]).forEach(function(m){var o=document.createElement("option");o.textContent=m;sel.appendChild(o)});
    var x=document.createElement("option");x.value="__other";x.textContent=L.other_model;sel.appendChild(x);
    if(keep)sel.value=keep;
  }
  var pm=document.getElementById("pMake"),pd=document.getElementById("pModel");
  pm.addEventListener("change",function(){pd.value="";fillModels(pd,pm.value);if(CARS[pm.value])load(function(){})});
  fillModels(pd,"");
  /* quote form: make -> model list, "other model" opens a text field */
  var fm=document.getElementById("fMake"),fs=document.getElementById("fModelSel"),fi=document.getElementById("fModel");
  function syncF(){var v=fs.value;if(v==="__other"){if((CARS[fm.value]||[]).indexOf(fi.value)>-1)fi.value="";fi.hidden=false;}else{fi.hidden=true;fi.value=v;}fi.dispatchEvent(new Event("input"));}
  function fillF(model){fillModels(fs,fm.value);fs.value="";if(model){if((CARS[fm.value]||[]).indexOf(model)>-1)fs.value=model;else{fs.value="__other";fi.value=model;}}else if(fm.value&&!CARS[fm.value])fs.value="__other";syncF();}
  fm.addEventListener("change",function(){fi.value="";fillF("");});
  fs.addEventListener("change",function(){syncF();if(fs.value==="__other")fi.focus();});
  fillF("");window.__fillF=fillF;
  var started=false;function start(){if(started)return;started=true;pickMake(Object.keys(CARS)[0])}
  if("IntersectionObserver" in window){var io=new IntersectionObserver(function(e){if(e[0].isIntersecting){start();io.disconnect()}},{rootMargin:"600px"});io.observe(document.getElementById("cars"))}else start();
  window.__pickCar=function(make,model){if(!CARS[make])return false;started=true;pickMake(make,model);return true;};
  window.__carsReady=function(cb){load(function(){setTimeout(cb,30)})};window.__carsStart=start;
  window.addEventListener("load",function(){setTimeout(start,1200)});
})();
'''

def inject(lang, data):
    s = S[lang]
    path = os.path.join(ROOT, LANGS[lang], 'index.html')
    h = open(path).read()
    tag = re.search(r'class="tag">([^<]+)<', h)
    tagtxt = tag.group(1) if tag else {'ru': 'под эту машину', 'et': 'sellele autole', 'en': 'made for this car'}[lang]
    fm = re.search(r'function fmt\(p\)\{(.*?)\}\n', h).group(1)
    L = dict(s, tag=tagtxt)
    js = (JS.replace('__CARS__', json.dumps({m: list(v) for m, v in data['cars'].items()}, ensure_ascii=False, separators=(',', ':')))
            .replace('__L__', json.dumps(L, ensure_ascii=False)).replace('__P__', '/' + LANGS[lang]).replace('__FMT__', fm)
            .replace('__LANG__', lang).replace('__V__', W.V(f'js/cars-{lang}.json')))
    a = h.index('/* by-car picker */\n(function(){')
    b = h.index('})();\n', a) + len('})();\n')
    h = h[:a] + js + h[b:]
    # hero: модель выбирается из списка
    h = re.sub(r'<input id="pModel"[^>]*>', f'<select id="pModel" aria-label="{s["model"]}"><option value="">{s["model"]}</option></select>', h)
    # список марок в формах
    makes = list(data['cars']) + [s['other']]
    h = re.sub(r'var MAKES=\[[^\]]*\];', 'var MAKES=' + json.dumps(makes, ensure_ascii=False) + ';', h)
    # форма заявки: модель выбирается из списка, «Другая модель» открывает поле ввода; год из списка
    h = h.replace('<datalist id="fModelList"></datalist>', '')
    h = re.sub(r'(<input id="fModel"[^>]*?) list="fModelList"', r'\1', h)
    if 'id="fModelSel"' not in h:
        h = h.replace('<input id="fModel"', f'<select id="fModelSel" aria-label="{s["model"]}"><option value="">{s["model"]}</option></select><input id="fModel" hidden style="grid-column:1/-1"', 1)
    m = re.search(r'<input id="fYear" placeholder="([^"]*)" [^>]*>', h)
    if m:
        old_lbl = {'ru': 'до 1990', 'et': 'enne 1990', 'en': 'before 1990'}[lang]
        opts = ''.join(f'<option>{y}</option>' for y in range(2027, 1989, -1)) + f'<option>{old_lbl}</option>'
        h = h.replace(m.group(0), f'<select id="fYear" aria-label="{m.group(1)}"><option value="">{m.group(1)}</option>{opts}</select>', 1)
    if '#fModel[hidden]' not in h:
        h = h.replace('</style>', '#fModel[hidden]{display:none}</style>', 1)
    h = h.replace('$("fModel").value=$("pModel").value==="__other"?"":$("pModel").value;go(1);', '$("fModel").value=$("pModel").value==="__other"?"":$("pModel").value;if(window.__fillF)window.__fillF($("fModel").value);go(1);')
    # «Другая модель» в hero не переносим в форму
    h = h.replace('$("fModel").value=$("pModel").value;go(1);', '$("fModel").value=$("pModel").value==="__other"?"":$("pModel").value;go(1);')
    h = h.replace('''var target=(window.__pickCar&&window.__pickCar($("pMake").value))?"cars":"quote";
  $(target).scrollIntoView({behavior:reduce?"auto":"smooth"});''', '''var mk=$("pMake").value,md=$("pModel").value;
  (window.__carsReady||function(f){f()})(function(){var target=(window.__pickCar&&md!=="__other"&&window.__pickCar(mk,md))?"cars":"quote";
  if(target==="quote"&&window.__carsStart)window.__carsStart();
  setTimeout(function(){$(target).scrollIntoView({behavior:reduce?"auto":"smooth"})},60);});''')
    if '.fit-g{' not in h:
        h = h.replace('</style>', '.fit{display:block}.fit-g{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.fit-h{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px 16px;margin:28px 0 14px}.fit-h:first-child{margin-top:0}.fit-h h3{font-family:var(--display);font-size:22px;font-weight:600}.fit-h a{color:var(--bronze);font-weight:600}.fit-note{color:var(--graphite);max-width:62ch;margin:-4px 0 14px}@media (max-width:900px){.fit-g{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}@media (max-width:640px){.makes,.models{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;margin-inline:-24px;padding-inline:24px;scroll-padding-inline:24px}.makes::-webkit-scrollbar,.models::-webkit-scrollbar{display:none}.makes button,.models button{flex:none;white-space:nowrap}}</style>', 1)
    open(path, 'w').write(h)

def main():
    for lang in LANGS:
        data = build(lang)
        p = os.path.join(ROOT, 'js', f'cars-{lang}.json')
        json.dump(data, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
        inject(lang, data)
        n = sum(len(v) for v in data['cars'].values())
        spec = sum(1 for m in data['cars'].values() for r in m.values() if any(data['items'][i]['f'] for i in r[0]) or r[1])
        print(lang, len(data['cars']), 'makes', n, 'models,', spec, 'with car-specific items,', len(data['items']), 'items,', os.path.getsize(p) // 1024, 'KB')

if __name__ == '__main__':
    main()
