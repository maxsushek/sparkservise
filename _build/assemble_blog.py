#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка блога: 3 статьи (/blog/<slug>/) + индекс (/blog/). Каркас фиксирован."""
import json, html, os, re

REPO = "/Users/koristuvac/Downloads/sparkservise-git"
BUILD = os.path.join(REPO, "_build", "blog")

ARTICLES = [
    ("original-ili-kopiya-displeya-iphone", "Дисплеи", "screen", "2026-06-18", "18 июня 2026"),
    ("iphone-upal-v-vodu-chto-delat", "Первая помощь", "water", "2026-06-21", "21 июня 2026"),
    ("pochemu-bystro-saditsya-batareya", "Аккумулятор", "battery", "2026-06-24", "24 июня 2026"),
]
SLUGS = [a[0] for a in ARTICLES]
MODIFIED_ISO = "2026-06-25"
MODIFIED_DISP = "25 июня 2026"

def word_count(a):
    txt = (a.get("lead","") or "") + " " + (a.get("conclusion","") or "")
    for s in (a.get("sections") or []):
        for b in (s.get("blocks") or []):
            txt += " " + (b.get("text","") or "")
            for it in (b.get("items") or []): txt += " " + str(it)
    for f in (a.get("faq") or []):
        txt += " " + f.get("q","") + " " + f.get("a","")
    return len(txt.split())

ICON = {
 "screen": '<rect x="3" y="4" width="18" height="13" rx="1.5"/><path d="M8 21h8M12 17v4"/>',
 "water": '<path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/>',
 "battery": '<rect x="3" y="8" width="16" height="8" rx="2"/><path d="M21 11v2M7 12h6"/>',
}

def esc(s): return html.escape(str(s), quote=False)
def escA(s): return html.escape(str(s), quote=True)

def resolve(target):
    t = str(target).strip()
    if t == "home": return "../../"
    if t == "blog": return "../../blog/"
    if t == "remont-iphone-17-pro-max": return "../../remont-iphone/iphone-17-pro-max/"
    if t in SLUGS: return "../" + t + "/"
    return "../../" + t + "/"

_LINK = re.compile(r"\{\{L:([^|}]+)\|([^}]+)\}\}")
def linkify(escaped_text):
    return _LINK.sub(lambda m: '<a href="%s">%s</a>' % (resolve(m.group(1)), m.group(2).strip()), escaped_text)
def rich(text):  # escape then resolve link tokens
    return linkify(esc(text))

def cover(slug, icon_key, alt):
    inner = ICON.get(icon_key, ICON["screen"])
    svg = ('<svg class="cov" viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s">'
           '<defs><linearGradient id="cb_%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FDECEE"/><stop offset="1" stop-color="#EEF0F4"/></linearGradient></defs>'
           '<rect width="800" height="380" fill="url(#cb_%s)"/>'
           '<circle cx="120" cy="70" r="64" fill="rgba(225,29,42,.05)"/>'
           '<circle cx="690" cy="330" r="96" fill="rgba(225,29,42,.045)"/>'
           '<circle cx="400" cy="180" r="84" fill="#fff"/>'
           '<g fill="none" stroke="#E11D2A" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" transform="translate(400 180) scale(3.6) translate(-12 -12)">%s</g>'
           '<text x="400" y="320" text-anchor="middle" fill="#9aa0ad" font-family="-apple-system,Arial" font-size="20" font-weight="600">SPARK · Блог</text>'
           '</svg>') % (escA(alt), slug, slug, inner)
    return ('<figure class="art-cover">'
            '<img src="cover.webp" alt="%s" width="800" height="380" '
            'onload="var f=this.nextElementSibling;if(f)f.style.display=\'none\'" onerror="this.remove()">'
            '%s</figure>') % (escA(alt), svg)

def inline_figure(alt, caption):
    return ('<figure class="art-fig">'
            '<img src="inline.webp" alt="%s" '
            'onload="var p=this.nextElementSibling;if(p)p.style.display=\'none\'" onerror="this.remove()">'
            '<div class="ph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg> Фото скоро добавим</div>'
            '<figcaption>%s</figcaption></figure>') % (escA(alt), esc(caption))

def render_blocks(blocks):
    out = []
    for b in (blocks or []):
        t = b.get("t")
        if t == "p": out.append("<p>%s</p>" % rich(b.get("text", "")))
        elif t == "h3": out.append("<h3>%s</h3>" % esc(b.get("text", "")))
        elif t == "tip": out.append('<div class="tip">%s</div>' % rich(b.get("text", "")))
        elif t in ("ul", "ol"):
            tag = "ul" if t == "ul" else "ol"
            items = "".join("<li>%s</li>" % rich(i) for i in (b.get("items") or []))
            out.append("<%s>%s</%s>" % (tag, items, tag))
    return "\n        ".join(out)

