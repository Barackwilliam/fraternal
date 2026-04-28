from django.contrib import admin
from .models import USSDConfig

@admin.register(USSDConfig)
class USSDConfigAdmin(admin.ModelAdmin):
    list_display = ['is_active', 'message_imezimwa']