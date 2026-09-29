"""
Maktaba ya muundo wa website: headers (juu na sidebars), footers, fonts na
rangi tayari.

KWA NINI FAILI HILI

Kila website ya mteja ilikuwa na sura moja: navbar ya "glass" na footer
moja. Presets 4 za zamani (nav_presets.py) hazikuwa na CSS ya menyu ya simu,
kwa hiyo kitufe ☰ kilionekana kila mahali. Hapa kuna muundo 14 wa header
(8 za juu, 6 za sidebar) na 12 za footer, zote:

  - zinafuata rangi ya mteja (--accent) na nav nyeusi/nyeupe (--nav-*)
  - zina menyu ya simu inayofanya kazi (jtMenu() ya base.html, #jt-links)
  - ni CSS tupu — hakuna JavaScript wala font ya ziada, zinafunguka haraka

Placeholders ni zile zile za nav_presets.py ({{logo}}, {{nav_links}} ...)
pamoja na mpya: {{cta}}, {{contact_list}}, {{address}}, {{credit}}.

`thumb` ni jina la mchoro mdogo unaoonyeshwa kwenye Studio (studio.html).
"""

# ══════════════════════════════════════════════════════════════
#  CSS YA PAMOJA
# ══════════════════════════════════════════════════════════════

HEADER_COMMON_CSS = """
.hx{z-index:60;font-family:inherit}
.hx a{text-decoration:none}
.hx-brand{display:inline-flex;align-items:center;gap:10px;color:var(--nav-ink);font-weight:800;font-size:18px;
  letter-spacing:-.02em;line-height:1.15;min-width:0}
.hx-brand img{height:34px;width:auto;border-radius:8px;display:block;flex-shrink:0}
.hx-menu{display:flex;align-items:center;gap:4px}
.hx-menu a{color:var(--nav-mut);font-weight:600;font-size:14.5px;transition:color .2s,background .2s,border-color .2s}
.hx-menu a:hover,.hx-menu a.on{color:var(--nav-ink)}
.hx-cta{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--accent);color:#fff!important;
  padding:10px 18px;border-radius:10px;font-weight:700;font-size:14px;white-space:nowrap;transition:filter .2s,transform .2s}
.hx-cta:hover{filter:brightness(1.08);transform:translateY(-1px)}
.hx-burger{display:none;width:42px;height:42px;border:1px solid var(--nav-line);border-radius:10px;background:transparent;
  cursor:pointer;align-items:center;justify-content:center;flex-direction:column;gap:5px;flex-shrink:0}
.hx-burger span,.hx-burger::before,.hx-burger::after{content:"";display:block;width:18px;height:2px;background:var(--nav-ink);border-radius:2px}
.hx-x{display:none}
.hx-dark{--nav-ink:#f4f6fa;--nav-mut:rgba(244,246,250,.68);--nav-solid:#0a0e16;--nav-line:rgba(255,255,255,.12)}
.hx-onaccent{--nav-ink:#fff;--nav-mut:rgba(255,255,255,.84);--nav-solid:var(--accent);--nav-line:rgba(255,255,255,.32)}
.hx-onaccent .hx-cta{background:#fff;color:var(--accent)!important}
@media(max-width:900px){
  /* backdrop-filter inageuza header kuwa "containing block" ya position:fixed —
     menyu ya skrini nzima ingebanwa ndani ya urefu wa header. Kwenye simu: rangi thabiti. */
  .hx{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
  .hx-top_classic,.hx-top_glass,.hx-top_centered,.hx-top_split{background:var(--nav-solid)!important}
  .hx-burger{display:inline-flex}
  .hx .hx-menu{position:fixed;inset:0;z-index:90;flex-direction:column;align-items:stretch;justify-content:center;gap:4px;
    padding:84px 28px 40px;background:var(--nav-solid);opacity:0;visibility:hidden;transition:opacity .25s,visibility .25s}
  .hx .hx-menu.open{opacity:1;visibility:visible}
  .hx nav.hx-menu a{font-size:20px;letter-spacing:normal;text-transform:none;padding:14px 16px;border-radius:12px;
    text-align:center;justify-content:center;border:none!important}
  .hx .hx-menu .hx-cta{margin-top:12px}
  .hx-x{display:block;position:absolute;top:18px;right:20px;width:44px;height:44px;border:none;background:transparent;
    color:var(--nav-ink);font-size:32px;line-height:1;cursor:pointer}
}
"""

