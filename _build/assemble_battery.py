#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страницы услуги «Замена аккумулятора iPhone» — вложенный спойк хаба:
/remont-iphone/zamena-akkumulyatora/ (глубина-2). Переиспользует каркас assemble.py
(NAV/FOOTER/STYLE/MODAL_JS/helpers), деривит depth-2 пути (../ -> ../../).
Уникальные блоки: SVG-герой «батарея+искра», таблица цен по 38 моделям (строки ССЫЛАЮТСЯ
на модельные страницы — модель-агностичный ранжирующий сигнал + модельный лонг-тейл у моделей).
Скрипты/фавикон/og-хост/UA — навешивает пайплайн после генерации."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esc, escA, icon = D.esc, D.escA, D.icon
SLUG = "remont-iphone/zamena-akkumulyatora"
NAME = "Замена аккумулятора iPhone"
CANON = "https://sparkservice.od.ua/" + SLUG + "/"

# depth-2 nav/footer из общих (в этих строках ../ встречается только в href/src)
def d2(s): return s.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
NAV2, FOOTER2 = d2(D.NAV), d2(D.FOOTER)

# ── данные: цена аккумулятора по моделям (из калькулятора хаба), ссылка на модель ──
MODELS = [
    ("iPhone 17 Pro Max","iphone-17-pro-max",2000,2600),("iPhone 17 Pro","iphone-17-pro",1800,2400),
    ("iPhone 17 Air","iphone-17-air",1700,2300),("iPhone 17","iphone-17",1600,2200),
    ("iPhone 16 Pro Max","iphone-16-pro-max",1800,2400),("iPhone 16 Pro","iphone-16-pro",1600,2200),
    ("iPhone 16 Plus","iphone-16-plus",1500,2100),("iPhone 16","iphone-16",1400,2000),
    ("iPhone 15 Pro Max","iphone-15-pro-max",1500,2100),("iPhone 15 Pro","iphone-15-pro",1400,1900),
    ("iPhone 15 Plus","iphone-15-plus",1300,1800),("iPhone 15","iphone-15",1200,1700),
    ("iPhone 14 Pro Max","iphone-14-pro-max",1300,1900),("iPhone 14 Pro","iphone-14-pro",1200,1800),
    ("iPhone 14 Plus","iphone-14-plus",1100,1600),("iPhone 14","iphone-14",1000,1500),
    ("iPhone 13 Pro Max","iphone-13-pro-max",1000,1500),("iPhone 13 Pro","iphone-13-pro",950,1450),
    ("iPhone 13","iphone-13",900,1400),("iPhone 13 mini","iphone-13-mini",900,1350),
    ("iPhone 12 Pro Max","iphone-12-pro-max",900,1350),("iPhone 12 Pro","iphone-12-pro",870,1300),
    ("iPhone 12","iphone-12",850,1300),("iPhone 12 mini","iphone-12-mini",850,1250),
    ("iPhone 11 Pro Max","iphone-11-pro-max",870,1250),("iPhone 11 Pro","iphone-11-pro",860,1230),
    ("iPhone 11","iphone-11",850,1200),("iPhone XS Max","iphone-xs-max",850,1200),
    ("iPhone XS","iphone-xs",850,1180),("iPhone XR","iphone-xr",850,1150),
    ("iPhone X","iphone-x",850,1150),("iPhone 8 Plus","iphone-8-plus",850,1100),
    ("iPhone 8","iphone-8",850,1050),("iPhone 7 Plus","iphone-7-plus",850,1050),
    ("iPhone 7","iphone-7",850,1000),("iPhone SE 3 (2022)","iphone-se-2022",850,1150),
    ("iPhone SE 2 (2020)","iphone-se-2020",850,1100),("iPhone SE (2016)","iphone-se-2016",850,1000),
]
def grn(n): return format(n, ",d").replace(",", " ")   # 1200 -> "1 200"

