/* SPARK — конверсии Google Ads + Meta Pixel.
   ──────────────────────────────────────────────────────────────────────────
   ЗАПОЛНИ 3 значения в CFG ниже своими ID и закоммить — трекинг включится сам.
   Пока стоят плейсхолды (XXXX) — всё ВЫКЛЮЧЕНО (ничего не грузится, ноль ошибок).
   Где взять:
     googleAdsId  — Google Ads → Цели/Конверсии → тег: "AW-XXXXXXXXX"
     googleLabel  — там же у конкретной конверсии "Отправка формы": часть ПОСЛЕ "/"
                    (send_to выглядит как AW-123456789/AbCdEfGh123)
     metaPixelId  — Meta Events Manager → Data sources → Pixel ID (число 15-16 цифр)
   Расширенные конверсии: дополнительно ВКЛЮЧИ их в Google Ads (Конверсии → Настройки →
   Расширенные конверсии → через тег Google) и Advanced Matching в Meta Events Manager.
   ────────────────────────────────────────────────────────────────────────── */
(function () {
  var CFG = {
    googleAdsId: "AW-XXXXXXXXX",          // Google Ads conversion ID
    googleLabel: "XXXXXXXXXXXXXXXXXXXX",   // Google Ads conversion label (после "/")
    metaPixelId: "XXXXXXXXXXXXXXX",        // Meta Pixel ID
    value: 0,                              // ценность лида (0 — без ценности)
    currency: "UAH"
  };

  function set(v) { return v && !/X{4,}/.test(String(v)); }
  var GADS = set(CFG.googleAdsId), FB = set(CFG.metaPixelId);

  // ── Google Ads (gtag.js) + Enhanced Conversions ──
  if (GADS) {
    var g = document.createElement("script");
    g.async = true;
    g.src = "https://www.googletagmanager.com/gtag/js?id=" + CFG.googleAdsId;
    document.head.appendChild(g);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date());
    gtag("config", CFG.googleAdsId, { allow_enhanced_conversions: true });
  }

  // ── Meta Pixel ──
  if (FB) {
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    fbq("init", CFG.metaPixelId);
    fbq("track", "PageView");
  }

  // ── нормализация украинского телефона → 9-значный абонентский номер ──
  function natPhone(v) {
    var d = (v || "").replace(/\D/g, "");
    if (d.indexOf("380") === 0) d = d.slice(3);
    else if (d.indexOf("38") === 0) d = d.slice(2);
    if (d.indexOf("0") === 0) d = d.slice(1);
    return d.length === 9 ? d : "";
  }

  // ── Lead на успешной отправке формы ──
  // Кнопка отправки disabled, пока форма невалидна → клик по активной = валидный лид.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".js-submit, #mSubmit");
    if (!btn || btn.disabled || btn.dataset.spkFired) return;
    btn.dataset.spkFired = "1";

    var box = btn.closest(".sf, .modal-card, .modal-body, form") || document;
    function val(sel) { var el = box.querySelector(sel) || document.querySelector(sel); return el ? (el.value || "").trim() : ""; }
    var name = val(".js-name") || val("#mName");
    var service = val(".js-device") || val("#mDevice");
    var nat = natPhone(val(".js-phone") || val("#mPhone"));
    var e164 = nat ? "+380" + nat : "";

    if (GADS && window.gtag) {
      var ud = {};
      if (e164) ud.phone_number = e164;
      if (name) ud.address = { first_name: name };
      if (Object.keys(ud).length) gtag("set", "user_data", ud);
      gtag("event", "conversion", {
        send_to: CFG.googleAdsId + "/" + CFG.googleLabel,
        value: CFG.value, currency: CFG.currency
      });
    }
    if (FB && window.fbq) {
      var am = {};
      if (nat) am.ph = "380" + nat;
      if (name) am.fn = name.toLowerCase();
      if (am.ph || am.fn) { try { fbq("init", CFG.metaPixelId, am); } catch (_) {} }
      fbq("track", "Lead", { content_name: service, value: CFG.value, currency: CFG.currency });
    }
  }, true);
})();
