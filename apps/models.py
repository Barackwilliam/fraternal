# app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


# ============================================================
# SERVICES
# ============================================================

class Service(models.Model):
    # service_type = models.CharField(max_length=255)
    Service_type = models.CharField(max_length=100, db_column='Service_type')
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_type

    # Open Graph image (Facebook / WhatsApp preview)
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ""

    # Optimized image for normal website usage
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ""


# ============================================================
# FAQ
# ============================================================

class Question(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    def __str__(self):
        return self.question


# ============================================================
# TEAM MEMBERS
# ============================================================

class Team(models.Model):
    full_name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255)

    facebook_link = models.URLField(max_length=300, blank=True, null=True)
    twitter_link = models.URLField(max_length=300, blank=True, null=True)
    instagram_link = models.URLField(max_length=300, blank=True, null=True)
    linkedin_link = models.URLField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.full_name

    # Open Graph preview
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ""

    # Optimized image
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ""


# ============================================================
# CONTACT MESSAGES
# ============================================================

class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


# ============================================================
# WEBSITE PROJECT SYSTEM
# ============================================================

class WebsiteType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class ProjectProposal(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    website_type = models.ForeignKey(WebsiteType, on_delete=models.CASCADE)

    requirements = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    pdf_file = models.URLField(blank=True)

    def __str__(self):
        return f"{self.client.name} - {self.website_type.name}"


# ============================================================
# WEBSITE MANAGEMENT SYSTEM
# ============================================================

class ManagedWebsite(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("maintenance", "Maintenance"),
        ("terminated", "Terminated"),
    ]

    SITE_TYPE_CHOICES = [
        ("django", "Django Website"),
        ("static", "Static HTML/CSS"),
        ("wordpress", "WordPress"),
        ("other", "Other"),
    ]

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="managed_websites"
    )

    name = models.CharField(max_length=200)
    url = models.URLField()

    site_type = models.CharField(
        max_length=20,
        choices=SITE_TYPE_CHOICES,
        default="django"
    )

    api_key = models.CharField(
        max_length=64,
        unique=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    suspension_message = models.TextField(
        blank=True,
        default="This service has been temporarily suspended. Please contact the administrator."
    )

    suspension_reason = models.TextField(blank=True)

    # Hosting Billing
    hosting_start_date = models.DateField()
    hosting_end_date = models.DateField()

    monthly_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Notification Settings
    auto_suspend_on_expiry = models.BooleanField(default=True)
    send_expiry_warnings = models.BooleanField(default=True)

    warning_days_before = models.IntegerField(default=7)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def days_until_expiry(self):
        return (self.hosting_end_date - timezone.now().date()).days

    @property
    def is_overdue(self):
        return self.hosting_end_date < timezone.now().date()

    @property
    def total_paid(self):
        return sum(p.amount for p in self.payments.all())

    def __str__(self):
        return f"{self.name} ({self.client.name})"

    class Meta:
        verbose_name = "Managed Website"
        verbose_name_plural = "Managed Websites"
        ordering = ["-created_at"]


# ============================================================
# HOSTING PAYMENTS
# ============================================================

class HostingPayment(models.Model):

    website = models.ForeignKey(
        ManagedWebsite,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField()

    months_covered = models.IntegerField(default=1)

    payment_method = models.CharField(
        max_length=50,
        blank=True
    )

    transaction_ref = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(blank=True)

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.website.name} - TZS {self.amount} ({self.payment_date})"

    class Meta:
        verbose_name = "Hosting Payment"
        verbose_name_plural = "Hosting Payments"
        ordering = ["-payment_date"]


# ============================================================
# WEBSITE FEATURES
# ============================================================

class WebsiteFeature(models.Model):

    website = models.ForeignKey(
        ManagedWebsite,
        on_delete=models.CASCADE,
        related_name="features"
    )

    feature_key = models.CharField(max_length=100)
    feature_name = models.CharField(max_length=200)

    is_enabled = models.BooleanField(default=True)

    disabled_reason = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Enabled" if self.is_enabled else "Disabled"
        return f"{status} - {self.website.name} → {self.feature_name}"

    class Meta:
        unique_together = ["website", "feature_key"]
        verbose_name = "Website Feature"
        verbose_name_plural = "Website Features"


# ============================================================
# SCHEDULED ACTIONS
# ============================================================

class ScheduledAction(models.Model):

    ACTION_TYPES = [
        ("suspend", "Suspend Website"),
        ("restore", "Restore Website"),
        ("maintenance", "Enable Maintenance Mode"),
        ("send_email", "Send Email"),
        ("disable_feature", "Disable Feature"),
        ("enable_feature", "Enable Feature"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    website = models.ForeignKey(
        ManagedWebsite,
        on_delete=models.CASCADE,
        related_name="scheduled_actions"
    )

    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES
    )

    scheduled_at = models.DateTimeField()

    action_data = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    executed_at = models.DateTimeField(null=True, blank=True)

    result_message = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} → {self.website.name} @ {self.scheduled_at}"

    class Meta:
        verbose_name = "Scheduled Action"
        verbose_name_plural = "Scheduled Actions"
        ordering = ["scheduled_at"]


# ============================================================
# CLIENT NOTIFICATIONS
# ============================================================

class ClientNotification(models.Model):

    NOTIFICATION_TYPES = [
        ("payment_reminder", "Payment Reminder"),
        ("payment_received", "Payment Received"),
        ("suspension_warning", "Suspension Warning"),
        ("suspension", "Website Suspended"),
        ("restoration", "Website Restored"),
        ("maintenance", "Maintenance Notice"),
        ("update", "General Update"),
        ("invoice", "Invoice"),
        ("support", "Support Request"),
        ("general", "General Message"),
        ("custom", "Custom Message"),
    ]

    website = models.ForeignKey(
        ManagedWebsite,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default="custom"
    )

    subject = models.CharField(max_length=200)

    message = models.TextField()

    sent_at = models.DateTimeField(auto_now_add=True)

    sent_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} → {self.client.name} ({self.sent_at.date()})"

    class Meta:
        verbose_name = "Client Notification"
        verbose_name_plural = "Client Notifications"
        ordering = ["-sent_at"]

