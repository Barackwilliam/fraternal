# Proposal model — mapendekezo ya kitaalamu + e-accept
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0020_contract_signatures'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, editable=False, max_length=48, unique=True)),
                ('client_name', models.CharField(blank=True, max_length=160)),
                ('client_email', models.EmailField(blank=True, max_length=254)),
                ('client_company', models.CharField(blank=True, max_length=160)),
                ('client_phone', models.CharField(blank=True, max_length=40)),
                ('title', models.CharField(default='Project Proposal', max_length=200)),
                ('project_name', models.CharField(blank=True, max_length=200)),
                ('reference_number', models.CharField(blank=True, help_text='e.g. JT-2026-001 (auto if blank)', max_length=40)),
                ('valid_until', models.DateField(blank=True, help_text='Proposal expiry date', null=True)),
                ('summary_en', models.TextField(blank=True)),
                ('summary_sw', models.TextField(blank=True)),
                ('scope_en', models.TextField(blank=True)),
                ('scope_sw', models.TextField(blank=True)),
                ('about_en', models.TextField(blank=True)),
                ('about_sw', models.TextField(blank=True)),
                ('sections', models.JSONField(blank=True, default=list)),
                ('line_items', models.JSONField(blank=True, default=list)),
                ('currency', models.CharField(default='TZS', max_length=8)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('pricing_note', models.CharField(blank=True, help_text='e.g. Prices valid for 30 days. VAT exclusive.', max_length=300)),
                ('timeline_items', models.JSONField(blank=True, default=list)),
                ('payment_terms', models.CharField(blank=True, max_length=300)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('sent', 'Sent to client'), ('viewed', 'Viewed'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('expired', 'Expired')], default='draft', max_length=12)),
                ('accent_color', models.CharField(default='#00d4ff', max_length=9)),
                ('logo_url', models.URLField(blank=True)),
                ('provider_name', models.CharField(default='JamiiTek', max_length=120)),
                ('provider_rep', models.CharField(default='W. Chipindi', max_length=120)),
                ('accepted_name', models.CharField(blank=True, max_length=160)),
                ('accepted_email', models.EmailField(blank=True, max_length=254)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('accepted_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('decline_reason', models.CharField(blank=True, max_length=300)),
                ('viewed_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proposals', to='apps.client')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
