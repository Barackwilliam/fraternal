"""
Maktaba ya muundo wa website: headers (juu na sidebars), footers, fonts na
rangi tayari.

KWA NINI FAILI HILI

Kila website ya mteja ilikuwa na sura moja: navbar ya "glass" na footer
moja. Hapa kuna muundo 14 wa header (8 za juu, 6 za sidebar) na 16 za
footer, zote:

  - zinafuata rangi ya mteja (--accent) na nav nyeusi/nyeupe (--nav-*)
  - zina menyu ya simu inayofanya kazi (jtMenu() ya base.html, #jt-links)
  - ni CSS tupu — hakuna JavaScript wala font ya ziada, zinafunguka haraka

MENYU YA SIMU

Zamani kila header ilifungua menyu ile ile: skrini nzima, links katikati.
Sasa kuna mitindo 6 (MOBILE_MENUS): sidebar ya kushoto inayoteleza, drawer
ya kulia, bottom sheet, kadi ya dropdown, skrini nzima na tab bar ya chini
kama app. Kila header ina mtindo wake wa kawaida ('mobile'), na mteja
anaweza kuchagua mwingine kwenye Studio (theme_settings['mobile_menu']).
Menyu ina kichwa (logo + ✕), links zenye namba na mshale, kitufe cha
mawasiliano, na njia za mkato za simu/WhatsApp/email chini.

Placeholders ni zile zile za nav_presets.py ({{logo}}, {{nav_links}} ...)
pamoja na {{cta}}, {{contact_list}}, {{m_contact}}, {{mm}} (class ya mtindo
wa menyu ya simu).

`thumb` ni jina la mchoro mdogo unaoonyeshwa kwenye Studio (studio.html).
"""

# ══════════════════════════════════════════════════════════════
#  MENYU YA SIMU — mitindo 6
# ══════════════════════════════════════════════════════════════

# key: (jina, maelezo) — key inakuwa class hx-m-<key> kwenye header
MOBILE_MENUS = {
    'left': ('Side drawer', 'Slides in from the left like a real sidebar'),
    'right': ('Right drawer', 'Panel slides in from the right'),
    'sheet': ('Bottom sheet', 'Rises from the bottom — easy to reach with a thumb'),
    'drop': ('Floating card', 'A rounded card drops down from the top'),
    'full': ('Full screen', 'Big bold links fill the whole screen'),
    'tabs': ('App tab bar', 'Links always visible at the bottom, like an app'),
}


def mobile_menu_for(site, header_key):
    """Mtindo wa menyu ya simu: chaguo la mteja, au wa kawaida wa header."""
    choice = (site.theme_settings or {}).get('mobile_menu', '')
    if choice in MOBILE_MENUS:
        return choice
    return HEADERS.get(header_key, {}).get('mobile', 'right')


# ══════════════════════════════════════════════════════════════
#  CSS YA PAMOJA
# ══════════════════════════════════════════════════════════════

