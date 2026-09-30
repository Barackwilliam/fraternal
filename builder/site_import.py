"""
Kupakia website nzima kwa ZIP — "weka sehemu moja, pata website nzima".

TATIZO

Kubandika code kwenye editor kunafaa website ya faili moja tu. Designer
akikabidhi folda (index.html, about.html, style.css, images/logo.png),
mteja alikwama kwa sababu tatu:

  1. Kila ukurasa ulibandikwa peke yake.
  2. Links kama href="about.html" zilivunjika — kwetu ukurasa ni /p/about/.
  3. CSS, JS na picha hazikuwepo kwenye server yetu.

SULUHISHO

Mteja anapakia ZIP ya folda nzima. Hapa:

  - kila .html inakuwa SitePage (index.html -> Home, about.html -> /p/about/)
  - picha, CSS, JS na fonts zinapakiwa Supabase
  - links zote zinaandikwa upya: about.html -> /p/about/,
    images/logo.png -> URL yake ya Supabase (pia ndani ya CSS: url(...))
  - HTML kamili (pamoja na <head>) inahifadhiwa kwenye SitePage.raw_document
    na inatolewa kama ilivyo — bila navbar/footer ya JamiiTek juu yake

Hatua mbili: `prepare()` inachakata na kupakia assets, mteja anaona
hakikisho, kisha view inaandika pages kwenye database.

USALAMA

  - ZIP <= 25MB, files <= 400, jumla ikifunguliwa <= 80MB (zip bomb)
  - aina zilizo kwenye ASSET_TYPES pekee — .php, .exe, .sh n.k. zinarukwa
  - njia yenye '..', '/' mwanzoni au C:\\ -> ZIP nzima inakataliwa
  - symlinks na ZIP zenye password zinakataliwa
"""
import posixpath
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

from django.utils.text import slugify

MAX_ZIP_BYTES = 25 * 1024 * 1024
MAX_FILES = 400
MAX_TOTAL_BYTES = 80 * 1024 * 1024
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_PAGES = 30
UPLOAD_WORKERS = 8

PAGE_EXTS = {'html', 'htm'}

# Aina pekee zinazopakiwa. Kila kitu kingine kinarukwa na kuonyeshwa
# kwa mteja kwenye hakikisho.
ASSET_TYPES = {
    'css': 'text/css',
    'js': 'application/javascript',
    'mjs': 'application/javascript',
    'json': 'application/json',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
    'gif': 'image/gif',
    'avif': 'image/avif',
    'svg': 'image/svg+xml',
    'ico': 'image/x-icon',
    'woff': 'font/woff',
    'woff2': 'font/woff2',
    'ttf': 'font/ttf',
    'otf': 'font/otf',
    'eot': 'application/vnd.ms-fontobject',
    'pdf': 'application/pdf',
    'mp4': 'video/mp4',
    'webm': 'video/webm',
    'mp3': 'audio/mpeg',
}

# Takataka za mfumo wa uendeshaji — zinarukwa kimya
_JUNK = re.compile(r'(^|/)(__MACOSX|\.DS_Store|Thumbs\.db|desktop\.ini)(/|$)', re.I)


class ImportRejected(Exception):
    """ZIP haiwezi kutumika kabisa. Ujumbe unaonyeshwa kwa mteja."""


def _ext(path):
    return path.rsplit('.', 1)[-1].lower() if '.' in path.rsplit('/', 1)[-1] else ''


# ══════════════════════════════════════════════════════════════
#  1. KUSOMA ZIP KWA USALAMA
# ══════════════════════════════════════════════════════════════

