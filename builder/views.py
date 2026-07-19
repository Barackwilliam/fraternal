"""
Dashboard ya mteja ("cPanel" ya JamiiTek Builder) — inafanya kazi kwenye
platform kuu (jamiitek.com/builder/...).
"""
import os
import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import (
    ClientWebsite, SitePage, SiteCollection, SiteItem, SiteAsset, SiteInquiry, AiUsageLog,
    available_website_types, validate_subdomain,
)
from .site_templates import all_templates, apply_template
from .insights import get_insights


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

    ai_draft = request.session.get('ai_draft')
    ai_prefill = {}
    if ai_draft and ai_draft.get('plan') and request.GET.get('from') == 'ai':
        plan = ai_draft['plan']
        ai_prefill = {
            'site_name': plan.get('site_name', ''),
            'website_type': plan.get('website_type', 'default'),
        }

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

                # AI draft ipo? Iweke kwenye site (juu ya template)
                ai_draft = request.session.get('ai_draft')
                if ai_draft and ai_draft.get('plan'):
                    _apply_ai_plan(site, ai_draft['plan'])
                    del request.session['ai_draft']
                    request.session.modified = True
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
        'ai_prefill': ai_prefill,
        'from_ai': bool(ai_prefill),
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



# ═══════════════════════════════════════════════════════════
# ONE-SHOT AI WEBSITE GENERATOR
# Kutoka sentensi moja ya biashara → website nzima tayari.
# ═══════════════════════════════════════════════════════════

def ai_generator(request):
    """Public page yenye textarea moja: 'Describe your business'."""
    return render(request, 'builder/ai_generator.html', {})


@require_POST
def ai_generate_website(request):
    """
    Endpoint ya AJAX inayoitwa na ai_generator.html.
    Inarudisha JSON — kama sio-authenticated, ina-store draft kwenye session
    kisha ina-redirect mteja kwa signup. Baada ya signup, apply_ai_draft()
    inaingia otomatiki.
    """
    from . import ai_oneshot
    description = (request.POST.get('description') or '').strip()

    try:
        ok, result = ai_oneshot.generate_website_plan(description)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('ai_generate_website crashed')
        return JsonResponse({'ok': False,
            'error': f'Server error while generating ({type(e).__name__}). '
                     'Check /builder/ai/status/ for diagnostics.'}, status=500)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)

    # Store kwenye session — italetwa kwenye signup au apply mara moja
    request.session['ai_draft'] = {
        'description': description,
        'plan': result,
    }
    request.session.modified = True

    if request.user.is_authenticated:
        return JsonResponse({
            'ok': True,
            'next': reverse('builder:ai_apply'),
            'preview': {
                'site_name': result['site_name'],
                'tagline': result['tagline'],
                'website_type': result['website_type'],
                'items_count': len(result.get('items', [])),
            },
        })
    return JsonResponse({
        'ok': True,
        'next': reverse('builder:signup') + '?from=ai',
        'preview': {
            'site_name': result['site_name'],
            'tagline': result['tagline'],
            'website_type': result['website_type'],
            'items_count': len(result.get('items', [])),
        },
    })


def _apply_ai_plan(site, plan):
    """Weka AI-generated content kwenye ClientWebsite + collections zake."""
    from . import ai_oneshot
    from .ai_designs import render_home

    # 1. Update field za site
    site.tagline = plan.get('tagline', '')[:200] or site.tagline
    site.accent_color = plan.get('palette', {}).get('primary',
                        plan.get('accent_color', site.accent_color))
    site.nav_layout = plan.get('nav_layout', site.nav_layout)
    site.save(update_fields=['tagline', 'accent_color', 'nav_layout'])

    # 2. Ongeza items kwenye primary collection
    primary_slug = ai_oneshot.PRIMARY_COLLECTION.get(site.website_type, 'services')
    col = site.collections.filter(slug=primary_slug).first()
    if col is not None:
        col.items.all().delete()
        for it in plan.get('items', [])[:8]:
            title = str(it.get('title', ''))[:200].strip()
            if not title:
                continue
            data = {
                'description': str(it.get('description', ''))[:2000],
                'price': str(it.get('price', ''))[:80],
            }
            extra = it.get('extra') or {}
            if isinstance(extra, dict):
                for k, v in extra.items():
                    if isinstance(v, (str, int, float)) and str(v).strip():
                        data[str(k)[:40]] = str(v)[:600]
            SiteItem.objects.create(
                collection=col, title=title, data=data, is_visible=True,
            )

    # 3. Home page — DESIGN TOFAUTI kulingana na style AI iliyochagua
    home = site.pages.filter(slug='home').first()
    if home is not None:
        home.html_cache = render_home(
            plan.get('design_style', 'sunset_bold'),
            plan.get('palette', {}),
            plan,
            col,
        )
        home.save()

    site.bump_version()


