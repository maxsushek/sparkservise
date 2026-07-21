#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
indexnow_ping.py — отправляет URL сайта на переобход через IndexNow.

Кого уведомляет: Bing, Yandex, Seznam, Naver (общий пул IndexNow).
Google протокол НЕ поддерживает — для него отдельно GSC «Запросить индексирование».

Зачем это здесь: Bing питает ChatGPT и Copilot, а по GA4 именно ChatGPT —
канал с лучшей конверсией. Плюс у сайта много страниц ждёт индексации.

Запускать ПОСЛЕ деплоя (URL должны быть уже доступны):
    python3 _build/indexnow_ping.py            # все URL из sitemap.xml
    python3 _build/indexnow_ping.py --changed  # только изменённые в последнем коммите
    python3 _build/indexnow_ping.py --dry      # показать, что отправилось бы

Ключ лежит в _build/indexnow_key.txt, файл-подтверждение — <key>.txt в корне.
"""
import json, os, re, subprocess, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "sparkservice.od.ua"
BASE = f"https://{HOST}"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_PATH = os.path.join(REPO, "_build", "indexnow_key.txt")
BATCH = 10000          # лимит IndexNow на один запрос


def log(m): print(f"[indexnow] {m}")


def load_key():
    if not os.path.exists(KEY_PATH):
        log("нет _build/indexnow_key.txt — сначала сгенерируйте ключ"); return None
    key = open(KEY_PATH, encoding="utf-8").read().strip()
    if not re.fullmatch(r"[a-f0-9]{8,128}", key):
        log(f"ключ некорректен: {key!r}"); return None
    if not os.path.exists(os.path.join(REPO, key + ".txt")):
        log(f"нет файла-подтверждения {key}.txt в корне — IndexNow отклонит запрос"); return None
    return key


def urls_from_sitemap():
    p = os.path.join(REPO, "sitemap.xml")
    if not os.path.exists(p):
        log("нет sitemap.xml"); return []
    return re.findall(r"<loc>(https://[^<]+)</loc>", open(p, encoding="utf-8").read())


def urls_changed():
    """URL страниц, HTML которых изменился в последнем коммите."""
    try:
        out = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                             cwd=REPO, capture_output=True, text=True, timeout=30).stdout
    except Exception as e:
        log(f"git недоступен ({e}) — беру весь sitemap"); return urls_from_sitemap()
    urls = []
    for f in out.splitlines():
        if not f.endswith("index.html"):
            continue
        path = f[:-len("index.html")]
        if path.startswith(("_build/", "admin/")):
            continue
        urls.append(BASE + "/" + path)
    return urls


def submit(key, urls):
    payload = {"host": HOST, "key": key,
               "keyLocation": f"{BASE}/{key}.txt",
               "urlList": urls}
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def main():
    dry = "--dry" in sys.argv
    key = load_key()
    if not key:
        return 0                      # fail-safe: не роняем пайплайн

    urls = urls_changed() if "--changed" in sys.argv else urls_from_sitemap()
    urls = sorted(set(u for u in urls if u.startswith(BASE)))
    if not urls:
        log("нечего отправлять"); return 0

    log(f"URL к отправке: {len(urls)}")
    if dry:
        for u in urls[:10]:
            log(f"  {u}")
        if len(urls) > 10:
            log(f"  … и ещё {len(urls) - 10}")
        return 0

    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        try:
            code = submit(key, chunk)
            # 200 — принято, 202 — принято к обработке (ключ ещё проверяется)
            log(f"отправлено {len(chunk)} URL → HTTP {code}"
                + (" ✓" if code in (200, 202) else " — проверьте ответ"))
        except Exception as e:
            log(f"ошибка отправки ({e}) — не критично, попробуйте позже")
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
