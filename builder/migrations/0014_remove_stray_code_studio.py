"""Ondoa mabaki ya `0008_code_studio` — migration iliyoingia kwa bahati mbaya.

Ilitoka kwenye patch ya zamani ya "Code Studio" ambayo haikutakiwa kutumika
(Studio iliyopo ina `raw_document` yake). Iliingia pamoja na patch nyingine,
ikaleta namba mbili za `0008` kwenye builder.

Kama iliwahi kuendeshwa, iliongeza nguzo nne kwenye `builder_sitepage` ambazo
model haizijui: `mode`, `code_html`, `code_css`, `code_updated_at`. Nguzo za
aina hiyo zikiwa NOT NULL bila default ya database, kila SitePage mpya ingeshindwa
kuhifadhiwa.

Migration hii ni salama kwa hali zote mbili:
  - kama nguzo zipo  -> zinaondolewa, na rekodi ya 0008_code_studio inafutwa
  - kama hazipo      -> haifanyi chochote
"""
from django.db import migrations

STRAY_COLUMNS = ('mode', 'code_html', 'code_css', 'code_updated_at')
TABLE = 'builder_sitepage'


def cleanup(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cur:
        existing = {c.name for c in conn.introspection.get_table_description(cur, TABLE)}
    qn = schema_editor.quote_name
    for col in STRAY_COLUMNS:
        if col in existing:
            schema_editor.execute(f'ALTER TABLE {qn(TABLE)} DROP COLUMN {qn(col)}')
    with conn.cursor() as cur:
        cur.execute("DELETE FROM django_migrations WHERE app = %s AND name = %s",
                    ['builder', '0008_code_studio'])


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0013_default_top_header'),
    ]

    operations = [
        migrations.RunPython(cleanup, migrations.RunPython.noop),
    ]
