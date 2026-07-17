"""
Dashboard ya mteja ("cPanel" ya JamiiTek Builder) — inafanya kazi kwenye
platform kuu (jamiitek.com/builder/...).
"""
import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import (
    ClientWebsite, SitePage, SiteCollection, SiteItem, SiteAsset, SiteInquiry,
    available_website_types, validate_subdomain,
)
from .site_templates import all_templates, apply_template


def _register_subdomain(site):
    """
    IMEZIMWA by default — subdomains zinaishi kwenye database tu na
    middleware inazi-route. Wildcard *.jamiitek.com kwenye Render + CNAME
    moja ya Cloudflare vinatosheleza subdomains ZOTE bila kusajili chochote.

    Washa TU kama dharura (wildcard ikizuiwa) kwa env var:
        BUILDER_AUTO_REGISTER_SUBDOMAINS=1
    (kumbuka: kila domain ya ziada Render ina gharama — haifai kwa wingi)
    """
    import os
    if os.getenv('BUILDER_AUTO_REGISTER_SUBDOMAINS') != '1':
        return
    try:
        from django.conf import settings as dj_settings
        from . import render_api
        if render_api.is_configured():
            base = getattr(dj_settings, 'BUILDER_BASE_DOMAIN', 'jamiitek.com')
            render_api.add_custom_domain(f'{site.subdomain}.{base}')
    except Exception:
        import logging
        logging.getLogger(__name__).exception('subdomain auto-register failed')


def _my_site(request, site_id):
    return get_object_or_404(ClientWebsite, id=site_id, owner=request.user)


# ── Signup + kuunda website ─────────────────────────────

def signup(request):
    """Account mpya + website ya kwanza kwa hatua moja."""
    if request.user.is_authenticated:
        return redirect('builder:my_sites')

    form = UserCreationForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        subdomain = (request.POST.get('subdomain') or '').lower().strip()
        site_name = (request.POST.get('site_name') or '').strip()
        website_type = request.POST.get('website_type') or 'default'
        try:
            validate_subdomain(subdomain)
            if ClientWebsite.objects.filter(subdomain=subdomain).exists():
                raise ValidationError('This subdomain is already taken. Choose another one.')
            if not site_name:
                raise ValidationError('Enter your website name.')
            with transaction.atomic():
                user = form.save()
                site = ClientWebsite.objects.create(
                    owner=user, subdomain=subdomain,
                    site_name=site_name, website_type=website_type,
                )
                site.bootstrap_from_schema()
                apply_template(site, request.POST.get('template_key', 'clean_start'))
            _register_subdomain(site)
            login(request, user)
            messages.success(request, f'Congratulations! Your website {site.subdomain}.jamiitek.com has been created.')
            return redirect('builder:site_dashboard', site_id=site.id)
        except ValidationError as e:
            error = ' '.join(e.messages)

    return render(request, 'builder/signup.html', {
        'form': form, 'error': error,
        'website_types': available_website_types(),
        'site_templates': all_templates(),
    })


@login_required
def my_sites(request):
    sites = request.user.websites.all()
    if sites.count() == 1:
        return redirect('builder:site_dashboard', site_id=sites.first().id)
    return render(request, 'builder/my_sites.html', {'sites': sites})


@login_required
def create_site(request):
    """Website ya ziada kwa mteja aliyekwishakuwa na account."""
    error = None
    if request.method == 'POST':
        subdomain = (request.POST.get('subdomain') or '').lower().strip()
        site_name = (request.POST.get('site_name') or '').strip()
        website_type = request.POST.get('website_type') or 'default'
        try:
            validate_subdomain(subdomain)
            if ClientWebsite.objects.filter(subdomain=subdomain).exists():
                raise ValidationError('This subdomain is already taken.')
            if not site_name:
                raise ValidationError('Enter the website name.')
            site = ClientWebsite.objects.create(
                owner=request.user, subdomain=subdomain,
                site_name=site_name, website_type=website_type,
            )
            site.bootstrap_from_schema()
            apply_template(site, request.POST.get('template_key', 'clean_start'))
            _register_subdomain(site)
            return redirect('builder:site_dashboard', site_id=site.id)
        except ValidationError as e:
            error = ' '.join(e.messages)
    return render(request, 'builder/create_site.html', {
        'error': error, 'website_types': available_website_types(),
        'site_templates': all_templates(),
    })


# ── Dashboard ───────────────────────────────────────────

def get_started(request):
    """Public chooser: order a website, buy one, or build it yourself."""
    return render(request, 'builder/get_started.html')


@login_required
def tutorial(request):
    """Mwongozo kamili wa kutumia builder — hatua kwa hatua."""
    return render(request, 'builder/tutorial.html', {
        'website_types': available_website_types(),
        'first_site': request.user.websites.first(),
    })


