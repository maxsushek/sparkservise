  /* ====== Lightweight, runs immediately (header/nav/reveal/callbar/modal) ====== */
  var hdr=document.getElementById('hdr');
  addEventListener('scroll',function(){hdr.style.boxShadow=scrollY>6?'0 6px 20px -14px rgba(0,0,0,.25)':'none'},{passive:true});
  var b=document.getElementById('burger'),m=document.getElementById('mnav');
  b.addEventListener('click',function(){var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o)});
  m.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){m.classList.remove('open');b.setAttribute('aria-expanded',false)})});
  var rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(!rm && 'IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
  } else { document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in')}); }

  /* ---- Sticky call bar: threshold cached, recomputed only on resize (no per-frame layout read) ---- */
  (function(){
    var bar=document.querySelector('.callbar');
    if(!bar) return;
    var hero=document.querySelector('.hero');
    var threshold=200, ticking=false;
    function measure(){ threshold = hero ? Math.max(hero.offsetHeight-100, 200) : window.innerHeight*0.8; }
    function check(){ bar.classList.toggle('show', window.scrollY > threshold); ticking=false; }
    function onScroll(){ if(!ticking){ ticking=true; requestAnimationFrame(check); } }
    window.addEventListener('scroll', onScroll, {passive:true});
    window.addEventListener('resize', function(){ measure(); check(); }, {passive:true});
    window.addEventListener('load', measure, {passive:true});
    measure(); check();
  })();

  /* ---- Booking modal: open/close is lightweight and wired now;
          the heavy form validation + price calculator are deferred (initHeavy) ---- */
  var modal=document.getElementById('bookModal'), modalCard=null, modalName=null, lastFocus=null;
  if(modal){
    modalCard=modal.querySelector('.modal-card'); modalName=document.getElementById('mName');
    var openM=function(){lastFocus=document.activeElement;initHeavy();modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.classList.add('modal-open');requestAnimationFrame(function(){modal.classList.add('show');});setTimeout(function(){if(modalName)modalName.focus();},360);};
    var closeM=function(){modal.classList.remove('show');modal.setAttribute('aria-hidden','true');document.body.classList.remove('modal-open');setTimeout(function(){modal.classList.remove('open');modalCard.classList.remove('done');},300);if(lastFocus&&lastFocus.focus)lastFocus.focus();};
    document.addEventListener('click',function(e){
      var op=e.target.closest('a[href="#book"],[data-book]');
      if(op){e.preventDefault();openM();return;}
      if(e.target.closest('[data-close]'))closeM();
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('open'))closeM();});
  }

  /* ====== Deferred heavy work: price calculator + smart form validation ======
     Runs on first idle, first scroll, first pointer, or when the modal opens —
     whichever comes first. Keeps it off the critical render path. ====== */
  var heavyDone=false;
  function initHeavy(){
    if(heavyDone) return; heavyDone=true;

    /* ---- Price calculator ----
       iPhone: ТОЧНЫЕ цены из хаба (var TIERS). IPH_TIERS заполняется build-скриптом
       _build/sync_calc.py из remont-iphone/index.html — единый источник правды.
       Остальные устройства: эвристические demo-цены (нет per-model TIERS). ---- */
    var IPH_TIERS=
    /*TIERS-START*/{"iPhone 17 Pro Max":{"Замена экрана (дисплея)":[11000,11000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2000,2600],"Замена заднего стекла":[8200,8200],"Не заряжается (разъём)":[1500,2100],"После воды":[1700,4800],"Замена камеры":[2400,3500],"Динамик / микрофон":[1600,2400],"Face ID":[3200,4800],"Ремонт платы":[2800,7500]},"iPhone 17 Pro":{"Замена экрана (дисплея)":[11000,11000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1800,2400],"Замена заднего стекла":[8200,8200],"Не заряжается (разъём)":[1400,1900],"После воды":[1500,4500],"Замена камеры":[2200,3200],"Динамик / микрофон":[1500,2200],"Face ID":[3000,4500],"Ремонт платы":[2500,7200]},"iPhone 17 Air":{"Замена экрана (дисплея)":[10000,10000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1700,2300],"Замена заднего стекла":[8200,8200],"Не заряжается (разъём)":[1300,1850],"После воды":[1450,4300],"Замена камеры":[2000,3000],"Динамик / микрофон":[1400,2100],"Face ID":[2900,4300],"Ремонт платы":[2400,6800]},"iPhone 17":{"Замена экрана (дисплея)":[10000,10000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1600,2200],"Замена заднего стекла":[8200,8200],"Не заряжается (разъём)":[1250,1750],"После воды":[1350,4100],"Замена камеры":[1800,2700],"Динамик / микрофон":[1250,2000],"Face ID":[2700,4100],"Ремонт платы":[2200,6400]},"iPhone 16 Pro Max":{"Замена экрана (дисплея)":[8200,8200],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[4500,4500],"Замена заднего стекла":[4750,4750],"Не заряжается (разъём)":[1400,1900],"После воды":[1500,4500],"Замена камеры":[5500,5500],"Динамик / микрофон":[1500,2200],"Face ID":[3000,4500],"Ремонт платы":[2500,7000]},"iPhone 16 Pro":{"Замена экрана (дисплея)":[8000,8000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[4200,4200],"Замена заднего стекла":[4750,4750],"Не заряжается (разъём)":[1200,1800],"После воды":[1400,4200],"Замена камеры":[5500,5500],"Динамик / микрофон":[1300,2000],"Face ID":[2800,4200],"Ремонт платы":[2200,6500]},"iPhone 16 Plus":{"Замена экрана (дисплея)":[7000,7000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[4200,4200],"Замена заднего стекла":[4600,4600],"Не заряжается (разъём)":[1200,1700],"После воды":[1300,4000],"Замена камеры":[1800,2600],"Динамик / микрофон":[1200,1900],"Face ID":[2600,4000],"Ремонт платы":[2100,6200]},"iPhone 16":{"Замена экрана (дисплея)":[7000,7000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[4200,4200],"Замена заднего стекла":[4200,4200],"Не заряжается (разъём)":[1100,1600],"После воды":[1200,3800],"Замена камеры":[4500,4500],"Динамик / микрофон":[1100,1800],"Face ID":[2400,3800],"Ремонт платы":[2000,6000]},"iPhone 15 Pro Max":{"Замена экрана (дисплея)":[5900,5900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2900,2900],"Замена заднего стекла":[4200,4200],"Не заряжается (разъём)":[1200,1700],"После воды":[1300,4000],"Замена камеры":[7000,7000],"Динамик / микрофон":[1200,1900],"Face ID":[2600,4000],"Ремонт платы":[2200,6200]},"iPhone 15 Pro":{"Замена экрана (дисплея)":[4900,4900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2900,2900],"Замена заднего стекла":[4200,4200],"Не заряжается (разъём)":[1100,1600],"После воды":[1200,3800],"Замена камеры":[6500,6500],"Динамик / микрофон":[1100,1800],"Face ID":[2400,3800],"Ремонт платы":[2000,5800]},"iPhone 15 Plus":{"Замена экрана (дисплея)":[4900,4900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2900,2900],"Замена заднего стекла":[3500,3500],"Не заряжается (разъём)":[1050,1550],"После воды":[1100,3600],"Замена камеры":[6000,6000],"Динамик / микрофон":[1050,1700],"Face ID":[2300,3600],"Ремонт платы":[1900,5500]},"iPhone 15":{"Замена экрана (дисплея)":[4900,4900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1200,1700],"Замена заднего стекла":[3500,3500],"Не заряжается (разъём)":[1000,1500],"После воды":[1000,3500],"Замена камеры":[6000,6000],"Динамик / микрофон":[1000,1600],"Face ID":[2200,3400],"Ремонт платы":[1800,5200]},"iPhone 14 Pro Max":{"Замена экрана (дисплея)":[4900,4900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1300,1900],"Замена заднего стекла":[3100,3100],"Не заряжается (разъём)":[1050,1550],"После воды":[1200,3800],"Замена камеры":[5000,5000],"Динамик / микрофон":[2200,2200],"Face ID":[2400,3800],"Ремонт платы":[2000,5800]},"iPhone 14 Pro":{"Замена экрана (дисплея)":[4100,4100],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2600,2600],"Замена заднего стекла":[2800,2800],"Не заряжается (разъём)":[1000,1500],"После воды":[1100,3600],"Замена камеры":[5000,5000],"Динамик / микрофон":[2500,2500],"Face ID":[2200,3600],"Ремонт платы":[1800,5500]},"iPhone 14 Plus":{"Замена экрана (дисплея)":[3600,3600],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2600,2600],"Замена заднего стекла":[2900,2900],"Не заряжается (разъём)":[950,1450],"После воды":[1000,3400],"Замена камеры":[5000,5000],"Динамик / микрофон":[2200,2200],"Face ID":[2100,3400],"Ремонт платы":[1700,5000]},"iPhone 14":{"Замена экрана (дисплея)":[3400,3400],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2000,2000],"Замена заднего стекла":[2900,2900],"Не заряжается (разъём)":[900,1400],"После воды":[900,3200],"Замена камеры":[5000,5000],"Динамик / микрофон":[2100,2100],"Face ID":[2000,3200],"Ремонт платы":[1600,4800]},"iPhone 13 Pro Max":{"Замена экрана (дисплея)":[3500,3500],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[2000,2000],"Замена заднего стекла":[2400,2400],"Не заряжается (разъём)":[900,1350],"После воды":[900,3200],"Замена камеры":[4500,4500],"Динамик / микрофон":[1500,1500],"Face ID":[2000,3200],"Ремонт платы":[1600,4800]},"iPhone 13 Pro":{"Замена экрана (дисплея)":[3400,3400],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1900,1900],"Замена заднего стекла":[2400,2400],"Не заряжается (разъём)":[870,1300],"После воды":[850,3100],"Замена камеры":[4000,4000],"Динамик / микрофон":[1500,1500],"Face ID":[1900,3100],"Ремонт платы":[1550,4600]},"iPhone 13":{"Замена экрана (дисплея)":[3100,3100],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1700,1700],"Замена заднего стекла":[2000,2000],"Не заряжается (разъём)":[850,1300],"После воды":[800,3000],"Замена камеры":[3900,3900],"Динамик / микрофон":[1500,1500],"Face ID":[1800,3000],"Ремонт платы":[1500,4500]},"iPhone 13 mini":{"Замена экрана (дисплея)":[3500,3500],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1850,1850],"Замена заднего стекла":[1900,1900],"Не заряжается (разъём)":[830,1250],"После воды":[780,2900],"Замена камеры":[3900,3900],"Динамик / микрофон":[1500,1500],"Face ID":[1750,2900],"Ремонт платы":[1450,4300]},"iPhone 12 Pro Max":{"Замена экрана (дисплея)":[3200,3200],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1900,1900],"Замена заднего стекла":[2200,2200],"Не заряжается (разъём)":[830,1250],"После воды":[800,2900],"Замена камеры":[4300,4300],"Динамик / микрофон":[1800,1800],"Face ID":[1700,2900],"Ремонт платы":[1450,4400]},"iPhone 12 Pro":{"Замена экрана (дисплея)":[2900,2900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1900,1900],"Замена заднего стекла":[2200,2200],"Не заряжается (разъём)":[810,1220],"После воды":[770,2850],"Замена камеры":[4300,4300],"Динамик / микрофон":[1800,1800],"Face ID":[1650,2850],"Ремонт платы":[1420,4300]},"iPhone 12":{"Замена экрана (дисплея)":[2900,2900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1800,1800],"Замена заднего стекла":[2000,2000],"Не заряжается (разъём)":[800,1200],"После воды":[750,2800],"Замена камеры":[3900,3900],"Динамик / микрофон":[1800,1800],"Face ID":[1600,2800],"Ремонт платы":[1400,4200]},"iPhone 12 mini":{"Замена экрана (дисплея)":[2600,2600],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1800,1800],"Замена заднего стекла":[1700,1700],"Не заряжается (разъём)":[780,1180],"После воды":[730,2700],"Замена камеры":[3900,3900],"Динамик / микрофон":[1800,1800],"Face ID":[1550,2700],"Ремонт платы":[1350,4100]},"iPhone 11 Pro Max":{"Замена экрана (дисплея)":[2300,2300],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1500,1500],"Замена заднего стекла":[1600,1600],"Не заряжается (разъём)":[770,1150],"После воды":[730,2600],"Замена камеры":[2400,2400],"Динамик / микрофон":[1000,1000],"Face ID":[1550,2600],"Ремонт платы":[1250,3900]},"iPhone 11 Pro":{"Замена экрана (дисплея)":[2000,2000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1300,1300],"Замена заднего стекла":[1450,1450],"Не заряжается (разъём)":[760,1130],"После воды":[720,2550],"Замена камеры":[2100,2100],"Динамик / микрофон":[900,900],"Face ID":[1520,2550],"Ремонт платы":[1230,3850]},"iPhone 11":{"Замена экрана (дисплея)":[2200,2200],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1200,1200],"Замена заднего стекла":[1300,1300],"Не заряжается (разъём)":[750,1100],"После воды":[700,2500],"Замена камеры":[2100,2100],"Динамик / микрофон":[1000,1000],"Face ID":[1500,2500],"Ремонт платы":[1200,3800]},"iPhone XS Max":{"Замена экрана (дисплея)":[2000,2000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1200,1200],"Замена заднего стекла":[950,950],"Не заряжается (разъём)":[700,1050],"После воды":[680,2400],"Замена камеры":[2700,2700],"Динамик / микрофон":[1400,1400],"Face ID":[1400,2400],"Ремонт платы":[1100,3600]},"iPhone XS":{"Замена экрана (дисплея)":[1700,1700],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1100,1100],"Замена заднего стекла":[950,950],"Не заряжается (разъём)":[690,1030],"После воды":[670,2350],"Замена камеры":[2400,2400],"Динамик / микрофон":[1400,1400],"Face ID":[1380,2350],"Ремонт платы":[1080,3500]},"iPhone XR":{"Замена экрана (дисплея)":[1400,2000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1000,1000],"Замена заднего стекла":[950,950],"Не заряжается (разъём)":[680,1020],"После воды":[660,2300],"Замена камеры":[1800,1800],"Динамик / микрофон":[1000,1000],"Face ID":[1350,2300],"Ремонт платы":[1050,3400]},"iPhone X":{"Замена экрана (дисплея)":[1700,1700],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[950,950],"Замена заднего стекла":[950,950],"Не заряжается (разъём)":[670,1000],"После воды":[650,2250],"Замена камеры":[1900,1900],"Динамик / микрофон":[1400,1400],"Face ID":[1300,2250],"Ремонт платы":[1000,3300]},"iPhone 8 Plus":{"Замена экрана (дисплея)":[1000,1000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[900,900],"Замена заднего стекла":[850,850],"Не заряжается (разъём)":[650,980],"После воды":[650,2200],"Замена камеры":[2300,2300],"Динамик / микрофон":[400,400],"Кнопка Home / Touch ID":[950,1500],"Ремонт платы":[950,3200]},"iPhone 8":{"Замена экрана (дисплея)":[900,900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[800,800],"Замена заднего стекла":[850,850],"Не заряжается (разъём)":[640,960],"После воды":[640,2150],"Замена камеры":[1990,1990],"Динамик / микрофон":[400,400],"Кнопка Home / Touch ID":[920,1450],"Ремонт платы":[920,3100]},"iPhone 7 Plus":{"Замена экрана (дисплея)":[900,900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[800,800],"Не заряжается (разъём)":[630,950],"После воды":[630,2100],"Замена камеры":[2300,2300],"Динамик / микрофон":[400,400],"Кнопка Home / Touch ID":[900,1400],"Ремонт платы":[900,3000]},"iPhone 7":{"Замена экрана (дисплея)":[900,900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[700,700],"Не заряжается (разъём)":[620,940],"После воды":[620,2050],"Замена камеры":[1050,1050],"Динамик / микрофон":[300,300],"Кнопка Home / Touch ID":[880,1380],"Ремонт платы":[880,2900]},"iPhone SE 3 (2022)":{"Замена экрана (дисплея)":[1000,1000],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[1400,1400],"Не заряжается (разъём)":[700,1050],"После воды":[700,2300],"Замена камеры":[2000,2000],"Динамик / микрофон":[700,1120],"Кнопка Home / Touch ID":[1000,1600],"Ремонт платы":[1000,3300]},"iPhone SE 2 (2020)":{"Замена экрана (дисплея)":[900,900],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[900,900],"Не заряжается (разъём)":[700,1000],"После воды":[700,2200],"Замена камеры":[1700,1700],"Динамик / микрофон":[1000,1000],"Кнопка Home / Touch ID":[1000,1600],"Ремонт платы":[1000,3200]},"iPhone SE (2016)":{"Замена экрана (дисплея)":[600,600],"Замена стекла (без замены дисплея)":[0,0],"Замена аккумулятора":[800,800],"Не заряжается (разъём)":[600,900],"После воды":[600,2000],"Замена камеры":[450,450],"Динамик / микрофон":[200,200],"Кнопка Home / Touch ID":[850,1350],"Ремонт платы":[850,2800]}}/*TIERS-END*/
    ;
    /* ---- Живое обновление цен из CMS (Supabase published_prices) ----
       Калькулятор сразу работает на запечённых ценах (SEO/мгновенно), а как только
       придёт свежий снимок из админки — тихо обновляемся БЕЗ пересборки сайта.
       Любая ошибка/недоступность → остаёмся на запечённых ценах. ---- */
    (function(){
      try{
        var SB='https://xvqqoyttvfmrjvufkkzm.supabase.co',
            AK='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh2cXFveXR0dmZtcmp2dWZra3ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM0MDQwMDgsImV4cCI6MjA5ODk4MDAwOH0.yaUDu6A4ajFSKx7Xn51BEUgMgkpF47HOhRocCYfjpSU';
        fetch(SB+'/rest/v1/model_prices?select=label,prices,published_prices&order=sort.asc',
              {headers:{apikey:AK,Authorization:'Bearer '+AK}})
          .then(function(r){return r.ok?r.json():null;})
          .then(function(rows){
            if(!rows||!rows.length) return;
            var n=0;
            rows.forEach(function(row){
              var pr=row.published_prices||row.prices;   // клиенту — только опубликованное
              if(row.label && pr && IPH_TIERS[row.label]){ IPH_TIERS[row.label]=pr; n++; }
            });
            if(n && typeof calc==='function'){ try{ if(typeof loadProblems==='function') loadProblems(); calc(); }catch(e){} }
          })['catch'](function(){});
      }catch(e){}
    })();
    var DATA={
      iphone:{label:"iPhone"},
      macbook:{label:"MacBook",
        models:["MacBook Pro 14/16 (M-series)","MacBook Pro 13","MacBook Air (M-series)","MacBook Air 13","MacBook Pro Retina","MacBook Air (старый)"],
        problems:{"Замена матрицы":[3500,16000],"Замена клавиатуры":[1800,6500],"Замена аккумулятора":[1500,4500],"Чистка после воды":[1200,6000],"Не включается (плата)":[2000,9000],"Апгрейд SSD / RAM":[900,3500]}},
      ipad:{label:"iPad",
        models:["iPad Pro 12.9","iPad Pro 11","iPad Air","iPad","iPad mini"],
        problems:{"Замена стекла (тачскрина)":[1200,5500],"Замена дисплея":[1800,9000],"Замена аккумулятора":[1200,3000],"Не заряжается (разъём)":[900,2200],"После воды":[1000,4500]}},
      watch:{label:"Apple Watch",
        models:["Apple Watch Ultra","Series 9 / 8 / 7","Series 6 / SE","Series 5 / 4","Series 3 и старше"],
        problems:{"Замена стекла":[900,3500],"Замена дисплея":[1500,6000],"Замена аккумулятора":[800,2200],"После воды":[700,3000]}},
      airpods:{label:"AirPods",
        models:["AirPods Pro 2","AirPods Pro","AirPods 3","AirPods 2","AirPods Max"],
        problems:{"Чистка":[400,900],"Не заряжаются":[500,1500],"Замена амбушюр / сетки":[400,1200],"Диагностика звука":[300,800]}}
    };
    function tierMult(model){
      if(/Ultra|Pro 14\/16|Pro Max/.test(model)) return 1.5;
      if(/Series 9|Pro 11|Pro 12\.9|Air \(M|AirPods Pro 2|Max/.test(model)) return 1.2;
      if(/Series 8|Series 7|Air|iPad\b|AirPods 3|AirPods Pro\b/.test(model)) return 0.95;
      return 0.7;
    }
    function r50(n){return Math.round(n/50)*50;}
    var elDev=document.getElementById('cDevice'),elModel=document.getElementById('cModel'),elProb=document.getElementById('cProblem'),
        elPrice=document.getElementById('cPrice'),elMeta=document.getElementById('cMeta');
    if(elDev&&elModel&&elProb){
      var curDev='iphone';
      var IPH_MODELS=Object.keys(IPH_TIERS);
      var fill=function(sel,arr){sel.innerHTML='';arr.forEach(function(v){var o=document.createElement('option');o.textContent=v;sel.appendChild(o);});};
      var loadProblems=function(){
        if(curDev==='iphone'){fill(elProb,Object.keys(IPH_TIERS[elModel.value]||{}));}
        else{fill(elProb,Object.keys(DATA[curDev].problems));}
      };
      var loadDevice=function(){fill(elModel,curDev==='iphone'?IPH_MODELS:DATA[curDev].models);loadProblems();calc();};
      var buildDevices=function(){
        Object.keys(DATA).forEach(function(k,i){
          var btn=document.createElement('button');btn.type='button';btn.className='seg-btn'+(i===0?' on':'');btn.textContent=DATA[k].label;btn.dataset.k=k;
          btn.addEventListener('click',function(){curDev=k;elDev.querySelectorAll('.seg-btn').forEach(function(x){x.classList.remove('on')});btn.classList.add('on');loadDevice();});
          elDev.appendChild(btn);
        });
      };
      var calc=function(){
        var prob=elProb.value,model=elModel.value,lo,hi;
        if(curDev==='iphone'){
          var p=(IPH_TIERS[model]||{})[prob];
          if(!p){elPrice.textContent='-';elMeta.innerHTML='';return;}
          lo=p[0];hi=p[1];
        } else {
          var dd=DATA[curDev];
          if(!dd.problems[prob]){elPrice.textContent='-';elMeta.innerHTML='';return;}
          var base=dd.problems[prob],mm=tierMult(model);
          lo=r50(base[0]*mm);hi=r50(base[1]*Math.min(mm,1.3));
          if(hi<=lo) hi=lo+ r50(base[0]*0.3);
        }
        elPrice.innerHTML=(!lo&&!hi)?'<small>Уточняйте при заявке</small>':(lo===hi)?lo.toLocaleString('ru-RU')+' <small>₴</small>':'от '+lo.toLocaleString('ru-RU')+' <small>до '+hi.toLocaleString('ru-RU')+' ₴</small>';
        var t=(curDev==='iphone')?'30-60 минут':'от 1 часа';
        elMeta.innerHTML='<span class="free">Диагностика 0 ₴</span><span>Гарантия 12 мес</span><span>Срок: '+t+'</span>';
      };
      elModel.addEventListener('change',function(){if(curDev==='iphone')loadProblems();calc();});
      elProb.addEventListener('change',calc);
      buildDevices();loadDevice();
    }

    /* ---- Smart booking forms (modal + inline): same approach, reusable ---- */
    var OPS=[
      {n:'Kyivstar',c:['67','68','96','97','98','77']},
      {n:'Vodafone',c:['50','66','95','99']},
      {n:'lifecell',c:['63','73','93']},
      {n:'оператор',c:['91','92','94']}
    ];
    function detect(code){for(var i=0;i<OPS.length;i++){if(OPS[i].c.indexOf(code)>-1)return OPS[i].n;}return null;}
    function rawDigits(v){var d=v.replace(/\D/g,'');if(d.indexOf('38')===0)d=d.slice(2);if(d.length&&d[0]!=='0')d='0'+d;return d.slice(0,10);}
    function fmt(d){var o='';if(d.length>0)o='('+d.slice(0,3);if(d.length>=3)o+=') ';if(d.length>3)o+=d.slice(3,6);if(d.length>6)o+='-'+d.slice(6,8);if(d.length>8)o+='-'+d.slice(8,10);return o;}
    function esc(s){return String(s).replace(/[<>&"]/g,function(c){return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c];});}

    function wireForm(o){
      if(!o.name||!o.phone||!o.submit) return;
      var dots=o.dotsWrap?o.dotsWrap.querySelectorAll('i'):[];
      var phoneValid=false;
      function checkPhone(){
        var d=rawDigits(o.phone.value); o.phone.value=fmt(d);
        var box=o.phone.closest('.mf-input'); phoneValid=false;
        if(d.length===0){o.hint.textContent='Введите номер мобильного оператора Украины';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else if(d.length<10){o.hint.textContent='Введите номер полностью';o.hint.className='mf-hint js-hint';box.classList.remove('valid','invalid');}
        else{var op=detect(d.slice(1,3));
          if(op){phoneValid=true;o.hint.innerHTML='<span class="mf-op">✓ '+op+'</span> номер распознан';o.hint.className='mf-hint js-hint ok';box.classList.add('valid');box.classList.remove('invalid');}
          else{o.hint.textContent='Проверьте код оператора - такого в Украине нет';o.hint.className='mf-hint js-hint err';box.classList.add('invalid');box.classList.remove('valid');}
        }
        for(var i=0;i<dots.length;i++){ if(i<d.length) dots[i].classList.add('on'); else dots[i].classList.remove('on'); }
        if(o.dotsWrap){o.dotsWrap.classList.remove('valid','invalid'); if(d.length===10) o.dotsWrap.classList.add(phoneValid?'valid':'invalid');}
        return d;
      }
      function checkName(){var ok=o.name.value.trim().length>=2;o.name.closest('.mf-input').classList.toggle('valid',ok);return ok;}
      function update(){
        var nameOk=checkName(); var d=checkPhone();
        var p=Math.round(((nameOk?1:0)+Math.min(d.length/10,1))/2*100);
        if(o.bar)o.bar.style.width=p+'%'; if(o.pct)o.pct.textContent=p+'%';
        o.submit.disabled=!(nameOk&&phoneValid);
      }
      o.name.addEventListener('input',update);
      o.phone.addEventListener('input',update);
      o.submit.addEventListener('click',function(){
        if(o.submit.disabled)return;
        if(o.summary)o.summary.innerHTML=
          '<div><span>Имя</span><b>'+esc(o.name.value.trim())+'</b></div>'+
          '<div><span>Телефон</span><b>+38 '+esc(o.phone.value)+'</b></div>'+
          '<div><span>Запрос</span><b>'+esc(o.dev?o.dev.value:'')+'</b></div>';
        if(o.bar)o.bar.style.width='100%';
        o.root.classList.add('done');
      });
      update();
    }

    if(modal){
      wireForm({root:modalCard,name:modalName,phone:document.getElementById('mPhone'),dev:document.getElementById('mDevice'),hint:document.getElementById('mPhoneHint'),bar:document.getElementById('mpBar'),pct:document.getElementById('mPct'),submit:document.getElementById('mSubmit'),dotsWrap:document.getElementById('mPhoneDots'),summary:document.getElementById('msSummary')});
    }

    var inlineRoot=document.getElementById('bookFormInline');
    if(inlineRoot){
      wireForm({root:inlineRoot,name:inlineRoot.querySelector('.js-name'),phone:inlineRoot.querySelector('.js-phone'),dev:inlineRoot.querySelector('.js-device'),hint:inlineRoot.querySelector('.js-hint'),bar:inlineRoot.querySelector('.js-bar'),pct:inlineRoot.querySelector('.js-pct'),submit:inlineRoot.querySelector('.js-submit'),dotsWrap:inlineRoot.querySelector('.js-dots'),summary:inlineRoot.querySelector('.js-summary')});
    }
  }

  if('requestIdleCallback' in window){ requestIdleCallback(initHeavy,{timeout:1500}); }
  else { setTimeout(initHeavy,800); }
  addEventListener('scroll', initHeavy, {passive:true, once:true});
  addEventListener('pointerdown', initHeavy, {once:true});
