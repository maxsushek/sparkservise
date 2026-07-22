#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Замена экрана (дисплея) iPhone» — вложенный спойк хаба:
/remont-iphone/zamena-ekrana/ (глубина-2). Combined-страница (как топ-конкуренты app-lab):
одна страница ловит и «замена экрана/дисплея», и «замена стекла» — с блоком-решением
«стекло или модуль», чтобы НЕ каннибалить саму себя двумя страницами и сконцентрировать вес.
Переиспользует каркас assemble.py (NAV/FOOTER/STYLE/MODAL_JS/helpers), depth-2 пути.
Цена в таблице — «Замена экрана (дисплея)» (data-svc для CMS), строки ссылаются на модели.
Скрипты/фавикон/og-хост/UA/sitemap — навешивает пайплайн после генерации."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/zamena-ekrana"
NAME = "Замена экрана iPhone"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

# ── цены «Замена экрана (дисплея)» по моделям (из TIERS), ссылка на модель ──
MODELS = [
    ("iPhone 17 Pro Max","iphone-17-pro-max",11000,11000),("iPhone 17 Pro","iphone-17-pro",11000,11000),
    ("iPhone 17 Air","iphone-17-air",10000,10000),("iPhone 17","iphone-17",10000,10000),
    ("iPhone 16 Pro Max","iphone-16-pro-max",8200,8200),("iPhone 16 Pro","iphone-16-pro",8000,8000),
    ("iPhone 16 Plus","iphone-16-plus",7000,7000),("iPhone 16","iphone-16",7000,7000),
    ("iPhone 15 Pro Max","iphone-15-pro-max",5900,5900),("iPhone 15 Pro","iphone-15-pro",4900,4900),
    ("iPhone 15 Plus","iphone-15-plus",4900,4900),("iPhone 15","iphone-15",4900,4900),
    ("iPhone 14 Pro Max","iphone-14-pro-max",4900,4900),("iPhone 14 Pro","iphone-14-pro",4100,4100),
    ("iPhone 14 Plus","iphone-14-plus",3600,3600),("iPhone 14","iphone-14",3400,3400),
    ("iPhone 13 Pro Max","iphone-13-pro-max",3500,3500),("iPhone 13 Pro","iphone-13-pro",3400,3400),
    ("iPhone 13","iphone-13",3100,3100),("iPhone 13 mini","iphone-13-mini",3500,3500),
    ("iPhone 12 Pro Max","iphone-12-pro-max",3200,3200),("iPhone 12 Pro","iphone-12-pro",2900,2900),
    ("iPhone 12","iphone-12",2900,2900),("iPhone 12 mini","iphone-12-mini",2600,2600),
    ("iPhone 11 Pro Max","iphone-11-pro-max",2300,2300),("iPhone 11 Pro","iphone-11-pro",2000,2000),
    ("iPhone 11","iphone-11",2200,2200),("iPhone XS Max","iphone-xs-max",2000,2000),
    ("iPhone XS","iphone-xs",1700,1700),("iPhone XR","iphone-xr",1400,2000),
    ("iPhone X","iphone-x",1700,1700),("iPhone 8 Plus","iphone-8-plus",1000,1000),
    ("iPhone 8","iphone-8",900,900),("iPhone 7 Plus","iphone-7-plus",900,900),
    ("iPhone 7","iphone-7",900,900),("iPhone SE 3 (2022)","iphone-se-2022",1000,1000),
    ("iPhone SE 2 (2020)","iphone-se-2020",900,900),("iPhone SE (2016)","iphone-se-2016",600,600),
]
def grn(n): return format(n, ",d").replace(",", " ")

# ── признаки: что именно с экраном (и куда это ведёт — модуль или только стекло) ──
SIGNS = [
    ("screen","Разбит дисплей, чёрный экран","Экран не показывает изображение, чёрный или белый — нужна замена дисплейного модуля целиком."),
    ("wrench","Полосы, пятна, засветы","Появились полосы, цветные пятна, области засветки или «залипшее» изображение — матрица повреждена, меняется модуль."),
    ("power","Не реагирует на касания","Тачскрин не отвечает полностью или полосами, палец «не слушается» — повреждён сенсорный слой, нужен модуль."),
    ("battery","Разбито только стекло","Стекло в трещинах, но картинка целая и тач работает — можно заменить ТОЛЬКО стекло, это дешевле замены модуля."),
    ("clock","Мерцание, выгорание, битые пиксели","Экран мерцает, есть выгоревшие участки или мёртвые пиксели — ресурс матрицы исчерпан, меняется дисплей."),
    ("shield","Экран приподнялся по краю","Дисплей отходит от корпуса — часто из-за вздутого аккумулятора. Сначала бесплатная диагностика, менять может понадобиться и АКБ."),
]