def read_zip(file_obj):
    """
    Inarudisha (files, skipped):
      files   — {njia: bytes} kwa pages na assets zinazoruhusiwa
      skipped — [(njia, sababu)] kwa files zilizorukwa
    """
    size = getattr(file_obj, 'size', None)
    if size is not None and size > MAX_ZIP_BYTES:
        raise ImportRejected(f'The ZIP is too large ({size // 1024 // 1024}MB). The limit is 25MB.')
    try:
        zf = zipfile.ZipFile(file_obj)
    except (zipfile.BadZipFile, OSError):
        raise ImportRejected('This file is not a valid ZIP archive.')

    entries = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace('\\', '/')
        if _JUNK.search(name) or name.rsplit('/', 1)[-1].startswith('.'):
            continue
        # Njia hatari zinakataa ZIP nzima — si kurukwa kimya.
        segments = name.split('/')
        if name.startswith('/') or re.match(r'^[a-zA-Z]:', name) or '..' in segments:
            raise ImportRejected(f'The ZIP contains an unsafe file path: "{name[:80]}".')
        if info.flag_bits & 0x1:
            raise ImportRejected('Password-protected ZIP files are not supported.')
        entries.append((name, info))

    if len(entries) > MAX_FILES:
        raise ImportRejected(f'The ZIP has {len(entries)} files. The limit is {MAX_FILES}.')
    if sum(info.file_size for _, info in entries) > MAX_TOTAL_BYTES:
        raise ImportRejected('The ZIP is too large once extracted. The limit is 80MB.')

    # Folda ya juu inayofunika kila kitu (mysite/index.html) inaondolewa
    names = [n for n, _ in entries]
    prefix = ''
    if names and all('/' in n for n in names):
        first = names[0].split('/', 1)[0] + '/'
        if all(n.startswith(first) for n in names):
            prefix = first

    files, skipped = {}, []
    for name, info in entries:
        path = name[len(prefix):]
        ext = _ext(path)
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            skipped.append((path, 'symbolic link'))
            continue
        if ext not in PAGE_EXTS and ext not in ASSET_TYPES:
            skipped.append((path, f'.{ext} files are not allowed' if ext else 'unknown file type'))
            continue
        if info.file_size > MAX_FILE_BYTES:
            skipped.append((path, 'larger than 10MB'))
            continue
        with zf.open(info) as fh:
            data = fh.read(MAX_FILE_BYTES + 1)   # usiamini file_size iliyotangazwa
        if len(data) > MAX_FILE_BYTES:
            skipped.append((path, 'larger than 10MB'))
            continue
        files[path] = data
    return files, skipped


# ══════════════════════════════════════════════════════════════
#  2. RAMANI YA KURASA: njia -> slug
# ══════════════════════════════════════════════════════════════

_TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title\s*>', re.I | re.S)


def _decode(data):
    # Herufi NUL (\x00) haziwezi kuhifadhiwa kwenye JSON/text ya Postgres —
    # HTML iliyozibeba ilileta "Internal Server Error" wakati wa kuhifadhi.
    for enc in ('utf-8-sig', 'cp1252'):
        try:
            return data.decode(enc).replace('\x00', '')
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', 'replace').replace('\x00', '')


def plan_pages(page_paths):
    """{njia: slug}. index.html ya juu kabisa ndiyo Home."""
    paths = sorted(page_paths, key=lambda p: (p.count('/'), p))
    home = next((p for p in paths if p.lower() in ('index.html', 'index.htm')), None)
    if home is None and paths:
        home = next((p for p in paths if '/' not in p), paths[0])

    slugs, used = {}, {'home'}
    for p in paths:
        if p == home:
            slugs[p] = 'home'
            continue
        stem = p.rsplit('.', 1)[0]
        if stem.lower().endswith('/index'):
            stem = stem[:-len('/index')]
        base = slugify(stem.replace('/', '-'))[:70] or 'page'
        if base == 'home':
            base = 'home-page'
        slug, n = base, 2
        while slug in used:
            slug = f'{base}-{n}'
            n += 1
        used.add(slug)
        slugs[p] = slug
    return slugs


def page_url(slug):
    return '/' if slug == 'home' else f'/p/{slug}/'


# ══════════════════════════════════════════════════════════════
#  3. KUANDIKA LINKS UPYA
# ══════════════════════════════════════════════════════════════

_SCHEME = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')
_ATTR_RE = re.compile(
    r'(?P<pre>\s(?P<name>src|href|poster|action|data-src|data-bg|data-background|content)'
    r'\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)', re.I | re.S)
_SRCSET_RE = re.compile(r'(?P<pre>\s(?:srcset|data-srcset)\s*=\s*)(?P<q>["\'])(?P<val>.*?)(?P=q)', re.I | re.S)
_CSS_URL_RE = re.compile(r'url\(\s*(?P<q>["\']?)(?P<val>[^"\')]+?)(?P=q)\s*\)', re.I)
_CSS_IMPORT_RE = re.compile(r'@import\s+(?P<q>["\'])(?P<val>[^"\']+)(?P=q)', re.I)


