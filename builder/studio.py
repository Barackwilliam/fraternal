"""
Website Studio — kujenga website hatua kwa hatua.

TATIZO

Dashboard ilikuwa na kila kitu ukurasa mmoja: templates, rangi, navbar,
pages, mawasiliano. Mteja mpya hakujua aanzie wapi, na kila chaguo
lilihitaji kuhifadhi kisha kufungua site kwenye tab nyingine kuona matokeo.

SULUHISHO

Hatua 6, moja baada ya nyingine, kila moja na hakikisho la moja kwa moja
(iframe ya /studio/preview/) linalobadilika papo hapo mteja akibonyeza
chaguo — kabla hajahifadhi:

  1. Biashara  — jina, tagline (✨ AI), logo, mawasiliano
  2. Mtindo    — rangi tayari au yako mwenyewe, nav nyeusi/nyeupe, font
  3. Header    — Chagua (14) · ✨ AI · 💻 Code
  4. Footer    — Chagua (12) · ✨ AI · 💻 Code
  5. Kurasa    — kila ukurasa: drag & drop · 💻 Code · ✨ AI; ZIP; maudhui
  6. Publish

Hatua zilizokamilika zinahifadhiwa kwenye theme_settings['studio_done'].
Studio haitumii three.js wala background ya WebGL — inafunguka haraka.
"""
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .layouts import FONTS, PALETTES
from .nav_presets import FOOTERS, HEADERS, get_preset_catalog
from .views import _my_site

STEPS = [
    ('business', 'Business', 'Name, logo & contact'),
    ('style', 'Colors & Font', 'Your brand look'),
    ('header', 'Header & Menu', 'Top bar or sidebar'),
    ('footer', 'Footer', 'Bottom of every page'),
    ('pages', 'Pages & Content', 'Build each page'),
    ('publish', 'Go Live', 'Publish your site'),
]
STEP_KEYS = [k for k, _, _ in STEPS]
HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def _done(site):
    return set((site.theme_settings or {}).get('studio_done', []))


def _mark_done(site, step):
    ts = dict(site.theme_settings or {})
    done = set(ts.get('studio_done', []))
    done.add(step)
    ts['studio_done'] = sorted(done)
    site.theme_settings = ts


def studio_progress(site):
    """Kwa dashboard: (hatua zilizokamilika, jumla, hatua inayofuata)."""
    done = _done(site)
    nxt = next((k for k in STEP_KEYS if k not in done), 'publish')
    return len(done & set(STEP_KEYS)), len(STEP_KEYS), nxt


def _save_step(request, site, step):
    """Hifadhi fomu ya hatua. Inarudisha ujumbe wa kosa au None."""
    p = request.POST
    fields = []
    if step == 'business':
        name = (p.get('site_name') or '').strip()
        if not name:
            return 'Enter your business name.'
        site.site_name = name[:120]
        for f, n in (('tagline', 200), ('contact_phone', 30), ('whatsapp_number', 30),
                     ('contact_email', 254), ('contact_address', 200), ('logo_url', 200)):
            setattr(site, f, (p.get(f) or '').strip()[:n])
        fields = ['site_name', 'tagline', 'contact_phone', 'whatsapp_number',
                  'contact_email', 'contact_address', 'logo_url']
    elif step == 'style':
        accent = (p.get('accent_color') or '').strip()
        if HEX_RE.match(accent):
            site.accent_color = accent
        site.dark_nav = p.get('dark_nav') == 'on'
        font = p.get('font', 'system')
        ts = dict(site.theme_settings or {})
        ts['font'] = font if font in FONTS else 'system'
        site.theme_settings = ts
        fields = ['accent_color', 'dark_nav']
    elif step == 'header':
        if p.get('mode') == 'custom':
            html = (p.get('html') or '').strip()
            if not html:
                return 'Write or generate your header code first — or pick a ready design.'
            site.custom_nav_html = html[:40000]
            site.nav_preset = ''
        else:
            key = p.get('preset', '')
            if key not in HEADERS:
                return 'Pick a header design.'
            site.nav_preset, site.custom_nav_html = key, ''
        fields = ['nav_preset', 'custom_nav_html']
    elif step == 'footer':
        if p.get('mode') == 'custom':
            html = (p.get('html') or '').strip()
            if not html:
                return 'Write or generate your footer code first — or pick a ready design.'
            site.custom_footer_html = html[:40000]
        else:
            key = p.get('preset', '')
            if key not in FOOTERS:
                return 'Pick a footer design.'
            site.footer_preset, site.custom_footer_html = key, ''
        fields = ['footer_preset', 'custom_footer_html']
    elif step == 'publish':
        site.is_published = True
        fields = ['is_published']

    _mark_done(site, step)
    site.save(update_fields=fields + ['theme_settings'])
    site.bump_version()
    return None


