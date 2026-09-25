"""
Kupunguza picha za blog zilizokwisha pakiwa (kabla widget haijaanza kupunguza).

Picha ya simu ya 3-5MB → WebP ~1600px ~150-300KB. Inatumika na admin action
"Optimize cover images (faster loading)" kwenye Blog posts.
"""
import io
import logging
import urllib.request

logger = logging.getLogger(__name__)

MAX_PX = 1600
QUALITY = 82
SKIP_BELOW = 350 * 1024          # picha ndogo tayari — usiguse


def optimize_cover(post):
    """Rudisha (status, maelezo). status: 'ok' | 'skip' | 'error'."""
    from PIL import Image, ImageOps
    from . import storage
    from .models import BlogPost

    url = post.cover_image or ''
    if not url:
        return 'skip', 'no image'
    if 'images.unsplash.com' in url:
        return 'skip', 'Unsplash (already resized automatically)'
    if '/storage/v1/object/public/' not in url:
        return 'skip', 'not a Supabase image'

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'JamiiTek-optimizer'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
    except Exception as e:
        return 'error', f'download failed: {e}'

    if len(data) < SKIP_BELOW:
        return 'skip', f'already small ({len(data) // 1024}KB)'

    try:
        im = Image.open(io.BytesIO(data))
        if getattr(im, 'is_animated', False):
            return 'skip', 'animated image'
        im = ImageOps.exif_transpose(im)          # picha za simu zisigeuke
        if im.mode not in ('RGB', 'L'):
            bg = Image.new('RGB', im.size, (255, 255, 255))
            bg.paste(im, mask=im.convert('RGBA').split()[-1])
            im = bg
        im.thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)
        out = io.BytesIO()
        im.save(out, 'WEBP', quality=QUALITY, method=6)
    except Exception as e:
        return 'error', f'processing failed: {e}'

    if out.tell() >= len(data):
        return 'skip', 'no gain'

    out.seek(0)
    out.name = 'cover.webp'
    res = storage.upload(out, folder='blog', filename='cover.webp', content_type='image/webp')
    if not res.get('success'):
        return 'error', res.get('error') or 'upload failed'

    old_kb, new_kb = len(data) // 1024, out.getbuffer().nbytes // 1024
    # .update() — bila kubadili updated_at wala kutuma signals nzito; cache inafutwa hapa chini
    BlogPost.objects.filter(pk=post.pk).update(cover_image=res['url'])
    storage.delete(url)
    return 'ok', f'{old_kb}KB → {new_kb}KB'


def image_width(url, max_bytes=256 * 1024):
    """
    Upana wa picha (px) bila kupakua picha nzima — header ya JPEG/PNG/WebP inatosha.
    Rudisha int au None (ikishindikana — hakuna onyo linaloonyeshwa kimakosa).
    """
    if not url:
        return None
    if 'images.unsplash.com' in url:
        return 2000          # Unsplash inatoa ukubwa wowote (tunaomba 1200px kwa Google)
    from PIL import ImageFile
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'JamiiTek-check',
                                                   'Range': f'bytes=0-{max_bytes}'})
        parser = ImageFile.Parser()
        with urllib.request.urlopen(req, timeout=8) as r:
            read = 0
            while read < max_bytes:
                chunk = r.read(16 * 1024)
                if not chunk:
                    break
                read += len(chunk)
                parser.feed(chunk)
                if parser.image:
                    return parser.image.size[0]
    except Exception:
        return None
    return None
