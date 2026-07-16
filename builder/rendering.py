"""
Shortcode rendering — inaruhusu mteja kuweka collections POPOTE kwenye
design yake. Ndani ya editor (GrapesJS) kuna blocks zinazoingiza:

    [[collection:packages]]      → grid ya cards za packages zake
    [[collection:trips]]         → grid ya trips
    [[site:name]] [[site:phone]] [[site:email]] [[site:address]]
    [[site:tagline]] [[site:whatsapp]] [[site:logo]]

Wakati wa kuserve page, shortcodes zinabadilishwa na content halisi
kutoka database — kwa hiyo mteja akiongeza package mpya, inaonekana
kila mahali alipoweka block hiyo, bila kugusa design.
"""
import re
import html as html_lib

from django.core.cache import cache

SHORTCODE_RE = re.compile(r'\[\[(collection|site|form):([a-z0-9_-]+)\]\]')

CARD_CSS = """
<style>
.jt-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(272px,1fr));gap:26px;margin:34px 0;}
.jt-card{background:rgba(255,255,255,.75);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,.6);border-radius:18px;overflow:hidden;
  box-shadow:0 4px 22px rgba(10,25,18,.1);display:flex;flex-direction:column;color:#20261f;text-decoration:none;
  transition:transform .3s cubic-bezier(.22,.9,.3,1),box-shadow .3s;}
.jt-card:hover{transform:translateY(-7px);box-shadow:0 18px 44px rgba(10,25,18,.18);}
.jt-card-img-wrap{overflow:hidden;height:196px;background:linear-gradient(100deg,#e8e6dd 40%,#f2f0e8 50%,#e8e6dd 60%);
  background-size:200% 100%;animation:jtskel 1.4s infinite;}
@keyframes jtskel{to{background-position:-200% 0}}
.jt-card-img{width:100%;height:196px;object-fit:cover;display:block;transition:transform .5s cubic-bezier(.22,.9,.3,1);}
.jt-card:hover .jt-card-img{transform:scale(1.07);}
.jt-card-body{padding:19px 21px 23px;flex:1;display:flex;flex-direction:column;}
.jt-card-title{font-size:19px;font-weight:800;margin:0 0 6px;letter-spacing:-.01em;}
.jt-card-desc{font-size:14px;color:#5a635a;line-height:1.55;margin:0 0 12px;flex:1;}
.jt-card-meta{font-size:13px;color:#7d857c;margin-bottom:6px;}
.jt-card-price{font-size:18px;font-weight:800;color:var(--accent,#c07f16);margin-top:auto;
  filter:brightness(.75) saturate(1.4);}
.jt-badge{display:inline-block;background:color-mix(in srgb,var(--accent,#e8a13c) 20%,#fff);
  color:color-mix(in srgb,var(--accent,#e8a13c) 60%,#000);font-size:12px;font-weight:800;
  padding:4px 12px;border-radius:20px;margin-bottom:9px;width:fit-content;}
.jt-empty{padding:38px;text-align:center;color:#98a096;border:2px dashed #d8d5c8;border-radius:16px;margin:26px 0;
  background:rgba(255,255,255,.4);}
</style>
"""


def _esc(value):
    return html_lib.escape(str(value)) if value is not None else ''


def _fmt_price(value):
    try:
        n = float(str(value).replace(',', ''))
        return f'{n:,.0f}'
    except (ValueError, TypeError):
        return _esc(value)


def render_collection(site, slug):
    """Rudisha HTML ya grid ya items za collection."""
    collection = site.collections.filter(slug=slug).first()
    if collection is None:
        return f'<div class="jt-empty">Collection "{_esc(slug)}" does not exist.</div>'

    items = collection.items.filter(is_visible=True)
    if not items.exists():
        return (f'<div class="jt-empty">{collection.icon} No '
                f'{_esc(collection.name)} yet — add some from your dashboard.</div>')

    price_key = next(
        (f['key'] for f in collection.fields if f.get('type') == 'price'), None
    )
    date_key = next(
        (f['key'] for f in collection.fields if f.get('type') == 'date'), None
    )

    cards = []
    for item in items:
        img = ''
        if item.image_url:
            # Uploadcare inline resize — hakuna processing server-side
            src = item.image_url.rstrip('/') + '/-/resize/600x/'
            img = (f'<div class="jt-card-img-wrap"><img class="jt-card-img" src="{_esc(src)}" alt="{_esc(item.title)}" loading="lazy"></div>')

        desc = _esc(item.data.get('description', ''))[:150]
        duration = item.data.get('duration', '')
        meta_bits = []
        if duration:
            meta_bits.append(f'⏱ {_esc(duration)}')
        if date_key and item.data.get(date_key):
            meta_bits.append(f'📅 {_esc(item.data[date_key])}')
        venue = item.data.get('venue') or item.data.get('region') or ''
        if venue:
            meta_bits.append(f'📍 {_esc(venue)}')
        meta = f'<div class="jt-card-meta">{" · ".join(meta_bits)}</div>' if meta_bits else ''

        price = ''
        if price_key and item.data.get(price_key):
            price = f'<div class="jt-card-price">{_fmt_price(item.data[price_key])}</div>'

        badge = '<span class="jt-badge">⭐ Featured</span>' if item.is_featured else ''
        url = f'/c/{collection.slug}/{item.slug}/'

        cards.append(
            f'<a class="jt-card" href="{url}">{img}<div class="jt-card-body">{badge}'
            f'<h3 class="jt-card-title">{_esc(item.title)}</h3>'
            f'<p class="jt-card-desc">{desc}…</p>{meta}{price}</div></a>'
        )

    return CARD_CSS + f'<div class="jt-grid">{"".join(cards)}</div>'