# ── шаги (процесс) ──
STEPS = [
    ("Бесплатная диагностика","Смотрим, что именно повреждено — только стекло или весь модуль, работает ли тач, Face ID и датчики. Чините без переплаты за лишнее.",""),
    ("Согласуем: стекло или модуль","Честно говорим, достаточно ли замены стекла или нужен дисплейный модуль, называем точную цену по вашей модели. Оплата по факту.",""),
    ("Замена","Дисплейный модуль меняем за 30-60 минут при вас. Переклейку только стекла (по технологии OCA) делаем 1-2 дня — с сохранением родной матрицы.","30-60 мин"),
    ("Проверка и гарантия","Проверяем изображение, тач, яркость, Face ID и датчики. Выдаём гарантию 12 месяцев на экран и работу.","12 месяцев"),
]

# ── FAQ ──
FAQ = [
    ("Сколько стоит замена экрана iPhone?","Зависит от модели и типа ремонта: замена дисплейного модуля — от 900 ₴ на iPhone 7-8, 2200-3500 ₴ на iPhone 11-13, до 8200-11000 ₴ на флагманах iPhone 16-17 Pro Max. Точные цены по моделям — в таблице выше. Если разбито только стекло, а дисплей работает, замена стекла выходит дешевле — стоимость называем после бесплатной диагностики."),
    ("Можно ли заменить только стекло, не меняя весь дисплей?","Да — если разбито только внешнее стекло, а изображение целое и тач работает (нет полос, чёрных пятен, «мёртвых» зон). Тогда мы снимаем битое стекло и приклеиваем новое по технологии OCA, сохраняя вашу родную матрицу. Это заметно дешевле замены всего модуля. Если же есть полосы, пятна или не работает тач — повреждена матрица, и нужен весь дисплейный модуль."),
    ("Чем замена стекла отличается от замены дисплея (модуля)?","Экран iPhone — это «бутерброд»: защитное стекло + сенсор + матрица (OLED/LCD), склеенные в один модуль. Если пострадало только стекло — меняем его отдельно (переклейка). Если повреждена матрица или сенсор (полосы, пятна, нет тача) — меняется весь модуль. На диагностике определяем, что именно нужно, — вы не платите за лишнее."),
    ("Сколько времени занимает замена экрана?","Замена дисплейного модуля — 30-60 минут при вас. Переклейка только стекла сложнее технологически и занимает 1-2 дня, потому что стекло приклеивается к матрице под вакуумом и должно выстояться."),
    ("Какой дисплей вы ставите — оригинал или копию?","Предлагаем варианты: оригинальный дисплей, качественный сервисный (Soft/Hard OLED) и совместимый — с разной ценой и характеристиками. Честно объясняем разницу по яркости, цветопередаче и True Tone до начала работ, выбираете вы под свой бюджет."),
    ("Сохранится ли Face ID и True Tone после замены экрана?","Face ID не зависит от дисплея и продолжает работать — мы аккуратно переносим на новый экран все родные шлейфы и датчики. True Tone сохраняется на оригинальном дисплее; на некоторых совместимых он может отключиться — предупреждаем об этом заранее."),
    ("Какая гарантия на замену экрана?","12 месяцев на экран и работу мастера. Если появятся полосы, засветы или вопросы к сенсору не по вашей вине — бесплатно проверим и заменим по гарантии."),
    ("Разбит экран и телефон не включается — что делать?","Сначала бесплатная диагностика: иногда после падения «чёрный экран» — это не только дисплей, но и повреждение платы или шлейфа. Проверим и честно скажем, поможет ли замена экрана или нужен ремонт платы, до начала работ и без обязательств."),
]

