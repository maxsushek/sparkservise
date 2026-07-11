#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pull_prices.py — тянет цены из Supabase (таблица model_prices) и переписывает
единый источник цен `var TIERS=[...]` в remont-iphone/index.html.

Запускается ПЕРВЫМ в build.sh, до assemble_model / assemble_battery / sync_calc.

Fail-safe by design:
  • нет сети / нет ключа / пустой ответ / любая ошибка → файл НЕ трогаем, exit 0.
    Сборка продолжается на ценах, уже зашитых в коммит. Сломать сайт нельзя.

Локальный тест без живой БД:
  PULL_PRICES_FIXTURE=/path/to/mp_fixture.json python3 _build/pull_prices.py
"""
import os, re, json, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB  = os.path.join(ROOT, "remont-iphone", "index.html")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xvqqoyttvfmrjvufkkzm.supabase.co")
# anon-ключ достаточно: чтение model_prices публичное (цены и так на сайте).
ANON_KEY = os.environ.get(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2cXFveXR0dmZtcmp2dWZra3ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MDQwMDgsImV4cCI6MjA5ODk4MDAwOH0.yaUDu6A4ajFSKx7Xn51BEUgMgkpF47HOhRocCYfjpSU",
)


def log(msg):
    print(f"[pull_prices] {msg}")


def fetch_rows():
    """Возвращает список строк model_prices (или бросает исключение)."""
    fixture = os.environ.get("PULL_PRICES_FIXTURE")
    if fixture:
        log(f"фикстура: {fixture}")
        with open(fixture, encoding="utf-8") as f:
            return json.load(f)
    url = f"{SUPABASE_URL}/rest/v1/model_prices?select=id,sort,label,time_text,prices&order=sort.asc"
    req = urllib.request.Request(url, headers={
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def js_prices(prices: dict) -> str:
    """{'Услуга':[lo,hi],...} → JS-литерал в формате TIERS (порядок ключей сохранён)."""
    parts = []
    for svc, pair in prices.items():
        lo, hi = int(pair[0]), int(pair[1])
        parts.append(f"'{svc}':[{lo},{hi}]")
    return "{" + ",".join(parts) + "}"


def build_tiers_block(rows) -> str:
    lines = ["  var TIERS=["]
    body = []
    for r in rows:
        rid   = r["id"]
        label = r["label"]
        tm    = r.get("time_text") or "30-60 мин"
        pr    = r["prices"]
        if isinstance(pr, str):            # json-текст из REST на всякий
            pr = json.loads(pr)
        body.append(
            f"    {{id:'{rid}',label:'{label}',"
            f"prices:{js_prices(pr)},time:'{tm}'}}"
        )
    lines.append(",\n".join(body))
    lines.append("  ];")
    return "\n".join(lines)


def validate(rows) -> bool:
    if not rows or not isinstance(rows, list):
        log("пустой ответ — пропускаю")
        return False
    if len(rows) < 20:
        log(f"подозрительно мало моделей ({len(rows)}) — пропускаю ради безопасности")
        return False
    for r in rows:
        if not r.get("id") or not r.get("label") or not r.get("prices"):
            log(f"строка без id/label/prices ({r.get('id')}) — пропускаю")
            return False
        for svc, pair in r["prices"].items() if isinstance(r["prices"], dict) else []:
            if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                    or not all(isinstance(x, int) and x > 0 for x in pair)):
                log(f"кривая цена {r['id']} / {svc}: {pair} — пропускаю")
                return False
    return True


def main():
    try:
        rows = fetch_rows()
    except Exception as e:
        log(f"не смог получить цены ({e}) — оставляю коммит как есть. OK.")
        return 0

    if not validate(rows):
        return 0

    src = open(HUB, encoding="utf-8").read()
    m = re.search(r"  var TIERS=\[.*?\n  \];", src, re.S)
    if not m:
        log("не нашёл блок var TIERS в hub — пропускаю")
        return 0

    new_block = build_tiers_block(rows)
    if m.group(0) == new_block:
        log(f"цены совпадают с коммитом ({len(rows)} моделей) — правки не нужны.")
        return 0

    out = src[:m.start()] + new_block + src[m.end():]

    # sanity: результат должен парситься тем же регэкспом, что и assemble_model
    check = re.search(r"var TIERS=\[(.*?)\];", out, re.S).group(1)
    n = len(re.findall(r"\{id:'([^']+)',label:'([^']+)',prices:\{([^}]*)\},time:'([^']+)'\}", check))
    if n != len(rows):
        log(f"после сборки распознано {n}/{len(rows)} моделей — НЕ пишу (защита).")
        return 0

    open(HUB, "w", encoding="utf-8").write(out)
    log(f"var TIERS обновлён из Supabase: {len(rows)} моделей ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
