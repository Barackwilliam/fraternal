"""
python manage.py seed_plans

Seeds 3 subscription plans into the database.
Run once after deployment.
"""
from django.core.management.base import BaseCommand
from apps.chatbot.models import SubscriptionPlan


PLANS = [
    {
        'name':         'Starter',
        'slug':         'basic',
        'price_tzs':    15000,
        'msg_limit':    5000,
        'max_services': 5,
        'features':     ['5000 messages/month', 'Email support', 'Basic dashboard'],
        'sort_order':   1,
        'is_active':    True,
    },
    {
        'name':         'Business',
        'slug':         'pro',
        'price_tzs':    30000,
        'msg_limit':    10000,
        'max_services': 20,
        'features':     ['1,0000 messages/month', 'WhatsApp support', 'Full analytics', 'Unlimited FAQs'],
        'sort_order':   2,
        'is_active':    True,
    },
    {
        'name':         'Enterprise',
        'slug':         'enterprise',
        'price_tzs':    60000,
        'msg_limit':    0,
        'max_services': 50,
        'features':     ['Unlimited messages', 'Priority support', 'Custom setup'],
        'sort_order':   3,
        'is_active':    True,
    },
]


class Command(BaseCommand):
    help = 'Seed subscription plans into the database'

    def handle(self, *args, **options):
        self.stdout.write('Seeding subscription plans...\n')
        created = 0
        updated = 0
        for data in PLANS:
            obj, is_new = SubscriptionPlan.objects.update_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if is_new:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {obj.name} — TZS {obj.price_tzs:,}/month'))
            else:
                updated += 1
                self.stdout.write(f'  ↺  Updated: {obj.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — {created} created, {updated} updated.'
        ))
        self.stdout.write('\nCurrent plans:')
        for p in SubscriptionPlan.objects.order_by('sort_order'):
            limit = 'Unlimited' if p.is_unlimited else f'{p.msg_limit:,} msgs'
            self.stdout.write(f'  {p.sort_order}. {p.name:12} TZS {p.price_tzs:>8,}  {limit}')