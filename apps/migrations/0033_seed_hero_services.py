"""Hamisha hero (slaidi 5) na "What we build" (huduma 8) kutoka template kwenda database.

Zilikuwa zimeandikwa ndani ya index.html. Zilionekana homepage lakini si
kwenye admin, kwa hiyo hazikuweza kuhaririwa. Sasa ni rekodi za kawaida.

HERO: slaidi zinaongezwa TU kama jedwali la HeroSlide ni tupu.

HUDUMA: `Service` inatumika pia na ukurasa wa /service/, kwa hiyo huenda
tayari una huduma kwenye database. Hatugusi maelezo wala picha zako:
  - huduma yenye JINA lile lile ipo -> tunaijaza sehemu mpya za kadi tu
    (summary, icon, rangi, link) na kuiweka show_on_home
  - haipo -> tunaiunda
Huduma nyingine zako zilizopo zinabaki kama zilivyo, na hazionekani
homepage mpaka utakapoweka tiki ya "Show on home".

Picha ni faili zilizopo kwenye static (/static/images/...), zinaandikwa
kama URL kamili kwa sababu ImageMixin inakubali URL za http pekee.
"""
from django.conf import settings
from django.db import migrations

HERO = [{'image': 'images/hero/hero-1.jpg',
  'eyebrow': 'Website Development',
  'headline': 'We Build Websites That *Win Customers*',
  'subheadline': 'Fast, secure and mobile-first sites designed to turn visitors into paying customers. '
                 'Delivered in 2–6 weeks, from TZS 150,000.',
  'cta_label': 'Start Your Project',
  'cta_url': '/get-started/',
  'cta2_label': 'See Our Work',
  'cta2_url': '#work'},
 {'image': 'images/hero/hero-2.jpg',
  'eyebrow': 'AI WhatsApp Chatbot',
  'headline': 'Answer Every Customer, *Even at 2am*',
  'subheadline': 'JamiiBot replies to your WhatsApp customers in Swahili and English, 24 hours a day — and '
                 'on your website too. Live in 10 minutes, from TZS 5,000 a month.',
  'cta_label': 'Get Free Trial',
  'cta_url': '/bot/',
  'cta2_label': 'Try It on WhatsApp',
  'cta2_url': 'https://wa.me/255629712678'},
 {'image': 'images/hero/hero-3.jpg',
  'eyebrow': 'Hosting & Domains',
  'headline': 'Hosting That *Never Sleeps*',
  'subheadline': '99.9% uptime, free SSL, daily backups and renewal reminders before anything expires. '
                 'Domains from TZS 15,000 a year.',
  'cta_label': 'Check a Domain',
  'cta_url': '#domains',
  'cta2_label': 'View Hosting',
  'cta2_url': '#hosting'},
 {'image': 'images/hero/hero-4.jpg',
  'eyebrow': 'Website Builder',
  'headline': 'Your Website Live in *10 Minutes*',
  'subheadline': 'Pick a template, let AI write your content, and publish on a free jamiitek.com subdomain. '
                 'Orders go straight to your WhatsApp.',
  'cta_label': 'Start Building Free',
  'cta_url': '/builder/',
  'cta2_label': 'Browse Templates',
  'cta2_url': '/templates/'},
 {'image': 'images/hero/hero-5.jpg',
  'eyebrow': 'Custom Software & Mobile Apps',
  'headline': 'Systems Built *Around Your Business*',
  'subheadline': 'POS, school management, booking, inventory — Android and iOS apps engineered for Tanzanian '
                 'networks and real workloads.',
  'cta_label': 'Discuss Your System',
  'cta_url': '/get-started/',
  'cta2_label': 'Explore Services',
  'cta2_url': '/service/'}]