# Inaongezwa kwa sidebars pekee — inasogeza maudhui kulia kwenye kompyuta,
# na kugeuza sidebar kuwa bar ya juu kwenye simu.
SIDE_COMMON_CSS = """
.hx-side{position:fixed;top:0;left:0;bottom:0;width:var(--side-w);display:flex;flex-direction:column;gap:26px;
  padding:28px 18px 22px;overflow-y:auto;background:var(--nav-solid);border-right:1px solid var(--nav-line)}
.hx-side .hx-menu{flex-direction:column;align-items:stretch;gap:2px}
.hx-side .hx-menu a{display:block;padding:11px 14px;border-radius:10px}
.hx-side-foot{margin-top:auto;display:flex;flex-direction:column;gap:12px}
.hx-side-meta{font-size:12.5px;color:var(--nav-mut);line-height:1.55}
@media(min-width:901px){.jt-body{margin-left:var(--side-w)}}
@media(max-width:900px){
  .hx-side{position:sticky;bottom:auto;width:auto;flex-direction:row;align-items:center;justify-content:space-between;
    gap:12px;padding:12px 18px;border-right:none;border-bottom:1px solid var(--nav-line);overflow:visible}
  .hx-side-foot{display:none}
}
"""

TOP_HTML = """<header class="hx hx-{key}{extra}">
  <a class="hx-brand" href="/">{{{{logo}}}}<span>{{{{site_name}}}}</span></a>
  <button class="hx-burger" onclick="jtMenu(true)" aria-label="Open menu"><span></span></button>
  <nav class="hx-menu" id="jt-links"><button class="hx-x" onclick="jtMenu(false)" aria-label="Close menu">&times;</button>{{{{nav_links}}}}{cta}</nav>
</header>"""

SIDE_HTML = """<aside class="hx hx-side hx-{key}{extra}">
  <a class="hx-brand" href="/">{{{{logo}}}}<span>{{{{site_name}}}}</span></a>
  <button class="hx-burger" onclick="jtMenu(true)" aria-label="Open menu"><span></span></button>
  <nav class="hx-menu" id="jt-links"><button class="hx-x" onclick="jtMenu(false)" aria-label="Close menu">&times;</button>{{{{nav_links}}}}</nav>
  <div class="hx-side-foot">{{{{tagline_meta}}}}{{{{cta}}}}</div>
</aside>"""


def _top(key, extra='', cta=True):
    return TOP_HTML.format(key=key, extra=extra, cta='{{cta}}' if cta else '')


def _side(key, extra=''):
    return SIDE_HTML.format(key=key, extra=extra)


# ══════════════════════════════════════════════════════════════
#  HEADERS — 8 za juu, 6 za sidebar
# ══════════════════════════════════════════════════════════════

