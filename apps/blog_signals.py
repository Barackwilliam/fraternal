"""
Blog signals:
1. Makala/maoni yakibadilika → cache ya blog inafutwa papo hapo (kasi bila data ya zamani).
2. Makala ikichapishwa (au kubadilishwa ikiwa published) → IndexNow ping (SEO: indexing haraka).
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .models import BlogPost, BlogComment, BlogAuthor


def _bump():
    from .blog_views import bump_cache_version
    try:
        bump_cache_version()
    except Exception:
        pass


@receiver(pre_save, sender=BlogPost)
def _remember_status(sender, instance, **kwargs):
    old = None
    if instance.pk:
        old = sender.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
    instance._old_status = old


@receiver(post_save, sender=BlogPost)
def _post_saved(sender, instance, **kwargs):
    _bump()
    if instance.status == 'published':
        from .indexnow import ping
        paths = [f'/blog/{instance.slug}/']
        if getattr(instance, '_old_status', None) != 'published':
            paths.append('/blog/')          # makala mpya → ukurasa wa mbele umebadilika
        ping(paths)


@receiver(post_delete, sender=BlogPost)
@receiver(post_save, sender=BlogAuthor)
@receiver(post_delete, sender=BlogAuthor)
@receiver(post_save, sender=BlogComment)
@receiver(post_delete, sender=BlogComment)
def _changed(sender, **kwargs):
    _bump()
