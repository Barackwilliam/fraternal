from django.db import migrations, models


class Migration(migrations.Migration):
    """
    footer_preset mpya + default za site MPYA (sidebar, footer ya safu nne).

    AddField inatumia default '' kwanza ili site ZILIZOPO zibaki na muonekano
    wao wa sasa; AlterField inabadilisha default kwa site zitakazoundwa baadaye.
    """

    dependencies = [
        ('builder', '0010_siteimport_website_set_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientwebsite',
            name='footer_preset',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='clientwebsite',
            name='footer_preset',
            field=models.CharField(blank=True, default='f_columns', max_length=20),
        ),
        migrations.AlterField(
            model_name='clientwebsite',
            name='nav_preset',
            field=models.CharField(blank=True, default='side_classic', max_length=20),
        ),
    ]
