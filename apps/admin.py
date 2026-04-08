# app/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe

from .forms import ServiceAdminForm, TeamAdminForm
from .models import (
    Service,
    Question,
    Team,
    Contact,
    WebsiteType,
    Client,
    ProjectProposal,
    ManagedWebsite,
    HostingPayment,
    WebsiteFeature,
    ScheduledAction,
    ClientNotification,
    DomainRecord,
    DomainRenewalPayment,
    EmailHostingPlan,
    EmailHostingPayment,
)

# ============================================================
# SERVICE ADMIN
# ============================================================

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == "image":
            formfield.widget.attrs.update({
                "role": "uploadcare-uploader",
                "data-public-key": "4c3ba9de492e0e0eaddc",
            })

        return formfield

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.get_image_url()}" style="max-height:100px;" />'
            )
        return "No Image"

    image_preview.short_description = "Preview"

    list_display = ("service_type", "image_preview")


admin.site.register(Service, ServiceAdmin)


# ============================================================
# FAQ ADMIN
# ============================================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question",)
    search_fields = ("question",)


# ============================================================
# CONTACT MESSAGES
# ============================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "subject")
    search_fields = ("full_name", "email", "subject")


# ============================================================
# WEBSITE TYPES
# ============================================================

@admin.register(WebsiteType)
class WebsiteTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ============================================================
# CLIENT ADMIN
# ============================================================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "company")
    search_fields = ("name", "email")


# ============================================================
# PROJECT PROPOSALS
# ============================================================

@admin.register(ProjectProposal)
class ProjectProposalAdmin(admin.ModelAdmin):
    list_display = ("client", "website_type", "created_at", "updated_at")
    list_filter = ("website_type", "created_at")
    search_fields = ("client__name", "website_type__name")


# ============================================================
# TEAM ADMIN
# ============================================================

class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == "image":
            formfield.widget.attrs.update({
                "role": "uploadcare-uploader",
                "data-public-key": "4c3ba9de492e0e0eaddc",
            })

        return formfield

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.get_image_url()}" style="max-height:100px;" />'
            )
        return "No Image"

    image_preview.short_description = "Preview"

    list_display = ("full_name", "position", "image_preview")
    search_fields = ("full_name", "position")


admin.site.register(Team, TeamAdmin)


# ============================================================
# WEBSITE MANAGEMENT SYSTEM ADMIN
# ============================================================

@admin.register(ManagedWebsite)
class ManagedWebsiteAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "client",
        "status",
        "hosting_end_date",
        "days_until_expiry_display",
    )

    list_filter = ("status", "site_type")

    search_fields = ("name", "client__name", "url")

    readonly_fields = ("api_key", "created_at", "updated_at")

    def days_until_expiry_display(self, obj):
        return f"{obj.days_until_expiry} days"

    days_until_expiry_display.short_description = "Days Until Expiry"


# ============================================================
# HOSTING PAYMENTS
# ============================================================

@admin.register(HostingPayment)
class HostingPaymentAdmin(admin.ModelAdmin):

    list_display = (
        "website",
        "amount",
        "payment_date",
        "months_covered",
        "payment_method",
    )

    list_filter = ("payment_date", "payment_method")


# ============================================================
# SCHEDULED ACTIONS
# ============================================================

@admin.register(ScheduledAction)
class ScheduledActionAdmin(admin.ModelAdmin):

    list_display = (
        "website",
        "action_type",
        "scheduled_at",
        "status",
    )

    list_filter = ("status", "action_type")

    readonly_fields = ("executed_at", "result_message")


# ============================================================
# CLIENT NOTIFICATIONS
# ============================================================

@admin.register(ClientNotification)
class ClientNotificationAdmin(admin.ModelAdmin):

    list_display = (
        "client",
        "subject",
        "notification_type",
        "email_sent",
        "sent_at",
    )

    list_filter = ("notification_type", "email_sent")

    readonly_fields = ("sent_at",)

# ============================================================
# WEBSITE FEATURES
# ============================================================

@admin.register(WebsiteFeature)
class WebsiteFeatureAdmin(admin.ModelAdmin):
    list_display  = ("website", "feature_name", "feature_key", "is_enabled")
    list_filter   = ("is_enabled",)
    search_fields = ("website__name", "feature_key", "feature_name")
    list_editable = ("is_enabled",)


# ============================================================
# DOMAIN RECORDS
# ============================================================

class DomainRenewalPaymentInline(admin.TabularInline):
    model  = DomainRenewalPayment
    extra  = 0
    readonly_fields = ("created_at",)
    fields = ("paid_date", "renewed_until", "amount", "payment_method", "transaction_ref", "recorded_by", "notes")


# DomainDNSRecordInline defined below - added to DomainRecordAdmin via patch at bottom of file

