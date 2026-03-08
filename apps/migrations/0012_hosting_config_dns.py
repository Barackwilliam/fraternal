from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0011_domain_email_hosting'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostingConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_type', models.CharField(choices=[('shared','Shared Hosting'),('vps','VPS Server'),('dedicated','Dedicated Server'),('cloud','Cloud Hosting')], default='shared', max_length=20)),
                ('server_os', models.CharField(choices=[('ubuntu_22','Ubuntu 22.04 LTS'),('ubuntu_20','Ubuntu 20.04 LTS'),('debian_12','Debian 12'),('centos_8','CentOS Stream 8')], default='ubuntu_22', max_length=20)),
                ('stack', models.CharField(choices=[('django','Python / Django'),('php_apache','PHP / Apache'),('php_nginx','PHP / Nginx'),('node','Node.js'),('static','Static / Nginx')], default='django', max_length=20)),
                ('server_location', models.CharField(default='Dar es Salaam, Tanzania', max_length=100)),
                ('ip_address', models.GenericIPAddressField(default='197.250.10.1')),
                ('server_hostname', models.CharField(default='srv1.jamiitek.co.tz', max_length=200)),
                ('disk_total_gb', models.DecimalField(decimal_places=1, default=10.0, max_digits=6)),
                ('disk_used_gb', models.DecimalField(decimal_places=1, default=1.2, max_digits=6)),
                ('bandwidth_gb', models.DecimalField(decimal_places=1, default=100.0, max_digits=8)),
                ('bandwidth_used', models.DecimalField(decimal_places=1, default=4.5, max_digits=8)),
                ('ram_mb', models.IntegerField(default=512)),
                ('cpu_cores', models.IntegerField(default=1)),
                ('monthly_visits', models.IntegerField(default=0)),
                ('python_version', models.CharField(blank=True, default='3.11.6', max_length=20)),
                ('php_version', models.CharField(blank=True, max_length=20)),
                ('django_version', models.CharField(blank=True, default='5.1', max_length=20)),
                ('db_engine', models.CharField(default='PostgreSQL 15', max_length=50)),
                ('web_server', models.CharField(default='Nginx 1.24', max_length=50)),
                ('ftp_host', models.CharField(default='ftp.jamiitek.co.tz', max_length=200)),
                ('ftp_username', models.CharField(blank=True, max_length=100)),
                ('ftp_port', models.IntegerField(default=22)),
                ('db_host', models.CharField(default='db.jamiitek.co.tz', max_length=200)),
                ('db_name', models.CharField(blank=True, max_length=100)),
                ('db_username', models.CharField(blank=True, max_length=100)),
                ('db_port', models.IntegerField(default=5432)),
                ('ssl_type', models.CharField(choices=[('lets_encrypt',"Let's Encrypt (Free)"),('comodo','Comodo SSL'),('wildcard','Wildcard SSL'),('none','No SSL')], default='lets_encrypt', max_length=20)),
                ('ssl_issued_date', models.DateField(blank=True, null=True)),
                ('ssl_expiry_date', models.DateField(blank=True, null=True)),
                ('ssl_issuer', models.CharField(default="Let's Encrypt Authority X3", max_length=100)),
                ('https_redirect', models.BooleanField(default=True)),
                ('auto_backup', models.BooleanField(default=True)),
                ('backup_frequency', models.CharField(default='Daily', max_length=20)),
                ('last_backup', models.DateField(blank=True, null=True)),
                ('cdn_enabled', models.BooleanField(default=False)),
                ('firewall_enabled', models.BooleanField(default=True)),
                ('ddos_protection', models.BooleanField(default=True)),
                ('uptime_percent', models.DecimalField(decimal_places=2, default=99.97, max_digits=5)),
                ('last_downtime', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('website', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hosting_config', to='apps.managedwebsite')),
            ],
            options={'verbose_name': 'Hosting Configuration', 'verbose_name_plural': 'Hosting Configurations'},
        ),
        migrations.CreateModel(
            name='DomainDNSRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_type', models.CharField(choices=[('A','A — IPv4 Address'),('AAAA','AAAA — IPv6 Address'),('CNAME','CNAME — Canonical Name'),('MX','MX — Mail Exchange'),('TXT','TXT — Text Record'),('NS','NS — Name Server'),('SRV','SRV — Service Record'),('CAA','CAA — Certification Authority')], max_length=10)),
                ('name', models.CharField(help_text='e.g. @ or www or mail', max_length=253)),
                ('value', models.TextField(help_text='e.g. 197.250.10.1 or target domain')),
                ('ttl', models.IntegerField(default=3600, help_text='Time to live in seconds')),
                ('priority', models.IntegerField(default=0, help_text='Used for MX and SRV records')),
                ('status', models.CharField(choices=[('active','Active'),('propagating','Propagating'),('inactive','Inactive')], default='active', max_length=15)),
                ('proxy', models.BooleanField(default=False, help_text='CDN/Proxy enabled (like Cloudflare)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dns_records', to='apps.domainrecord')),
            ],
            options={'verbose_name': 'DNS Record', 'verbose_name_plural': 'DNS Records', 'ordering': ['record_type', 'name']},
        ),
    ]