NAV = '''<div class="topbar">
  <div class="wrap">
    <span class="tb-item tb-hide"><span class="dot"></span> Сегодня работаем · 10:00-19:00</span>
    <span class="right"><span class="lang"><a href="https://sparkservice.od.ua/">UA</a><span>/</span><a class="on" href="#">RU</a></span></span>
  </div>
</div>
<header class="site" id="hdr">
  <div class="wrap nav">
    <a class="brand" href="{{P}}" aria-label="SPARK - сервисный центр Apple в Одессе"><img src="{{P}}logo.png" alt="SPARK - ремонт и сервис техники Apple в Одессе" width="320" height="164" style="height:36px;width:auto"></a>
    <nav class="nav-links" aria-label="Основная навигация">
      <span class="has-drop">
        <a href="{{P}}remont-iphone/" role="button" aria-haspopup="true">Ремонт</a>
        <span class="drop" role="menu">
          <a href="{{P}}remont-iphone/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="2" width="10" height="20" rx="2.5"/></svg> Ремонт iPhone</a>
          <a href="{{P}}remont-macbook/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20l-1.5-2H3.5z"/></svg> Ремонт MacBook</a>
          <a href="{{P}}remont-imac/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="13" rx="1.5"/><path d="M9 20h6"/></svg> Ремонт iMac</a>
          <a href="{{P}}remont-ipad/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="3" width="14" height="18" rx="2"/></svg> Ремонт iPad</a>
          <a href="{{P}}remont-apple-watch/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="6" width="10" height="12" rx="3"/></svg> Ремонт Apple Watch</a>
          <a href="{{P}}remont-airpods/"><svg class="di" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3v10M16 3v10"/></svg> Ремонт AirPods</a>
        </span>
      </span>
      <span class="has-drop">
        <a href="{{P}}razblokirovka-icloud/" role="button" aria-haspopup="true">Услуги</a>
        <span class="drop" role="menu">
          <a href="{{P}}razblokirovka-icloud/">Разблокировка iCloud</a>
          <a href="{{P}}razblokirovka-iphone/">Разблокировка iPhone</a>
          <a href="{{P}}diagnostika/">Диагностика</a>
          <a href="{{P}}vosstanovlenie-dannyh/">Восстановление данных</a>
        </span>
      </span>
      <a href="{{P}}#prices">Цены</a>
      <a href="{{P}}blog/">Блог</a>
      <a href="{{P}}kontakty/">Контакты</a>
    </nav>
    <div class="nav-right">
      <span class="hphone"><a href="tel:+380960755452">+38 (096) 075-54-52</a><small>Пн-Сб 10:00-19:00</small></span>
      <a class="btn btn-spark hcta" href="#book">Записаться</a>
      <button class="burger" id="burger" aria-label="Меню" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>
<nav class="mnav" id="mnav" aria-label="Мобильное меню">
  <p class="grp">Ремонт устройств</p>
  <a href="{{P}}remont-iphone/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="2" width="10" height="20" rx="2.5"/></svg></span> iPhone</a>
  <a href="{{P}}remont-macbook/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="4" y="4" width="16" height="11" rx="1.5"/><path d="M2 19h20l-1.5-2H3.5z"/></svg></span> MacBook</a>
  <a href="{{P}}remont-imac/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="3" y="3" width="18" height="13" rx="1.5"/><path d="M9 20h6"/></svg></span> iMac</a>
  <a href="{{P}}remont-ipad/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="3" width="14" height="18" rx="2"/></svg></span> iPad</a>
  <a href="{{P}}remont-apple-watch/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="7" y="6" width="10" height="12" rx="3"/></svg></span> Apple Watch</a>
  <a href="{{P}}remont-airpods/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M8 3v10M16 3v10"/></svg></span> AirPods</a>
  <p class="grp">Услуги</p>
  <a href="{{P}}razblokirovka-icloud/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 18a4 4 0 010-8 5 5 0 019.6-1.3A3.5 3.5 0 0117.5 18z"/></svg></span> Разблокировка iCloud</a>
  <a href="{{P}}razblokirovka-iphone/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><rect x="5" y="11" width="14" height="9" rx="2"/></svg></span> Разблокировка iPhone</a>
  <a href="{{P}}diagnostika/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></span> Диагностика</a>
  <a href="{{P}}vosstanovlenie-dannyh/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/></svg></span> Восстановление данных</a>
  <p class="grp">Информация</p>
  <a href="{{P}}#prices"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 7v5l9 9 5-5-9-9H3z"/></svg></span> Цены и сроки</a>
  <a href="{{P}}blog/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M6 3h9l3 3v15H6z"/></svg></span> Блог</a>
  <a href="{{P}}kontakty/"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 3s6 7 6 11a6 6 0 11-12 0c0-4 6-11 6-11z"/></svg></span> Контакты</a>
  <a class="cta" href="#book">Записаться</a>
</nav>
'''

