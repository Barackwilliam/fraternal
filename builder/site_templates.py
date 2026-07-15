"""
JamiiTek Template Library — advanced pre-customized templates.

Kila aina ya website ina templates zaidi ya moja, kila moja na:
  - nav_layout: 'topnav' au 'sidenav' (UI structure tofauti kabisa)
  - global_css: design system nzima ya site (CSS variables + styles)
  - pages: HTML ya kila page (inatumia shortcodes za [[site:...]] na [[collection:...]])

Pages ambazo template haija-define zinachukua starter_html kutoka schema.
Mteja anaweza kubadilisha KILA KITU baadaye kwenye editor.
"""

# ── CSS ya pamoja: animations za scroll-reveal kwenye site za wateja ──
REVEAL_CSS = """
.jt-reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease}
.jt-reveal.jt-in{opacity:1;transform:none}
@media (prefers-reduced-motion: reduce){.jt-reveal{opacity:1;transform:none;transition:none}}
"""

TEMPLATES = {

    # ══════════════ TOURISM ══════════════
    'savanna_luxe': {
        'label': 'Savanna Luxe',
        'types': ['tourism'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#0d2419 0%,#1e4536 55%,#e8a13c 140%)',
        'tagline': 'Hero kubwa ya giza-dhahabu, kifahari, kwa kampuni za safari',
        'global_css': REVEAL_CSS + """
:root{--sb:#0d2419;--sb2:#153524;--sa:#e8a13c;--stx:#eef3ec}
body{background:#fbfaf6;color:#26302a}
.jt-nav{background:rgba(13,36,25,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid rgba(232,161,60,.25)}
.jt-nav .logo{color:#fff}.jt-nav .links a{color:#d7e2d6}
.jt-nav .links a:hover{background:rgba(232,161,60,.16);color:#fff}
.jt-footer{background:var(--sb)}
h1,h2,h3{letter-spacing:.2px}
.jt-card{border:1px solid rgba(232,161,60,.18)}
.jt-card-price{color:#7a4e0a}
""",
        'pages': {
            'home': """
<section style="min-height:88vh;display:flex;align-items:flex-end;background:linear-gradient(180deg,rgba(13,36,25,.35),rgba(13,36,25,.92)),linear-gradient(140deg,#123021,#0d2419);color:#fff;padding:0 24px 90px">
 <div class="jt-reveal" style="max-width:1100px;margin:0 auto;width:100%">
  <p style="letter-spacing:6px;text-transform:uppercase;color:#e8a13c;font-size:13px;margin-bottom:14px">[[site:name]] · Tanzania</p>
  <h1 style="font-size:clamp(40px,7vw,74px);line-height:1.04;margin:0 0 18px;max-width:760px">Pori Linakuita.<br>Twende Pamoja.</h1>
  <p style="font-size:19px;opacity:.85;max-width:560px;margin-bottom:34px">[[site:tagline]]</p>
  <a href="/p/packages/" style="background:#e8a13c;color:#0d2419;padding:16px 40px;border-radius:8px;font-weight:800;text-decoration:none;font-size:16px">Angalia Safari Packages</a>
  <a href="[[site:whatsapp]]" style="margin-left:14px;color:#fff;border:1.5px solid rgba(255,255,255,.5);padding:15px 30px;border-radius:8px;text-decoration:none;font-weight:700">WhatsApp</a>
 </div>
</section>
<section class="jt-reveal" style="padding:90px 24px 30px;max-width:1100px;margin:0 auto;text-align:center">
 <p style="letter-spacing:4px;text-transform:uppercase;color:#b3852f;font-size:12px">Signature Journeys</p>
 <h2 style="font-size:clamp(30px,4.5vw,44px);margin:8px 0 0">Packages Zetu Maarufu</h2>
</section>
<section class="jt-reveal" style="padding:0 24px 40px;max-width:1100px;margin:0 auto">[[collection:packages]]</section>
<section style="background:#0d2419;color:#fff;padding:90px 24px">
 <div class="jt-reveal" style="max-width:1100px;margin:0 auto">
  <h2 style="text-align:center;font-size:clamp(28px,4vw,40px);margin-bottom:8px">Destinations</h2>
  <p style="text-align:center;opacity:.7;margin-bottom:10px">Kutoka Serengeti mpaka Zanzibar.</p>
  [[collection:destinations]]
 </div>
</section>
<section class="jt-reveal" style="padding:90px 24px;text-align:center">
 <h2 style="font-size:clamp(26px,4vw,36px)">Upcoming Trips</h2>
 <div style="max-width:1100px;margin:0 auto">[[collection:trips]]</div>
 <a href="[[site:whatsapp]]" style="display:inline-block;margin-top:20px;background:#25d366;color:#fff;padding:14px 36px;border-radius:8px;text-decoration:none;font-weight:800">Book kwa WhatsApp</a>
</section>""",
        },
    },

    'expedition_side': {
        'label': 'Expedition (Side Nav)',
        'types': ['tourism'],
        'nav_layout': 'sidenav',
        'preview': 'linear-gradient(140deg,#141a17 0%,#243b2e 60%,#c96a35 150%)',
        'tagline': 'Side navigation ya kudumu, mtindo wa jarida la kisafari',
        'global_css': REVEAL_CSS + """
:root{--sb:#141a17;--sa:#c96a35}
body{background:#0f1412;color:#e6e9e4}
.jt-sidenav{background:rgba(20,26,23,.72);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-right:1px solid rgba(201,106,53,.25)}
.jt-sidenav .logo{color:#fff}
.jt-sidenav a{color:#b9c4ba}
.jt-sidenav a:hover,.jt-sidenav a.on{background:rgba(201,106,53,.18);color:#fff}
.jt-footer{background:#0b0f0d}
.jt-card{background:#1a221d;color:#e6e9e4;border:1px solid rgba(201,106,53,.2)}
.jt-card-title{color:#fff}.jt-card-desc{color:#a9b3aa}.jt-card-price{color:#e8a13c}
""",
        'pages': {
            'home': """
<section style="min-height:92vh;display:flex;align-items:center;padding:60px 32px;background:radial-gradient(1000px 500px at 80% 10%,rgba(201,106,53,.22),transparent 60%),#0f1412">
 <div class="jt-reveal" style="max-width:820px">
  <p style="color:#c96a35;letter-spacing:5px;text-transform:uppercase;font-size:12px;margin-bottom:16px">Expedition Co. · [[site:name]]</p>
  <h1 style="font-size:clamp(42px,6.5vw,70px);line-height:1.05;margin:0 0 20px;color:#fff">Kila Safari<br>ni Hadithi Mpya.</h1>
  <p style="font-size:18px;color:#a9b3aa;max-width:520px;margin-bottom:32px">[[site:tagline]]</p>
  <a href="/p/packages/" style="background:#c96a35;color:#fff;padding:15px 36px;border-radius:6px;font-weight:800;text-decoration:none">Packages →</a>
 </div>
</section>
<section class="jt-reveal" style="padding:70px 32px"><h2 style="color:#fff;font-size:32px;margin-bottom:6px">Packages</h2>[[collection:packages]]</section>
<section class="jt-reveal" style="padding:30px 32px 70px"><h2 style="color:#fff;font-size:32px;margin-bottom:6px">Destinations</h2>[[collection:destinations]]</section>""",
        },
    },

    # ══════════════ E-COMMERCE ══════════════
    'duka_glass': {
        'label': 'Duka Glass',
        'types': ['ecommerce'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#1b1035 0%,#3b1f6e 60%,#e8a13c 160%)',
        'tagline': 'Glassmorphism kamili — duka la kisasa kabisa',
        'global_css': REVEAL_CSS + """
:root{--sa:#8b5cf6}
body{background:linear-gradient(160deg,#150c2e,#241348 55%,#1b1035);color:#ece8f8;min-height:100vh}
.jt-nav{background:rgba(255,255,255,.07);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border-bottom:1px solid rgba(255,255,255,.14)}
.jt-nav .logo{color:#fff}.jt-nav .links a{color:#d6cdf2}
.jt-nav .links a:hover{background:rgba(255,255,255,.12);color:#fff}
.jt-footer{background:rgba(0,0,0,.35)}
.jt-card{background:rgba(255,255,255,.08);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border:1px solid rgba(255,255,255,.15);color:#ece8f8}
.jt-card-title{color:#fff}.jt-card-desc{color:#c9c0e6}.jt-card-price{color:#e8a13c}
.jt-card:hover{border-color:rgba(232,161,60,.5)}
""",
        'pages': {
            'home': """
<section style="min-height:78vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:70px 24px">
 <div class="jt-reveal">
  <h1 style="font-size:clamp(38px,6vw,64px);margin:0 0 14px;background:linear-gradient(90deg,#fff,#c9b3ff);-webkit-background-clip:text;background-clip:text;color:transparent">[[site:name]]</h1>
  <p style="font-size:18px;color:#c9c0e6;max-width:520px;margin:0 auto 30px">[[site:tagline]]</p>
  <a href="/p/shop/" style="background:linear-gradient(90deg,#8b5cf6,#e8a13c);color:#fff;padding:15px 42px;border-radius:40px;font-weight:800;text-decoration:none;box-shadow:0 10px 34px rgba(139,92,246,.4)">Nunua Sasa 🛍️</a>
 </div>
</section>
<section class="jt-reveal" style="padding:20px 24px 80px;max-width:1100px;margin:0 auto">
 <h2 style="text-align:center;font-size:34px;color:#fff;margin-bottom:4px">Bidhaa Zetu</h2>
 [[collection:products]]
 <p style="text-align:center"><a href="[[site:whatsapp]]" style="display:inline-block;margin-top:8px;background:#25d366;color:#fff;padding:13px 32px;border-radius:40px;text-decoration:none;font-weight:800">Agiza kwa WhatsApp</a></p>
</section>""",
        },
    },

    # ══════════════ RESTAURANT ══════════════
    'ladha': {
        'label': 'Ladha',
        'types': ['restaurant'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#2b1208 0%,#5c2610 60%,#e8a13c 160%)',
        'tagline': 'Joto la jiko — rangi za viungo na moto',
        'global_css': REVEAL_CSS + """
body{background:#fdf8f1;color:#33241a}
.jt-nav{background:rgba(43,18,8,.88);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.jt-nav .logo{color:#fff}.jt-nav .links a{color:#ecd9c8}
.jt-nav .links a:hover{background:rgba(232,161,60,.2);color:#fff}
.jt-footer{background:#2b1208}
.jt-card{border:1px solid #efdcc4}
.jt-card-price{color:#8a3c12}
""",
        'pages': {
            'home': """
<section style="min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;background:linear-gradient(180deg,rgba(43,18,8,.55),rgba(43,18,8,.9)),linear-gradient(140deg,#5c2610,#2b1208);color:#fff;padding:70px 24px">
 <div class="jt-reveal">
  <p style="letter-spacing:5px;text-transform:uppercase;color:#e8a13c;font-size:12px;margin-bottom:12px">Karibu · [[site:name]]</p>
  <h1 style="font-size:clamp(40px,6.5vw,66px);margin:0 0 16px">Ladha ya Nyumbani,<br>Kila Siku.</h1>
  <p style="font-size:18px;opacity:.85;margin-bottom:30px">[[site:tagline]]</p>
  <a href="/p/menu/" style="background:#e8a13c;color:#2b1208;padding:15px 40px;border-radius:8px;font-weight:800;text-decoration:none">Angalia Menu 🍛</a>
 </div>
</section>
<section class="jt-reveal" style="padding:80px 24px;max-width:1100px;margin:0 auto">
 <h2 style="text-align:center;font-size:36px">Vyakula Vyetu</h2>
 [[collection:menu]]
 <p style="text-align:center"><a href="[[site:whatsapp]]" style="display:inline-block;background:#25d366;color:#fff;padding:13px 32px;border-radius:8px;text-decoration:none;font-weight:800">Agiza kwa WhatsApp</a></p>
</section>""",
        },
    },

    # ══════════════ COMPANY PROFILE ══════════════
    'corporate_sky': {
        'label': 'Corporate Sky',
        'types': ['companyprofile', 'default'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#071a2e 0%,#0e3a5c 60%,#38bdf8 170%)',
        'tagline': 'Professional, safi, ya kuaminika — kwa kampuni',
        'global_css': REVEAL_CSS + """
body{background:#f6f9fc;color:#1d2733}
.jt-nav{background:rgba(255,255,255,.85);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border-bottom:1px solid #e3ecf4}
.jt-nav .logo{color:#071a2e}.jt-nav .links a{color:#33465c}
.jt-nav .links a:hover{background:#e8f2fb;color:#071a2e}
.jt-footer{background:#071a2e}
.jt-card{border:1px solid #e3ecf4}
.jt-card-price{color:#0e3a5c}
""",
        'pages': {
            'home': """
<section style="min-height:74vh;display:flex;align-items:center;background:linear-gradient(140deg,#071a2e,#0e3a5c);color:#fff;padding:70px 24px">
 <div class="jt-reveal" style="max-width:1100px;margin:0 auto;width:100%">
  <h1 style="font-size:clamp(36px,5.5vw,58px);line-height:1.1;max-width:700px;margin:0 0 18px">[[site:name]]</h1>
  <p style="font-size:19px;opacity:.85;max-width:560px;margin-bottom:30px">[[site:tagline]]</p>
  <a href="/p/contact/" style="background:#38bdf8;color:#071a2e;padding:14px 36px;border-radius:8px;font-weight:800;text-decoration:none">Wasiliana Nasi</a>
 </div>
</section>
<section class="jt-reveal" style="padding:80px 24px;max-width:1100px;margin:0 auto">
 <h2 style="text-align:center;font-size:34px">Huduma Zetu</h2>
 [[collection:services]]
</section>""",
        },
    },

    'studio_side': {
        'label': 'Studio (Side Nav)',
        'types': ['companyprofile', 'default'],
        'nav_layout': 'sidenav',
        'preview': 'linear-gradient(140deg,#101014 0%,#26262e 65%,#e8a13c 170%)',
        'tagline': 'Portfolio/studio yenye side navigation nyeusi ya kifahari',
        'global_css': REVEAL_CSS + """
body{background:#101014;color:#e9e9ee}
.jt-sidenav{background:rgba(16,16,20,.78);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  border-right:1px solid rgba(255,255,255,.1)}
.jt-sidenav .logo{color:#fff}
.jt-sidenav a{color:#a9a9b6}
.jt-sidenav a:hover,.jt-sidenav a.on{background:rgba(232,161,60,.15);color:#fff}
.jt-footer{background:#0a0a0d}
.jt-card{background:#1a1a20;color:#e9e9ee;border:1px solid rgba(255,255,255,.09)}
.jt-card-title{color:#fff}.jt-card-desc{color:#a9a9b6}.jt-card-price{color:#e8a13c}
""",
        'pages': {
            'home': """
<section style="min-height:90vh;display:flex;align-items:center;padding:60px 32px;background:radial-gradient(900px 460px at 85% 15%,rgba(232,161,60,.14),transparent 60%)">
 <div class="jt-reveal" style="max-width:800px">
  <p style="color:#e8a13c;letter-spacing:5px;text-transform:uppercase;font-size:12px;margin-bottom:14px">[[site:name]]</p>
  <h1 style="font-size:clamp(40px,6vw,66px);line-height:1.06;color:#fff;margin:0 0 18px">Tunajenga Kazi<br>Zinazokumbukwa.</h1>
  <p style="font-size:18px;color:#a9a9b6;max-width:520px;margin-bottom:30px">[[site:tagline]]</p>
  <a href="/p/contact/" style="background:#e8a13c;color:#101014;padding:14px 36px;border-radius:6px;font-weight:800;text-decoration:none">Anza Mradi →</a>
 </div>
</section>
<section class="jt-reveal" style="padding:60px 32px"><h2 style="color:#fff;font-size:32px">Huduma</h2>[[collection:services]]</section>
<section class="jt-reveal" style="padding:20px 32px 70px"><h2 style="color:#fff;font-size:32px">Timu</h2>[[collection:team]]</section>""",
        },
    },

    # ══════════════ EVENTS ══════════════
    'pulse': {
        'label': 'Pulse',
        'types': ['events'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#12041f 0%,#3b0764 60%,#f0abfc 170%)',
        'tagline': 'Neon glass — kwa matukio, matamasha na shows',
        'global_css': REVEAL_CSS + """
body{background:linear-gradient(160deg,#12041f,#1e0836 60%,#12041f);color:#f3e8ff;min-height:100vh}
.jt-nav{background:rgba(255,255,255,.06);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border-bottom:1px solid rgba(240,171,252,.2)}
.jt-nav .logo{color:#fff}.jt-nav .links a{color:#e2ccf7}
.jt-nav .links a:hover{background:rgba(240,171,252,.14);color:#fff}
.jt-footer{background:rgba(0,0,0,.4)}
.jt-card{background:rgba(255,255,255,.07);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  border:1px solid rgba(240,171,252,.22);color:#f3e8ff}
.jt-card-title{color:#fff}.jt-card-desc{color:#d8c3ee}.jt-card-price{color:#f0abfc}
""",
        'pages': {
            'home': """
<section style="min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:70px 24px">
 <div class="jt-reveal">
  <h1 style="font-size:clamp(40px,7vw,70px);margin:0 0 14px;background:linear-gradient(90deg,#f0abfc,#818cf8);-webkit-background-clip:text;background-clip:text;color:transparent">[[site:name]]</h1>
  <p style="font-size:18px;color:#d8c3ee;margin-bottom:30px">[[site:tagline]]</p>
  <a href="/p/events/" style="background:linear-gradient(90deg,#a855f7,#ec4899);color:#fff;padding:15px 42px;border-radius:40px;font-weight:800;text-decoration:none;box-shadow:0 10px 34px rgba(168,85,247,.45)">Matukio Yajayo 🎉</a>
 </div>
</section>
<section class="jt-reveal" style="padding:20px 24px 80px;max-width:1100px;margin:0 auto">
 <h2 style="text-align:center;font-size:34px;color:#fff">Usikose!</h2>
 [[collection:events]]
</section>""",
        },
    },

    # ══════════════ DEFAULT / CLEAN ══════════════
    'clean_start': {
        'label': 'Clean Start',
        'types': ['default', 'companyprofile', 'ecommerce', 'restaurant', 'tourism', 'events'],
        'nav_layout': 'topnav',
        'preview': 'linear-gradient(140deg,#f4f1ea 0%,#dcd6c6 70%,#16342a 220%)',
        'tagline': 'Msingi mweupe safi — anzia hapa ujenge chochote',
        'global_css': REVEAL_CSS + """
body{background:#fff;color:#222}
.jt-nav{background:rgba(255,255,255,.9);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid #eee}
""",
        'pages': {},   # inatumia starter za schema kama zilivyo
    },
}


def templates_for_type(website_type):
    """Templates zinazofaa kwa aina fulani ya website (kwa mpangilio)."""
    out = []
    for key, t in TEMPLATES.items():
        if website_type in t['types']:
            out.append({'key': key, **t})
    return out or [{'key': 'clean_start', **TEMPLATES['clean_start']}]


def all_templates():
    return [{'key': k, **t} for k, t in TEMPLATES.items()]


def apply_template(site, template_key):
    """Weka design ya template kwenye site: nav layout, global css, na pages."""
    t = TEMPLATES.get(template_key) or TEMPLATES['clean_start']
    site.template_key = template_key if template_key in TEMPLATES else 'clean_start'
    site.nav_layout = t['nav_layout']
    site.global_css = t['global_css']
    site.save(update_fields=['template_key', 'nav_layout', 'global_css'])
    for slug, html in t.get('pages', {}).items():
        page = site.pages.filter(slug=slug).first()
        if page:
            page.html_cache = html
            page.grapes_data = {}
            page.save(update_fields=['html_cache', 'grapes_data', 'updated_at'])
