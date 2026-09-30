"""
Template ikihifadhiwa (admin) → IndexNow ping (Bing, ChatGPT search, DuckDuckGo)
kwa ukurasa wake, jamii yake, marketplace na /llms.txt — zinaorodheshwa ndani ya
dakika badala ya kusubiri crawl. Google inasoma sitemap.xml (TemplateSitemap).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import WebsiteTemplate


@receiver(post_save, sender=WebsiteTemplate)
def _template_saved(sender, instance, **kwargs):
    if not instance.is_active or not instance.slug:
        return
    from .indexnow import ping
    from .template_seo import cat_key, cat_slug
    ping([instance.get_absolute_url(), f'/templates/c/{cat_slug(cat_key(instance))}/',
          '/templates/', '/llms.txt'])
