"""End-to-end test ya builder: signup → bootstrap → items → subdomain render → shortcodes."""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from builder.models import ClientWebsite, SiteItem


class BuilderFlowTest(TestCase):
    def test_full_flow(self):
        c = Client()
        # 1. Signup + kuunda website ya utalii
        r = c.post('/builder/signup/', {
            'username': 'willy_test', 'password1': 'Kilimanjaro#2026', 'password2': 'Kilimanjaro#2026',
            'subdomain': 'kiliadventures', 'site_name': 'Kili Adventures', 'website_type': 'tourism',
        })
        self.assertEqual(r.status_code, 302, r.content[:500])
        site = ClientWebsite.objects.get(subdomain='kiliadventures')

        # 2. Structure imejitengeneza automatic kutoka schema
        page_slugs = set(site.pages.values_list('slug', flat=True))
        assert {'home', 'packages', 'trips', 'destinations', 'contact'} <= page_slugs, page_slugs
        col_slugs = set(site.collections.values_list('slug', flat=True))
        assert {'packages', 'trips', 'destinations'} == col_slugs, col_slugs
        print('✓ Signup + auto-structure (tourism): pages =', sorted(page_slugs))

        # 3. Ongeza package (kama mteja anavyofanya kwenye panel)
        packages = site.collections.get(slug='packages')
        r = c.post(f'/builder/site/{site.id}/collections/{packages.id}/new/', {
            'title': 'Serengeti Safari — Siku 5',
            'f_description': 'Safari kamili ya Serengeti na Ngorongoro.',
            'f_price': '1200', 'f_duration': 'Siku 5, Usiku 4',
            'f_destinations_covered': 'Serengeti, Ngorongoro',
            'f_includes': 'Usafiri 4x4\nMalazi\nChakula',
            'f_excludes': 'Tiketi za ndege',
            'f_itinerary': 'Siku 1: Arusha...',
            'is_visible': 'on', 'is_featured': 'on',
        })
        self.assertEqual(r.status_code, 302)
        item = SiteItem.objects.get(title__startswith='Serengeti')
        assert item.data['includes'] == ['Usafiri 4x4', 'Malazi', 'Chakula']
        print('✓ Package imeongezwa, list field imechakatwa:', item.data['includes'])

        # 4. Subdomain routing + shortcode rendering (draft: owner anaona preview)
        r = c.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        assert 'Serengeti Safari' in html, 'package haionekani kwenye [[collection:packages]]'
        assert 'Kili Adventures' in html, '[[site:name]] haija-render'
        assert '[[' not in html, 'shortcode left unrendered'
        print('✓ Subdomain + shortcodes zime-render (package inaonekana home page)')

        # 5. Item detail page + WhatsApp
        site.whatsapp_number = '+255712345678'
        site.save()
        r = c.get(f'/c/packages/{item.slug}/', HTTP_HOST='kiliadventures.jamiitek.com')
        self.assertEqual(r.status_code, 200)
        assert 'wa.me/255712345678' in r.content.decode()
        print('✓ Item detail + WhatsApp booking link')

        # 6. Mgeni (si mmiliki) anaona coming soon kwa draft site
        c2 = Client()
        r = c2.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        assert 'coming soon' in r.content.decode().lower()
        # Publish → mgeni anaona site
        site.is_published = True
        site.save()
        r = c2.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        assert 'Serengeti Safari' in r.content.decode()
        print('✓ Draft/publish flow inafanya kazi')

        # 7. Subdomain isiyopo → 404 nzuri
        r = c2.get('/', HTTP_HOST='haipo123.jamiitek.com')
        self.assertEqual(r.status_code, 404)
        assert 'not registered' in r.content.decode()
        print('✓ Subdomain isiyopo → page ya kuvutia mteja mpya')

        # 8. GrapesJS save/load endpoints
        home = site.pages.get(slug='home')
        r = c.post(f'/builder/site/{site.id}/pages/{home.id}/save/',
                   json.dumps({'project': {'pages': []}, 'html': '<h1>[[site:name]]</h1>[[collection:packages]]', 'css': 'h1{color:red}'}),
                   content_type='application/json')
        self.assertEqual(r.status_code, 200)
        r = c.get(f'/builder/site/{site.id}/pages/{home.id}/load/')
        assert r.json() == {'pages': []}
        r = c2.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        html = r.content.decode()
        assert '<h1>Kili Adventures</h1>' in html and 'Serengeti' in html
        print('✓ Editor save/load + design mpya ina-render na shortcodes')

        # 9. Usalama: mteja mwingine hawezi kuhariri site ya Willy
        User.objects.create_user('mwizi', password='Wizi#123456')
        c3 = Client(); c3.login(username='mwizi', password='Wizi#123456')
        r = c3.get(f'/builder/site/{site.id}/')
        self.assertEqual(r.status_code, 404)
        print('✓ Ownership security: mteja mwingine anapata 404')

        # 10. Reserved subdomain inakataliwa
        r = c3.post('/builder/new/', {'subdomain': 'admin', 'site_name': 'X', 'website_type': 'default'})
        assert ClientWebsite.objects.filter(subdomain='admin').count() == 0
        print('✓ Reserved subdomains zinakataliwa')
        print('\n=== TESTS ZOTE ZIMEPITA ✓ ===')
