"""
Navbar & Footer — presets za muundo + custom HTML ya mteja.

Mfumo:
  - Kama site.custom_nav_html ipo → tunaitumia (custom kamili ya mteja)
  - Vinginevyo kama site.nav_preset ipo → tunatumia preset ya muundo huo
  - Vinginevyo → default (glass nav ya sasa, base.html inaishughulikia)

PLACEHOLDERS (zinafanya kazi kwenye custom HTML na presets):
  {{logo}}       → <img> ya logo (kama ipo) — vinginevyo tupu
  {{site_name}}  → jina la biashara
  {{nav_links}}  → <a> za pages zote za nav (auto kutoka database)
  {{phone}}      → simu
  {{email}}      → email
  {{whatsapp}}   → link ya WhatsApp (wa.me/…)
  {{year}}       → mwaka wa sasa
  {{tagline}}    → tagline

Placeholders zinamwezesha mteja kubadilisha MUUNDO bila kuvunja links za
pages (ambazo ni dynamic). Custom HTML bila {{nav_links}} pia inaruhusiwa —
mteja anaweza kuandika links zake mwenyewe kwa mkono.
"""
from datetime import datetime
import re


# ═══ NAV PRESETS — muundo tofauti wa navbar ═══
NAV_PRESETS = {
    'logo_left': {
        'name': 'Logo Left + Links',
        'desc': 'Classic — logo left, menu right',
        'html': '''<nav class="cnav cnav-logoleft">
  <a class="cnav-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <button class="cnav-burger" onclick="jtMenu(true)">☰</button>
  <div class="cnav-menu" id="jt-links"><button class="cnav-x" onclick="jtMenu(false)">×</button>{{nav_links}}</div>
</nav>''',
        'css': '''.cnav-logoleft{position:sticky;top:0;z-index:60;display:flex;align-items:center;justify-content:space-between;
  gap:16px;padding:15px 28px;background:var(--nav-bg);backdrop-filter:blur(16px);border-bottom:1px solid rgba(0,0,0,.06)}
.cnav-logoleft .cnav-brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:19px;text-decoration:none;color:var(--nav-ink)}
.cnav-logoleft .cnav-brand img{height:36px;border-radius:8px}
.cnav-logoleft .cnav-menu{display:flex;align-items:center;gap:4px}
.cnav-logoleft .cnav-menu a{padding:9px 15px;border-radius:10px;font-size:14.5px;text-decoration:none;color:var(--nav-mut);font-weight:600;transition:.2s}
.cnav-logoleft .cnav-menu a:hover{color:var(--nav-ink);background:color-mix(in srgb,var(--accent) 16%,transparent)}''',
    },
    'centered': {
        'name': 'Centered Logo',
        'desc': 'Logo in the middle, links split',
        'html': '''<nav class="cnav cnav-centered">
  <button class="cnav-burger" onclick="jtMenu(true)">☰</button>
  <div class="cnav-menu" id="jt-links"><button class="cnav-x" onclick="jtMenu(false)">×</button>{{nav_links}}</div>
  <a class="cnav-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
</nav>''',
        'css': '''.cnav-centered{position:sticky;top:0;z-index:60;display:flex;flex-direction:column;align-items:center;gap:8px;
  padding:18px 24px;background:var(--nav-bg);backdrop-filter:blur(16px);border-bottom:1px solid rgba(0,0,0,.06);text-align:center}
.cnav-centered .cnav-brand{display:flex;flex-direction:column;align-items:center;gap:6px;font-weight:800;font-size:22px;text-decoration:none;color:var(--nav-ink);order:-1}
.cnav-centered .cnav-brand img{height:44px;border-radius:8px}
.cnav-centered .cnav-menu{display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:center}
.cnav-centered .cnav-menu a{padding:8px 14px;border-radius:8px;font-size:14px;text-decoration:none;color:var(--nav-mut);font-weight:600;transition:.2s}
.cnav-centered .cnav-menu a:hover{color:var(--accent)}''',
    },
    'pill_cta': {
        'name': 'Modern + CTA Button',
        'desc': 'Logo, links, and a WhatsApp button',
        'html': '''<nav class="cnav cnav-pill">
  <a class="cnav-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <button class="cnav-burger" onclick="jtMenu(true)">☰</button>
  <div class="cnav-menu" id="jt-links"><button class="cnav-x" onclick="jtMenu(false)">×</button>{{nav_links}}
    <a class="cnav-cta" href="{{whatsapp}}">💬 Contact</a></div>
</nav>''',
        'css': '''.cnav-pill{position:sticky;top:12px;z-index:60;margin:12px auto;max-width:1080px;display:flex;align-items:center;
  justify-content:space-between;gap:16px;padding:12px 20px;background:var(--nav-bg);backdrop-filter:blur(18px);
  border:1px solid rgba(0,0,0,.07);border-radius:100px;box-shadow:0 8px 30px rgba(0,0,0,.08)}
.cnav-pill .cnav-brand{display:flex;align-items:center;gap:9px;font-weight:800;font-size:18px;text-decoration:none;color:var(--nav-ink)}
.cnav-pill .cnav-brand img{height:32px;border-radius:7px}
.cnav-pill .cnav-menu{display:flex;align-items:center;gap:4px}
.cnav-pill .cnav-menu a{padding:8px 14px;border-radius:100px;font-size:14px;text-decoration:none;color:var(--nav-mut);font-weight:600;transition:.2s}
.cnav-pill .cnav-menu a:hover{color:var(--nav-ink);background:color-mix(in srgb,var(--accent) 14%,transparent)}
.cnav-pill .cnav-cta{background:var(--accent)!important;color:#fff!important;font-weight:700}
.cnav-pill .cnav-cta:hover{filter:brightness(1.08)}''',
    },
    'minimal': {
        'name': 'Minimal Underline',
        'desc': 'Clean, no background, underline hover',
        'html': '''<nav class="cnav cnav-minimal">
  <a class="cnav-brand" href="/">{{logo}}<span>{{site_name}}</span></a>
  <button class="cnav-burger" onclick="jtMenu(true)">☰</button>
  <div class="cnav-menu" id="jt-links"><button class="cnav-x" onclick="jtMenu(false)">×</button>{{nav_links}}</div>
</nav>''',
        'css': '''.cnav-minimal{position:sticky;top:0;z-index:60;display:flex;align-items:center;justify-content:space-between;
  gap:16px;padding:20px 32px;background:transparent}
.cnav-minimal .cnav-brand{display:flex;align-items:center;gap:9px;font-weight:800;font-size:19px;text-decoration:none;color:var(--nav-ink);letter-spacing:-.01em}
.cnav-minimal .cnav-brand img{height:34px;border-radius:7px}
.cnav-minimal .cnav-menu{display:flex;align-items:center;gap:22px}
.cnav-minimal .cnav-menu a{padding:4px 0;font-size:14.5px;text-decoration:none;color:var(--nav-mut);font-weight:600;
  border-bottom:2px solid transparent;transition:.2s}
.cnav-minimal .cnav-menu a:hover{color:var(--nav-ink);border-bottom-color:var(--accent)}''',
    },
}


