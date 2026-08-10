from django.db import migrations


class Migration(migrations.Migration):
    """
    Neutralised on purpose — do not delete this file.

    It used to AddField facebook_link / instagram_link / linkedin_link /
    twitter_link onto Team. But Team is not created by 0001_initial; it is
    created by 0003_team, which already includes all four fields.

    Because 0003_team depends on 0002_rename_image_1... rather than on this
    file, Django is free to run 0003_team first. On a fresh database that
    produced:

        django.db.utils.OperationalError: duplicate column name: facebook_link

    Existing databases are unaffected: Django records only the migration
    name, so this stays "applied" everywhere it already ran. Emptying the
    operations fixes new installs without rewriting history.
    """

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = []
