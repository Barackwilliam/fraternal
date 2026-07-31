"""
JamiiTek ChatBot SaaS — Complete Models
All database tables for the chatbot platform.
"""
import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator


# ─────────────────────────────────────────────
# SUBSCRIPTION PLANS
# ─────────────────────────────────────────────
class SubscriptionPlan(models.Model):
    name         = models.CharField(max_length=60)
    slug         = models.SlugField(unique=True)
    price_tzs    = models.PositiveIntegerField(help_text="Monthly price in TZS")
    msg_limit    = models.PositiveIntegerField(help_text="Messages per month (0=unlimited)")
    max_services = models.PositiveIntegerField(default=10, help_text="Max services/FAQs")
    features     = models.JSONField(default=list, help_text="List of feature strings")
    is_active    = models.BooleanField(default=True)
    sort_order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.name} — TZS {self.price_tzs:,}/mo"

    @property
    def is_unlimited(self):
        return self.msg_limit == 0


# ─────────────────────────────────────────────
# CHATBOT CLIENT (Business that owns a bot)
# ─────────────────────────────────────────────
class ChatbotClient(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chatbot_profile')
    full_name        = models.CharField(max_length=150)
    business_name    = models.CharField(max_length=200)
    email            = models.EmailField()
    phone            = models.CharField(max_length=20)
    country          = models.CharField(max_length=60, default='Tanzania')
    city             = models.CharField(max_length=60, default='Dar es Salaam')
    api_key          = models.CharField(max_length=64, unique=True, editable=False)
    is_verified      = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    notes            = models.TextField(blank=True)

    class Meta:
        verbose_name = "Chatbot Client"

    def __str__(self):
        return f"{self.business_name} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    @property
    def active_bot(self):
        return self.bots.filter(is_active=True).first()

    @property
    def total_messages(self):
        return Message.objects.filter(conversation__bot__client=self).count()


# ─────────────────────────────────────────────
# BOT CONFIGURATION (The actual bot)
# ─────────────────────────────────────────────
class BotConfig(models.Model):
    LANGUAGE_CHOICES = [
        ('sw', 'Swahili'),
        ('en', 'English'),
        ('sw+en', 'Swahili + English (auto-detect)'),
    ]
    TONE_CHOICES = [
        ('professional', 'Professional & Formal'),
        ('friendly',     'Friendly & Warm'),
        ('casual',       'Casual & Fun'),
        ('formal',       'Very Formal'),
    ]
    STATUS_CHOICES = [
        ('draft',     'Draft — Not deployed'),
        ('pending',   'Pending — Awaiting Phone ID setup'),
        ('active',    'Active — Running'),
        ('suspended', 'Suspended — Paused'),
        ('cancelled', 'Cancelled'),
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client         = models.ForeignKey(ChatbotClient, on_delete=models.CASCADE, related_name='bots')
    bot_name       = models.CharField(max_length=100, help_text="e.g. Amara, Juma, Helper")
    business_name  = models.CharField(max_length=200)
    description    = models.TextField(help_text="What does this bot do? Describe its main purpose.")
    language       = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='sw+en')
    tone           = models.CharField(max_length=20, choices=TONE_CHOICES, default='friendly')
    greeting_msg   = models.TextField(help_text="First message when user says hi")
    fallback_msg   = models.TextField(default="Samahani, sijaelewea vizuri. Tafadhali uliza tena au piga simu +255XXX.")
    human_handoff_msg = models.TextField(
        default="Nitakupeleka kwa mtu wa kweli sasa hivi. Subiri kidogo...",
        help_text="Message when bot cannot handle and transfers to human"
    )
    whatsapp_number    = models.CharField(max_length=20, help_text="e.g. +255750123456", blank=True)
    whatsapp_phone_id  = models.CharField(max_length=50, blank=True, help_text="Meta Phone Number ID")
    whatsapp_token     = models.CharField(max_length=500, blank=True, help_text="WhatsApp Cloud API token")
    webhook_verify_token = models.CharField(max_length=100, blank=True, editable=False)
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active          = models.BooleanField(default=False)
    deployed_at        = models.DateTimeField(null=True, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    # AI Settings
    ai_model           = models.CharField(max_length=60, default='claude-sonnet-4-5')
    ai_temperature     = models.FloatField(default=0.7, help_text="0=strict, 1=creative")
    max_context_msgs   = models.PositiveSmallIntegerField(default=10, help_text="Messages to remember in conversation")
    collect_name       = models.BooleanField(default=True, help_text="Ask for customer name at start")
    collect_phone      = models.BooleanField(default=False, help_text="Ask for customer phone")

    # Admin controls
    admin_suspended_reason = models.TextField(blank=True)
    admin_notes            = models.TextField(blank=True)

    class Meta:
        verbose_name = "Bot Configuration"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bot_name} — {self.business_name} [{self.status}]"

    def save(self, *args, **kwargs):
        if not self.webhook_verify_token:
            self.webhook_verify_token = secrets.token_hex(16)
        super().save(*args, **kwargs)

    def build_system_prompt(self):
        """Build the AI system prompt from bot configuration."""
        services_text = ""
        for svc in self.services.filter(is_active=True):
            services_text += f"\n- {svc.name}: {svc.description}"
            if svc.price:
                services_text += f" (Bei: {svc.price})"

        faqs_text = ""
        for faq in self.faqs.filter(is_active=True):
            faqs_text += f"\nQ: {faq.question}\nA: {faq.answer}\n"

        lang_instruction = {
            'sw':    "Jibu KILA WAKATI kwa Kiswahili tu.",
            'en':    "Always respond in English only.",
            'sw+en': "Detect the language the customer writes in and respond in the same language (Swahili or English)."
        }.get(self.language, "")

        tone_instruction = {
            'professional': "Kuwa wa kitaalamu na rasmi. Tumia maneno ya heshima.",
            'friendly':     "Kuwa rafiki, wa karibu, na mwenye huruma. Tumia emoji kidogo.",
            'casual':       "Kuwa burudani, wa kirafiki, kama rafiki anayesaidia.",
            'formal':       "Kuwa rasmi sana. Tumia lugha ya biashara ya hali ya juu.",
        }.get(self.tone, "")

        prompt = f"""Wewe ni {self.bot_name}, msaidizi wa AI wa {self.business_name}.

MAELEZO YAKO:
{self.description}

LUGHA: {lang_instruction}
MTINDO: {tone_instruction}

HUDUMA TUNAZOTOA:
{services_text if services_text else "Jibu maswali ya jumla kuhusu biashara."}

MASWALI YA MARA KWA MARA (FAQ):
{faqs_text if faqs_text else "Hakuna FAQ zilizowekwa — tumia akili yako na maelezo ya biashara."}

MWONGOZO MUHIMU:
1. Jibu kwa ufupi na wazi — si zaidi ya aya 2-3.
2. Kama hujui jibu, sema ukweli na elekeza kwenye timu ya binadamu.
3. USITOE bei au habari ambazo hazijakuwa kwenye mfumo huu.
4. Kama mteja anataka binadamu, jibu: "{self.human_handoff_msg}"
5. Daima kuwa mwenye heshima na subira.
6. Kama swali halihusiani na biashara hii, eleza kwa upole kwamba unaweza tu kusaidia mambo ya {self.business_name}.

UJUMBE WA KUANZA: {self.greeting_msg}
UJUMBE WA KUSHINDWA: {self.fallback_msg}"""
        return prompt

    @property
    def webhook_url(self):
        from django.conf import settings
        base = getattr(settings, 'SITE_URL', 'https://jamiitek.com')
        return f"{base}/chatbot/webhook/{self.id}/"


# ─────────────────────────────────────────────
# BOT SERVICES (What the business offers)
# ─────────────────────────────────────────────
class BotService(models.Model):
    bot         = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='services')
    name        = models.CharField(max_length=150, help_text="e.g. Website Design")
    description = models.TextField(help_text="Describe this service in detail")
    price       = models.CharField(max_length=100, blank=True, help_text="e.g. TZS 500,000 or Free")
    keywords    = models.CharField(max_length=300, blank=True, help_text="Comma-separated trigger words")
    is_active   = models.BooleanField(default=True)
    sort_order  = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.bot.bot_name})"