# ── признаки, что пора менять (карточки) ──
SIGNS = [
    ("battery","Здоровье ниже 80%","В «Настройки → Аккумулятор → Состояние» ёмкость упала ниже 80% — iPhone уже просит замену и снижает производительность."),
    ("clock","Быстро разряжается","Не доживает до вечера, разряжается за пару часов или «прыгает» с 40% сразу на 20% — ёмкость деградировала."),
    ("power","Выключается сам","Отключается на холоде или при заряде 20-30%, хотя показывает ещё есть заряд — классический признак старой батареи."),
    ("shield","Вздулся аккумулятор","Экран приподнимается, появился зазор по краю или качается на столе — менять срочно, вздутие опасно."),
    ("fire","Греется и долго заряжается","Нагревается при зарядке и обычном использовании, заряжается заметно дольше обычного."),
    ("wrench","«Сервис» в состоянии батареи","Система показывает «Важное сообщение об аккумуляторе» или «Сервис» — ресурс исчерпан."),
]

# ── шаги (процесс) ──
STEPS = [
    ("Бесплатная диагностика","Проверяем ёмкость, контроллер питания и разъём — убеждаемся, что дело именно в аккумуляторе, а не в плате.",""),
    ("Согласуем цену и срок","Называем точную стоимость по вашей модели до начала работ. Оплата только по факту — без предоплаты.",""),
    ("Замена при вас","Меняем аккумулятор за 20-30 минут в мастерской. На новые современные модели — с сохранением герметичности.","≈20 мин"),
    ("Проверка и гарантия","Тестируем зарядку и автономность, выдаём гарантию 12 месяцев на аккумулятор и работу.","12 месяцев"),
]

# ── FAQ ──
FAQ = [
    ("Сколько стоит замена аккумулятора на iPhone?","Цена зависит от модели: от 850 ₴ для iPhone 7-11 и SE, 1200-2100 ₴ для iPhone 14-16, до 2600 ₴ для iPhone 17 Pro Max. Точную стоимость по вашей модели смотрите в таблице выше — диагностика бесплатная, итоговую цену называем до начала работ."),
    ("Сколько времени занимает замена батареи?","В среднем 20-30 минут — меняем при вас в мастерской. Если параллельно нужна диагностика платы или чистка разъёма, скажем об этом сразу после проверки."),
    ("Какая гарантия на новый аккумулятор?","12 месяцев — и на сам аккумулятор, и на работу мастера. Если в течение гарантии появятся вопросы к автономности, бесплатно проверим и решим."),
    ("Вы ставите оригинальный аккумулятор или копию?","Используем качественные сервисные аккумуляторы с проверенной ёмкостью. Разницу между оригиналом, сервисным и дешёвым «no-name» АКБ честно объясняем до замены — вы сами выбираете вариант под бюджет."),
    ("Почему после замены не показывается «Состояние аккумулятора»?","Это особенность iOS: на новых iPhone при установке неоригинального аккумулятора система убирает раздел «Состояние» и может показывать уведомление о неоригинальной детали. На работу и автономность это не влияет — телефон работает штатно. Мы предупреждаем об этом заранее."),
    ("Когда пора менять аккумулятор?","Если ёмкость упала ниже 80%, телефон быстро разряжается, выключается на морозе или при 20-30% заряда, греется или аккумулятор вздулся — пора менять. Вздутие опасно, с ним лучше не тянуть."),
    ("Нужно ли записываться заранее?","Не обязательно — можно приехать в рабочие часы, диагностика бесплатная. Но если позвоните или оставите заявку заранее, подготовим аккумулятор под вашу модель, и замена пройдёт быстрее."),
    ("Меняете аккумулятор, если телефон был в воде или падал?","Да, но сначала бесплатная диагностика: после воды или удара причиной быстрого разряда может быть плата или контроллер питания, а не только батарея. Проверим и скажем честно, поможет ли замена."),
]

# ── SEO-абзацы ──
SEO = [
    "Аккумулятор iPhone — расходник: после 500-800 циклов зарядки его ёмкость заметно падает, телефон перестаёт держать заряд и может выключаться при остатке 20-30%. Сервисный центр SPARK в Одессе меняет аккумуляторы на всех моделях iPhone — от iPhone 7 и SE до iPhone 17 Pro Max — за 20-30 минут, с гарантией 12 месяцев и бесплатной диагностикой перед работой.",
    "Перед заменой мы всегда проверяем, действительно ли дело в аккумуляторе: иногда быстрый разряд вызывает не батарея, а контроллер питания, разъём или фоновые процессы после залития. Поэтому диагностика бесплатная и ни к чему не обязывает — если замена не нужна, честно об этом скажем. Точную цену по вашей модели вы видите в таблице выше, а нужную модель можно открыть и посмотреть все виды ремонта.",
    "Работаем в центре Одессы на ул. Академика Королёва, 23 — рядом с Киевским рынком. Оплата по факту, без предоплаты. Приходите с любым iPhone или оставьте заявку — перезвоним за 15 минут, подскажем цену и срок замены аккумулятора.",
]

