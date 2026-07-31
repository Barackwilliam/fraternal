"""
JamiiTek SEO — Sitemap definitions
Covers: public pages, service pages, chatbot landing, bot registration
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import date


class StaticPageSitemap(Sitemap):
    """All important static/public pages."""
    protocol = 'https'
    changefreq = 'weekly'

    pages = [
        # (url_name, priority, changefreq)
        ('home',            1.0,  'daily'),
        ('service',         0.9,  'weekly'),
        ('About',           0.7,  'monthly'),
        ('contact',         0.7,  'monthly'),
        ('select_website',  0.8,  'weekly'),
        ('jamiibot_landing',0.95, 'daily'),     # Bot landing page
        ('chatbot_register',0.9,  'weekly'),    # Bot signup
    ]

    def items(self):
        return self.pages

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]

    def lastmod(self, item):
        return date.today()


class ServiceSitemap(Sitemap):
    """Dynamic service pages."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.85

    def items(self):
        from apps.models import Service
        return Service.objects.all()

    def location(self, item):
        return reverse('service')

    def lastmod(self, item):
        return date.today()


# Combine all sitemaps
sitemaps = {
    'static':   StaticPageSitemap(),
    'services': ServiceSitemap(),
}