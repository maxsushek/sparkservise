/* SPARK — отправка заявки в Supabase (таблица leads) прямым fetch в REST.
   Ноль внешних библиотек. anon-ключ ПУБЛИЧНЫЙ (это норма Supabase) — защита на RLS:
   роль anon может только INSERT, читать базу заявок не может.
   ──────────────────────────────────────────────────────────────────────────
   ЗАПОЛНИ 2 значения в CFG своими (Project Settings -> Data API / API Keys):
     url      — Project URL, вида https://<ref>.supabase.co
     anonKey  — публичный "anon"/"publishable" ключ
   Пока стоят плейсхолдеры (REPLACE_) — модуль СПИТ (ничего не шлёт, ноль ошибок).
   ──────────────────────────────────────────────────────────────────────────
   Ловит клик по активной кнопке .js-submit/#mSubmit (кнопка активна только при
   валидной форме). Дедуп: окно 3 сек на кнопку. Антиспам: honeypot + тайм-трап.
   Событие в dataLayer (для GTM) шлёт отдельный analytics.js — тут только запись в БД. */
(function () {
  "use strict";
  var CFG = {
    url: "https://xvqqoyttvfmrjvufkkzm.supabase.co",
    anonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2cXFveXR0dmZtcmp2dWZra3ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MDQwMDgsImV4cCI6MjA5ODk4MDAwOH0.yaUDu6A4ajFSKx7Xn51BEUgMgkpF47HOhRocCYfjpSU"
  };
  function ready(v) { return v && v.indexOf("REPLACE_") !== 0; }
  if (!ready(CFG.url) || !ready(CFG.anonKey)) return; // спит до заполнения

  var loadedAt = Date.now();

  // honeypot: скрытое поле в каждую форму; бот заполнит -> дропаем
  function addHoneypot() {
    var forms = document.querySelectorAll("#spkExitModal, #bookFormInline, .modal-card");
    for (var i = 0; i < forms.length; i++) {
      if (forms[i].querySelector(".spk-hp")) continue;
      var inp = document.createElement("input");
      inp.type = "text"; inp.className = "spk-hp"; inp.tabIndex = -1;
      inp.setAttribute("autocomplete", "off"); inp.setAttribute("aria-hidden", "true");
      inp.style.cssText = "position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none";
      forms[i].appendChild(inp);
    }
  }
  if (document.readyState !== "loading") addHoneypot();
  else document.addEventListener("DOMContentLoaded", addHoneypot);

  function val(box, sel) { var el = box.querySelector(sel); return el ? (el.value || "").trim() : ""; }

  // Источник «первого касания»: UTM-метки + gclid(Google Ads)/fbclid(Meta) + реферер +
  // страница входа. Сохраняется в sessionStorage при ПЕРВОМ заходе -> если человек полистал
  // сайт и отправил заявку на другой странице, метки не теряются. Кладём в utm (jsonb).
  function firstTouch() {
    try {
      var K = "spk_attr", saved = sessionStorage.getItem(K);
      if (saved) return JSON.parse(saved);
      var q = new URLSearchParams(location.search), u = {}, p, v,
          keys = ["source", "medium", "campaign", "term", "content"];
      for (var i = 0; i < keys.length; i++) { v = q.get("utm_" + keys[i]); if (v) u[keys[i]] = v.slice(0, 120); }
      var g = q.get("gclid"), f = q.get("fbclid");
      if (g) u.gclid = g.slice(0, 120);
      if (f) u.fbclid = f.slice(0, 120);
      u.landing = (location.pathname + location.search).slice(0, 300);   // страница входа
      var o = {
        utm: u,
        referrer: (document.referrer || "").slice(0, 300) || null        // откуда пришёл
      };
      sessionStorage.setItem(K, JSON.stringify(o));
      return o;
    } catch (e) { return { utm: null, referrer: (document.referrer || "").slice(0, 300) || null }; }
  }
  firstTouch();   // зафиксировать источник как можно раньше (на первой странице сессии)

  document.addEventListener("click", function (e) {
    var t = e.target;
    var btn = t && t.closest ? t.closest(".js-submit, #mSubmit") : null;
    if (!btn || btn.disabled) return;
    var now = Date.now();
    if (now - (parseInt(btn.getAttribute("data-spk-lead") || "0", 10)) < 3000) return; // дедуп
    btn.setAttribute("data-spk-lead", String(now));

    var box = btn.closest("#spkExitModal, #bookFormInline, .modal-card, form") || document;

    // антиспам: honeypot заполнен ИЛИ отправка <1.5с после загрузки -> тихо выходим
    var hp = box.querySelector(".spk-hp");
    if ((hp && hp.value) || (now - loadedAt) < 1500) return;

    var phone = val(box, ".js-phone") || val(box, "#mPhone");
    if (!phone) return;

    var source = box.id === "spkExitModal" ? "exit_popup"
      : (btn.id === "mSubmit" ? "modal_callback"
      : (box.id === "bookFormInline" ? "inline_form" : "unknown"));

    var attr = firstTouch();
    // устройство/браузер/язык браузера — из текущего клиента (не first-touch), в тот же utm-объект
    var ua = navigator.userAgent || "";
    var u = (attr.utm && typeof attr.utm === "object") ? attr.utm : {};
    u.device = /iPad|Tablet/i.test(ua) ? "Планшет" : (/Mobi|Android|iPhone|iPod/i.test(ua) ? "Мобильный" : "Компьютер");
    u.browser = /Edg\//.test(ua) ? "Edge" : (/OPR\/|Opera/.test(ua) ? "Opera" : (/Chrome\//.test(ua) && !/Chromium/.test(ua) ? "Chrome" : (/Firefox\//.test(ua) ? "Firefox" : (/Version\/[\d.]+.*Safari/.test(ua) ? "Safari" : ""))));
    u.os = /Windows/.test(ua) ? "Windows" : (/Android/.test(ua) ? "Android" : (/iPhone|iPad|iPod/.test(ua) ? "iOS" : (/Mac OS X/.test(ua) ? "macOS" : (/Linux/.test(ua) ? "Linux" : ""))));
    try { if (navigator.language) u.blang = navigator.language.slice(0, 12); } catch (e) {}

    var row = {
      name: (val(box, ".js-name") || val(box, "#mName")) || null,
      phone: phone.slice(0, 32),
      service: (val(box, ".js-device") || val(box, "#mDevice")) || null,
      source: source,
      page_url: location.pathname.slice(0, 500),   // страница, где отправили заявку
      lang: (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru",  // язык версии сайта
      utm: Object.keys(u).length ? u : null,   // источник + gclid/fbclid + landing + устройство/браузер/язык
      referrer: attr.referrer || null
    };

    // fire-and-forget: UI-успех рисует main.js/exit-popup.js; сеть не блокирует
    try {
      fetch(CFG.url.replace(/\/$/, "") + "/rest/v1/leads", {
        method: "POST",
        headers: {
          "apikey": CFG.anonKey,
          "Authorization": "Bearer " + CFG.anonKey,
          "Content-Type": "application/json",
          "Prefer": "return=minimal"   // anon не имеет SELECT -> не просим строку назад
        },
        body: JSON.stringify(row),
        keepalive: true                // долетит, даже если страница закрывается
      })["catch"](function () {});
    } catch (e) {}
  }, true);
})();