# ═══ FOOTER PRESETS ═══
FOOTER_PRESETS = {
    'simple': {
        'name': 'Simple',
        'desc': 'One line — name, contact, credit',
        'html': '''<footer class="cfoot cfoot-simple">
  <div class="cfoot-wrap">
    <div><strong>{{site_name}}</strong>{{tagline_line}}</div>
    <div class="cfoot-contact">{{phone_line}}{{email_line}}</div>
    <div class="cfoot-badge">© {{year}} · Built with <a href="https://jamiitek.com">JamiiTek</a></div>
  </div>
</footer>''',
        'css': '''.cfoot-simple{background:#101a14;color:#b9cbbd;padding:40px 24px;margin-top:70px;font-size:14px}
.cfoot-simple .cfoot-wrap{max-width:1060px;margin:0 auto;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;align-items:center}
.cfoot-simple strong{color:#fff;font-size:16px}
.cfoot-simple a{color:var(--accent);text-decoration:none}
.cfoot-simple .cfoot-badge{font-size:12px;opacity:.75}''',
    },
    'columns': {
        'name': 'Multi-Column',
        'desc': 'Brand, links, and contact columns',
        'html': '''<footer class="cfoot cfoot-cols">
  <div class="cfoot-grid">
    <div class="cfoot-brand"><strong>{{site_name}}</strong>{{tagline_line}}</div>
    <div><h4>Pages</h4>{{nav_links}}</div>
    <div><h4>Contact</h4>{{phone_line}}{{email_line}}{{whatsapp_line}}</div>
  </div>
  <div class="cfoot-bottom">© {{year}} {{site_name}} · Built with <a href="https://jamiitek.com">JamiiTek</a></div>
</footer>''',
        'css': '''.cfoot-cols{background:#0d1510;color:#a9bdae;padding:56px 24px 24px;margin-top:70px;font-size:14px}
.cfoot-cols .cfoot-grid{max-width:1060px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr;gap:34px}
.cfoot-cols h4{color:#fff;font-size:13px;text-transform:uppercase;letter-spacing:1px;margin:0 0 14px}
.cfoot-cols strong{color:#fff;font-size:19px}
.cfoot-cols a{color:#a9bdae;text-decoration:none;display:block;padding:4px 0;transition:.2s}
.cfoot-cols a:hover{color:var(--accent)}
.cfoot-cols .cfoot-bottom{max-width:1060px;margin:40px auto 0;padding-top:22px;border-top:1px solid rgba(255,255,255,.08);
  font-size:12.5px;opacity:.7;text-align:center}
.cfoot-cols .cfoot-bottom a{display:inline;color:var(--accent)}
@media(max-width:720px){.cfoot-cols .cfoot-grid{grid-template-columns:1fr;gap:26px}}''',
    },
    'centered': {
        'name': 'Centered',
        'desc': 'Logo and links centered',
        'html': '''<footer class="cfoot cfoot-centered">
  <strong>{{site_name}}</strong>{{tagline_line}}
  <div class="cfoot-links">{{nav_links}}</div>
  <div class="cfoot-contact">{{phone_line}}{{email_line}}</div>
  <div class="cfoot-badge">© {{year}} · Built with <a href="https://jamiitek.com">JamiiTek</a></div>
</footer>''',
        'css': '''.cfoot-centered{background:#101a14;color:#b9cbbd;padding:54px 24px;margin-top:70px;text-align:center;font-size:14px}
.cfoot-centered strong{color:#fff;font-size:22px;display:block;margin-bottom:6px}
.cfoot-centered .cfoot-links{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;margin:20px 0}
.cfoot-centered .cfoot-links a{color:#b9cbbd;text-decoration:none;font-weight:600;transition:.2s}
.cfoot-centered .cfoot-links a:hover{color:var(--accent)}
.cfoot-centered a{color:var(--accent);text-decoration:none}
.cfoot-centered .cfoot-badge{font-size:12px;opacity:.7;margin-top:18px}
.cfoot-centered .cfoot-contact{font-size:13.5px;opacity:.85}''',
    },
}


