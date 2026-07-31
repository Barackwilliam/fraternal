"""
Management command: send_expiry_emails

Run daily to check all websites/domains and send expiry warnings automatically.

USAGE:
    python manage.py send_expiry_emails

HEROKU SCHEDULER (free):
    Add job: python manage.py send_expiry_emails
    Frequency: Daily

RENDER CRON (paid) or manual:
    Set cron: 0 8 * * * cd /app && python manage.py send_expiry_emails
"""

from django.core.management.base import BaseCommand
from apps.utils.email_notifications import send_bulk_expiry_warnings


class Command(BaseCommand):
    help = 'Send hosting and domain expiry warning emails to all clients'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Checking all websites and domains...')

        result = send_bulk_expiry_warnings()

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Done!\n"
            f"   Emails sent:  {result['sent']}\n"
            f"   Skipped:      {result['skipped']}\n"
            f"   Errors:       {result['errors']}\n"
        ))
