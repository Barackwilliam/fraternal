from django.db import models

class USSDConfig(models.Model):
    is_active = models.BooleanField(default=True)
    message_imezimwa = models.CharField(
        max_length=255,
        default="Huduma ya Shamba Mfukoni haipo kwa sasa. Jaribu baadaye."
    )

    class Meta:
        verbose_name = "USSD Configuration"

    def __str__(self):
        return "USSD Config"