@login_required
def studio(request, site_id, step=None):
    site = _my_site(request, site_id)
    step = step or studio_progress(site)[2]
    if step not in STEP_KEYS:
        raise Http404

    if request.method == 'POST':
        error = _save_step(request, site, step)
        if error:
            messages.error(request, error)
            return redirect('builder:studio_step', site_id=site.id, step=step)
        if step == 'publish':
            messages.success(request, 'Your website is live! 🎉')
            return redirect('builder:studio_step', site_id=site.id, step='publish')
        nxt = STEP_KEYS[STEP_KEYS.index(step) + 1]
        return redirect('builder:studio_step', site_id=site.id, step=nxt)

    idx = STEP_KEYS.index(step)
    done = _done(site)
    catalog = get_preset_catalog()
    return render(request, 'builder/studio.html', {
        'site': site,
        'step': step,
        'step_num': idx + 1,
        'step_title': STEPS[idx][1],
        'steps': [{'key': k, 'title': t, 'sub': s, 'num': i + 1, 'done': k in done,
                   'current': k == step} for i, (k, t, s) in enumerate(STEPS)],
        'prev_step': STEP_KEYS[idx - 1] if idx else None,
        'next_step': STEP_KEYS[idx + 1] if idx + 1 < len(STEPS) else None,
        'progress_pct': int(len(done & set(STEP_KEYS)) / len(STEPS) * 100),
        'headers_side': [h for h in catalog['nav'] if h['kind'] == 'side'],
        'headers_top': [h for h in catalog['nav'] if h['kind'] == 'top'],
        'footers': catalog['footer'],
        'palettes': PALETTES,
        'fonts': [(k, v[0]) for k, v in FONTS.items()],
        'current_font': (site.theme_settings or {}).get('font', 'system'),
        'pages': site.pages.all(),
        'collections': site.collections.all(),
        'preview_url': reverse('builder:studio_preview', args=[site.id]),
    })


@login_required
@xframe_options_sameorigin
def studio_preview(request, site_id):
    """
    Hakikisho la site ndani ya Studio, likiwa na chaguo ambazo HAZIJAHIFADHIWA
    bado (?header=&footer=&accent=&dark=&font=&page=). Site inabadilishwa
    kwenye memory tu — database haiguswi.

    Iko kwenye domain ya dashboard (si subdomain ya mteja) kwa sababu
    iframe ya domain nyingine ingezuiwa. @xframe_options_sameorigin inaruhusu
    iframe ya Studio hata pale X_FRAME_OPTIONS ya mfumo ni DENY.
    """
    from . import public_views
    from .rendering import render_page_html, render_raw_document

    site = _my_site(request, site_id)
    g = request.GET
    # "▶ Preview this code" inatuma code ambayo haijahifadhiwa kwa POST
    if request.method == 'POST':
        if 'header_html' in request.POST:
            site.custom_nav_html = request.POST['header_html'][:40000]
        if 'footer_html' in request.POST:
            site.custom_footer_html = request.POST['footer_html'][:40000]
    if g.get('header') in HEADERS:
        site.nav_preset, site.custom_nav_html = g['header'], ''
    if g.get('footer') in FOOTERS:
        site.footer_preset, site.custom_footer_html = g['footer'], ''
    if HEX_RE.match(g.get('accent', '')):
        site.accent_color = g['accent']
    if g.get('dark') in ('0', '1'):
        site.dark_nav = g['dark'] == '1'
    if g.get('font') in FONTS:
        site.theme_settings = {**(site.theme_settings or {}), 'font': g['font']}

    slug = g.get('page') or 'home'
    page = site.pages.filter(slug=slug).first() or site.pages.first()
    if page is None:
        return HttpResponse('<p style="font-family:sans-serif;padding:40px">Add a page to see a preview.</p>')
    if page.raw_document:
        return HttpResponse(render_raw_document(site, page))
    return render(request, 'builder/public/page.html', public_views._ctx(site, {
        'page': page,
        'page_html': render_page_html(site, page),
        'is_preview': True,
    }))
