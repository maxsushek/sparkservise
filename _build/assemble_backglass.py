#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Замена заднего стекла iPhone» — вложенный спойк хаба:
/remont-iphone/zamena-zadnego-stekla/ (глубина-2). Отдельный запрос («заднее стекло /
задняя крышка / задняя панель») — НЕ пересекается с «замена экрана/стекла» (переднее),
кросс-линк на страницу экрана разводит фронт/бэк. Только модели со стеклянной задней
крышкой (33 из 38; у iPhone 7/SE корпус алюминиевый). Каркас — assemble.py."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/zamena-zadnego-stekla"
NAME = "Замена заднего стекла iPhone"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

# ── цены «Замена заднего стекла» по моделям (из TIERS); только со стеклянной крышкой ──
MODELS = [
    ("iPhone 17 Pro Max","iphone-17-pro-max",8200,8200),("iPhone 17 Pro","iphone-17-pro",8200,8200),
    ("iPhone 17 Air","iphone-17-air",8200,8200),("iPhone 17","iphone-17",8200,8200),
    ("iPhone 16 Pro Max","iphone-16-pro-max",4750,4750),("iPhone 16 Pro","iphone-16-pro",4750,4750),
    ("iPhone 16 Plus","iphone-16-plus",4600,4600),("iPhone 16","iphone-16",4200,4200),
    ("iPhone 15 Pro Max","iphone-15-pro-max",4200,4200),("iPhone 15 Pro","iphone-15-pro",4200,4200),
    ("iPhone 15 Plus","iphone-15-plus",3500,3500),("iPhone 15","iphone-15",3500,3500),
    ("iPhone 14 Pro Max","iphone-14-pro-max",3100,3100),("iPhone 14 Pro","iphone-14-pro",2800,2800),
    ("iPhone 14 Plus","iphone-14-plus",2900,2900),("iPhone 14","iphone-14",2900,2900),
    ("iPhone 13 Pro Max","iphone-13-pro-max",2400,2400),("iPhone 13 Pro","iphone-13-pro",2400,2400),
    ("iPhone 13","iphone-13",2000,2000),("iPhone 13 mini","iphone-13-mini",1900,1900),
    ("iPhone 12 Pro Max","iphone-12-pro-max",2200,2200),("iPhone 12 Pro","iphone-12-pro",2200,2200),
    ("iPhone 12","iphone-12",2000,2000),("iPhone 12 mini","iphone-12-mini",1700,1700),
    ("iPhone 11 Pro Max","iphone-11-pro-max",1600,1600),("iPhone 11 Pro","iphone-11-pro",1450,1450),
    ("iPhone 11","iphone-11",1300,1300),("iPhone XS Max","iphone-xs-max",950,950),
    ("iPhone XS","iphone-xs",950,950),("iPhone XR","iphone-xr",950,950),
    ("iPhone X","iphone-x",950,950),("iPhone 8 Plus","iphone-8-plus",850,850),
    ("iPhone 8","iphone-8",850,850),
]
def grn(n): return format(n, ",d").replace(",", " ")

# ── признаки: что с задним стеклом ──
SIGNS = [
    ("screen","Разбито заднее стекло","Задняя панель в трещинах или разбита — стекло осыпается, портит вид и защиту корпуса."),
    ("wrench","Стекло крошится и режет","Осколки выпадают, острые края режут руку и цепляют карман — эксплуатировать так небезопасно."),
    ("power","Не работает беспроводная зарядка","После удара по задней панели Qi-зарядка или MagSafe перестали держать — часто дело в разбитом стекле над катушкой."),
    ("shield","Трещины пропускают влагу и пыль","Через щели внутрь попадает пыль и влага — растёт риск для платы и камеры, лучше не тянуть."),
    ("battery","Задняя крышка отходит","Стекло приподнялось, появился зазор — иногда из-за вздутого аккумулятора. Нужна бесплатная диагностика."),
    ("clock","Готовите к продаже","Целая задняя панель заметно поднимает цену и вид телефона при перепродаже или трейд-ин."),
]