HEADER_COMMON_CSS = """
.hx{z-index:60;font-family:inherit;--m-ease:cubic-bezier(.32,.72,0,1)}
.hx a{text-decoration:none}
.hx-brand{display:inline-flex;align-items:center;gap:10px;color:var(--nav-ink);font-weight:800;font-size:18px;
  letter-spacing:-.02em;line-height:1.15;min-width:0}
.hx-brand img{height:34px;width:auto;border-radius:8px;display:block;flex-shrink:0}
.hx-menu{display:flex;align-items:center;gap:4px}
.hx-mlinks{display:contents}
.hx-mhead,.hx-mfoot,.hx-scrim,.hx-x{display:none}
.hx-menu a{color:var(--nav-mut);font-weight:600;font-size:14.5px;transition:color .2s,background .2s,border-color .2s}
.hx-menu a:hover,.hx-menu a.on{color:var(--nav-ink)}
.hx-cta{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--accent);color:#fff!important;
  padding:10px 18px;border-radius:10px;font-weight:700;font-size:14px;white-space:nowrap;transition:filter .2s,transform .2s}
.hx-cta:hover{filter:brightness(1.08);transform:translateY(-1px)}
.hx-burger{display:none;width:44px;height:44px;border:1px solid var(--nav-line);border-radius:12px;background:transparent;
  cursor:pointer;align-items:center;justify-content:center;flex-direction:column;gap:5px;flex-shrink:0;padding:0}
.hx-burger span,.hx-burger::before,.hx-burger::after{content:"";display:block;width:18px;height:2px;background:var(--nav-ink);
  border-radius:2px;transition:width .25s}
.hx-burger::after{width:12px;margin-left:6px}
.hx-burger:hover::after{width:18px;margin-left:0}
.hx-dark{--nav-ink:#f4f6fa;--nav-mut:rgba(244,246,250,.68);--nav-solid:#0a0e16;--nav-line:rgba(255,255,255,.12)}
.hx-onaccent{--nav-ink:#fff;--nav-mut:rgba(255,255,255,.84);--nav-solid:var(--accent);--nav-line:rgba(255,255,255,.32)}
.hx-onaccent .hx-cta{background:#fff;color:var(--accent)!important}
@media(max-width:900px){
  /* backdrop-filter inageuza header kuwa "containing block" ya position:fixed —
     menyu ingebanwa ndani ya urefu wa header. Kwenye simu: rangi thabiti. */
  .hx{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
  .hx-top_classic,.hx-top_glass,.hx-top_centered,.hx-top_split{background:var(--nav-solid)!important}
  .hx-burger{display:inline-flex}

  /* ── Paneli ya menyu (ya pamoja kwa mitindo yote) ── */
  .hx nav.hx-menu{position:fixed;z-index:90;display:flex;flex-direction:column;align-items:stretch;justify-content:flex-start;gap:0;
    margin:0;padding:0;background:var(--nav-solid);color:var(--nav-ink);overflow-y:auto;overscroll-behavior:contain;
    visibility:hidden;box-shadow:0 30px 80px rgba(3,6,14,.35);
    transition:transform .5s var(--m-ease),opacity .35s ease,visibility 0s linear .5s}
  .hx .hx-menu.open{visibility:visible;transition:transform .5s var(--m-ease),opacity .35s ease,visibility 0s}
  .hx .hx-mhead{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px 16px 16px 22px;
    border-bottom:1px solid var(--nav-line);flex-shrink:0}
  /* Kichwa cha menyu kinarithi mitindo ya "a" ya header husika — virudishe */
  .hx .hx-menu .hx-mhead .hx-brand{display:inline-flex;padding:0;border:none!important;background:none;font-size:17px;
    font-weight:800;letter-spacing:-.02em;text-transform:none;font-family:inherit;color:var(--nav-ink)}
  .hx .hx-menu .hx-mhead .hx-brand img{height:30px}
  .hx .hx-menu .hx-mhead a::before,.hx .hx-menu .hx-mhead a::after,.hx nav.hx-menu .hx-mfoot a::before,
  .hx nav.hx-menu .hx-mfoot a::after,.hx nav.hx-menu .hx-cta::before,.hx nav.hx-menu .hx-cta::after{content:none}
  .hx .hx-x{display:inline-flex;position:relative;width:42px;height:42px;border-radius:50%;border:1px solid var(--nav-line);
    background:color-mix(in srgb,var(--nav-ink) 6%,transparent);cursor:pointer;flex-shrink:0;padding:0}
  .hx .hx-x::before,.hx .hx-x::after{content:"";position:absolute;left:50%;top:50%;width:16px;height:2px;border-radius:2px;
    background:var(--nav-ink);transform:translate(-50%,-50%) rotate(45deg)}
  .hx .hx-x::after{transform:translate(-50%,-50%) rotate(-45deg)}
  .hx .hx-mlinks{display:flex;flex-direction:column;gap:2px;padding:14px 12px;counter-reset:m}
  .hx nav.hx-menu .hx-mlinks a{counter-increment:m;display:flex;align-items:center;gap:14px;padding:15px 14px;border-radius:14px;
    font-size:17px;font-weight:600;line-height:1.3;color:var(--nav-ink);background:none;border:none!important;text-align:left;
    justify-content:flex-start;letter-spacing:-.01em;text-transform:none;font-family:inherit;box-shadow:none;
    opacity:0;transform:translateX(14px);transition:opacity .4s ease,transform .5s var(--m-ease),background .2s}
  .hx nav.hx-menu .hx-mlinks a::before{content:counter(m,decimal-leading-zero);width:22px;height:auto;flex-shrink:0;
    background:none;border-radius:0;font-size:11.5px;font-weight:700;letter-spacing:.04em;color:var(--nav-mut);
    font-variant-numeric:tabular-nums;position:static;transform:none;opacity:1}
  .hx nav.hx-menu .hx-mlinks a::after{content:"";margin-left:auto;width:8px;height:8px;flex-shrink:0;
    border-top:2px solid currentColor;border-right:2px solid currentColor;transform:rotate(45deg);opacity:.3;
    position:static;background:none}
  .hx nav.hx-menu .hx-mlinks a:active{background:color-mix(in srgb,var(--nav-ink) 7%,transparent)}
  .hx nav.hx-menu .hx-mlinks a.on{background:color-mix(in srgb,var(--accent) 16%,transparent);color:var(--nav-ink)}
  .hx nav.hx-menu .hx-mlinks a.on::before{color:var(--accent)}
  .hx nav.hx-menu .hx-mlinks a.on::after{opacity:.8;color:var(--accent)}
  .hx-onaccent nav.hx-menu .hx-mlinks a.on{background:rgba(255,255,255,.2)}
  .hx-onaccent nav.hx-menu .hx-mlinks a.on::before,.hx-onaccent nav.hx-menu .hx-mlinks a.on::after{color:#fff}
  .hx .hx-menu.open .hx-mlinks a{opacity:1;transform:none}
  .hx .hx-menu.open .hx-mlinks a:nth-child(2){transition-delay:.04s}.hx .hx-menu.open .hx-mlinks a:nth-child(3){transition-delay:.08s}
  .hx .hx-menu.open .hx-mlinks a:nth-child(4){transition-delay:.12s}.hx .hx-menu.open .hx-mlinks a:nth-child(5){transition-delay:.16s}
  .hx .hx-menu.open .hx-mlinks a:nth-child(6){transition-delay:.2s}.hx .hx-menu.open .hx-mlinks a:nth-child(n+7){transition-delay:.24s}
  .hx nav.hx-menu .hx-cta{display:flex;margin:8px 22px 0;padding:15px 20px;border-radius:14px;font-size:15.5px;
    letter-spacing:normal;text-transform:none;font-family:inherit}
  .hx .hx-mfoot{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto;padding:22px 22px calc(24px + env(safe-area-inset-bottom))}
  .hx .hx-mfoot:empty{display:none}
  .hx nav.hx-menu .hx-mfoot a{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:999px;
    border:1px solid var(--nav-line);font-size:13px;font-weight:600;color:var(--nav-ink);letter-spacing:normal;text-transform:none;
    font-family:inherit;
    background:color-mix(in srgb,var(--nav-ink) 4%,transparent)}
  .hx .hx-mfoot svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .hx .hx-scrim{display:block;position:fixed;inset:0;z-index:85;background:rgba(5,8,15,.55);
    -webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);opacity:0;visibility:hidden;
    transition:opacity .4s ease,visibility 0s linear .4s}
  html.jt-menu-open .hx .hx-scrim{opacity:1;visibility:visible;transition:opacity .4s ease,visibility 0s}
  html.jt-menu-open,html.jt-menu-open body{overflow:hidden}

  /* ── 1. Sidebar ya kushoto ── */
  .hx-m-left nav.hx-menu{top:0;bottom:0;left:0;width:min(86vw,360px);border-radius:0 24px 24px 0;transform:translateX(-104%)}
  .hx-m-left nav.hx-menu.open{transform:none}
  .hx-m-left nav.hx-menu .hx-mlinks a{transform:translateX(-14px)}
  /* ── 2. Drawer ya kulia ── */
  .hx-m-right nav.hx-menu{top:0;bottom:0;right:0;width:min(88vw,380px);border-radius:24px 0 0 24px;transform:translateX(104%)}
  .hx-m-right nav.hx-menu.open{transform:none}
  /* ── 3. Bottom sheet ── */
  .hx-m-sheet nav.hx-menu{left:0;right:0;bottom:0;max-height:86vh;max-height:86dvh;border-radius:26px 26px 0 0;transform:translateY(104%)}
  .hx-m-sheet nav.hx-menu.open{transform:none}
  .hx-m-sheet .hx-mhead{position:relative;padding-top:26px}
  .hx-m-sheet .hx-mhead::before{content:"";position:absolute;top:9px;left:50%;width:40px;height:5px;margin-left:-20px;
    border-radius:5px;background:var(--nav-line)}
  .hx-m-sheet nav.hx-menu .hx-mlinks a{transform:translateY(12px)}
  /* ── 4. Kadi inayoshuka kutoka juu ── */
  .hx-m-drop nav.hx-menu{top:10px;left:10px;right:10px;max-height:calc(100vh - 20px);max-height:calc(100dvh - 20px);
    border-radius:24px;border:1px solid var(--nav-line);transform:translateY(-16px) scale(.97);transform-origin:top center;opacity:0}
  .hx-m-drop nav.hx-menu.open{transform:none;opacity:1}
  .hx-m-drop nav.hx-menu .hx-mlinks a{transform:translateY(-8px)}
  /* ── 5. Skrini nzima ── */
  .hx-m-full nav.hx-menu{inset:0;opacity:0;transform:scale(1.03);box-shadow:none;
    background:radial-gradient(600px 380px at 100% 0%,color-mix(in srgb,var(--accent) 22%,transparent),transparent 70%),var(--nav-solid)}
  .hx-m-full nav.hx-menu.open{opacity:1;transform:none}
  .hx-m-full .hx-mhead{border-bottom:none}
  .hx-m-full .hx-mlinks{padding:18px 22px;gap:0}
  .hx-m-full nav.hx-menu .hx-mlinks a{font-size:clamp(28px,8.5vw,40px);font-weight:800;letter-spacing:-.03em;padding:12px 0;
    border-radius:0;border-bottom:1px solid var(--nav-line)!important;transform:translateY(22px)}
  .hx-m-full nav.hx-menu .hx-mlinks a::before{align-self:flex-start;margin-top:.55em}
  .hx-m-full nav.hx-menu .hx-mlinks a.on{background:none;color:var(--accent)}
  /* ── 6. Tab bar ya chini kama app — links zinaonekana daima ── */
  .hx-m-tabs .hx-burger{display:none!important}
  .hx-m-tabs nav.hx-menu{visibility:visible;top:auto;left:10px;right:10px;bottom:calc(10px + env(safe-area-inset-bottom));
    flex-direction:row;border-radius:20px;border:1px solid var(--nav-line);padding:6px;overflow-x:auto;scrollbar-width:none;
    transform:none;box-shadow:0 12px 40px rgba(3,6,14,.28)}
  .hx-m-tabs nav.hx-menu::-webkit-scrollbar{display:none}
  .hx-m-tabs .hx-mhead,.hx-m-tabs .hx-mfoot,.hx-m-tabs nav.hx-menu .hx-cta,.hx-m-tabs .hx-scrim{display:none!important}
  .hx-m-tabs .hx-mlinks{flex-direction:row;padding:0;gap:4px;flex:1}
  .hx-m-tabs nav.hx-menu .hx-mlinks a{flex:1 0 auto;flex-direction:column;justify-content:center;gap:4px;padding:9px 12px;
    border-radius:14px;font-size:12px;font-weight:700;text-align:center;white-space:nowrap;opacity:1;transform:none}
  .hx-m-tabs nav.hx-menu .hx-mlinks a::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--nav-line);margin:0}
  .hx-m-tabs nav.hx-menu .hx-mlinks a.on::before{background:var(--accent)}
  .hx-m-tabs.hx-onaccent nav.hx-menu .hx-mlinks a.on::before{background:#fff}
  .hx-m-tabs nav.hx-menu .hx-mlinks a::after{display:none}
  body:has(.hx-m-tabs) .jt-body{padding-bottom:86px}
}
@media(prefers-reduced-motion:reduce){.hx .hx-menu,.hx nav.hx-menu .hx-mlinks a{transition:none!important}}
"""

