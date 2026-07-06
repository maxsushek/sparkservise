/* SPARK exit-intent popup — компактный: заголовок «Не нашли что искали?» + ОДНО поле телефона
   с «начинкой» основной формы сайта (маска, точки-индикатор, определение оператора).
   Shell/анимация/поведение — как у модалки сайта (.modal / .mf-*). Появляется при попытке уйти.
   Показ: ≥15с И ≥30% прокрутки И exit-intent. Лимиты: 1/сессия · 7 дней после закрытия · никогда после заявки.
   Превью без лимитов: ?popup=1. Классы .js-submit/.js-phone/.js-device → лид ловит analytics.js
   (событие generate_lead в dataLayer). Сам попап шлёт в dataLayer: exit_popup_show (с trigger)
   и exit_popup_close (закрыт без заявки) — воронка настраивается в GTM. */
(function () {
  "use strict";
  if (window.__sparkExit) return;
  window.__sparkExit = 1;

  var lang = (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru";
  var T = {
    ru: {
      badge: "Бесплатная консультация", title: "Не нашли что искали?",
      desc: "Оставьте номер телефона — наш специалист свяжется с вами и бесплатно ответит на вопросы.",
      submit: "Жду звонка", note: "Перезвоним в течение 15 минут. Данные не передаём третьим лицам.",
      trust: ["Бесплатная диагностика", "Гарантия 12 месяцев", "Без предоплаты"],
      hint: "Введите номер мобильного оператора Украины", hintFull: "Введите номер полностью",
      hintErr: "Проверьте код оператора", hintOk: "номер распознан", sumPhone: "Телефон",
      okTitle: "Заявка принята!", okText: "Перезвоним в течение 15 минут в рабочее время.",
      done: "Готово", close: "Закрыть", device: "Обратный звонок (exit popup)"
    },
    uk: {
      badge: "Безкоштовна консультація", title: "Не знайшли те, що шукали?",
      desc: "Залиште номер телефону — наш спеціаліст зв'яжеться з вами й безкоштовно відповість на запитання.",
      submit: "Чекаю на дзвінок", note: "Передзвонимо протягом 15 хвилин. Дані не передаємо третім особам.",
      trust: ["Безкоштовна діагностика", "Гарантія 12 місяців", "Без передоплати"],
      hint: "Введіть номер мобільного оператора України", hintFull: "Введіть номер повністю",
      hintErr: "Перевірте код оператора", hintOk: "номер розпізнано", sumPhone: "Телефон",
      okTitle: "Заявку прийнято!", okText: "Передзвонимо протягом 15 хвилин у робочий час.",
      done: "Готово", close: "Закрити", device: "Зворотний дзвінок (exit popup)"
    }
  }[lang];

  var MIN_MS = 15000, MIN_SCROLL = 0.3, CLOSE_DAYS = 7;
  var K_SEEN = "spark_exit_seen", K_CLOSED = "spark_exit_closed", K_LEAD = "spark_exit_lead";
  var preview = /[?&]popup=1/.test(location.search);          // мгновенный показ без условий
  var test = /[?&](popup|test)=1/.test(location.search);       // тест: события с test_mode, флаги не пишем (синхронно с analytics.js)
  var start = Date.now(), maxScroll = 0, shown = false, armed = false, modal = null, closed = false;

  // событие воронки попапа → dataLayer (GTM подхватит позже; очередь сохраняется)
  function track(ev, extra) {
    try {
      var d = { event: ev, language: lang, test_mode: test };
      if (extra) for (var k in extra) d[k] = extra[k];
      (window.dataLayer = window.dataLayer || []).push(d);
    } catch (e) {}
  }

  function lg(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ls(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function sg(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ss(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }

  function suppressed() {
    if (preview) return false;
    if (lg(K_LEAD)) return true;
    if (sg(K_SEEN)) return true;
    var c = parseInt(lg(K_CLOSED) || "0", 10);
    return c && (Date.now() - c) < CLOSE_DAYS * 864e5;
  }
  function engaged() { return preview || ((Date.now() - start) >= MIN_MS && maxScroll >= MIN_SCROLL); }

  addEventListener("scroll", function () {
    var sh = document.documentElement.scrollHeight;
    if (sh > 0) { var p = (scrollY + innerHeight) / sh; if (p > maxScroll) maxScroll = p; }
  }, { passive: true });

  // --- телефон (идентично основной форме сайта: маска + точки + оператор) ---
  var OPS = [{ n: "Kyivstar", c: ["67", "68", "96", "97", "98", "77"] }, { n: "Vodafone", c: ["50", "66", "95", "99"] }, { n: "lifecell", c: ["63", "73", "93"] }, { n: "оператор", c: ["91", "92", "94"] }];
  function detect(code) { for (var i = 0; i < OPS.length; i++) if (OPS[i].c.indexOf(code) > -1) return OPS[i].n; return null; }
  function rawDigits(v) { var d = v.replace(/\D/g, ""); if (d.indexOf("38") === 0) d = d.slice(2); if (d.length && d[0] !== "0") d = "0" + d; return d.slice(0, 10); }
  function fmt(d) { var o = ""; if (d.length > 0) o = "(" + d.slice(0, 3); if (d.length >= 3) o += ") "; if (d.length > 3) o += d.slice(3, 6); if (d.length > 6) o += "-" + d.slice(6, 8); if (d.length > 8) o += "-" + d.slice(8, 10); return o; }
  function esc(s) { return String(s).replace(/[<>&"]/g, function (c) { return { "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;" }[c]; }); }

  function build() {
    modal = document.createElement("div");
    modal.className = "modal"; modal.id = "spkExitModal"; modal.setAttribute("aria-hidden", "true");
    var trust = T.trust.map(function (t) { return "<span><b>✓</b> " + t + "</span>"; }).join("");
    modal.innerHTML =
      '<div class="modal-overlay" data-spk-close></div>' +
      '<div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="spkExitTitle">' +
        '<button class="modal-x" type="button" aria-label="' + T.close + '" data-spk-close>&times;</button>' +
        '<div class="modal-body">' +
          '<div class="mf-head"><span class="eyebrow">' + T.badge + '</span><h3 id="spkExitTitle">' + T.title + '</h3><p>' + T.desc + '</p></div>' +
          '<div class="mf-field">' +
            '<div class="mf-input"><span class="mf-pre">+38</span><input class="js-phone spk-phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(0__) ___-__-__"><span class="mf-ok">✓</span></div>' +
            '<div class="mf-dots spk-dots" aria-hidden="true"><span><i></i><i></i><i></i></span><span><i></i><i></i><i></i></span><span><i></i><i></i></span><span><i></i><i></i></span></div>' +
            '<div class="mf-hint spk-hint">' + T.hint + '</div>' +
          '</div>' +
          '<input class="js-device" type="hidden" value="' + T.device + '">' +
          '<button class="btn btn-spark mf-submit js-submit spk-submit" type="button" disabled>' + T.submit + '</button>' +
          '<p class="mf-note">' + T.note + '</p>' +
          '<div class="mf-trust">' + trust + '</div>' +
        '</div>' +
        '<div class="modal-success">' +
          '<div class="ms-check"><svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="26" cy="26" r="25" fill="rgba(31,174,90,.10)"/><path d="M15 27l7 7 15-16" stroke="#1FAE5A" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>' +
          '<h3>' + T.okTitle + '</h3><p>' + T.okText + '</p>' +
          '<div class="ms-sum spk-sum"></div>' +
          '<button class="btn btn-line" type="button" data-spk-close>' + T.done + '</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(modal);

    var card = modal.querySelector(".modal-card");
    var phone = modal.querySelector(".spk-phone"), hint = modal.querySelector(".spk-hint");
    var dotsWrap = modal.querySelector(".spk-dots"), dots = dotsWrap.querySelectorAll("i");
    var submit = modal.querySelector(".spk-submit"), summary = modal.querySelector(".spk-sum");
    var valid = false;

    function check() {
      var d = rawDigits(phone.value); phone.value = fmt(d); var box = phone.closest(".mf-input"); valid = false;
      if (d.length === 0) { hint.textContent = T.hint; hint.className = "mf-hint spk-hint"; box.classList.remove("valid", "invalid"); }
      else if (d.length < 10) { hint.textContent = T.hintFull; hint.className = "mf-hint spk-hint"; box.classList.remove("valid", "invalid"); }
      else { var op = detect(d.slice(1, 3)); if (op) { valid = true; hint.innerHTML = '<span class="mf-op">✓ ' + op + "</span> " + T.hintOk; hint.className = "mf-hint spk-hint ok"; box.classList.add("valid"); box.classList.remove("invalid"); } else { hint.textContent = T.hintErr; hint.className = "mf-hint spk-hint err"; box.classList.add("invalid"); box.classList.remove("valid"); } }
      for (var i = 0; i < dots.length; i++) { if (i < d.length) dots[i].classList.add("on"); else dots[i].classList.remove("on"); }
      dotsWrap.classList.remove("valid", "invalid"); if (d.length === 10) dotsWrap.classList.add(valid ? "valid" : "invalid");
      submit.disabled = !valid;
    }
    phone.addEventListener("input", check);
    submit.addEventListener("click", function () {
      if (submit.disabled) return;
      if (!test) ls(K_LEAD, "1");   // analytics.js поймает этот же клик по .js-submit
      summary.innerHTML = "<div><span>" + T.sumPhone + "</span><b>+38 " + esc(phone.value) + "</b></div>";
      card.classList.add("done");
    });
    modal.addEventListener("click", function (e) { if (e.target.closest("[data-spk-close]")) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && modal.classList.contains("open")) close(); });
    return phone;
  }

  function open(trig) {
    if (shown || suppressed()) return;
    shown = true; if (!test) ss(K_SEEN, "1");
    track("exit_popup_show", { trigger: trig || "unknown" });
    var phone = build();
    modal.classList.add("open"); modal.setAttribute("aria-hidden", "false"); document.body.classList.add("modal-open");
    requestAnimationFrame(function () { modal.classList.add("show"); });
    setTimeout(function () { try { phone.focus(); } catch (e) {} }, 360);
  }
  function close() {
    if (!modal || closed) return;   // guard: двойной Escape/клик в окно фейда не задваивает событие
    closed = true;
    var card = modal.querySelector(".modal-card");
    if (!(card && card.classList.contains("done"))) track("exit_popup_close");
    if (!test && !lg(K_LEAD)) ls(K_CLOSED, String(Date.now()));
    modal.classList.remove("show"); modal.setAttribute("aria-hidden", "true"); document.body.classList.remove("modal-open");
    setTimeout(function () { modal.classList.remove("open"); }, 300);
  }

  // --- триггеры ---
  if (preview) { setTimeout(function () { open("preview"); }, 600); return; }

  // ПК: курсор ушёл за верхнюю границу окна (mouseleave надёжнее; mouseout — запасной)
  document.addEventListener("mouseleave", function (e) { if (e.clientY <= 0 && engaged()) open("mouse_top"); });
  document.addEventListener("mouseout", function (e) {
    if (e.clientY <= 0 && !e.relatedTarget && !e.toElement && engaged()) open("mouse_top");
  });

  var touch = matchMedia("(hover:none)").matches || "ontouchstart" in window;
  if (touch) {
    // ловушку «назад» ставим раньше (8с ИЛИ 20% скролла) — так свайп/кнопка «назад» на iOS ловятся надёжнее
    function armReady() { return (Date.now() - start) >= 8000 || maxScroll >= 0.2; }
    function arm() {
      if (armed || shown || suppressed() || !armReady()) return;
      armed = true; try { history.pushState({ spkExit: 1 }, "", location.href); } catch (e) {}
    }
    addEventListener("scroll", arm, { passive: true });
    addEventListener("touchend", arm, { passive: true });
    setTimeout(arm, 8200);
    addEventListener("popstate", function () {
      if (armed && !shown && !suppressed()) { try { history.pushState({ spkExit: 1 }, "", location.href); } catch (e) {} open("back_gesture"); }
    });
    // свернул вкладку / переключился в другое приложение / закрывает — покажем (увидит при возврате)
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden" && engaged() && !shown && !suppressed()) open("tab_hidden");
    });
    var lastY = scrollY, lastT = Date.now();
    addEventListener("scroll", function () {
      var y = scrollY, t = Date.now(), dt = t - lastT;
      if (dt > 0 && (lastY - y) / dt > 1.1 && y < 320 && engaged()) open("scroll_up");
      lastY = y; lastT = t;
    }, { passive: true });
  }
})();