FOOTER = '''<footer class="site" id="footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot reveal">
        <a class="brand" href="{{P}}"><img src="{{P}}logo-footer.png" alt="SPARK - сервисный центр Apple в Одессе" width="320" height="164" style="height:40px;width:auto"></a>
        <p>Сервисный центр по ремонту техники Apple в Одессе. Ремонтируем Apple с любовью.</p>
        <div class="soc">
          <a href="https://www.instagram.com/spark__odessa/" rel="nofollow noopener" target="_blank" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41-.56-.22-.96-.48-1.38-.9-.42-.42-.68-.82-.9-1.38-.16-.42-.36-1.06-.41-2.23-.06-1.27-.07-1.65-.07-4.85s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41 1.27-.06 1.65-.07 4.85-.07M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.31-1.46.72-2.13 1.38C1.35 2.68.94 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.31.79.72 1.46 1.38 2.13.67.66 1.34 1.07 2.13 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.31 1.46-.72 2.13-1.38.66-.67 1.07-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91-.31-.79-.72-1.46-1.38-2.13C21.32 1.35 20.65.94 19.86.63 19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0z"/><path d="M12 5.84A6.16 6.16 0 1 0 18.16 12 6.16 6.16 0 0 0 12 5.84M12 16a4 4 0 1 1 4-4 4 4 0 0 1-4 4z"/><circle cx="18.41" cy="5.59" r="1.44"/></svg></a>
          <a href="https://t.me/sparks3m" rel="nofollow noopener" target="_blank" aria-label="Telegram"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.9 4.3l-3.3 15.5c-.2 1.1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.3 13.1l-4.8-1.5c-1-.3-1-1 .2-1.5L20.6 2.9c.9-.3 1.6.2 1.3 1.4z"/></svg></a>
          <a href="https://wa.me/380960755452" rel="nofollow noopener" target="_blank" aria-label="WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 00-8.5 15.2L2 22l4.9-1.3A10 10 0 1012 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.4.6c-.1.2-.3.3-.1.6.1.2.6 1 1.3 1.6.9.8 1.6 1 1.9 1.2.2.1.4.1.5-.1l.6-.8c.2-.2.4-.2.6-.1l1.8.9c.2.1.4.2.5.3.1.3.1.7-.1 1.3z"/></svg></a>
        </div>
      </div>
      <div class="foot reveal"><h3>Ремонт</h3><ul>
        <li><a href="{{P}}remont-iphone/">Ремонт iPhone</a></li>
        <li><a href="{{P}}remont-macbook/">Ремонт MacBook</a></li>
        <li><a href="{{P}}remont-imac/">Ремонт iMac</a></li>
        <li><a href="{{P}}remont-apple-watch/">Ремонт Apple Watch</a></li>
        <li><a href="{{P}}remont-ipad/">Ремонт iPad</a></li>
        <li><a href="{{P}}remont-airpods/">Ремонт AirPods</a></li>
      </ul></div>
      <div class="foot reveal"><h3>Компания</h3><ul>
        <li><a href="{{P}}razblokirovka-icloud/">Разблокировка iCloud</a></li>
        <li><a href="{{P}}razblokirovka-iphone/">Разблокировка iPhone</a></li>
        <li><a href="{{P}}diagnostika/">Диагностика</a></li>
          <li><a href="{{P}}vosstanovlenie-dannyh/">Восстановление данных</a></li>
        <li><a href="{{P}}blog/">Блог</a></li>
        <li><a href="{{P}}o-kompanii/">О компании</a></li>
        <li><a href="{{P}}kontakty/">Контакты</a></li>
      </ul></div>
      <div class="foot reveal"><h3>Контакты</h3>
        <p>ул. Академика Королёва, 23, Одесса<br>Пн-Сб: 10:00-19:00 · Вс: выходной</p>
        <p><a href="{{P}}kontakty/">Как нас найти →</a></p>
      </div>
    </div>
    <div class="copyr"><span>© 2026 SPARK · Сервисный центр Apple в Одессе</span><span>Прототип нового сайта</span></div>
  </div>
</footer>
<div class="callbar">
  <a class="btn btn-line" href="tel:+380960755452">☎ Позвонить</a>
  <a class="btn btn-spark" href="#book">Записаться</a>
</div>
<div class="fab" aria-label="Связаться в мессенджере">
  <a class="tg" href="https://t.me/sparks3m" target="_blank" rel="noopener" aria-label="Telegram"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M21.9 4.3l-3.3 15.5c-.2 1.1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-5 9.1-8.2c.4-.4-.1-.6-.6-.2L6.3 13.1l-4.8-1.5c-1-.3-1-1 .2-1.5L20.6 2.9c.9-.3 1.6.2 1.3 1.4z"/></svg></a>
  <a class="wa" href="https://wa.me/380960755452" target="_blank" rel="noopener" aria-label="WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 00-8.5 15.2L2 22l4.9-1.3A10 10 0 1012 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.4 0 .5l-.4.6c-.1.2-.3.3-.1.6.1.2.6 1 1.3 1.6.9.8 1.6 1 1.9 1.2.2.1.4.1.5-.1l.6-.8c.2-.2.4-.2.6-.1l1.8.9c.2.1.4.2.5.3.1.3.1.7-.1 1.3z"/></svg></a>
</div>
'''

