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

    /* ---- Price calculator (demo data, no backend) ---- */
    var DATA={
      iphone:{label:"iPhone",
        models:["iPhone 17 Pro Max","iPhone 17 Pro","iPhone 17 Air","iPhone 17","iPhone 16 Pro Max","iPhone 16 Pro","iPhone 16","iPhone 15 Pro Max","iPhone 15 Pro","iPhone 15","iPhone 14 Pro","iPhone 14","iPhone 13","iPhone 12","iPhone 11","iPhone SE"],
        problems:{"Замена экрана (дисплея)":[1200,7500],"Замена аккумулятора":[850,2400],"Замена стекла":[900,3800],"Не заряжается (разъём)":[750,1900],"После воды":[700,4500],"Замена камеры":[800,3200],"Динамик / микрофон":[700,2200],"Face ID":[1500,4500]}},
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
      if(/Ultra|17 Pro|16 Pro Max|16 Pro|Pro 14\/16|Pro Max/.test(model)) return 1.5;
      if(/iPhone 17|16|15 Pro|15|Series 9|Pro 11|Pro 12\.9|Air \(M|AirPods Pro 2|Max/.test(model)) return 1.2;
      if(/14|13|Series 8|Series 7|Air|iPad\b|AirPods 3|AirPods Pro\b/.test(model)) return 0.95;
      return 0.7;
    }
    function r50(n){return Math.round(n/50)*50;}
    var elDev=document.getElementById('cDevice'),elModel=document.getElementById('cModel'),elProb=document.getElementById('cProblem'),
        elPrice=document.getElementById('cPrice'),elMeta=document.getElementById('cMeta');
    if(elDev&&elModel&&elProb){
      var curDev='iphone';
      var fill=function(sel,arr){sel.innerHTML='';arr.forEach(function(v){var o=document.createElement('option');o.textContent=v;sel.appendChild(o);});};
      var loadDevice=function(){fill(elModel,DATA[curDev].models);fill(elProb,Object.keys(DATA[curDev].problems));calc();};
      var buildDevices=function(){
        Object.keys(DATA).forEach(function(k,i){
          var btn=document.createElement('button');btn.type='button';btn.className='seg-btn'+(i===0?' on':'');btn.textContent=DATA[k].label;btn.dataset.k=k;
          btn.addEventListener('click',function(){curDev=k;elDev.querySelectorAll('.seg-btn').forEach(function(x){x.classList.remove('on')});btn.classList.add('on');loadDevice();});
          elDev.appendChild(btn);
        });
      };
      var calc=function(){
        var dd=DATA[curDev],prob=elProb.value,model=elModel.value;
        if(!dd.problems[prob]){elPrice.textContent='-';elMeta.innerHTML='';return;}
        var base=dd.problems[prob],mm=tierMult(model);
        var lo=r50(base[0]*mm),hi=r50(base[1]*Math.min(mm,1.3));
        if(hi<=lo) hi=lo+ r50(base[0]*0.3);
        elPrice.innerHTML='от '+lo.toLocaleString('ru-RU')+' <small>до '+hi.toLocaleString('ru-RU')+' ₴</small>';
        var t=(curDev==='iphone')?'30-60 минут':'от 1 часа';
        elMeta.innerHTML='<span class="free">Диагностика 0 ₴</span><span>Гарантия 12 мес</span><span>Срок: '+t+'</span>';
      };
      elModel.addEventListener('change',calc);elProb.addEventListener('change',calc);
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