@login_required
def site_dashboard(request, site_id):
    from django.db.models import Count
    site = _my_site(request, site_id)
    collections = site.collections.annotate(items_count=Count('items'))
    total_items = sum(c.items_count for c in collections)
    # Hatua za kuanza (onboarding) — zina-tick automatic
    pages = site.pages.all()
    has_items = total_items > 0
    has_contact = bool(site.contact_phone or site.whatsapp_number)
    has_design = site.pages.exclude(grapes_data={}).exists()
    col_list = list(collections)
    first_col = col_list[0] if col_list else None
    first_page = pages[0] if pages else None
    steps = [
        {'done': has_contact,
         'label': 'Fill in your contact details (phone / WhatsApp)', 'url': '#settings'},
        {'done': has_items,
         'label': f'Add your first {first_col.name_singular if first_col else "content item"}',
         'url': (f'/builder/site/{site.id}/collections/{first_col.id}/new/' if first_col else '#')},
        {'done': has_design, 'label': 'Open the editor and customize your Home design',
         'url': (f'/builder/site/{site.id}/pages/{first_page.id}/edit/' if first_page else '#')},
        {'done': site.is_published, 'label': 'Publish — take your website live',
         'url': '#publish'},
    ]
    done_count = sum(1 for st in steps if st['done'])
    return render(request, 'builder/dashboard.html', {
        'site': site,
        'pages': pages,
        'collections': col_list,
        'total_items': total_items,
        'site_templates': [t for t in all_templates()
                           if site.website_type in t['types']],
        'onb_steps': steps,
        'onb_done': done_count,
        'onb_total': len(steps),
        'onb_pct': int(done_count / len(steps) * 100),
        'new_inquiries': site.inquiries.filter(status='new').count(),
    })


@login_required
@require_POST
def change_template(request, site_id):
    site = _my_site(request, site_id)
    apply_template(site, request.POST.get('template_key', 'clean_start'))
    messages.success(request, 'Template mpya imewekwa! Design zako za awali za pages za template zimebadilishwa.')
    return redirect('builder:site_dashboard', site_id=site.id)


@login_required
@require_POST
def site_settings_save(request, site_id):
    site = _my_site(request, site_id)
    for field in ('site_name', 'tagline', 'contact_phone', 'contact_email',
                  'contact_address', 'whatsapp_number', 'logo_url',
                  'nav_style', 'accent_color'):
        if field in request.POST:
            setattr(site, field, request.POST[field].strip())
    site.dark_nav = request.POST.get('dark_nav') == 'on'

    domain_changed = False
    old_domain = site.custom_domain
    if site.is_premium and 'custom_domain' in request.POST:
        new_domain = (request.POST['custom_domain'].strip().lower()
                      .replace('https://', '').replace('http://', '')
                      .rstrip('/')) or None
        if new_domain != old_domain:
            site.custom_domain = new_domain
            domain_changed = True

    site.save()
    site.bump_version()
    messages.success(request, 'Website details saved.')

    # ── Auto-registration ya custom domain kwenye Render (bila dashboard) ──
    if domain_changed:
        from . import render_api
        if old_domain:
            render_api.remove_custom_domain(old_domain)
        if site.custom_domain:
            ok, msg = render_api.add_custom_domain(site.custom_domain)
            (messages.success if ok else messages.warning)(request, msg)
            if render_api.check_dns(site.custom_domain):
                messages.success(request,
                    f'DNS check: "{site.custom_domain}" is already pointing to our '
                    'servers — your domain should be live within minutes. ✅')
            else:
                messages.info(request,
                    f'DNS check: "{site.custom_domain}" is not pointing to us yet. '
                    'Add a CNAME record at your registrar: '
                    f'{site.custom_domain} → jamiitek.onrender.com')
    return redirect('builder:site_dashboard', site_id=site.id)


@login_required
@require_POST
def toggle_publish(request, site_id):
    site = _my_site(request, site_id)
    site.is_published = not site.is_published
    site.save(update_fields=['is_published'])
    state = 'is now live' if site.is_published else 'has been unpublished'
    messages.success(request, f'Your website {state}.')
    return redirect('builder:site_dashboard', site_id=site.id)


# ── Pages + Editor ──────────────────────────────────────