class _Resolver:
    """Inageuza njia ya ndani ya ZIP kuwa URL yake mpya."""

    def __init__(self, pages, assets):
        self.pages = pages          # {njia: slug}
        self.assets = assets        # {njia: url ya Supabase}
        self.missing = set()

    def __call__(self, ref, base_dir, report=True):
        raw = (ref or '').strip()
        if not raw or raw.startswith(('#', '//', '{', '$')) or _SCHEME.match(raw):
            return None
        path, frag = (raw.split('#', 1) + [''])[:2]
        path, query = (path.split('?', 1) + [''])[:2]
        path = unquote(path)
        if not path:
            return None
        if path.startswith('/'):
            target = posixpath.normpath(path.lstrip('/')) if path != '/' else '.'
        else:
            target = posixpath.normpath(posixpath.join(base_dir, path))
        if target.startswith('..'):
            return None
        frag = f'#{frag}' if frag else ''

        candidates = [target] if target != '.' else []
        candidates += [posixpath.join(target, 'index.html'), posixpath.join(target, 'index.htm')] \
            if target != '.' else ['index.html', 'index.htm']
        candidates += [target + '.html']        # href="about" -> about.html
        for c in candidates:
            if c in self.pages:
                q = f'?{query}' if query else ''
                return page_url(self.pages[c]) + q + frag
            if c in self.assets:
                return self.assets[c] + frag
        if report and _ext(target):
            self.missing.add(target)
        return None


def rewrite_css(css, base_dir, resolve):
    def url_sub(m):
        new = resolve(m.group('val'), base_dir)
        return f'url("{new}")' if new else m.group(0)

    def import_sub(m):
        new = resolve(m.group('val'), base_dir)
        return f'@import "{new}"' if new else m.group(0)

    css = _CSS_IMPORT_RE.sub(import_sub, css)
    return _CSS_URL_RE.sub(url_sub, css)


def rewrite_html(html, base_dir, resolve):
    def attr_sub(m):
        name = m.group('name').lower()
        # content="" ni kwa <meta og:image> tu — usiripoti "missing" kwa viewport n.k.
        new = resolve(m.group('val'), base_dir, report=(name != 'content'))
        return f'{m.group("pre")}{m.group("q")}{new}{m.group("q")}' if new else m.group(0)

    def srcset_sub(m):
        parts = []
        for candidate in m.group('val').split(','):
            bits = candidate.strip().split(None, 1)
            if not bits:
                continue
            new = resolve(bits[0], base_dir)
            parts.append(' '.join([new or bits[0]] + bits[1:]))
        return f'{m.group("pre")}{m.group("q")}{", ".join(parts)}{m.group("q")}'

    html = _ATTR_RE.sub(attr_sub, html)
    html = _SRCSET_RE.sub(srcset_sub, html)
    # url(...) ndani ya <style> na style="..." — HTML nzima kwa mara moja
    return rewrite_css(html, base_dir, resolve)


# ══════════════════════════════════════════════════════════════
#  4. HATUA KUU: chakata + pakia
# ══════════════════════════════════════════════════════════════

def ensure_document(html, title):
    """Faili lisilo na <body> (kipande tu) linafunikwa na HTML kamili."""
    if re.search(r'<body\b', html, re.I):
        return html
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n</head>\n<body>\n{html}\n</body>\n</html>')


