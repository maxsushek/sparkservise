/* SPARK exit-intent popup — компактный: заголовок «Не нашли что искали?» + ОДНО поле телефона
   с «начинкой» основной формы сайта (маска, точки-индикатор, определение оператора).
   Shell/анимация/поведение — как у модалки сайта (.modal / .mf-*).

   Триггеры (только реальный уход, CRO-аудит 2026-07-08):
     ПК     — курсор ушёл за верх окна (clientY<=10) + грейс-период 1000мс: вернулся — не показываем.
     Мобайл — «рывок к верху»: непрерывный подъём >=45% высоты экрана со скоростью >=1.2px/мс,
              закончившийся у верха страницы. Защита iOS: rubber-band (y<0), клавиатура (blackout 1с).
   История браузера НЕ трогаем: back-ловушка удалена (политика Google «back button hijacking»,
   enforcement 15.06.2026). visibilitychange удалён (ловил вернувшихся, не уходящих).

   Гейт показа («тихий» пресет): >=40с на странице И (>=60% прокрутки ИЛИ >=1500px вглубь) — для всех триггеров.
   Не показываем: открыта модалка записи / фокус в поле ввода / юзер открывал форму записи в сессии.
   Лимиты: показ -> 14 дней тишины; закрыл -> 30 дней; 2 закрытия -> никогда; заявка (любой формой) -> никогда.
   (Safari ITP режет localStorage до ~7 дней — длинные кулдауны там best-effort.)
   Превью без лимитов: ?popup=1. Классы .js-submit/.js-phone/.js-device -> лид ловит analytics.js.
   Воронка: exit_popup_show {trigger} / exit_popup_close {time_open_ms, fast_close} -> dataLayer
   (+ дублируются в GA4 напрямую через gtag, если счётчик настроен). */
