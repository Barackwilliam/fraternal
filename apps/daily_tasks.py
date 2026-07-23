"""
Kuendesha kazi za kila siku BILA cron (Render FREE, bila GitHub Actions).

Jinsi inavyofanya kazi:
  Mtu yeyote akifungua tovuti, middleware inaangalia kama kazi ya leo
  imeshafanyika. Kama bado, inaanzisha thread ya nyuma inayofanya kazi
  hiyo — mtumiaji haoni ucheleweshaji hata kidogo.

Usalama:
  • Ombi la kwanza linaweka alama MARA MOJA kabla ya kuanza kazi, kwa hiyo
    maombi 100 yanayoingia pamoja hayatafungua kazi 100.
  • Kazi yenyewe haiathiriwi na kurudiwa (inachukua tovuti zenye
    status='active' tu), kwa hiyo hata ikirudiwa hakuna madhara.
  • Kila kitu kiko ndani ya try/except — kazi ikishindwa, tovuti
    inaendelea kufanya kazi kawaida.
"""
import logging
import threading
from datetime import date

from django.core.cache import cache
from django.db import connection

logger = logging.getLogger(__name__)

CACHE_KEY = 'jamiitek:daily_tasks:last_run'
CACHE_TTL = 60 * 60 * 30          # saa 30 — inatosha siku moja
_thread_lock = threading.Lock()
_running = False


def _run_tasks_in_background():
    """Kazi halisi. Inaendeshwa kwenye thread ya nyuma."""
    global _running
    try:
        from . import hosting_service
        report = hosting_service.run_auto_suspend(notify=True)
        n, m = len(report['suspended']), len(report['maintenance'])
        if n or m:
            logger.info('[daily] auto-suspend: %d suspended, %d maintenance', n, m)
    except Exception:
        logger.exception('[daily] auto-suspend failed')
    finally:
        # Muhimu: funga muunganisho wa database wa thread hii
        try:
            connection.close()
        except Exception:
            pass
        with _thread_lock:
            _running = False


class DailyTasksMiddleware:
    """
    Inaendesha kazi za kila siku mara moja tu kwa siku, kwenye thread ya nyuma.

    Weka MWISHONI mwa MIDDLEWARE kwenye settings.py.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._maybe_run()
        except Exception:
            # Kamwe isivunje ombi la mtumiaji
            logger.exception('[daily] middleware check failed')
        return response

    def _maybe_run(self):
        global _running

        # Ruka maombi ya static/media na ya admin — hayahitaji kuangalia
        today = date.today().isoformat()

        try:
            last = cache.get(CACHE_KEY)
        except Exception:
            # Cache haipatikani (Redis imelala) — usifanye kitu leo
            return

        if last == today:
            return

        with _thread_lock:
            if _running:
                return
            _running = True

        # Weka alama KABLA ya kuanza — kuzuia maombi mengine kuanzisha kazi ile ile
        try:
            cache.set(CACHE_KEY, today, CACHE_TTL)
        except Exception:
            with _thread_lock:
                _running = False
            return

        t = threading.Thread(target=_run_tasks_in_background,
                             name='jamiitek-daily-tasks', daemon=True)
        t.start()
        logger.info('[daily] tasks started in background for %s', today)


def force_run_now():
    """Lazimisha kazi ifanyike sasa (kwa ajili ya kitufe cha 'Run now')."""
    try:
        cache.delete(CACHE_KEY)
    except Exception:
        pass
