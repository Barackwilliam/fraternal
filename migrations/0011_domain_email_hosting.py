from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_alter_clientnotification_notification_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Domain Record ──────────────────────────────────────────
        migrations.CreateModel(
            name='DomainRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain_name', models.CharField(max_length=253)),
                ('registrar', models.CharField(choices=[('zicta', 'ZICTA (.co.tz / .tz)'), ('godaddy', 'GoDaddy'), ('cloudflare', 'Cloudflare'), ('namecheap', 'Namecheap'), ('other', 'Other')], default='other', max_length=30)),
                ('registrar_other', models.CharField(blank=True, max_length=100)),
                ('registration_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('renewal_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('auto_renew', models.BooleanField(default=True)),
                ('send_renewal_warnings', models.BooleanField(default=True)),
                ('warning_days_before', models.IntegerField(default=30)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expiring_soon', 'Expiring Soon'), ('expired', 'Expired'), ('pending_renewal', 'Pending Renewal'), ('transferred', 'Transferred Out')], default='active', max_length=20)),
                ('dns_nameservers', models.TextField(blank=True, help_text='One per line')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='apps.managedwebsite')),
            ],
            options={'verbose_name': 'Domain Record', 'verbose_name_plural': 'Domain Records', 'ordering': ['expiry_date']},
        ),
        # ── Domain Renewal Payment ─────────────────────────────────
        migrations.CreateModel(
            name='DomainRenewalPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid_date', models.DateField()),
                ('renewed_until', models.DateField()),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('transaction_ref', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='renewal_payments', to='apps.domainrecord')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-paid_date']},
        ),
        # ── Email Hosting Plan ─────────────────────────────────────
        migrations.CreateModel(
            name='EmailHostingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_name', models.CharField(max_length=200)),
                ('email_domain', models.CharField(help_text='e.g. yourcompany.co.tz', max_length=253)),
                ('accounts_count', models.PositiveIntegerField(default=1)),
                ('storage_gb', models.DecimalField(decimal_places=1, default=5.0, max_digits=6)),
                ('monthly_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('suspension_message', models.TextField(blank=True, default='Your email hosting has been suspended. Please contact JamiiTek.')),
                ('auto_suspend_on_expiry', models.BooleanField(default=True)),
                ('send_expiry_warnings', models.BooleanField(default=True)),
                ('warning_days_before', models.IntegerField(default=7)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_plans', to='apps.client')),
                ('website', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_plans', to='apps.managedwebsite')),
            ],
            options={'verbose_name': 'Email Hosting Plan', 'verbose_name_plural': 'Email Hosting Plans', 'ordering': ['-created_at']},
        ),
        # ── Email Hosting Payment ──────────────────────────────────
        migrations.CreateModel(
            name='EmailHostingPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateField()),
                ('months_covered', models.IntegerField(default=1)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('transaction_ref', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_payments', to='apps.emailhostingplan')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-payment_date']},
        ),
    ]
