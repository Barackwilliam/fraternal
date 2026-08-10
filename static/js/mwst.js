/* ==========================================================================
   MWST MMS — shared behaviour
   Hakuna framework. Vanilla JS tu ili iwe rahisi kuhamishia Django templates.
   ========================================================================== */
(function () {
  "use strict";

  /* ---------- Helpers ---------- */
  const $  = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  const css = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  /* ---------- Sidebar ---------- */
  const app = $(".app");

  function toggleSidebar() {
    if (!app) return;
    if (window.innerWidth <= 1024) {
      app.classList.toggle("is-mobileopen");
    } else {
      app.classList.toggle("is-collapsed");
      try {
        localStorage.setItem(
          "mwst.sidebar",
          app.classList.contains("is-collapsed") ? "collapsed" : "open"
        );
      } catch (e) {}
    }
  }

  $$("[data-toggle-sidebar]").forEach((b) =>
    b.addEventListener("click", toggleSidebar)
  );
  const scrim = $(".scrim");
  if (scrim) scrim.addEventListener("click", () => app.classList.remove("is-mobileopen"));

  try {
    if (localStorage.getItem("mwst.sidebar") === "collapsed" && window.innerWidth > 1024) {
      app && app.classList.add("is-collapsed");
    }
  } catch (e) {}

  /* ---------- Sub-menu groups ---------- */
  $$(".nav-group > .nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      const group = link.closest(".nav-group");
      if (!group) return;
      e.preventDefault();
      group.classList.toggle("is-open");
    });
  });

  /* ---------- Theme ---------- */
  const THEME_KEY = "mwst.theme";
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    $$("[data-theme-icon]").forEach((el) => {
      el.setAttribute("href", t === "dark" ? "#i-sun" : "#i-moon");
    });
  }
  let saved = "light";
  try { saved = localStorage.getItem(THEME_KEY) || "light"; } catch (e) {}
  applyTheme(saved);

  $$("[data-toggle-theme]").forEach((b) =>
    b.addEventListener("click", () => {
      const next =
        document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
      window.MWST.redrawCharts();
    })
  );

  /* ---------- Chart.js defaults & factory ---------- */
  const registry = [];

  function baseOptions() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: css("--ink") || "#0f172a",
          titleFont: { family: "Inter", size: 12, weight: "600" },
          bodyFont: { family: "Inter", size: 12 },
          padding: 10,
          cornerRadius: 8,
          displayColors: true,
          boxWidth: 8,
          boxHeight: 8,
          boxPadding: 4,
        },
      },
    };
  }

  function axisOptions() {
    const grid = css("--line-soft") || "#eef2f6";
    const tick = css("--muted") || "#64748b";
    return {
      x: {
        grid: { display: false, drawBorder: false },
        ticks: { color: tick, font: { family: "Inter", size: 10.5 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: grid, drawBorder: false },
        border: { display: false },
        ticks: {
          color: tick,
          font: { family: "Inter", size: 10.5 },
          padding: 6,
          callback: (v) => window.MWST.shortNum(v),
        },
      },
    };
  }

  function make(canvas, cfg) {
    if (!canvas || typeof Chart === "undefined") return null;
    const chart = new Chart(canvas.getContext("2d"), cfg);
    registry.push({ canvas, cfg, chart });
    return chart;
  }

  /* ---------- Public API ---------- */
  window.MWST = {
    $, $$, css,

    shortNum(v) {
      const n = Number(v);
      if (!isFinite(n)) return v;
      const a = Math.abs(n);
      if (a >= 1e9) return (n / 1e9).toFixed(a % 1e9 === 0 ? 0 : 1) + "B";
      if (a >= 1e6) return (n / 1e6).toFixed(a % 1e6 === 0 ? 0 : 1) + "M";
      if (a >= 1e3) return (n / 1e3).toFixed(a % 1e3 === 0 ? 0 : 1) + "K";
      return String(n);
    },

    money(v) {
      return "TZS " + Number(v).toLocaleString("en-US");
    },

    /* Line / area chart — Ukuaji wa Wanachama, Mwenendo wa Michango */
    line(el, labels, series) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const datasets = series.map((s) => {
        const color = s.color || css("--c1");
        let fill = false;
        if (s.fill) {
          const g = canvas.getContext("2d").createLinearGradient(0, 0, 0, canvas.offsetHeight || 220);
          g.addColorStop(0, s.fillTop || "rgba(18,134,74,.20)");
          g.addColorStop(1, "rgba(18,134,74,0)");
          fill = { target: "origin", above: g };
        }
        return {
          label: s.label,
          data: s.data,
          borderColor: color,
          backgroundColor: color,
          borderWidth: 2.4,
          pointRadius: 2.6,
          pointHoverRadius: 5,
          pointBackgroundColor: "#fff",
          pointBorderColor: color,
          pointBorderWidth: 2,
          tension: 0.34,
          fill: s.fill ? fill : false,
        };
      });
      const opts = baseOptions();
      opts.scales = axisOptions();
      return make(canvas, { type: "line", data: { labels, datasets }, options: opts });
    },

    /* Bar chart — Muhtasari wa Mapato */
    bar(el, labels, series) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const datasets = series.map((s) => ({
        label: s.label,
        data: s.data,
        backgroundColor: s.color || css("--c1"),
        borderRadius: 5,
        borderSkipped: false,
        maxBarThickness: 26,
      }));
      const opts = baseOptions();
      opts.scales = axisOptions();
      return make(canvas, { type: "bar", data: { labels, datasets }, options: opts });
    },

    /* Donut — Wanachama kwa Kategoria, Michango kwa Aina */
    donut(el, labels, data, colors, cutout) {
      const canvas = typeof el === "string" ? $(el) : el;
      if (!canvas) return;
      const opts = baseOptions();
      opts.cutout = cutout || "68%";
      opts.plugins.tooltip.callbacks = {
        label: (c) => " " + c.label + ": " + Number(c.raw).toLocaleString("en-US"),
      };
      return make(canvas, {
        type: "doughnut",
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: colors,
            borderWidth: 3,
            borderColor: css("--surface") || "#fff",
            hoverOffset: 6,
          }],
        },
        options: opts,
      });
    },

    redrawCharts() {
      registry.forEach((r) => {
        r.chart.destroy();
        r.chart = new Chart(r.canvas.getContext("2d"), r.cfg);
      });
    },
  };

  /* ---------- Animate progress bars on load ---------- */
  requestAnimationFrame(() => {
    $$("[data-prog]").forEach((el) => {
      el.style.width = el.getAttribute("data-prog") + "%";
    });
  });

  /* ---------- Gauge rings ---------- */
  $$("[data-gauge]").forEach((el) => {
    const pct = Number(el.getAttribute("data-gauge"));
    const circle = $(".gauge__fill", el);
    if (!circle) return;
    const r = circle.r.baseVal.value;
    const c = 2 * Math.PI * r;
    circle.style.strokeDasharray = c;
    circle.style.strokeDashoffset = c;
    requestAnimationFrame(() => {
      circle.style.strokeDashoffset = c - (pct / 100) * c;
    });
  });

  /* ---------- Live clock for topbar date pill ---------- */
  const clock = $("[data-clock]");
  if (clock) {
    const tick = () => {
      const d = new Date();
      clock.textContent = d.toLocaleTimeString("en-GB", {
        hour: "2-digit", minute: "2-digit", second: "2-digit",
      });
    };
    tick();
    setInterval(tick, 1000);
  }
})();

