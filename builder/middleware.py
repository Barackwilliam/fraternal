"""
Subdomain routing: dukalangu.jamiitek.com → website ya mteja.
jamiitek.com / www.jamiitek.com / jamiitek.onrender.com → platform yenyewe.
"""
from django.conf import settings
from django.shortcuts import render

# Hosts zinazoserve platform kuu (si website za wateja)
PLATFORM_HOSTS = getattr(settings, 'BUILDER_PLATFORM_HOSTS', {
    'jamiitek.com', 'www.jamiitek.com', 'jamiitek.onrender.com',
    'localhost', '127.0.0.1', 'testserver',
})

BASE_DOMAIN = getattr(settings, 'BUILDER_BASE_DOMAIN', 'jamiitek.com')


class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        request.client_site = None
        request.subdomain = None

        if host in PLATFORM_HOSTS:
            return self.get_response(request)

        subdomain = None
        if host.endswith('.' + BASE_DOMAIN):
            subdomain = host[: -(len(BASE_DOMAIN) + 1)]
        elif host.endswith('.localhost'):          # kwa testing: duka.localhost:8000
            subdomain = host[: -len('.localhost')]

        if subdomain and '.' not in subdomain and subdomain != 'www':
            from .models import ClientWebsite
            site = (
                ClientWebsite.objects
                .filter(subdomain=subdomain)
                .select_related('owner')
                .first()
            )
            if site is None:
                return render(request, 'builder/public/site_not_found.html',
                              {'subdomain': subdomain}, status=404)
            if site.is_suspended:
                return render(request, 'builder/public/site_suspended.html',
                              {'site': site}, status=403)
            request.client_site = site
            request.subdomain = subdomain
            request.urlconf = 'builder.public_urls'   # URLs za website ya mteja tu

        return self.get_response(request)
