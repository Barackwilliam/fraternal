from django.db import migrations, models
import django.db.models.deletion
import secrets


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0008_alter_projectproposal_pdf_file_alter_service_image_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagedWebsite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Jina la Website')),
                ('url', models.URLField(verbose_name='URL ya Website')),
                ('site_type', models.CharField(choices=[('django', 'Django Website'), ('static', 'Static HTML/CSS'), ('wordpress', 'WordPress'), ('other', 'Nyingine')], default='django', max_length=20)),
                ('api_key', models.CharField(blank=True, max_length=64, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('maintenance', 'Maintenance'), ('terminated', 'Terminated')], default='active', max_length=20)),
                ('suspension_message', models.TextField(blank=True, default='Huduma imesimamishwa kwa muda. Tafadhali wasiliana na msimamizi.', verbose_name='Ujumbe wa Kusimamishwa')),
                ('suspension_reason', models.TextField(blank=True, verbose_name='Sababu ya Kusimamishwa (internal)')),
                ('hosting_start_date', models.DateField(verbose_name='Tarehe ya Kuanza Hosting')),
                ('hosting_end_date', models.DateField(verbose_name='Tarehe ya Kuisha Hosting')),
                ('monthly_cost', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Bei ya Kila Mwezi (TZS)')),
                ('auto_suspend_on_expiry', models.BooleanField(default=True, verbose_name='Simamisha Kiotomatiki Ikiisha')),
                ('send_expiry_warnings', models.BooleanField(default=True, verbose_name='Tuma Onyo Kabla ya Kuisha')),
                ('warning_days_before', models.IntegerField(default=7, verbose_name='Siku za Onyo Kabla ya Kuisha')),
                ('notes', models.TextField(blank=True, verbose_name='Maelezo ya Ndani')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_websites', to='apps.client')),
            ],
            options={'verbose_name': 'Website Inayosimamiwa', 'verbose_name_plural': 'Websites Zinazosimamia', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='HostingPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Kiasi (TZS)')),
                ('payment_date', models.DateField(verbose_name='Tarehe ya Malipo')),
                ('months_covered', models.IntegerField(default=1, verbose_name='Miezi Inayolipwa')),
                ('payment_method', models.CharField(blank=True, max_length=50, verbose_name='Njia ya Malipo')),
                ('transaction_ref', models.CharField(blank=True, max_length=100, verbose_name='Nambari ya Muamala')),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='apps.managedwebsite')),
                ('recorded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'verbose_name': 'Malipo ya Hosting', 'verbose_name_plural': 'Malipo ya Hosting', 'ordering': ['-payment_date']},
        ),
        migrations.CreateModel(
            name='WebsiteFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_key', models.CharField(max_length=100, verbose_name='Kitambulisho cha Huduma')),
                ('feature_name', models.CharField(max_length=200, verbose_name='Jina la Huduma')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Imewashwa')),
                ('disabled_reason', models.TextField(blank=True, verbose_name='Sababu ya Kuzima')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='apps.managedwebsite')),
            ],
            options={'verbose_name': 'Huduma ya Website', 'verbose_name_plural': 'Huduma za Website', 'unique_together': {('website', 'feature_key')}},
        ),
        migrations.CreateModel(
            name='ScheduledAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('suspend', '🔴 Simamisha Website'), ('restore', '🟢 Rudisha Website'), ('maintenance', '🟡 Weka Maintenance Mode'), ('send_email', '📧 Tuma Barua Pepe'), ('disable_feature', '🚫 Zima Huduma'), ('enable_feature', '✅ Washa Huduma')], max_length=30)),
                ('scheduled_at', models.DateTimeField(verbose_name='Wakati wa Kutekeleza')),
                ('action_data', models.JSONField(blank=True, default=dict, verbose_name='Data ya Kitendo')),
                ('status', models.CharField(choices=[('pending', 'Inasubiri'), ('completed', 'Imekamilika'), ('failed', 'Imeshindwa'), ('cancelled', 'Imesimamishwa')], default='pending', max_length=20)),
                ('executed_at', models.DateTimeField(blank=True, null=True)),
                ('result_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_actions', to='apps.managedwebsite')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'verbose_name': 'Kitendo Kilichopangwa', 'verbose_name_plural': 'Vitendo Vilivyopangwa', 'ordering': ['scheduled_at']},
        ),
        migrations.CreateModel(
            name='ClientNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('payment_reminder', '💰 Kumbusho la Malipo'), ('suspension_warning', '⚠️ Onyo la Kusimamishwa'), ('suspended', '🔴 Taarifa ya Kusimamishwa'), ('restored', '🟢 Taarifa ya Kurudishwa'), ('maintenance', '🔧 Taarifa ya Matengenezo'), ('update', '📢 Taarifa ya Kisasa'), ('invoice', '🧾 Ankara'), ('custom', '✉️ Ujumbe Maalum')], default='custom', max_length=30)),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='apps.client')),
                ('website', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='apps.managedwebsite')),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={'verbose_name': 'Taarifa kwa Mteja', 'verbose_name_plural': 'Taarifa kwa Wateja', 'ordering': ['-sent_at']},
        ),
    ]
