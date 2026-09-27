"""Unda jedwali la cache (`jamiitek_cache`).

Ratiba ya mfumo mzima — DailyTasksMiddleware — inakumbuka "kazi hii
imeshafanyika leo" kwa alama zilizohifadhiwa kwenye cache. Cache ya
awali ilikuwa LocMemCache: kumbukumbu ya process moja, inayofutwa kila
deploy. Kwa hiyo digest na ripoti za mwezi zingeweza kutumwa mara kadhaa
kwa siku ile ile.

`createcachetable` ni salama kuendeshwa mara nyingi — inaangalia kwanza
kama jedwali lipo. Ikiwa unatumia Redis (REDIS_URL imewekwa), jedwali
hili linaundwa lakini halitumiki, na halina madhara.
"""
from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    call_command('createcachetable', 'jamiitek_cache',
                 database=schema_editor.connection.alias, verbosity=0)


def drop_cache_table(apps, schema_editor):
    with schema_editor.connection.cursor() as c:
        c.execute('DROP TABLE IF EXISTS jamiitek_cache')


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0037_blog_authors'),
    ]

    operations = [
        migrations.RunPython(create_cache_table, drop_cache_table),
    ]
