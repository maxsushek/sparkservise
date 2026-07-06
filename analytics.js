/* SPARK — слой данных для GTM (только dataLayer.push, прямых тегов нет).
   ──────────────────────────────────────────────────────────────────────────
   Все рекламные теги вешаются ПОЗЖЕ в Google Tag Manager. Этот файл лишь
   складывает события в window.dataLayer (GTM обработает и те, что легли до
   его загрузки — очередь сохраняется).

   СОБЫТИЯ:
     generate_lead      — валидная отправка ЛЮБОЙ формы (кнопки неактивны до
                          валидности → клик по активной = валидный лид).
       form_id          — exit_popup | modal_callback | inline_form
       service          — что чинит (значение поля устройства/услуги)
       language         — ru | uk
       event_id         — уникальный id лида (дедуп Meta Pixel ↔ Conversions API)
       test_mode        — true при ?popup=1 / ?test=1 (исключай триггером в GTM)
       user_data        — данные для РАСШИРЕННЫХ КОНВЕРСИЙ:
                            .phone_number      E.164 ("+380XXXXXXXXX")
                            .address.first_name имя (если форма его собирает)
     exit_popup_show    — показ exit-попапа (параметр trigger: mouse_top |
                          back_gesture | tab_hidden | scroll_up | preview)
     exit_popup_close   — попап закрыт БЕЗ заявки (для воронки popup CR)
                          (оба события шлёт exit-popup.js)

   НАСТРОЙКА В GTM (когда появятся ID):
     1. Триггер «Специальное событие: generate_lead» (+ условие test_mode ≠ true).
     2. Google Ads Conversion Tracking → включить Enhanced Conversions →
        переменная «Данные, предоставленные пользователем» → тип «Код» →
        вернуть {{DLV - user_data}} (Data Layer Variable, имя: user_data).
     3. Meta Pixel → событие Lead, advanced matching: ph из user_data.phone_number
        (без «+»), fn из user_data.address.first_name; eventID = {{DLV - event_id}}.
     4. Для воронки попапа: GA4-события по exit_popup_show / exit_popup_close.

   ДЕДУП: окно 3 сек на кнопку (data-spk-t) — двойные/тройные клики схлопываются
   в 1 событие, но ПОВТОРНАЯ легитимная заявка позже (модалка переиспользуемая)
   учитывается. Слушатель один на весь документ (все 3 формы) → задвоение невозможно.
   ────────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";
  window.dataLayer = window.dataLayer || [];

  var TEST = /[?&](popup|test)=1/.test(location.search);
  var lang = (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru";
  var seq = 0;
  function uid() { return "spk-" + Date.now().toString(36) + "-" + (++seq) + "-" + Math.floor(Math.random() * 1e9).toString(36); }

  // нормализация украинского телефона → 9-значный абонентский номер (без 0)
  function natPhone(v) {
    var d = (v || "").replace(/\D/g, "");
    if (d.indexOf("380") === 0) d = d.slice(3);
    else if (d.indexOf("38") === 0) d = d.slice(2);
    if (d.indexOf("0") === 0) d = d.slice(1);
    return d.length === 9 ? d : "";
  }

  // ── generate_lead: успешная отправка формы ──
  // capture-фаза: сработает даже если другой обработчик остановит всплытие
  document.addEventListener("click", function (e) {
    var t = e.target;
    var btn = t && t.closest ? t.closest(".js-submit, #mSubmit") : null;
    if (!btn || btn.disabled) return;
    // дедуп: 3-сек окно на кнопку (не вечный флаг — модалка допускает повторную заявку)
    var now = Date.now();
    if (now - (parseInt(btn.getAttribute("data-spk-t") || "0", 10)) < 3000) return;
    btn.setAttribute("data-spk-t", String(now));

    // контейнер формы — значения берём ТОЛЬКО из него (не тянем чужие поля)
    var box = btn.closest("#spkExitModal, #bookFormInline, .modal-card, form") || document;
    function val(sel) { var el = box.querySelector(sel); return el ? (el.value || "").trim() : ""; }

    var form_id = btn.closest("#spkExitModal") ? "exit_popup"
      : btn.id === "mSubmit" ? "modal_callback"
      : btn.closest("#bookFormInline") ? "inline_form" : "form";

    var name = val(".js-name") || val("#mName");
    var service = val(".js-device") || val("#mDevice");
    var nat = natPhone(val(".js-phone") || val("#mPhone"));

    var ud = {};
    if (nat) ud.phone_number = "+380" + nat;
    if (name) ud.address = { first_name: name };

    var ev = {
      event: "generate_lead",
      event_id: uid(),
      form_id: form_id,
      language: lang,
      test_mode: TEST,
      user_data: ud
    };
    if (service) ev.service = service;
    window.dataLayer.push(ev);
  }, true);
})();
