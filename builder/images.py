"""URL za picha — sehemu MOJA kwa builder nzima.

TATIZO LILILOZAA FAILI HILI

Picha za wateja zilikuwa zinahifadhiwa Uploadcare. Uploadcare inabadilisha
ukubwa kwa kuongeza maagizo kwenye URL:

    https://ucarecdn.com/<uuid>/-/resize/600x/

Upload ilihamishwa kwenda Supabase, lakini rendering haikusasishwa. Sehemu
nane ziliendelea kuongeza `-/resize/600x/` kwenye KILA URL, kwa hiyo URL
ya Supabase ikawa:

    https://xxx.supabase.co/storage/v1/object/public/media/sites/5/logo.png/-/resize/80x/

Supabase inaona hilo kama faili lenye jina "logo.png/-/resize/80x/" —
halipo — na inarudisha 404. Logo, favicon, picha za bidhaa, na picha za
kushiriki kwenye WhatsApp — zote zilikuwa zinavunjika kwa kila website.

SULUHISHO

`image_url(url, width)`:
  - Uploadcare (picha za zamani) -> maagizo ya kupunguza ukubwa yanaongezwa
  - Supabase, au URL nyingine yoyote -> inarudishwa kama ilivyo

Supabase ya bure haina kubadilisha ukubwa (ni ya Pro), kwa hiyo hatutumii
`/render/image/`. Picha inatolewa kwa ukubwa wake halisi; CSS inaipanga.
"""
from urllib.parse import urlparse


def _is_uploadcare(url):
    host = (urlparse(url).netloc or '').lower()
    return host.endswith('ucarecdn.com') or host.endswith('ucarecd.net')


def image_url(url, width=None, height=None):
    """URL salama ya picha kwa ukubwa unaohitajika.

    Haijawahi kurudisha URL iliyovunjika: kitu kisichotambulika
    kinarudishwa kama kilivyo.
    """
    url = (url or '').strip()
    if not url:
        return ''
    if not (width or height) or not _is_uploadcare(url):
        return url

    base = url.split('/-/', 1)[0].rstrip('/')     # ondoa maagizo ya zamani
    size = f'{width or ""}x{height or ""}'
    return f'{base}/-/resize/{size}/-/format/auto/-/quality/smart/'