@login_required
def ai_apply(request):
    """Chukua draft kutoka session, unda ClientWebsite mpya, weka content."""
    draft = request.session.get('ai_draft')
    if not draft:
        messages.error(request, 'The AI draft has expired — please try again.')
        return redirect('builder:ai_generator')

    plan = draft['plan']
    website_type = plan.get('website_type', 'default')

    # Chagua subdomain automatic kutoka jina la biashara
    import re
    base = re.sub(r'[^a-z0-9]+', '-', plan.get('site_name', 'site').lower()).strip('-')[:40]
    if not base:
        base = 'site'
    subdomain = base
    n = 2
    while ClientWebsite.objects.filter(subdomain=subdomain).exists():
        subdomain = f'{base}-{n}'
        n += 1
        if n > 999:
            subdomain = f'{base}-{request.user.id}'
            break

    try:
        with transaction.atomic():
            site = ClientWebsite.objects.create(
                owner=request.user,
                subdomain=subdomain,
                site_name=plan.get('site_name', 'My Website')[:120],
                website_type=website_type,
            )
            site.bootstrap_from_schema()
            _apply_ai_plan(site, plan)
    except ValidationError as e:
        messages.error(request, ' '.join(e.messages))
        return redirect('builder:ai_generator')

    del request.session['ai_draft']
    request.session.modified = True

    messages.success(request,
        f'✨ Your website is ready! "{site.site_name}" has been created — '
        'review the content and hit Publish when you are happy.')
    return redirect('builder:site_dashboard', site_id=site.id)


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
        'insights': get_insights(site)[:3],
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


@login_required
def ai_status(request):
    """
    Diagnostic ya AI — inaonyesha hasa kipi kimekwama:
    package, API key, mtandao kwenda Groq, cache. Staff/owner yeyote.
    """
    import time
    checks = {}

    # 1. groq package
    try:
        import groq  # noqa
        checks['groq_package'] = {'ok': True, 'detail': f'installed (v{getattr(groq, "__version__", "?")})'}
    except ImportError:
        checks['groq_package'] = {'ok': False, 'detail': 'NOT installed — run: pip install groq'}

    # 2. API key
    key = os.getenv('GROQ_API_KEY', '')
    checks['api_key'] = {'ok': bool(key),
        'detail': f'present ({key[:7]}…)' if key else 'MISSING — add GROQ_API_KEY to .env / Render env'}

    # 3. Mtandao kwenda Groq (models list — nyepesi, haitumii tokens)
    if checks['groq_package']['ok'] and key:
        try:
            from groq import Groq
            t0 = time.time()
            client = Groq(api_key=key)
            models = client.models.list()
            ms = int((time.time() - t0) * 1000)
            names = [m.id for m in models.data][:3]
            checks['groq_reachable'] = {'ok': True,
                'detail': f'reachable in {ms}ms · models e.g. {names}'}
        except Exception as e:
            checks['groq_reachable'] = {'ok': False,
                'detail': f'{type(e).__name__}: {str(e)[:180]} — check internet/VPN/firewall on the SERVER side'}
    else:
        checks['groq_reachable'] = {'ok': False, 'detail': 'skipped (fix package/key first)'}

    # 4. Model configured
    from .ai import GROQ_MODEL
    checks['model'] = {'ok': True, 'detail': GROQ_MODEL}

    # 5. Cache backend (+ REDIS_URL forensics — prefix tu, password haionyeshwi)
    from django.core.cache import cache
    redis_url = os.getenv('REDIS_URL', '')
    url_info = ''
    if redis_url:
        prefix = redis_url[:14]
        url_info = (f' · REDIS_URL starts with: {prefix!r} '
                    f'(len={len(redis_url)}, '
                    f'leading_space={redis_url != redis_url.lstrip()}, '
                    f'has_quotes={redis_url[0] in chr(34) + chr(39)})')
    else:
        url_info = ' · REDIS_URL is EMPTY/absent (LocMem in use)'
    try:
        cache.set('jt_diag', 'ok', 10)
        backend = type(cache).__name__
        checks['cache'] = {'ok': cache.get('jt_diag') == 'ok',
                           'detail': backend + url_info}
    except Exception as e:
        checks['cache'] = {'ok': False,
                           'detail': f'{type(e).__name__}: {str(e)[:120]}{url_info}'}

    # 6. Rate limit yako
    from .ai import _check_rate_limit, AI_DAILY_LIMIT
    ok_rate, remaining = _check_rate_limit(request.user)
    checks['your_rate_limit'] = {'ok': ok_rate,
        'detail': f'{remaining}/{AI_DAILY_LIMIT} requests left today'}

    all_ok = all(c['ok'] for c in checks.values())
    return JsonResponse({'all_ok': all_ok, 'checks': checks},
                        json_dumps_params={'indent': 2})


