from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('apps', '0004_team'),
    ]
    operations = [
        migrations.AddField(
            model_name='team',
            name='linkedin_link',
            field=models.URLField(max_length=300, blank=True, null=True),
        ),
    ]