# ── шаги (процесс) ──
STEPS = [
    ("Бесплатная диагностика","Проверяем заднее стекло, стекло камеры, беспроводную зарядку и нет ли вздутия АКБ — чтобы менять только то, что нужно.",""),
    ("Согласуем цвет и цену","Подбираем стекло в цвет вашей модели, называем точную стоимость до начала работ. Оплата по факту, без предоплаты.",""),
    ("Снимаем лазером, ставим новое","Старое стекло приклеено намертво — аккуратно снимаем на лазерном станке, не задевая плату, антенны и катушку зарядки, и ставим новое.","1-2 часа"),
    ("Проверка и гарантия","Проверяем беспроводную зарядку, камеру и посадку стекла. Выдаём гарантию 12 месяцев на стекло и работу.","12 месяцев"),
]

# ── FAQ ──
FAQ = [
    ("Сколько стоит замена заднего стекла на iPhone?","Зависит от модели: от 850 ₴ на iPhone 8, 1300-2400 ₴ на iPhone 11-13, до 4200-8200 ₴ на iPhone 15-17. Точные цены по моделям — в таблице выше. Диагностика бесплатная, итоговую стоимость называем до начала работ."),
    ("Как снимают старое заднее стекло?","Заднее стекло приклеено к корпусу очень прочно, поэтому снимаем его на лазерном станке: лазер аккуратно разрушает клеевой слой, не повреждая плату, антенны и катушку беспроводной зарядки. Затем ставим новое стекло на герметик. «Отковырять» стекло без лазера правильно нельзя — можно повредить внутренности."),
    ("Сохранится ли беспроводная зарядка и MagSafe после замены?","Да — при замене сохраняем катушку Qi и магниты MagSafe, переносим их на новую панель. После работы обязательно проверяем беспроводную зарядку. Если Qi не работала из-за разбитого стекла, после замены обычно восстанавливается."),
    ("Сколько времени занимает замена заднего стекла?","Обычно 1-2 часа в мастерской. На моделях со сложной проклейкой или при попутной диагностике можем попросить оставить телефон на несколько часов — скажем об этом сразу."),
    ("Можно ли ходить с разбитым задним стеклом?","Лучше не тянуть: острые осколки режут руку, трещины пропускают внутрь пыль и влагу, а над камерой или катушкой зарядки повреждённое стекло может мешать их работе. Плюс целая задняя панель сохраняет вид и цену телефона."),
    ("Стекло будет оригинального цвета?","Да, подбираем заднее стекло в цвет вашей модели. Если точного оттенка временно нет, предложим ближайший вариант и честно покажем разницу до установки."),
    ("Какая гарантия на замену заднего стекла?","12 месяцев на стекло и работу мастера. Если появятся вопросы к посадке стекла или беспроводной зарядке не по вашей вине — бесплатно проверим и устраним."),
    ("Заднее стекло разбилось, но телефон работает — обязательно менять?","Не срочно, но желательно: через трещины внутрь идёт пыль и влага, острые края опасны, а на некоторых моделях повреждённая панель мешает беспроводной зарядке. Если сомневаетесь — приходите на бесплатную диагностику, честно скажем, стоит ли менять сейчас."),
]

# ── SEO-абзацы ──
SEO = [
    "Заднее стекло (задняя крышка) есть на всех iPhone начиная с iPhone 8 и X — оно защищает корпус, обеспечивает беспроводную зарядку и MagSafe. При падении задняя панель часто трескается или разбивается. Сервисный центр SPARK в Одессе меняет заднее стекло на моделях от iPhone 8 до iPhone 17 Pro Max — с сохранением Qi-зарядки, гарантией 12 месяцев и бесплатной диагностикой.",
    "Заднее стекло приклеено к корпусу очень прочно, поэтому снимаем его на лазерном станке — так мы не повреждаем плату, антенны и катушку беспроводной зарядки. Это отдельная услуга: если у вас разбит передний экран, а не задняя панель, смотрите замену экрана — там про дисплей и переднее стекло. Точную цену по вашей модели видно в таблице выше.",
    "Работаем в центре Одессы на ул. Академика Королёва, 23 — рядом с Киевским рынком. Оплата по факту, без предоплаты. Приходите с любым iPhone или оставьте заявку — перезвоним за 15 минут, подскажем цвет и цену замены заднего стекла.",
]