HEADERS = {
    # ── Sidebars (ya kwanza ndiyo default ya site mpya) ──
    'side_classic': {
        'name': 'Sidebar Classic', 'kind': 'side', 'thumb': 'side-light',
        'desc': 'Clean left sidebar with an active marker — calm and professional',
        'html': _side('side_classic'),
        'css': """:root{--side-w:264px}
.hx-side_classic .hx-brand{font-size:19px;padding:0 6px}
.hx-side_classic .hx-menu a{position:relative}
.hx-side_classic .hx-menu a:hover{background:color-mix(in srgb,var(--nav-ink) 6%,transparent)}
.hx-side_classic .hx-menu a.on{background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--nav-ink)}
.hx-side_classic .hx-menu a.on::before{content:"";position:absolute;left:0;top:10px;bottom:10px;width:3px;border-radius:3px;background:var(--accent)}""",
    },
    'side_midnight': {
        'name': 'Sidebar Midnight', 'kind': 'side', 'thumb': 'side-dark',
        'desc': 'Deep dark sidebar with a soft accent glow — premium SaaS look',
        'html': _side('side_midnight', ' hx-dark'),
        'css': """:root{--side-w:272px}
.hx-side_midnight{background:linear-gradient(180deg,#0b1020,#070a14);border-right:1px solid rgba(255,255,255,.06)}
.hx-side_midnight .hx-brand{font-size:19px;padding:0 6px}
.hx-side_midnight .hx-menu a:hover{background:rgba(255,255,255,.05)}
.hx-side_midnight .hx-menu a.on{background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 28%,transparent),transparent);
  color:#fff;box-shadow:inset 2px 0 0 var(--accent)}
.hx-side_midnight .hx-cta{box-shadow:0 8px 24px color-mix(in srgb,var(--accent) 40%,transparent)}""",
    },
    'side_accent': {
        'name': 'Sidebar Brand Color', 'kind': 'side', 'thumb': 'side-accent',
        'desc': 'Your brand color fills the sidebar — bold and memorable',
        'html': _side('side_accent', ' hx-onaccent'),
        'css': """:root{--side-w:260px}
.hx-side_accent{background:var(--accent);border-right:none}
.hx-side_accent .hx-brand{font-size:20px;padding:0 6px}
.hx-side_accent .hx-menu a:hover{background:rgba(255,255,255,.14)}
.hx-side_accent .hx-menu a.on{background:#fff;color:var(--accent)}""",
    },
    'side_slim': {
        'name': 'Slim Sidebar', 'kind': 'side', 'thumb': 'side-slim',
        'desc': 'Narrow sidebar with small uppercase links — minimal and modern',
        'html': _side('side_slim'),
        'css': """:root{--side-w:216px}
.hx-side_slim{padding:30px 14px 20px;gap:34px}
.hx-side_slim .hx-brand{font-size:16px;flex-direction:column;align-items:flex-start;gap:12px}
.hx-side_slim .hx-menu a{font-size:12px;letter-spacing:.14em;text-transform:uppercase;padding:10px 12px;display:flex;align-items:center;gap:10px}
.hx-side_slim .hx-menu a::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--nav-line);transition:background .2s}
.hx-side_slim .hx-menu a:hover::before,.hx-side_slim .hx-menu a.on::before{background:var(--accent)}
.hx-side_slim .hx-cta{font-size:13px;padding:9px 12px}
@media(max-width:900px){.hx-side_slim .hx-brand{flex-direction:row}.hx-side_slim .hx-menu a{justify-content:center}}""",
    },
    'side_floating': {
        'name': 'Floating Card Sidebar', 'kind': 'side', 'thumb': 'side-float',
        'desc': 'Sidebar floats as a rounded card with a soft shadow',
        'html': _side('side_floating'),
        'css': """:root{--side-w:292px}
@media(min-width:901px){
  .hx-side_floating{top:16px;left:16px;bottom:16px;width:calc(var(--side-w) - 32px);border-radius:22px;
    border:1px solid var(--nav-line);box-shadow:0 20px 60px rgba(15,23,42,.12)}
}
.hx-side_floating .hx-brand{font-size:19px;padding:0 6px}
.hx-side_floating .hx-menu a:hover{background:color-mix(in srgb,var(--nav-ink) 6%,transparent)}
.hx-side_floating .hx-menu a.on{background:var(--accent);color:#fff}""",
    },
    'side_editorial': {
        'name': 'Editorial Sidebar', 'kind': 'side', 'thumb': 'side-editorial',
        'desc': 'Magazine-style serif brand and large links on warm paper',
        'html': _side('side_editorial'),
        'css': """:root{--side-w:300px}
.hx-side_editorial{background:#f7f3ec;--nav-ink:#1b1712;--nav-mut:#6d6254;--nav-solid:#f7f3ec;--nav-line:#e6dccd;padding:40px 28px 28px}
.hx-side_editorial .hx-brand{font-family:Georgia,'Times New Roman',serif;font-size:28px;font-weight:700;letter-spacing:-.01em}
.hx-side_editorial .hx-menu{gap:0}
.hx-side_editorial .hx-menu a{font-family:Georgia,'Times New Roman',serif;font-size:20px;font-weight:400;padding:12px 0;
  border-radius:0;border-bottom:1px solid var(--nav-line)}
.hx-side_editorial .hx-menu a:hover,.hx-side_editorial .hx-menu a.on{color:var(--accent);padding-left:6px}
.hx-side_editorial .hx-cta{border-radius:0}""",
    },

    # ── Za juu ──
    'top_classic': {
        'name': 'Classic Bar', 'kind': 'top', 'thumb': 'bar',
        'desc': 'Logo left, menu right, clean hairline — the timeless choice',
        'html': _top('top_classic'),
        'css': """.hx-top_classic{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;gap:20px;
  padding:14px clamp(16px,4vw,40px);background:var(--nav-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--nav-line)}
.hx-top_classic .hx-menu a{padding:9px 14px;border-radius:9px}
.hx-top_classic .hx-menu a:hover,.hx-top_classic .hx-menu a.on{background:color-mix(in srgb,var(--accent) 14%,transparent)}
.hx-top_classic .hx-cta{margin-left:10px}""",
    },
    'top_glass': {
        'name': 'Floating Glass', 'kind': 'top', 'thumb': 'float',
        'desc': 'Rounded glass bar that floats above your content',
        'html': _top('top_glass'),
        'css': """.hx-top_glass{position:sticky;top:14px;margin:14px auto 0;width:min(1120px,calc(100% - 24px));display:flex;align-items:center;
  justify-content:space-between;gap:18px;padding:10px 12px 10px 20px;background:var(--nav-bg);backdrop-filter:blur(20px) saturate(1.4);
  -webkit-backdrop-filter:blur(20px) saturate(1.4);border:1px solid var(--nav-line);border-radius:18px;box-shadow:0 12px 40px rgba(15,23,42,.14)}
.hx-top_glass .hx-menu a{padding:9px 14px;border-radius:999px}
.hx-top_glass .hx-menu a:hover,.hx-top_glass .hx-menu a.on{background:color-mix(in srgb,var(--nav-ink) 8%,transparent)}
.hx-top_glass .hx-cta{border-radius:12px;margin-left:8px}""",
    },
    'top_centered': {
        'name': 'Centered Brand', 'kind': 'top', 'thumb': 'center',
        'desc': 'Logo on top in the middle, menu centered below — elegant',
        'html': _top('top_centered', cta=False),
        'css': """.hx-top_centered{position:sticky;top:0;display:flex;flex-direction:column;align-items:center;gap:12px;
  padding:22px clamp(16px,4vw,40px) 12px;background:var(--nav-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--nav-line);text-align:center}
.hx-top_centered .hx-brand{font-size:24px}
.hx-top_centered .hx-menu{gap:26px}
.hx-top_centered .hx-menu a{padding:6px 0;border-bottom:2px solid transparent;font-size:14px;letter-spacing:.02em}
.hx-top_centered .hx-menu a:hover,.hx-top_centered .hx-menu a.on{border-bottom-color:var(--accent)}
@media(max-width:900px){.hx-top_centered{flex-direction:row;justify-content:space-between;padding:14px 18px}
  .hx-top_centered .hx-brand{font-size:19px}}""",
    },
    'top_split': {
        'name': 'Split Luxury', 'kind': 'top', 'thumb': 'split',
        'desc': 'Menu left, logo center, contact button right — boutique style',
        'html': """<header class="hx hx-top_split">
  <nav class="hx-menu" id="jt-links"><button class="hx-x" onclick="jtMenu(false)" aria-label="Close menu">&times;</button>{{nav_links}}</nav>
  <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <div class="hx-split-end">{{cta}}<button class="hx-burger" onclick="jtMenu(true)" aria-label="Open menu"><span></span></button></div>
</header>""",
        'css': """.hx-top_split{position:sticky;top:0;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:20px;
  padding:16px clamp(16px,4vw,44px);background:var(--nav-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-bottom:1px solid var(--nav-line)}
.hx-top_split .hx-brand{font-size:21px;letter-spacing:.04em;text-transform:uppercase;justify-self:center}
.hx-top_split .hx-menu{gap:22px}
.hx-top_split .hx-menu a{font-size:13px;letter-spacing:.12em;text-transform:uppercase}
.hx-top_split .hx-split-end{justify-self:end;display:flex;align-items:center;gap:10px}
.hx-top_split .hx-cta{border-radius:0;letter-spacing:.08em;text-transform:uppercase;font-size:12.5px;padding:11px 20px}
@media(max-width:900px){.hx-top_split{grid-template-columns:1fr auto}.hx-top_split .hx-brand{justify-self:start;font-size:17px}
  .hx-top_split .hx-split-end .hx-cta{display:none}}""",
    },
    'top_accent': {
        'name': 'Brand Color Bar', 'kind': 'top', 'thumb': 'accent',
        'desc': 'Full-width bar in your brand color with a white button',
        'html': _top('top_accent', ' hx-onaccent'),
        'css': """.hx-top_accent{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;gap:20px;
  padding:14px clamp(16px,4vw,40px);background:var(--accent);box-shadow:0 4px 20px color-mix(in srgb,var(--accent) 35%,transparent)}
.hx-top_accent .hx-menu a{padding:9px 14px;border-radius:9px}
.hx-top_accent .hx-menu a:hover,.hx-top_accent .hx-menu a.on{background:rgba(255,255,255,.16);color:#fff}
.hx-top_accent .hx-cta{margin-left:10px}""",
    },
    'top_minimal': {
        'name': 'Minimal Line', 'kind': 'top', 'thumb': 'minimal',
        'desc': 'Quiet solid bar, just type and a thin underline on hover',
        'html': _top('top_minimal', cta=False),
        'css': """.hx-top_minimal{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:24px clamp(16px,5vw,56px);
  background:var(--nav-solid)}
.hx-top_minimal .hx-menu{gap:28px}
.hx-top_minimal .hx-menu a{padding:4px 0;border-bottom:1px solid transparent;font-weight:500}
.hx-top_minimal .hx-menu a:hover,.hx-top_minimal .hx-menu a.on{border-bottom-color:var(--nav-ink);color:var(--nav-ink)}""",
    },
    'top_corporate': {
        'name': 'Corporate + Contact Strip', 'kind': 'top', 'thumb': 'strip',
        'desc': 'Thin strip with phone and email above a solid menu bar',
        'html': """<header class="hx hx-top_corporate">
  <div class="hx-strip"><span>{{phone_inline}}{{email_inline}}</span><span>{{tagline}}</span></div>
  <div class="hx-bar">
    <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
    <button class="hx-burger" onclick="jtMenu(true)" aria-label="Open menu"><span></span></button>
    <nav class="hx-menu" id="jt-links"><button class="hx-x" onclick="jtMenu(false)" aria-label="Close menu">&times;</button>{{nav_links}}{{cta}}</nav>
  </div>
</header>""",
        'css': """.hx-top_corporate{position:sticky;top:0}
.hx-top_corporate .hx-strip{display:flex;justify-content:space-between;gap:16px;padding:7px clamp(16px,4vw,40px);
  background:color-mix(in srgb,var(--accent) 88%,#000);color:#fff;font-size:12.5px;font-weight:500}
.hx-top_corporate .hx-strip span{display:flex;gap:18px;flex-wrap:wrap}
.hx-top_corporate .hx-bar{display:flex;align-items:center;justify-content:space-between;gap:20px;
  padding:14px clamp(16px,4vw,40px);background:var(--nav-solid);border-bottom:1px solid var(--nav-line);
  box-shadow:0 2px 14px rgba(15,23,42,.06)}
.hx-top_corporate .hx-menu a{padding:9px 14px;border-radius:8px}
.hx-top_corporate .hx-menu a:hover,.hx-top_corporate .hx-menu a.on{color:var(--accent)}
.hx-top_corporate .hx-cta{margin-left:10px;border-radius:8px}
@media(max-width:900px){.hx-top_corporate .hx-strip span:last-child{display:none}}""",
    },
    'top_midnight': {
        'name': 'Midnight Premium', 'kind': 'top', 'thumb': 'dark',
        'desc': 'Always-dark bar with a glowing gradient edge — tech & luxury',
        'html': _top('top_midnight', ' hx-dark'),
        'css': """.hx-top_midnight{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;gap:20px;
  padding:15px clamp(16px,4vw,40px);background:rgba(8,11,20,.86);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.hx-top_midnight::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:.7}
.hx-top_midnight .hx-menu a{padding:9px 14px;border-radius:9px}
.hx-top_midnight .hx-menu a:hover,.hx-top_midnight .hx-menu a.on{color:#fff;background:rgba(255,255,255,.06)}
.hx-top_midnight .hx-cta{margin-left:10px;background:linear-gradient(135deg,var(--accent),color-mix(in srgb,var(--accent) 55%,#7c3aed));
  box-shadow:0 8px 26px color-mix(in srgb,var(--accent) 38%,transparent)}""",
    },
}