SERVICES = [{'name': 'Website Development',
  'image': 'images/services/web-development.jpg',
  'summary': 'Modern responsive websites built for speed, security and conversion. From TZS 150,000.',
  'link_url': '',
  'link_label': 'Learn more',
  'icon': 'code',
  'accent': '#2E7BF6'},
 {'name': 'AI WhatsApp Bot',
  'image': 'images/services/jamiibot.jpg',
  'summary': 'JamiiBot answers customers 24/7 in Swahili and English, on WhatsApp and your website. From TZS '
             '5,000/month.',
  'link_url': '/bot/',
  'link_label': 'Learn more',
  'icon': 'bot',
  'accent': '#1FA97A'},
 {'name': 'Hosting & Servers',
  'image': 'images/services/hosting.jpg',
  'summary': '99.9% uptime, free SSL, daily backups and proactive monitoring on every plan.',
  'link_url': '#hosting',
  'link_label': 'Learn more',
  'icon': 'server',
  'accent': '#7431C4'},
 {'name': 'Domain Registration',
  'image': 'images/services/domains.jpg',
  'summary': 'Register .com, .co.tz and .tz domains — we handle the registry paperwork.',
  'link_url': '#domains',
  'link_label': 'Check availability',
  'icon': 'globe',
  'accent': '#16A34A'},
 {'name': 'Mobile App Development',
  'image': 'images/services/mobile-apps.jpg',
  'summary': 'Android and iOS apps designed for scale, offline resilience and low data use.',
  'link_url': '',
  'link_label': 'Learn more',
  'icon': 'mobile',
  'accent': '#F5A623'},
 {'name': 'UI/UX Design',
  'image': 'images/services/ui-ux-design.jpg',
  'summary': 'Interfaces people actually understand — and that turn visitors into customers.',
  'link_url': '',
  'link_label': 'Learn more',
  'icon': 'design',
  'accent': '#14B8A6'},
 {'name': 'Website Builder',
  'image': 'images/services/website-builder.jpg',
  'summary': 'Build your own site in 10 minutes with a free subdomain on jamiitek.com.',
  'link_url': '/builder/',
  'link_label': 'Try it free',
  'icon': 'builder',
  'accent': '#F97316'},
 {'name': 'Ready-Made Templates',
  'image': 'images/services/templates.jpg',
  'summary': 'Launch in hours, not weeks. Hosted from TZS 15,000/month.',
  'link_url': '/templates/',
  'link_label': 'Browse templates',
  'icon': 'layout',
  'accent': '#EF4444'}]


def _static(path):
    base = (getattr(settings, 'SITE_URL', '') or 'https://www.jamiitek.com').rstrip('/')
    return f'{base}/static/{path}'


def seed(apps, schema_editor):
    HeroSlide = apps.get_model('apps', 'HeroSlide')
    Service = apps.get_model('apps', 'Service')

    if not HeroSlide.objects.exists():
        for i, h in enumerate(HERO, start=1):
            HeroSlide.objects.create(
                image=_static(h['image']), eyebrow=h['eyebrow'], headline=h['headline'],
                subheadline=h['subheadline'], cta_label=h['cta_label'], cta_url=h['cta_url'],
                cta2_label=h['cta2_label'], cta2_url=h['cta2_url'],
                focal='center', is_active=True, order=i * 10,
            )

    for i, s in enumerate(SERVICES, start=1):
        card = dict(show_on_home=True, order=i * 10, summary=s['summary'],
                    link_url=s['link_url'], link_label=s['link_label'],
                    icon=s['icon'], accent=s['accent'])
        existing = Service.objects.filter(service_type__iexact=s['name']).first()
        if existing:
            for k, v in card.items():
                setattr(existing, k, v)
            if not existing.image:
                existing.image = _static(s['image'])
            existing.save()
        else:
            Service.objects.create(service_type=s['name'], description=s['summary'],
                                   image=_static(s['image']), **card)


def unseed(apps, schema_editor):
    HeroSlide = apps.get_model('apps', 'HeroSlide')
    HeroSlide.objects.filter(headline__in=[h['headline'] for h in HERO]).delete()
    Service = apps.get_model('apps', 'Service')
    Service.objects.filter(service_type__in=[s['name'] for s in SERVICES]).update(show_on_home=False)


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0032_service_home_card'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