RELATED = [
    ("../../remont-iphone/","Ремонт iPhone — все услуги"),
    ("../zamena-ekrana/","Замена экрана iPhone (переднее стекло, дисплей)"),
    ("../../diagnostika/","Бесплатная диагностика"),
    ("../zamena-akkumulyatora/","Замена аккумулятора iPhone"),
]

FORM_OPTS = ["Замена заднего стекла iPhone", "Разбито заднее стекло", "Не работает беспроводная зарядка",
             "Трещины на задней панели", "Другое (опишу в разговоре)"]

def hero_svg():
    grad = D._GRAD % {"p": "bg"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена заднего стекла iPhone">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#bgs)"/>'
      '<rect x="40" y="40" width="220" height="280" rx="18" fill="#12151b"/>'
      '<rect x="56" y="56" width="82" height="82" rx="18" fill="#1b1f27" stroke="#2b303a" stroke-width="2"/>'
      '<circle cx="82" cy="82" r="15" fill="#0b0d11" stroke="#2b303a" stroke-width="2"/>'
      '<circle cx="114" cy="112" r="15" fill="#0b0d11" stroke="#2b303a" stroke-width="2"/>'
      '<polyline points="150,150 130,210 176,224 120,300" fill="none" stroke="#E11D2A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
      '<line x1="130" y1="210" x2="88" y2="190" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      '<line x1="176" y1="224" x2="228" y2="196" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      '<circle cx="150" cy="252" r="20" fill="none" stroke="#878d99" stroke-width="2"/>'
      '<path d="M143 252a7 7 0 0114 0M138 252a12 12 0 0124 0" fill="none" stroke="#878d99" stroke-width="2" stroke-linecap="round"/>'
      + D._check(214, 250, 20) +
      '<text x="150" y="312" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="17" font-weight="700">Новое заднее стекло</text>'
      '<text x="150" y="334" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')