MODAL_JS = '''<div class="modal" id="bookModal" aria-hidden="true">
  <div class="modal-overlay" data-close></div>
  <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="bookTitle">
    <button class="modal-x" type="button" aria-label="Закрыть" data-close>&times;</button>
    <div class="modal-body">
      <div class="mf-progress"><div class="mf-progress-row"><span>Заполнение заявки</span><b id="mPct">0%</b></div><div class="mf-progress-track"><i id="mpBar"></i></div></div>
      <div class="mf-head"><span class="eyebrow">Сервис Apple SPARK</span><h3 id="bookTitle">Оставьте заявку</h3><p>Перезвоним за 15 минут, подскажем цену и срок. Диагностика бесплатная.</p></div>
      <div class="mf-field"><label for="mName">Ваше имя</label><div class="mf-input"><input id="mName" type="text" autocomplete="name" placeholder="Как к вам обращаться"><span class="mf-ok">✓</span></div></div>
      <div class="mf-field"><label for="mPhone">Телефон</label>
        <div class="mf-input"><span class="mf-pre">+38</span><input id="mPhone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>
        <div class="mf-dots" id="mPhoneDots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>
        <div class="mf-hint" id="mPhoneHint">Введите номер мобильного оператора Украины</div>
      </div>
      <div class="mf-field"><label for="mDevice">Что вас интересует</label><div class="mf-input"><select id="mDevice" aria-label="Что случилось">
        <option>Ремонт iPhone</option><option>Ремонт MacBook / iMac</option><option>Ремонт iPad / Apple Watch / AirPods</option><option>Разблокировка iCloud</option><option>Другое</option>
      </select></div></div>
      <button class="btn btn-spark mf-submit" id="mSubmit" type="button" disabled>Отправить заявку</button>
      <p class="mf-note">Нажимая кнопку, вы соглашаетесь на обработку данных. Мы не передаём их третьим лицам.</p>
      <div class="mf-trust"><span><b>✓</b> Бесплатная диагностика</span><span><b>✓</b> Гарантия 12 месяцев</span><span><b>✓</b> Без предоплаты</span></div>
    </div>
    <div class="modal-success">
      <div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
      <h3>Заявка принята!</h3><p>Перезвоним в течение 15 минут в рабочее время.</p>
      <div class="ms-sum" id="msSummary"></div>
      <button class="btn btn-line" type="button" data-close>Готово</button>
    </div>
  </div>
</div>
<script>
  var hdr=document.getElementById('hdr');
  addEventListener('scroll',function(){hdr.style.boxShadow=scrollY>6?'0 6px 20px -14px rgba(0,0,0,.25)':'none'},{passive:true});
  var b=document.getElementById('burger'),m=document.getElementById('mnav');
  b.addEventListener('click',function(){var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){m.classList.remove('open');b.setAttribute('aria-expanded',false)})});
  var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!rm && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  } else { document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in')}); }
  (function(){
    var OPS=[{n:'Kyivstar',c:['67','68','96','97','98','77']},{n:'Vodafone',c:['50','66','95','99']},{n:'lifecell',c:['63','73','93']},{n:'оператор',c:['91','92','94']}];
    function detect(code){for(var i=0;i<OPS.length;i++){if(OPS[i].c.indexOf(code)>-1)return OPS[i].n;}return null;}
    function rawDigits(v){var d=v.replace(/\\D/g,'');if(d.indexOf('38')===0)d=d.slice(2);if(d.length&&d[0]!=='0')d='0'+d;return d.slice(0,10);}
    function fmt(d){var o='';if(d.length>0)o='('+d.slice(0,3);if(d.length>=3)o+=') ';if(d.length>3)o+=d.slice(3,6);if(d.length>6)o+='-'+d.slice(6,8);if(d.length>8)o+='-'+d.slice(8,10);return o;}
    function esc(s){return String(s).replace(/[<>&"]/g,function(c){return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c];});}
    function wireForm(o){
      if(!o.name||!o.phone||!o.submit) return;
      var dots=o.dotsWrap?o.dotsWrap.querySelectorAll('i'):[];var phoneValid=false;
      function checkPhone(){var d=rawDigits(o.phone.value); o.phone.value=fmt(d);var box=o.phone.closest('.mf-input'); phoneValid=false;
        if(d.length===0){o.hint.textContent='Введите номер мобильного оператора Украины';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else if(d.length<10){o.hint.textContent='Введите номер полностью';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else{var op=detect(d.slice(1,3));if(op){phoneValid=true;o.hint.innerHTML='<span class="mf-op">✓ '+op+'</span> номер распознан';o.hint.className='mf-hint js-hint ok';box.classList.add('valid');box.classList.remove('invalid');}else{o.hint.textContent='Проверьте код оператора';o.hint.className='mf-hint js-hint err';box.classList.add('invalid');box.classList.remove('valid');}}
        for(var i=0;i<dots.length;i++){ if(i<d.length) dots[i].classList.add('on'); else dots[i].classList.remove('on'); }
        if(o.dotsWrap){o.dotsWrap.classList.remove('valid','invalid'); if(d.length===10) o.dotsWrap.classList.add(phoneValid?'valid':'invalid');}
        return d;}
      function checkName(){var ok=o.name.value.trim().length>=2;o.name.closest('.mf-input').classList.toggle('valid',ok);return ok;}
      function update(){var nameOk=checkName(); var d=checkPhone();var p=Math.round(((nameOk?1:0)+Math.min(d.length/10,1))/2*100);if(o.bar)o.bar.style.width=p+'%'; if(o.pct)o.pct.textContent=p+'%';o.submit.disabled=!(nameOk&&phoneValid);}
      o.name.addEventListener('input',update);o.phone.addEventListener('input',update);
      o.submit.addEventListener('click',function(){if(o.submit.disabled)return;if(o.summary)o.summary.innerHTML='<div><span>Имя</span><b>'+esc(o.name.value.trim())+'</b></div>'+'<div><span>Телефон</span><b>+38 '+esc(o.phone.value)+'</b></div>'+'<div><span>Запрос</span><b>'+esc(o.dev?o.dev.value:'')+'</b></div>';if(o.bar)o.bar.style.width='100%';o.root.classList.add('done');});
      update();}
    var modal=document.getElementById('bookModal');
    if(modal){var card=modal.querySelector('.modal-card'), nameEl=document.getElementById('mName');
      wireForm({root:card,name:nameEl,phone:document.getElementById('mPhone'),dev:document.getElementById('mDevice'),hint:document.getElementById('mPhoneHint'),bar:document.getElementById('mpBar'),pct:document.getElementById('mPct'),submit:document.getElementById('mSubmit'),dotsWrap:document.getElementById('mPhoneDots'),summary:document.getElementById('msSummary')});
      var lastFocus=null;
      function openM(){lastFocus=document.activeElement;modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.classList.add('modal-open');requestAnimationFrame(function(){modal.classList.add('show');});setTimeout(function(){if(nameEl)nameEl.focus();},360);}
      function closeM(){modal.classList.remove('show');modal.setAttribute('aria-hidden','true');document.body.classList.remove('modal-open');setTimeout(function(){modal.classList.remove('open');card.classList.remove('done');},300);if(lastFocus&&lastFocus.focus)lastFocus.focus();}
      document.addEventListener('click',function(e){var op=e.target.closest('a[href="#book"],[data-book]');if(op){e.preventDefault();openM();return;}if(e.target.closest('[data-close]'))closeM();});
      document.addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('open'))closeM();});}
  })();
  (function(){var bar=document.querySelector('.callbar');if(!bar) return;var hero=document.querySelector('.page-hero,.art');var ticking=false;
    function point(){ return hero ? Math.max(hero.offsetHeight-100, 200) : window.innerHeight*0.8; }
    function check(){ bar.classList.toggle('show', window.scrollY > point()); ticking=false; }
    function onScroll(){ if(!ticking){ ticking=true; requestAnimationFrame(check); } }
    window.addEventListener('scroll', onScroll, {passive:true});window.addEventListener('resize', onScroll, {passive:true});check();})();
</script>
</body>
</html>
'''

