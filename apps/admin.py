from django.contrib import admin
from .forms import ServiceAdminForm,TeamAdminForm
from django.utils.safestring import mark_safe


from .models import Service, Question, Team, Contact, WebsiteType, Client, ProjectProposal

# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ('Service_type', 'created_at')
#     search_fields = ('Service_type',)

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
