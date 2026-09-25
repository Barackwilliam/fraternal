"""Blog views — ukurasa wa mbele (mtindo wa gazeti), makala, maoni, na sharing."""
import logging
import re
import threading
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Count, F, Q, Prefetch
from django.db.models.functions import Length
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import BlogPost, BlogCategory, BlogComment, BlogAuthor

logger = logging.getLogger(__name__)

PER_PAGE = 12
# Domain moja rasmi kwa SEO (jamiitek.com na www.jamiitek.com zote zinafunguka —
# canonical moja inazuia Google kuona nakala mbili). Inalingana na base.html.
CANONICAL_BASE = (getattr(settings, 'CANONICAL_BASE_URL', '') or 'https://jamiitek.com').rstrip('/')
FRONT_WINDOW = 60          # ukurasa wa mbele unajengwa kutoka makala 60 za karibuni tu
CACHE_SECONDS = 300        # dakika 5; inafutwa papo hapo makala/maoni yakibadilika


# ─────────────────────────────────────────────
# CACHE — kasi. Kila BlogPost/BlogComment ikihifadhiwa, `blog:ver` inaongezeka
# (apps/blog_signals.py), hivyo cache zote za zamani zinapuuzwa mara moja.
# ─────────────────────────────────────────────
def cache_version():
    v = cache.get('blog:ver')
    if v is None:
        v = 1
        cache.set('blog:ver', v, None)
    return v


def bump_cache_version():
    try:
        cache.incr('blog:ver')
    except ValueError:
        cache.set('blog:ver', 2, None)


def _share_urls(request, post):
    """Tengeneza share links za social media kwa post."""
    url = f'{CANONICAL_BASE}/blog/{post.slug}/'
    title = post.title
    text = f'{post.title} — {post.excerpt}'
    u = quote(url, safe='')
    t = quote(title, safe='')
    tx = quote(text, safe='')
    return {
        'url': url,
        'whatsapp': f'https://wa.me/?text={tx}%20{u}',
        'facebook': f'https://www.facebook.com/sharer/sharer.php?u={u}',
        'twitter': f'https://twitter.com/intent/tweet?text={t}&url={u}&via=JamiiTek',
        'linkedin': f'https://www.linkedin.com/sharing/share-offsite/?url={u}',
        'telegram': f'https://t.me/share/url?url={u}&text={t}',
    }


def _published():
    # `body` haipakiwi kwenye orodha (ndiyo sehemu nzito); `body_len` inatosha kwa read time.
    return (BlogPost.objects.filter(status='published')
            .select_related('category')
            .defer('body')
            .annotate(n_comments=Count('comments', filter=Q(comments__is_approved=True)),
                      body_len=Length('body')))


def _nav_context():
    """Vitu vinavyoonekana kwenye kila ukurasa wa blog: categories, ticker, most read.
    Vinahifadhiwa kwenye cache (queries 3 → 0 kwa maombi mengi)."""
    key = f'blog:nav:{cache_version()}'
    ctx = cache.get(key)
    if ctx is None:
        cats = list(BlogCategory.objects
                    .annotate(n=Count('posts', filter=Q(posts__status='published')))
                    .filter(n__gt=0).order_by('-n', 'name'))
        ticker = list(BlogPost.objects.filter(status='published')
                      .order_by('-published_at').values('title', 'slug')[:8])
        most_read = list(BlogPost.objects.filter(status='published')
                         .select_related('category').defer('body')
                         .order_by('-views', '-published_at')[:5])
        ctx = {'nav_categories': cats, 'ticker': ticker, 'most_read': most_read}
        cache.set(key, ctx, CACHE_SECONDS)
    return dict(ctx)


def _cacheable(request):
    """Kurasa za wageni tu (bila login/messages) ndizo zinahifadhiwa kama HTML kamili."""
    if request.method != 'GET' or request.user.is_authenticated:
        return False
    try:
        from django.contrib.messages import get_messages
        if len(get_messages(request)):
            return False
    except Exception:
        pass
    return True


