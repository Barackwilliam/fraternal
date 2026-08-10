from django.db import migrations


class Migration(migrations.Migration):
    """
    Neutralised on purpose — do not delete this file.

    Same story as 0002: 0004_team already creates Team with linkedin_link,
    so adding it again fails on a fresh database with

        django.db.utils.OperationalError: duplicate column name: linkedin_link

    Existing databases keep it recorded as applied, so nothing changes there.
    """

    dependencies = [
        ('apps', '0004_team'),
    ]

    operations = []