# ═══════════════════════════════════════════════════════════
# SUPER-ADMIN — udhibiti wa platform nzima (staff only)
# ═══════════════════════════════════════════════════════════

def _staff_only(user):
    return user.is_authenticated and user.is_staff


@login_required
def superadmin(request):
    """Dashboard ya wewe (staff): sites zote, stats, na actions."""
    if not request.user.is_staff:
        return redirect('builder:my_sites')

    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    all_sites = ClientWebsite.objects.select_related('owner')

    stats = {
        'total_sites': all_sites.count(),
        'published': all_sites.filter(is_published=True).count(),
        'premium': all_sites.filter(is_premium=True).count(),
        'suspended': all_sites.filter(is_suspended=True).count(),
        'new_week': all_sites.filter(created_at__gte=week_ago).count(),
        'new_month': all_sites.filter(created_at__gte=month_ago).count(),
        'total_users': User.objects.count(),
        'inquiries_total': SiteInquiry.objects.count(),
        'inquiries_week': SiteInquiry.objects.filter(created_at__gte=week_ago).count(),
        'ai_calls_week': AiUsageLog.objects.filter(created_at__gte=week_ago).count(),
    }

    # Filters + search
    q = (request.GET.get('q') or '').strip()
    flt = request.GET.get('f', 'all')
    sites = all_sites.annotate(
        items_count=Count('collections__items', distinct=True),
        inq_count=Count('inquiries', distinct=True),
    ).order_by('-created_at')

    if q:
        sites = sites.filter(
            Q(subdomain__icontains=q) | Q(site_name__icontains=q) |
            Q(owner__username__icontains=q) | Q(custom_domain__icontains=q))
    if flt == 'published':
        sites = sites.filter(is_published=True)
    elif flt == 'draft':
        sites = sites.filter(is_published=False)
    elif flt == 'premium':
        sites = sites.filter(is_premium=True)
    elif flt == 'suspended':
        sites = sites.filter(is_suspended=True)

    return render(request, 'builder/superadmin.html', {
        'stats': stats,
        'sites': sites[:200],
        'q': q,
        'flt': flt,
    })


@login_required
@require_POST
def superadmin_action(request, site_id):
    """Actions: toggle premium / suspend / publish."""
    if not request.user.is_staff:
        return redirect('builder:my_sites')
    site = get_object_or_404(ClientWebsite, id=site_id)
    action = request.POST.get('action')

    if action == 'toggle_premium':
        site.is_premium = not site.is_premium
        site.save(update_fields=['is_premium'])
        messages.success(request,
            f'{site.subdomain}: premium {"ON ⭐" if site.is_premium else "OFF"}')
    elif action == 'toggle_suspend':
        site.is_suspended = not site.is_suspended
        site.save(update_fields=['is_suspended'])
        site.bump_version()
        messages.success(request,
            f'{site.subdomain}: {"SUSPENDED 🚫" if site.is_suspended else "reactivated ✓"}')
    elif action == 'toggle_publish':
        site.is_published = not site.is_published
        site.save(update_fields=['is_published'])
        site.bump_version()
        messages.success(request,
            f'{site.subdomain}: {"published" if site.is_published else "unpublished"}')

    back = request.POST.get('back', '')
    return redirect(f"/builder/superadmin/?{back}")


# ── Global CSS + AI Theme (customization ya website nzima) ──

@login_required
@require_POST
def save_global_css(request, site_id):
    """Hifadhi Global CSS — inatumika pages ZOTE za site + public."""
    site = _my_site(request, site_id)
    css = (request.POST.get('global_css') or '')[:60000]
    site.global_css = css
    site.save(update_fields=['global_css'])
    site.bump_version()
    return JsonResponse({'ok': True, 'saved': True})


@login_required
def get_global_css(request, site_id):
    """Rudisha Global CSS ya sasa (kwa editor kuipakia)."""
    site = _my_site(request, site_id)
    return JsonResponse({'ok': True, 'global_css': site.global_css or ''})


