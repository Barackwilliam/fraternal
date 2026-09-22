/* ============================================================
   JamiiTek — mwitikio wa kugusa
   ============================================================

   Inashughulikia kitu kimoja: kumwambia mtu kwamba mfumo umesikia.

   Bila hii, mtu anabonyeza mara nne akidhani hakigusi — na fomu
   inatumwa mara nne. Rekodi za marudio si tatizo la muonekano.

   HAKUNA MAKTABA. Hakuna jQuery, hakuna kifurushi. Inafanya kazi
   kwenye template zote tano bila kubadilisha chochote kilichopo.
   ============================================================ */

(function () {
  'use strict';

  var SHOW_AFTER = 120;   // ms kabla ya spinner — ombi la haraka halionyeshi
  var busy = new WeakMap();

  // ── Mstari wa maendeleo ─────────────────────────────────
  var bar = null, barTimer = null;

  var trickle = null, pct = 0, running = false;

  function progressStart(opts) {
    if (running) return;
    running = true;
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'jt-progress';
      bar.innerHTML = '<i></i>';          // kichwa kinachong'aa
      document.body.appendChild(bar);
    }
    pct = 8;
    bar.style.transition = 'none';
    bar.style.opacity = '1';
    bar.style.width = pct + '%';
    void bar.offsetWidth;                 // reflow ili transition ianze upya
    bar.style.transition = '';
    // Inasonga haraka mwanzoni, kisha polepole zaidi karibu na mwisho —
    // haifiki 100% mpaka ukurasa ufike. Mstari uliosimama ungeonekana
    // kama umeganda; unaosonga unasema "bado nafanya kazi".
    clearInterval(trickle);
    trickle = setInterval(function () {
      pct += (94 - pct) * 0.09;
      if (bar) bar.style.width = pct + '%';
    }, 180);
    if (!(opts && opts.noOverlay)) overlaySchedule();
  }

  function progressDone() {
    running = false;
    clearInterval(trickle);
    overlayHide();
    if (!bar) return;
    bar.style.width = '100%';
    setTimeout(function () { if (bar && !running) bar.style.opacity = '0'; }, 260);
  }

  // ── Skrini ya kupakia ───────────────────────────────────
  // Inaonekana tu ukurasa ukichelewa zaidi ya 450ms. Ukurasa wa haraka
  // hauionyeshi kabisa — skrini inayowaka kwa 100ms inaonekana kama
  // hitilafu, si kasi.
  var ov = null, ovTimer = null, ovSlow = null, ovSafety = null;

  function isSw() {
    return (document.documentElement.lang || '').toLowerCase().indexOf('sw') === 0;
  }

  function iconUrl() {
    var l = document.querySelector('link[rel~="icon"]');
    return l ? l.href : '';
  }

  function overlayBuild() {
    if (ov) return ov;
    ov = document.createElement('div');
    ov.id = 'jt-loader';
    ov.setAttribute('role', 'status');
    ov.setAttribute('aria-live', 'polite');
    var ico = iconUrl();
    ov.innerHTML =
      '<div class="jt-ld-card">' +
        '<div class="jt-ld-mark">' +
          '<span class="jt-ld-ring"></span><span class="jt-ld-ring r2"></span>' +
          '<span class="jt-ld-core">' + (ico ? '<img src="' + ico + '" alt="">' : '<b></b>') + '</span>' +
        '</div>' +
        '<div class="jt-ld-txt">' + (isSw() ? 'Inafungua' : 'Loading') +
          '<span class="jt-ld-dots"><i>.</i><i>.</i><i>.</i></span></div>' +
        '<div class="jt-ld-sub"></div>' +
      '</div>';
    document.body.appendChild(ov);
    return ov;
  }

  function overlaySchedule() {
    clearTimeout(ovTimer); clearTimeout(ovSlow); clearTimeout(ovSafety);
    ovTimer = setTimeout(function () {
      overlayBuild();
      ov.querySelector('.jt-ld-sub').textContent = '';
      ov.classList.add('on');
    }, 450);
    // Mtandao wa polepole: mwambie ukweli badala ya kumwacha akisubiri kimya
    ovSlow = setTimeout(function () {
      if (ov && ov.classList.contains('on')) {
        ov.querySelector('.jt-ld-sub').textContent = isSw()
          ? 'Mtandao uko polepole kidogo — tunaendelea…'
          : 'Your connection is a little slow — still working…';
      }
    }, 5000);
    // Kinga: link inayopakua faili (PDF) haibadilishi ukurasa. Bila hii,
    // skrini ya kupakia ingebaki milele juu ya ukurasa uliopo.
    ovSafety = setTimeout(progressDone, 15000);
  }

  function overlayHide() {
    clearTimeout(ovTimer); clearTimeout(ovSlow); clearTimeout(ovSafety);
    if (ov) ov.classList.remove('on');
  }

  // ── Hali ya kusubiri ────────────────────────────────────

  function setBusy(el, label) {
    if (!el || busy.has(el)) return;

    var w = el.offsetWidth, h = el.offsetHeight;
    busy.set(el, {
      width: el.style.width,
      height: el.style.height,
      disabled: el.disabled,
    });

    // Ukubwa unashikiliwa ili ukurasa usiruke lebo inapofichwa
    if (w) el.style.width = w + 'px';
    if (h) el.style.height = h + 'px';

    var timer = setTimeout(function () {
      el.setAttribute('data-jt-busy', '');
      if (label) el.setAttribute('data-jt-label', label);
    }, SHOW_AFTER);

    busy.get(el).timer = timer;

    // Kuzuia kutuma mara ya pili. `disabled` kwenye <button> ndani ya
    // fomu ingezuia thamani yake isitumwe, kwa hiyo tunatumia
    // pointer-events (CSS) na bendera hii badala yake.
    el.setAttribute('aria-busy', 'true');
    if (el.tagName === 'A') el.style.pointerEvents = 'none';
  }

  function clearBusy(el) {
    var s = busy.get(el);
    if (!s) return;
    clearTimeout(s.timer);
    el.removeAttribute('data-jt-busy');
    el.removeAttribute('data-jt-label');
    el.removeAttribute('aria-busy');
    el.style.width = s.width;
    el.style.height = s.height;
    if (el.tagName === 'A') el.style.pointerEvents = '';
    busy.delete(el);
  }

  // ── Fomu ────────────────────────────────────────────────

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.hasAttribute('data-jt-skip')) return;

    // Fomu iliyoshatumwa haitumwi tena. Hii ndiyo inayozuia
    // rekodi za marudio.
    if (form.hasAttribute('data-jt-sent')) {
      e.preventDefault();
      return;
    }
    // Fomu yenye kasoro ya uthibitishaji bado haijatumwa
    if (typeof form.checkValidity === 'function' && !form.checkValidity()) return;

    form.setAttribute('data-jt-sent', '');

    var btn = form.querySelector('[type="submit"]')
           || form.querySelector('button:not([type="button"])');
    if (btn) setBusy(btn, btn.getAttribute('data-jt-wait') || '');

    // Fomu ya kupakua (export) haibadilishi ukurasa
    var act = form.getAttribute('action') || '';
    progressStart({ noOverlay: /pdf|download|export/i.test(act) });
  }, true);

  // ── Viungo vinavyobadilisha ukurasa ─────────────────────

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    if (a.hasAttribute('data-jt-skip')) return;

    var href = a.getAttribute('href') || '';
    if (!href
        || href.charAt(0) === '#'
        || href.indexOf('javascript:') === 0
        || href.indexOf('mailto:') === 0
        || href.indexOf('tel:') === 0
        || a.target === '_blank'
        || a.hasAttribute('download')
        || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;

    // Kiungo cha nje hakibadilishi ukurasa huu kwa njia tunayoweza
    // kuifuatilia — mstari wa maendeleo ungekwama.
    try {
      var u = new URL(a.href, location.href);
      if (u.origin !== location.origin) return;
    } catch (_) { return; }

    // Link ya kupakua (PDF, export) haibadilishi ukurasa
    var isFile = /\/(pdf|download|export)\/|\.(pdf|csv|xlsx?|docx?|zip)(\?|$)/i.test(u.pathname + u.search);
    progressStart({ noOverlay: isFile });
    if (a.classList.contains('btn') || a.classList.contains('b')
        || a.classList.contains('sb')) {
      setBusy(a, a.getAttribute('data-jt-wait') || '');
    }
  }, true);

  // ── Mguso unaoonekana: wimbi kutoka pale kidole kilipogusa ──
  // Linachorwa kwenye tabaka lake juu ya kitufe (position: fixed), si
  // ndani yake — kwa hiyo halibadilishi overflow wala muundo wa kitufe
  // chochote kilichopo, na linafanya kazi kwenye kila template.
  var TAP = 'a[href],button,[role="button"],input[type="submit"],input[type="button"],summary,label[for]';

  document.addEventListener('pointerdown', function (e) {
    if (e.button !== 0 && e.pointerType === 'mouse') return;
    var el = e.target.closest && e.target.closest(TAP);
    if (!el || el.disabled || el.closest('[data-jt-noripple]')) return;

    var cs = getComputedStyle(el);
    var r = el.getBoundingClientRect();
    // Link ndani ya sentensi: kufifia kidogo tu, si wimbi
    if (cs.display === 'inline' || r.width < 24 || r.height < 16) {
      el.classList.add('jt-tap');
      setTimeout(function () { el.classList.remove('jt-tap'); }, 220);
      return;
    }
    // Kitu kikubwa kupita kiasi (sehemu nzima ya ukurasa) — hakuna wimbi
    if (r.width * r.height > innerWidth * innerHeight * 0.5) return;

    var box = document.createElement('span');
    box.className = 'jt-ripple-box';
    box.style.cssText = 'left:' + r.left + 'px;top:' + r.top + 'px;width:' + r.width +
      'px;height:' + r.height + 'px;border-radius:' + cs.borderRadius + ';color:' + cs.color;
    var d = Math.max(r.width, r.height) * 2.2;
    var dot = document.createElement('i');
    dot.style.cssText = 'width:' + d + 'px;height:' + d + 'px;left:' +
      (e.clientX - r.left - d / 2) + 'px;top:' + (e.clientY - r.top - d / 2) + 'px';
    box.appendChild(dot);
    document.body.appendChild(box);
    setTimeout(function () { box.remove(); }, 650);
  }, { passive: true });

  // ── Kupakia mapema ──────────────────────────────────────
  // Kidole/kipanya kikikaa juu ya link kwa 65ms (au kidole kikigusa
  // skrini), ukurasa unaanza kupakuliwa KABLA ya kubonyeza. Kati ya
  // kugusa na kuachia kuna ~100–300ms — ukurasa mara nyingi unakuwa
  // umeshafika. Hiyo ndiyo inayofanya mfumo uhisi wa papo hapo.
  //
  // Kinga: GET ya link fulani ina athari (logout, delete…). Hizo
  // HAZIPAKIWI MAPEMA kamwe — tungemtoa mtu nje kwa kupitisha kipanya tu.
  var UNSAFE = /logout|signout|sign-out|delete|remove|destroy|toggle|suspend|activate|deactivat|disconnect|cancel|reset|approve|reject|verify|resend|restart|clear|purge|pay|checkout|\/cron\/|\/tasks\/|\/admin\/|\/api\/|webhook|download|export|\/pdf|\.pdf|action=/i;
  var fetched = {};
  var conn = navigator.connection || {};
  var canPrefetch = !(conn.saveData || /2g/.test(conn.effectiveType || ''));
  var hoverT = null;

  function prefetchable(a) {
    if (!canPrefetch || !a || a.target === '_blank' || a.hasAttribute('download')
        || a.hasAttribute('data-jt-noprefetch')) return false;
    var u;
    try { u = new URL(a.href, location.href); } catch (_) { return false; }
    if (u.origin !== location.origin || !/^https?:$/.test(u.protocol)) return false;
    if (u.pathname === location.pathname && u.search === location.search) return false;
    return !UNSAFE.test(u.pathname + u.search);
  }

  function prefetch(url) {
    if (fetched[url]) return;
    fetched[url] = 1;
    var l = document.createElement('link');
    l.rel = 'prefetch';
    l.href = url;
    l.as = 'document';
    document.head.appendChild(l);
  }

  document.addEventListener('mouseover', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!prefetchable(a)) return;
    clearTimeout(hoverT);
    hoverT = setTimeout(function () { prefetch(a.href); }, 65);
  }, { passive: true });
  document.addEventListener('mouseout', function () { clearTimeout(hoverT); }, { passive: true });
  document.addEventListener('touchstart', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (prefetchable(a)) prefetch(a.href);
  }, { passive: true });

  // ── Kurudi nyuma ────────────────────────────────────────
  // Browser inaweza kurudisha ukurasa kutoka kwenye kumbukumbu
  // (bfcache) ikiwa na kitufe bado kinazunguka. Tunaisafisha.

  window.addEventListener('pageshow', function (ev) {
    if (!ev.persisted) { progressDone(); return; }
    document.querySelectorAll('[data-jt-busy]').forEach(clearBusy);
    document.querySelectorAll('[data-jt-sent]').forEach(function (f) {
      f.removeAttribute('data-jt-sent');
    });
    progressDone();
  });

  // Inashika urambazaji ambao haukupitia link wala fomu (location.href=…)
  window.addEventListener('beforeunload', function () { progressStart(); });
  // Faili likipakuliwa, ukurasa unabaki na dirisha linarudi kuwa hai
  window.addEventListener('focus', function () { if (running) setTimeout(progressDone, 800); });

  // ── API kwa code ya ukurasa ─────────────────────────────
  // fetch() inayotumika kwenye QR, maarifa na sessions inaweza
  // kuonyesha hali ile ile bila kuandika upya.

  window.jt = {
    busy: setBusy,
    done: clearBusy,
    progress: { start: progressStart, done: progressDone },
  };
})();
