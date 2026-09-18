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

  function progressStart() {
    if (!bar) {
      bar = document.createElement('div');
      bar.id = 'jt-progress';
      document.body.appendChild(bar);
    }
    bar.style.opacity = '.9';
    bar.style.width = '0';
    // Kulazimisha reflow ili transition ianze kutoka sifuri
    void bar.offsetWidth;
    bar.style.width = '60%';
    clearTimeout(barTimer);
    // Inafika 90% kisha inasubiri. Kuifikisha 100% kabla ukurasa
    // haujafika kungemfanya mtu adhani umeganda.
    barTimer = setTimeout(function () { if (bar) bar.style.width = '90%'; }, 600);
  }

  function progressDone() {
    if (!bar) return;
    clearTimeout(barTimer);
    bar.style.width = '100%';
    setTimeout(function () { if (bar) bar.style.opacity = '0'; }, 200);
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

    progressStart();
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

    progressStart();
    if (a.classList.contains('btn') || a.classList.contains('b')
        || a.classList.contains('sb')) {
      setBusy(a, a.getAttribute('data-jt-wait') || '');
    }
  }, true);

  // ── Kurudi nyuma ────────────────────────────────────────
  // Browser inaweza kurudisha ukurasa kutoka kwenye kumbukumbu
  // (bfcache) ikiwa na kitufe bado kinazunguka. Tunaisafisha.

  window.addEventListener('pageshow', function (ev) {
    if (!ev.persisted) return;
    document.querySelectorAll('[data-jt-busy]').forEach(clearBusy);
    document.querySelectorAll('[data-jt-sent]').forEach(function (f) {
      f.removeAttribute('data-jt-sent');
    });
    progressDone();
  });

  window.addEventListener('beforeunload', progressStart);

  // ── API kwa code ya ukurasa ─────────────────────────────
  // fetch() inayotumika kwenye QR, maarifa na sessions inaweza
  // kuonyesha hali ile ile bila kuandika upya.

  window.jt = {
    busy: setBusy,
    done: clearBusy,
    progress: { start: progressStart, done: progressDone },
  };
})();
