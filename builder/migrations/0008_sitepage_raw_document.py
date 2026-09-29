from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0007_custom_domain_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitepage',
            name='raw_document',
            field=models.TextField(blank=True),
        ),
    ]
