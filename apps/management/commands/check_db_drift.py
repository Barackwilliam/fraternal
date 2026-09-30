"""Linganisha models na jedwali halisi ya database.

Django inaamini kwamba kila migration iliyoandikwa kwenye `django_migrations`
ilifanikiwa kikamilifu. Ikitokea migration ilikatika katikati — mtandao
ukakatika, Supabase ikachoka, au mtu akaiweka kwa mkono kama "applied" —
Django haitagundua kamwe. `showmigrations` itaonyesha [X], lakini nguzo
haipo. Kosa linakuja baadaye kama:

    django.db.utils.ProgrammingError: column apps_managedwebsite.discount_3m
    does not exist

Command hii inasoma jedwali halisi na kuzilinganisha na models. Haibadilishi
chochote — inaonyesha tu kilichokosekana, na SQL ya kukirekebisha.

    python manage.py check_db_drift
    python manage.py check_db_drift --app apps
    python manage.py check_db_drift --sql        # SQL pekee
"""
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Onyesha nguzo zilizopo kwenye models lakini hazipo kwenye database.'

    def add_arguments(self, parser):
        parser.add_argument('--app', default=None,
                            help='Kagua app moja pekee, mfano: apps')
        parser.add_argument('--sql', action='store_true',
                            help='Toa SQL ya kurekebisha pekee, bila maelezo')

    def handle(self, *args, **opts):
        only_app = opts.get('app')
        sql_only = opts.get('sql')

        with connection.cursor() as cursor:
            existing_tables = set(connection.introspection.table_names(cursor))

            missing_tables = []
            missing_columns = []   # (model, table, column, field)
            extra_columns = []     # (table, column)

            for model in django_apps.get_models():
                if only_app and model._meta.app_label != only_app:
                    continue
                if not model._meta.managed:
                    continue

                table = model._meta.db_table
                if table not in existing_tables:
                    missing_tables.append((model, table))
                    continue

                desc = connection.introspection.get_table_description(cursor, table)
                db_cols = {c.name for c in desc}
                # Nguzo NOT NULL isiyo na default: INSERT ya Django (isiyoijua)
                # inashindwa — inazuia kuhifadhi rows mpya kabisa.
                blocking = {c.name for c in desc
                            if not c.null_ok and getattr(c, 'default', None) is None}
                model_cols = {}
                for field in model._meta.local_fields:
                    model_cols[field.column] = field

                for col, field in model_cols.items():
                    if col not in db_cols:
                        missing_columns.append((model, table, col, field))

                for col in db_cols - set(model_cols):
                    extra_columns.append((table, col, col in blocking))

        if sql_only:
            for _, table, col, field in missing_columns:
                self.stdout.write(self._alter_sql(table, col, field))
            return

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING(
            f'Database: {connection.settings_dict.get("NAME")} '
            f'({connection.vendor})'))
        self.stdout.write('')

        if not missing_tables and not missing_columns:
            self.stdout.write(self.style.SUCCESS(
                '  Nguzo zote za models zipo kwenye database.'))
        else:
            if missing_tables:
                self.stdout.write(self.style.ERROR('  JEDWALI ZINAZOKOSEKANA'))
                for model, table in missing_tables:
                    self.stdout.write(
                        f'    {table:<44} ({model._meta.label})')
                self.stdout.write('')
                self.stdout.write(
                    '    Jedwali zima halipo — hiyo si drift, ni migration '
                    'ambayo haijaendeshwa kabisa. Endesha `migrate` kwanza.')
                self.stdout.write('')

            if missing_columns:
                self.stdout.write(self.style.ERROR('  NGUZO ZINAZOKOSEKANA'))
                for model, table, col, field in missing_columns:
                    self.stdout.write(f'    {table}.{col}')
                self.stdout.write('')
                self.stdout.write(
                    '  Nguzo hizi zipo kwenye models lakini hazipo kwenye '
                    'database. Migration iliyotakiwa kuziunda ime-')
                self.stdout.write(
                    '  rekodiwa kama "applied", lakini haikukamilika. SQL ya '
                    'kurekebisha:')
                self.stdout.write('')
                for _, table, col, field in missing_columns:
                    self.stdout.write(
                        self.style.WARNING('    ' + self._alter_sql(table, col, field)))
                self.stdout.write('')
                self.stdout.write(
                    '  Endesha SQL hii kwenye Supabase SQL Editor, kisha '
                    'endesha command hii tena kuthibitisha.')

        breaking = [(t, c) for t, c, b in extra_columns if b]
        harmless = [(t, c) for t, c, b in extra_columns if not b]
        if breaking:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(
                '  NGUZO ZA ZIADA ZINAZOZUIA KUHIFADHI (NOT NULL, bila default)'))
            for table, col in breaking:
                self.stdout.write(f'    {table}.{col}')
            self.stdout.write('')
            self.stdout.write(
                '  Django haizijui, kwa hiyo haiziwekei thamani — kila INSERT kwenye')
            self.stdout.write(
                '  jedwali hizi inashindwa (IntegrityError / 500). SQL salama ya kurekebisha')
            self.stdout.write(
                '  (inaruhusu NULL tu — haifuti nguzo wala data):')
            self.stdout.write('')
            for table, col in breaking:
                self.stdout.write(self.style.WARNING(
                    f'    ALTER TABLE "{table}" ALTER COLUMN "{col}" DROP NOT NULL;'))
        if harmless:
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(
                '  NGUZO ZILIZOACHWA (zipo kwenye database, hazipo kwenye models)'))
            for table, col in harmless:
                self.stdout.write(f'    {table}.{col}')
            self.stdout.write('')
            self.stdout.write(
                '  Hizi hazizuii kuhifadhi (zinaruhusu NULL au zina default). Ni mabaki '
                'ya fields zilizoondolewa. Ziache mpaka uwe na uhakika.')

        self.stdout.write('')

    # ── msaada ────────────────────────────────────────────────
    def _alter_sql(self, table, col, field):
        """SQL ya kuongeza nguzo moja, kwa vendor iliyopo.

        `IF NOT EXISTS` inafanya kazi PostgreSQL (Supabase). SQLite haiiungi
        mkono — kwenye SQLite iondoe kwa mkono.
        """
        db_type = field.db_type(connection) or 'text'

        null = '' if field.null else ' NOT NULL'
        default = ''
        if not field.null and field.has_default():
            value = field.get_default()
            if callable(value):
                value = value()
            if isinstance(value, str):
                default = f" DEFAULT '{value}'"
            elif isinstance(value, bool):
                default = f" DEFAULT {'true' if value else 'false'}"
            elif value is not None:
                default = f' DEFAULT {value}'

        return (f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS '
                f'"{col}" {db_type}{default}{null};')
