from django.contrib import admin

from .models import Alama, Kazi, Ripoti


@admin.register(Kazi)
class KaziAdmin(admin.ModelAdmin):
    list_display = ('title', 'worker', 'status', 'priority', 'channel', 'created_at')
    list_filter = ('worker', 'status', 'channel', 'priority')
    search_fields = ('title', 'detail', 'recipient_name', 'recipient_email', 'key')
    readonly_fields = ('created_at', 'updated_at', 'closed_at', 'pushed_at', 'wilife_code')


@admin.register(Ripoti)
class RipotiAdmin(admin.ModelAdmin):
    list_display = ('date', 'kind', 'delivered', 'created_at')
    list_filter = ('kind',)


@admin.register(Alama)
class AlamaAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')