def _nav_links_html(site, page_slug=None):
    """<a> za pages zote za nav, kutoka database."""
    out = []
    for p in site.pages.filter(show_in_nav=True).order_by('sort_order', 'id'):
        href = '/' if p.slug == 'home' else f'/p/{p.slug}/'
        on = ' class="on"' if page_slug and p.slug == page_slug else ''
        out.append(f'<a href="{href}"{on}>{p.title}</a>')
    return '\n'.join(out)


def _placeholders(site, page_slug=None):
    logo = ''
    if site.logo_url:
        logo = f'<img src="{site.logo_url}-/resize/80x/" alt="" loading="eager">'
    wa = ''
    if site.whatsapp_number:
        digits = re.sub(r'\D', '', site.whatsapp_number)
        wa = f'https://wa.me/{digits}'
    tagline_line = f'<div class="cfoot-tag">{site.tagline}</div>' if site.tagline else ''
    phone_line = f'<div>📞 {site.contact_phone}</div>' if site.contact_phone else ''
    email = getattr(site, 'contact_email', '') or ''
    email_line = f'<div>✉ {email}</div>' if email else ''
    whatsapp_line = f'<div>💬 <a href="{wa}">WhatsApp</a></div>' if wa else ''
    return {
        '{{logo}}': logo,
        '{{site_name}}': site.site_name,
        '{{nav_links}}': _nav_links_html(site, page_slug),
        '{{phone}}': site.contact_phone or '',
        '{{email}}': email,
        '{{whatsapp}}': wa or '#',
        '{{year}}': str(datetime.now().year),
        '{{tagline}}': site.tagline or '',
        '{{tagline_line}}': tagline_line,
        '{{phone_line}}': phone_line,
        '{{email_line}}': email_line,
        '{{whatsapp_line}}': whatsapp_line,
    }


def _fill(html, ph):
    for k, v in ph.items():
        html = html.replace(k, v)
    return html


def render_nav(site, page_slug=None):
    """Rudisha (html, css) ya navbar. Tupu = tumia default ya base.html."""
    ph = _placeholders(site, page_slug)
    if site.custom_nav_html.strip():
        return _fill(site.custom_nav_html, ph), ''
    if site.nav_preset in NAV_PRESETS:
        preset = NAV_PRESETS[site.nav_preset]
        return _fill(preset['html'], ph), preset['css']
    return '', ''   # default → base.html inarender nav yake ya kawaida


def render_footer(site, page_slug=None):
    """Rudisha (html, css) ya footer. Tupu = tumia default ya base.html."""
    ph = _placeholders(site, page_slug)
    if site.custom_footer_html.strip():
        return _fill(site.custom_footer_html, ph), ''
    # footer preset inaweza kuhifadhiwa kwenye nav_preset? Hapana — tuna field moja.
    # Tunatumia convention: footer preset inahifadhiwa ndani ya custom_footer_html
    # kama mteja amechagua preset (tunaijaza pale). Kwa hiyo hapa default tu.
    return '', ''


def get_preset_catalog():
    """Kwa UI — orodha ya presets zote na preview."""
    return {
        'nav': [{'key': k, **{kk: vv for kk, vv in v.items() if kk in ('name', 'desc')}}
                for k, v in NAV_PRESETS.items()],
        'footer': [{'key': k, **{kk: vv for kk, vv in v.items() if kk in ('name', 'desc')}}
                   for k, v in FOOTER_PRESETS.items()],
    }
