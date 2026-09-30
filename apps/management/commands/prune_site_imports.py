"""Futa files za ZIP imports za Builder ambazo hazitumiki tena.

Upakiaji wa ZIP (builder/site_import.py) unapakia picha, CSS na JS
Supabase. Files hizo zinakuwa takataka katika hali mbili:

1. HAZIKUTHIBITISHWA — mteja hakubonyeza "Import", au upakiaji
   ulishindwa katikati. Zinafutwa baada ya saa IMPORT_TTL_HOURS.

2. SITE IMEFUTWA — rekodi inabaki bila site (on_delete=SET_NULL),
   kwa hiyo files zake zinafutwa mara moja.

3. ZIMEACHWA — mteja alipakia ZIP mpya iliyochukua nafasi ya kurasa
   zote za import ya zamani (au alizifuta). Import inafutwa pale tu
   ambapo HAKUNA hata URL yake moja inayotajwa tena kwenye site.

   Kwa nini import nzima, si file moja moja? CSS ya import inaita picha
   zake kwa url(...), na maandishi ya CSS yako Supabase — hatuyaoni hapa.
   Ukurasa mmoja wa zamani ukiendelea kutumia style.css yake, picha
   zinazoitwa na CSS hiyo lazima zibaki. Kuangalia import kama kitu
   kimoja kunaepuka kufuta kitu kinachotumika.

Inaendeshwa na DailyTasksMiddleware (apps/daily_tasks.py) mara moja kwa siku.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps import storage
from builder.models import SiteAsset, SiteImport, SiteItem
from builder.views import IMPORT_TTL_HOURS

# Kikomo kwa mzunguko mmoja — import moja inaweza kuwa na files 400
BATCH = 10
# Import iliyothibitishwa karibuni haiguswi (mteja anaweza kuwa bado anahariri)
CONFIRMED_GRACE = timedelta(hours=1)


def site_text(site):
    """Kila mahali site inaweza kutaja URL ya file — kwa ukaguzi wa 'inatumika?'."""
    parts = [site.logo_url, site.global_css, site.custom_nav_html, site.custom_footer_html]
    for raw, html, css in site.pages.values_list('raw_document', 'html_cache', 'css_cache'):
        parts += [raw, html, css]
    for img, data in SiteItem.objects.filter(collection__website=site).values_list('image_url', 'data'):
        parts += [img, json.dumps(data)]
    return '\n'.join(p or '' for p in parts)


def _delete_files(imp):
    """Futa files za import. Inarudisha idadi iliyofutwa; zilizoshindwa zinabaki kwenye rekodi."""
    with ThreadPoolExecutor(max_workers=8) as pool:
        ok = list(pool.map(storage.delete, imp.uploaded))
    failed = [u for u, good in zip(imp.uploaded, ok) if not good]
    gone = [u for u, good in zip(imp.uploaded, ok) if good]
    # Picha zilizofutwa zisibaki kwenye maktaba ya picha ya editor
    SiteAsset.objects.filter(website_id=imp.website_id, url__in=gone).delete()
    if failed:
        # Jaribu tena mzunguko ujao — usipoteze rekodi ya files zilizobaki
        imp.uploaded = failed
        imp.save(update_fields=['uploaded'])
    else:
        imp.delete()
    return len(gone)


class Command(BaseCommand):
    help = 'Futa files za Builder ZIP imports zisizothibitishwa au zisizotumika tena'

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        if not storage.is_configured():
            if not opts['quiet']:
                self.stdout.write('Supabase haijasanidiwa — hakuna cha kufuta')
            return
        now = timezone.now()

        # 1. Hazikuthibitishwa
        stale = list(SiteImport.objects.filter(
            confirmed_at__isnull=True,
            created_at__lt=now - timedelta(hours=IMPORT_TTL_HOURS),
        ).order_by('created_at')[:BATCH])
        files = sum(_delete_files(imp) for imp in stale)

        # 2. Site imefutwa
        orphaned = list(SiteImport.objects.filter(website__isnull=True)[:BATCH])
        files += sum(_delete_files(imp) for imp in orphaned)

        # 3. Zilizothibitishwa lakini hakuna kinachozitumia tena
        abandoned = 0
        confirmed = (SiteImport.objects
                     .filter(confirmed_at__lt=now - CONFIRMED_GRACE, website__isnull=False)
                     .select_related('website').order_by('website_id', 'created_at'))
        texts = {}
        for imp in confirmed:
            if abandoned >= BATCH:
                break
            site = imp.website
            if site.pk not in texts:
                texts[site.pk] = site_text(site)
            if not any(u in texts[site.pk] for u in imp.uploaded):
                files += _delete_files(imp)
                abandoned += 1

        if not opts['quiet']:
            self.stdout.write(f'Imports: {len(stale)} hazikuthibitishwa, {len(orphaned)} za sites '
                              f'zilizofutwa, {abandoned} zimeachwa · '
                              f'files {files} zimefutwa')
