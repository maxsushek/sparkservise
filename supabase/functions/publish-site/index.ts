// SPARK — Edge Function «publish-site»
// Кнопка «Опубликовать» в админке зовёт эту функцию → она дёргает Vercel Deploy Hook,
// который запускает пересборку сайта (bash build.sh → pull_prices → регенерация → deploy).
//
// Развёртывание (владелец, один раз):
//   1) Vercel → Project Settings → Git → Deploy Hooks → создать хук (ветка main),
//      скопировать URL вида https://api.vercel.com/v1/integrations/deploy/prj_.../...
//   2) Задать секрет Supabase:
//        supabase secrets set VERCEL_DEPLOY_HOOK_URL="https://api.vercel.com/v1/integrations/deploy/..."
//      (или через Dashboard → Edge Functions → Secrets)
//   3) Задеплоить функцию:
//        supabase functions deploy publish-site
//
// SUPABASE_URL / SUPABASE_ANON_KEY / SUPABASE_SERVICE_ROLE_KEY подставляются автоматически.

import { createClient } from "jsr:@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const json = (obj: unknown, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { ...CORS, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "method_not_allowed" }, 405);

  const url = Deno.env.get("SUPABASE_URL")!;
  const anon = Deno.env.get("SUPABASE_ANON_KEY")!;

  try {
    // 1) Проверяем, что зовёт именно админ (по его JWT, с уважением RLS).
    const authHeader = req.headers.get("Authorization") || "";
    const asUser = createClient(url, anon, { global: { headers: { Authorization: authHeader } } });
    const { data: isAdmin, error: adminErr } = await asUser.rpc("is_admin");
    if (adminErr || !isAdmin) return json({ error: "not_admin" }, 403);

    // 2) Триггерим пересборку через Vercel Deploy Hook.
    const hook = Deno.env.get("VERCEL_DEPLOY_HOOK_URL");
    if (!hook) return json({ ok: false, error: "no_hook_configured", hint: "Задайте секрет VERCEL_DEPLOY_HOOK_URL" }, 503);

    const resp = await fetch(hook, { method: "POST" });
    const text = await resp.text();
    if (!resp.ok) return json({ ok: false, error: "hook_failed", status: resp.status, vercel: text.slice(0, 500) }, 502);

    // 3) Только ПОСЛЕ принятого хука повышаем черновик до опубликованного одним
    //    атомарным стейтментом (RPC). Сборка стартует через ~десятки секунд —
    //    к тому моменту published_prices уже = prices, и build их и запечёт.
    //    Если стамп не удался — честно возвращаем snapshot:false, чтобы админка
    //    НЕ показывала ложное «Опубликовано» и доверяла состоянию БД.
    const service = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!service) return json({ ok: true, snapshot: false, warn: "no_service_key", message: "Пересборка запущена" }, 200);
    const { error: stampErr } = await createClient(url, service).rpc("promote_prices");
    if (stampErr) return json({ ok: true, snapshot: false, warn: "stamp_failed", detail: stampErr.message, message: "Пересборка запущена" }, 200);

    return json({ ok: true, snapshot: true, message: "Пересборка запущена, снимок обновлён" }, 200);
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
