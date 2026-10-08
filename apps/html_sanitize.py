"""
Kisafishaji cha HTML kwa allowlist (apps/html_sanitize.py).

Makala za blog zinaandikwa na AI kutoka habari za nje (RSS), kisha
zinaonyeshwa kwa `|safe`. Kisafishaji cha zamani (regex) kiliondoa tu
`on...="..."` zenye alama mbili za nukuu — `<img src=x onerror=...>`,
`href="javascript:..."` na `<svg onload=...>` zilipita.

Hapa tunajenga HTML upya: tag na attribute zilizo kwenye orodha tu ndizo
zinazobaki, kila thamani inaescape-iwa, na link zinaruhusiwa kwa
http/https/mailto/tel/# na njia za ndani tu.
"""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

ALLOWED_TAGS = {
    'p', 'br', 'hr', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'em', 'i', 'u',
    'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre', 'span', 'div', 'small',
    'sub', 'sup', 'mark', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption',
    'figure', 'figcaption', 'img',
}
VOID_TAGS = {'br', 'hr', 'img'}
# Maudhui ya tags hizi yanaondolewa kabisa (si maandishi tu)
DROP_CONTENT = {'script', 'style', 'iframe', 'object', 'embed', 'noscript',
                'template', 'svg', 'math', 'head', 'title', 'textarea', 'select'}
ALLOWED_ATTRS = {
    'a': {'href', 'title', 'target', 'rel'},
    'img': {'src', 'alt', 'title', 'width', 'height', 'loading'},
    'th': {'colspan', 'rowspan', 'scope'},
    'td': {'colspan', 'rowspan'},
    # style haiwezi kuendesha JS kwenye browsers za kisasa; makala za zamani zinaitumia
    '*': {'class', 'id', 'style'},
}
URL_ATTRS = {'href', 'src'}
SAFE_SCHEMES = {'http', 'https', 'mailto', 'tel', ''}


def _safe_url(value, tag):
    v = (value or '').strip()
    # Herufi za udhibiti/nafasi zinaweza kuficha "java\tscript:"
    compact = ''.join(ch for ch in v if ch > ' ')
    try:
        scheme = urlparse(compact).scheme.lower()
    except ValueError:
        return None
    if tag == 'img' and scheme not in ('http', 'https', ''):
        return None
    if scheme not in SAFE_SCHEMES:
        return None
    return v


class _Cleaner(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.drop_depth = 0
        self.open = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DROP_CONTENT:
            if tag not in VOID_TAGS:
                self.drop_depth += 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS:
            return
        allowed = ALLOWED_ATTRS.get(tag, set()) | ALLOWED_ATTRS['*']
        parts = []
        for name, value in attrs:
            name = (name or '').lower()
            if name not in allowed or value is None:
                continue
            if name in URL_ATTRS:
                value = _safe_url(value, tag)
                if value is None:
                    continue
            if name == 'target' and value != '_blank':
                continue
            parts.append(f' {name}="{escape(value, quote=True)}"')
        if tag == 'a' and any(p.startswith(' target=') for p in parts):
            parts = [p for p in parts if not p.startswith(' rel=')]
            parts.append(' rel="noopener noreferrer"')
        self.out.append(f'<{tag}{"".join(parts)}>')
        if tag not in VOID_TAGS:
            self.open.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS and self.open and self.open[-1] == tag.lower():
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DROP_CONTENT:
            if self.drop_depth:
                self.drop_depth -= 1
            return
        if self.drop_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        if tag in self.open:
            # Funga tags zilizobaki wazi ndani yake (HTML mbovu ya AI)
            while self.open:
                t = self.open.pop()
                self.out.append(f'</{t}>')
                if t == tag:
                    break

    def handle_data(self, data):
        if not self.drop_depth:
            self.out.append(escape(data, quote=False))

    def close(self):
        super().close()
        while self.open:
            self.out.append(f'</{self.open.pop()}>')


def clean_html(html):
    """HTML salama kuonyesha kwa `|safe`. Maandishi hayapotei; tags hatari zinaondoka."""
    if not html:
        return ''
    c = _Cleaner()
    c.feed(str(html))
    c.close()
    return ''.join(c.out).strip()
