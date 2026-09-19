"""
Weka bei mpya za mpango: Elfu 5, 10, 15.

Render free tier hairuhusu kuendesha `seed_plans` kwa mkono, na `build.sh`
inaendesha `migrate` pekee. Kwa hiyo tunaweka bei kupitia data migration
hii — inajiendesha yenyewe wakati wa deploy.

Inatumia update_or_create kwa `slug`, kwa hiyo inasasisha mipango iliyopo
NA inatengeneza kama haipo (kwa DB mpya).
"""
from django.db import migrations


PLANS = [
    {'slug': 'basic',      'name': 'Starter',    'price_tzs': 5000,  'msg_limit': 5000,
     'max_services': 5,  'features': ['5,000 messages / month', 'Email support', 'Dashboard'],
     'sort_order': 1, 'is_active': True},
    {'slug': 'pro',        'name': 'Business',   'price_tzs': 10000, 'msg_limit': 10000,
     'max_services': 20, 'features': ['10,000 messages / month', 'WhatsApp support', 'Full analytics', 'Unlimited FAQs'],
     'sort_order': 2, 'is_active': True},
    {'slug': 'enterprise', 'name': 'Enterprise', 'price_tzs': 15000, 'msg_limit': 0,
     'max_services': 50, 'features': ['Unlimited messages', 'Priority support', 'Custom setup'],
     'sort_order': 3, 'is_active': True},
]


def set_prices(apps, schema_editor):
    Plan = apps.get_model('chatbot', 'SubscriptionPlan')
    for data in PLANS:
        Plan.objects.update_or_create(slug=data['slug'], defaults=data)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0011_default_messages'),
    ]

    operations = [
        migrations.RunPython(set_prices, noop),
    ]