# Inaongezwa kwa sidebars pekee — inasogeza maudhui kulia kwenye kompyuta,
# na kugeuza sidebar kuwa bar ya juu kwenye simu (menyu inateleza kama sidebar).
SIDE_COMMON_CSS = """
.hx-side{position:fixed;top:0;left:0;bottom:0;width:var(--side-w);display:flex;flex-direction:column;gap:26px;
  padding:28px 18px 22px;overflow-y:auto;background:var(--nav-solid);border-right:1px solid var(--nav-line)}
.hx-side .hx-menu{flex-direction:column;align-items:stretch;gap:2px}
.hx-side .hx-menu a{display:block;padding:11px 14px;border-radius:10px}
.hx-side-foot{margin-top:auto;display:flex;flex-direction:column;gap:12px}
.hx-side-meta{font-size:12.5px;color:var(--nav-mut);line-height:1.55}
@media(min-width:901px){.jt-body{margin-left:var(--side-w)}.hx-side nav.hx-menu .hx-cta{display:none}}
@media(max-width:900px){
  .hx-side{position:sticky;bottom:auto;width:auto;flex-direction:row;align-items:center;justify-content:space-between;
    gap:12px;padding:12px 18px;border-right:none;border-bottom:1px solid var(--nav-line);overflow:visible}
  .hx-side-foot{display:none}
}
"""

MENU_HTML = """<nav class="hx-menu" id="jt-links" aria-label="Main menu">
    <div class="hx-mhead"><a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><button class="hx-x" type="button" onclick="jtMenu(false)" aria-label="Close menu"></button></div>
    <div class="hx-mlinks">{{nav_links}}</div>@CTA@
    <div class="hx-mfoot">{{m_contact}}</div>
  </nav>"""

BURGER_HTML = ('<button class="hx-burger" type="button" onclick="jtMenu(true)" aria-label="Open menu" '
               'aria-controls="jt-links" aria-expanded="false"><span></span></button>')
SCRIM_HTML = '<div class="hx-scrim" onclick="jtMenu(false)"></div>'

TOP_HTML = """<header class="hx hx-@KEY@@EXTRA@ {{mm}}">
  <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  @BURGER@
  @MENU@
  @SCRIM@
</header>"""

