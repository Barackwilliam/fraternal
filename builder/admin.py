from django.contrib import admin
from .models import ClientWebsite, SitePage, SiteCollection, SiteItem, SiteAsset, AiUsageLog


@admin.register(ClientWebsite)
class ClientWebsiteAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'subdomain', 'website_type', 'owner',
                    'is_published', 'is_suspended', 'created_at')
    list_filter = ('website_type', 'is_published', 'is_suspended')
    search_fields = ('site_name', 'subdomain', 'owner__username')
    actions = ['suspend_sites', 'unsuspend_sites']

    @admin.action(description='Simamisha websites (suspend)')
    def suspend_sites(self, request, queryset):
        queryset.update(is_suspended=True)

    @admin.action(description='Rudisha websites (unsuspend)')
    def unsuspend_sites(self, request, queryset):
        queryset.update(is_suspended=False)


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'website', 'updated_at')
    search_fields = ('title', 'website__subdomain')


@admin.register(SiteCollection)
class SiteCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'website')


@admin.register(SiteItem)
class SiteItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection', 'is_visible', 'is_featured', 'updated_at')
    list_filter = ('is_visible', 'is_featured')


admin.site.register(SiteAsset)
admin.site.register(AiUsageLog)