# ══════════════════════════════════════════════════════════════
#  FOOTERS — 12
# ══════════════════════════════════════════════════════════════

FOOTER_COMMON_CSS = """
.fx{margin-top:80px;font-size:14.5px;line-height:1.65}
.fx a{text-decoration:none;color:inherit;transition:color .2s,opacity .2s}
.fx-wrap{max-width:1160px;margin:0 auto;padding:0 clamp(18px,4vw,40px)}
.fx-brand{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:20px;letter-spacing:-.02em}
.fx-brand img{height:36px;width:auto;border-radius:8px}
.fx h4{font-size:12px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 16px;font-weight:700}
.fx-links{display:flex;flex-direction:column;gap:9px}
.fx-contact{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:9px}
.fx-contact b{display:block;font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;opacity:.6}
.fx-cta{display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:#fff!important;padding:12px 22px;
  border-radius:10px;font-weight:700;white-space:nowrap;transition:filter .2s,transform .2s}
.fx-cta:hover{filter:brightness(1.08);transform:translateY(-1px)}
.fx-credit{font-size:12.5px;opacity:.7}
.fx-credit a{text-decoration:underline;text-underline-offset:3px}
.fx-dark{background:#0b0f16;color:#9aa6b4}.fx-dark .fx-brand,.fx-dark h4{color:#f3f5f8}
.fx-dark a:hover{color:#fff}
.fx-light{background:#f6f7f9;color:#5b6675;border-top:1px solid #e6e9ee}.fx-light .fx-brand,.fx-light h4{color:#0f172a}
.fx-light a:hover{color:var(--accent)}
"""