ART_CSS = '''<style>
  .bc{padding:14px 0;font-size:.86rem;color:var(--muted)}
  .bc a{color:var(--muted);font-weight:500}.bc a:hover{color:var(--spark)}
  .bc span{margin:0 7px;opacity:.5}
  .art{max-width:760px;margin:0 auto;padding:22px 0 10px}
  .art-cat{display:inline-block;font-size:.76rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--spark);background:var(--spark-soft);padding:5px 12px;border-radius:999px;margin-bottom:14px}
  .art h1{font-size:clamp(1.65rem,4vw,2.35rem);line-height:1.16;font-weight:750;letter-spacing:-.02em;color:var(--ink);margin:0 0 14px}
  .art-meta{display:flex;flex-wrap:wrap;gap:7px 14px;font-size:.88rem;color:var(--muted);align-items:center}
  .art-meta .sep{opacity:.45}
  .art-cover{margin:18px 0 26px;border-radius:var(--r-lg);overflow:hidden;border:1px solid var(--line);background:var(--bg)}
  .art-cover img,.art-cover .cov{display:block;width:100%;height:auto}
  .art-lead{font-size:1.16rem;line-height:1.6;color:#3a3f4a;margin-bottom:24px}
  .toc{background:var(--bg);border:1px solid var(--line);border-radius:var(--r);padding:15px 20px;margin-bottom:28px}
  .toc b{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:8px}
  .toc ol{margin:0;padding-left:18px;display:grid;gap:6px;font-size:.96rem}
  .toc a{color:var(--text);font-weight:500}.toc a:hover{color:var(--spark)}
  .art-body{font-size:1.06rem;line-height:1.78;color:var(--text)}
  .art-body h2{font-size:1.45rem;font-weight:700;letter-spacing:-.01em;color:var(--ink);margin:36px 0 12px;scroll-margin-top:88px}
  .art-body h3{font-size:1.18rem;font-weight:650;color:var(--ink);margin:24px 0 8px}
  .art-body p{margin:0 0 16px}
  .art-body ul,.art-body ol{margin:0 0 18px;padding-left:22px;display:grid;gap:9px}
  .art-body p a,.art-body li a,.art-body .tip a{color:var(--spark);font-weight:550;text-decoration:underline;text-underline-offset:2px}
  .art-cta .btn{color:#fff;text-decoration:none}
  .art-body .tip{background:var(--spark-soft);border-left:3px solid var(--spark);border-radius:0 10px 10px 0;padding:14px 18px;margin:0 0 18px;font-size:.99rem;color:#6a2330}
  .art-cta{background:var(--ink);color:#fff;border-radius:var(--r-lg);padding:28px 24px;margin:32px 0;text-align:center}
  .art-cta h3{color:#fff;font-size:1.32rem;font-weight:700;margin-bottom:8px}
  .art-cta p{color:#c7ccd6;margin-bottom:18px;font-size:1rem}
  .art-rel{margin:30px 0}
  .art-rel b{display:block;font-size:.95rem;font-weight:650;color:var(--ink);margin-bottom:10px}
  .rel-links{display:flex;flex-wrap:wrap;gap:8px}
  .rel-links a{display:inline-flex;padding:8px 14px;border:1px solid var(--line);border-radius:999px;font-size:.9rem;font-weight:500;color:var(--text);background:#fff}
  .rel-links a:hover{border-color:var(--spark);color:var(--spark)}
  .art-faq{margin:30px 0}
  .read-next{border-top:1px solid var(--line);margin-top:36px;padding-top:24px}
  .read-next h2{font-size:1.2rem;font-weight:700;margin-bottom:14px}
  .rn-grid{display:grid;grid-template-columns:1fr;gap:12px}
  @media(min-width:620px){.rn-grid{grid-template-columns:1fr 1fr}}
  .rn-card{display:block;background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;transition:border-color .15s,transform .15s}
  .rn-card:hover{border-color:var(--spark);transform:translateY(-2px)}
  .rn-card .c{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--spark);font-weight:700}
  .rn-card h3{font-size:1rem;font-weight:600;color:var(--ink);margin-top:5px;line-height:1.3}
  .blog-hero{padding:40px 0 8px}
  .blog-hero h1{font-size:clamp(1.8rem,4.4vw,2.6rem);font-weight:750;letter-spacing:-.025em;color:var(--ink);margin-bottom:12px}
  .blog-hero p{font-size:1.08rem;color:var(--muted);max-width:60ch}
  .tldr{background:#fff;border:1px solid var(--line);border-left:4px solid var(--spark);border-radius:0 12px 12px 0;padding:18px 22px;margin:0 0 26px}
  .tldr b{display:block;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;color:var(--spark);margin-bottom:10px}
  .tldr ul{margin:0;padding-left:20px;display:grid;gap:8px}
  .tldr li{font-size:1rem;line-height:1.5;color:var(--text)}
  .art-fig{margin:24px 0;border-radius:var(--r-lg);overflow:hidden;border:1px solid var(--line);background:var(--bg)}
  .art-fig img{display:block;width:100%;height:auto}
  .art-fig .ph{display:flex;align-items:center;justify-content:center;gap:9px;min-height:200px;color:#9aa0ad;font-size:.92rem;font-weight:500}
  .art-fig .ph svg{width:22px;height:22px}
  .art-fig figcaption{font-size:.82rem;color:var(--muted);padding:9px 15px;border-top:1px solid var(--line);background:#fff}
  .art-author{display:flex;align-items:center;gap:13px;background:var(--bg);border:1px solid var(--line);border-radius:var(--r);padding:15px 17px;margin:32px 0}
  .art-author .av{width:44px;height:44px;border-radius:50%;background:var(--spark-soft);color:var(--spark);display:grid;place-items:center;flex-shrink:0}
  .art-author .av svg{width:22px;height:22px}
  .art-author p{margin:0;font-size:.9rem;color:var(--muted);line-height:1.5}
  .art-author b{color:var(--ink);font-weight:600}
  .poll{background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px 22px 20px;margin:34px 0;box-shadow:var(--shadow)}
  .poll-tag{display:inline-block;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--spark);background:var(--spark-soft);padding:4px 11px;border-radius:999px;margin-bottom:11px}
  .poll h3{font-size:1.18rem;font-weight:700;color:var(--ink);margin:0 0 5px}
  .poll-top p{font-size:.9rem;color:var(--muted);margin:0 0 16px;line-height:1.45}
  .poll-opts{display:grid;gap:9px}
  .poll .opt{position:relative;display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;text-align:left;border:1.5px solid var(--line);background:#fff;border-radius:11px;padding:13px 15px;font:inherit;font-size:.96rem;font-weight:600;color:var(--ink);cursor:pointer;overflow:hidden;transition:border-color .15s,transform .1s}
  .poll .opt:hover{border-color:#c9cdd6}
  .poll .opt:active{transform:scale(.99)}
  .poll .opt .bar{position:absolute;left:0;top:0;bottom:0;width:0;background:#EDEFF3;z-index:0;border-radius:0 8px 8px 0;transition:width .7s cubic-bezier(.22,.61,.36,1)}
  .poll .opt.win .bar{background:#E2E5EA}
  .poll .opt.mine .bar{background:rgba(225,29,42,.15)}
  .poll .opt .lbl,.poll .opt .pct{position:relative;z-index:1}
  .poll .opt .pct{font-weight:700;color:#5f6676;font-variant-numeric:tabular-nums;opacity:0;transition:opacity .3s}
  .poll .opt.win .pct{color:var(--spark)}
  .poll .opt.mine{border-color:var(--spark)}
  .poll .opt.mine .lbl::after{content:" ✓";color:var(--spark);font-weight:800}
  .poll.voted .opt{cursor:default}
  .poll.voted .opt .pct{opacity:1}
  .poll-foot{margin-top:14px;font-size:.84rem;color:var(--muted)}
  .poll-foot b{color:var(--ink)}
  .poll-cta{display:none;margin-top:15px;padding-top:15px;border-top:1px solid var(--line);align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
  .poll.voted .poll-cta{display:flex}
  .poll-cta .ct{font-size:.92rem;color:var(--text)}
  .poll-cta .ct b{color:var(--ink)}
  .poll-cta .poll-btn{display:inline-flex;align-items:center;gap:6px;background:linear-gradient(120deg,#E8222C,#BE0E18);color:#fff;font-weight:600;font-size:.92rem;padding:11px 18px;border-radius:10px;white-space:nowrap;text-decoration:none;box-shadow:0 8px 20px -12px rgba(225,29,42,.5)}
  .poll-cta .poll-btn:hover{transform:translateY(-1px)}
</style>'''

