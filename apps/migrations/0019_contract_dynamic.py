# Contract: client optional + dynamic fields (sections, line_items, custom_fields)
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0018_contract'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contracts', to='apps.client'),
        ),
        migrations.AddField(model_name='contract', name='client_name', field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name='contract', name='client_email', field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name='contract', name='client_company', field=models.CharField(blank=True, max_length=160)),
        migrations.AddField(model_name='contract', name='client_phone', field=models.CharField(blank=True, max_length=40)),
        migrations.AddField(model_name='contract', name='client_address', field=models.CharField(blank=True, max_length=300)),
        migrations.AddField(model_name='contract', name='sections', field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name='contract', name='line_items', field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name='contract', name='custom_fields', field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name='contract', name='accent_color', field=models.CharField(default='#25d366', max_length=9)),
        migrations.AddField(model_name='contract', name='logo_url', field=models.URLField(blank=True)),
    ]