/* ==========================================================================
   BACKEND-PENDING MODAL
   Kila kitu chenye data-backend kinatoa popup nzuri badala ya kufa kimya.
   ========================================================================== */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  const box = document.getElementById("mwst-i18n");
  if (box && window.MWST) {
    try { window.MWST.i18n = JSON.parse(box.textContent); } catch (e) {}
  }
  const T = (window.MWST && window.MWST.i18n) || {};
  const t = (k, fb) => T[k] || fb;

  const scrim = document.createElement("div");
  scrim.className = "modal-scrim";
  scrim.setAttribute("role", "dialog");
  scrim.setAttribute("aria-modal", "true");
  scrim.innerHTML =
    '<div class="modal">' +
      '<div class="modal__top">' +
        '<button class="modal__x" data-close aria-label="Close">' +
          '<svg width="16" height="16"><use href="#i-x-circle"></use></svg></button>' +
        '<div class="modal__badge"><svg><use href="#i-lock"></use></svg></div>' +
        '<div class="modal__eyebrow"></div>' +
        '<div class="modal__title"></div>' +
      "</div>" +
      '<div class="modal__body">' +
        '<p class="modal__text"></p>' +
        '<span class="modal__chip"><svg><use href="#i-info"></use></svg><span></span></span>' +
      "</div>" +
      '<div class="modal__foot">' +
        '<button class="btn btn--ghost" data-close></button>' +
        '<button class="btn btn--primary" data-close></button>' +
      "</div>" +
    "</div>";
  document.body.appendChild(scrim);

  const elEyebrow = $(".modal__eyebrow", scrim);
  const elTitle = $(".modal__title", scrim);
  const elText = $(".modal__text", scrim);
  const elChip = $(".modal__chip span", scrim);
  const btns = $$(".modal__foot .btn", scrim);
  let lastFocus = null;

  function open(feature) {
    elEyebrow.textContent = t("pending_eyebrow", "Inakuja hivi karibuni");
    elTitle.textContent = feature || t("pending_title", "Kipengele hiki");
    elText.textContent = t(
      "backend_pending",
      "Kipengele hiki kitapatikana mfumo wa nyuma (backend) utakapokamilika. " +
      "Kwa sasa unaona muundo na taarifa za mfano."
    );
    elChip.textContent = t("pending_chip", "Muundo umekamilika — data ni ya mfano");
    btns[0].textContent = t("pending_close", "Sawa, nimeelewa");
    btns[1].textContent = t("pending_explore", "Endelea Kutazama");

    lastFocus = document.activeElement;
    scrim.classList.add("is-open");
    document.body.style.overflow = "hidden";
    setTimeout(() => btns[1].focus(), 60);
  }

  function close() {
    scrim.classList.remove("is-open");
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }

  scrim.addEventListener("click", (e) => {
    if (e.target === scrim || e.target.closest("[data-close]")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && scrim.classList.contains("is-open")) close();
  });

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-backend]");
    if (!el) return;
    e.preventDefault();
    open(el.getAttribute("data-backend"));
  });

  if (window.MWST) window.MWST.pending = open;
})();