POLL_HTML = '''<div class="poll" id="spark-poll">
        <div class="poll-top">
          <span class="poll-tag">Опрос</span>
          <h3>Какая у вас модель iPhone?</h3>
          <p>Проголосуйте — узнайте, что приносят чаще всего, и цену ремонта вашей модели.</p>
        </div>
        <div class="poll-opts" id="pollOpts"></div>
        <div class="poll-foot"><span id="pollFoot">Нажмите свой вариант, чтобы проголосовать</span></div>
        <div class="poll-cta"><span class="ct" id="pollCtaText">Спасибо за голос!</span><a class="poll-btn" id="pollCtaBtn" href="../../remont-iphone/">Ремонт iPhone →</a></div>
      </div>
      <script>
      (function(){
        var OPTS=[
          {k:"16",label:"iPhone 16 / 16 Pro",base:96,svc:"Ремонт iPhone 16"},
          {k:"15",label:"iPhone 15 / 15 Pro",base:138,svc:"Ремонт iPhone 15"},
          {k:"14",label:"iPhone 14 / 14 Pro",base:121,svc:"Ремонт iPhone 14"},
          {k:"13",label:"iPhone 13 / 13 Pro",base:167,svc:"Ремонт iPhone 13"},
          {k:"12",label:"iPhone 12 / 12 Pro",base:104,svc:"Ремонт iPhone 12"},
          {k:"old",label:"iPhone 11, X, SE и старше",base:79,svc:"Ремонт iPhone"}
        ];
        var KEY="spark_poll_iphone_model";
        var counts={}; OPTS.forEach(function(o){counts[o.k]=o.base;});
        var poll=document.getElementById("spark-poll"); if(!poll) return;
        var optsEl=document.getElementById("pollOpts"), foot=document.getElementById("pollFoot");
        var ctatext=document.getElementById("pollCtaText"), ctabtn=document.getElementById("pollCtaBtn");
        var saved=null; try{saved=localStorage.getItem(KEY);}catch(e){}
        OPTS.forEach(function(o){
          var b=document.createElement("button"); b.className="opt"; b.setAttribute("data-k",o.k);
          b.innerHTML='<span class="bar"></span><span class="lbl">'+o.label+'</span><span class="pct"></span>';
          b.addEventListener("click",function(){ if(poll.classList.contains("voted"))return; vote(o.k); });
          optsEl.appendChild(b);
        });
        function total(){var t=0;for(var k in counts)t+=counts[k];return t;}
        function render(mine){
          var t=total(), max=0;
          OPTS.forEach(function(o){ if(counts[o.k]>max)max=counts[o.k]; });
          OPTS.forEach(function(o){
            var el=optsEl.querySelector('[data-k="'+o.k+'"]');
            var pct=Math.round(counts[o.k]/t*100);
            el.querySelector(".bar").style.width=pct+"%";
            el.querySelector(".pct").textContent=pct+"%";
            el.classList.toggle("win",counts[o.k]===max);
            el.classList.toggle("mine",o.k===mine);
          });
          foot.innerHTML='Всего голосов: <b>'+t.toLocaleString("ru-RU")+'</b>';
          var win=OPTS.reduce(function(a,b){return counts[a.k]>=counts[b.k]?a:b;});
          var mineO=null; OPTS.forEach(function(o){if(o.k===mine)mineO=o;}); if(!mineO)mineO=win;
          ctatext.innerHTML='Нужен ремонт вашего iPhone?';
          ctabtn.textContent=mineO.svc+' →';
        }
        function vote(k){
          counts[k]=(counts[k]||0)+1;
          try{localStorage.setItem(KEY,k);}catch(e){}
          poll.classList.add("voted"); render(k);
        }
        if(saved){ poll.classList.add("voted"); render(saved); }
      })();
      </script>'''

