"""Code Studio na Taarifa za Biashara — njia rahisi za mteja kusimamia website.

CODE STUDIO
    /builder/site/<id>/pages/<page>/code/
    Mteja anabandika HTML/CSS yake, anaona hakikisho pembeni, na anahifadhi.
    Code inahifadhiwa KAMA ILIVYO — haipiti GrapesJS, ambayo ingeondoa
    <script>, kupoteza <head>, na kuandika muundo upya.

TAARIFA ZA BIASHARA
    /builder/site/<id>/info/
    Jina, simu, WhatsApp, email, anwani, logo na rangi — kwenye ukurasa wake.
    Zilikuwa chini kabisa ya dashboard, chini ya sehemu saba nyingine; mteja
    aliyetaka kubadilisha namba ya simu hakuweza kuzipata.
"""
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ClientWebsite, SitePage
from .rendering import render_shortcodes

# Kikomo cha ukubwa — ukurasa mmoja wa HTML haupaswi kuzidi hiki.
# Unazuia mtu kubandika faili la MB 50 lenye picha za base64.
MAX_CODE = 1_500_000

# Shortcodes zinazoonyeshwa kwenye menyu ya Code Studio
SHORTCODES = [
    ('[[site:name]]', 'Jina la biashara'),
    ('[[site:tagline]]', 'Kauli mbiu'),
    ('[[site:phone]]', 'Namba ya simu'),
    ('[[site:whatsapp]]', 'Kitufe cha WhatsApp'),
    ('[[site:email]]', 'Email'),
    ('[[site:address]]', 'Anwani'),
    ('[[site:logo]]', 'Logo'),
    ('[[form:inquiry]]', 'Fomu ya maswali ya wateja'),
]


def _my_site(request, site_id):
    return get_object_or_404(ClientWebsite, id=site_id, owner=request.user)


# ══════════════════════════════════════════════════════════
#  CODE STUDIO
# ══════════════════════════════════════════════════════════

@login_required
def code_studio(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)

    if page.mode == 'code' or page.code_html:
        html, css = page.code_html, page.code_css
    else:
        # Mara ya kwanza: anza na muundo wa sasa wa visual editor,
        # ili mteja asianze na ukurasa mtupu.
        html, css = page.html_cache, page.css_cache

    collections = [(f'[[collection:{c.slug}]]', f'Orodha ya {c.name}')
                   for c in site.collections.all()]
    return render(request, 'builder/code_studio.html', {
        'site': site,
        'page': page,
        'pages': site.pages.order_by('sort_order', 'id'),
        'start_html': html,
        'start_css': css,
        'shortcodes': SHORTCODES + collections,
        'max_code': MAX_CODE,
    })


def _read(request):
    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        return None, None
    return (data.get('html') or ''), (data.get('css') or '')


@login_required
@require_POST
def code_save(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    html, css = _read(request)
    if html is None:
        return JsonResponse({'ok': False, 'error': 'Data haikusomeka.'}, status=400)
    if len(html) + len(css) > MAX_CODE:
        return JsonResponse({'ok': False, 'error': 'Code ni kubwa mno (zaidi ya 1.5 MB). '
                             'Picha ziweke kama link, si ndani ya code.'}, status=400)
    if not html.strip():
        return JsonResponse({'ok': False, 'error': 'Ukurasa hauwezi kuwa mtupu.'}, status=400)

    page.code_html = html
    page.code_css = css
    page.mode = 'code'
    page.code_updated_at = timezone.now()
    page.save(update_fields=['code_html', 'code_css', 'mode', 'code_updated_at'])
    site.bump_version()          # futa cache — mabadiliko yaonekane papo hapo

    url = site.public_url.rstrip('/') + ('/' if page.slug == 'home' else f'/p/{page.slug}/')
    return JsonResponse({
        'ok': True,
        'full_page': page.is_full_document,
        'url': url,
        'published': site.is_published,
        'saved_at': timezone.localtime(page.code_updated_at).strftime('%H:%M'),
    })


@login_required
@require_POST
def code_preview(request, site_id, page_id):
    """Hakikisho — linatumia template ile ile ya umma, kwa hiyo linafanana kabisa na live."""
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    html, css = _read(request)
    if html is None:
        return HttpResponse('Data haikusomeka', status=400)

    body = render_shortcodes(site, html)
    head = html.lstrip()[:600].lower()
    if head.startswith('<!doctype') or '<html' in head:
        return HttpResponse(body)

    from .public_views import _ctx
    # Kitu cha muda chenye code mpya — HAKIHIFADHIWI
    page.mode, page.code_html, page.code_css = 'code', html, css
    return HttpResponse(render_to_string(
        'builder/public/page.html', _ctx(site, {'page': page, 'page_html': body}), request=request))


@login_required
@require_POST
def code_to_visual(request, site_id, page_id):
    """Rudi kwenye visual editor. Code haifutwi — inabaki kwa ajili ya kurudi baadaye."""
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    page.mode = 'visual'
    page.save(update_fields=['mode'])
    site.bump_version()
    messages.success(request, f'"{page.title}" sasa inatumia visual editor. Code yako imehifadhiwa, unaweza kurudi kwake wakati wowote.')
    return redirect('builder:page_editor', site_id=site.id, page_id=page.id)


# ══════════════════════════════════════════════════════════
#  TAARIFA ZA BIASHARA
# ══════════════════════════════════════════════════════════

INFO_FIELDS = ('site_name', 'tagline', 'contact_phone', 'whatsapp_number',
               'contact_email', 'contact_address', 'logo_url', 'accent_color')


@login_required
def business_info(request, site_id):
    site = _my_site(request, site_id)

    if request.method == 'POST':
        errors = []
        for f in INFO_FIELDS:
            if f in request.POST:
                setattr(site, f, request.POST[f].strip())
        if not site.site_name:
            errors.append('Jina la biashara linahitajika.')
        if site.accent_color and not (site.accent_color.startswith('#') and len(site.accent_color) in (4, 7)):
            errors.append('Rangi iwe kama #1a73e8.')
        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            site.save()
            site.bump_version()
            messages.success(request, 'Taarifa zimehifadhiwa. Zimebadilika kila mahali kwenye website yako.')
            return redirect('builder:business_info', site_id=site.id)

    filled = sum(1 for f in ('contact_phone', 'whatsapp_number', 'contact_email',
                             'contact_address', 'logo_url', 'tagline') if getattr(site, f, ''))
    return render(request, 'builder/business_info.html', {
        'site': site,
        'filled': filled,
        'filled_pct': round(filled * 100 / 6),
    })
