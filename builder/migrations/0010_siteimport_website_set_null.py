import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0009_siteimport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteimport',
            name='website',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='imports', to='builder.clientwebsite'),
        ),
    ]