def schema_blocks(slug, a, iso, category):
    url = "https://sparkservice.od.ua/blog/%s/" % slug
    img = url + "cover.webp"
    post = {"@context":"https://schema.org","@type":"BlogPosting","@id":url+"#article",
        "mainEntityOfPage":{"@type":"WebPage","@id":url},
        "headline": a.get("title") or a.get("h1"), "description": a.get("metaDescription",""),
        "image": img, "datePublished": iso, "dateModified": MODIFIED_ISO, "wordCount": word_count(a), "inLanguage":"ru-RU",
        "articleSection": category, "keywords": a.get("keywords",""),
        "author":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/","description":"Сервисный центр по ремонту техники Apple в Одессе, 9 лет опыта, 32 000+ ремонтов"},
        "publisher":{"@type":"Organization","name":"SPARK","logo":{"@type":"ImageObject","url":"https://sparkservice.od.ua/og/logo.png"}}}
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Блог","item":"https://sparkservice.od.ua/blog/"},
        {"@type":"ListItem","position":3,"name": a.get("h1") or a.get("title"),"item":url}]}
    faq = a.get("faq") or []
    blocks = [post, crumb]
    if faq:
        blocks.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":f.get("q",""),"acceptedAnswer":{"@type":"Answer","text":f.get("a","")}} for f in faq]})
    ht = a.get("howTo")
    if ht and ht.get("steps"):
        blocks.append({"@context":"https://schema.org","@type":"HowTo","name": ht.get("name") or a.get("h1"),
            "step":[{"@type":"HowToStep","position":i+1,"name":s.get("name",""),"text":s.get("text","")} for i,s in enumerate(ht.get("steps") or [])]})
    return "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in blocks)

def excerpt(a):
    return a.get("metaDescription") or a.get("lead","")[:160]

def build_article(slug, category, icon_key, iso, disp, a, meta):
    sections = a.get("sections") or []
    toc = "".join('<li><a href="#s%d">%s</a></li>' % (i, esc(s.get("h2",""))) for i, s in enumerate(sections))
    body = []
    for i, s in enumerate(sections):
        body.append('<h2 id="s%d">%s</h2>' % (i, esc(s.get("h2",""))))
        body.append(render_blocks(s.get("blocks")))
        if i == 0 and len(sections) >= 3:
            body.append(inline_figure(a.get("coverAlt", a.get("h1","")), a.get("h1","")))
    body_html = "\n        ".join(body)
    tldr = a.get("tldr") or []
    tldr_html = ('<div class="tldr"><b>Коротко</b><ul>%s</ul></div>' %
                 "".join("<li>%s</li>" % esc(t) for t in tldr)) if tldr else ""
    author_html = ('<div class="art-author"><div class="av"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></div>'
        '<p><b>Мастерская SPARK</b> — сервисный центр по ремонту техники Apple в Одессе. 9 лет опыта, более 32 000 отремонтированных устройств. Материал подготовили и проверили наши мастера.<br>Обновлено: %s</p></div>') % MODIFIED_DISP
    faq = a.get("faq") or []
    faq_html = ""
    if faq:
        items = "".join('<details%s><summary>%s</summary><div class="a">%s</div></details>' % (
            (" open" if k==0 else ""), esc(f.get("q","")), rich(f.get("a",""))) for k,f in enumerate(faq))
        faq_html = '<section class="art-faq"><h2>Частые вопросы</h2><div class="faq">%s</div></section>' % items
    cta = a.get("cta") or {}
    cta_html = ""
    if cta:
        cta_html = ('<div class="art-cta"><h3>%s</h3><p>%s</p>'
                    '<a class="btn btn-spark" href="%s">%s</a></div>') % (
            esc(cta.get("title","Нужен ремонт?")), esc(cta.get("text","")),
            resolve(cta.get("target","remont-iphone")), esc(cta.get("button","Узнать цену")))
    rels = a.get("relatedServices") or []
    rel_html = ""
    if rels:
        links = "".join('<a href="%s">%s</a>' % (resolve(r.get("slug","remont-iphone")), esc(r.get("text",""))) for r in rels)
        rel_html = '<div class="art-rel"><b>Связанные услуги</b><div class="rel-links">%s</div></div>' % links
    # read next: other 2 articles
    rn = [x for x in ARTICLES if x[0] != slug]
    rn_cards = ""
    for (s2, cat2, ic2, iso2, disp2) in rn:
        m2 = meta.get(s2, {})
        rn_cards += '<a class="rn-card" href="../%s/"><span class="c">%s</span><h3>%s</h3></a>' % (
            s2, esc(cat2), esc(m2.get("h1") or m2.get("title") or s2))
    read_next = '<section class="read-next"><h2>Читайте также</h2><div class="rn-grid">%s</div></section>' % rn_cards

    title = a.get("title") or ("%s — блог SPARK" % a.get("h1",""))
    desc = a.get("metaDescription","")
    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>%s</title>\n' % escA(title)
    p += '<meta name="description" content="%s">\n' % escA(desc)
    p += '<meta name="keywords" content="%s">\n' % escA(a.get("keywords",""))
    p += '<meta name="robots" content="index, follow">\n'
    p += '<link rel="canonical" href="https://sparkservice.od.ua/blog/%s/">\n' % slug
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="article">\n'
    p += '<meta property="og:title" content="%s">\n' % escA(a.get("h1") or title)
    p += '<meta property="og:description" content="%s">\n' % escA(a.get("ogDescription") or desc)
    p += '<meta property="og:url" content="https://sparkservice.od.ua/blog/%s/">\n' % slug
    p += '<meta property="og:locale" content="ru_RU">\n'
    p += '<meta property="og:image" content="https://sparkservice.od.ua/blog/%s/cover.webp">\n\n' % slug
    p += schema_blocks(slug, a, iso, category) + "\n\n"
    p += '<link rel="stylesheet" href="../../styles.css">\n' + ART_CSS + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n'
    p += NAV.replace("{{P}}", "../../") + "\n"
    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../../">Главная</a><span>›</span><a href="../../blog/">Блог</a><span>›</span><span>%s</span></div>\n  </div>\n' % esc(a.get("h1") or title)
    p += '  <div class="wrap">\n    <article class="art">\n'
    p += '      <div class="art-head">\n        <span class="art-cat">%s</span>\n        <h1>%s</h1>\n' % (esc(category), esc(a.get("h1","")))
    p += '        <div class="art-meta"><span>Мастерская SPARK</span><span class="sep">·</span><time datetime="%s">%s</time><span class="sep">·</span><span>%s чтения</span></div>\n      </div>\n' % (iso, esc(disp), esc(a.get("readingTime","5 мин")))
    p += '      ' + cover(slug, icon_key, a.get("coverAlt", a.get("h1",""))) + '\n'
    p += '      <p class="art-lead">%s</p>\n' % rich(a.get("lead",""))
    if tldr_html:
        p += '      %s\n' % tldr_html
    if toc:
        p += '      <nav class="toc" aria-label="Содержание"><b>Содержание</b><ol>%s</ol></nav>\n' % toc
    p += '      <div class="art-body">\n        %s\n' % body_html
    if a.get("conclusion"):
        p += '        <h2 id="итог">Коротко о главном</h2>\n        <p>%s</p>\n' % rich(a.get("conclusion"))
    p += '        %s\n      </div>\n' % cta_html
    p += '      ' + POLL_HTML + '\n'
    p += '      %s\n      %s\n      %s\n      %s\n' % (faq_html, rel_html, author_html, read_next)
    p += '    </article>\n  </div>\n</main>\n\n'
    p += FOOTER.replace("{{P}}", "../../") + "\n"
    p += MODAL_JS
    return p

