"""Futa files za ZIP imports za Builder ambazo mteja hakuzithibitisha.

Upakiaji wa ZIP (builder/site_import.py) unapakia picha, CSS na JS
Supabase KABLA mteja hajaona hakikisho. Asipobonyeza "Import" — au
upakiaji ukishindwa katikati — files hizo hazitumiki na kitu chochote.
Command hii inazifuta baada ya saa IMPORT_TTL_HOURS.

Inaendeshwa na DailyTasksMiddleware (apps/daily_tasks.py) mara moja kwa siku.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps import storage
from builder.models import SiteImport
from builder.views import IMPORT_TTL_HOURS

# Kikomo kwa mzunguko mmoja — import moja inaweza kuwa na files 400
BATCH = 10


class Command(BaseCommand):
    help = 'Futa files za Builder ZIP imports zisizothibitishwa'

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        now = timezone.now()

        # Rekodi za imports zilizothibitishwa hazihitajiki tena (files ni za site)
        done, _ = SiteImport.objects.filter(
            confirmed_at__isnull=False, confirmed_at__lt=now - timedelta(days=30)).delete()

        if not storage.is_configured():
            if not opts['quiet']:
                self.stdout.write('Supabase haijasanidiwa — hakuna cha kufuta')
            return

        stale = SiteImport.objects.filter(
            confirmed_at__isnull=True,
            created_at__lt=now - timedelta(hours=IMPORT_TTL_HOURS),
        ).order_by('created_at')[:BATCH]

        removed = files = 0
        for imp in stale:
            with ThreadPoolExecutor(max_workers=8) as pool:
                ok = list(pool.map(storage.delete, imp.uploaded))
            failed = [u for u, good in zip(imp.uploaded, ok) if not good]
            files += len(imp.uploaded) - len(failed)
            if failed:
                # Jaribu tena mzunguko ujao — usipoteze rekodi ya files zilizobaki
                imp.uploaded = failed
                imp.save(update_fields=['uploaded'])
            else:
                imp.delete()
                removed += 1

        if not opts['quiet']:
            self.stdout.write(f'Imports {removed} zimesafishwa · files {files} zimefutwa · '
                              f'rekodi {done} za zamani zimeondolewa')
