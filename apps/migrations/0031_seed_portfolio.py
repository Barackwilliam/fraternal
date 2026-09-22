"""Hamisha kadi sita za "Selected work" kutoka template kwenda database.

Zilikuwa zimeandikwa ndani ya index.html kama akiba. Zilionekana kwenye
homepage lakini hazikuonekana kwenye admin — kwa hiyo hazikuweza
kuhaririwa wala kufutwa. Sasa ni rekodi za kawaida za PortfolioItem.

Zinaongezwa TU kama jedwali ni tupu. Ukiwa tayari umeongeza projects
zako, migration hii haigusi chochote.

Hazina picha kwa makusudi: picha zilizokuwa kwenye template zilikuwa
placeholders zenye maandishi "Screenshot of the live site". Kadi bila
picha inaonyesha herufi ya kwanza, hadi utakapopakia screenshot halisi.
"""
from django.db import migrations

PROJECTS = [
    ('Mudandaza', 'POS & Marketplace',
     'Multi-branch point of sale with inventory, loans and four languages.'),
    ('Safari Travels', 'Tourism',
     'Tour packages, enquiry forms and booking flow for inbound travellers.'),
    ('NyumbaChap', 'Real Estate',
     'Property listings with search, agent dashboards and lead capture.'),
    ('Charles Academy', 'School System',
     'Students, fees, results and PDF report cards in one system.'),
    ('Kilimoni AI', 'AI Assistant',
     'WhatsApp advisor giving farmers crop guidance in Swahili.'),
    ('Rode Poultry', 'E-Commerce',
     'Bilingual online store with orders routed straight to WhatsApp.'),
]


def seed(apps, schema_editor):
    PortfolioItem = apps.get_model('apps', 'PortfolioItem')
    if PortfolioItem.objects.exists():
        return
    for i, (title, category, summary) in enumerate(PROJECTS, start=1):
        PortfolioItem.objects.create(
            title=title, category=category, summary=summary,
            is_featured=True, order=i * 10,   # nafasi ya kuingiza katikati baadaye
        )


def unseed(apps, schema_editor):
    PortfolioItem = apps.get_model('apps', 'PortfolioItem')
    PortfolioItem.objects.filter(
        title__in=[p[0] for p in PROJECTS], image='', live_url='',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0030_supabase_image'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