# связанные ссылки (низ SEO-блока)
RELATED = [
    ("../../remont-iphone/","Ремонт iPhone — все услуги"),
    ("../../diagnostika/","Бесплатная диагностика"),
    ("../../blog/pochemu-bystro-saditsya-batareya/","Почему быстро садится батарея"),
    ("../../blog/iphone-ne-zaryazhaetsya/","iPhone не заряжается: что делать"),
]

FORM_OPTS = ["Замена аккумулятора iPhone", "iPhone быстро разряжается", "Вздулся аккумулятор",
             "iPhone выключается сам", "Другое (опишу в разговоре)"]

def hero_svg():
    # фирменный SVG-герой: телефон + батарея + красная искра (в стиле service-героев)
    grad = D._GRAD % {"p": "bt"}
    return ('<div class="hero-art">\n        '
      '<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Замена аккумулятора iPhone">'
      + grad +
      '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#bts)"/>'
      # корпус батареи
      '<rect x="96" y="70" width="108" height="200" rx="16" fill="none" stroke="#E11D2A" stroke-width="6"/>'
      '<rect x="132" y="56" width="36" height="18" rx="5" fill="#E11D2A"/>'
      # уровень заряда
      '<rect x="110" y="150" width="80" height="106" rx="8" fill="rgba(225,29,42,.85)"/>'
      # молния-искра поверх
      '<polygon points="158,96 118,178 150,178 138,250 192,158 158,158 172,96" fill="#fff"/>'
      + D._check(210, 250, 20) +
      '<text x="150" y="306" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="18" font-weight="700">Новый аккумулятор</text>'
      '<text x="150" y="330" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса · гарантия 12 мес</text>'
      '</svg>\n      </div>')