/* ==========================================================================
   PUBLIC SITE — drawer, counters, reveal, accordion, tabs
   ========================================================================== */
(function () {
  "use strict";
  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  /* ---- Mobile drawer ---- */
  const drawer = $(".drawer");
  const dScrim = $(".drawer-scrim");
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    dScrim && dScrim.classList.toggle("is-open", open);
    document.body.style.overflow = open ? "hidden" : "";
  }
  $$("[data-drawer-open]").forEach((b) => b.addEventListener("click", () => setDrawer(true)));
  $$("[data-drawer-close]").forEach((b) => b.addEventListener("click", () => setDrawer(false)));
  dScrim && dScrim.addEventListener("click", () => setDrawer(false));

  /* ---- Scroll reveal ---- */
  const reveals = $$(".reveal");
  if (reveals.length) {
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => entries.forEach((en, i) => {
          if (!en.isIntersecting) return;
          setTimeout(() => en.target.classList.add("is-in"), (i % 6) * 70);
          io.unobserve(en.target);
        }),
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
      reveals.forEach((r) => io.observe(r));
    } else {
      reveals.forEach((r) => r.classList.add("is-in"));
    }
  }

  /* ---- Counters ---- */
  function animate(el) {
    const target = parseFloat(el.getAttribute("data-count"));
    const suffix = el.getAttribute("data-suffix") || "";
    const dur = 1400;
    const start = performance.now();
    function step(now) {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const v = target * eased;
      el.textContent =
        (target >= 1000 ? Math.round(v).toLocaleString("en-US") : v.toFixed(target % 1 ? 1 : 0)) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const io2 = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { animate(e.target); io2.unobserve(e.target); }
    }), { threshold: 0.4 });
    counters.forEach((c) => io2.observe(c));
  } else {
    counters.forEach(animate);
  }

  /* ---- Accordion ---- */
  $$(".acc__btn").forEach((b) =>
    b.addEventListener("click", () => {
      const item = b.closest(".acc__item");
      const open = item.classList.contains("is-open");
      $$(".acc__item", item.parentElement).forEach((i) => i.classList.remove("is-open"));
      if (!open) item.classList.add("is-open");
    })
  );

  /* ---- Filter tabs ---- */
  $$("[data-tabs]").forEach((group) => {
    const targetSel = group.getAttribute("data-tabs");
    group.addEventListener("click", (e) => {
      const tab = e.target.closest(".tab");
      if (!tab) return;
      $$(".tab", group).forEach((t) => t.classList.remove("is-active"));
      tab.classList.add("is-active");
      const key = tab.getAttribute("data-filter");
      $$(targetSel + " [data-cat]").forEach((card) => {
        const show = key === "all" || card.getAttribute("data-cat") === key;
        card.style.display = show ? "" : "none";
      });
    });
  });

  /* ---- Smooth scroll ---- */
  $$('a[href^="#"]:not([data-backend])').forEach((a) =>
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length < 2) return;
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    })
  );
})();

