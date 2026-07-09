#!/usr/bin/env python3
# set_og_host.py — временный пост-процессор: переписывает ХОСТ только у og:image и
# twitter:image на LIVE_HOST (туда, где файлы РЕАЛЬНО отдаются сейчас).
#
# Зачем: canonical/og:url по стратегии указывают на будущий домен sparkservice.od.ua,
# но домен пока отдаёт СТАРЫЙ сайт (Tilda) — картинки og там 404, и Telegram/соцсети
# не могут отрисовать превью. Пути og:image идентичны на обоих хостах (GH Pages
# отдаёт репозиторий по /sparkservise/), поэтому достаточно подменить хост.
#
# ⚠ ВРЕМЕННО. После переезда домена на GitHub Pages:
#   - файлы og:image начнут отдаваться уже с sparkservice.od.ua (HTTP 200),
#   - этот шаг больше не нужен → выставить LIVE_HOST = CANON_HOST (станет no-op)
#     или убрать вызов из пайплайна.
# Идемпотентно. Запускать ПОСЛЕ make_ua / inject_analytics / inline_css.
import os, re, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON_HOST = "https://sparkservice.od.ua"          # что стоит в canonical/og:url (будущий домен)
LIVE_HOST = "https://sparkservice.od.ua"           # домен переехал на Vercel — og:image на канонический домен

# только og:image и twitter:image; canonical/og:url НЕ трогаем.
# Хост-агностично: нормализуем С ЛЮБОГО хоста на LIVE_HOST + СТРИПИМ project-префикс /sparkservise
# (GH Pages отдавал репо под /sparkservise/; на Vercel/домене файлы в корне). Реальные пути og
# начинаются с /og, /blog, /remont-... — с /sparkservise никогда, поэтому стрип безопасен.
PATTERNS = [
    re.compile(r'(<meta\s+property="og:image"\s+content=")https?://[^/"]+(?:/sparkservise)?(/[^"]*")'),
    re.compile(r'(<meta\s+name="twitter:image"\s+content=")https?://[^/"]+(?:/sparkservise)?(/[^"]*")'),
]

def process(f):
    t = open(f, encoding="utf-8").read()
    orig = t
    for pat in PATTERNS:
        t = pat.sub(lambda m: m.group(1) + LIVE_HOST + m.group(2), t)
    if t != orig:
        open(f, "w", encoding="utf-8").write(t)
        return True
    return False

def main():
    # После переезда домена: выставить LIVE_HOST = CANON_HOST — скрипт нормализует og:image
    # с vercel.app обратно на домен (HTTP 200 уже с домена). Раннего return больше нет — всегда чиним.
    n = tot = 0
    for f in glob.glob(os.path.join(REPO, "**", "index.html"), recursive=True):
        if "_build" in f:
            continue
        tot += 1
        if process(f):
            n += 1
    print("og:image/twitter:image хост -> LIVE: %d из %d страниц" % (n, tot))

if __name__ == "__main__":
    main()