@login_required
@require_POST
def ai_theme(request, site_id):
    """
    AI Theme: mtu anaandika 'nataka iwe ya kisasa, rangi za bahari' →
    AI ina-generate Global CSS block inayobadilisha look ya website nzima.
    """
    site = _my_site(request, site_id)

    from .ai import _check_rate_limit, AI_DAILY_LIMIT
    ok_rate, remaining = _check_rate_limit(request.user)
    if not ok_rate:
        return JsonResponse({'ok': False,
            'error': f'Daily AI limit reached ({AI_DAILY_LIMIT}). Try again tomorrow.'},
            status=429)

    brief = (request.POST.get('brief') or '').strip()
    if len(brief) < 3:
        return JsonResponse({'ok': False, 'error': 'Please describe the look you want.'}, status=400)

    try:
        from . import ai_theme as ai_theme_mod
        ok, css = ai_theme_mod.generate_theme_css(site, brief)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('ai_theme crashed')
        return JsonResponse({'ok': False,
            'error': f'Server error ({type(e).__name__}). Check /builder/ai/status/.'}, status=500)

    if not ok:
        return JsonResponse({'ok': False, 'error': css}, status=400)

    AiUsageLog.objects.create(user=request.user)
    return JsonResponse({'ok': True, 'css': css, 'remaining': remaining - 1})


# ── AI Field Helper (magic buttons) ────────────────────

@login_required
@require_POST
def ai_field(request):
    """
    Endpoint ya AJAX inayoitwa na kila magic ✨ button kwenye forms.
    POST fields:
        field_type — moja ya keys za FIELD_PROMPTS (site_name, tagline, ...)
        site_id    — hiari; ClientWebsite ambayo mtu anahariri
        context    — JSON (hiari) ya fields nyingine za form
        hint       — user note (hiari)
    """
    from . import ai_field as ai_field_mod

    # Rate limit share ile ile ya ai_assist
    from .ai import _check_rate_limit
    ok_rate, remaining = _check_rate_limit(request.user)
    if not ok_rate:
        from .ai import AI_DAILY_LIMIT
        return JsonResponse({'ok': False,
            'error': f'Daily AI limit reached ({AI_DAILY_LIMIT}). Try again tomorrow.'},
            status=429)

    field_type = (request.POST.get('field_type') or '').strip()
    hint = (request.POST.get('hint') or '').strip()

    site = None
    site_id = request.POST.get('site_id')
    if site_id:
        try:
            site = ClientWebsite.objects.get(id=site_id, owner=request.user)
        except (ClientWebsite.DoesNotExist, ValueError):
            pass

    ctx = {}
    ctx_raw = request.POST.get('context')
    if ctx_raw:
        try:
            parsed = json.loads(ctx_raw)
            if isinstance(parsed, dict):
                ctx = {k: v for k, v in parsed.items() if isinstance(v, (str, int, float))}
        except (ValueError, TypeError):
            pass

    try:
        ok, result = ai_field_mod.generate_field(field_type, site, ctx, hint)
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('ai_field crashed')
        return JsonResponse({'ok': False,
            'error': f'Server error ({type(e).__name__}). '
                     'Check /builder/ai/status/ for diagnostics.'}, status=500)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)

    # Log usage kwa ajili ya rate limit
    AiUsageLog.objects.create(user=request.user)
    return JsonResponse({'ok': True, 'text': result, 'remaining': remaining - 1})


@login_required
@require_POST
def ai_suggest_items(request, site_id, collection_id):
    """
    AI Coach action: generate items 4-6 mpya, ziingie kama HIDDEN drafts
    ili mtu azipitie kabla hazijaonekana kwenye website.
    """
    site = _my_site(request, site_id)
    collection = get_object_or_404(SiteCollection, id=collection_id, website=site)

    from .ai import _check_rate_limit, AI_DAILY_LIMIT
    ok_rate, remaining = _check_rate_limit(request.user)
    if not ok_rate:
        messages.error(request,
            f'Daily AI limit reached ({AI_DAILY_LIMIT}). Try again tomorrow.')
        return redirect('builder:collection_items', site_id=site.id,
                        collection_id=collection.id)

    from . import ai_oneshot
    ok, result = ai_oneshot.suggest_items(site, collection, count=5)
    if not ok:
        messages.error(request, result)
        return redirect('builder:collection_items', site_id=site.id,
                        collection_id=collection.id)

    created = 0
    for it in result:
        data = {'description': it['description'], 'price': it['price']}
        for k, v in (it.get('extra') or {}).items():
            if isinstance(v, (str, int, float)) and str(v).strip():
                data[str(k)[:40]] = str(v)[:600]
        SiteItem.objects.create(
            collection=collection, title=it['title'], data=data,
            is_visible=False,  # HIDDEN draft — mtu ana-review kwanza
        )
        created += 1

    AiUsageLog.objects.create(user=request.user)
    site.bump_version()
    messages.success(request,
        f'✨ AI added {created} suggestions as HIDDEN drafts — review each one, '
        f'add photos, then tick "Visible on website" to publish the ones you like.')
    return redirect('builder:collection_items', site_id=site.id,
                    collection_id=collection.id)


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
