# apps/admin.py
from django.contrib import admin
from .forms import ServiceAdminForm,TeamAdminForm
from django.utils.safestring import mark_safe
from .models import Service, Question, Team, Contact, WebsiteType, Client, ProjectProposal

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'image':
            formfield.widget.attrs.update({
                'role': 'uploadcare-uploader',
                'data-public-key': '76122001cca4add87f02', 
            })
        return formfield

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.get_image_url()}" style="max-height: 100px;" />')
        return "No Image"

    image_preview.short_description = 'Preview'

    list_display = ('Service_type', 'image_preview')
admin.site.register(Service, ServiceAdmin)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question',)



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject')
    search_fields = ('full_name', 'email', 'subject')

@admin.register(WebsiteType)
class WebsiteTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company')
    search_fields = ('name', 'email')

@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ('client', 'website_type', 'created_at', 'updated_at')
    list_filter = ('website_type', 'created_at')
    search_fields = ('client__name', 'website_type__name')


class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'image':
            formfield.widget.attrs.update({
                'role': 'uploadcare-uploader',
                'data-public-key': '76122001cca4add87f02', 
            })
        return formfield

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.get_image_url()}" style="max-height: 100px;" />')
        return "No Image"

    image_preview.short_description = 'Preview'

    list_display = ('full_name', 'position','image_preview')
    search_fields = ('full_name', 'position')

admin.site.register(Team, TeamAdmin)

# ── Management System Admin ────────────────────────────────
from .models import ManagedWebsite, HostingPayment, WebsiteFeature, ScheduledAction, ClientNotification

@admin.register(ManagedWebsite)
class ManagedWebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'hosting_end_date', 'days_until_expiry')
    list_filter = ('status', 'site_type')
    search_fields = ('name', 'client__name', 'url')
    readonly_fields = ('api_key', 'created_at', 'updated_at')
    
    def days_until_expiry(self, obj):
        return f"{obj.days_until_expiry} siku"
    days_until_expiry.short_description = "Inaisha Baada ya"

@admin.register(HostingPayment)
class HostingPaymentAdmin(admin.ModelAdmin):
    list_display = ('website', 'amount', 'payment_date', 'months_covered', 'payment_method')
    list_filter = ('payment_date', 'payment_method')

@admin.register(ScheduledAction)
class ScheduledActionAdmin(admin.ModelAdmin):
    list_display = ('website', 'action_type', 'scheduled_at', 'status')
    list_filter = ('status', 'action_type')
    readonly_fields = ('executed_at', 'result_message')

@admin.register(ClientNotification)
class ClientNotificationAdmin(admin.ModelAdmin):
    list_display = ('client', 'subject', 'notification_type', 'email_sent', 'sent_at')
    list_filter = ('notification_type', 'email_sent')
    readonly_fields = ('sent_at',)