(function () {
  "use strict";
  if (window.__sparkExit) return;
  window.__sparkExit = 1;

  var lang = (document.documentElement.lang || "ru").toLowerCase().indexOf("uk") === 0 ? "uk" : "ru";
  var T = {
    ru: {
      badge: "Бесплатная консультация", title: "Не нашли что искали?",
      desc: "Оставьте номер — мастер перезвонит в течение 15 минут, бесплатно подскажет цену и срок ремонта.",
      submit: "Жду звонка", note: "Позвоним один раз по вашему вопросу. Данные не передаём третьим лицам.",
      trust: ["Бесплатная диагностика", "Гарантия 12 месяцев", "Без предоплаты"],
      hint: "Введите номер мобильного оператора Украины", hintFull: "Введите номер полностью",
      hintErr: "Проверьте код оператора", hintOk: "номер распознан", sumPhone: "Телефон",
      okTitle: "Заявка принята!", okText: "Перезвоним в течение 15 минут в рабочее время.",
      done: "Готово", close: "Закрыть", device: "Обратный звонок (exit popup)"
    },
    uk: {
      badge: "Безкоштовна консультація", title: "Не знайшли те, що шукали?",
      desc: "Залиште номер — майстер передзвонить протягом 15 хвилин, безкоштовно підкаже ціну та термін ремонту.",
      submit: "Чекаю на дзвінок", note: "Зателефонуємо один раз щодо вашого питання. Дані не передаємо третім особам.",
      trust: ["Безкоштовна діагностика", "Гарантія 12 місяців", "Без передоплати"],
      hint: "Введіть номер мобільного оператора України", hintFull: "Введіть номер повністю",
      hintErr: "Перевірте код оператора", hintOk: "номер розпізнано", sumPhone: "Телефон",
      okTitle: "Заявку прийнято!", okText: "Передзвонимо протягом 15 хвилин у робочий час.",
      done: "Готово", close: "Закрити", device: "Зворотний дзвінок (exit popup)"
    }
  }[lang];

  var MIN_MS = 40000, MIN_SCROLL = 0.6, MIN_DEPTH_PX = 1500;      // гейт вовлечённости («тихий» пресет)
  var GRACE_MS = 1000;                                            // ПК: отмена при возврате курсора
  var UP_RUN = 0.45, UP_VEL = 1.2, UP_TOP = 0.5;                  // мобайл: рывок к верху
  var CLOSE_DAYS = 30, SEEN_DAYS = 14, MAX_CLOSES = 2;            // лимиты частоты (gentle-уровень)
  var K_SEEN = "spark_exit_seen", K_SEEN_AT = "spark_exit_seen_at", K_CLOSED = "spark_exit_closed",
      K_CLOSES = "spark_exit_closes", K_LEAD = "spark_exit_lead", K_BOOK = "spark_exit_book";
  var preview = /[?&]popup=1/.test(location.search);          // мгновенный показ без условий
  var test = /[?&](popup|test)=1/.test(location.search);       // тест: события с test_mode, флаги не пишем (синхронно с analytics.js)
  var start = Date.now(), maxScroll = 0, maxY = 0, shown = false, modal = null, closed = false, openedAt = 0;

  // событие воронки попапа → dataLayer (GTM подхватит) + зеркало в GA4 напрямую, если gtag уже настроен
  function track(ev, extra) {
    try {
      var d = { event: ev, language: lang, test_mode: test };
      if (extra) for (var k in extra) d[k] = extra[k];
      (window.dataLayer = window.dataLayer || []).push(d);
      if (!test && typeof window.gtag === "function") {
        var p = { language: lang };
        if (extra) for (var k2 in extra) p[k2] = extra[k2];
        window.gtag("event", ev, p);
      }
    } catch (e) {}
  }

  function lg(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function ls(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function sg(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ss(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }

  function suppressed() {
    if (preview) return false;
    if (lg(K_LEAD)) return true;                                            // заявка была — никогда
    if (parseInt(lg(K_CLOSES) || "0", 10) >= MAX_CLOSES) return true;       // 2 закрытия — никогда
    if (sg(K_SEEN)) return true;                                            // уже показан в этой вкладке
    if (sg(K_BOOK)) return true;                                            // открывал форму записи — сессию не трогаем
    var sa = parseInt(lg(K_SEEN_AT) || "0", 10);
    if (sa && (Date.now() - sa) < SEEN_DAYS * 864e5) return true;           // показ — 14 дней тишины
    var c = parseInt(lg(K_CLOSED) || "0", 10);
    return !!(c && (Date.now() - c) < CLOSE_DAYS * 864e5);                  // закрыл — 30 дней
  }
  function engaged() {
    return preview || ((Date.now() - start) >= MIN_MS && (maxScroll >= MIN_SCROLL || maxY >= MIN_DEPTH_PX));
  }
  // юзер занят конверсией: открыта модалка записи или печатает в поле — не мешаем
  function uiBusy() {
    if (document.body.classList.contains("modal-open")) return true;
    var a = document.activeElement, tn = a && a.tagName;
    return tn === "INPUT" || tn === "TEXTAREA" || tn === "SELECT";
  }

  addEventListener("scroll", function () {
    var sh = document.documentElement.scrollHeight;
    if (sh > 0) { var p = (scrollY + innerHeight) / sh; if (p > maxScroll) maxScroll = p; }
    if (scrollY > maxY) maxY = scrollY;
  }, { passive: true });

  // интент записи: открыл модалку — не показываем до конца сессии; отправил ЛЮБУЮ форму — никогда
  document.addEventListener("click", function (e) {
    if (!e.target || !e.target.closest) return;
    if (e.target.closest('a[href="#book"],[data-book]') && !test) ss(K_BOOK, "1");
    var btn = e.target.closest(".js-submit,#mSubmit");
    if (btn && !btn.disabled && !btn.closest("#spkExitModal") && !test) ls(K_LEAD, "1");
  }, true);

  // --- телефон (идентично основной форме сайта: маска + точки + оператор) ---
  var OPS = [{ n: "Kyivstar", c: ["67", "68", "96", "97", "98", "77"] }, { n: "Vodafone", c: ["50", "66", "95", "99"] }, { n: "lifecell", c: ["63", "73", "93"] }, { n: "оператор", c: ["91", "92", "94"] }];
  function detect(code) { for (var i = 0; i < OPS.length; i++) if (OPS[i].c.indexOf(code) > -1) return OPS[i].n; return null; }
  function rawDigits(v) { var d = v.replace(/\D/g, ""); if (d.indexOf("38") === 0) d = d.slice(2); return d.slice(0, 10); }
  function fmt(d) { var o = ""; if (d.length > 0) o = "(" + d.slice(0, 3); if (d.length >= 3) o += ") "; if (d.length > 3) o += d.slice(3, 6); if (d.length > 6) o += "-" + d.slice(6, 8); if (d.length > 8) o += "-" + d.slice(8, 10); return o; }
  // Маска с сохранением курсора; ведущий «0» только при вводе, не при удалении (иначе код оператора не стереть).
  function isDel(e) { return !!(e && e.inputType && e.inputType.indexOf("delete") === 0); }
  function applyMask(inp, deleting) { var sel = inp.selectionStart; if (sel == null) sel = inp.value.length; var before = inp.value.slice(0, sel).replace(/\D/g, "").length; var raw = inp.value.replace(/\D/g, ""); if (raw.indexOf("38") === 0) { raw = raw.slice(2); before = before > 2 ? before - 2 : 0; } if (!deleting && raw.length && raw.charAt(0) !== "0") { raw = "0" + raw; before++; } raw = raw.slice(0, 10); if (before > raw.length) before = raw.length; inp.value = fmt(raw); var val = inp.value, pos = before <= 0 ? 0 : val.length, seen = 0; if (before > 0) { for (var i = 0; i < val.length; i++) { var c = val.charCodeAt(i); if (c >= 48 && c <= 57) { seen++; if (seen === before) { pos = i + 1; break; } } } } try { inp.setSelectionRange(pos, pos); } catch (_) {} return raw; }
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
      var d = rawDigits(phone.value); var box = phone.closest(".mf-input"); valid = false;
      if (d.length === 0) { hint.textContent = T.hint; hint.className = "mf-hint spk-hint"; box.classList.remove("valid", "invalid"); }
      else if (d.length < 10) { hint.textContent = T.hintFull; hint.className = "mf-hint spk-hint"; box.classList.remove("valid", "invalid"); }
      else { var op = detect(d.slice(1, 3)); if (op) { valid = true; hint.innerHTML = '<span class="mf-op">✓ ' + op + "</span> " + T.hintOk; hint.className = "mf-hint spk-hint ok"; box.classList.add("valid"); box.classList.remove("invalid"); } else { hint.textContent = T.hintErr; hint.className = "mf-hint spk-hint err"; box.classList.add("invalid"); box.classList.remove("valid"); } }
      for (var i = 0; i < dots.length; i++) { if (i < d.length) dots[i].classList.add("on"); else dots[i].classList.remove("on"); }
      dotsWrap.classList.remove("valid", "invalid"); if (d.length === 10) dotsWrap.classList.add(valid ? "valid" : "invalid");
      submit.disabled = !valid;
    }
    phone.addEventListener("input", function (e) { applyMask(phone, isDel(e)); check(); });
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
    if (shown || suppressed() || (!preview && uiBusy())) return;
    shown = true; openedAt = Date.now();
    if (!test) { ss(K_SEEN, "1"); ls(K_SEEN_AT, String(openedAt)); }
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
    if (!(card && card.classList.contains("done"))) {
      var openMs = Date.now() - openedAt;
      track("exit_popup_close", { time_open_ms: openMs, fast_close: openMs < 2000 });
      if (!test) {
        ls(K_CLOSED, String(Date.now()));
        ls(K_CLOSES, String(parseInt(lg(K_CLOSES) || "0", 10) + 1));
      }
    }
    modal.classList.remove("show"); modal.setAttribute("aria-hidden", "true"); document.body.classList.remove("modal-open");
    setTimeout(function () { modal.classList.remove("open"); }, 300);
  }

  // --- триггеры ---
  if (preview) { setTimeout(function () { open("preview"); }, 600); return; }

  var graceT = null, quietUntil = 0;
  addEventListener("pageshow", function (e) {   // возврат из bfcache: не стреляем «отложенным» показом
    if (e.persisted) { if (graceT) { clearTimeout(graceT); graceT = null; } quietUntil = Date.now() + 1000; }
  });

  // hover:none — телефоны/планшеты; ноутбук с тачскрином (hover:hover) остаётся на ПК-триггере
  var touch = matchMedia("(hover: none)").matches;

  if (!touch) {
    // ПК: курсор ушёл за верхнюю границу окна -> грейс 1с; вернулся до истечения -> отмена (лимиты не тратятся)
    document.addEventListener("mouseleave", function (e) {
      if (shown || graceT) return;
      if (e.clientY > 10) return;
      if (!engaged() || suppressed() || uiBusy()) return;
      graceT = setTimeout(function () { graceT = null; open("mouse_top"); }, GRACE_MS);
    });
    document.addEventListener("mouseenter", function () {
      if (graceT) { clearTimeout(graceT); graceT = null; }
    });
  } else {
    // Мобайл: «рывок к верху» — непрерывный подъём >=45% экрана, быстро, финиш у верха страницы,
    // и обязательно после реального свайпа пальцем (touchmove <3с — отсекает якорные переходы,
    // iOS-жест «тап по статус-бару» и программные прокрутки).
    // Один точный триггер вместо back-ловушки (политика Google) и visibilitychange (ловил вернувшихся).
    var upStartY = null, upStartT = 0, lastY = scrollY, lastT = Date.now(), lastTouchMove = 0;
    function resetRun() { upStartY = null; }
    addEventListener("touchmove", function () { lastTouchMove = Date.now(); }, { passive: true });
    addEventListener("focusin", function () { quietUntil = Date.now() + 1000; resetRun(); }, true);   // клавиатура дёргает viewport
    addEventListener("focusout", function () { quietUntil = Date.now() + 1000; resetRun(); }, true);
    addEventListener("resize", function () { quietUntil = Date.now() + 500; resetRun(); });           // URL-бар/поворот
    document.addEventListener("click", function (e) {                                                 // якорный переход = скачок, не уход
      if (e.target && e.target.closest && e.target.closest('a[href*="#"]')) { quietUntil = Date.now() + 1500; resetRun(); }
    }, true);
    addEventListener("scroll", function () {
      var y = scrollY, t = Date.now(), dt = t - lastT, py = lastY;
      lastY = y; lastT = t;
      if (shown || t < quietUntil) { resetRun(); return; }
      if (y < 0) { resetRun(); return; }            // iOS rubber-band
      if (dt > 400) resetRun();                     // пауза — новый жест
      if (y >= py) { resetRun(); return; }          // вниз/на месте — сброс
      if (upStartY === null) { upStartY = py; upStartT = t - Math.min(dt, 400); }
      var dist = upStartY - y, vel = dist / Math.max(t - upStartT, 1);
      if (dist >= innerHeight * UP_RUN && vel >= UP_VEL && y < innerHeight * UP_TOP &&
          (t - lastTouchMove) < 3000 && engaged() && !suppressed() && !uiBusy()) {
        open("scroll_up");
      }
    }, { passive: true });
  }
})();
