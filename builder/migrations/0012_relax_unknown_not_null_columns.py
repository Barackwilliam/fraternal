"""
Ruhusu NULL kwenye nguzo za ZIADA za majedwali ya builder (Postgres pekee).

TATIZO

Database ya production ina nguzo kwenye builder_sitepage (code_css na
nyingine) ambazo hazipo kwenye models, na ni NOT NULL bila default. Django
haizijui, kwa hiyo haiziwekei thamani, na kila INSERT ya ukurasa ilishindwa:

    IntegrityError: null value in column "code_css" of relation
    "builder_sitepage" violates not-null constraint

Matokeo: kuunda website → 500, site ikibaki bila kurasa, na panel → 500.

SULUHISHO

Kwa kila jedwali la builder, nguzo ambazo migrations hazijui (zinalinganishwa
na state ya migrations hadi 0011) na ni NOT NULL → DROP NOT NULL.
  - haifuti nguzo wala data (mfumo mwingine unaozitumia bado unaziandikia)
  - nguzo za models haziguswi kamwe
  - kuiendesha tena hakuna madhara; kwenye database safi haifanyi kitu
  - SQLite (tests/dev) inarukwa
"""
from django.db import migrations

TABLES = ('ClientWebsite', 'SitePage', 'SiteCollection', 'SiteItem', 'SiteAsset',
          'SiteInquiry', 'AiUsageLog', 'SiteImport')


def relax(apps, schema_editor):
    conn = schema_editor.connection
    if conn.vendor != 'postgresql':
        return
    with conn.cursor() as cur:
        for name in TABLES:
            model = apps.get_model('builder', name)
            table = model._meta.db_table
            known = {f.column for f in model._meta.local_fields}
            cur.execute(
                """SELECT column_name FROM information_schema.columns
                   WHERE table_schema = current_schema() AND table_name = %s
                     AND is_nullable = 'NO'""", [table])
            for (column,) in cur.fetchall():
                if column in known:
                    continue
                cur.execute('ALTER TABLE {} ALTER COLUMN {} DROP NOT NULL'.format(
                    schema_editor.quote_name(table), schema_editor.quote_name(column)))
                print(f'  builder: {table}.{column} sasa inaruhusu NULL')


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0011_layout_presets'),
    ]

    operations = [
        migrations.RunPython(relax, migrations.RunPython.noop),
    ]