FOOTERS = {
    'f_columns': {
        'name': 'Four Columns', 'thumb': 'cols',
        'desc': 'Brand, pages, contact and a call-to-action — the business standard',
        'html': """<footer class="fx fx-dark fx-f_columns"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p></div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
    <div><h4>Get started</h4><p>Talk to us today — we reply fast.</p>{{cta_footer}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span><span class="fx-credit">{{credit}}</span></div>
</div></footer>""",
        'css': """.fx-f_columns{padding:72px 0 28px}
.fx-f_columns .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr 1.2fr;gap:40px}
.fx-f_columns .fx-about{margin:14px 0 0;max-width:300px}
.fx-f_columns .fx-cta{margin-top:14px}
.fx-f_columns .fx-bottom{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:56px;padding-top:24px;
  border-top:1px solid rgba(255,255,255,.08);font-size:13px}
@media(max-width:900px){.fx-f_columns .fx-grid{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.fx-f_columns .fx-grid{grid-template-columns:1fr;gap:30px}}""",
    },
    'f_cta_band': {
        'name': 'Call-to-Action Band', 'thumb': 'cta',
        'desc': 'Big "ready to start?" banner in your brand color, then links',
        'html': """<footer class="fx fx-f_cta_band">
  <div class="fx-band"><div class="fx-wrap fx-band-in">
    <div><h3>Ready to work with {{site_name}}?</h3><p>{{tagline}}</p></div>{{cta_footer}}
  </div></div>
  <div class="fx-dark fx-lower"><div class="fx-wrap fx-lower-in">
    <a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
    <div class="fx-row">{{nav_links}}</div>
    <span class="fx-credit">&copy; {{year}} · {{credit}}</span>
  </div></div>
</footer>""",
        'css': """.fx-f_cta_band .fx-band{background:var(--accent);color:#fff;padding:64px 0}
.fx-f_cta_band .fx-band-in{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap}
.fx-f_cta_band h3{font-size:clamp(26px,3.6vw,38px);letter-spacing:-.02em;line-height:1.15;margin:0 0 6px;color:#fff}
.fx-f_cta_band .fx-band p{margin:0;opacity:.88}
.fx-f_cta_band .fx-band .fx-cta{background:#fff;color:var(--accent)!important;padding:15px 30px;font-size:15px}
.fx-f_cta_band .fx-lower{padding:30px 0}
.fx-f_cta_band .fx-lower-in{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.fx-f_cta_band .fx-row{display:flex;gap:22px;flex-wrap:wrap}""",
    },
    'f_mega': {
        'name': 'Mega Dark', 'thumb': 'mega',
        'desc': 'Huge brand name watermark over rich dark columns — high-end',
        'html': """<footer class="fx fx-dark fx-f_mega"><div class="fx-wrap">
  <div class="fx-top">
    <div class="fx-lead"><h3>{{tagline_or_name}}</h3>{{cta_footer}}</div>
    <div><h4>Explore</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Reach us</h4>{{contact_list}}</div>
  </div>
  <div class="fx-mark">{{site_name}}</div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}</span><span class="fx-credit">{{credit}}</span></div>
</div></footer>""",
        'css': """.fx-f_mega{padding:84px 0 26px;background:radial-gradient(1200px 400px at 20% 0%,color-mix(in srgb,var(--accent) 16%,transparent),transparent),#07090f;overflow:hidden}
.fx-f_mega .fx-top{display:grid;grid-template-columns:2fr 1fr 1.2fr;gap:44px}
.fx-f_mega h3{color:#fff;font-size:clamp(24px,3vw,34px);line-height:1.2;letter-spacing:-.02em;margin:0 0 22px;max-width:460px}
.fx-f_mega .fx-mark{font-size:clamp(56px,13vw,180px);font-weight:900;letter-spacing:-.05em;line-height:.9;margin:64px 0 20px;
  color:transparent;-webkit-text-stroke:1px rgba(255,255,255,.14);white-space:nowrap;overflow:hidden;text-overflow:clip}
.fx-f_mega .fx-bottom{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:13px}
@media(max-width:820px){.fx-f_mega .fx-top{grid-template-columns:1fr;gap:32px}}""",
    },
    'f_centered': {
        'name': 'Centered', 'thumb': 'center',
        'desc': 'Logo, links and contact stacked in the middle — friendly',
        'html': """<footer class="fx fx-light fx-f_centered"><div class="fx-wrap">
  <a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <p class="fx-tag">{{tagline}}</p>
  <div class="fx-row">{{nav_links}}</div>
  <div class="fx-row fx-small">{{phone_inline}}{{email_inline}}</div>
  <div class="fx-credit">&copy; {{year}} {{site_name}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_centered{padding:64px 0 34px;text-align:center}
.fx-f_centered .fx-tag{margin:10px auto 0;max-width:520px}
.fx-f_centered .fx-row{display:flex;justify-content:center;gap:24px;flex-wrap:wrap;margin-top:24px;font-weight:600;color:#1e293b}
.fx-f_centered .fx-small{font-weight:500;color:inherit;margin-top:14px;font-size:14px}
.fx-f_centered .fx-credit{margin-top:30px}""",
    },
    'f_minimal': {
        'name': 'Minimal Line', 'thumb': 'line',
        'desc': 'One quiet line: name, links, copyright',
        'html': """<footer class="fx fx-f_minimal"><div class="fx-wrap fx-in">
  <span class="fx-name">{{site_name}}</span>
  <div class="fx-row">{{nav_links}}</div>
  <span class="fx-credit">&copy; {{year}} · {{credit}}</span>
</div></footer>""",
        'css': """.fx-f_minimal{padding:28px 0;border-top:1px solid color-mix(in srgb,currentColor 14%,transparent);color:#586271}
.fx-f_minimal .fx-in{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.fx-f_minimal .fx-name{font-weight:800;color:#0f172a}
.fx-f_minimal .fx-row{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}
.fx-f_minimal a:hover{color:var(--accent)}""",
    },
    'f_split': {
        'name': 'Split Contact Card', 'thumb': 'split',
        'desc': 'Brand story on the left, a contact card on the right',
        'html': """<footer class="fx fx-light fx-f_split"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p>{{tagline}}</p><div class="fx-row">{{nav_links}}</div></div>
    <div class="fx-card"><h4>Let's talk</h4>{{contact_list}}{{cta_footer}}</div>
  </div>
  <div class="fx-credit fx-bottom">&copy; {{year}} {{site_name}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_split{padding:72px 0 30px}
.fx-f_split .fx-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:48px;align-items:start}
.fx-f_split p{margin:14px 0 22px;max-width:440px}
.fx-f_split .fx-row{display:flex;gap:20px;flex-wrap:wrap;font-weight:600;color:#1e293b}
.fx-f_split .fx-card{background:#fff;border:1px solid #e6e9ee;border-radius:18px;padding:28px;box-shadow:0 20px 50px rgba(15,23,42,.07)}
.fx-f_split .fx-card .fx-cta{margin-top:18px;width:100%}
.fx-f_split .fx-bottom{margin-top:44px}
@media(max-width:820px){.fx-f_split .fx-grid{grid-template-columns:1fr}}""",
    },
    'f_accent': {
        'name': 'Brand Color', 'thumb': 'accent',
        'desc': 'Whole footer in your brand color with white text',
        'html': """<footer class="fx fx-f_accent"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p>{{tagline}}</p></div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom fx-credit">&copy; {{year}} {{site_name}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_accent{background:var(--accent);color:rgba(255,255,255,.86);padding:68px 0 28px}
.fx-f_accent .fx-brand,.fx-f_accent h4{color:#fff}
.fx-f_accent .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr;gap:40px}
.fx-f_accent p{margin:12px 0 0;max-width:340px}
.fx-f_accent a:hover{color:#fff;opacity:.8}
.fx-f_accent .fx-bottom{margin-top:48px;padding-top:22px;border-top:1px solid rgba(255,255,255,.22)}
@media(max-width:820px){.fx-f_accent .fx-grid{grid-template-columns:1fr;gap:28px}}""",
    },
    'f_cards': {
        'name': 'Contact Cards', 'thumb': 'cards',
        'desc': 'Three large tap-to-contact cards — perfect for mobile customers',
        'html': """<footer class="fx fx-light fx-f_cards"><div class="fx-wrap">
  <h3>Get in touch with {{site_name}}</h3>
  <div class="fx-cardrow">{{contact_cards}}</div>
  <div class="fx-bottom"><div class="fx-row">{{nav_links}}</div><span class="fx-credit">&copy; {{year}} · {{credit}}</span></div>
</div></footer>""",
        'css': """.fx-f_cards{padding:72px 0 30px}
.fx-f_cards h3{color:#0f172a;font-size:clamp(24px,3vw,32px);letter-spacing:-.02em;margin:0 0 26px;text-align:center}
.fx-f_cards .fx-cardrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}
.fx-f_cards .fx-ccard{display:block;background:#fff;border:1px solid #e6e9ee;border-radius:16px;padding:22px 24px;
  transition:transform .2s,box-shadow .2s,border-color .2s}
.fx-f_cards .fx-ccard:hover{transform:translateY(-3px);border-color:var(--accent);box-shadow:0 16px 40px rgba(15,23,42,.08)}
.fx-f_cards .fx-ccard b{display:block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
.fx-f_cards .fx-ccard span{color:#0f172a;font-weight:700;font-size:16px;word-break:break-word}
.fx-f_cards .fx-bottom{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:44px;padding-top:22px;border-top:1px solid #e6e9ee}
.fx-f_cards .fx-row{display:flex;gap:20px;flex-wrap:wrap;font-weight:600;color:#1e293b}""",
    },
    'f_editorial': {
        'name': 'Editorial', 'thumb': 'editorial',
        'desc': 'Large serif name and refined fine print — magazine elegance',
        'html': """<footer class="fx fx-f_editorial"><div class="fx-wrap">
  <div class="fx-name">{{site_name}}</div>
  <div class="fx-grid">
    <p>{{tagline}}</p>
    <div class="fx-links">{{nav_links}}</div>
    {{contact_list}}
  </div>
  <div class="fx-credit">&copy; {{year}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_editorial{background:#f7f3ec;color:#6d6254;padding:76px 0 30px;border-top:1px solid #e6dccd}
.fx-f_editorial .fx-name{font-family:Georgia,'Times New Roman',serif;font-size:clamp(40px,7vw,84px);color:#1b1712;
  letter-spacing:-.02em;line-height:1;padding-bottom:30px;border-bottom:1px solid #e6dccd}
.fx-f_editorial .fx-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:40px;padding:34px 0}
.fx-f_editorial p{margin:0;font-family:Georgia,'Times New Roman',serif;font-size:18px;color:#3a322a;max-width:380px}
.fx-f_editorial a:hover{color:var(--accent)}
@media(max-width:820px){.fx-f_editorial .fx-grid{grid-template-columns:1fr;gap:24px}}""",
    },
    'f_simple': {
        'name': 'Simple Dark', 'thumb': 'simple',
        'desc': 'Compact dark footer: name, contact and credit on one row',
        'html': """<footer class="fx fx-dark fx-f_simple"><div class="fx-wrap fx-in">
  <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><div class="fx-tag">{{tagline}}</div></div>
  <div class="fx-row">{{phone_inline}}{{email_inline}}</div>
  <span class="fx-credit">&copy; {{year}} · {{credit}}</span>
</div></footer>""",
        'css': """.fx-f_simple{padding:40px 0}
.fx-f_simple .fx-in{display:flex;align-items:center;justify-content:space-between;gap:22px;flex-wrap:wrap}
.fx-f_simple .fx-brand{font-size:17px}
.fx-f_simple .fx-tag{font-size:13px;margin-top:2px}
.fx-f_simple .fx-row{display:flex;gap:18px;flex-wrap:wrap}""",
    },
    'f_gradient': {
        'name': 'Gradient Glow', 'thumb': 'gradient',
        'desc': 'Deep gradient from your brand color into night — modern tech',
        'html': """<footer class="fx fx-f_gradient"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p>{{tagline}}</p>{{cta_footer}}</div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom fx-credit">&copy; {{year}} {{site_name}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_gradient{background:linear-gradient(160deg,color-mix(in srgb,var(--accent) 70%,#0b1020) 0%,#0b1020 62%);
  color:rgba(255,255,255,.76);padding:76px 0 28px}
.fx-f_gradient .fx-brand,.fx-f_gradient h4{color:#fff}
.fx-f_gradient .fx-grid{display:grid;grid-template-columns:1.8fr 1fr 1.2fr;gap:44px}
.fx-f_gradient p{margin:12px 0 20px;max-width:360px}
.fx-f_gradient .fx-cta{background:#fff;color:#0b1020!important}
.fx-f_gradient a:hover{color:#fff}
.fx-f_gradient .fx-bottom{margin-top:52px;padding-top:22px;border-top:1px solid rgba(255,255,255,.12)}
@media(max-width:820px){.fx-f_gradient .fx-grid{grid-template-columns:1fr;gap:28px}}""",
    },
    'f_stacked': {
        'name': 'Stacked Links', 'thumb': 'stacked',
        'desc': 'Big stacked page links with arrows — bold and mobile-first',
        'html': """<footer class="fx fx-dark fx-f_stacked"><div class="fx-wrap">
  <div class="fx-grid">
    <div class="fx-big">{{nav_links}}</div>
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p>{{tagline}}</p>{{contact_list}}</div>
  </div>
  <div class="fx-bottom fx-credit">&copy; {{year}} {{site_name}} · {{credit}}</div>
</div></footer>""",
        'css': """.fx-f_stacked{padding:72px 0 28px}
.fx-f_stacked .fx-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:56px;align-items:start}
.fx-f_stacked .fx-big{display:flex;flex-direction:column}
.fx-f_stacked .fx-big a{display:flex;justify-content:space-between;align-items:center;font-size:clamp(22px,3vw,34px);font-weight:700;
  color:#f3f5f8;letter-spacing:-.02em;padding:14px 0;border-bottom:1px solid rgba(255,255,255,.08)}
.fx-f_stacked .fx-big a::after{content:"\\2197";font-size:.7em;opacity:.4;transition:opacity .2s,transform .2s}
.fx-f_stacked .fx-big a:hover{color:var(--accent)}
.fx-f_stacked .fx-big a:hover::after{opacity:1;transform:translate(3px,-3px)}
.fx-f_stacked p{margin:12px 0 22px}
.fx-f_stacked .fx-bottom{margin-top:52px}
@media(max-width:820px){.fx-f_stacked .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
}

DEFAULT_HEADER = 'side_classic'
DEFAULT_FOOTER = 'f_columns'


# ══════════════════════════════════════════════════════════════
#  FONTS NA RANGI
# ══════════════════════════════════════════════════════════════

# (jina, query ya Google Fonts au None, font ya maandishi, font ya vichwa)
# 'system' haipakii chochote — ndiyo ya haraka zaidi, na ndiyo default.
FONTS = {
    'system': ('System (fastest)', None,
               "-apple-system,'Segoe UI',Roboto,Arial,sans-serif", None),
    'inter': ('Inter — clean', 'Inter:wght@400;600;800', "'Inter',sans-serif", None),
    'poppins': ('Poppins — friendly', 'Poppins:wght@400;600;800', "'Poppins',sans-serif", None),
    'montserrat': ('Montserrat — bold', 'Montserrat:wght@400;600;800', "'Montserrat',sans-serif", None),
    'dm_sans': ('DM Sans — modern', 'DM+Sans:wght@400;600;800', "'DM Sans',sans-serif", None),
    'playfair': ('Playfair + Inter — luxury', 'Playfair+Display:wght@600;800&family=Inter:wght@400;600',
                 "'Inter',sans-serif", "'Playfair Display',Georgia,serif"),
    'lora': ('Lora + Source Sans — editorial', 'Lora:wght@600;700&family=Source+Sans+3:wght@400;600',
             "'Source Sans 3',sans-serif", "'Lora',Georgia,serif"),
}

# Rangi tayari: (jina, accent, nav nyeusi?)
PALETTES = [
    ('Ocean', '#2563eb', False),
    ('Emerald', '#059669', False),
    ('Safari Gold', '#d97706', True),
    ('Royal', '#7c3aed', True),
    ('Coral', '#e11d48', False),
    ('Teal', '#0d9488', True),
    ('Midnight', '#0ea5e9', True),
    ('Graphite', '#334155', False),
    ('Sunset', '#ea580c', False),
    ('Forest', '#15803d', True),
]


def font_for(site, override=None):
    """(href ya Google Fonts au '', font ya maandishi, font ya vichwa)."""
    key = override or (site.theme_settings or {}).get('font') or 'system'
    _, query, body, head = FONTS.get(key, FONTS['system'])
    href = f'https://fonts.googleapis.com/css2?family={query}&display=swap' if query else ''
    return href, body, head or body
