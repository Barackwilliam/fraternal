# apps/receipt_models.py
"""
Development receipts — proof of payment for building a client's website.

Different from Invoice: an Invoice asks for money at the client level, a
Receipt confirms money already received for one specific ManagedWebsite.
A client can have several websites, so each website carries its own receipts.

Add to apps/models.py (bottom):

    from .receipt_models import DevelopmentReceipt   # noqa: F401
"""

import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class DevelopmentReceipt(models.Model):

    METHODS = [
        ('mpesa',     'M-Pesa'),
        ('tigopesa',  'Tigo Pesa'),
        ('airtel',    'Airtel Money'),
        ('halopesa',  'HaloPesa'),
        ('bank',      'Bank Transfer'),
        ('cash',      'Cash'),
        ('other',     'Other'),
    ]

    KINDS = [
        ('full',     'Full payment'),
        ('deposit',  'Deposit / Advance'),
        ('balance',  'Balance / Final'),
        ('partial',  'Part payment'),
    ]

    website = models.ForeignKey(
        'ManagedWebsite', on_delete=models.CASCADE, related_name='receipts')

    receipt_number = models.CharField(
        max_length=40, blank=True, help_text='Auto: RCP-YYYY-NNNN if left blank')
    token = models.CharField(max_length=48, unique=True, editable=False, db_index=True)

    kind = models.CharField(max_length=10, choices=KINDS, default='full')
    title = models.CharField(max_length=200, default='Website Development Payment')
    description = models.TextField(
        blank=True, help_text='Short summary of what was built')

    # [{"desc": "...", "qty": 1, "unit_price": 150000, "amount": 150000}]
    line_items = models.JSONField(default=list, blank=True)

    currency = models.CharField(max_length=8, default='TZS')
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='e.g. 18 for 18% VAT. Leave blank for none.')
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)

    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text='How much the client actually paid on this receipt')

    payment_method = models.CharField(max_length=12, choices=METHODS, default='mpesa')
    payment_reference = models.CharField(
        max_length=120, blank=True, help_text='M-Pesa / bank transaction reference')
    payment_date = models.DateField(default=timezone.now)

    received_by = models.CharField(max_length=120, default='W. Chipindi')
    notes = models.TextField(blank=True)

    is_published = models.BooleanField(
        default=True, help_text='Untick to hide this receipt from the client portal')

    # ── Electronic signature (filled by the client at download time) ──
    require_signature = models.BooleanField(
        default=True,
        help_text='Ask the client to sign before the PDF downloads')
    signature_data = models.TextField(
        blank=True, help_text='Base64 PNG of the drawn signature')
    signature_name = models.CharField(max_length=160, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_ip = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'Development Receipt'

    def __str__(self):
        return f'{self.receipt_number or "Receipt"} — {self.website.name}'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(24)

        # Safety net: if payment_date ever arrives as a raw string (e.g. from
        # a form field, admin import, or API call), convert it before we
        # touch .year below.
        if isinstance(self.payment_date, str):
            from datetime import datetime as _dt
            try:
                self.payment_date = _dt.strptime(self.payment_date, '%Y-%m-%d').date()
            except ValueError:
                self.payment_date = timezone.now().date()

        super().save(*args, **kwargs)
        if not self.receipt_number and self.pk:
            year = (self.payment_date or timezone.now().date()).year
            number = f'RCP-{year}-{self.pk:04d}'
            DevelopmentReceipt.objects.filter(pk=self.pk).update(receipt_number=number)
            self.receipt_number = number

    # ── client shortcuts ──────────────────────────────────────
    @property
    def client(self):
        return self.website.client

    @property
    def client_name(self):
        return getattr(self.client, 'name', '') or ''

    @property
    def client_company(self):
        return getattr(self.client, 'company', '') or ''

    @property
    def client_email(self):
        return getattr(self.client, 'email', '') or ''

    @property
    def client_phone(self):
        return getattr(self.client, 'phone', '') or ''

    # ── money ─────────────────────────────────────────────────
    @property
    def subtotal(self):
        total = 0
        for item in self.line_items or []:
            try:
                total += float(item.get('amount') or 0)
            except (TypeError, ValueError):
                continue
        return total

    @property
    def discounted_subtotal(self):
        total = self.subtotal - float(self.discount_amount or 0)
        return max(0, total)

    @property
    def tax_amount(self):
        if not self.tax_percent:
            return 0
        return self.discounted_subtotal * float(self.tax_percent) / 100

    @property
    def grand_total(self):
        return self.discounted_subtotal + self.tax_amount

    @property
    def balance_due(self):
        return max(0, self.grand_total - float(self.amount_paid or 0))

    @property
    def is_fully_paid(self):
        return self.grand_total > 0 and self.balance_due <= 0

    @property
    def status_label(self):
        if self.is_fully_paid:
            return 'PAID IN FULL'
        if float(self.amount_paid or 0) > 0:
            return 'PART PAYMENT'
        return 'UNPAID'

    # ── signature / verification ──────────────────────────────
    @property
    def is_signed(self):
        return bool(self.signed_at and (self.signature_data or self.signature_name))

    @property
    def needs_signature(self):
        return self.require_signature and not self.is_signed

    @property
    def public_url(self):
        return f'/receipt/{self.token}/'

    @property
    def verify_path(self):
        return f'/receipt/verify/{self.token}/'

    @property
    def verify_url(self):
        base = getattr(settings, 'SITE_URL', 'https://jamiitek.com').rstrip('/')
        return f'{base}{self.verify_path}'

    @property
    def barcode_value(self):
        """Code 128-B only handles ASCII 32..126, so keep it plain."""
        return (self.receipt_number or f'RCP{self.pk or 0}')[:32]

    @property
    def filename(self):
        safe = ''.join(c for c in self.website.name if c.isalnum() or c in ' -_').strip()
        safe = safe.replace(' ', '-') or 'website'
        return f'{self.receipt_number or "receipt"}-{safe}.pdf'