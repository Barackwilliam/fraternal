"""
SiteAsset: `uploadcare_url` -> `url`.

Image zote sasa ziko Supabase Storage. Jina la zamani lingekuwa
linadanganya — na code inayolisoma ingemfanya msomaji adhani bado
tunatumia Uploadcare.

RenameField inahifadhi data iliyomo (hakuna iliyopo — hakuna tovuti
iliyojengwa bado), kwa hiyo hii ni salama pande zote mbili.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0005_clientwebsite_custom_footer_html_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteasset',
            old_name='uploadcare_url',
            new_name='url',
        ),
    ]