def build():
    title = "Замена аккумулятора iPhone в Одессе — цена от 850 ₴ | SPARK"
    desc = "Замена аккумулятора iPhone в Одессе за 20-30 минут: цена от 850 ₴, гарантия 12 месяцев, бесплатная диагностика. Все модели — от iPhone 7 до 17 Pro Max. Оплата по факту."
    kw = "замена аккумулятора iphone, замена аккумулятора айфон, замена батареи iphone, замена аккумулятора iphone одесса, поменять аккумулятор айфон одесса"
    h1 = "Замена аккумулятора iPhone в Одессе"
    sub = "Меняем аккумулятор на любом iPhone за 20-30 минут при вас. Бесплатная диагностика, качественные аккумуляторы, гарантия 12 месяцев и оплата по факту — без предоплаты."

    # ── JSON-LD ──
    lo_min = min(m[2] for m in MODELS)
    service = {"@context":"https://schema.org","@type":"Service","@id":CANON+"#service",
        "name":"Замена аккумулятора iPhone в Одессе","serviceType":"Замена аккумулятора iPhone",
        "description":desc,"areaServed":{"@type":"City","name":"Одесса"},
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "offers":{"@type":"Offer","priceCurrency":"UAH","price":str(lo_min),"priceSpecification":{"@type":"PriceSpecification","minPrice":str(lo_min),"priceCurrency":"UAH"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Ремонт iPhone","item":"https://sparkservice.od.ua/remont-iphone/"},
        {"@type":"ListItem","position":3,"name":"Замена аккумулятора","item":CANON}]}
    faqpage = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in (service, crumb, faqpage))

    # ── head ──
    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="%s">\n' % CANON
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("Замена аккумулятора iPhone в Одессе | SPARK"), escA(desc))
    p += '<meta property="og:url" content="%s">\n<meta property="og:locale" content="ru_RU">\n' % CANON
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../../styles.css">\n' + D.STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + NAV2 + '\n'

    # ── breadcrumb (3 уровня) ──
    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../remont-iphone/">Ремонт iPhone</a><span>›</span><span>Замена аккумулятора</span></div>\n  </div>\n\n'

    # ── hero ──
    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">Ремонт iPhone в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(h1), esc(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.9</span> <b>Google</b><span class="sep">·</span>127 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          <span>🔋 <b>от 850 ₴ · ≈20 минут</b></span>\n        </div>\n'
    p += '      </div>\n      ' + hero_svg() + '\n    </div>\n  </section>\n\n'

    # ── признаки ──
    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(ic), esc(t), esc(d)) for ic,t,d in SIGNS)
    p += '  <section class="sec" id="signs">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Когда менять</span>\n        <h2>Признаки, что пора менять аккумулятор</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % cards

    # ── таблица цен по моделям (строки ссылаются на модели) ──
    rows = "\n            ".join(
        '<tr><td class="svc-name"><a href="../../remont-iphone/%s/">Замена аккумулятора %s</a></td><td class="pr">%s ₴</td><td class="time">≈20 мин</td></tr>' % (
            slug, esc(label), grn(lo)+" – "+grn(hi)) for label,slug,lo,hi in MODELS)
    p += ('  <section class="sec sec-bg" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
          '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость замены аккумулятора по моделям</h2>\n'
          '        <p class="lead-p">Цены ориентировочные. Точную стоимость называем после бесплатной диагностики. Нажмите на модель — там все виды ремонта и цены.</p>\n      </div>\n'
          '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Модель</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)

    # ── оригинал/копия (info box) ──
    p += ('  <section class="sec" id="info">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Важно знать</span>\n        <h2>Оригинал, сервисный или копия аккумулятора</h2>\n      </div>\n'
          '      <div class="legal-box reveal" style="border-left-color:var(--spark)"><ul>'
          '<li><span class="ck">✓</span><span><b>Сервисный аккумулятор с проверенной ёмкостью</b> — оптимальный баланс цены и ресурса, наш основной вариант.</span></li>'
          '<li><span class="ck">✓</span><span><b>Честно про разницу.</b> До замены объясняем, чем сервисный АКБ отличается от оригинала и дешёвого «no-name», — выбираете вы.</span></li>'
          '<li><span class="ck">✓</span><span><b>Про «Состояние аккумулятора».</b> На новых iPhone с неоригинальным АКБ iOS убирает раздел «Состояние» и показывает уведомление — на работу это не влияет, предупреждаем заранее.</span></li>'
          '<li><span class="ck">✓</span><span><b>Гарантия 12 месяцев</b> на аккумулятор и работу — при любых вопросах к автономности проверим бесплатно.</span></li>'
          '</ul></div>\n    </div>\n  </section>\n\n')

    # ── процесс ──
    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(t), esc(d), ('<span class="%s">%s</span>' % ("badge w" if "месяц" in b.lower() else "badge", esc(b)) if b else "")) for t,d,b in STEPS)
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">Замена аккумулятора за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % steps

    # ── почему мы (reuse) ──
    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Проверим ёмкость и причину разряда до начала работ — без обязательств.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Гарантия 12 месяцев</h3><p>На аккумулятор и работу мастера. Оплата по факту, без предоплаты.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>За 20-30 минут</h3><p>Меняем аккумулятор при вас — не нужно оставлять телефон надолго.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''

    # ── SEO текст + related ──
    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % esc(x) for x in SEO)
    rel = "\n          ".join('<a href="%s">%s</a>' % (href, esc(t)) for href,t in RELATED)
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">Замена аккумулятора iPhone в Одессе — сервис SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (seops, rel)

    # ── FAQ ──
    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(q), esc(a)) for i,(q,a) in enumerate(FAQ))
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы о замене аккумулятора</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs

    # ── форма ──
    opts = "".join('<option>%s</option>' % esc(o) for o in FORM_OPTS)
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Оставьте номер — назовём цену замены за 15 минут</h2>\n          <p>Бесплатно подскажем стоимость аккумулятора под вашу модель и срок. Или просто позвоните — мастер на связи.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: замена аккумулятора</h3>\n'
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

    p += FOOTER2 + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", "Замена аккумулятора iPhone").replace("{{MODALOPTIONS}}", opts)
    return p

def main():
    outd = os.path.join(REPO, SLUG)
    os.makedirs(outd, exist_ok=True)
    h = build()
    open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
    print("✓ %s/index.html (%d симв., %d моделей, %d FAQ)" % (SLUG, len(h), len(MODELS), len(FAQ)))

if __name__ == "__main__":
    main()
