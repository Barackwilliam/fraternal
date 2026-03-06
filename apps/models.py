# app/models.py
from django.db import models


# Create your models here.

class Service(models.Model):
    Service_type = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Service_type

    # Kwa Open Graph preview (Facebook, WhatsApp etc.)
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ''

    # Kwa matumizi ya kawaida kwenye site (speed optimized)
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ''



class Question(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()

    
    def __str__(self):
        return self.question

class Team(models.Model):
    full_name = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)  # Hifadhi Uploadcare UUID au URL
    position = models.CharField(max_length=255)
    facebook_link = models.URLField(max_length=300, blank=True, null=True)
    twitter_link = models.URLField(max_length=300, blank=True, null=True)
    instagram_link = models.URLField(max_length=300, blank=True, null=True)
    linkedIn = models.URLField(max_length=300, blank=True, null=True)
    
    def __str__(self):
        return self.full_name

    # Kwa Open Graph preview (Facebook, WhatsApp etc.)
    def get_og_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/resize/1200x630/-/format/auto/"
        return ''

    # Kwa matumizi ya kawaida kwenye site (speed optimized)
    def get_image_url(self):
        if self.image:
            return f"https://ucarecdn.com/{self.image}/-/format/jpg/-/quality/smart/"
        return ''


    
class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()

    def __str__(self):
        return self.full_name



from django.contrib.auth.models import User

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
import secrets
from django.utils import timezone

class ManagedWebsite(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('maintenance', 'Maintenance'),
        ('terminated', 'Terminated'),
    ]
    SITE_TYPE_CHOICES = [
        ('django', 'Django Website'),
        ('static', 'Static HTML/CSS'),
        ('wordpress', 'WordPress'),
        ('other', 'Nyingine'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='managed_websites')
    name = models.CharField(max_length=200, verbose_name="Jina la Website")
    url = models.URLField(verbose_name="URL ya Website")
    site_type = models.CharField(max_length=20, choices=SITE_TYPE_CHOICES, default='django')
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    suspension_message = models.TextField(
        blank=True,
        default="Huduma imesimamishwa kwa muda. Tafadhali wasiliana na msimamizi.",
        verbose_name="Ujumbe wa Kusimamishwa"
    )
    suspension_reason = models.TextField(blank=True, verbose_name="Sababu ya Kusimamishwa (internal)")
    
    # Hosting billing
    hosting_start_date = models.DateField(verbose_name="Tarehe ya Kuanza Hosting")
    hosting_end_date = models.DateField(verbose_name="Tarehe ya Kuisha Hosting")
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bei ya Kila Mwezi (TZS)")
    
    # Notification settings
    auto_suspend_on_expiry = models.BooleanField(default=True, verbose_name="Simamisha Kiotomatiki Ikiisha")
    send_expiry_warnings = models.BooleanField(default=True, verbose_name="Tuma Onyo Kabla ya Kuisha")
    warning_days_before = models.IntegerField(default=7, verbose_name="Siku za Onyo Kabla ya Kuisha")
    
    notes = models.TextField(blank=True, verbose_name="Maelezo ya Ndani")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_urlsafe(48)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def days_until_expiry(self):
        from datetime import date
        delta = self.hosting_end_date - date.today()
        return delta.days

    @property
    def is_overdue(self):
        from datetime import date
        return self.hosting_end_date < date.today()

    @property  
    def total_paid(self):
        return sum(p.amount for p in self.payments.all())

    def __str__(self):
        return f"{self.name} ({self.client.name})"

    class Meta:
        verbose_name = "Website Inayosimamiwa"
        verbose_name_plural = "Websites Zinazosimamia"
        ordering = ['-created_at']


class HostingPayment(models.Model):
    website = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kiasi (TZS)")
    payment_date = models.DateField(verbose_name="Tarehe ya Malipo")
    months_covered = models.IntegerField(default=1, verbose_name="Miezi Inayolipwa")
    payment_method = models.CharField(max_length=50, blank=True, verbose_name="Njia ya Malipo")
    transaction_ref = models.CharField(max_length=100, blank=True, verbose_name="Nambari ya Muamala")
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.website.name} - TZS {self.amount} ({self.payment_date})"

    class Meta:
        verbose_name = "Malipo ya Hosting"
        verbose_name_plural = "Malipo ya Hosting"
        ordering = ['-payment_date']


class WebsiteFeature(models.Model):
    website = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE, related_name='features')
    feature_key = models.CharField(max_length=100, verbose_name="Kitambulisho cha Huduma")
    feature_name = models.CharField(max_length=200, verbose_name="Jina la Huduma")
    is_enabled = models.BooleanField(default=True, verbose_name="Imewashwa")
    disabled_reason = models.TextField(blank=True, verbose_name="Sababu ya Kuzima")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "✅" if self.is_enabled else "❌"
        return f"{status} {self.website.name} → {self.feature_name}"

    class Meta:
        unique_together = ['website', 'feature_key']
        verbose_name = "Huduma ya Website"
        verbose_name_plural = "Huduma za Website"


class ScheduledAction(models.Model):
    ACTION_TYPES = [
        ('suspend', '🔴 Simamisha Website'),
        ('restore', '🟢 Rudisha Website'),
        ('maintenance', '🟡 Weka Maintenance Mode'),
        ('send_email', '📧 Tuma Barua Pepe'),
        ('disable_feature', '🚫 Zima Huduma'),
        ('enable_feature', '✅ Washa Huduma'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Inasubiri'),
        ('completed', 'Imekamilika'),
        ('failed', 'Imeshindwa'),
        ('cancelled', 'Imesimamishwa'),
    ]

    website = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE, related_name='scheduled_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    scheduled_at = models.DateTimeField(verbose_name="Wakati wa Kutekeleza")
    action_data = models.JSONField(default=dict, blank=True, verbose_name="Data ya Kitendo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    executed_at = models.DateTimeField(null=True, blank=True)
    result_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} → {self.website.name} @ {self.scheduled_at.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Kitendo Kilichopangwa"
        verbose_name_plural = "Vitendo Vilivyopangwa"
        ordering = ['scheduled_at']


class ClientNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('payment_reminder', '💰 Kumbusho la Malipo'),
        ('suspension_warning', '⚠️ Onyo la Kusimamishwa'),
        ('suspended', '🔴 Taarifa ya Kusimamishwa'),
        ('restored', '🟢 Taarifa ya Kurudishwa'),
        ('maintenance', '🔧 Taarifa ya Matengenezo'),
        ('update', '📢 Taarifa ya Kisasa'),
        ('invoice', '🧾 Ankara'),
        ('custom', '✉️ Ujumbe Maalum'),
    ]

    website = models.ForeignKey(ManagedWebsite, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='custom')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} → {self.client.name} ({self.sent_at.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = "Taarifa kwa Mteja"
        verbose_name_plural = "Taarifa kwa Wateja"
        ordering = ['-sent_at']
