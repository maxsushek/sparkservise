# Управление ценами из админки — настройка

Владелец правит цены во вкладке **«Цены»** админки (`/admin/`). Модель работы:

```
Правишь цены  →  «Сохранить черновик»  →  «Опубликовать на сайт»  →  цены на сайте (через 1–2 мин)
                 (запись в Supabase)        (пересборка статики)
```

- **Черновик** — сохранено в базе, но сайт ещё отдаёт старые цены. Виден жёлтый баннер «N изменений не на сайте».
- **Опубликовано** — сайт пересобран, клиенты видят новые цены. Баннер зелёный.
- **Сломать сайт правкой цены нельзя:** при пустых/битых данных сборка (`build.sh` → `pull_prices.py`) оставляет прежние цены из последнего коммита.

---

## Что уже сделано в коде

| Файл | Назначение |
|---|---|
| `admin/index.html` | Вкладка «Цены»: грид модели, поиск, single/диапазон, черновик/публикация, валидация, клавиатура, мобайл |
| `_build/sql/model_prices_setup.sql` | Таблица `model_prices` + RLS + GRANT + снимок `published_prices` |
| `_build/pull_prices.py` | На сборке тянет цены из Supabase → переписывает `var TIERS` (fail-safe) |
| `build.sh` | Полная пересборка сайта в правильном порядке |
| `supabase/functions/publish-site/index.ts` | Кнопка «Опубликовать» → проверяет админа → дёргает пересборку Vercel |

---

## Настройка (владелец, разово)

### Шаг 1 — База (Supabase → SQL Editor)
Если ещё не запускал весь `_build/sql/model_prices_setup.sql` — запусти его целиком.
Если таблица уже создана, добери недостающее:

```sql
-- доступ к таблице
grant select on public.model_prices to anon, authenticated;
grant insert, update, delete on public.model_prices to authenticated;

-- снимок «что сейчас на сайте» (для индикатора «неопубликовано» и модалки-diff)
alter table public.model_prices
  add column if not exists published_prices json,
  add column if not exists published_at    timestamptz;
update public.model_prices set published_prices = prices where published_prices is null;
```

После этого вкладка «Цены» полностью рабочая: **правка → Сохранить черновик** уже работает.
(Кнопка «Опубликовать» до Шагов 2–4 честно скажет «публикацию пока выполняет разработчик».)

### Шаг 2 — Vercel Deploy Hook
Vercel → проект сайта → **Settings → Git → Deploy Hooks** → создать хук на ветку `main`.
Скопировать URL вида `https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy`.

### Шаг 3 — Секрет + Edge Function (Supabase)
```bash
supabase secrets set VERCEL_DEPLOY_HOOK_URL="https://api.vercel.com/v1/integrations/deploy/prj_xxx/yyy"
supabase functions deploy publish-site
```
(`SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` Supabase подставляет сам.)

### Шаг 4 — Сборка при пересборке (Vercel)
Vercel → проект → **Settings → Build & Development**:
- **Build Command:** `bash build.sh`
- **Output Directory:** `.` (корень)
- Framework Preset: **Other**

> ⚠️ Сначала проверь на **Preview**-деплое: сделай тестовую правку цены → «Опубликовать» → дождись сборки → открой превью-URL и убедись, что цена изменилась. Только потом полагайся на Production. Если сборка упадёт — прежний прод остаётся живым (Vercel не публикует неудачный билд).

---

## Как это работает под капотом
1. «Сохранить черновик» пишет `model_prices.prices` (+ `updated_at`) в Supabase.
2. «Опубликовать» → `publish-site` проверяет `is_admin()`, дёргает Deploy Hook, стампует `published_prices = prices`.
3. Vercel запускает `bash build.sh` → `pull_prices.py` читает `model_prices` (anon, read-only) и переписывает `var TIERS` в `remont-iphone/index.html` → пайплайн регенерит 37 страниц моделей + страницу АКБ + калькулятор на главной → деплой.
4. Порядок услуг сохраняется сквозь весь путь (тип колонки `json`, не `jsonb`). Набор/порядок/имена услуг из UI менять нельзя — это защищает порядок прайса и SEO.

## Расширение (Phase 3)
Тот же движок (черновик → снимок → баннер → diff → публикация) переиспользуется для текстов/FAQ страниц: добавляются как новые вкладки/типы ячеек на том же dirty-трекинге и той же кнопке публикации. Структурные операции (набор/порядок услуг, slug, разметка) остаются на стороне разработчика.
