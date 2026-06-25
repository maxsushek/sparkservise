#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка страниц услуг (разблокировка iPhone, диагностика) из _build/service/<slug>.json.
Переиспользует каркас (NAV/FOOTER/MODAL_JS/helpers) из assemble.py -> единый дизайн."""
import json, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as D

REPO = "/Users/koristuvac/Downloads/sparkservise-git"
BUILD = os.path.join(REPO, "_build", "service")
esc, escA, icon = D.esc, D.escA, D.icon

SERVICES = [("razblokirovka-iphone", "Разблокировка iPhone"), ("diagnostika", "Диагностика"), ("vosstanovlenie-dannyh", "Восстановление данных")]
SLUG_NAMES = {
 "razblokirovka-icloud":"Разблокировка iCloud","razblokirovka-iphone":"Разблокировка iPhone",
 "remont-iphone":"Ремонт iPhone","diagnostika":"Диагностика","kontakty":"Контакты",
 "remont-macbook":"Ремонт MacBook","remont-imac":"Ремонт iMac","remont-ipad":"Ремонт iPad",
 "remont-apple-watch":"Ремонт Apple Watch","remont-airpods":"Ремонт AirPods",
}
ICON_INNER = {
 "lock":'<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>',
 "search":'<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/>',
 "data":'<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
}

def resolve(t):
    t = str(t).strip()
    if t == "home": return "../"
    if t == "remont-iphone-17-pro-max": return "../remont-iphone/iphone-17-pro-max/"
    return "../" + t + "/"
_LINK = re.compile(r"\{\{L:([^|}]+)\|([^}]+)\}\}")
def linkify(s): return _LINK.sub(lambda m: '<a href="%s">%s</a>' % (resolve(m.group(1)), m.group(2).strip()), s)
def rich(t): return linkify(esc(t))

LEGAL_CSS = ('''  .legal-box{background:#fff;border:1px solid var(--line);border-left:4px solid var(--ok);border-radius:var(--r);padding:22px 24px;margin-top:8px}
  .legal-box ul{list-style:none;display:grid;gap:11px}
  .legal-box li{display:flex;gap:10px;font-size:.96rem;color:var(--text);line-height:1.5}
  .legal-box li b{color:var(--ink)}
  .legal-box .ck{color:var(--ok);font-weight:800;flex-shrink:0}
  .freebanner{background:var(--spark-soft);border:1px solid #f3cdd2;border-radius:var(--r-lg);padding:26px;text-align:center;margin-top:8px}
  .freebanner .big{font-size:1.6rem;font-weight:750;color:var(--spark);margin-bottom:6px}
  .freebanner p{color:var(--muted);margin:0;max-width:60ch;margin-left:auto;margin-right:auto}
</style>''')
SERVICE_STYLE = D.STYLE.replace("</style>", LEGAL_CSS)

def hero_service(name, heroIcon):
    inner = ICON_INNER.get(heroIcon, ICON_INNER["lock"])
    svg = ('<svg class="phone" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">' % escA(name)
        + (D._GRAD % {"p": "sv"}) +
        '<rect x="10" y="10" width="280" height="340" rx="26" fill="url(#svs)"/>'
        '<circle cx="150" cy="120" r="52" fill="rgba(225,29,42,.12)"/>'
        '<g fill="none" stroke="#E11D2A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" transform="translate(150 120) scale(3.2) translate(-12 -12)">' + inner + '</g>'
        + D._check(186, 156, 17) +
        '<text x="150" y="220" text-anchor="middle" fill="#fff" font-family="-apple-system,Arial" font-size="18" font-weight="700">%s</text>' % esc(name) +
        '<text x="150" y="246" text-anchor="middle" fill="#878d99" font-family="-apple-system,Arial" font-size="13">SPARK · Одесса</text>'
        '</svg>')
    return '<div class="hero-art">\n        ' + svg + '\n      </div>'

def build(slug, name, c):
    g = lambda k, d="": c.get(k, d) or d
    title = g("title", "%s в Одессе | SPARK" % name)
    desc = g("description"); kw = g("keywords"); ogd = g("ogDescription", desc)
    h1 = g("h1", "%s в Одессе" % name); sub = g("sub"); quickPrice = g("quickPrice", "")
    heroIcon = g("heroIcon", "lock"); diagFree = bool(c.get("diagFree"))
    cases = c.get("cases") or []; info = c.get("infoBox") or {}
    pr = c.get("priceRows") or []; proc = c.get("process") or []
    faq = c.get("faq") or []; seo = c.get("seo") or []
    formOptions = c.get("formOptions") or ["%s — заявка" % name]
    related = c.get("relatedSlugs") or []

    service = {"@context":"https://schema.org","@type":"Service","@id":"https://sparkservice.od.ua/%s/#service"%slug,
        "name":"%s в Одессе"%name,"description":ogd or sub,
        "provider":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","telephone":"+380960755452",
            "address":{"@type":"PostalAddress","streetAddress":"ул. Академика Королёва, 23","addressLocality":"Одесса","addressCountry":"UA"}},
        "areaServed":{"@type":"City","name":"Одесса"},"serviceType":name}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":name,"item":"https://sparkservice.od.ua/%s/"%slug}]}
    blocks = [service, crumb]
    if faq:
        blocks.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":f.get("q",""),"acceptedAnswer":{"@type":"Answer","text":f.get("a","")}} for f in faq]})
    schema_html = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in blocks)

    cards = "\n        ".join('<div class="rtype reveal">\n          <h3><span class="ri">%s</span> %s</h3>\n          <p>%s</p>\n        </div>' % (
        icon(t.get("icon","wrench")), esc(t.get("title","")), rich(t.get("desc",""))) for t in cases)

    infobox = ""
    if info.get("bullets"):
        lis = "".join('<li><span class="ck">✓</span><span>%s</span></li>' % rich(b) for b in info["bullets"])
        infobox = ('  <section class="sec sec-bg" id="info">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
                   '        <span class="sec-tag">%s</span>\n        <h2>%s</h2>\n      </div>\n      <div class="legal-box reveal"><ul>%s</ul></div>\n    </div>\n  </section>\n\n' % (
                   esc("Важно" if not diagFree else "Что вы получите"), esc(info.get("title","")), lis))

    if diagFree:
        price_section = ('  <section class="sec" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
            '        <span class="sec-tag">Стоимость</span>\n        <h2>Сколько стоит диагностика</h2>\n      </div>\n'
            '      <div class="freebanner reveal"><div class="big">Бесплатно</div><p>Находим причину поломки и называем точную цену и срок до начала ремонта — без обязательств. Платите только за ремонт, если согласитесь.</p></div>\n    </div>\n  </section>\n\n')
    elif pr:
        rows = "\n            ".join('<tr><td class="svc-name">%s</td><td class="pr">%s</td><td class="time">%s</td></tr>' % (
            esc(r.get("service","")), esc(D.normprice(r.get("price",""))), esc(r.get("time",""))) for r in pr)
        price_section = ('  <section class="sec sec-bg" id="prices">\n    <div class="wrap">\n      <div class="sec-head reveal">\n'
            '        <span class="sec-tag">Цены</span>\n        <h2>Стоимость услуги</h2>\n        <p class="lead-p">Цены ориентировочные. Точную стоимость назовём после бесплатной проверки по IMEI.</p>\n      </div>\n'
            '      <div class="ptable-wrap reveal"><table class="price-table"><thead><tr><th>Услуга</th><th>Цена</th><th>Срок</th></tr></thead><tbody>\n            %s\n          </tbody></table></div>\n    </div>\n  </section>\n\n' % rows)
    else:
        price_section = ""

    steps = "\n        ".join('<div class="step reveal"><h3>%s</h3><p>%s</p>%s</div>' % (
        esc(s.get("title","")), esc(s.get("desc","")),
        ('<span class="%s">%s</span>' % ("badge w" if "месяц" in (s.get("badge","") or "").lower() else "badge", esc(s.get("badge"))) if s.get("badge") else "")
        ) for s in proc)

    seops = "\n        ".join('<p style="color:var(--muted);font-size:.95rem;line-height:1.7;margin-bottom:14px">%s</p>' % rich(p) for p in seo)
    rel = "\n          ".join('<a href="%s">%s</a>' % (resolve(s), esc(SLUG_NAMES.get(s, s))) for s in related)
    fqs = "\n        ".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
        (" open" if i==0 else ""), esc(f.get("q","")), rich(f.get("a",""))) for i,f in enumerate(faq))
    opts = "".join('<option>%s</option>' % esc(o) for o in formOptions)
    quick_html = ('<span>🔒 <b>%s</b></span>' % esc(quickPrice)) if quickPrice else ""

    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n<meta name="description" content="%s">\n<meta name="keywords" content="%s">\n' % (escA(title), escA(desc), escA(kw))
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="https://sparkservice.od.ua/%s/">\n' % slug
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (escA("%s в Одессе | SPARK"%name), escA(ogd))
    p += '<meta property="og:url" content="https://sparkservice.od.ua/%s/">\n<meta property="og:locale" content="ru_RU">\n' % slug
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += schema_html + '\n\n<link rel="stylesheet" href="../styles.css">\n' + SERVICE_STYLE + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n' + D.NAV + '\n'
    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../">Главная</a><span>›</span><span>%s</span></div>\n  </div>\n\n' % esc(name)
    p += '  <section class="page-hero">\n    <div class="wrap">\n      <div class="page-hero-copy">\n'
    p += '        <span class="eyebrow">%s в Одессе</span>\n        <h1>%s</h1>\n        <p class="sub">%s</p>\n' % (esc(name), esc(h1), rich(sub))
    p += '        <div class="hero-cta">\n          <a class="btn btn-spark" href="#book">Записаться</a>\n          <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>\n        </div>\n'
    p += '        <p class="cta-note">⏱ <b>Перезвоним за 15 минут</b> · бесплатная диагностика</p>\n'
    p += '        <div class="trustbar"><span class="tb-star">★ 4.9</span> <b>Google</b><span class="sep">·</span>127 отзывов<span class="sep">·</span><b>32 000</b> ремонтов<span class="sep">·</span>9 лет</div>\n'
    p += '        <div class="quick">\n          <span>📍 <b>ул. Академика Королёва, 23</b></span>\n          <span>🕐 <b>Пн-Сб 10:00-19:00</b></span>\n          %s\n        </div>\n' % quick_html
    p += '      </div>\n      ' + hero_service(name, heroIcon) + '\n    </div>\n  </section>\n\n'
    p += '  <section class="sec" id="cases">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Услуга</span>\n        <h2>%s</h2>\n      </div>\n      <div class="repair-types">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % (
        esc("Что разблокируем" if not diagFree else "Что диагностируем"), cards)
    p += infobox
    p += price_section
    p += '  <section class="sec sec-ink" id="process">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Как мы работаем</span>\n        <h2 style="color:#fff">%s за 4 шага</h2>\n      </div>\n      <div class="steps">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % (esc(name), steps)
    p += '''  <section class="sec" id="why">
    <div class="wrap">
      <div class="sec-head reveal"><span class="sec-tag">Почему выбирают нас</span><h2>Преимущества SPARK</h2></div>
      <div class="why-grid">
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></div><h3>Бесплатная диагностика</h3><p>Проверим и назовём цену до начала работ — без обязательств.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg></div><h3>Честно и легально</h3><p>Беремся только за прозрачные случаи. Оплата по факту результата.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></div><h3>Быстро</h3><p>Большинство задач решаем в день обращения или за 1-3 дня.</p></div>
        <div class="why reveal"><div class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div><h3>Опытные мастера</h3><p>9 лет на рынке Одессы, более 32 000 решённых обращений.</p></div>
      </div>
    </div>
  </section>\n\n'''
    p += '  <section class="sec sec-bg" id="seo-text">\n    <div class="wrap">\n      <div class="reveal" style="max-width:80ch">\n        <h2 style="font-size:1.3rem;margin-bottom:14px">%s в Одессе — сервисный центр SPARK</h2>\n        %s\n        <p style="margin-top:18px;font-weight:600;color:var(--ink)">Смотрите также:</p>\n        <div class="other-models">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n\n' % (esc(name), seops, rel)
    p += '  <section class="sec" id="faq">\n    <div class="wrap">\n      <div class="sec-head reveal">\n        <span class="sec-tag">Частые вопросы</span>\n        <h2>Вопросы об услуге</h2>\n      </div>\n      <div class="faq reveal">\n        %s\n      </div>\n    </div>\n  </section>\n\n' % fqs
    p += '  <section class="sec sec-ink" id="book">\n    <div class="wrap">\n      <div class="book">\n        <div class="copy reveal">\n          <span class="sec-tag">Заявка</span>\n          <h2>Опишите задачу — перезвоним за 15 минут</h2>\n          <p>Бесплатно подскажем, возможно ли решение, цену и срок. Или просто позвоните — мастер на связи.</p>\n        </div>\n'
    p += '        <div class="form sf reveal" id="bookFormInline">\n          <div class="sf-body">\n            <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b class="js-pct">0%</b></div><div class="mf-progress-track"><i class="js-bar"></i></div></div>\n'
    p += '            <h3 class="sf-title">Заявка: %s</h3>\n' % esc(name)
    p += '''            <div class="mf-field"><label>Ваше имя</label><div class="mf-input"><input class="js-name" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
            <div class="mf-field"><label>Телефон</label>
              <div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
              <div class="mf-dots js-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
              <div class="mf-hint js-hint">Введите номер мобильного оператора Украины</div>
            </div>
            <div class="mf-field"><label>Что нужно</label><div class="mf-input"><select class="js-device" aria-label="Что случилось">''' + opts + '''</select></div></div>
            <button class="btn btn-spark mf-submit js-submit" type="button" disabled>Отправить заявку</button>
            <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных.</p>
            <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Оплата по факту</span><span><b>✓</b> Только легально</span></div>
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
    p += D.FOOTER + "\n" + D.MODAL_JS.replace("Ремонт {{DEVICE}}", esc(name)).replace("{{MODALOPTIONS}}", opts)
    return linkify(p)  # финальный проход: резолвим любые оставшиеся токены {{L:...}}

def main():
    written = []
    for slug, name in SERVICES:
        path = os.path.join(BUILD, slug + ".json")
        if not os.path.exists(path): print("MISSING", slug); continue
        try: c = json.load(open(path, encoding="utf-8"))
        except Exception as e: print("BAD JSON", slug, e); continue
        outd = os.path.join(REPO, slug); os.makedirs(outd, exist_ok=True)
        h = build(slug, name, c)
        open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
        written.append("%s (%d симв., %d случаев, %d цен, %d FAQ)" % (slug, len(h), len(c.get("cases") or []), len(c.get("priceRows") or []), len(c.get("faq") or [])))
    print("=== WRITTEN ===")
    for w in written: print("  ✓", w)

if __name__ == "__main__":
    main()
