"""
Sajili IPN URL kwa Pesapal na upate ipn_id ya kuweka kwenye env.

    python manage.py pesapal_register_ipn

Inatumia PESAPAL_BASE_URL + /pay/ipn/. Weka ipn_id inayorudi kwenye
env PESAPAL_IPN_ID ili tusisajili kila mara (hiari — mfumo unaweza
kusajili moja kwa moja pia).
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from apps.pesapal_client import PesapalClient, PesapalError


class Command(BaseCommand):
    help = 'Register the Pesapal IPN URL and print the ipn_id'

    def add_arguments(self, parser):
        parser.add_argument('--type', default='POST', choices=['POST', 'GET'],
                            help='ipn_notification_type (default POST)')

    def handle(self, *args, **opts):
        client = PesapalClient()
        if not client.configured:
            raise CommandError('Weka PESAPAL_CONSUMER_KEY / PESAPAL_CONSUMER_SECRET kwanza.')

        base = (getattr(settings, 'PESAPAL_BASE_URL', '') or '').rstrip('/')
        ipn_url = f'{base}{reverse("pesapal_ipn")}'
        self.stdout.write(f'Env: {client.env}')
        self.stdout.write(f'IPN URL: {ipn_url}')

        try:
            data = client.register_ipn(ipn_url, notification_type=opts['type'])
        except PesapalError as e:
            raise CommandError(f'Imeshindikana: {e}')

        ipn_id = data.get('ipn_id', '')
        self.stdout.write(self.style.SUCCESS(f'\nipn_id = {ipn_id}'))
        self.stdout.write('\nWeka hii kwenye env:')
        self.stdout.write(f'  PESAPAL_IPN_ID={ipn_id}\n')
