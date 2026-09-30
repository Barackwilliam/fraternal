"""
Navbar & Footer — presets za muundo + custom HTML ya mteja.

Mfumo:
  - Kama site.custom_nav_html ipo → tunaitumia (custom kamili ya mteja)
  - Vinginevyo kama site.nav_preset ipo → muundo kutoka builder/layouts.py
    (HEADERS), au preset ya zamani hapa chini (NAV_PRESETS)
  - Vinginevyo → default (glass nav ya sasa, base.html inaishughulikia)

Footer ni hivyo hivyo: custom_footer_html → footer_preset (layouts.FOOTERS
au FOOTER_PRESETS za zamani) → default ya base.html.

NAV_PRESETS na FOOTER_PRESETS za hapa chini ni za ZAMANI: zinabaki ili site
zinazozitumia zisivunjike, lakini Studio inaonyesha za layouts.py pekee.

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
from builder.images import image_url
from builder.layouts import (HEADERS, FOOTERS, HEADER_COMMON_CSS, SIDE_COMMON_CSS,
                             FOOTER_COMMON_CSS, mobile_menu_for)
from datetime import datetime
import html as html_lib
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


# Aikoni ndogo (SVG ya mistari) — hazipakii faili lolote la ziada
ICONS = {
    'Phone': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 '
             '19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 '
             '2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    'WhatsApp': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3 21l2.1-5.4A8.4 '
                '8.4 0 1 1 21 11.5z"/><path d="M9 9.5c.3 1.8 1.7 3.3 3.5 3.8l1-1 2 .8-.4 1.6"/></svg>',
    'Email': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/>'
             '<path d="m22 6-10 7L2 6"/></svg>',
    'Address': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/>'
               '<circle cx="12" cy="10" r="3"/></svg>',
}


def _nav_links_html(site, page_slug=None):
    """<a> za pages zote za nav, kutoka database."""
    out = []
    for p in site.pages.filter(show_in_nav=True).order_by('sort_order', 'id'):
        href = '/' if p.slug == 'home' else f'/p/{p.slug}/'
        on = ' class="on"' if page_slug and p.slug == page_slug else ''
        out.append(f'<a href="{href}"{on}>{html_lib.escape(p.title)}</a>')
    return '\n'.join(out)


def _placeholders(site, page_slug=None):
    esc = html_lib.escape
    name = esc(site.site_name or '')
    tagline = esc(site.tagline or '')
    phone = esc(site.contact_phone or '')
    email = esc(getattr(site, 'contact_email', '') or '')
    address = esc(getattr(site, 'contact_address', '') or '')
    logo = ''
    if site.logo_url:
        logo = f'<img src="{esc(image_url(site.logo_url, 80))}" alt="" loading="eager">'
    wa = ''
    if site.whatsapp_number:
        digits = re.sub(r'\D', '', site.whatsapp_number)
        wa = f'https://wa.me/{digits}'
    tel = 'tel:' + re.sub(r'[^\d+]', '', site.contact_phone or '') if site.contact_phone else ''
    cta_href = wa or tel or ('mailto:' + email if email else '/p/contact/')

    tagline_line = f'<div class="cfoot-tag">{tagline}</div>' if tagline else ''
    phone_line = f'<div>📞 {phone}</div>' if phone else ''
    email_line = f'<div>✉ {email}</div>' if email else ''
    whatsapp_line = f'<div>💬 <a href="{wa}">WhatsApp</a></div>' if wa else ''

    # Mawasiliano yaliyopo tu — hakuna mistari mitupu
    contacts = []
    if phone:
        contacts.append(('Phone', tel, phone))
    if wa:
        contacts.append(('WhatsApp', wa, 'Chat with us'))
    if email:
        contacts.append(('Email', f'mailto:{email}', email))
    if address:
        contacts.append(('Address', '', address))
    contact_list = '<ul class="fx-contact">' + ''.join(
        f'<li><b>{k}</b>' + (f'<a href="{h}">{v}</a>' if h else f'<span>{v}</span>') + '</li>'
        for k, h, v in contacts) + '</ul>' if contacts else ''
    contact_cards = ''.join(
        (f'<a class="fx-ccard" href="{h}">' if h else '<div class="fx-ccard">')
        + f'<i>{ICONS[k]}</i><b>{k}</b><span>{v}</span>' + ('</a>' if h else '</div>')
        for k, h, v in contacts)
    linked = [(k, h, v) for k, h, v in contacts if h]
    contact_icons = ('<div class="fx-icons">' + ''.join(
        f'<a href="{h}" aria-label="{k}" title="{k}">{ICONS[k]}</a>' for k, h, _ in linked) + '</div>') if linked else ''
    # Njia za mkato chini ya menyu ya simu
    m_contact = ''.join(f'<a href="{h}">{ICONS[k]}{"Call" if k == "Phone" else k}</a>' for k, h, _ in linked)
    # Mawasiliano makubwa ya footer ya "Let's talk": email, vinginevyo simu, vinginevyo WhatsApp
    big = next(((h, v) for k, h, v in contacts if k == 'Email'), None) or \
        next(((h, v) for k, h, v in contacts if k == 'Phone'), None) or \
        next(((h, 'Chat on WhatsApp') for k, h, v in contacts if k == 'WhatsApp'), None)
    big_contact = f'<a class="fx-big" href="{big[0]}">{big[1]}</a>' if big else ''
    ghost_href, ghost_text = (tel, f'Call {phone}') if phone else (('mailto:' + email, 'Email us') if email else ('', ''))

    return {
        '{{logo}}': logo,
        '{{site_name}}': name,
        '{{nav_links}}': _nav_links_html(site, page_slug),
        '{{phone}}': phone,
        '{{email}}': email,
        '{{address}}': address,
        '{{whatsapp}}': wa or '#',
        '{{year}}': str(datetime.now().year),
        '{{tagline}}': tagline,
        '{{tagline_or_name}}': tagline or name,
        '{{tagline_line}}': tagline_line,
        '{{tagline_meta}}': f'<div class="hx-side-meta">{tagline}</div>' if tagline else '',
        '{{phone_line}}': phone_line,
        '{{email_line}}': email_line,
        '{{whatsapp_line}}': whatsapp_line,
        '{{phone_inline}}': f'<a href="{tel}">{phone}</a>' if phone else '',
        '{{email_inline}}': f'<a href="mailto:{email}">{email}</a>' if email else '',
        '{{cta}}': f'<a class="hx-cta" href="{cta_href}">Get in touch</a>',
        '{{cta_footer}}': f'<a class="fx-cta" href="{cta_href}">Contact us</a>',
        '{{contact_list}}': contact_list,
        '{{contact_cards}}': contact_cards,
        '{{contact_icons}}': contact_icons,
        '{{m_contact}}': m_contact,
        '{{big_contact}}': big_contact,
        '{{cta_ghost}}': f'<a class="fx-ghost" href="{ghost_href}">{ghost_text}</a>' if ghost_href else '',
        '{{to_top}}': ('<a class="fx-totop" href="#" onclick="window.scrollTo({top:0,behavior:\'smooth\'});'
                       'return false">Back to top</a>'),
        '{{credit}}': 'Developed by <a href="https://www.jamiitek.com" target="_blank" rel="noopener">JamiiTek</a>',
    }


def _fill(html, ph):
    for k, v in ph.items():
        html = html.replace(k, v)
    return html


def header_css(key):
    """CSS kamili ya header ya layouts.py (pamoja na ya sidebar ikiwa side)."""
    h = HEADERS[key]
    extra = SIDE_COMMON_CSS if h['kind'] == 'side' else ''
    return HEADER_COMMON_CSS + extra + h['css']


def render_nav(site, page_slug=None):
    """Rudisha (html, css) ya navbar. Tupu = tumia default ya base.html."""
    ph = _placeholders(site, page_slug)
    if site.custom_nav_html.strip():
        # CSS ya pamoja inapendezesha {{cta}} na kufunga scroll menyu ikiwa wazi
        return _fill(site.custom_nav_html, ph), HEADER_COMMON_CSS
    if site.nav_preset in HEADERS:
        ph['{{mm}}'] = 'hx-m-' + mobile_menu_for(site, site.nav_preset)
        return _fill(HEADERS[site.nav_preset]['html'], ph), header_css(site.nav_preset)
    if site.nav_preset in NAV_PRESETS:
        preset = NAV_PRESETS[site.nav_preset]
        return _fill(preset['html'], ph), preset['css']
    return '', ''   # default → base.html inarender nav yake ya kawaida


def render_footer(site, page_slug=None):
    """Rudisha (html, css) ya footer. Tupu = tumia default ya base.html."""
    ph = _placeholders(site, page_slug)
    if site.custom_footer_html.strip():
        # {{contact_icons}}, {{cta_footer}}, {{to_top}} n.k. zinapata muonekano wao
        return _fill(site.custom_footer_html, ph), FOOTER_COMMON_CSS
    key = getattr(site, 'footer_preset', '')
    if key in FOOTERS:
        return _fill(FOOTERS[key]['html'], ph), FOOTER_COMMON_CSS + FOOTERS[key]['css']
    if key in FOOTER_PRESETS:
        return _fill(FOOTER_PRESETS[key]['html'], ph), FOOTER_PRESETS[key]['css']
    return '', ''


def get_preset_catalog():
    """Kwa UI — muundo wote unaoweza kuchaguliwa (wa layouts.py)."""
    return {
        'nav': [{'key': k, 'name': v['name'], 'desc': v['desc'], 'kind': v['kind'], 'thumb': v['thumb']}
                for k, v in HEADERS.items()],
        'footer': [{'key': k, 'name': v['name'], 'desc': v['desc'], 'thumb': v['thumb']}
                   for k, v in FOOTERS.items()],
    }
