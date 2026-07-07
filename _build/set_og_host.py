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
CANON_HOST = "https://sparkservice.od.ua"          # что стоит в тегах (будущий домен)
LIVE_HOST = "https://maxsushek.github.io/sparkservise"  # где файлы отдаются сейчас

# только og:image и twitter:image; canonical/og:url НЕ трогаем
PATTERNS = [
    re.compile(r'(<meta\s+property="og:image"\s+content=")' + re.escape(CANON_HOST) + r'(/[^"]*")'),
    re.compile(r'(<meta\s+name="twitter:image"\s+content=")' + re.escape(CANON_HOST) + r'(/[^"]*")'),
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
    if LIVE_HOST == CANON_HOST:
        print("set_og_host: LIVE_HOST == CANON_HOST — нечего делать (домен переехал)")
        return
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