SIDE_HTML = """<aside class="hx hx-side hx-@KEY@@EXTRA@ {{mm}}">
  <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  @BURGER@
  @MENU@
  <div class="hx-side-foot">{{tagline_meta}}{{cta}}</div>
  @SCRIM@
</aside>"""


def _menu(cta=True):
    return MENU_HTML.replace('@CTA@', '{{cta}}' if cta else '')


def _build(tpl, key, extra='', cta=True):
    for token, value in (('@KEY@', key), ('@EXTRA@', extra), ('@BURGER@', BURGER_HTML),
                         ('@MENU@', _menu(cta)), ('@SCRIM@', SCRIM_HTML)):
        tpl = tpl.replace(token, value)
    return tpl


def _top(key, extra='', cta=True):
    return _build(TOP_HTML, key, extra, cta)


def _side(key, extra=''):
    return _build(SIDE_HTML, key, extra, cta=True)


# ══════════════════════════════════════════════════════════════
#  HEADERS — 8 za juu, 6 za sidebar
# ══════════════════════════════════════════════════════════════

HEADERS = {
    # ── Sidebars (ya kwanza ndiyo default ya site mpya) ──
    'side_classic': {
        'mobile': 'left',
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
        'mobile': 'left',
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
        'mobile': 'left',
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
        'mobile': 'left',
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
        'mobile': 'left',
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
        'mobile': 'full',
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
        'mobile': 'right',
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
        'mobile': 'drop',
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
        'mobile': 'sheet',
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
        'mobile': 'full',
        'name': 'Split Luxury', 'kind': 'top', 'thumb': 'split',
        'desc': 'Menu left, logo center, contact button right — boutique style',
        'html': """<header class="hx hx-top_split {{mm}}">
  """ + _menu(cta=False) + """
  <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <div class="hx-split-end">{{cta}}""" + BURGER_HTML + """</div>
  """ + SCRIM_HTML + """
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
        'mobile': 'right',
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
        'mobile': 'drop',
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
        'mobile': 'right',
        'name': 'Corporate + Contact Strip', 'kind': 'top', 'thumb': 'strip',
        'desc': 'Thin strip with phone and email above a solid menu bar',
        'html': """<header class="hx hx-top_corporate {{mm}}">
  <div class="hx-strip"><span>{{phone_inline}}{{email_inline}}</span><span>{{tagline}}</span></div>
  <div class="hx-bar">
    <a class="hx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
    """ + BURGER_HTML + """
    """ + _menu() + """
  </div>
  """ + SCRIM_HTML + """
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
        'mobile': 'full',
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
#  FOOTERS — 16
# ══════════════════════════════════════════════════════════════
# Hakuna footer yenye "Built with JamiiTek": alama ya JamiiTek inaongezwa
# na server chini ya kila ukurasa (builder/branding.py), mteja hawezi kuiondoa.

FOOTER_COMMON_CSS = """
.fx{--fx-ink:#0f172a;--fx-mut:#5b6675;--fx-line:#e5e8ee;position:relative;margin-top:88px;font-size:15px;line-height:1.7;color:var(--fx-mut)}
.fx a{text-decoration:none;color:inherit;transition:color .2s,opacity .2s,background .2s,border-color .2s,transform .2s}
.fx-wrap{max-width:1200px;margin:0 auto;padding:0 clamp(20px,4vw,48px)}
.fx .fx-brand{display:inline-flex;align-items:center;gap:12px;font-weight:800;font-size:22px;letter-spacing:-.02em;color:var(--fx-ink)}
.fx-brand img{height:40px;width:auto;border-radius:10px}
.fx h3{font-family:var(--font-head,inherit);color:var(--fx-ink);font-weight:800;letter-spacing:-.03em;line-height:1.1;margin:0}
.fx h4{font-size:12px;letter-spacing:.16em;text-transform:uppercase;margin:0 0 20px;font-weight:700;color:var(--fx-ink)}
.fx p{margin:0}
.fx-about{margin-top:16px!important;max-width:340px}
.fx-links{display:flex;flex-direction:column;gap:12px}
.fx-links a{display:inline-flex;align-items:center;gap:8px;width:fit-content}
.fx-links a:hover{color:var(--fx-ink);transform:translateX(3px)}
.fx-row{display:flex;flex-wrap:wrap;gap:10px 26px}
.fx-row a:hover{color:var(--fx-ink)}
.fx-contact{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:14px}
.fx-contact b{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;opacity:.65;margin-bottom:1px}
.fx-contact a,.fx-contact span{color:var(--fx-ink);font-weight:600;word-break:break-word}
.fx-contact a:hover{color:var(--accent)}
.fx-icons{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.fx-icons a{width:44px;height:44px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
  border:1px solid var(--fx-line);color:var(--fx-ink)}
.fx-icons a:hover{background:var(--accent);border-color:var(--accent);color:#fff;transform:translateY(-2px)}
.fx svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}
.fx-cta{display:inline-flex;align-items:center;justify-content:center;gap:10px;background:var(--accent);color:#fff!important;
  padding:15px 28px;border-radius:12px;font-weight:700;font-size:15px;white-space:nowrap;
  box-shadow:0 12px 30px color-mix(in srgb,var(--accent) 30%,transparent)}
.fx-cta:hover{filter:brightness(1.08);transform:translateY(-2px)}
.fx-cta::after{content:"\\2192";transition:transform .2s}
.fx-cta:hover::after{transform:translateX(3px)}
.fx-ghost{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:14px 26px;border-radius:12px;
  font-weight:700;font-size:15px;border:1.5px solid currentColor;white-space:nowrap}
.fx-ghost:hover{transform:translateY(-2px)}
.fx-btns{display:flex;flex-wrap:wrap;gap:12px}
.fx-bottom{display:flex;justify-content:space-between;align-items:center;gap:14px 24px;flex-wrap:wrap;margin-top:72px;padding:26px 0 30px;
  border-top:1px solid var(--fx-line);font-size:13.5px}
.fx .fx-totop{display:inline-flex;align-items:center;gap:8px;font-weight:600;color:var(--fx-ink)}
.fx-totop::after{content:"\\2191";display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;
  border:1px solid var(--fx-line);transition:transform .2s}
.fx-totop:hover::after{transform:translateY(-3px)}
.fx .fx-big{display:inline-block;font-weight:800;letter-spacing:-.03em;color:var(--fx-ink);border-bottom:2px solid var(--accent);
  line-height:1.15;word-break:break-word}
.fx .fx-big:hover{color:var(--accent)}
.fx-dark{--fx-ink:#f4f6fa;--fx-mut:#9aa5b4;--fx-line:rgba(255,255,255,.1);background:#0a0d14;color:var(--fx-mut)}
.fx-light{--fx-ink:#0f172a;--fx-mut:#5b6675;--fx-line:#e5e8ee;background:#f7f8fa;border-top:1px solid #e9ecf1;color:var(--fx-mut)}
@media(max-width:900px){.fx{margin-top:64px}.fx-bottom{margin-top:52px}}
@media(max-width:560px){.fx-btns>a{flex:1 1 100%}}
"""

FOOTERS = {
    'f_columns': {
        'name': 'Four Columns', 'thumb': 'cols',
        'desc': 'Brand, pages, contact and a project card — the business standard',
        'html': """<footer class="fx fx-dark fx-f_columns"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p>{{contact_icons}}</div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
    <div class="fx-card"><h4>Start today</h4><p>Tell us what you need — we reply fast, usually within the hour.</p>{{cta_footer}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_columns{padding-top:96px}
.fx-f_columns .fx-grid{display:grid;grid-template-columns:1.5fr 1fr 1.2fr 1.4fr;gap:48px}
.fx-f_columns .fx-card{background:rgba(255,255,255,.04);border:1px solid var(--fx-line);border-radius:20px;padding:26px}
.fx-f_columns .fx-card .fx-cta{margin-top:20px;width:100%}
@media(max-width:1000px){.fx-f_columns .fx-grid{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.fx-f_columns .fx-grid{grid-template-columns:1fr;gap:40px}}""",
    },
    'f_cta_band': {
        'name': 'Call-to-Action Band', 'thumb': 'cta',
        'desc': 'Big "ready to start?" banner in your brand color, then full links',
        'html': """<footer class="fx fx-f_cta_band">
  <div class="fx-band"><div class="fx-wrap fx-band-in">
    <div><h3>Ready to work with {{site_name}}?</h3><p>{{tagline_or_name}} — talk to us today and get a fast answer.</p></div>
    <div class="fx-btns">{{cta_footer}}{{cta_ghost}}</div>
  </div></div>
  <div class="fx-dark fx-lower"><div class="fx-wrap">
    <div class="fx-grid">
      <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p></div>
      <div><h4>Explore</h4><div class="fx-links">{{nav_links}}</div></div>
      <div><h4>Contact</h4>{{contact_list}}</div>
    </div>
    <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}</span>{{to_top}}</div>
  </div></div>
</footer>""",
        'css': """.fx-f_cta_band .fx-band{background:radial-gradient(900px 300px at 85% 0%,rgba(255,255,255,.18),transparent 70%),var(--accent);color:#fff;padding:88px 0}
.fx-f_cta_band .fx-band-in{display:flex;align-items:center;justify-content:space-between;gap:32px;flex-wrap:wrap}
.fx-f_cta_band .fx-band h3{font-size:clamp(30px,4.4vw,52px);color:#fff;margin-bottom:12px;max-width:640px}
.fx-f_cta_band .fx-band p{opacity:.9;font-size:17px;max-width:560px}
.fx-f_cta_band .fx-band .fx-cta{background:#fff;color:var(--accent)!important;box-shadow:0 14px 34px rgba(0,0,0,.18)}
.fx-f_cta_band .fx-band .fx-ghost{color:#fff}
.fx-f_cta_band .fx-lower{padding-top:80px}
.fx-f_cta_band .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr;gap:48px}
@media(max-width:820px){.fx-f_cta_band .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
    'f_mega': {
        'name': 'Mega Dark', 'thumb': 'mega',
        'desc': 'Huge outlined brand name over rich dark columns — high-end',
        'html': """<footer class="fx fx-dark fx-f_mega"><div class="fx-wrap">
  <div class="fx-top">
    <div class="fx-lead"><h3>{{tagline_or_name}}</h3><div class="fx-btns">{{cta_footer}}</div>{{contact_icons}}</div>
    <div><h4>Explore</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Reach us</h4>{{contact_list}}</div>
  </div>
  <div class="fx-mark" aria-hidden="true">{{site_name}}</div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_mega{padding-top:110px;overflow:hidden;
  background:radial-gradient(1100px 460px at 12% 0%,color-mix(in srgb,var(--accent) 22%,transparent),transparent 70%),#06080d}
.fx-f_mega .fx-top{display:grid;grid-template-columns:2fr 1fr 1.2fr;gap:56px}
.fx-f_mega h3{font-size:clamp(30px,3.8vw,48px);margin-bottom:30px;max-width:520px}
.fx-f_mega .fx-mark{font-size:clamp(64px,15vw,210px);font-weight:900;letter-spacing:-.05em;line-height:.85;margin:90px 0 0;
  color:transparent;-webkit-text-stroke:1px rgba(255,255,255,.16);white-space:nowrap;overflow:hidden}
.fx-f_mega .fx-bottom{margin-top:30px}
@media(max-width:860px){.fx-f_mega .fx-top{grid-template-columns:1fr;gap:40px}}""",
    },
    'f_centered': {
        'name': 'Centered', 'thumb': 'center',
        'desc': 'Logo, links and contact icons stacked in the middle — friendly',
        'html': """<footer class="fx fx-light fx-f_centered"><div class="fx-wrap">
  <a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <p class="fx-tag">{{tagline}}</p>
  <div class="fx-pills">{{nav_links}}</div>
  {{contact_icons}}
  <div class="fx-row fx-small">{{phone_inline}}{{email_inline}}</div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_centered{padding-top:96px;text-align:center}
.fx-f_centered .fx-brand{font-size:28px}.fx-f_centered .fx-brand img{height:48px}
.fx-f_centered .fx-tag{margin:14px auto 0;max-width:560px;font-size:17px}
.fx-f_centered .fx-pills{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-top:34px}
.fx-f_centered .fx-pills a{padding:10px 18px;border-radius:999px;background:#fff;border:1px solid var(--fx-line);font-weight:600;color:var(--fx-ink)}
.fx-f_centered .fx-pills a:hover{border-color:var(--accent);color:var(--accent)}
.fx-f_centered .fx-icons{justify-content:center;margin-top:30px}
.fx-f_centered .fx-small{justify-content:center;margin-top:18px;font-size:14px}
.fx-f_centered .fx-bottom{justify-content:center;flex-direction:column}""",
    },
    'f_minimal': {
        'name': 'Minimal', 'thumb': 'line',
        'desc': 'Quiet and airy: name and tagline left, links right',
        'html': """<footer class="fx fx-f_minimal"><div class="fx-wrap">
  <div class="fx-in">
    <div><div class="fx-name">{{site_name}}</div><p>{{tagline}}</p></div>
    <div class="fx-row">{{nav_links}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}</span><div class="fx-row">{{phone_inline}}{{email_inline}}</div></div>
</div></footer>""",
        'css': """.fx-f_minimal{padding-top:64px;border-top:1px solid var(--fx-line);background:#fff}
.fx-f_minimal .fx-in{display:flex;align-items:flex-end;justify-content:space-between;gap:28px;flex-wrap:wrap}
.fx-f_minimal .fx-name{font-weight:800;font-size:26px;letter-spacing:-.03em;color:var(--fx-ink);margin-bottom:6px}
.fx-f_minimal .fx-row{font-weight:600}
.fx-f_minimal .fx-bottom{margin-top:48px}
.fx-f_minimal a:hover{color:var(--accent)}""",
    },
    'f_split': {
        'name': 'Split Contact Card', 'thumb': 'split',
        'desc': 'Brand story on the left, a floating contact card on the right',
        'html': """<footer class="fx fx-light fx-f_split"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><h3>{{tagline_or_name}}</h3><div class="fx-row">{{nav_links}}</div></div>
    <div class="fx-card"><h4>Let's talk</h4>{{contact_list}}{{cta_footer}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_split{padding-top:100px}
.fx-f_split .fx-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:64px;align-items:start}
.fx-f_split h3{font-size:clamp(28px,3.4vw,42px);margin:26px 0 30px;max-width:520px}
.fx-f_split .fx-row{font-weight:600;color:var(--fx-ink)}
.fx-f_split .fx-card{background:#fff;border:1px solid var(--fx-line);border-radius:24px;padding:34px;box-shadow:0 30px 70px rgba(15,23,42,.09)}
.fx-f_split .fx-card .fx-cta{margin-top:26px;width:100%}
@media(max-width:860px){.fx-f_split .fx-grid{grid-template-columns:1fr;gap:40px}}""",
    },
    'f_accent': {
        'name': 'Brand Color', 'thumb': 'accent',
        'desc': 'Whole footer in your brand color with a bold headline',
        'html': """<footer class="fx fx-f_accent"><div class="fx-wrap">
  <div class="fx-head"><h3>{{tagline_or_name}}</h3>{{cta_footer}}</div>
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>{{contact_icons}}</div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_accent{--fx-ink:#fff;--fx-mut:rgba(255,255,255,.82);--fx-line:rgba(255,255,255,.24);background:var(--accent);padding-top:96px}
.fx-f_accent .fx-head{display:flex;align-items:flex-end;justify-content:space-between;gap:28px;flex-wrap:wrap;
  padding-bottom:56px;margin-bottom:56px;border-bottom:1px solid var(--fx-line)}
.fx-f_accent h3{font-size:clamp(30px,4.2vw,52px);max-width:680px}
.fx-f_accent .fx-cta{background:#fff;color:var(--accent)!important;box-shadow:0 14px 34px rgba(0,0,0,.16)}
.fx-f_accent .fx-contact a:hover,.fx-f_accent .fx-links a:hover{color:#fff;opacity:.8}
.fx-f_accent .fx-icons a:hover{background:#fff;color:var(--accent);border-color:#fff}
.fx-f_accent .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr;gap:48px}
@media(max-width:820px){.fx-f_accent .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
    'f_cards': {
        'name': 'Contact Cards', 'thumb': 'cards',
        'desc': 'Large tap-to-contact cards — perfect for mobile customers',
        'html': """<footer class="fx fx-light fx-f_cards"><div class="fx-wrap">
  <div class="fx-head"><span class="fx-kicker">Contact</span><h3>Get in touch with {{site_name}}</h3><p>{{tagline}}</p></div>
  <div class="fx-cardrow">{{contact_cards}}</div>
  <div class="fx-bottom"><div class="fx-row">{{nav_links}}</div><span>&copy; {{year}} {{site_name}}</span></div>
</div></footer>""",
        'css': """.fx-f_cards{padding-top:100px}
.fx-f_cards .fx-head{text-align:center;max-width:640px;margin:0 auto 48px}
.fx-f_cards .fx-kicker{display:inline-block;font-size:12px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.fx-f_cards h3{font-size:clamp(30px,4vw,48px);margin-bottom:12px}
.fx-f_cards .fx-cardrow{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}
.fx-f_cards .fx-ccard{display:flex;flex-direction:column;gap:14px;background:#fff;border:1px solid var(--fx-line);border-radius:22px;padding:28px}
.fx-f_cards a.fx-ccard:hover{transform:translateY(-4px);border-color:var(--accent);box-shadow:0 24px 50px rgba(15,23,42,.09)}
.fx-f_cards .fx-ccard i{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;
  background:color-mix(in srgb,var(--accent) 12%,#fff);color:var(--accent)}
.fx-f_cards .fx-ccard svg{width:22px;height:22px}
.fx-f_cards .fx-ccard b{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--fx-mut)}
.fx-f_cards .fx-ccard span{color:var(--fx-ink);font-weight:700;font-size:17px;word-break:break-word;margin-top:-8px}
.fx-f_cards .fx-row{font-weight:600;color:var(--fx-ink)}""",
    },
    'f_editorial': {
        'name': 'Editorial', 'thumb': 'editorial',
        'desc': 'Large serif name and refined fine print — magazine elegance',
        'html': """<footer class="fx fx-f_editorial"><div class="fx-wrap">
  <div class="fx-name">{{site_name}}</div>
  <div class="fx-grid">
    <p>{{tagline}}</p>
    <div><h4>Index</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Correspondence</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_editorial{--fx-ink:#1b1712;--fx-mut:#6d6254;--fx-line:#e2d7c5;background:#f7f3ec;padding-top:100px}
.fx-f_editorial .fx-name{font-family:Georgia,'Times New Roman',serif;font-size:clamp(52px,9vw,120px);color:var(--fx-ink);
  letter-spacing:-.03em;line-height:.95;padding-bottom:40px;border-bottom:1px solid var(--fx-line)}
.fx-f_editorial .fx-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:48px;padding-top:44px}
.fx-f_editorial p{font-family:Georgia,'Times New Roman',serif;font-size:21px;line-height:1.5;color:#3a322a;max-width:420px}
.fx-f_editorial h4{font-family:Georgia,'Times New Roman',serif;font-style:italic;text-transform:none;letter-spacing:0;font-size:15px;font-weight:400}
.fx-f_editorial a:hover{color:var(--accent)}
@media(max-width:820px){.fx-f_editorial .fx-grid{grid-template-columns:1fr;gap:32px}}""",
    },
    'f_simple': {
        'name': 'Simple Dark', 'thumb': 'simple',
        'desc': 'Compact dark footer with icons and a contact button',
        'html': """<footer class="fx fx-dark fx-f_simple"><div class="fx-wrap">
  <div class="fx-in">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p></div>
    <div class="fx-end">{{contact_icons}}{{cta_footer}}</div>
  </div>
  <div class="fx-bottom"><div class="fx-row">{{nav_links}}</div><span>&copy; {{year}} {{site_name}}</span></div>
</div></footer>""",
        'css': """.fx-f_simple{padding-top:72px}
.fx-f_simple .fx-in{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap}
.fx-f_simple .fx-end{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.fx-f_simple .fx-icons{margin:0}
.fx-f_simple .fx-bottom{margin-top:48px}""",
    },
    'f_gradient': {
        'name': 'Gradient Glow', 'thumb': 'gradient',
        'desc': 'Deep gradient from your brand color into night — modern tech',
        'html': """<footer class="fx fx-f_gradient"><div class="fx-wrap">
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p>
      <div class="fx-btns">{{cta_footer}}</div>{{contact_icons}}</div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_gradient{--fx-ink:#fff;--fx-mut:rgba(255,255,255,.72);--fx-line:rgba(255,255,255,.12);padding-top:104px;
  background:radial-gradient(700px 360px at 90% 10%,color-mix(in srgb,var(--accent) 35%,transparent),transparent 70%),
  linear-gradient(160deg,color-mix(in srgb,var(--accent) 60%,#0b1020) 0%,#0b1020 58%)}
.fx-f_gradient .fx-grid{display:grid;grid-template-columns:1.8fr 1fr 1.2fr;gap:56px}
.fx-f_gradient .fx-btns{margin-top:26px}
.fx-f_gradient .fx-cta{background:#fff;color:#0b1020!important}
@media(max-width:820px){.fx-f_gradient .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
    'f_stacked': {
        'name': 'Stacked Links', 'thumb': 'stacked',
        'desc': 'Big stacked page links with arrows — bold and mobile-first',
        'html': """<footer class="fx fx-dark fx-f_stacked"><div class="fx-wrap">
  <div class="fx-grid">
    <div class="fx-stack">{{nav_links}}</div>
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p>
      <div class="fx-gap">{{contact_list}}</div>{{contact_icons}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_stacked{padding-top:96px}
.fx-f_stacked .fx-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:72px;align-items:start}
.fx-f_stacked .fx-stack{display:flex;flex-direction:column}
.fx-f_stacked .fx-stack a{display:flex;justify-content:space-between;align-items:center;font-size:clamp(26px,3.6vw,44px);font-weight:800;
  color:var(--fx-ink);letter-spacing:-.03em;padding:18px 0;border-bottom:1px solid var(--fx-line)}
.fx-f_stacked .fx-stack a::after{content:"\\2197";font-size:.6em;opacity:.35;transition:opacity .2s,transform .2s}
.fx-f_stacked .fx-stack a:hover{color:var(--accent);padding-left:8px}
.fx-f_stacked .fx-stack a:hover::after{opacity:1;transform:translate(4px,-4px)}
.fx-f_stacked .fx-gap{margin-top:30px}
@media(max-width:820px){.fx-f_stacked .fx-grid{grid-template-columns:1fr;gap:48px}}""",
    },
    'f_statement': {
        'name': 'Big Statement', 'thumb': 'statement',
        'desc': 'A giant "Let’s talk" with your email or phone as the hero',
        'html': """<footer class="fx fx-dark fx-f_statement"><div class="fx-wrap">
  <span class="fx-kicker">Have a project in mind?</span>
  <h3>Let's talk.</h3>
  <div class="fx-bigrow">{{big_contact}}{{cta_footer}}</div>
  <div class="fx-grid">
    <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p></div>
    <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div><h4>Contact</h4>{{contact_list}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_statement{padding-top:120px;background:#07090e}
.fx-f_statement .fx-kicker{display:flex;align-items:center;gap:12px;font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
.fx-f_statement .fx-kicker::before{content:"";width:34px;height:2px;background:var(--accent)}
.fx-f_statement h3{font-size:clamp(64px,14vw,190px);letter-spacing:-.06em;line-height:.9;margin:22px 0 36px}
.fx-f_statement .fx-bigrow{display:flex;align-items:center;justify-content:space-between;gap:24px 40px;flex-wrap:wrap;
  padding-bottom:72px;margin-bottom:72px;border-bottom:1px solid var(--fx-line)}
.fx-f_statement .fx-big{font-size:clamp(24px,3.6vw,44px)}
.fx-f_statement .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr;gap:48px}
@media(max-width:820px){.fx-f_statement .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
    'f_bento': {
        'name': 'Bento Grid', 'thumb': 'bento',
        'desc': 'Rounded tiles for brand, pages, contact and a call-to-action',
        'html': """<footer class="fx fx-light fx-f_bento"><div class="fx-wrap">
  <div class="fx-bento">
    <div class="fx-tile fx-t-brand"><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><h3>{{tagline_or_name}}</h3>{{contact_icons}}</div>
    <div class="fx-tile"><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
    <div class="fx-tile"><h4>Contact</h4>{{contact_list}}</div>
    <div class="fx-tile fx-t-cta"><h3>Ready when you are.</h3><p>Send us a message and we'll get back to you quickly.</p>{{cta_footer}}</div>
  </div>
  <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
</div></footer>""",
        'css': """.fx-f_bento{padding-top:96px;background:#f1f3f6}
.fx-f_bento .fx-bento{display:grid;grid-template-columns:1.4fr 1fr 1fr;grid-template-rows:auto auto;gap:16px}
.fx-f_bento .fx-tile{background:#fff;border:1px solid var(--fx-line);border-radius:26px;padding:32px}
.fx-f_bento .fx-t-brand{grid-row:span 2;display:flex;flex-direction:column;justify-content:space-between;gap:30px}
.fx-f_bento .fx-t-brand h3{font-size:clamp(28px,3.2vw,40px)}
.fx-f_bento .fx-t-cta{grid-column:span 2;--fx-ink:#fff;--fx-mut:rgba(255,255,255,.88);color:var(--fx-mut);background:var(--accent);border:none;
  display:grid;grid-template-columns:1fr auto;align-items:center;gap:8px 24px}
.fx-f_bento .fx-t-cta h3{font-size:clamp(24px,2.6vw,32px)}
.fx-f_bento .fx-t-cta p{grid-column:1}
.fx-f_bento .fx-t-cta .fx-cta{grid-column:2;grid-row:1 / span 2;background:#fff;color:var(--accent)!important}
@media(max-width:900px){.fx-f_bento .fx-bento{grid-template-columns:1fr 1fr}.fx-f_bento .fx-t-brand{grid-row:auto;grid-column:span 2}}
@media(max-width:600px){.fx-f_bento .fx-bento{grid-template-columns:1fr}.fx-f_bento .fx-t-brand,.fx-f_bento .fx-t-cta{grid-column:auto}
  .fx-f_bento .fx-t-cta{grid-template-columns:1fr}.fx-f_bento .fx-t-cta .fx-cta{grid-column:1;grid-row:auto;margin-top:12px}}""",
    },
    'f_wave': {
        'name': 'Soft Wave', 'thumb': 'wave',
        'desc': 'A flowing wave in your brand color above a light footer',
        'html': """<footer class="fx fx-f_wave">
  <svg class="fx-wavesvg" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,64 C240,120 480,0 720,40 C960,80 1200,120 1440,56 L1440,120 L0,120 Z"/></svg>
  <div class="fx-waveband"><div class="fx-wrap fx-band-in"><h3>{{tagline_or_name}}</h3><div class="fx-btns">{{cta_footer}}{{cta_ghost}}</div></div></div>
  <div class="fx-light fx-lower"><div class="fx-wrap">
    <div class="fx-grid">
      <div><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a><p class="fx-about">{{tagline}}</p>{{contact_icons}}</div>
      <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
      <div><h4>Contact</h4>{{contact_list}}</div>
    </div>
    <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div>
  </div></div>
</footer>""",
        'css': """.fx-f_wave .fx-wavesvg{display:block;width:100%;height:clamp(50px,7vw,110px);fill:var(--accent);stroke:none;margin-bottom:-1px}
.fx-f_wave .fx-waveband{background:var(--accent);color:#fff;padding:24px 0 80px}
.fx-f_wave .fx-band-in{display:flex;align-items:center;justify-content:space-between;gap:28px;flex-wrap:wrap}
.fx-f_wave .fx-waveband h3{color:#fff;font-size:clamp(28px,3.8vw,46px);max-width:640px}
.fx-f_wave .fx-waveband .fx-cta{background:#fff;color:var(--accent)!important}
.fx-f_wave .fx-waveband .fx-ghost{color:#fff}
.fx-f_wave .fx-lower{padding-top:80px;border-top:none}
.fx-f_wave .fx-grid{display:grid;grid-template-columns:1.6fr 1fr 1.2fr;gap:48px}
@media(max-width:820px){.fx-f_wave .fx-grid{grid-template-columns:1fr;gap:36px}}""",
    },
    'f_dual': {
        'name': 'Dual Panel', 'thumb': 'dual',
        'desc': 'Brand-color action panel beside rich dark columns',
        'html': """<footer class="fx fx-f_dual"><div class="fx-dualgrid">
  <div class="fx-panel"><a class="fx-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
    <h3>{{tagline_or_name}}</h3><div class="fx-btns">{{cta_footer}}</div>{{contact_icons}}</div>
  <div class="fx-dark fx-cols"><div class="fx-grid">
      <div><h4>Pages</h4><div class="fx-links">{{nav_links}}</div></div>
      <div><h4>Contact</h4>{{contact_list}}</div>
    </div>
    <div class="fx-bottom"><span>&copy; {{year}} {{site_name}}. All rights reserved.</span>{{to_top}}</div></div>
</div></footer>""",
        'css': """.fx-f_dual .fx-dualgrid{display:grid;grid-template-columns:minmax(300px,1fr) 1.4fr}
.fx-f_dual .fx-panel{--fx-ink:#fff;--fx-mut:rgba(255,255,255,.85);--fx-line:rgba(255,255,255,.3);background:var(--accent);color:var(--fx-mut);
  padding:96px clamp(24px,5vw,72px) 72px;display:flex;flex-direction:column;gap:26px}
.fx-f_dual .fx-panel h3{font-size:clamp(30px,3.4vw,46px)}
.fx-f_dual .fx-panel .fx-cta{background:#fff;color:var(--accent)!important}
.fx-f_dual .fx-panel .fx-icons{margin-top:auto}
.fx-f_dual .fx-panel .fx-icons a:hover{background:#fff;color:var(--accent);border-color:#fff}
.fx-f_dual .fx-cols{padding:96px clamp(24px,5vw,72px) 0;display:flex;flex-direction:column}
.fx-f_dual .fx-grid{display:grid;grid-template-columns:1fr 1.3fr;gap:48px}
.fx-f_dual .fx-bottom{margin-top:auto;padding-top:26px}
.fx-f_dual .fx-grid+.fx-bottom{margin-top:72px}
@media(max-width:860px){.fx-f_dual .fx-dualgrid{grid-template-columns:1fr}.fx-f_dual .fx-grid{grid-template-columns:1fr;gap:36px}
  .fx-f_dual .fx-panel{padding-top:72px}.fx-f_dual .fx-cols{padding-top:64px}}""",
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