# ─────────────────────────────────────────────
# BOT FAQs
# ─────────────────────────────────────────────
class BotFAQ(models.Model):
    bot       = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='faqs')
    question  = models.TextField()
    answer    = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"FAQ: {self.question[:60]}..."


# ─────────────────────────────────────────────
# SUBSCRIPTION
# ─────────────────────────────────────────────
class BotSubscription(models.Model):
    STATUS_CHOICES = [
        ('trial',     'Free Trial'),
        ('active',    'Active'),
        ('overdue',   'Overdue'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    bot          = models.OneToOneField(BotConfig, on_delete=models.CASCADE, related_name='subscription')
    plan         = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    start_date   = models.DateField(auto_now_add=True)
    end_date     = models.DateField(null=True, blank=True)
    trial_ends   = models.DateField(null=True, blank=True)
    messages_used = models.PositiveIntegerField(default=0)
    auto_renew   = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bot.bot_name} — {self.plan.name} [{self.status}]"

    @property
    def is_active(self):
        return self.status in ('trial', 'active')

    @property
    def days_remaining(self):
        if not self.end_date:
            return None
        delta = (self.end_date - timezone.now().date()).days
        return max(delta, 0)

    @property
    def messages_remaining(self):
        if self.plan.is_unlimited:
            return 999999
        return max(self.plan.msg_limit - self.messages_used, 0)

    @property
    def usage_percent(self):
        if self.plan.is_unlimited:
            return 0
        if self.plan.msg_limit == 0:
            return 0
        return min(int((self.messages_used / self.plan.msg_limit) * 100), 100)


# ─────────────────────────────────────────────
# SUBSCRIPTION PAYMENTS
# ─────────────────────────────────────────────
class SubscriptionPayment(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    subscription    = models.ForeignKey(BotSubscription, on_delete=models.CASCADE, related_name='payments')
    amount          = models.PositiveIntegerField(help_text="TZS")
    months_covered  = models.PositiveSmallIntegerField(default=1)
    payment_method  = models.CharField(max_length=60, default='NMB Bank Transfer')
    transaction_ref = models.CharField(max_length=100)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date    = models.DateField(auto_now_add=True)
    verified_at     = models.DateTimeField(null=True, blank=True)
    verified_by     = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_bot_payments')
    notes           = models.TextField(blank=True)

    def __str__(self):
        return f"TZS {self.amount:,} — {self.subscription.bot.bot_name} [{self.status}]"


# ─────────────────────────────────────────────
# CONVERSATIONS
# ─────────────────────────────────────────────
class Conversation(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot             = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='conversations')
    customer_phone  = models.CharField(max_length=20, db_index=True)
    customer_name   = models.CharField(max_length=150, blank=True)
    wa_contact_name = models.CharField(max_length=150, blank=True, help_text="Name from WhatsApp profile")
    is_active       = models.BooleanField(default=True)
    started_at      = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    message_count   = models.PositiveIntegerField(default=0)
    is_human_handoff = models.BooleanField(default=False, help_text="Transferred to human agent")
    metadata        = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-last_message_at']
        unique_together = [('bot', 'customer_phone')]

    def __str__(self):
        return f"{self.customer_phone} ↔ {self.bot.bot_name}"

    def get_recent_messages(self, limit=10):
        return self.messages.order_by('-created_at')[:limit][::-1]


# ─────────────────────────────────────────────
# MESSAGES
# ─────────────────────────────────────────────
class Message(models.Model):
    ROLE_CHOICES = [
        ('user',      'Customer'),
        ('assistant', 'Bot'),
        ('system',    'System'),
    ]

    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation   = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role           = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content        = models.TextField()
    wa_message_id  = models.CharField(max_length=100, blank=True, db_index=True)
    tokens_used    = models.PositiveIntegerField(default=0)
    ai_model       = models.CharField(max_length=60, blank=True)
    latency_ms     = models.PositiveIntegerField(default=0, help_text="AI response time in ms")
    is_delivered   = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}..."


# ─────────────────────────────────────────────
# ANALYTICS (Daily aggregation)
# ─────────────────────────────────────────────
class BotAnalytics(models.Model):
    bot              = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='analytics')
    date             = models.DateField()
    messages_in      = models.PositiveIntegerField(default=0)
    messages_out     = models.PositiveIntegerField(default=0)
    new_conversations = models.PositiveIntegerField(default=0)
    unique_users     = models.PositiveIntegerField(default=0)
    avg_latency_ms   = models.PositiveIntegerField(default=0)
    tokens_used      = models.PositiveIntegerField(default=0)
    handoffs         = models.PositiveIntegerField(default=0)
    errors           = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('bot', 'date')]
        ordering = ['-date']

    def __str__(self):
        return f"{self.bot.bot_name} — {self.date}"