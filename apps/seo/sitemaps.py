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
        # Bila ordering, pagination ya sitemap inaweza kutoa matokeo
        # yasiyolingana kila ombi (UnorderedObjectListWarning).
        # Kila huduma ilikuwa na location ile ile (/service/), kwa hiyo
        # huduma 8 = URL moja iliyorudiwa mara 8 kwenye sitemap. Google
        # inaona nakala. Moja inatosha.
        return Service.objects.order_by('pk')[:1]

    def location(self, item):
        return reverse('service')

    def lastmod(self, item):
        return date.today()


class BlogSitemap(Sitemap):
    """Published blog posts + the blog index."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        from apps.models import BlogPost
        # .only(): bila kupakia body ya kila makala (sitemap ingekuwa nzito sana)
        return list(BlogPost.objects.filter(status='published').order_by('-published_at')
                    .only('slug', 'updated_at', 'published_at'))

    def location(self, item):
        return reverse('blog_detail', kwargs={'slug': item.slug})

    def lastmod(self, item):
        return item.updated_at or item.published_at


class BlogAuthorSitemap(Sitemap):
    """Kurasa za waandishi + sera ya uhariri (E-E-A-T)."""
    protocol = 'https'
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        from apps.models import BlogAuthor
        return ['__policy__'] + list(BlogAuthor.objects.filter(is_active=True).order_by('pk'))

    def location(self, item):
        if item == '__policy__':
            return reverse('blog_editorial')
        return reverse('blog_author', args=[item.slug])


class BlogIndexSitemap(Sitemap):
    """The /blog/ landing page."""
    protocol = 'https'
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return ['blog_list']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        from apps.models import BlogPost
        latest = BlogPost.objects.filter(status='published').order_by('-published_at').first()
        return latest.published_at if latest else date.today()


# Combine all sitemaps
sitemaps = {
    'static':     StaticPageSitemap(),
    'services':   ServiceSitemap(),
    'blog_index': BlogIndexSitemap(),
    'blog':       BlogSitemap(),
    'blog-authors': BlogAuthorSitemap(),
}