def prepare(file_obj, uploader):
    """
    Chakata ZIP nzima. `uploader(data, ext, content_type)` inarudisha URL
    (au inatupa ImportRejected) — inapitishwa hapa ili tests zisiguse Supabase.

    Inarudisha dict: {pages: [...], skipped: [...], missing: [...], assets: n}
    """
    files, skipped = read_zip(file_obj)
    page_paths = [p for p in files if _ext(p) in PAGE_EXTS]
    if not page_paths:
        raise ImportRejected('No .html file was found in the ZIP. Make sure it contains index.html.')
    if len(page_paths) > MAX_PAGES:
        raise ImportRejected(f'The ZIP has {len(page_paths)} pages. The limit is {MAX_PAGES}.')

    pages = plan_pages(page_paths)
    assets = {}
    resolve = _Resolver(pages, assets)

    # a) Assets zisizo CSS kwanza — CSS inazihitaji kwa url(...).
    #    Sambamba: files 400 moja moja zingezidi timeout ya gunicorn (30s).
    with ThreadPoolExecutor(max_workers=UPLOAD_WORKERS) as pool:
        futures = {
            path: pool.submit(uploader, data, _ext(path), ASSET_TYPES[_ext(path)])
            for path, data in files.items()
            if _ext(path) in ASSET_TYPES and _ext(path) != 'css'
        }
        for path, fut in futures.items():
            assets[path] = fut.result()      # kosa lolote linapanda hapa

    # b) CSS — @import ya CSS nyingine inahitaji hiyo iwe imepakiwa kwanza
    pending = [p for p in files if _ext(p) == 'css']
    while pending:
        ready = [p for p in pending if not any(
            _css_dep(ref, p) in pending and _css_dep(ref, p) != p
            for ref in _CSS_IMPORT_RE.findall(_decode(files[p]))
        )] or pending[:1]                       # mzunguko -> endelea hata hivyo
        for path in ready:
            css = rewrite_css(_decode(files[path]), posixpath.dirname(path), resolve)
            assets[path] = uploader(css.encode('utf-8'), 'css', ASSET_TYPES['css'])
            pending.remove(path)

    # c) Kurasa
    out = []
    for path in sorted(page_paths, key=lambda p: (pages[p] != 'home', pages[p])):
        html = _decode(files[path])
        m = _TITLE_RE.search(html)
        title = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
        if not title:
            title = 'Home' if pages[path] == 'home' else \
                pages[path].replace('-', ' ').title()
        doc = rewrite_html(html, posixpath.dirname(path), resolve)
        out.append({
            'path': path, 'slug': pages[path], 'title': title[:200],
            'document': ensure_document(doc, title),
        })

    return {
        'pages': out,
        'skipped': skipped,
        'missing': sorted(resolve.missing)[:50],
        'assets': len(assets),
    }


def _css_dep(ref_match, css_path):
    """Njia ya CSS inayoitwa na @import ndani ya css_path."""
    ref = ref_match[1] if isinstance(ref_match, tuple) else ref_match
    return posixpath.normpath(posixpath.join(posixpath.dirname(css_path), ref.split('?')[0]))


# ══════════════════════════════════════════════════════════════
#  5. EDITOR: kuhariri page iliyopakiwa bila kupoteza <head> yake
# ══════════════════════════════════════════════════════════════
#
# GrapesJS inahariri <body> tu na inaondoa <script>. Kwa hiyo:
#   - editor inapewa body bila scripts (SitePage.html_cache)
#   - ikihifadhi, body mpya inarudishwa ndani ya document ile ile,
#     scripts za zamani zinarudishwa mwisho wa body, na CSS ya editor
#     inakaa kwenye <style id="jt-editor-css"> ndani ya <head>

_BODY_RE = re.compile(r'(<body\b[^>]*>)(.*)(</body\s*>)', re.I | re.S)
_HEAD_RE = re.compile(r'<head\b[^>]*>(.*?)</head\s*>', re.I | re.S)
_SCRIPT_RE = re.compile(r'<script\b[^>]*>.*?</script\s*>', re.I | re.S)
_EDITOR_CSS_RE = re.compile(r'\s*<style id="jt-editor-css">.*?</style>', re.S)
_HEAD_STYLES_RE = re.compile(r'<link\b[^>]*rel=["\']?stylesheet[^>]*>|<style\b[^>]*>.*?</style\s*>', re.I | re.S)


def editable_body(document):
    """HTML ya body bila scripts — ndiyo editor inayoonyesha."""
    m = _BODY_RE.search(document or '')
    body = m.group(2) if m else (document or '')
    return _SCRIPT_RE.sub('', body).strip()


def canvas_head(document):
    """<link rel=stylesheet> na <style> za <head> — ili canvas ifanane na site."""
    m = _HEAD_RE.search(document or '')
    if not m:
        return ''
    head = _EDITOR_CSS_RE.sub('', m.group(1))
    return '\n'.join(_HEAD_STYLES_RE.findall(head))


def merge_editor_save(document, body_html, css):
    """Rudisha body iliyohaririwa ndani ya document kamili."""
    m = _BODY_RE.search(document)
    if not m:
        return document
    scripts = '\n'.join(_SCRIPT_RE.findall(m.group(2)))
    new_body = f'{m.group(1)}\n{body_html}\n{scripts}\n{m.group(3)}'
    doc = document[:m.start()] + new_body + document[m.end():]

    doc = _EDITOR_CSS_RE.sub('', doc)
    if css and css.strip():
        safe_css = css.replace('</style', '<\\/style')
        style = f'\n<style id="jt-editor-css">{safe_css}</style>'
        doc = re.sub(r'</head\s*>', lambda h: style + '\n' + h.group(0), doc, count=1, flags=re.I)
    return doc
