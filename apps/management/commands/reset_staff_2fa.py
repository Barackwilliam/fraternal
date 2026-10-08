"""
Ondoa 2FA ya staff aliyepoteza simu NA recovery codes.

    python manage.py reset_staff_2fa <username>

Akiingia tena, atalazimishwa kuunganisha simu mpya (QR mpya).
Iendeshe kwenye Render → Shell tu, baada ya kuthibitisha ni yeye kweli.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from apps.security_models import StaffTwoFactor


class Command(BaseCommand):
    help = 'Reset two-step verification for a staff user (lost phone).'

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, username, **opts):
        user = User.objects.filter(username=username).first()
        if not user:
            raise CommandError(f'User "{username}" haipo.')
        n, _ = StaffTwoFactor.objects.filter(user=user).delete()
        # Sessions zake zote zinakufa — anaanza upya kwa nywila + simu mpya
        from django.contrib.sessions.models import Session
        killed = 0
        for s in Session.objects.all().iterator():
            if str(s.get_decoded().get('_auth_user_id')) == str(user.pk):
                s.delete()
                killed += 1
        self.stdout.write(self.style.SUCCESS(
            f'2FA ya {username} imeondolewa ({n} rekodi), sessions {killed} zimefungwa. '
            'Akiingia tena ataunganisha simu mpya.'))