FORM_CSS = """
<style>
.jt-form{max-width:560px;margin:26px auto;background:rgba(255,255,255,.85);border:1px solid rgba(0,0,0,.08);
  border-radius:16px;padding:26px;box-shadow:0 6px 26px rgba(10,25,18,.1);}
.jt-form h3{margin:0 0 6px;font-size:21px;}
.jt-form p.jt-sub{margin:0 0 16px;color:#6b7268;font-size:14px;}
.jt-form label{display:block;font-size:13px;font-weight:700;margin:12px 0 5px;color:#333;}
.jt-form input,.jt-form textarea{width:100%;padding:11px 13px;border:1.5px solid #ddd;border-radius:10px;
  font-size:15px;font-family:inherit;box-sizing:border-box;}
.jt-form input:focus,.jt-form textarea:focus{outline:none;border-color:var(--accent,#e8a13c);}
.jt-form textarea{min-height:90px;resize:vertical;}
.jt-form .jt-row{display:flex;gap:12px;flex-wrap:wrap;}
.jt-form .jt-row>div{flex:1;min-width:140px;}
.jt-form button{width:100%;margin-top:18px;padding:14px;border:none;border-radius:11px;font-size:15.5px;
  font-weight:800;cursor:pointer;background:var(--accent,#e8a13c);color:#1c1508;}
.jt-form .jt-hp{position:absolute;left:-9999px;opacity:0;height:0;overflow:hidden;}
.jt-form .jt-ok{background:#dff0e2;color:#1c6b34;border:1px solid #a9dcb5;border-radius:10px;
  padding:12px 15px;margin-bottom:14px;font-size:14px;display:none;}
</style>
"""


def render_inquiry_form(site, item=None):
    """Booking/inquiry form inayopost /inquiry/ ya website husika."""
    item_field = (f'<input type="hidden" name="item_id" value="{item.id}">'
                  if item is not None else '')
    title = f'Book: {_esc(item.title)}' if item is not None else 'Send an Inquiry'
    return FORM_CSS + f"""
<div class="jt-form" id="jt-inquiry">
  <div class="jt-ok" id="jt-ok">✅ Thank you! Your inquiry has been received — we will contact you shortly.</div>
  <h3>{title}</h3>
  <p class="jt-sub">Fill in the form and we will get back to you as soon as possible.</p>
  <form method="post" action="/inquiry/" onsubmit="return jtSend(this)">
    {item_field}
    <input class="jt-hp" type="text" name="website_url" tabindex="-1" autocomplete="off">
    <label>Your Name *</label>
    <input type="text" name="name" required maxlength="120">
    <div class="jt-row">
      <div><label>Phone / WhatsApp *</label>
      <input type="tel" name="phone" required maxlength="40" placeholder="+255 ..."></div>
      <div><label>Email</label>
      <input type="email" name="email" maxlength="120"></div>
    </div>
    <div class="jt-row">
      <div><label>Preferred Date</label>
      <input type="date" name="preferred_date"></div>
      <div><label>Number of People</label>
      <input type="number" name="people_count" min="1" max="10000"></div>
    </div>
    <label>Message</label>
    <textarea name="message" maxlength="3000" placeholder="Tell us what you need..."></textarea>
    <button type="submit">Send Inquiry ✉️</button>
  </form>
</div>
<script>
async function jtSend(f){{
  const btn = f.querySelector('button'); btn.disabled = true; btn.textContent = 'Sending…';
  try {{
    const res = await fetch('/inquiry/', {{method:'POST', body:new FormData(f)}});
    if (res.ok) {{ f.style.display='none'; document.getElementById('jt-ok').style.display='block';
      document.getElementById('jt-inquiry').scrollIntoView({{behavior:'smooth'}}); }}
    else {{ btn.disabled=false; btn.textContent='Send Inquiry ✉️'; alert('Something went wrong. Please try again.'); }}
  }} catch(e) {{ btn.disabled=false; btn.textContent='Send Inquiry ✉️'; alert('Network error. Please try again.'); }}
  return false;
}}
</script>"""


def _site_value(site, key):
    wa = (site.whatsapp_number or site.contact_phone or '').replace('+', '').replace(' ', '')
    mapping = {
        'name': _esc(site.site_name),
        'tagline': _esc(site.tagline),
        'phone': _esc(site.contact_phone),
        'email': _esc(site.contact_email),
        'address': _esc(site.contact_address),
        'whatsapp': f'https://wa.me/{wa}' if wa else '#',
        'logo': _esc(site.logo_url),
    }
    return mapping.get(key, '')


def render_shortcodes(site, html):
    """Badilisha shortcodes zote kwenye HTML ya page."""
    def replacer(match):
        kind, key = match.group(1), match.group(2)
        if kind == 'site':
            return _site_value(site, key)
        if kind == 'form':
            return render_inquiry_form(site)
        return render_collection(site, key)
    return SHORTCODE_RE.sub(replacer, html or '')


def render_page_html(site, page):
    """
    HTML kamili ya page. Cache key ina content_version ya site — kwa hiyo
    mteja akibadilisha KITU CHOCHOTE (page, item, settings), version
    inapanda na cache inajipoteza yenyewe PAPO HAPO. Wageni wanapata
    page kutoka cache moja kwa moja bila queries za collections.
    """
    cache_key = f'jtpage:{site.id}:{page.id}:v{site.content_version}'
    result = cache.get(cache_key)
    if result is None:
        result = render_shortcodes(site, page.html_cache)
        cache.set(cache_key, result, 3600)  # saa 1 — version ndiyo invalidator
    return result
