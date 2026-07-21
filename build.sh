#!/usr/bin/env bash
#
# build.sh — полная детерминированная пересборка сайта SPARK.
# Порядок выведен из зависимостей скриптов (докстринги _build/*.py).
#
# Использование:
#   bash build.sh                 # обычная пересборка
#   BUILD_SKIP_PULL=1 bash build.sh   # не тянуть цены из Supabase (только локальные)
#
# В Vercel:  Build Command = bash build.sh   (Output Directory = .)
# pull_prices — fail-safe: нет БД/сети → сборка идёт на ценах из коммита.

set -euo pipefail
cd "$(dirname "$0")"

PY=python3
$PY --version

step () { echo ""; echo "▶ $*"; }

# 1) Единый источник цен: Supabase → var TIERS (fail-safe, может ничего не менять)
if [ "${BUILD_SKIP_PULL:-0}" != "1" ]; then
  step "pull_prices — Supabase → var TIERS"
  $PY _build/pull_prices.py
fi

# 2) Хабы устройств (iPad/MacBook/iMac/Watch/AirPods; iPhone-хаб не трогается)
step "assemble — хабы устройств";           $PY _build/assemble.py
# 3) Spoke-страницы моделей iPhone из TIERS
step "assemble_model — модели iPhone";       $PY _build/assemble_model.py
# 4) Посадочная «Замена аккумулятора»
step "assemble_battery — АКБ";               $PY _build/assemble_battery.py
# 4.1) Посадочная «Замена стекла Apple Watch» (нет контент-json → шаг пропускается)
step "assemble_watch_glass — стекло Watch";  $PY _build/assemble_watch_glass.py
# 5) Страницы услуг (разблокировка, диагностика, восстановление)
step "assemble_service — услуги";            $PY _build/assemble_service.py
# 6) Блог
step "assemble_blog — блог";                 $PY _build/assemble_blog.py
# 7) Под-модели не-iPhone устройств
step "assemble_device_model — устройства";   $PY _build/assemble_device_model.py
# 8) Мини-фото моделей в iPhone-хаб (до make_ua)
step "apply_model_photos — фото моделей";    $PY _build/apply_model_photos.py
# 9) Калькулятор на главной (main.js) ← TIERS
step "sync_calc — калькулятор главной";      $PY _build/sync_calc.py

# 10) UA-страницы из RU по каталогу переводов.
#     make_ua внутри сам зовёт i18n_wire. Он ВОЗВРАЩАЕТ 1 как ПРЕДУПРЕЖДЕНИЕ
#     о непереведённых сегментах (не фатально). Отличаем предупреждение от
#     реального падения: после запуска должно существовать ≥60 UA-страниц.
step "make_ua — украинские страницы (+ i18n_wire внутри)"
$PY _build/make_ua.py || echo "  make_ua: предупреждения (непереведённые сегменты) — это не ошибка, продолжаю"
UA_PAGES=$(find ua -name index.html 2>/dev/null | wc -l | tr -d ' ')
if [ "$UA_PAGES" -lt 60 ]; then
  echo "✖ make_ua собрал лишь $UA_PAGES UA-страниц (<60) — это уже реальный сбой. Стоп."; exit 1
fi
echo "  UA-страниц на месте: $UA_PAGES"
# 11) Подстраховка обвязки (идемпотентно; make_ua её уже вызвал)
step "i18n_wire — hreflang/canonical (подстраховка)";  $PY _build/i18n_wire.py || true
# 12) Активный пункт меню (после i18n_wire — нужны финальные пути)
step "mark_current_nav — активное меню";     $PY _build/mark_current_nav.py

# 12.5) Server-render прайса хаба: запекаем строки в <tbody id="priceBody"> (RU+UA),
#       чтобы цены были в HTML для краулеров. После make_ua (UA-хаб уже собран).
step "prerender_hub_prices — прайс хаба в HTML"; $PY _build/prerender_hub_prices.py

# 12.6) Рейтинг Google → во все страницы (из _build/google_rating.json).
#       Значения обновляет еженедельный GitHub Action (.github/workflows/google-rating.yml).
#       Ключ в Vercel НЕ задаём — иначе платный запрос уйдёт на каждой сборке.
if [ -n "${GOOGLE_PLACES_API_KEY:-}" ]; then
  step "fetch_google_rating — рейтинг из Places API"; $PY _build/fetch_google_rating.py || true
fi
step "apply_rating — рейтинг по страницам";  $PY _build/apply_rating.py

# 13-16) Инъекции в <head> и финальная оптимизация
step "inject_favicon — фавикон";             $PY _build/inject_favicon.py
step "inject_analytics — analytics.js";      $PY _build/inject_analytics.py
step "set_og_host — хост og:image";          $PY _build/set_og_host.py
step "inline_css — инлайн CSS главной";      $PY _build/inline_css.py

# 17) lastmod в sitemap по git (только если репозиторий на месте)
if [ -d .git ]; then
  step "sync_sitemap_dates — даты sitemap";  $PY _build/sync_sitemap_dates.py || true
fi

echo ""
echo "✅ build.sh завершён"
