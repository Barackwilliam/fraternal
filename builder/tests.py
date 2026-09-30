"""End-to-end test ya builder: signup → bootstrap → items → subdomain render → shortcodes."""
import io
import itertools
import json
import zipfile
from unittest import mock

from django.test import TestCase, SimpleTestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
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


# ══ Kupakia website nzima kwa ZIP ══════════════════════════════

def _zip(files, prefix=''):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name, data in files.items():
            zf.writestr(prefix + name, data)
    buf.seek(0)
    return buf


SAMPLE_SITE = {
    'index.html': (
        '<!DOCTYPE html><html><head><title>Duka Letu</title>'
        '<link rel="stylesheet" href="css/style.css"></head>'
        '<body><nav><a href="about.html">About</a> <a href="./contact.html#form">Contact</a>'
        ' <a href="#huduma">Huduma</a> <a href="https://example.com">Ext</a></nav>'
        '<img src="images/logo.png" srcset="images/logo.png 1x, images/logo@2x.png 2x">'
        '<div style="background:url(\'images/bg.jpg\')"></div>'
        '<img src="images/missing.png"><script src="js/app.js"></script>'
        '<script>console.log("hi")</script></body></html>'),
    'about.html': '<html><head><title>About Us</title></head><body><a href="index.html">Home</a></body></html>',
    'contact.html': '<h1>Contact</h1><a href="/">Home</a>',
    'blog/index.html': '<html><body><a href="../about.html">About</a></body></html>',
    'css/style.css': '@import "base.css"; body{background:url(../images/bg.jpg)} @font-face{src:url("../fonts/a.woff2")}',
    'css/base.css': 'h1{color:red}',
    'images/logo.png': b'\x89PNG fake',
    'images/logo@2x.png': b'\x89PNG fake2',
    'images/bg.jpg': b'jpg',
    'fonts/a.woff2': b'font',
    'js/app.js': 'console.log(1)',
    'server.php': '<?php echo 1;',
    '__MACOSX/._index.html': 'junk',
    '.DS_Store': 'junk',
}


def _fake_uploader():
    uploaded, counter = {}, itertools.count()

    def up(data, ext, content_type):
        url = f'https://cdn.test/f{next(counter)}.{ext}'
        uploaded[url] = data
        return url
    return up, uploaded


