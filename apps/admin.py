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
    list_display = ("client", "website_type", "created_at", "updated_at", "convert_link")
    list_filter = ("website_type", "created_at")
    search_fields = ("client__name", "website_type__name")

    def convert_link(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(
            f'<a href="/manage/proposals/from-lead/{obj.pk}/" '
            f'style="background:#25d366;color:#04120a;padding:5px 11px;border-radius:6px;'
            f'font-weight:700;text-decoration:none;white-space:nowrap">'
            f'→ Premium Proposal</a>'
        )
    convert_link.short_description = 'Convert'


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

# ============================================================
# WEBSITE TEMPLATES ADMIN
# ============================================================
from .models import WebsiteTemplate

@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'badge', 'rating', 'price_hosted_monthly', 'price_source_code', 'is_active', 'order')
    list_editable = ('is_active', 'order', 'badge')
    list_filter   = ('category', 'is_active', 'badge')
    search_fields = ('name', 'description')
    ordering      = ('order', '-created_at')

    fieldsets = (
        ('📋 Basic Info', {
            'fields': ('name', 'category', 'description', 'badge', 'rating')
        }),
        ('💰 Pricing', {
            'fields': ('price_hosted_monthly', 'price_source_code'),
            'description': 'Bei za plan 1 (hosted) na plan 3 (source code). Plan 2 (Full Build) ni Custom Quote daima.'
        }),
        ('🎨 Card Appearance', {
            'fields': ('gradient_start', 'gradient_end'),
            'description': 'Rangi za gradient kwenye card. Tumia hex colors kama #ff6584'
        }),
        ('💻 Template HTML Code', {
            'fields': ('preview_html',),
            'description': '⚠️ Weka HTML code yote ya template hapa. Itaonekana kwenye /templates/preview/<id>/'
        }),
        ('⚙️ Settings', {
            'fields': ('is_active', 'order')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['preview_html'].widget.attrs.update({
            'rows': 30,
            'style': 'font-family: monospace; font-size: 12px; background: #1e1e1e; color: #d4d4d4; padding: 10px;'
        })
        return form


# ============================================================
# BLOG ADMIN
# ============================================================
from .models import BlogPost, BlogCategory


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'status', 'category', 'is_featured', 'views', 'published_at')
    list_filter = ('status', 'is_featured', 'category')
    search_fields = ('title', 'excerpt', 'body', 'focus_keyword')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('status', 'is_featured')
    readonly_fields = ('views', 'created_at', 'updated_at', 'read_minutes')
    change_list_template = 'admin/blog_changelist.html'
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'body', 'cover_image')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword'),
            'description': 'Leave meta fields blank to auto-use the title and excerpt.'
        }),
        ('Publishing', {
            'fields': ('author_name', 'status', 'is_featured', 'published_at')
        }),
        ('Stats', {
            'fields': ('views', 'read_minutes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('ai-write/', self.admin_site.admin_view(self.ai_write_view),
                 name='blog_ai_write'),
        ]
        return custom + urls

    def ai_write_view(self, request):
        """Button ya admin: AI inaandika rasimu papo hapo."""
        from django.shortcuts import redirect
        from django.contrib import messages
        from apps.models import BlogPost, BlogCategory
        from apps import blog_ai

        existing = list(BlogPost.objects.values_list('title', flat=True))
        try:
            ok, result = blog_ai.generate_draft(existing_titles=existing)
        except Exception as e:
            messages.error(request, f'AI imeshindwa: {type(e).__name__}')
            return redirect('admin:apps_blogpost_changelist')

        if not ok:
            messages.error(request, f'AI imeshindwa: {result}')
            return redirect('admin:apps_blogpost_changelist')

        base_slug = result['slug']
        slug = base_slug
        n = 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{n}'
            n += 1

        cat, _ = BlogCategory.objects.get_or_create(
            slug='web-development', defaults={'name': 'Web Development'})

        post = BlogPost.objects.create(
            title=result['title'], slug=slug, category=cat,
            excerpt=result['excerpt'], body=result['body'],
            meta_description=result['meta_description'],
            focus_keyword=result['focus_keyword'],
            author_name='JamiiTek', status='draft', is_featured=False,
        )
        messages.success(request,
            f'✓ AI imeandika rasimu: "{post.title}" ({result["language"].upper()}). '
            f'Kagua na uweke Published ukiridhika.')
        return redirect('admin:apps_blogpost_change', post.pk)


# ============================================================
# CONTRACT ADMIN (na AI drafting)
# ============================================================
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'client_col', 'status', 'amount_col', 'currency',
                    'signed_name', 'created_at', 'builder_link')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('title', 'project_name', 'client_name', 'client__name', 'signed_name')
    readonly_fields = ('token', 'share_link', 'signed_name', 'signed_email', 'signed_at',
                       'signed_ip', 'signed_language', 'viewed_at', 'sent_at',
                       'created_at', 'updated_at')
    fieldsets = (
        ('✨ New: Use the Contract Builder for dynamic sections, line items & AI on every field', {
            'fields': (),
            'description': 'This admin form still works, but for sections/line-items/custom-fields '
                           'and per-field AI, use <a href="/manage/contracts/" target="_blank">the Contract Builder</a> instead.'
        }),
        ('Client (optional — registered client OR type details directly below)', {
            'fields': ('client', 'client_name', 'client_email', 'client_company', 'client_phone', 'client_address')
        }),
        ('Project', {
            'fields': ('title', 'project_name')
        }),
        ('Terms Summary (shows at top of contract)', {
            'fields': ('total_amount', 'currency', 'payment_terms', 'timeline')
        }),
        ('Contract Text — use "AI: Draft contract" button, then edit here', {
            'fields': ('body_en', 'body_sw'),
            'description': 'You can draft with AI (button top-right of the list), then refine before sending. '
                           'For dynamic sections instead of one long text, use the Contract Builder.'
        }),
        ('Branding & Signatures', {
            'fields': ('accent_color', 'logo_url', 'provider_signature',
                       'provider_signed_date', 'signature_block_en', 'signature_block_sw'),
            'classes': ('collapse',)
        }),
        ('Provider (JamiiTek)', {
            'fields': ('provider_name', 'provider_rep')
        }),
        ('Status & Sharing', {
            'fields': ('status', 'share_link', 'token')
        }),
        ('Signature (filled when client signs)', {
            'fields': ('signed_name', 'signed_email', 'signed_at', 'signed_ip',
                       'signed_language', 'agreed_to_terms', 'decline_reason'),
            'classes': ('collapse',)
        }),
        ('Tracking', {
            'fields': ('viewed_at', 'sent_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_col(self, obj):
        return obj.display_client
    client_col.short_description = 'Client'

    def amount_col(self, obj):
        return obj.computed_total or obj.total_amount or '—'
    amount_col.short_description = 'Amount'

    def builder_link(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<a href="/manage/contracts/{obj.pk}/edit/" target="_blank">Open in Builder →</a>')
    builder_link.short_description = 'Builder'

    def share_link(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.pk or not obj.token:
            return '— (save first)'
        url = f'https://jamiitek.com/contract/{obj.token}/'
        return mark_safe(
            f'<a href="{url}" target="_blank" style="color:#25d366;font-weight:600">{url}</a>'
            f'<br><small style="color:#888">Send this link to your client. They choose language & sign or download.</small>')
    share_link.short_description = 'Client link'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('<int:pk>/ai-draft/', self.admin_site.admin_view(self.ai_draft_view),
                 name='contract_ai_draft'),
        ]
        return custom + urls

    def ai_draft_view(self, request, pk):
        """AI inaandaa maandishi ya mkataba (EN + SW) kutoka info ya contract."""
        from django.shortcuts import redirect
        from django.contrib import messages
        from apps import contract_ai

        contract = self.get_object(request, pk)
        if not contract:
            messages.error(request, 'Contract not found.')
            return redirect('admin:apps_contract_changelist')

        info = {
            'client_name': contract.client.name,
            'company': contract.client.company,
            'project_name': contract.project_name,
            'title': contract.title,
            'total_amount': contract.total_amount,
            'currency': contract.currency,
            'payment_terms': contract.payment_terms,
            'timeline': contract.timeline,
            'scope': contract.project_name or contract.title,
            'provider_rep': contract.provider_rep,
        }
        try:
            ok, result = contract_ai.generate_contract(info)
        except Exception as e:
            messages.error(request, f'AI failed: {type(e).__name__}')
            return redirect('admin:apps_contract_change', pk)

        if not ok:
            messages.error(request, f'AI failed: {result}')
            return redirect('admin:apps_contract_change', pk)

        contract.title = result['title'] or contract.title
        contract.body_en = result['body_en']
        contract.body_sw = result['body_sw']
        contract.save(update_fields=['title', 'body_en', 'body_sw'])
        messages.success(request,
            '✓ AI drafted the contract in English & Swahili. Review and refine below, '
            'then set status to "Sent" and share the link with your client.')
        return redirect('admin:apps_contract_change', pk)

    change_form_template = 'admin/contract_change_form.html'


# ── PROPOSAL ADMIN ──
from .models import Proposal
from django.utils.safestring import mark_safe


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('title', 'client_col', 'status', 'value_col', 'currency',
                    'reference_number', 'created_at', 'builder_link')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('title', 'project_name', 'client_name', 'reference_number', 'accepted_name')
    readonly_fields = ('token', 'reference_number', 'accepted_name', 'accepted_email',
                       'accepted_at', 'accepted_ip', 'viewed_at', 'sent_at',
                       'created_at', 'updated_at')
    fieldsets = (
        ('✨ Use the Proposal Builder for the full experience', {
            'fields': (),
            'description': 'This admin form works, but for the premium builder with AI on '
                           'every field, line items, and timeline, use '
                           '<a href="/manage/proposals/" target="_blank">the Proposal Builder</a>.'
        }),
        ('Client (optional)', {
            'fields': ('client', 'client_name', 'client_email', 'client_company', 'client_phone')
        }),
        ('Proposal', {
            'fields': ('title', 'project_name', 'reference_number', 'valid_until', 'status')
        }),
        ('Content (English)', {
            'fields': ('summary_en', 'scope_en', 'about_en'),
            'classes': ('collapse',)
        }),
        ('Content (Swahili)', {
            'fields': ('summary_sw', 'scope_sw', 'about_sw'),
            'classes': ('collapse',)
        }),
        ('Pricing & Terms', {
            'fields': ('currency', 'discount_amount', 'pricing_note', 'payment_terms')
        }),
        ('Branding', {
            'fields': ('accent_color', 'logo_url', 'provider_name', 'provider_rep'),
            'classes': ('collapse',)
        }),
        ('Response (filled when client accepts)', {
            'fields': ('accepted_name', 'accepted_email', 'accepted_at', 'accepted_ip', 'decline_reason'),
            'classes': ('collapse',)
        }),
        ('Sharing & Tracking', {
            'fields': ('token', 'viewed_at', 'sent_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def client_col(self, obj):
        return obj.display_client
    client_col.short_description = 'Client'

    def value_col(self, obj):
        return obj.grand_total or '—'
    value_col.short_description = 'Value'

    def builder_link(self, obj):
        return mark_safe(f'<a href="/manage/proposals/{obj.pk}/edit/" target="_blank">Open in Builder →</a>')
    builder_link.short_description = 'Builder'


# ── COMPANY PROFILE + INVOICE ADMIN ──
from .models import CompanyProfile, Invoice


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('company_name', 'is_active', 'updated_at', 'builder_link')
    fieldsets = (
        ('✨ Use the Company Profile builder', {
            'fields': (),
            'description': 'For the full editor with AI, use '
                           '<a href="/manage/profile/" target="_blank">the Company Profile builder</a>.'
        }),
        ('Identity', {'fields': ('company_name', 'short_name', 'tagline_en', 'tagline_sw',
                                 'subtitle_en', 'subtitle_sw', 'period', 'logo_url', 'is_active')}),
        ('Content (English)', {'fields': ('about_en', 'mission_en', 'vision_en', 'pricing_note_en'),
                               'classes': ('collapse',)}),
        ('Content (Swahili)', {'fields': ('about_sw', 'mission_sw', 'vision_sw', 'pricing_note_sw'),
                               'classes': ('collapse',)}),
        ('Contact', {'fields': ('email', 'phone', 'website', 'address')}),
    )

    def builder_link(self, obj):
        return mark_safe('<a href="/manage/profile/" target="_blank">Open builder →</a>')
    builder_link.short_description = 'Builder'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('invoice_number', 'client_col', 'invoice_type', 'total_col',
                    'balance_col', 'status', 'due_date', 'builder_link')
    list_filter = ('status', 'invoice_type', 'currency', 'created_at')
    search_fields = ('invoice_number', 'title', 'client_name', 'project_name', 'paid_reference')
    readonly_fields = ('token', 'viewed_at', 'sent_at', 'created_at', 'updated_at')
    fieldsets = (
        ('✨ Use the Invoice builder', {
            'fields': (),
            'description': 'For live totals, VAT, payment methods and AI, use '
                           '<a href="/manage/invoices/" target="_blank">the Invoice builder</a>.'
        }),
        ('Client (optional)', {'fields': ('client', 'client_name', 'client_email',
                                          'client_company', 'client_phone', 'client_address')}),
        ('Invoice', {'fields': ('invoice_number', 'invoice_type', 'title', 'project_name',
                                'issue_date', 'due_date', 'status')}),
        ('Amounts', {'fields': ('currency', 'tax_percent', 'discount_amount', 'amount_paid',
                                'payment_terms', 'paid_reference', 'paid_at')}),
        ('Notes', {'fields': ('notes_en', 'notes_sw'), 'classes': ('collapse',)}),
        ('Branding', {'fields': ('provider_name', 'provider_rep', 'logo_url'), 'classes': ('collapse',)}),
        ('Tracking', {'fields': ('token', 'viewed_at', 'sent_at', 'created_at', 'updated_at'),
                      'classes': ('collapse',)}),
    )

    def client_col(self, obj):
        return obj.display_client
    client_col.short_description = 'Client'

    def total_col(self, obj):
        return f'{obj.currency} {obj.grand_total:,.0f}'
    total_col.short_description = 'Total'

    def balance_col(self, obj):
        return '—' if obj.is_paid else f'{obj.balance_due:,.0f}'
    balance_col.short_description = 'Balance'

    def builder_link(self, obj):
        return mark_safe(f'<a href="/manage/invoices/{obj.pk}/edit/" target="_blank">Open in Builder →</a>')
    builder_link.short_description = 'Builder'
