"""
Daraja kati ya Templates Marketplace (apps.WebsiteTemplate) na Builder.

TATIZO

Mifumo miwili haikuwasiliana: mteja aliona template nzuri kwenye
/templates/, lakini njia pekee ilikuwa kuinunua kwa WhatsApp. Hakuweza
kuichukua na kuibadilisha mwenyewe kwenye builder.

SULUHISHO

"✨ Customize in Builder" kwenye kila template:

  1. Mteja asiye na account anajisajili kwanza (usajili wa web builder),
     kisha anarudishwa hapa hapa.
  2. Anachagua jina na subdomain (au site yake iliyopo).
  3. HTML kamili ya template inakuwa ukurasa wa Home kama `raw_document` —
     njia ile ile ya kurasa za ZIP: <head> (CSS, fonts) na scripts zinabaki,
     editor ya drag & drop / code inahariri body, na public site inaionyesha
     kama ilivyo (pamoja na alama ya JamiiTek).
  4. Anafunguliwa editor moja kwa moja; akihifadhi Business na Pages kwenye
     Studio anaweza kupublish kwenye <jina>.jamiitek.com.
"""
import re

from django.db import transaction
from django.utils.text import slugify

from .models import ClientWebsite, SitePage
from .site_import import editable_body, ensure_document

# Aina ya template → website_type ya builder (collections na AI zinaitumia)
CATEGORY_TYPES = {
    'tourism': 'tourism', 'hotel': 'tourism', 'restaurant': 'restaurant',
    'shop': 'ecommerce', 'school': 'school', 'real estate': 'realestate',
    'church': 'ngo',
}


def website_type_for(tpl):
    return CATEGORY_TYPES.get((tpl.category or '').lower(), 'companyprofile')


def suggest_subdomain(name):
    """Pendekezo la subdomain isiyotumika kutoka jina la biashara."""
    base = re.sub(r'[^a-z0-9-]', '', slugify(name or ''))[:40].strip('-') or 'mysite'
    if len(base) < 3:
        base = f'{base}site'
    sub, n = base, 2
    while ClientWebsite.objects.filter(subdomain=sub).exists():
        sub = f'{base}{n}'
        n += 1
    return sub


def put_template_on_home(site, tpl):
    """HTML ya template inakuwa Home ya site (ukurasa wa raw_document)."""
    document = ensure_document(tpl.preview_html or '', tpl.name)
    SitePage.objects.update_or_create(
        website=site, slug='home',
        defaults={
            'title': 'Home',
            'raw_document': document,
            'html_cache': editable_body(document),
            'css_cache': '',
            'grapes_data': {},          # editor ianze na HTML ya template
            'sort_order': 0,
        },
    )
    ts = dict(site.theme_settings or {})
    ts['source_template'] = {'id': tpl.pk, 'name': tpl.name}
    site.theme_settings = ts
    site.save(update_fields=['theme_settings'])
    site.bump_version()
    return site.pages.get(slug='home')


def create_site_from_template(owner, tpl, site_name, subdomain):
    """Site mpya yenye template kama Home. Yote au hakuna."""
    with transaction.atomic():
        site = ClientWebsite.objects.create(
            owner=owner, subdomain=subdomain, site_name=site_name[:120],
            website_type=website_type_for(tpl),
            # Template ina nav na footer zake — builder isiweke nyingine juu yake
            nav_preset='', footer_preset='',
        )
        page = put_template_on_home(site, tpl)
    return site, page
