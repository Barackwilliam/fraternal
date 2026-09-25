"""
JamiiTek SEO — robots.txt and other SEO endpoints
"""
from django.http import HttpResponse
from django.views.decorators.cache import cache_page


@cache_page(60 * 60 * 24)  # Cache 24 hours
def robots_txt(request):
    """
    Dynamic robots.txt — tells Google exactly what to crawl.
    Blocks admin/private portals, allows everything public.
    """
    host = request.get_host().split(':')[0]
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Block private areas",
        "Disallow: /admin/",
        "Disallow: /manage/",
        "Disallow: /chatbot/dashboard/",
        "Disallow: /chatbot/config/",
        "Disallow: /chatbot/conversations/",
        "Disallow: /chatbot/billing/",
        "Disallow: /chatbot/setup/",
        "Disallow: /portal/",
        "Disallow: /chatbot/webhook/",
        "Disallow: /chatbot/simulate/",
        "Disallow: /api/",
        "Disallow: /cron/",
        "",
        "# Allow important public pages",
        "Allow: /chatbot/register/",
        "Allow: /chatbot/login/",
        "Allow: /bot/",
        "",
        # Crawl-delay imeondolewa: Bing inaiheshimu na ingechelewesha
        # indexing ya habari mpya (makala ~10 kwa siku). Google inaipuuza.
        f"# Sitemaps",
        f"Sitemap: https://{host}/sitemap.xml",
        f"Sitemap: https://{host}/news-sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def news_sitemap(request):
    """
    Google News sitemap — makala za siku 2 zilizopita (kanuni ya Google News).
    Inasaidia habari mpya kuonekana haraka kwenye Google News / Top stories / Discover.
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.utils.html import escape
    from django.core.cache import cache
    from apps.models import BlogPost
    from apps.blog_views import cache_version

    host = request.get_host().split(':')[0]
    key = f'blog:newsmap:{cache_version()}:{host}'
    xml = cache.get(key)
    if xml is None:
        since = timezone.now() - timedelta(days=2)
        posts = (BlogPost.objects.filter(status='published', published_at__gte=since)
                 .order_by('-published_at').only('slug', 'title', 'published_at', 'cover_image',
                                                  'focus_keyword')[:1000])
        items = []
        for p in posts:
            img = (f'<image:image><image:loc>{escape(p.cover_image)}</image:loc></image:image>'
                   if p.cover_image else '')
            kw = (f'<news:keywords>{escape(p.focus_keyword)}</news:keywords>'
                  if p.focus_keyword else '')
            items.append(
                f'<url><loc>https://{host}/blog/{p.slug}/</loc>'
                f'<news:news><news:publication><news:name>JamiiTek Insights</news:name>'
                f'<news:language>en</news:language></news:publication>'
                f'<news:publication_date>{p.published_at.isoformat()}</news:publication_date>'
                f'<news:title>{escape(p.title)}</news:title>{kw}</news:news>{img}</url>')
        xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9" '
               'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
               + ''.join(items) + '</urlset>')
        cache.set(key, xml, 600)
    return HttpResponse(xml, content_type='application/xml')
