# Punguzo kwa malipo ya muda mrefu (3/6/12 miezi)
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0022_companyprofile_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='managedwebsite', name='discount_3m',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=5,
                help_text='Percent off when paying for 3 months at once',
                verbose_name='3-month discount (%)')),
        migrations.AddField(
            model_name='managedwebsite', name='discount_6m',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=5,
                help_text='Percent off when paying for 6 months at once',
                verbose_name='6-month discount (%)')),
        migrations.AddField(
            model_name='managedwebsite', name='discount_12m',
            field=models.DecimalField(decimal_places=2, default=20, max_digits=5,
                help_text='Percent off when paying for 12 months at once',
                verbose_name='12-month discount (%)')),
    ]