# ── SEO-абзацы ──
SEO = [
    "Разбитый экран — самая частая поломка iPhone. Сервисный центр SPARK в Одессе меняет экраны на всех моделях — от iPhone 7 и SE до iPhone 17 Pro Max. Дисплейный модуль меняем за 30-60 минут при вас, с гарантией 12 месяцев и бесплатной диагностикой перед работой. А если разбито только стекло, а картинка цела — предложим переклейку стекла, это дешевле замены всего модуля.",
    "Перед ремонтом всегда определяем, что именно повреждено: если пострадало только защитное стекло — меняем его отдельно и сохраняем вашу родную матрицу; если есть полосы, пятна или не работает сенсор — нужен весь дисплейный модуль. Так вы не переплачиваете за лишнее. Тип дисплея (оригинал, сервисный OLED или совместимый) подбираем под бюджет и честно объясняем разницу до начала работ. Точную цену по вашей модели видно в таблице выше.",
    "Работаем в центре Одессы на ул. Академика Королёва, 23 — рядом с Киевским рынком. Оплата по факту, без предоплаты. Приходите с любым iPhone или оставьте заявку — перезвоним за 15 минут, подскажем, нужна замена стекла или модуля, и назовём цену.",
]

RELATED = [
    ("../../remont-iphone/","Ремонт iPhone — все услуги"),
    ("../zamena-zadnego-stekla/","Замена заднего стекла iPhone (задняя крышка)"),
    ("../../diagnostika/","Бесплатная диагностика"),
    ("../../blog/original-ili-kopiya-displeya-iphone/","Оригинал или копия дисплея iPhone"),
]

FORM_OPTS = ["Замена экрана / дисплея iPhone", "Разбит дисплей / чёрный экран", "Разбито только стекло (дисплей работает)",
             "Полосы или не работает тач", "Другое (опишу в разговоре)"]

def hero_svg():
    grad = D._GRAD % {"p": "sc"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена экрана iPhone">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#scs)"/>'
      # экран
      '<rect x="40" y="40" width="220" height="280" rx="14" fill="#0e1116"/>'
      '<rect x="120" y="30" width="60" height="14" rx="7" fill="#0e1116"/>'
      # трещина (полилиния)
      '<polyline points="150,60 132,140 168,150 120,300" fill="none" stroke="#E11D2A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
      '<polyline points="132,140 90,120 M168,150 220,110" fill="none" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      '<line x1="168" y1="150" x2="224" y2="118" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      '<line x1="132" y1="140" x2="86" y2="118" stroke="#E11D2A" stroke-width="2.4" stroke-linecap="round"/>'
      # блик «новый экран»
      '<rect x="52" y="52" width="70" height="150" rx="8" fill="rgba(255,255,255,.06)"/>'
      + D._check(210, 250, 20) +
      '<text x="150" y="306" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="18" font-weight="700">Новый экран</text>'
      '<text x="150" y="330" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')