@login_required
def page_editor(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    return render(request, 'builder/editor.html', {
        'site': site, 'page': page,
        'collections': site.collections.all(),
        'uploadcare_public_key': _uploadcare_key(),
    })


def _uploadcare_key():
    import os
    return os.getenv('UPLOADCARE_PUBLIC_KEY', '')


@login_required
@require_POST
def page_create(request, site_id):
    site = _my_site(request, site_id)
    title = (request.POST.get('title') or '').strip()
    if not title:
        messages.error(request, 'Enter a page name.')
        return redirect('builder:site_dashboard', site_id=site.id)
    from django.utils.text import slugify
    base = slugify(title)[:70] or 'page'
    slug, n = base, 2
    while site.pages.filter(slug=slug).exists():
        slug = f'{base}-{n}'
        n += 1
    page = SitePage.objects.create(
        website=site, slug=slug, title=title,
        sort_order=site.pages.count(),
        html_cache=f'<section style="padding:60px 20px;max-width:900px;margin:0 auto;"><h1>{title}</h1><p>Anza kuhariri page hii.</p></section>',
    )
    return redirect('builder:page_editor', site_id=site.id, page_id=page.id)


@login_required
@require_POST
def page_delete(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    if page.slug == 'home':
        messages.error(request, 'The home page cannot be deleted.')
    else:
        page.delete()
        messages.success(request, f'Page "{page.title}" has been deleted.')
    return redirect('builder:site_dashboard', site_id=site.id)


# GrapesJS storage endpoints
@login_required
def page_load(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    return JsonResponse(page.grapes_data or {})


@login_required
@require_POST
def page_save(request, site_id, page_id):
    site = _my_site(request, site_id)
    page = get_object_or_404(SitePage, id=page_id, website=site)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'bad json'}, status=400)
    page.grapes_data = data.get('project', {})
    page.html_cache = data.get('html', '')
    page.css_cache = data.get('css', '')
    page.save()
    return JsonResponse({'status': 'ok'})


# ── Collections (Packages, Trips, Destinations, Products...) ──

@login_required
def collection_items(request, site_id, collection_id):
    site = _my_site(request, site_id)
    collection = get_object_or_404(SiteCollection, id=collection_id, website=site)
    return render(request, 'builder/items.html', {
        'site': site, 'collection': collection,
        'items': collection.items.all(),
        'uploadcare_public_key': _uploadcare_key(),
    })


@login_required
def item_form(request, site_id, collection_id, item_id=None):
    site = _my_site(request, site_id)
    collection = get_object_or_404(SiteCollection, id=collection_id, website=site)
    item = None
    if item_id:
        item = get_object_or_404(SiteItem, id=item_id, collection=collection)

    if request.method == 'POST':
        title = (request.POST.get('title') or '').strip()
        if not title:
            messages.error(request, 'A name/title is required.')
        else:
            data = {}
            for field in collection.fields:
                key = field['key']
                raw = (request.POST.get(f'f_{key}') or '').strip()
                if field.get('type') == 'list':
                    data[key] = [ln.strip() for ln in raw.splitlines() if ln.strip()]
                else:
                    data[key] = raw
            if item is None:
                item = SiteItem(collection=collection)
            item.title = title
            item.data = data
            item.image_url = (request.POST.get('image_url') or '').strip()
            item.is_featured = request.POST.get('is_featured') == 'on'
            item.is_visible = request.POST.get('is_visible', 'on') == 'on'
            item.save()
            messages.success(request, f'{collection.name_singular} "{title}" saved.')
            return redirect('builder:collection_items',
                            site_id=site.id, collection_id=collection.id)

    return render(request, 'builder/item_form.html', {
        'site': site, 'collection': collection, 'item': item,
        'uploadcare_public_key': _uploadcare_key(),
    })


@login_required
@require_POST
def item_delete(request, site_id, collection_id, item_id):
    site = _my_site(request, site_id)
    collection = get_object_or_404(SiteCollection, id=collection_id, website=site)
    item = get_object_or_404(SiteItem, id=item_id, collection=collection)
    item.delete()
    messages.success(request, f'"{item.title}" has been deleted.')
    return redirect('builder:collection_items', site_id=site.id, collection_id=collection.id)


# ── Inquiries / Bookings ────────────────────────────────

@login_required
def inquiries_list(request, site_id):
    site = _my_site(request, site_id)
    status = request.GET.get('status', 'all')
    qs = site.inquiries.select_related('item').all()
    if status in ('new', 'contacted', 'closed'):
        qs = qs.filter(status=status)
    return render(request, 'builder/inquiries.html', {
        'site': site,
        'inquiries': qs[:200],
        'status': status,
        'counts': {
            'all': site.inquiries.count(),
            'new': site.inquiries.filter(status='new').count(),
            'contacted': site.inquiries.filter(status='contacted').count(),
            'closed': site.inquiries.filter(status='closed').count(),
        },
    })


@login_required
@require_POST
def inquiry_status(request, site_id, inquiry_id):
    site = _my_site(request, site_id)
    inq = get_object_or_404(SiteInquiry, id=inquiry_id, website=site)
    new_status = request.POST.get('status')
    if new_status in ('new', 'contacted', 'closed'):
        inq.status = new_status
        inq.save(update_fields=['status'])
    return redirect(f"/builder/site/{site.id}/inquiries/?status={request.POST.get('back', 'all')}")


# ── Assets (Uploadcare) ─────────────────────────────────

@login_required
@require_POST
def asset_save(request, site_id):
    site = _my_site(request, site_id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'bad json'}, status=400)
    url = data.get('cdn_url', '')
    if not url.startswith('https://ucarecdn.com/'):
        return JsonResponse({'error': 'Not an Uploadcare URL.'}, status=400)
    asset = SiteAsset.objects.create(
        website=site, uploadcare_url=url, file_name=data.get('name', ''),
    )
    return JsonResponse({'status': 'ok', 'id': asset.id, 'url': url})


@login_required
def asset_list(request, site_id):
    site = _my_site(request, site_id)
    return JsonResponse({'assets': [
        {'id': a.id, 'url': a.uploadcare_url, 'name': a.file_name}
        for a in site.assets.all()[:100]
    ]})