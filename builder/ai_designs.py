"""
AI Design Variants — kila website ya One-Shot inapata design TOFAUTI.

AI (Pass 1) inachagua `design_style` + `palette` kulingana na mood ya
biashara; hapa tuna layouts 4 tofauti kabisa (muundo, rangi, fonts,
mpangilio wa sections) zinazojengwa kwa content ya AI.

Styles:
  sunset_bold   — hero kubwa ya gradient ya joto, stats strip, cards nene
  clean_minimal — background nyeupe, mistari myembamba, left-aligned, airy
  dark_luxury   — nyeusi + serif feel, dhahabu/premium, centered elegance
  fresh_split   — hero ya columns mbili (maandishi + panel ya rangi), rounded
"""

STYLES = ('sunset_bold', 'clean_minimal', 'dark_luxury', 'fresh_split')


def _esc(t):
    return (str(t or '').replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def _why_cards(why, card_css, title_css, text_css):
    cards = ''
    for w in (why or [])[:3]:
        if not isinstance(w, dict):
            continue
        t, d = _esc(w.get('title', ''))[:80], _esc(w.get('description', ''))[:300]
        if t or d:
            cards += (f'<div style="{card_css}">'
                      f'<h3 style="{title_css}">{t}</h3>'
                      f'<p style="{text_css}">{d}</p></div>')
    return cards


def render_home(style, palette, plan, primary_col):
    """Rudisha HTML ya home page kwa style husika. Daima ina [[form:inquiry]]."""
    if style not in STYLES:
        style = 'sunset_bold'
    p1 = palette.get('primary', '#e8734a')
    p2 = palette.get('deep', '#1c1030')

    headline = _esc(plan.get('hero_headline', ''))
    subline = _esc(plan.get('hero_subline', ''))
    about = _esc(plan.get('about_us', ''))
    tagline = _esc(plan.get('tagline', ''))
    why = plan.get('why_choose_us', [])
    col_slug = primary_col.slug if primary_col else 'services'
    col_name = _esc(primary_col.name) if primary_col else 'Services'

    if style == 'clean_minimal':
        return (
            f'<section style="padding:110px 24px 80px;background:#fcfbf8">'
            f'<div style="max-width:900px;margin:0 auto">'
            f'<p style="letter-spacing:4px;text-transform:uppercase;color:{p1};font-size:12px;font-weight:800;margin:0 0 18px">[[site:name]]</p>'
            f'<h1 style="font-size:clamp(34px,5.5vw,60px);line-height:1.08;margin:0 0 22px;color:#161616;letter-spacing:-.02em;font-weight:800">{headline}</h1>'
            f'<p style="font-size:18px;color:#5b6156;max-width:560px;line-height:1.75;margin:0 0 34px">{subline}</p>'
            f'<a href="[[site:whatsapp]]" style="display:inline-block;background:#161616;color:#fff;padding:15px 36px;border-radius:6px;text-decoration:none;font-weight:700">Get in Touch →</a>'
            f'</div></section>'
            f'<section style="padding:26px 24px;background:#fcfbf8"><div style="max-width:900px;margin:0 auto;border-top:1px solid #e4e1d8"></div></section>'
            f'<section style="padding:40px 24px 80px;background:#fcfbf8"><div style="max-width:1100px;margin:0 auto">'
            f'<h2 style="font-size:clamp(26px,3.5vw,36px);margin:0 0 6px;color:#161616">{col_name}</h2>'
            f'<p style="color:#8b917f;margin:0 0 8px">{tagline}</p>'
            f'[[collection:{col_slug}]]</div></section>'
            f'<section style="padding:80px 24px;background:#f2efe7"><div style="max-width:1100px;margin:0 auto">'
            f'<h2 style="font-size:clamp(26px,3.5vw,36px);margin:0 0 34px;color:#161616">Why Choose Us</h2>'
            f'<div style="display:flex;flex-wrap:wrap;gap:18px">'
            + _why_cards(why,
                'flex:1;min-width:240px;padding:28px;background:#fcfbf8;border:1px solid #e4e1d8;border-radius:4px',
                'margin:0 0 8px;font-size:18px;color:#161616',
                'margin:0;color:#5b6156;line-height:1.7;font-size:14.5px')
            + f'</div></div></section>'
            f'<section style="padding:80px 24px;background:#fcfbf8"><div style="max-width:760px;margin:0 auto">'
            f'<h2 style="font-size:clamp(26px,3.5vw,36px);margin:0 0 16px;color:#161616">About Us</h2>'
            f'<p style="font-size:16.5px;color:#5b6156;line-height:1.9">{about}</p></div></section>'
            f'[[form:inquiry]]'
        )

    if style == 'dark_luxury':
        return (
            f'<section style="min-height:82vh;display:flex;align-items:center;justify-content:center;text-align:center;'
            f'background:radial-gradient(900px 500px at 50% -10%,{p2},#0a0a0c 70%);color:#f3ede2;padding:90px 24px">'
            f'<div style="max-width:780px">'
            f'<p style="letter-spacing:6px;text-transform:uppercase;color:{p1};font-size:12px;font-weight:700;margin:0 0 22px">✦ [[site:name]] ✦</p>'
            f'<h1 style="font-family:Georgia,\'Times New Roman\',serif;font-size:clamp(36px,6vw,64px);line-height:1.12;margin:0 0 22px;font-weight:500">{headline}</h1>'
            f'<p style="font-size:17px;color:#b9b2a3;line-height:1.8;max-width:560px;margin:0 auto 38px">{subline}</p>'
            f'<a href="[[site:whatsapp]]" style="display:inline-block;border:1.5px solid {p1};color:{p1};padding:15px 44px;border-radius:2px;text-decoration:none;font-weight:600;letter-spacing:2px;text-transform:uppercase;font-size:13px">Enquire</a>'
            f'</div></section>'
            f'<section style="padding:90px 24px;background:#0a0a0c;color:#f3ede2"><div style="max-width:1100px;margin:0 auto;text-align:center">'
            f'<h2 style="font-family:Georgia,serif;font-size:clamp(28px,4vw,42px);font-weight:500;margin:0 0 8px">{col_name}</h2>'
            f'<p style="color:#8f887a;margin:0 0 10px;font-style:italic">{tagline}</p>'
            f'[[collection:{col_slug}]]</div></section>'
            f'<section style="padding:90px 24px;background:#100f12;color:#f3ede2"><div style="max-width:1100px;margin:0 auto">'
            f'<h2 style="font-family:Georgia,serif;text-align:center;font-size:clamp(28px,4vw,42px);font-weight:500;margin:0 0 44px">The Difference</h2>'
            f'<div style="display:flex;flex-wrap:wrap;gap:20px">'
            + _why_cards(why,
                f'flex:1;min-width:240px;padding:32px;background:transparent;border:1px solid #2a2830;border-top:2px solid {p1}',
                'margin:0 0 10px;font-size:19px;font-family:Georgia,serif;font-weight:500',
                'margin:0;color:#8f887a;line-height:1.8;font-size:14.5px')
            + f'</div></div></section>'
            f'<section style="padding:90px 24px;background:#0a0a0c;color:#f3ede2"><div style="max-width:720px;margin:0 auto;text-align:center">'
            f'<h2 style="font-family:Georgia,serif;font-size:clamp(28px,4vw,42px);font-weight:500;margin:0 0 20px">Our Story</h2>'
            f'<p style="font-size:16.5px;color:#b9b2a3;line-height:2">{about}</p></div></section>'
            f'[[form:inquiry]]'
        )

    if style == 'fresh_split':
        return (
            f'<section style="display:flex;flex-wrap:wrap;min-height:76vh;background:#ffffff">'
            f'<div style="flex:1;min-width:300px;display:flex;align-items:center;padding:70px clamp(24px,5vw,70px)">'
            f'<div><p style="display:inline-block;background:color-mix(in srgb,{p1} 14%,#fff);color:{p1};padding:7px 16px;border-radius:100px;font-size:12.5px;font-weight:800;margin:0 0 20px">[[site:name]]</p>'
            f'<h1 style="font-size:clamp(32px,4.8vw,54px);line-height:1.1;margin:0 0 18px;color:#17202a;font-weight:800;letter-spacing:-.02em">{headline}</h1>'
            f'<p style="font-size:16.5px;color:#66707c;line-height:1.75;max-width:480px;margin:0 0 30px">{subline}</p>'
            f'<a href="[[site:whatsapp]]" style="display:inline-block;background:{p1};color:#fff;padding:15px 34px;border-radius:100px;text-decoration:none;font-weight:800;box-shadow:0 10px 26px color-mix(in srgb,{p1} 40%,transparent)">💬 Talk to Us</a></div></div>'
            f'<div style="flex:1;min-width:300px;min-height:340px;background:linear-gradient(160deg,{p1},{p2});display:flex;align-items:center;justify-content:center;padding:50px">'
            f'<div style="max-width:340px;background:rgba(255,255,255,.14);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:30px;color:#fff">'
            f'<p style="font-size:15px;line-height:1.7;margin:0;font-weight:600">“{tagline}”</p></div></div>'
            f'</section>'
            f'<section style="padding:80px 24px;background:#f7f9fb"><div style="max-width:1100px;margin:0 auto;text-align:center">'
            f'<h2 style="font-size:clamp(26px,3.8vw,38px);margin:0 0 8px;color:#17202a;font-weight:800">{col_name}</h2>'
            f'[[collection:{col_slug}]]</div></section>'
            f'<section style="padding:80px 24px;background:#ffffff"><div style="max-width:1100px;margin:0 auto">'
            f'<h2 style="text-align:center;font-size:clamp(26px,3.8vw,38px);margin:0 0 40px;color:#17202a;font-weight:800">Why People Choose Us</h2>'
            f'<div style="display:flex;flex-wrap:wrap;gap:20px">'
            + _why_cards(why,
                f'flex:1;min-width:240px;padding:30px;background:#f7f9fb;border-radius:18px;border:1px solid #e8edf2',
                f'margin:0 0 8px;font-size:18px;color:{p1};font-weight:800',
                'margin:0;color:#66707c;line-height:1.7;font-size:14.5px')
            + f'</div></div></section>'
            f'<section style="padding:80px 24px;background:#f7f9fb"><div style="max-width:780px;margin:0 auto;text-align:center">'
            f'<h2 style="font-size:clamp(26px,3.8vw,38px);margin:0 0 16px;color:#17202a;font-weight:800">About Us</h2>'
            f'<p style="font-size:16.5px;color:#66707c;line-height:1.85">{about}</p></div></section>'
            f'[[form:inquiry]]'
        )

    # ── default: sunset_bold ──
    return (
        f'<section style="min-height:80vh;display:flex;align-items:center;justify-content:center;text-align:center;'
        f'background:linear-gradient(160deg,{p2} 10%,{p1} 130%);color:#fff;padding:90px 24px;position:relative;overflow:hidden">'
        f'<div style="position:relative;z-index:1;max-width:820px">'
        f'<p style="letter-spacing:5px;text-transform:uppercase;color:#fff;opacity:.85;font-size:13px;font-weight:800;margin:0 0 16px">Welcome to [[site:name]]</p>'
        f'<h1 style="font-size:clamp(36px,6.4vw,62px);line-height:1.08;margin:0 0 18px;font-weight:900;letter-spacing:-.02em;text-shadow:0 4px 30px rgba(0,0,0,.3)">{headline}</h1>'
        f'<p style="font-size:clamp(15px,2vw,18px);opacity:.92;margin:0 auto 34px;max-width:620px;line-height:1.7">{subline}</p>'
        f'<a href="[[site:whatsapp]]" style="display:inline-block;background:#fff;color:{p2};padding:16px 42px;border-radius:14px;font-weight:900;text-decoration:none;font-size:16px;box-shadow:0 12px 34px rgba(0,0,0,.3)">Get in Touch on WhatsApp</a>'
        f'</div>'
        f'<div style="position:absolute;inset:auto 0 0 0;height:120px;background:linear-gradient(transparent,rgba(0,0,0,.25))"></div>'
        f'</section>'
        f'<section style="padding:80px 24px;background:#fdfaf5"><div style="max-width:1100px;margin:0 auto;text-align:center">'
        f'<h2 style="font-size:clamp(28px,4vw,40px);margin:0 0 8px;color:#241a12;font-weight:900">{col_name}</h2>'
        f'<p style="color:#8a7f70;margin:0 auto 10px;max-width:520px">{tagline}</p>'
        f'[[collection:{col_slug}]]</div></section>'
        f'<section style="padding:80px 24px;background:linear-gradient(180deg,#fdfaf5,#f6efe3)"><div style="max-width:1100px;margin:0 auto">'
        f'<h2 style="text-align:center;font-size:clamp(28px,4vw,40px);margin:0 0 40px;color:#241a12;font-weight:900">Why Choose Us</h2>'
        f'<div style="display:flex;flex-wrap:wrap;gap:20px">'
        + _why_cards(why,
            f'flex:1;min-width:240px;padding:30px;background:#fff;border-radius:18px;box-shadow:0 10px 30px rgba(90,60,20,.08);border-top:4px solid {p1}',
            'margin:0 0 8px;font-size:19px;color:#241a12;font-weight:800',
            'margin:0;color:#8a7f70;line-height:1.7;font-size:14.5px')
        + f'</div></div></section>'
        f'<section style="padding:80px 24px;background:#fdfaf5"><div style="max-width:780px;margin:0 auto;text-align:center">'
        f'<h2 style="font-size:clamp(28px,4vw,40px);margin:0 0 16px;color:#241a12;font-weight:900">About Us</h2>'
        f'<p style="font-size:17px;color:#8a7f70;line-height:1.85">{about}</p></div></section>'
        f'[[form:inquiry]]'
    )
