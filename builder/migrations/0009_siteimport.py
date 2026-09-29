import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0008_sitepage_raw_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=32, unique=True)),
                ('result', models.JSONField(blank=True, default=dict)),
                ('uploaded', models.JSONField(blank=True, default=list)),
                ('images', models.JSONField(blank=True, default=list)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('website', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imports', to='builder.clientwebsite')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