def build():
    title = "Замена заднего стекла iPhone в Одессе — цена от 850 ₴ | SPARK"
    desc = "Замена заднего стекла (задней крышки) iPhone в Одессе: снимаем лазером, ставим новое с сохранением беспроводной зарядки и MagSafe. Гарантия 12 месяцев, бесплатная диагностика."
    kw = "замена заднего стекла iphone, замена задней крышки iphone, замена заднего стекла айфон одесса, разбил заднее стекло, замена стекла на задней панели iphone, замена задней крышки айфон"
    h1 = "Замена заднего стекла iPhone в Одессе"
    sub = "Меняем разбитое заднее стекло (заднюю крышку) на iPhone: аккуратно снимаем старое на лазерном станке и ставим новое — с сохранением беспроводной зарядки и MagSafe. Бесплатная диагностика, гарантия 12 месяцев, оплата по факту."

    lo_min = min(m[2] for m in MODELS)
    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Замена заднего стекла iPhone в Одессе","serviceType":"Замена заднего стекла iPhone",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Замена заднего стекла","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Замена заднего стекла iPhone в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n<script defer src="/price-live.js"></script>\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>Замена заднего стекла</span></div>\n  </div>\n\n'

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          <span>📱 <b>от 850 ₴ · снятие лазером</b></span>\n        </div>\n'
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Когда менять</span>\n        <h2>Признаки, что пора менять заднее стекло</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    p += ('  <section class="sec sec-bg" id="how">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как это делают</span>\n        <h2>Почему заднее стекло меняют лазером</h2>\n'
          '        <p class="lead-p">Заднее стекло приклеено к корпусу намертво. Снять его без специнструмента — риск повредить плату, антенны и беспроводную зарядку.</p>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Снимаем на лазерном станке.</b> Лазер аккуратно разрушает клей под стеклом, не задевая внутренности — это правильная технология замены задней панели.</span></li>'
          '<li><span class="ck">✓</span><span><b>Сохраняем беспроводную зарядку и MagSafe.</b> Катушку Qi и магниты переносим на новую панель и проверяем зарядку после работы.</span></li>'
          '<li><span class="ck">✓</span><span><b>Новое стекло в цвет</b> вашей модели, на герметик — восстанавливаем вид и защиту корпуса.</span></li>'
          '<li><span class="ck">✓</span><span><b>Разбит передний экран, а не задняя панель?</b> Это другая услуга — смотрите <a href="../zamena-ekrana/">замену экрана iPhone</a> (дисплей и переднее стекло).</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">Заднее стекло %s</a></td><td class="pr" data-price-label="%s" data-price-dash="en" data-svc="Замена заднего стекла">%s ₴</td><td class="time">1-2 часа</td></tr>' % (
            slug, esc(label), esc(label), (grn(lo) if lo==hi else grn(lo)+" – "+grn(hi))) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость замены заднего стекла по моделям</h2>\n'
          '        <p class="lead-p">Цены ориентировочные, точную назовём после бесплатной диагностики. Нажмите на модель — там все виды ремонта. Заднее стекло меняется на моделях от iPhone 8 (у iPhone 7 и SE корпус алюминиевый).</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена заднего стекла за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Проверим стекло, камеру и беспроводную зарядку до начала работ — без обязательств.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На стекло и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Лазерное снятие</h3><p>Меняем стекло правильно — без риска для платы и беспроводной зарядки.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена заднего стекла iPhone в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене заднего стекла</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — назовём цену замены за 15 минут</h2>\n          <p>Бесплатно подскажем цвет и стоимость заднего стекла под вашу модель. Или просто позвоните — мастер на связи.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: замена заднего стекла</h3>\n'
    p += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что случилось</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">''' + opts + '''</select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Гарантия 12 мес</span><span><b>✓</b> Оплата по факту</span></div>
          </div>
          <div class="sf-success">
            <div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
            <h3>Заявка принята!</h3><p>Перезвоним в течение 15 минут в рабочее время.</p>
            <div class="ms-sum js-summary"></div>
          </div>
        </div>
      </div>
    </div>
  </section>\n\n'''

    p += '''  <section class="sec sec-bg" id="contacts">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Контакты</span><h2>Как нас найти</h2>
        <p class="lead-p">Мы в центре Одессы, рядом с Киевским рынком. Бесплатная диагностика — приходите или вызовите курьера.</p></div>
      <div class="loc-grid reveal">
        <div class="loc-card">
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/><circle cx="12" cy="11" r="2"/></svg></span><div><b>Адрес</b><span>ул. Академика Королёва, 23, Одесса</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><div><b>Часы работы</b><span>Пн-Сб: 10:00-19:00 · Вс: выходной</span></div></div>
          <div class="loc-row"><span class="lr-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 4h4l1.5 5-2 1.2a12 12 0 005.3 5.3l1.2-2 5 1.5v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/></svg></span><div><b>Телефон</b><a href="tel:+380960755452">+38 (096) 075-54-52</a></div></div>
          <a class="btn btn-spark" href="https://www.google.com/maps/dir/?api=1&destination=46.4035605,30.7226524" target="_blank" rel="noopener">Проложить маршрут</a>
        </div>
        <div class="loc-map"><iframe loading="lazy" title="SPARK на карте Одессы" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2751.2871721068323!2d30.720994715589114!3d46.40336147912331!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40c6335e75e1ea93%3A0x24bdf429024f4684!2z0YPQuy4g0JDQutCw0LTQtdC80LjQutCwINCa0L7RgNC-0LvRkdCy0LAsIDIzLA!5e0!3m2!1sru!2sua!4v1667565183335!5m2!1sru!2sua"></iframe></div>
      </div>
    </div>
  </section>
</main>\n\n'''

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена заднего стекла iPhone").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
