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
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import BlogPost, BlogCategory, BlogComment

logger = logging.getLogger(__name__)

PER_PAGE = 12


def _share_urls(request, post):
    """Tengeneza share links za social media kwa post."""
    url = request.build_absolute_uri(f'/blog/{post.slug}/')
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
    return (BlogPost.objects.filter(status='published')
            .select_related('category')
            .annotate(n_comments=Count('comments', filter=Q(comments__is_approved=True))))


def _nav_context():
    """Vitu vinavyoonekana kwenye kila ukurasa wa blog: categories, ticker, most read."""
    cats = (BlogCategory.objects
            .annotate(n=Count('posts', filter=Q(posts__status='published')))
            .filter(n__gt=0).order_by('-n', 'name'))
    ticker = list(BlogPost.objects.filter(status='published')
                  .order_by('-published_at').values('title', 'slug')[:8])
    most_read = list(BlogPost.objects.filter(status='published')
                     .select_related('category').order_by('-views', '-published_at')[:5])
    return {'nav_categories': cats, 'ticker': ticker, 'most_read': most_read}


def blog_list(request):
    """Ukurasa wa mbele wa blog, au matokeo ya category / search."""
    posts = _published()

    cat_slug = request.GET.get('category')
    active_cat = BlogCategory.objects.filter(slug=cat_slug).first() if cat_slug else None
    q = (request.GET.get('q') or '').strip()[:100]

    ctx = {'active_cat': active_cat, 'q': q, 'categories': BlogCategory.objects.all()}
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

    # Ukurasa wa mbele (mtindo wa gazeti)
    ordered = list(posts.order_by('-published_at'))
    lead = next((p for p in ordered if p.is_featured), ordered[0] if ordered else None)
    rest = [p for p in ordered if lead is None or p.pk != lead.pk]
    top_stack, rest = rest[:3], rest[3:]

    shown = {p.pk for p in top_stack} | ({lead.pk} if lead else set())
    sections = []
    for cat in ctx['nav_categories'][:4]:
        items = [p for p in ordered if p.category_id == cat.pk and p.pk not in shown][:4]
        if items:
            sections.append({'category': cat, 'posts': items})

    page = Paginator(rest, PER_PAGE).get_page(request.GET.get('page'))
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
        BlogPost.objects.select_related('category'), slug=slug, status='published')

    # View counter (F() ili kuepuka race condition)
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)

    related = list(_published().filter(category=post.category).exclude(pk=post.pk)
                   .order_by('-published_at')[:4])
    if len(related) < 4:
        extra = (_published().exclude(pk=post.pk).exclude(pk__in=[r.pk for r in related])
                 .order_by('-published_at')[:4 - len(related)])
        related += list(extra)

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
        'canonical': request.build_absolute_uri(f'/blog/{post.slug}/'),
    }
    ctx.update(_nav_context())
    return render(request, 'blog/blog_detail.html', ctx)


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
