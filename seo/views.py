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
        "# Crawl delay for polite bots",
        "Crawl-delay: 5",
        "",
        f"# Sitemap",
        f"Sitemap: https://{host}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")