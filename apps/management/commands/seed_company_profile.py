"""Jaza CompanyProfile na data halisi ya JamiiTek (kutoka company profile docx)."""
from django.core.management.base import BaseCommand
from apps.models import CompanyProfile


SERVICES = [
    ('Web Development', 'Maendeleo ya Tovuti',
     'Custom websites and web applications built with Django, React, and modern frameworks. From business brochure sites to complex SaaS platforms — we build it all.',
     'Tovuti na programu za wavuti zilizoundwa kwa Django, React na teknolojia za kisasa. Kuanzia tovuti za biashara hadi mifumo mikubwa ya SaaS.'),
    ('Mobile Apps', 'Programu za Simu',
     'Native and cross-platform mobile applications using Flutter and Firebase. We build apps for Android and iOS that are fast, beautiful, and user-friendly.',
     'Programu za simu za Android na iOS kwa kutumia Flutter na Firebase — za haraka, nzuri na rahisi kutumia.'),
    ('WhatsApp Bots & AI Automation', 'WhatsApp Bots na AI',
     'Intelligent WhatsApp chatbots and automation tools for businesses. Customer support bots, order management systems, and AI-powered messaging workflows.',
     'Chatbot za WhatsApp na mifumo ya kiotomatiki kwa biashara — huduma kwa wateja, usimamizi wa oda, na ujumbe unaoendeshwa na AI.'),
    ('USSD Applications', 'Mifumo ya USSD',
     "USSD-based services via Africa's Talking for reaching customers without smartphones or internet — ideal for agriculture, health, and financial services.",
     'Huduma za USSD kufikia wateja wasio na simu janja au intaneti — nzuri kwa kilimo, afya na huduma za kifedha.'),
    ('E-Commerce Solutions', 'Mifumo ya Biashara Mtandaoni',
     'Full-featured online stores with product management, payments, and delivery tracking — built for the Tanzanian market.',
     'Maduka kamili ya mtandaoni yenye usimamizi wa bidhaa, malipo na ufuatiliaji wa usafirishaji — kwa soko la Tanzania.'),
    ('Digital Marketing & SEO', 'Masoko ya Kidijitali na SEO',
     'Google Ads management, Google Business Profile optimization, SEO strategy, and social media setup to grow your business online.',
     'Usimamizi wa Google Ads, Google Business Profile, mikakati ya SEO, na mitandao ya kijamii kukuza biashara yako.'),
    ('SaaS Platforms', 'Mifumo ya SaaS',
     'Multi-tenant software platforms for businesses needing subscription-based tools — including dashboards, reporting, invoicing, and user management.',
     'Mifumo ya SaaS kwa biashara zinazohitaji huduma za usajili — dashibodi, ripoti, ankara na usimamizi wa watumiaji.'),
]

WHY_US = [
    ('We are local — we understand the Tanzanian and East African market deeply',
     'Sisi ni wa hapa — tunaelewa soko la Tanzania na Afrika Mashariki kwa kina'),
    ('Affordable pricing without compromising on quality',
     'Bei nafuu bila kupunguza ubora'),
    ('We deliver complete, ready-to-use solutions — not half-finished projects',
     'Tunatoa mifumo kamili iliyo tayari kutumika — si miradi isiyokamilika'),
    ("Full support after delivery — we don't disappear after handover",
     'Msaada kamili baada ya kukabidhi — hatupotei'),
    ('We use modern, globally-proven technologies adapted for local needs',
     'Tunatumia teknolojia za kisasa zinazokubalika duniani, zilizobadilishwa kwa mahitaji ya hapa'),
    ('Clear communication throughout the project — no surprises',
     'Mawasiliano wazi katika mradi wote — hakuna mshangao'),
    ('Flexible payment terms — we work with your budget',
     'Masharti ya malipo yanayonyumbulika — tunafanya kazi na bajeti yako'),
]

PROJECTS = [
    ('MMexy Tanzania Adventures', 'Multilingual Safari Website', 'Django, Google Translate API'),
    ('Summit Scape Adventures', 'Safari Website + Google Ads', 'Django, Google Business Profile'),
    ('Kiliprecious Tours', 'Safari & Tour Company Website', 'Django'),
    ('Sunrise and Sunset Safaris', 'Safari Company Website', 'Django'),
    ('EM Adventure Tanzania', 'Adventure Tourism Website', 'Django'),
    ('Kili2Pori Expedition', 'Kilimanjaro Expedition Website', 'Django'),
    ('SokoSmart', 'E-Commerce / Marketplace Platform', 'Django'),
    ('Sokoni App', 'Local Business Directory App', 'Flutter, Firebase'),
    ('Mudandaza SaaS', 'Multi-Business Management Platform', 'Django, PostgreSQL'),
    ('Pendo Essence', 'E-Commerce Store', 'Django, Uploadcare'),
    ('Shamba Mfukoni', 'Agricultural USSD App', "Django, Africa's Talking"),
    ('Charles Academy', 'School Management System', 'Django, Live Chat'),
    ('SoftLoan', 'Student Loan Management System', 'Django, Uploadcare'),
]