@admin.register(DomainRecord)
class DomainRecordAdmin(admin.ModelAdmin):
    list_display  = ("domain_name", "website", "registrar", "expiry_date", "days_until_expiry_display", "status")
    list_filter   = ("status", "registrar", "auto_renew")
    search_fields = ("domain_name", "website__name", "website__client__name")
    readonly_fields = ("created_at", "updated_at")
    inlines       = [DomainRenewalPaymentInline]

    def days_until_expiry_display(self, obj):
        d = obj.days_until_expiry
        if d < 0:
            return f"Expired {abs(d)}d ago"
        return f"{d} days"
    days_until_expiry_display.short_description = "Days Until Expiry"


@admin.register(DomainRenewalPayment)
class DomainRenewalPaymentAdmin(admin.ModelAdmin):
    list_display  = ("domain", "paid_date", "renewed_until", "amount", "payment_method")
    list_filter   = ("payment_method", "paid_date")
    search_fields = ("domain__domain_name",)
    readonly_fields = ("created_at",)


# ============================================================
# EMAIL HOSTING
# ============================================================

class EmailHostingPaymentInline(admin.TabularInline):
    model  = EmailHostingPayment
    extra  = 0
    readonly_fields = ("created_at",)
    fields = ("payment_date", "months_covered", "amount", "payment_method", "transaction_ref", "recorded_by", "notes")


@admin.register(EmailHostingPlan)
class EmailHostingPlanAdmin(admin.ModelAdmin):
    list_display  = ("plan_name", "client", "email_domain", "accounts_count", "monthly_cost", "end_date", "status")
    list_filter   = ("status",)
    search_fields = ("plan_name", "email_domain", "client__name")
    readonly_fields = ("created_at", "updated_at")
    inlines       = [EmailHostingPaymentInline]


@admin.register(EmailHostingPayment)
class EmailHostingPaymentAdmin(admin.ModelAdmin):
    list_display  = ("plan", "payment_date", "months_covered", "amount", "payment_method")
    list_filter   = ("payment_method", "payment_date")
    search_fields = ("plan__plan_name", "plan__email_domain")
    readonly_fields = ("created_at",)


# ============================================================
# HOSTING CONFIGURATION
# ============================================================

from .models import HostingConfiguration, DomainDNSRecord

@admin.register(HostingConfiguration)
class HostingConfigurationAdmin(admin.ModelAdmin):
    list_display  = ("website", "server_type", "ip_address", "stack", "uptime_percent", "ssl_type", "updated_at")
    list_filter   = ("server_type", "stack", "ssl_type", "cdn_enabled", "auto_backup")
    search_fields = ("website__name", "ip_address", "server_hostname", "ftp_username", "db_name")
    readonly_fields = ("updated_at", "disk_percent", "bandwidth_percent", "ssl_days_left")

    fieldsets = (
        ("Website", {
            "fields": ("website",)
        }),
        ("Server", {
            "fields": ("server_type", "server_os", "stack", "server_location", "ip_address", "server_hostname", "cpu_cores", "ram_mb")
        }),
        ("Resources", {
            "fields": ("disk_total_gb", "disk_used_gb", "bandwidth_gb", "bandwidth_used", "monthly_visits")
        }),
        ("Stack Versions", {
            "fields": ("python_version", "django_version", "php_version", "db_engine", "web_server"),
            "classes": ("collapse",),
        }),
        ("SFTP Access", {
            "fields": ("ftp_host", "ftp_port", "ftp_username"),
            "classes": ("collapse",),
        }),
        ("Database Access", {
            "fields": ("db_host", "db_port", "db_name", "db_username"),
            "classes": ("collapse",),
        }),
        ("SSL Certificate", {
            "fields": ("ssl_type", "ssl_issuer", "ssl_issued_date", "ssl_expiry_date", "https_redirect"),
        }),
        ("Security & Features", {
            "fields": ("firewall_enabled", "ddos_protection", "cdn_enabled", "auto_backup", "backup_frequency", "last_backup"),
        }),
        ("Uptime", {
            "fields": ("uptime_percent", "last_downtime"),
        }),
        ("Notes", {
            "fields": ("notes", "updated_at"),
        }),
    )


# ============================================================
# DNS RECORDS
# ============================================================

class DomainDNSRecordInline(admin.TabularInline):
    model  = DomainDNSRecord
    extra  = 1
    fields = ("record_type", "name", "value", "ttl", "priority", "proxy", "status")


@admin.register(DomainDNSRecord)
class DomainDNSRecordAdmin(admin.ModelAdmin):
    list_display  = ("domain", "record_type", "name", "value", "ttl", "proxy", "status")
    list_filter   = ("record_type", "status", "proxy")
    search_fields = ("domain__domain_name", "name", "value")
    readonly_fields = ("created_at", "updated_at")


# Patch DomainRecordAdmin to include DomainDNSRecordInline (defined above)
DomainRecordAdmin.inlines = [DomainRenewalPaymentInline, DomainDNSRecordInline]