from django.contrib import admin
from .models import Service, Question, Team, Contact, WebsiteType, Client, ProjectProposal

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('Service_type', 'created_at')
    search_fields = ('Service_type',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question',)
    search_fields = ('question',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position')
    search_fields = ('full_name', 'position')

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