def blog_list(request):
    """Ukurasa wa mbele wa blog, au matokeo ya category / search.

    Kasi: kwa wageni ukurasa mzima (HTML) unatoka cache — hauna CSRF token wala
    data ya mtumiaji, hivyo ni salama kushirikiwa. Unafutwa makala ikibadilika."""
    use_cache = _cacheable(request)
    if use_cache:
        import hashlib
        key = 'blog:list:%s:%s' % (cache_version(),
                                   hashlib.md5(request.get_full_path().encode()).hexdigest())
        html = cache.get(key)
        if html is not None:
            resp = HttpResponse(html)
            resp['X-Blog-Cache'] = 'HIT'
            resp['Cache-Control'] = 'public, max-age=60'
            return resp
    resp = _blog_list(request)
    if use_cache and resp.status_code == 200:
        cache.set(key, resp.content.decode(), CACHE_SECONDS)
        resp['X-Blog-Cache'] = 'MISS'
        resp['Cache-Control'] = 'public, max-age=60'
    return resp


def _blog_list(request):
    posts = _published()

    cat_slug = request.GET.get('category')
    active_cat = BlogCategory.objects.filter(slug=cat_slug).first() if cat_slug else None
    q = (request.GET.get('q') or '').strip()[:100]

    ctx = {'active_cat': active_cat, 'q': q}
    ctx.update(_nav_context())

    if active_cat or q:
        # Matokeo: orodha rahisi yenye pagination
        if active_cat:
            posts = posts.filter(category=active_cat)
        if q:
            posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q)
                                 | Q(body__icontains=q) | Q(focus_keyword__icontains=q))
        page = Paginator(posts.order_by('-published_at'), PER_PAGE).get_page(request.GET.get('page'))
        ctx.update({'front': False, 'page': page, 'posts': page.object_list,
                    'result_count': page.paginator.count})
        return render(request, 'blog/blog_list.html', ctx)

    # Ukurasa wa mbele (mtindo wa gazeti). Hatupakii makala ZOTE — makala 10
    # kwa siku zingekuwa maelfu baada ya mwaka mmoja. Dirisha la karibuni linatosha.
    ordered = list(posts.order_by('-published_at')[:FRONT_WINDOW])
    lead = next((p for p in ordered if p.is_featured), None)
    if lead is None:
        lead = posts.filter(is_featured=True).order_by('-published_at').first() or \
            (ordered[0] if ordered else None)
    rest = [p for p in ordered if lead is None or p.pk != lead.pk]
    top_stack = rest[:3]

    shown = {p.pk for p in top_stack} | ({lead.pk} if lead else set())
    sections = []
    for cat in ctx['nav_categories'][:4]:
        items = [p for p in ordered if p.category_id == cat.pk and p.pk not in shown][:4]
        if items:
            sections.append({'category': cat, 'posts': items})

    # "More stories": pagination kwenye database (si kwenye Python list)
    rest_qs = posts.exclude(pk__in=list(shown)).order_by('-published_at')
    page = Paginator(rest_qs, PER_PAGE).get_page(request.GET.get('page'))
    ctx.update({
        'front': True,
        'lead': lead,
        'featured': lead,           # jina la zamani (kwa template za zamani)
        'top_stack': top_stack,
        'sections': sections,
        'page': page,
        'posts': page.object_list,
    })
    return render(request, 'blog/blog_list.html', ctx)


def blog_detail(request, slug):
    """Makala moja + maoni + share + related."""
    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'), slug=slug, status='published')

    # View counter (F() ili kuepuka race condition)
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)

    rkey = f'blog:rel:{cache_version()}:{post.pk}'
    related = cache.get(rkey)
    if related is None:
        related = list(_published().filter(category=post.category).exclude(pk=post.pk)
                       .order_by('-published_at')[:4])
        if len(related) < 4:
            extra = (_published().exclude(pk=post.pk).exclude(pk__in=[r.pk for r in related])
                     .order_by('-published_at')[:4 - len(related)])
            related += list(extra)
        cache.set(rkey, related, CACHE_SECONDS)

    approved = BlogComment.objects.filter(is_approved=True)
    comments = (approved.filter(post=post, parent__isnull=True)
                .prefetch_related(Prefetch('replies', queryset=approved.order_by('created_at')))
                .order_by('-created_at'))
    comment_count = approved.filter(post=post).count()

    reply_to = None
    rid = request.GET.get('reply')
    if rid and rid.isdigit():
        reply_to = approved.filter(post=post, pk=int(rid)).first()

    ctx = {
        'post': post,
        'related': related,
        'comments': comments,
        'comment_count': comment_count,
        'reply_to': reply_to,
        'notice': request.GET.get('c', ''),
        'share': _share_urls(request, post),
        'canonical': f'{CANONICAL_BASE}/blog/{post.slug}/',
        'site_root': CANONICAL_BASE,
        'word_count': len(re.sub(r'<[^>]+>', ' ', post.body).split()),
    }
    ctx.update(_nav_context())
    return render(request, 'blog/blog_detail.html', ctx)


