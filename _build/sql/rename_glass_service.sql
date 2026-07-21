-- ============================================================================
-- Переименование услуги: «Замена стекла (сепарация)» → «Замена стекла (без замены дисплея)»
--
-- Зачем: «сепарация» — мастерский жаргон, поисковый спрос по нему НУЛЕВОЙ
-- (Ahrefs: «сепарация дисплея» = 0/мес). Клиенты ищут «замена стекла»
-- (iphone 40/мес, «на телефоне» 200/мес) и не понимают термин.
--
-- ⚠️ ПОЗИЦИЯ КЛЮЧА СОХРАНЯЕТСЯ. Live-обновление цен на хабе сопоставляет
--    услуги ПО ПОЗИЦИИ, поэтому просто удалить+добавить нельзя — ключ уедет
--    в конец и цены разъедутся по строкам. Здесь объект пересобирается
--    с заменой имени на месте.
--
-- Обновляются ОБА столбца: prices и published_prices.
-- Идемпотентно: если ключа со старым именем нет, строка не трогается.
--
-- Запускать: Supabase → SQL Editor → вставить целиком → Run.
-- ============================================================================

-- 1) Черновик (prices)
update public.model_prices m
set prices = x.new_json
from (
  select mp.id,
         ('{' || string_agg(
             to_json(case when t.key = 'Замена стекла (сепарация)'
                          then 'Замена стекла (без замены дисплея)'
                          else t.key end)::text
             || ':' || t.value::text,
             ',' order by t.ord) || '}')::json as new_json
  from public.model_prices mp,
       json_each(mp.prices) with ordinality as t(key, value, ord)
  where mp.prices::jsonb ? 'Замена стекла (сепарация)'
  group by mp.id
) x
where m.id = x.id;

-- 2) Опубликованный снимок (published_prices) — то, что печётся на сайт
update public.model_prices m
set published_prices = x.new_json
from (
  select mp.id,
         ('{' || string_agg(
             to_json(case when t.key = 'Замена стекла (сепарация)'
                          then 'Замена стекла (без замены дисплея)'
                          else t.key end)::text
             || ':' || t.value::text,
             ',' order by t.ord) || '}')::json as new_json
  from public.model_prices mp,
       json_each(mp.published_prices) with ordinality as t(key, value, ord)
  where mp.published_prices is not null
    and mp.published_prices::jsonb ? 'Замена стекла (сепарация)'
  group by mp.id
) x
where m.id = x.id;

-- 3) Проверка: имя новое, позиция прежняя (2), цена не потерялась
select id,
       label,
       (select ord from json_each(prices) with ordinality as t(k, v, ord)
         where k = 'Замена стекла (без замены дисплея)')            as позиция,
       (prices->'Замена стекла (без замены дисплея)')::text         as цена_черновик,
       (published_prices->'Замена стекла (без замены дисплея)')::text as цена_на_сайте,
       (prices::jsonb ? 'Замена стекла (сепарация)')                as старый_ключ_остался
from public.model_prices
order by sort;

-- Ожидается: позиция = 2, цены совпадают, старый_ключ_остался = false у всех.
