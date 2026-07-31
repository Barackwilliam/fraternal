# Contract: provider signature + editable signature block
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0019_contract_dynamic'),
    ]

    operations = [
        migrations.AddField(model_name='contract', name='provider_signature',
            field=models.CharField(blank=True, default='W. Chipindi', max_length=120)),
        migrations.AddField(model_name='contract', name='provider_signed_date',
            field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name='contract', name='signature_block_en',
            field=models.TextField(blank=True)),
        migrations.AddField(model_name='contract', name='signature_block_sw',
            field=models.TextField(blank=True)),
        migrations.AlterField(model_name='contract', name='provider_rep',
            field=models.CharField(default='W. Chipindi', max_length=120)),
    ]
