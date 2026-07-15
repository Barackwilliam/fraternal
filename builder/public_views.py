"""
Public site rendering — views hizi zinatumika TU wakati request imekuja
kupitia subdomain ya mteja (SubdomainMiddleware ime-set request.client_site
na request.urlconf = 'builder.public_urls').
"""
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from .rendering import render_page_html, render_shortcodes


def _get_site(request):
    site = getattr(request, 'client_site', None)
    if site is None:
        raise Http404
    return site


def _ctx(site, extra=None):
    ctx = {
        'site': site,
        'nav_pages': site.pages.filter(show_in_nav=True).only(
            'slug', 'title', 'sort_order'
        ),
    }
    if extra:
        ctx.update(extra)
    return ctx


def _check_published(request, site):
    """Draft site inaonekana kwa mmiliki tu (preview)."""
    if site.is_published:
        return None
    if request.user.is_authenticated and (
        request.user == site.owner or request.user.is_staff
    ):
        return None
    return render(request, 'builder/public/coming_soon.html',
                  {'site': site}, status=200)


def home(request):
    site = _get_site(request)
    blocked = _check_published(request, site)
    if blocked:
        return blocked
    page = site.pages.filter(slug='home').first() or site.pages.first()
    if page is None:
        raise Http404
    return render(request, 'builder/public/page.html', _ctx(site, {
        'page': page,
        'page_html': render_page_html(site, page),
    }))


def page_view(request, slug):
    site = _get_site(request)
    blocked = _check_published(request, site)
    if blocked:
        return blocked
    page = get_object_or_404(site.pages, slug=slug)
    return render(request, 'builder/public/page.html', _ctx(site, {
        'page': page,
        'page_html': render_page_html(site, page),
    }))


def collection_list(request, col_slug):
    site = _get_site(request)
    blocked = _check_published(request, site)
    if blocked:
        return blocked
    collection = get_object_or_404(site.collections, slug=col_slug)
    body = render_shortcodes(site, f'[[collection:{col_slug}]]')
    return render(request, 'builder/public/collection.html', _ctx(site, {
        'collection': collection,
        'body': body,
    }))


def item_detail(request, col_slug, item_slug):
    site = _get_site(request)
    blocked = _check_published(request, site)
    if blocked:
        return blocked
    collection = get_object_or_404(site.collections, slug=col_slug)
    item = get_object_or_404(
        collection.items, slug=item_slug, is_visible=True
    )
    # Panga fields kwa mpangilio wa schema, kwa display safi
    display_fields = []
    for f in collection.fields:
        value = item.data.get(f['key'])
        if value:
            display_fields.append({
                'label': f.get('label', f['key']),
                'type': f.get('type', 'text'),
                'value': value,
            })
    wa = (site.whatsapp_number or site.contact_phone or '').replace('+', '').replace(' ', '')
    wa_link = ''
    if wa:
        msg = f'Hello, I would like to enquire about: {item.title}'
        wa_link = f'https://wa.me/{wa}?text={msg.replace(" ", "%20")}'
    return render(request, 'builder/public/item_detail.html', _ctx(site, {
        'collection': collection,
        'item': item,
        'display_fields': display_fields,
        'wa_link': wa_link,
    }))