/* ==========================================================================
   FOMU — onyesha nenosiri, cascading dropdowns
   ========================================================================== */
(function () {
  "use strict";
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));

  /* Onyesha / ficha nenosiri */
  $$("[data-toggle-pw]").forEach((btn) =>
    btn.addEventListener("click", () => {
      const field = btn.closest(".loginfield");
      const input = field && field.querySelector('input[type="password"], input[type="text"]');
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
    })
  );

  /* Mkoa -> Wilaya -> Kata */
  async function fill(select, url, placeholder) {
    select.innerHTML = `<option value="">${placeholder}</option>`;
    if (!url) return;
    try {
      const res = await fetch(url);
      const data = await res.json();
      data.results.forEach((r) => {
        const o = document.createElement("option");
        o.value = r.id;
        o.textContent = r.name;
        select.appendChild(o);
      });
    } catch (e) { /* kimya */ }
  }

  const region = document.querySelector("#id_region");
  const district = document.querySelector("#id_district");
  const ward = document.querySelector("#id_ward");

  if (region && district) {
    region.addEventListener("change", () => {
      fill(district, region.value ? `/api/wilaya/?region=${region.value}` : "", "—");
      if (ward) fill(ward, "", "—");
    });
  }
  if (district && ward) {
    district.addEventListener("change", () => {
      fill(ward, district.value ? `/api/kata/?district=${district.value}` : "", "—");
    });
  }
})();

/* ==========================================================================
   MAPENDELEO YA VIDAKUZI
   Kidirisha kidogo kinachotimiza ahadi iliyo kwenye Sera ya Vidakuzi.
   Uchaguzi unahifadhiwa kwenye localStorage kwa mwaka mmoja.
   ========================================================================== */
(function () {
  "use strict";

  var KEY = "mwst-cookie-consent";
  var MAX_AGE = 365 * 24 * 60 * 60 * 1000;
  var bar = document.getElementById("cookiebar");
  if (!bar) return;

  function read() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || !v.at || Date.now() - v.at > MAX_AGE) return null;
      return v;
    } catch (e) { return null; }
  }

  function show() { bar.hidden = false; requestAnimationFrame(function () { bar.classList.add("is-in"); }); }
  function hide() { bar.classList.remove("is-in"); setTimeout(function () { bar.hidden = true; }, 260); }

  function save(choice) {
    try {
      localStorage.setItem(KEY, JSON.stringify({ choice: choice, at: Date.now() }));
    } catch (e) { /* kivinjari kimezuia hifadhi — tunaendelea tu */ }
    document.documentElement.dataset.cookieConsent = choice;
    hide();
  }

  var saved = read();
  if (saved) {
    document.documentElement.dataset.cookieConsent = saved.choice;
  } else {
    show();
  }

  bar.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-cookie]");
    if (btn) save(btn.getAttribute("data-cookie"));
  });

  // Kitufe cha "Badilisha mapendeleo" kwenye ukurasa wa Sera ya Vidakuzi
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-cookie-reopen]")) {
      try { localStorage.removeItem(KEY); } catch (err) { /* kimya */ }
      delete document.documentElement.dataset.cookieConsent;
      show();
    }
  });
})();

/* ==========================================================================
   UKURASA WA KUINGIA — dokezo la jukumu
   Jukumu ni mwongozo wa maonyesho tu; ruhusa halisi zinatoka kwenye akaunti.
   ========================================================================== */
(function () {
  "use strict";
  var pick = document.querySelector(".rolepick");
  var hint = document.querySelector("[data-role-hint]");
  if (!pick) return;

  pick.addEventListener("change", function (e) {
    var input = e.target.closest("input[name='as']");
    if (!input) return;
    Array.prototype.forEach.call(pick.querySelectorAll(".rolepick__item"), function (el) {
      el.classList.toggle("is-on", el.contains(input));
    });
    if (hint) {
      var label = input.closest(".rolepick__item");
      var text = label && label.getAttribute("data-hint");
      if (text) hint.textContent = text;
    }
  });
})();

/* ==========================================================================
   KICHAGUA LUGHA
   Droplist inatuma fomu mara moja mtu anapochagua — hakuna kubonyeza.
   ========================================================================== */
(function () {
  "use strict";
  document.addEventListener("change", function (e) {
    var select = e.target.closest("[data-langform] select[name='language']");
    if (select) select.form.submit();
  });
})();
