"""Blog views — list, detail, na social sharing."""
from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.http import Http404
from urllib.parse import quote

from .models import BlogPost, BlogCategory


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


def blog_list(request):
    """Ukurasa wa blog: posts zote zilizochapishwa."""
    posts = BlogPost.objects.filter(status='published')
    featured = posts.filter(is_featured=True).first()
    if featured:
        posts = posts.exclude(pk=featured.pk)

    # Category filter
    cat_slug = request.GET.get('category')
    active_cat = None
    if cat_slug:
        active_cat = BlogCategory.objects.filter(slug=cat_slug).first()
        if active_cat:
            posts = posts.filter(category=active_cat)

    categories = BlogCategory.objects.all()
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'featured': featured,
        'categories': categories,
        'active_cat': active_cat,
    })


def blog_detail(request, slug):
    """Post moja + share buttons + related."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')

    # View counter (F() ili kuepuka race condition)
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)

    related = (BlogPost.objects
               .filter(status='published', category=post.category)
               .exclude(pk=post.pk)[:3])

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'related': related,
        'share': _share_urls(request, post),
        'canonical': request.build_absolute_uri(f'/blog/{post.slug}/'),
    })
