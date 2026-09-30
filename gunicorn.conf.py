"""
Mipangilio ya gunicorn. Gunicorn inasoma faili hili yenyewe (liko kwenye
folda inayoanzishwa) — linafanya kazi hata kama start command ya Render ni
`gunicorn jamiitek.wsgi` tu.

TIMEOUT: default ni sekunde 30. Kupakia ZIP ya website (picha nyingi kwenda
Supabase) kulizidi muda huo, gunicorn ikaua worker na mteja akaona
"Internal Server Error". Sasa ombi lina hadi sekunde 120.
"""
import os

timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
graceful_timeout = 30
keepalive = 5