# ─────────────────────────────────────────────
# WAANDISHI + SERA YA UHARIRI (E-E-A-T: Google inataka kujua nani anaandika
# na jinsi habari zinavyohakikiwa — muhimu kwa Google Discover / News)
# ─────────────────────────────────────────────
def blog_author(request, slug):
    author = get_object_or_404(BlogAuthor, slug=slug, is_active=True)
    posts = _published().filter(author=author).order_by('-published_at')
    page = Paginator(posts, PER_PAGE).get_page(request.GET.get('page'))
    ctx = {
        'author': author, 'page': page, 'posts': page.object_list,
        'post_count': page.paginator.count,
        'canonical': f'{CANONICAL_BASE}/blog/author/{author.slug}/'
                     + (f'?page={page.number}' if page.number > 1 else ''),
        'site_root': CANONICAL_BASE,
    }
    ctx.update(_nav_context())
    return render(request, 'blog/author.html', ctx)


def editorial_policy(request):
    ctx = {
        'authors': BlogAuthor.objects.filter(is_active=True),
        'canonical': f'{CANONICAL_BASE}/blog/editorial-policy/',
        'site_root': CANONICAL_BASE,
        'contact_email': getattr(settings, 'BLOG_REVIEW_EMAIL', '') or 'info@jamiitek.com',
    }
    ctx.update(_nav_context())
    return render(request, 'blog/editorial_policy.html', ctx)


# ─────────────────────────────────────────────
# MAONI (comments)
# ─────────────────────────────────────────────
_LINK_RE = re.compile(r'(https?://|www\.)', re.I)


@require_POST
def blog_comment(request, slug):
    """Pokea maoni au jibu. Ulinzi: honeypot, Turnstile, kasi (rate limit), viungo."""
    from .turnstile import verify_token, get_client_ip

    post = get_object_or_404(BlogPost, slug=slug, status='published')
    url = reverse('blog_detail', args=[slug])
    is_staff = request.user.is_authenticated and request.user.is_staff

    def back(code, anchor='comments'):
        return redirect(f'{url}?c={code}#{anchor}')

    # Honeypot: bots hujaza field iliyofichwa. Tunajifanya imefanikiwa.
    if request.POST.get('website'):
        return back('posted')

    name = (request.POST.get('name') or '').strip()[:60]
    body = (request.POST.get('body') or '').strip()
    email = (request.POST.get('email') or '').strip()[:254]
    if is_staff and not name:
        name = 'JamiiTek'

    if not name or len(body) < 2:
        return back('empty', 'comment-form')
    if len(body) > 2000:
        return back('long', 'comment-form')
    if len(_LINK_RE.findall(body)) > 2 and not is_staff:
        return back('links', 'comment-form')
    if email:
        try:
            validate_email(email)
        except ValidationError:
            email = ''

    ip = get_client_ip(request)
    if not is_staff:
        key = f'blogc:{ip}'
        if cache.get(key):
            return back('slow', 'comment-form')
        ok, _codes = verify_token(request.POST.get('cf-turnstile-response'), ip)
        if not ok:
            return back('captcha', 'comment-form')
        cache.set(key, 1, 20)

    parent = None
    pid = request.POST.get('parent') or ''
    if pid.isdigit():
        parent = BlogComment.objects.filter(pk=int(pid), post=post, is_approved=True).first()
        if parent and parent.parent_id:          # ngazi moja tu ya majibu
            parent = parent.parent

    comment = BlogComment.objects.create(
        post=post, parent=parent, name=name, email=email, body=body,
        is_staff_reply=is_staff, ip=ip)

    if not is_staff:
        _notify_owner_async(comment)

    return back('posted', f'comment-{comment.pk}')


def _notify_owner_async(comment):
    """Mjulishe mmiliki kuna maoni mapya (nyuma, isichelewesha msomaji)."""
    def _send():
        try:
            from apps.utils.email_notifications import send_blog_comment_notice
            send_blog_comment_notice(comment)
        except Exception:
            logger.exception('blog comment notice failed')
    threading.Thread(target=_send, daemon=True).start()
