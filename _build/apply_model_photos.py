#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проставляет мини-фото в карточки моделей на iPhone-хабе (remont-iphone/index.html).
Для каждой .mcard: если в папке модели есть <slug>.(webp|jpg|jpeg|png) → <img>, иначе SVG-плейсхолдер.
Идемпотентно. Фото — единый источник: файл в RU-папке модели показывается и на RU, и на UA
(путь на /ua/ чинит i18n_wire). Запускать при добавлении/удалении фото модели, затем make_ua."""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.join(REPO, "remont-iphone", "index.html")
EXT = (".webp", ".jpg", ".jpeg", ".png")
PH = ('<span class="mph"><svg class="ph-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
      'stroke-width="1.4"><rect x="6" y="2" width="12" height="20" rx="2.6"/><path d="M10.5 5h3"/></svg></span>')

def photo_for(slug, name):
    d = os.path.join(REPO, "remont-iphone", slug)
    for e in EXT:
        if os.path.exists(os.path.join(d, slug + e)):
            return ('<span class="mph"><img src="%s/%s%s" alt="Ремонт %s" loading="lazy" decoding="async"></span>'
                    % (slug, slug, e, name))
    return PH

def process_card(card):
    slug = re.search(r'href="([^"]+)"', card).group(1).rstrip("/").split("/")[-1]
    m = re.search(r'<span class="nm">([^<]+)<', card)
    name = m.group(1).strip() if m else slug
    card = re.sub(r'<span class="mph">.*?</span>', "", card, count=1, flags=re.S)   # снять старое фото/плейсхолдер
    card = re.sub(r'(<a class="mcard"[^>]*>)', lambda mm: mm.group(1) + photo_for(slug, name), card, count=1)
    return card

def main():
    t = open(HUB, encoding="utf-8").read()
    cnt = [0]
    def repl(m):
        cnt[0] += 1
        return process_card(m.group(0))
    t = re.sub(r'<a class="mcard".*?</a>', repl, t, flags=re.S)
    open(HUB, "w", encoding="utf-8").write(t)
    photos = t.count('<span class="mph"><img')
    print("карточек: %d | с фото: %d | плейсхолдеров: %d" % (cnt[0], photos, cnt[0] - photos))

if __name__ == "__main__":
    main()
