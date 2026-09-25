"""
Blog RSS feed — /blog/feed/

Inasaidia SEO (Google News/Discover, RSS readers, syndication) na inaruhusu
wasomaji kufuatilia makala mpya.
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed


class BlogFeed(Feed):
    feed_type = Rss201rev2Feed
    title = 'JamiiTek Insights — Latest Articles'
    link = '/blog/'
    description = 'Daily Tanzania & world news, plus digital tips for businesses — from JamiiTek.'
    feed_copyright = 'JamiiTek Technologies'

    def items(self):
        from apps.models import BlogPost
        return BlogPost.objects.filter(status='published').order_by('-published_at')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return reverse('blog_detail', kwargs={'slug': item.slug})

    def item_pubdate(self, item):
        return item.published_at

    def item_updateddate(self, item):
        return item.updated_at

    def item_author_name(self, item):
        return item.author_name or 'JamiiTek'

    def item_categories(self, item):
        return [item.category.name] if item.category else []