class SiteImportUnitTest(SimpleTestCase):
    def test_prepare_rewrites_pages_and_assets(self):
        from builder import site_import as si
        up, uploaded = _fake_uploader()
        result = si.prepare(_zip(SAMPLE_SITE, prefix='mysite/'), up)

        pages = {p['path']: p for p in result['pages']}
        self.assertEqual({p: pages[p]['slug'] for p in pages}, {
            'index.html': 'home', 'about.html': 'about',
            'contact.html': 'contact', 'blog/index.html': 'blog'})
        self.assertEqual(pages['index.html']['title'], 'Duka Letu')

        home = pages['index.html']['document']
        self.assertIn('href="/p/about/"', home)
        self.assertIn('href="/p/contact/#form"', home)
        self.assertIn('href="#huduma"', home)
        self.assertIn('href="https://example.com"', home)
        self.assertNotIn('images/logo.png', home)
        self.assertNotIn("url('images/bg.jpg')", home)
        self.assertRegex(home, r'srcset="https://cdn\.test/f\d+\.png 1x, https://cdn\.test/f\d+\.png 2x"')
        self.assertIn('src="images/missing.png"', home)        # haipo -> haiguswi
        self.assertEqual(result['missing'], ['images/missing.png'])

        self.assertIn('href="/"', pages['about.html']['document'])
        self.assertIn('href="/p/about/"', pages['blog/index.html']['document'])
        # Faili lisilo na <body> linafunikwa na document kamili
        self.assertIn('<body>', pages['contact.html']['document'])

        # CSS: url() na @import zinaelekezwa kwenye files zilizopakiwa
        css = [d.decode() for u, d in uploaded.items() if u.endswith('.css') and b'body' in d][0]
        self.assertNotIn('../images', css)
        self.assertNotIn('../fonts', css)
        self.assertNotIn('"base.css"', css)

        skipped = dict(result['skipped'])
        self.assertIn('server.php', skipped)
        self.assertEqual(len(skipped), 1)       # takataka za macOS zinarukwa kimya

    def test_unsafe_paths_rejected(self):
        from builder import site_import as si
        for bad in ('../evil.html', '/etc/passwd.html', 'a/../../x.html', 'C:/x.html'):
            with self.assertRaises(si.ImportRejected, msg=bad):
                si.read_zip(_zip({'index.html': 'x', bad: 'x'}))

    def test_not_a_zip_and_no_html(self):
        from builder import site_import as si
        with self.assertRaises(si.ImportRejected):
            si.read_zip(io.BytesIO(b'not a zip'))
        with self.assertRaises(si.ImportRejected):
            si.prepare(_zip({'style.css': 'x'}), _fake_uploader()[0])

    def test_editor_merge_keeps_head_and_scripts(self):
        from builder import site_import as si
        doc = ('<html><head><link rel="stylesheet" href="https://cdn.test/a.css"></head>'
               '<body class="x"><h1>Old</h1><script>go()</script></body></html>')
        self.assertEqual(si.editable_body(doc), '<h1>Old</h1>')
        self.assertIn('a.css', si.canvas_head(doc))

        merged = si.merge_editor_save(doc, '<h1>New</h1>', 'h1{color:red}')
        self.assertIn('<body class="x">', merged)
        self.assertIn('<h1>New</h1>', merged)
        self.assertNotIn('Old', merged)
        self.assertIn('<script>go()</script>', merged)
        self.assertIn('<style id="jt-editor-css">h1{color:red}</style>', merged)
        # Kuhifadhi mara ya pili hakurudufishi CSS wala scripts
        again = si.merge_editor_save(merged, '<h1>New</h1>', 'h1{color:blue}')
        self.assertEqual(again.count('jt-editor-css'), 1)
        self.assertEqual(again.count('go()'), 1)
        self.assertNotIn('jt-editor-css', si.canvas_head(again))


class SiteImportFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('mteja', password='Siri#123456')
        self.site = ClientWebsite.objects.create(
            owner=self.user, subdomain='dukaletu', site_name='Duka Letu', is_published=True)
        self.site.bootstrap_from_schema()
        self.c = Client()
        self.c.login(username='mteja', password='Siri#123456')

    _urls = itertools.count()      # URL mpya kila upakiaji, kama UUID za Supabase

    def _upload(self):
        counter = self._urls

        def fake_upload(data, folder, ext, content_type):
            return {'success': True, 'url': f'https://cdn.test/{folder}/{next(counter)}.{ext}'}
        with mock.patch('apps.storage.is_configured', return_value=True), \
                mock.patch('apps.storage.upload_bytes', side_effect=fake_upload):
            zf = SimpleUploadedFile('site.zip', _zip(SAMPLE_SITE).read(), 'application/zip')
            return self.c.post(f'/builder/site/{self.site.id}/import/', {'zip': zf})

    def test_upload_preview_confirm_render(self):
        r = self._upload()
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Check Your Pages')
        self.assertContains(r, 'server.php')
        token = r.context['token']

        # Kabla ya kuthibitisha, hakuna kilichobadilika
        self.assertFalse(self.site.pages.exclude(raw_document='').exists())

        r = self.c.post(f'/builder/site/{self.site.id}/import/confirm/',
                        {'token': token, 'remove_others': 'on'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(set(self.site.pages.values_list('slug', flat=True)),
                         {'home', 'about', 'contact', 'blog'})
        self.assertTrue(self.site.assets.exists())            # picha kwenye maktaba

        # Site inatolewa kama ilivyo — bila navbar ya JamiiTek
        r = Client().get('/', HTTP_HOST='dukaletu.jamiitek.com')
        html = r.content.decode()
        self.assertTrue(html.startswith('<!DOCTYPE html><html><head><title>Duka Letu'))
        self.assertIn('href="/p/about/"', html)
        r = Client().get('/p/about/', HTTP_HOST='dukaletu.jamiitek.com')
        self.assertContains(r, '<title>About Us</title>')

        # Token imetumika — haiwezi kutumika tena
        r = self.c.post(f'/builder/site/{self.site.id}/import/confirm/', {'token': token})
        self.assertRedirects(r, f'/builder/site/{self.site.id}/import/', fetch_redirect_response=False)

        # Editor inahifadhi body mpya bila kupoteza <head>
        home = self.site.pages.get(slug='home')
        r = self.c.get(f'/builder/site/{self.site.id}/pages/{home.id}/edit/')
        self.assertContains(r, 'canvas-head')
        self.c.post(f'/builder/site/{self.site.id}/pages/{home.id}/save/',
                    json.dumps({'project': {}, 'html': '<h1>Karibu</h1>', 'css': ''}),
                    content_type='application/json')
        html = Client().get('/', HTTP_HOST='dukaletu.jamiitek.com').content.decode()
        self.assertIn('<h1>Karibu</h1>', html)
        self.assertIn('<title>Duka Letu</title>', html)
        self.assertIn('console.log("hi")', html)

    def test_other_owner_cannot_import(self):
        User.objects.create_user('mwingine', password='Siri#123456')
        c = Client()
        c.login(username='mwingine', password='Siri#123456')
        r = c.get(f'/builder/site/{self.site.id}/import/')
        self.assertEqual(r.status_code, 404)

    def test_failed_upload_is_recorded_for_cleanup(self):
        from builder.models import SiteImport
        calls = itertools.count()

        def flaky(data, folder, ext, content_type):
            if next(calls) >= 2:
                return {'success': False, 'error': 'boom'}
            return {'success': True, 'url': f'https://cdn.test/{ext}/{next(calls)}'}
        with mock.patch('apps.storage.is_configured', return_value=True), \
                mock.patch('apps.storage.upload_bytes', side_effect=flaky):
            zf = SimpleUploadedFile('site.zip', _zip(SAMPLE_SITE).read(), 'application/zip')
            r = self.c.post(f'/builder/site/{self.site.id}/import/', {'zip': zf})
        self.assertContains(r, 'Uploading a file failed')
        imp = SiteImport.objects.get(website=self.site)
        self.assertTrue(imp.uploaded)                 # files za kufuta zimerekodiwa
        self.assertEqual(imp.result, {})
        self.assertFalse(self.site.pages.exclude(raw_document='').exists())

    def _prune(self, delete=lambda u: True):
        from django.core.management import call_command
        deleted = []
        with mock.patch('apps.storage.is_configured', return_value=True), \
                mock.patch('apps.storage.delete', side_effect=lambda u: deleted.append(u) or delete(u)):
            call_command('prune_site_imports', quiet=True)
        return deleted

    def _age(self, imp, **kw):
        from datetime import timedelta
        from django.utils import timezone
        from builder.models import SiteImport
        SiteImport.objects.filter(pk=imp.pk).update(**{
            k: timezone.now() - timedelta(days=2) for k in kw})

    def test_prune_deletes_stale_unconfirmed_imports(self):
        from builder.models import SiteImport

        r = self._upload()
        fresh = SiteImport.objects.get(token=r.context['token'])
        stale = SiteImport.objects.create(website=self.site, token='a' * 32,
                                          uploaded=['https://cdn.test/x.png', 'https://cdn.test/y.css'])
        self._age(stale, created_at=1)

        self.assertEqual(sorted(self._prune()), ['https://cdn.test/x.png', 'https://cdn.test/y.css'])
        self.assertFalse(SiteImport.objects.filter(pk=stale.pk).exists())
        self.assertTrue(SiteImport.objects.filter(pk=fresh.pk).exists())   # bado ndani ya saa 24

        # Kufuta kukishindwa, rekodi inabaki kwa jaribio lijalo
        self._age(fresh, created_at=1)
        self._prune(delete=lambda u: False)
        self.assertTrue(SiteImport.objects.get(pk=fresh.pk).uploaded)

    def test_reimport_cleans_up_old_import_only_when_unused(self):
        from builder.models import SiteImport, SiteAsset

        # Import ya kwanza, imethibitishwa
        r = self._upload()
        self.c.post(f'/builder/site/{self.site.id}/import/confirm/', {'token': r.context['token']})
        first = SiteImport.objects.get(token=r.context['token'])
        self._age(first, confirmed_at=1)
        first_urls = set(first.uploaded)

        # Bado inatumika -> haiguswi
        self.assertEqual(self._prune(), [])
        self.assertTrue(SiteImport.objects.filter(pk=first.pk).exists())

        # ZIP mpya inachukua nafasi ya kurasa zote
        r = self._upload()
        self.c.post(f'/builder/site/{self.site.id}/import/confirm/',
                    {'token': r.context['token'], 'remove_others': 'on'})
        second = SiteImport.objects.get(token=r.context['token'])

        # Mteja ameweka picha moja ya zamani kwenye page yake -> import ya zamani yote inabaki
        kept = next(u for u in first_urls if u.endswith('.png'))
        about = self.site.pages.get(slug='about')
        about.raw_document = about.raw_document.replace('</body>', f'<img src="{kept}"></body>')
        about.save()
        self.assertEqual(self._prune(), [])

        # Akiiondoa, import ya zamani inafutwa pamoja na picha zake kwenye maktaba
        about.raw_document = about.raw_document.replace(f'<img src="{kept}">', '')
        about.save()
        self.assertEqual(set(self._prune()), first_urls)
        self.assertFalse(SiteImport.objects.filter(pk=first.pk).exists())
        self.assertFalse(SiteAsset.objects.filter(url__in=first_urls).exists())
        self.assertTrue(SiteAsset.objects.filter(url__in=second.uploaded).exists())
        # Import mpya haiguswi: inatumika, na bado iko ndani ya saa ya neema
        self.assertTrue(SiteImport.objects.filter(pk=second.pk).exists())

    def test_deleting_site_cleans_up_its_imports(self):
        from builder.models import SiteImport
        r = self._upload()
        self.c.post(f'/builder/site/{self.site.id}/import/confirm/', {'token': r.context['token']})
        imp = SiteImport.objects.get(token=r.context['token'])
        urls = set(imp.uploaded)

        self.site.delete()
        imp.refresh_from_db()
        self.assertIsNone(imp.website)              # rekodi imebaki kwa ajili ya prune
        self.assertEqual(set(self._prune()), urls)
        self.assertFalse(SiteImport.objects.filter(pk=imp.pk).exists())


# ══ Website Studio + maktaba ya header/footer ══════════════════

class LayoutLibraryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('mjenzi', password='Siri#123456')
        self.site = ClientWebsite.objects.create(
            owner=self.user, subdomain='dukamjenzi', site_name='Duka & Co', is_published=True,
            contact_phone='+255 712 000 111', whatsapp_number='+255712000111',
            contact_email='hi@duka.co.tz', contact_address='Arusha', tagline='Bei nafuu')
        self.site.bootstrap_from_schema()

    def test_every_design_renders_without_leftover_placeholders(self):
        from builder.layouts import HEADERS, FOOTERS
        from builder.nav_presets import render_nav, render_footer
        self.assertGreaterEqual(len(HEADERS), 10)
        self.assertGreaterEqual(len(FOOTERS), 10)
        for key in HEADERS:
            self.site.nav_preset = key
            html, css = render_nav(self.site, 'home')
            self.assertNotIn('{{', html, key)
            self.assertIn('id="jt-links"', html, key)          # menyu ya simu inafanya kazi
            self.assertIn('Duka &amp; Co', html, key)          # jina lime-escape-iwa
            self.assertIn('.hx-burger', css, key)
            self.assertEqual('.jt-body{margin-left' in css, HEADERS[key]['kind'] == 'side', key)
        for key in FOOTERS:
            self.site.footer_preset = key
            html, css = render_footer(self.site)
            self.assertNotIn('{{', html, key)
            self.assertIn('JamiiTek', html, key)

    def test_new_sites_default_to_sidebar_existing_look_kept(self):
        r = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com')
        html = r.content.decode()
        self.assertIn('hx-side_classic', html)
        self.assertIn('fx-f_columns', html)
        self.assertIn('<body class="has-custom">', html)     # hakuna padding ya glass juu

        # Site ya zamani (nav_preset tupu) inabaki na nav ya glass ya awali
        ClientWebsite.objects.filter(pk=self.site.pk).update(nav_preset='', footer_preset='')
        html = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com').content.decode()
        self.assertIn('class="nav-glass"', html)
        self.assertIn('class="jt-footer"', html)
        self.assertNotIn('hx-side', html)

    def test_font_choice_loads_only_when_chosen(self):
        html = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com').content.decode()
        self.assertNotIn('fonts.googleapis.com', html)        # system: hakuna font ya ziada
        self.site.theme_settings = {'font': 'poppins'}
        self.site.save()
        html = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com').content.decode()
        self.assertIn('family=Poppins', html)


class StudioTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('studio', password='Siri#123456')
        self.site = ClientWebsite.objects.create(owner=self.user, subdomain='studiosite', site_name='Studio Site')
        self.site.bootstrap_from_schema()
        self.c = Client()
        self.c.login(username='studio', password='Siri#123456')
        self.base = f'/builder/site/{self.site.id}/studio/'

    def test_every_step_opens_and_others_are_blocked(self):
        for step in ('business', 'style', 'header', 'footer', 'pages', 'publish'):
            r = self.c.get(f'{self.base}{step}/')
            self.assertEqual(r.status_code, 200, step)
            self.assertNotContains(r, 'scifi-canvas')          # hakuna WebGL — inafunguka haraka
        self.assertEqual(self.c.get(f'{self.base}nope/').status_code, 404)
        other = Client()
        User.objects.create_user('jirani', password='Siri#123456')
        other.login(username='jirani', password='Siri#123456')
        self.assertEqual(other.get(self.base).status_code, 404)

    def test_walk_through_all_steps(self):
        r = self.c.post(f'{self.base}business/', {'site_name': 'Mama Lishe', 'tagline': 'Chakula kitamu',
                                                  'contact_phone': '+255 700 111 222'})
        self.assertRedirects(r, f'{self.base}style/', fetch_redirect_response=False)
        r = self.c.post(f'{self.base}style/', {'accent_color': 'red; }</style>', 'font': 'poppins', 'dark_nav': 'on'})
        self.assertRedirects(r, f'{self.base}header/', fetch_redirect_response=False)
        r = self.c.post(f'{self.base}header/', {'mode': 'preset', 'preset': 'nope'})
        self.assertRedirects(r, f'{self.base}header/', fetch_redirect_response=False)   # design isiyopo
        self.c.post(f'{self.base}header/', {'mode': 'preset', 'preset': 'top_glass'})
        self.c.post(f'{self.base}footer/', {'mode': 'custom', 'html': '<footer>{{site_name}} footer</footer>'})
        self.c.post(f'{self.base}pages/', {})
        self.c.post(f'{self.base}publish/', {})

        self.site.refresh_from_db()
        self.assertEqual(self.site.site_name, 'Mama Lishe')
        self.assertNotIn('style', self.site.accent_color)     # rangi mbaya imekataliwa
        self.assertEqual(self.site.theme_settings['font'], 'poppins')
        self.assertTrue(self.site.dark_nav)
        self.assertEqual(self.site.nav_preset, 'top_glass')
        self.assertIn('{{site_name}} footer', self.site.custom_footer_html)
        self.assertTrue(self.site.is_published)
        self.assertEqual(set(self.site.theme_settings['studio_done']),
                         {'business', 'style', 'header', 'footer', 'pages', 'publish'})

        html = Client().get('/', HTTP_HOST='studiosite.jamiitek.com').content.decode()
        self.assertIn('hx-top_glass', html)
        self.assertIn('Mama Lishe footer', html)

    def test_preview_shows_unsaved_choices_without_saving(self):
        r = self.c.get(f'{self.base}preview/?header=side_midnight&footer=f_mega&accent=%23123456&font=inter')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['X-Frame-Options'], 'SAMEORIGIN')
        self.assertContains(r, 'hx-side_midnight')
        self.assertContains(r, 'fx-f_mega')
        self.assertContains(r, '--accent:#123456')
        r = self.c.post(f'{self.base}preview/', {'header_html': '<nav id="jt-links">MPYA {{site_name}}</nav>'})
        self.assertContains(r, 'MPYA Studio Site')
        self.site.refresh_from_db()
        self.assertEqual(self.site.nav_preset, 'side_classic')     # hakuna kilichohifadhiwa
        self.assertEqual(self.site.custom_nav_html, '')
        self.assertEqual(self.site.accent_color, '#e8a13c')

    def test_dashboard_points_to_next_step(self):
        self.c.post(f'{self.base}business/', {'site_name': 'X'})
        r = self.c.get(f'/builder/site/{self.site.id}/')
        self.assertContains(r, f'{self.base}style/')
        self.assertContains(r, '1/6 done')

    # ── Studio bila kupakia ukurasa upya (fetch + JSON) ──
    def _ajax(self, step, data):
        return self.c.post(f'{self.base}{step}/', data, HTTP_X_REQUESTED_WITH='fetch')

    def test_ajax_save_returns_json_and_never_redirects(self):
        r = self._ajax('header', {'mode': 'preset', 'preset': 'side_midnight'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['ok'], True)
        self.assertIn('header', r.json()['done'])
        r = self._ajax('header', {'mode': 'preset', 'preset': 'nope'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('Pick a header', r.json()['error'])
        # Biashara inarudisha design zilizojazwa upya kwa jina jipya
        r = self._ajax('business', {'site_name': 'Jina & Jipya'})
        self.assertIn('Jina &amp; Jipya', r.json()['layout']['headers']['top_glass']['html'])

    def test_add_page_from_studio_stays_in_studio(self):
        r = self._ajax('pages', {'action': 'add_page', 'title': 'Gallery <b>'})
        self.assertEqual(r.status_code, 200)
        page = r.json()['page']
        self.assertEqual(page['slug'], 'gallery-b')
        self.assertTrue(page['edit'].endswith(f"/pages/{page['id']}/edit/"))
        created = self.site.pages.get(slug='gallery-b')
        self.assertIn('&lt;b&gt;', created.html_cache)          # jina lime-escape-iwa
        self.assertEqual(self._ajax('pages', {'action': 'add_page', 'title': ' '}).status_code, 400)
        # Editor ya ukurasa mpya inafunguka
        self.assertEqual(self.c.get(page['edit']).status_code, 200)

    def test_studio_page_ships_all_designs_and_preview_has_slots(self):
        r = self.c.get(self.base)
        layout = r.context['layout']
        self.assertEqual(len(layout['headers']), 14)
        self.assertEqual(len(layout['footers']), 12)
        self.assertContains(r, 'id="sd-layout"')
        r = self.c.get(f'{self.base}preview/')
        for slot in ('id="jt-nav-slot"', 'id="jt-nav-css"', 'id="jt-foot-slot"', 'id="jt-foot-css"', 'id="jt-font"'):
            self.assertContains(r, slot)

    def test_site_without_pages_gets_pages_and_a_real_preview(self):
        """Site iliyoundwa bila kurasa (Django admin) ilionyesha preview nyeupe na 404."""
        empty = ClientWebsite.objects.create(owner=self.user, subdomain='tupu', site_name='Tupu')
        self.assertFalse(empty.pages.exists())
        # Preview haiwi nyeupe hata kabla ya kurasa kuwepo
        r = self.c.get(f'/builder/site/{empty.id}/studio/preview/?header=side_accent')
        self.assertContains(r, 'hx-side_accent')
        self.assertContains(r, 'Your page content will appear here')
        # Kufungua Studio kunaunda kurasa za aina ya site
        self.c.get(f'/builder/site/{empty.id}/studio/')
        self.assertTrue(empty.pages.filter(slug='home').exists())
        empty.is_published = True
        empty.save()
        self.assertEqual(Client().get('/', HTTP_HOST='tupu.jamiitek.com').status_code, 200)


class BrokenDatabaseTest(TestCase):
    """
    Production: nguzo ya ziada NOT NULL kwenye builder_sitepage ilifanya kila
    INSERT ya ukurasa ishindwe. Kuunda site kulileta 500 na kuacha site nusu
    ("subdomain already taken" ukijaribu tena), na dashboard nayo ikawa 500.
    """
    def setUp(self):
        self.user = User.objects.create_user('mteja2', password='Siri#123456')
        self.c = Client()
        self.c.login(username='mteja2', password='Siri#123456')

    def _boom(self, *a, **k):
        from django.db import IntegrityError
        raise IntegrityError('null value in column "seo_title" violates not-null constraint')

    def test_failed_create_leaves_no_half_site(self):
        with mock.patch('builder.models.ClientWebsite.bootstrap_from_schema', self._boom):
            r = self.c.post('/builder/new/', {'site_name': 'ubungo', 'subdomain': 'sales',
                                              'website_type': 'companyprofile'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'We could not create your website')
        self.assertNotContains(r, 'seo_title')                     # maelezo ya kiufundi: staff tu
        self.assertFalse(ClientWebsite.objects.filter(subdomain='sales').exists())
        # Tatizo likiondoka, subdomain ile ile inafanya kazi
        r = self.c.post('/builder/new/', {'site_name': 'ubungo', 'subdomain': 'sales',
                                          'website_type': 'companyprofile'})
        self.assertEqual(r.status_code, 302)

    def test_dashboard_and_studio_do_not_500_when_pages_cannot_be_created(self):
        site = ClientWebsite.objects.create(owner=self.user, subdomain='nusu', site_name='Nusu')
        with mock.patch('builder.models.ClientWebsite.bootstrap_from_schema', self._boom):
            r = self.c.get(f'/builder/site/{site.id}/')
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'We could not create the pages')
            self.assertEqual(self.c.get(f'/builder/site/{site.id}/studio/').status_code, 200)

    def test_db_check_is_staff_only_and_reports_rollback(self):
        self.assertEqual(self.c.get('/builder/superadmin/db-check/').status_code, 404)
        self.user.is_staff = True
        self.user.save()
        r = self.c.get('/builder/superadmin/db-check/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, '0011_layout_presets')
        self.assertContains(r, 'Imerudishwa nyuma')
        self.assertFalse(ClientWebsite.objects.filter(subdomain='zz-dbcheck-rollback').exists())
        with mock.patch('builder.models.ClientWebsite.bootstrap_from_schema', self._boom):
            r = self.c.get('/builder/superadmin/db-check/')
        self.assertContains(r, 'IMESHINDWA')
        self.assertContains(r, 'seo_title')