class Command(BaseCommand):
    help = 'Seed the JamiiTek company profile with real data'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Overwrite the existing active profile')

    def handle(self, *args, **opts):
        profile = CompanyProfile.objects.filter(is_active=True).first()
        if profile and not opts['force']:
            self.stdout.write(self.style.WARNING(
                'An active profile already exists. Use --force to overwrite.'))
            return
        if profile is None:
            profile = CompanyProfile()

        profile.company_name = 'JamiiTek Digital Agency'
        profile.short_name = 'JamiiTek'
        profile.period = '2025 — 2026'
        profile.about_en = (
            'JamiiTek is a Tanzanian-based digital agency specializing in web development, '
            'mobile application development, AI-powered automation, and digital marketing '
            'solutions. Founded and operated by experienced Tanzanian developers, we are '
            'committed to delivering world-class technology solutions tailored to the '
            'African market.\n\n'
            'We believe that every business — big or small — deserves powerful digital '
            'tools. That is why we combine technical expertise with a deep understanding '
            'of local business needs to build solutions that actually work for our clients.'
        )
        profile.about_sw = (
            'JamiiTek ni kampuni ya kidijitali yenye makao yake Tanzania, inayobobea katika '
            'utengenezaji wa tovuti, programu za simu, mifumo ya kiotomatiki inayotumia AI, '
            'na masoko ya kidijitali. Imeanzishwa na kuendeshwa na wataalamu wa Kitanzania, '
            'tumejitolea kutoa suluhisho za teknolojia za kiwango cha kimataifa zinazofaa '
            'soko la Afrika.\n\n'
            'Tunaamini kila biashara — kubwa au ndogo — inastahili zana bora za kidijitali. '
            'Ndiyo maana tunachanganya utaalamu wa kiteknolojia na uelewa wa kina wa mahitaji '
            'ya biashara za hapa.'
        )
        profile.mission_en = (
            'To empower businesses and communities across Tanzania and East Africa with '
            'affordable, innovative, and reliable digital solutions that drive real growth.'
        )
        profile.mission_sw = (
            'Kuwezesha biashara na jamii kote Tanzania na Afrika Mashariki kwa suluhisho '
            'za kidijitali nafuu, za kibunifu na za kuaminika zinazoleta ukuaji halisi.'
        )
        profile.vision_en = (
            "To become East Africa's most trusted digital agency — known for quality, "
            'transparency, and technology that truly serves the people.'
        )
        profile.vision_sw = (
            'Kuwa kampuni ya kidijitali inayoaminika zaidi Afrika Mashariki — inayojulikana '
            'kwa ubora, uwazi, na teknolojia inayowahudumia watu kweli.'
        )
        profile.facts = [
            {'label_en': 'Registered', 'label_sw': 'Imesajiliwa', 'value': 'Dar es Salaam, Tanzania'},
            {'label_en': 'Specialization', 'label_sw': 'Utaalamu', 'value': 'Tech & Digital'},
            {'label_en': 'Website', 'label_sw': 'Tovuti', 'value': 'www.jamiitek.com'},
            {'label_en': 'Email', 'label_sw': 'Barua pepe', 'value': 'info@jamiitek.com'},
        ]
        profile.services = [
            {'name_en': a, 'name_sw': b, 'desc_en': c, 'desc_sw': d}
            for a, b, c, d in SERVICES
        ]
        profile.why_us = [{'text_en': a, 'text_sw': b} for a, b in WHY_US]
        profile.projects = [{'name': a, 'type': b, 'tech': c} for a, b, c in PROJECTS]
        profile.pricing_note_en = (
            'Every project is priced individually based on scope and complexity. '
            'We offer flexible payment terms — typically a deposit to begin and the '
            'balance on delivery. Contact us for a free, no-obligation quotation.'
        )
        profile.pricing_note_sw = (
            'Kila mradi hupangiwa bei kulingana na ukubwa na ugumu wake. Tunatoa masharti '
            'ya malipo yanayonyumbulika — kwa kawaida malipo ya awali kuanza na salio '
            'wakati wa kukabidhi. Wasiliana nasi kupata bei bila gharama yoyote.'
        )
        profile.email = 'info@jamiitek.com'
        profile.website = 'www.jamiitek.com'
        profile.address = 'Dar es Salaam, Tanzania'
        profile.is_active = True
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'✓ Company profile seeded: {len(profile.services)} services, '
            f'{len(profile.why_us)} points, {len(profile.projects)} projects.'))
        self.stdout.write('  View: /company-profile/   Edit: /manage/profile/')
