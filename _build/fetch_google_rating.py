#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_google_rating.py — тянет рейтинг и число отзывов из Google Places API
и кладёт их в _build/google_rating.json. Оттуда их разносит apply_rating.py.

Зачем: цифры отзывов раньше были зашиты в 5 генераторов и вручную свёрстанные
файлы, из-за чего устаревали (было 4.9/127 при реальных 4.8/158 — завышенный
рейтинг в review-разметке это риск санкций от Google и Bing).

Ходим в Places API (New) — legacy-версия закрыта для проектов, созданных после
марта 2025, ключ там просто получит REQUEST_DENIED. Fallback на legacy оставлен
для старых проектов, у которых он ещё включён.

Что нужно (переменные окружения, ключ в репозиторий не коммитим):
    GOOGLE_PLACES_API_KEY  — ключ Google Cloud с включённым Places API (New)
    GOOGLE_PLACE_ID        — идентификатор точки (ChIJ...). Не задан — найдём
                             по названию и координатам и подскажем в логе.

Запуск:
    GOOGLE_PLACES_API_KEY=... python3 _build/fetch_google_rating.py
    GOOGLE_PLACES_API_KEY=... python3 _build/fetch_google_rating.py --find-place-id

Fail-safe: нет ключа / ошибка сети / подозрительный ответ → json НЕ трогаем,
сборка идёт на прежних значениях. Сломать сайт нельзя.

Стоимость: поле rating относится к самому дорогому SKU, порядка $0.02 за запрос.
Дёргать на каждой сборке смысла нет — рейтинг меняется раз в недели, а сборок
под сотню в месяц. Поэтому запрос вынесен в еженедельный GitHub Action
(.github/workflows/google-rating.yml), который коммитит json; сборка его просто
читает. Выходит 4 запроса в месяц вместо 150.
"""
import json, os, sys, urllib.error, urllib.parse, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "_build", "google_rating.json")

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
PLACE_ID = os.environ.get("GOOGLE_PLACE_ID", "").strip()

# Ориентиры точки из кода сайта (для поиска place_id, если он не задан)
BIZ_NAME = "SPARK сервисный центр Apple Одесса"
BIZ_LAT, BIZ_LNG = 46.4035605, 30.7226524


def log(m): print(f"[google_rating] {m}")


def req(url, headers, data=None):
    r = urllib.request.Request(url, data=data, headers=headers,
                               method="POST" if data else "GET")
    with urllib.request.urlopen(r, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def err_body(e):
    try: return e.read().decode("utf-8")[:300]
    except Exception: return str(e)


# ── Places API (New) ──────────────────────────────────────────────────────────

def find_place_id_new():
    """Text Search (New): ищем точку по названию рядом с известными координатами."""
    body = json.dumps({
        "textQuery": BIZ_NAME,
        "locationBias": {"circle": {
            "center": {"latitude": BIZ_LAT, "longitude": BIZ_LNG}, "radius": 1000.0}},
        "maxResultCount": 3,
    }).encode("utf-8")
    d = req("https://places.googleapis.com/v1/places:searchText",
            {"Content-Type": "application/json", "X-Goog-Api-Key": API_KEY,
             "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress"},
            body)
    places = d.get("places") or []
    if not places:
        log("точка не найдена через Text Search (New)"); return None
    for p in places:
        log(f"найдено: {(p.get('displayName') or {}).get('text')} — {p.get('formattedAddress')}")
        log(f"  place_id: {p.get('id')}")
    return places[0].get("id")


def fetch_new(place_id):
    """Place Details (New). Возвращает (rating, total, name) либо None."""
    d = req(f"https://places.googleapis.com/v1/places/{urllib.parse.quote(place_id)}",
            {"X-Goog-Api-Key": API_KEY,
             "X-Goog-FieldMask": "rating,userRatingCount,displayName"})
    return (d.get("rating"), d.get("userRatingCount"),
            (d.get("displayName") or {}).get("text"))


# ── legacy Places API (только для старых проектов) ────────────────────────────

def fetch_legacy(place_id):
    q = urllib.parse.urlencode({
        "place_id": place_id, "fields": "rating,user_ratings_total,name",
        "language": "ru", "key": API_KEY})
    d = req("https://maps.googleapis.com/maps/api/place/details/json?" + q, {})
    if d.get("status") != "OK":
        log(f"legacy API вернул status={d.get('status')} {d.get('error_message','')}")
        return None
    r = d.get("result") or {}
    return r.get("rating"), r.get("user_ratings_total"), r.get("name")


def fetch(place_id):
    """Сначала New API, при отказе — legacy."""
    try:
        return fetch_new(place_id)
    except urllib.error.HTTPError as e:
        log(f"Places API (New) отказал ({e.code}): {err_body(e)}")
        log("пробую legacy Places API…")
    try:
        return fetch_legacy(place_id)
    except Exception as e:
        log(f"legacy тоже не ответил ({e})"); return None


def main():
    if not API_KEY:
        log("нет GOOGLE_PLACES_API_KEY — оставляю прежние значения. OK.")
        return 0

    if "--find-place-id" in sys.argv:
        try: find_place_id_new()
        except Exception as e: log(f"ошибка поиска: {err_body(e)}")
        return 0

    pid = PLACE_ID
    if not pid:
        try: pid = find_place_id_new()
        except Exception as e: log(f"ошибка поиска place_id: {err_body(e)}"); return 0
    if not pid:
        log("не определён place_id — оставляю прежние значения"); return 0

    got = fetch(pid)
    if not got:
        log("данные не получены — оставляю прежние значения"); return 0
    rating, total, name = got

    # ── защита от мусора: не даём испортить сайт кривым ответом ──
    if not isinstance(rating, (int, float)) or not (1.0 <= rating <= 5.0):
        log(f"подозрительный рейтинг {rating} — пропускаю"); return 0
    if not isinstance(total, int) or total < 1:
        log(f"подозрительное число отзывов {total} — пропускаю"); return 0

    prev = {}
    if os.path.exists(OUT):
        try: prev = json.load(open(OUT, encoding="utf-8"))
        except Exception: pass
    # число отзывов не должно резко падать — почти всегда это сбой на стороне API
    if prev.get("reviews") and total < prev["reviews"] * 0.8:
        log(f"число отзывов упало {prev['reviews']} → {total} (>20%) — пропускаю ради безопасности")
        return 0

    data = {"rating": f"{rating:.1f}", "reviews": total, "source": "Google Places API",
            "place_id": pid, "place_name": name}
    if prev.get("rating") == data["rating"] and prev.get("reviews") == data["reviews"]:
        log(f"без изменений: {data['rating']} ★ / {data['reviews']} отзывов")
        return 0

    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"обновлено: {prev.get('rating','?')}/{prev.get('reviews','?')} → "
        f"{data['rating']} ★ / {data['reviews']} отзывов ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