# ============================================================
# DOMAIN RENEWAL SYSTEM
# ============================================================

class DomainRecord(models.Model):

    STATUS_CHOICES = [
        ('active',          'Active'),
        ('expiring_soon',   'Expiring Soon'),
        ('expired',         'Expired'),
        ('pending_renewal', 'Pending Renewal'),
        ('transferred',     'Transferred Out'),
    ]

    REGISTRAR_CHOICES = [
        ('zicta',      'ZICTA (.co.tz / .tz)'),
        ('godaddy',    'GoDaddy'),
        ('cloudflare', 'Cloudflare'),
        ('namecheap',  'Namecheap'),
        ('other',      'Other'),
    ]

    website     = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE, related_name='domains')
    domain_name = models.CharField(max_length=253)
    registrar   = models.CharField(max_length=30, choices=REGISTRAR_CHOICES, default='other')
    registrar_other = models.CharField(max_length=100, blank=True)

    registration_date = models.DateField()
    expiry_date       = models.DateField()

    renewal_cost             = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    auto_renew               = models.BooleanField(default=True)
    send_renewal_warnings    = models.BooleanField(default=True)
    warning_days_before      = models.IntegerField(default=30)

    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    dns_nameservers = models.TextField(blank=True, help_text='One per line')
    notes           = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def days_until_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def __str__(self):
        return f'{self.domain_name} (expires {self.expiry_date})'

    class Meta:
        verbose_name = 'Domain Record'
        verbose_name_plural = 'Domain Records'
        ordering = ['expiry_date']


class DomainRenewalPayment(models.Model):
    domain          = models.ForeignKey(DomainRecord, on_delete=models.CASCADE, related_name='renewal_payments')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    paid_date       = models.DateField()
    renewed_until   = models.DateField()
    payment_method  = models.CharField(max_length=50, blank=True)
    transaction_ref = models.CharField(max_length=100, blank=True)
    notes           = models.TextField(blank=True)
    recorded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.domain.domain_name} renewed → {self.renewed_until}'

    class Meta:
        ordering = ['-paid_date']


# ============================================================
# EMAIL HOSTING SYSTEM
# ============================================================

class EmailHostingPlan(models.Model):

    STATUS_CHOICES = [
        ('active',    'Active'),
        ('suspended', 'Suspended'),
        ('expired',   'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    client   = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='email_plans')
    website  = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE,
                                 related_name='email_plans', null=True, blank=True)

    plan_name      = models.CharField(max_length=200)
    email_domain   = models.CharField(max_length=253, help_text='e.g. yourcompany.co.tz')
    accounts_count = models.PositiveIntegerField(default=1)
    storage_gb     = models.DecimalField(max_digits=6, decimal_places=1, default=5.0)

    monthly_cost   = models.DecimalField(max_digits=10, decimal_places=2)
    start_date     = models.DateField()
    end_date       = models.DateField()

    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    suspension_message = models.TextField(
        blank=True,
        default='Your email hosting has been suspended. Please contact JamiiTek.')

    auto_suspend_on_expiry = models.BooleanField(default=True)
    send_expiry_warnings   = models.BooleanField(default=True)
    warning_days_before    = models.IntegerField(default=7)

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def days_until_expiry(self):
        return (self.end_date - timezone.now().date()).days

    @property
    def is_overdue(self):
        return self.end_date < timezone.now().date()

    @property
    def total_paid(self):
        return sum(p.amount for p in self.email_payments.all())

    def __str__(self):
        return f'{self.plan_name} ({self.client.name})'

    class Meta:
        verbose_name = 'Email Hosting Plan'
        verbose_name_plural = 'Email Hosting Plans'
        ordering = ['-created_at']


class EmailHostingPayment(models.Model):
    plan            = models.ForeignKey(EmailHostingPlan, on_delete=models.CASCADE,
                                        related_name='email_payments')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date    = models.DateField()
    months_covered  = models.IntegerField(default=1)
    payment_method  = models.CharField(max_length=50, blank=True)
    transaction_ref = models.CharField(max_length=100, blank=True)
    notes           = models.TextField(blank=True)
    recorded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.plan.plan_name} – TZS {self.amount} ({self.payment_date})'

    class Meta:
        ordering = ['-payment_date']