def build():
    title = "Замена экрана iPhone в Одессе — цена от 600 ₴ | SPARK"
    desc = "Замена экрана (дисплея) iPhone в Одессе: модуль за 30-60 минут, гарантия 12 месяцев, бесплатная диагностика. Разбито только стекло? Заменим стекло — дешевле. Все модели."
    kw = "замена экрана iphone, замена дисплея iphone, замена стекла iphone, замена экрана айфон одесса, замена дисплея айфон, разбил экран айфон, замена стекла айфон одесса, переклейка стекла iphone"
    h1 = "Замена экрана (дисплея) iPhone в Одессе"
    sub = "Меняем разбитый экран на любом iPhone: дисплейный модуль — за 30-60 минут при вас. Разбито только стекло, а картинка цела? Заменим стекло — это дешевле. Бесплатная диагностика, гарантия 12 месяцев, оплата по факту."

    lo_min = min(m[2] for m in MODELS)
    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Замена экрана iPhone в Одессе","serviceType":"Замена экрана (дисплея) iPhone",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Замена экрана","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Замена экрана (дисплея) iPhone в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n<script defer src="/price-live.js"></script>\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>Замена экрана</span></div>\n  </div>\n\n'

    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.8</span> <b>Google</b><span class="sep">·</span>158 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          <span>📱 <b>от 600 ₴ · 30-60 минут</b></span>\n        </div>\n'
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    # ── признаки ──
    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Что с экраном</span>\n        <h2>Разбит экран? Смотрим, что именно повреждено</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    # ── БЛОК-РЕШЕНИЕ: стекло или модуль (ключевой combined-раздел, снимает каннибализацию) ──
    p += ('  <section class="sec sec-bg" id="glass-or-module">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Стекло или дисплей</span>\n        <h2>Менять только стекло или весь дисплейный модуль?</h2>\n'
          '        <p class="lead-p">Экран iPhone — это склеенный «бутерброд»: защитное стекло + сенсор + матрица. От того, что именно повреждено, зависит цена. Не платите за лишнее.</p>\n      </div>\n'
          '      <div class="repair-types reveal">\n'
          '        <div class="rtype" style="border-top:3px solid var(--spark)">\n          <h3>Заменить только стекло — дешевле</h3>\n'
          '          <p>Подходит, если <b>разбито только внешнее стекло</b>, а изображение целое и тач работает: нет полос, чёрных пятен и «мёртвых» зон. Снимаем битое стекло и приклеиваем новое по технологии OCA, <b>сохраняя вашу родную матрицу</b>. Занимает 1-2 дня.</p>\n        </div>\n'
          '        <div class="rtype" style="border-top:3px solid #0e1116">\n          <h3>Заменить дисплейный модуль</h3>\n'
          '          <p>Нужен, если повреждена сама матрица или сенсор: <b>полосы, цветные пятна, засветы, не реагирует касание, чёрный экран</b>. Меняется весь модуль целиком, с переносом родных шлейфов и датчиков. Занимает 30-60 минут при вас.</p>\n        </div>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark);margin-top:16px"><ul>'
          '<li><span class="ck">✓</span><span><b>Что именно нужно — покажем на бесплатной диагностике.</b> Проверим стекло, матрицу, тач и датчики, и честно скажем: достаточно стекла или нужен модуль.</span></li>'
          '<li><span class="ck">✓</span><span><b>Не работает тач или есть полосы?</b> Значит, дело не в стекле — переклейка не поможет, нужен дисплейный модуль.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    # ── таблица цен по моделям (модуль; строки ссылаются на модели) ──
    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">Замена экрана %s</a></td><td class="pr" data-price-label="%s" data-price-dash="en" data-svc="Замена экрана (дисплея)">%s ₴</td><td class="time">30-60 мин</td></tr>' % (
            slug, esc(label), esc(label), (grn(lo) if lo==hi else grn(lo)+" – "+grn(hi))) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость замены дисплея по моделям</h2>\n'
          '        <p class="lead-p">Цены на замену дисплейного модуля, ориентировочные. Замена только стекла — дешевле, стоимость называем после диагностики. Нажмите на модель — там все виды ремонта.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена (модуль)</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    # ── качество запчастей (info box) ──
    p += ('  <section class="sec sec-bg" id="info">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Важно знать</span>\n        <h2>Оригинал, сервисный OLED или совместимый дисплей</h2>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Оригинальный дисплей</b> — заводское качество, полная поддержка True Tone. Оптимален для новых флагманов.</span></li>'
          '<li><span class="ck">✓</span><span><b>Сервисный OLED (Soft/Hard)</b> — качественная замена с хорошей яркостью и цветом по разумной цене, наш частый выбор для моделей постарше.</span></li>'
          '<li><span class="ck">✓</span><span><b>Совместимый дисплей</b> — бюджетный вариант; честно скажем, где будет разница по яркости и что на нём может отключиться True Tone.</span></li>'
          '<li><span class="ck">✓</span><span><b>Переклейка стекла — по технологии OCA</b> под вакуумом, с сохранением родной матрицы: экран остаётся «родным», меняется только разбитое стекло.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    # ── процесс ──
    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена экрана за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    # ── почему мы ──
    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Определим, нужна замена стекла или модуля — до начала работ и без обязательств.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На экран и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Модуль за 30-60 минут</h3><p>Меняем дисплей при вас — не нужно оставлять телефон надолго.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    # ── SEO текст + related ──
    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена экрана iPhone в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    # ── FAQ ──
    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене экрана</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    # ── форма ──
    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — назовём цену замены за 15 минут</h2>\n          <p>Бесплатно подскажем, нужна замена стекла или модуля, и назовём цену под вашу модель. Или просто позвоните — мастер на связи.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: замена экрана</h3>\n'
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

    # ── контакты (карта) ──
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена экрана iPhone").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