def build_index(meta):
    cards = ""
    for (slug, category, icon_key, iso, disp) in ARTICLES:
        a = meta.get(slug, {})
        cards += ('<a class="blogc reveal" href="%s/">\n'
                  '          <span class="ph"><span class="cat">%s</span></span>\n'
                  '          <span class="bd"><h3>%s</h3><p>%s</p><span class="more">Читать <span class="ar">→</span></span></span>\n'
                  '        </a>\n        ') % (slug, esc(category), esc(a.get("h1") or a.get("title") or slug), esc(excerpt(a)))
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Главная","item":"https://sparkservice.od.ua/"},
        {"@type":"ListItem","position":2,"name":"Блог","item":"https://sparkservice.od.ua/blog/"}]}
    blog = {"@context":"https://schema.org","@type":"Blog","@id":"https://sparkservice.od.ua/blog/#blog",
        "name":"Блог SPARK","url":"https://sparkservice.od.ua/blog/","inLanguage":"ru-RU",
        "publisher":{"@type":"Organization","name":"SPARK","url":"https://sparkservice.od.ua/"}}
    sc = "\n".join('<script type="application/ld+json">\n'+json.dumps(x, ensure_ascii=False)+'\n</script>' for x in [blog, crumb])
    p = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    p += '<title>Блог SPARK — статьи о ремонте техники Apple в Одессе</title>\n'
    p += '<meta name="description" content="Полезные статьи сервисного центра SPARK: ремонт iPhone, замена дисплея и батареи, что делать если телефон упал в воду. Экспертные советы от мастеров Apple в Одессе.">\n'
    p += '<meta name="keywords" content="блог ремонт apple, советы по ремонту iphone, замена дисплея, iphone упал в воду, замена батареи, SPARK Одесса">\n'
    p += '<meta name="robots" content="index, follow">\n<link rel="canonical" href="https://sparkservice.od.ua/blog/">\n'
    p += '<meta name="theme-color" content="#ffffff">\n<meta property="og:type" content="website">\n'
    p += '<meta property="og:title" content="Блог SPARK — статьи о ремонте техники Apple">\n'
    p += '<meta property="og:description" content="Экспертные советы по ремонту iPhone и техники Apple от мастеров SPARK в Одессе.">\n'
    p += '<meta property="og:url" content="https://sparkservice.od.ua/blog/">\n<meta property="og:locale" content="ru_RU">\n'
    p += '<meta property="og:image" content="https://sparkservice.od.ua/og/spark.jpg">\n\n'
    p += sc + "\n\n"
    p += '<link rel="stylesheet" href="../styles.css">\n' + ART_CSS + '\n</head>\n<body>\n'
    p += '<a class="skip" href="#main">Перейти к содержимому</a>\n\n'
    p += NAV.replace("{{P}}", "../") + "\n"
    p += '<main id="main">\n  <div class="wrap">\n    <div class="bc" aria-label="Хлебные крошки"><a href="../">Главная</a><span>›</span><span>Блог</span></div>\n  </div>\n'
    p += '  <section class="blog-hero"><div class="wrap"><h1>Блог SPARK</h1><p>Экспертные статьи и советы о ремонте техники Apple: как продлить жизнь устройству, что делать в нештатной ситуации и как не переплатить за ремонт.</p></div></section>\n'
    p += '  <section class="sec"><div class="wrap">\n      <div class="blog-grid">\n        %s</div>\n    </div>\n  </section>\n</main>\n\n' % cards
    p += FOOTER.replace("{{P}}", "../") + "\n"
    p += MODAL_JS
    return p

def main():
    meta = {}
    for (slug, category, icon_key, iso, disp) in ARTICLES:
        path = os.path.join(BUILD, slug + ".json")
        if os.path.exists(path):
            try: meta[slug] = json.load(open(path, encoding="utf-8"))
            except Exception as e: print("BAD JSON", slug, e); meta[slug] = {}
        else:
            print("MISSING", slug); meta[slug] = {}
    written = []
    for (slug, category, icon_key, iso, disp) in ARTICLES:
        a = meta.get(slug, {})
        if not a: print("SKIP (no content):", slug); continue
        outd = os.path.join(REPO, "blog", slug); os.makedirs(outd, exist_ok=True)
        h = build_article(slug, category, icon_key, iso, disp, a, meta)
        open(os.path.join(outd, "index.html"), "w", encoding="utf-8").write(h)
        written.append("blog/%s (%d симв., %d секц., %d FAQ)" % (slug, len(h), len(a.get("sections") or []), len(a.get("faq") or [])))
    # index
    os.makedirs(os.path.join(REPO, "blog"), exist_ok=True)
    idx = build_index(meta)
    open(os.path.join(REPO, "blog", "index.html"), "w", encoding="utf-8").write(idx)
    written.append("blog/ (индекс, %d симв.)" % len(idx))
    print("=== WRITTEN ===")
    for w in written: print("  ✓", w)

if __name__ == "__main__":
    main()
