"""
Uthibitisho wa hatua mbili (2FA) kwa akaunti za staff — angalia apps/two_factor.py.
"""
from django.conf import settings
from django.db import models


class StaffTwoFactor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='two_factor')
    # Siri ya TOTP, imesimbwa (Fernet) — haisomeki hata database ikivuja
    secret_encrypted = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    # Hatua ya mwisho ya muda iliyotumika: code ile ile haiwezi kutumika mara mbili
    last_step = models.BigIntegerField(default=0)
    # sha256 za recovery codes ambazo bado hazijatumika
    recovery_hashes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Staff 2FA'
        verbose_name_plural = 'Staff 2FA'

    def __str__(self):
        return f'2FA · {self.user} · {"on" if self.confirmed else "setup"}'
