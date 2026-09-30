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

        # 4. Subdomain inaonyesha site iliyopublishiwa tu — hata mmiliki anaona "coming soon"
        r = c.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        html = r.content.decode()
        assert 'coming soon' in html.lower() and 'You are the owner' in html
        assert 'Serengeti Safari' not in html
        # Draft inaonekana kwenye preview ya Studio
        r = c.get(f'/builder/site/{site.id}/studio/preview/')
        assert 'Serengeti Safari' in r.content.decode()
        ClientWebsite.objects.filter(pk=site.pk).update(is_published=True)
        site.refresh_from_db()
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

        # 6. Mgeni anaona coming soon kwa draft site (bila maelezo ya mmiliki)
        site.is_published = False
        site.save()
        c2 = Client()
        r = c2.get('/', HTTP_HOST='kiliadventures.jamiitek.com')
        assert 'coming soon' in r.content.decode().lower()
        assert 'You are the owner' not in r.content.decode()
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

    def test_css_import_url_form_is_resolved(self):
        """`@import url("x.css")` — mtindo wa kawaida zaidi.

        Awali regex ilitambua `@import "x.css"` pekee. CSS iliyoitwa kwa
        url() ilipakiwa BAADA ya inayoiita, ikaripotiwa "haipo", na fonts
        za mteja hazikupakiwa kabisa.
        """
        from builder import site_import as si
        up, uploaded = _fake_uploader()
        files = {
            'index.html': '<html><head><link rel="stylesheet" href="css/main.css"></head><body>x</body></html>',
            # main.css ina url() PEKEE — kama ingekuwa na `@import "x"` pia,
            # ingesubiri kwa bahati na bug isingeonekana.
            'css/main.css': ("@import url('https://fonts.googleapis.com/css2?family=Inter');"
                             '@import url("fonts.css"); @import url(grid.css) screen;'),
            'css/fonts.css': '@import "old.css"; @font-face{src:url(../fonts/x.woff2)}',
            'css/grid.css': '.g{}', 'css/old.css': '.o{}', 'fonts/x.woff2': b'wOF2',
        }
        result = si.prepare(_zip(files), up)
        self.assertEqual(result['missing'], [])
        main = next(v.decode() for v in uploaded.values() if b'googleapis' in v)
        self.assertIn('fonts.googleapis.com', main)            # ya nje haiguswi
        self.assertNotIn('fonts.css', main)                    # zote zimeandikwa upya
        self.assertNotIn('grid.css', main)
        self.assertIn('screen', main)                          # media query imebaki

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
            self.assertIn('hx-m-' + HEADERS[key]['mobile'], html, key)   # mtindo wa menyu ya simu
            self.assertIn('hx-scrim', html, key)
            # Sidebar kwenye laptop: header ya juu yenye links wazi (haikai kushoto, haijifichi)
            self.assertNotIn('.jt-body{margin-left', css, key)
            self.assertEqual('.hx.hx-side nav.hx-menu{flex-direction:row' in css, HEADERS[key]['kind'] == 'side', key)
        for key in FOOTERS:
            self.site.footer_preset = key
            html, css = render_footer(self.site)
            self.assertNotIn('{{', html, key)
            self.assertIn('Duka &amp; Co', html, key)
            # Credit haiko ndani ya footer tena — branding.py inaiweka chini ya ukurasa
            self.assertNotIn('JamiiTek', html, key)

    def test_new_sites_default_to_top_bar_existing_look_kept(self):
        r = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com')
        html = r.content.decode()
        self.assertIn('hx-top_glass', html)
        self.assertIn('fx-f_columns', html)
        self.assertIn('<body class="has-custom">', html)     # hakuna padding ya glass juu

        # Site ya zamani (nav_preset tupu) inabaki na nav ya glass ya awali
        ClientWebsite.objects.filter(pk=self.site.pk).update(nav_preset='', footer_preset='')
        html = Client().get('/', HTTP_HOST='dukamjenzi.jamiitek.com').content.decode()
        self.assertIn('class="nav-glass"', html)
        self.assertIn('class="jt-footer"', html)
        self.assertNotIn('hx-side', html)

    def test_default_sidebars_move_to_top_bar_but_chosen_ones_stay(self):
        import importlib
        from django.apps import apps as django_apps
        mig = importlib.import_module('builder.migrations.0013_default_top_header')
        chosen = ClientWebsite.objects.create(owner=self.user, subdomain='imechaguliwa', site_name='C', nav_preset='side_classic',
                                              theme_settings={'studio_done': ['header']})
        ClientWebsite.objects.filter(pk=self.site.pk).update(nav_preset='side_classic')
        mig.to_top_bar(django_apps, None)
        self.site.refresh_from_db(); chosen.refresh_from_db()
        self.assertEqual(self.site.nav_preset, 'top_glass')
        self.assertEqual(chosen.nav_preset, 'side_classic')

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
        self.assertEqual(self.site.nav_preset, 'top_glass')        # hakuna kilichohifadhiwa
        self.assertEqual(self.site.custom_nav_html, '')
        self.assertEqual(self.site.accent_color, '#e8a13c')

    def test_dashboard_points_to_next_step(self):
        self.c.post(f'{self.base}business/', {'site_name': 'X'})
        r = self.c.get(f'/builder/site/{self.site.id}/')
        self.assertContains(r, f'{self.base}style/')
        self.assertContains(r, '<b>1/6</b><span>Setup steps</span>', html=False)

    def test_dashboard_shows_only_the_five_essentials(self):
        r = self.c.get(f'/builder/site/{self.site.id}/')
        for url in (f'{self.base}', f'/builder/site/{self.site.id}/inquiries/',
                    f'/builder/site/{self.site.id}/import/', '/bot/',
                    f'/builder/site/{self.site.id}/publish/'):
            self.assertContains(r, url)
        # Vilivyohamia Studio havipo tena kwenye dashboard
        for gone in ('Your Pages', 'Design Template', 'Website Details', 'name="custom_domain"',
                     'Getting Started', 'AI Coach', '/collections/'):
            self.assertNotContains(r, gone)

    def test_moved_features_live_in_studio(self):
        r = self.c.get(f'{self.base}pages/')
        self.assertContains(r, 'data-del-page=')
        self.assertContains(r, 'form="tpl-form"')
        r = self.c.get(f'{self.base}publish/')
        self.assertContains(r, 'Your own domain')
        # Kufuta ukurasa kwa fetch: JSON, bila kuondoka Studio; Home hailindwi kufutwa
        team = self.site.pages.get(slug='team')
        r = self.c.post(f'/builder/site/{self.site.id}/pages/{team.id}/delete/', HTTP_X_REQUESTED_WITH='fetch')
        self.assertEqual(r.json(), {'ok': True})
        self.assertFalse(self.site.pages.filter(slug='team').exists())
        home = self.site.pages.get(slug='home')
        r = self.c.post(f'/builder/site/{self.site.id}/pages/{home.id}/delete/', HTTP_X_REQUESTED_WITH='fetch')
        self.assertEqual(r.status_code, 400)
        # Domain kutoka Studio: haizimi dark nav, inarudi kwenye hatua ya Publish
        ClientWebsite.objects.filter(pk=self.site.pk).update(is_premium=True, dark_nav=True)
        with mock.patch('builder.render_api.add_custom_domain', return_value=(True, 'ok')), \
             mock.patch('builder.render_api.check_dns', return_value=False):
            r = self.c.post(f'/builder/site/{self.site.id}/settings/', {'custom_domain': 'www.duka.co.tz'})
        self.assertRedirects(r, f'{self.base}publish/', fetch_redirect_response=False)
        self.site.refresh_from_db()
        self.assertEqual(self.site.custom_domain, 'www.duka.co.tz')
        self.assertTrue(self.site.dark_nav)

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
        self.assertEqual(len(layout['footers']), 16)
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


class MobileMenuTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('simu', password='Siri#123456')
        self.site = ClientWebsite.objects.create(owner=self.user, subdomain='simu', site_name='Simu',
                                                 is_published=True, contact_phone='+255 700 000 000')
        self.site.bootstrap_from_schema()
        self.c = Client()
        self.c.login(username='simu', password='Siri#123456')
        self.base = f'/builder/site/{self.site.id}/studio/'

    def _home(self):
        return Client().get('/', HTTP_HOST='simu.jamiitek.com').content.decode()

    def test_each_header_has_its_own_phone_menu_and_owner_can_change_it(self):
        self.assertIn('hx-m-drop', self._home())                       # top bar ya default → kadi ya dropdown
        r = self.c.post(f'{self.base}header/', {'mode': 'preset', 'preset': 'top_classic', 'mobile_menu': 'tabs'},
                        HTTP_X_REQUESTED_WITH='fetch')
        self.assertEqual(r.status_code, 200)
        html = self._home()
        self.assertIn('hx-m-tabs', html)
        self.assertIn('class="hx-mfoot"><a href="tel:+255700000000">', html)   # njia ya mkato ya kupiga simu
        # Chaguo lisilojulikana → mtindo wa kawaida wa header
        self.c.post(f'{self.base}header/', {'mode': 'preset', 'preset': 'top_glass', 'mobile_menu': 'x"><script>'},
                    HTTP_X_REQUESTED_WITH='fetch')
        self.site.refresh_from_db()
        self.assertEqual(self.site.theme_settings['mobile_menu'], '')
        self.assertIn('hx-m-drop', self._home())

    def test_studio_offers_all_menu_styles_and_preview_applies_them(self):
        r = self.c.get(f'{self.base}header/')
        for key in ('left', 'right', 'sheet', 'drop', 'full', 'tabs'):
            self.assertContains(r, f'name="mobile_menu" value="{key}"')
        self.assertContains(r, 'id="pv-open"')                         # kitufe cha preview kwenye simu
        r = self.c.get(f'{self.base}preview/?header=top_classic&mobile=sheet')
        self.assertContains(r, 'hx-m-sheet')


class BrandingTest(TestCase):
    """"Developed by JamiiTek" iko kwenye kila ukurasa wa mteja na haiwezi kuondolewa."""
    def setUp(self):
        self.user = User.objects.create_user('chapa', password='Siri#123456')
        self.site = ClientWebsite.objects.create(owner=self.user, subdomain='chapa', site_name='Chapa',
                                                 is_published=True)
        self.site.bootstrap_from_schema()

    def _get(self, path='/'):
        return Client().get(path, HTTP_HOST='chapa.jamiitek.com')

    def assertBadge(self, html):
        self.assertEqual(html.count('<jamiitek-badge'), 1)
        self.assertIn('href="https://www.jamiitek.com" target="_blank"', html)
        self.assertIn('display:block!important', html)
        # Iko mwishoni kabisa, baada ya maudhui yote ya mteja
        self.assertLess(html.rindex('<jamiitek-badge'), html.rindex('</body>'))
        self.assertGreater(html.rindex('<jamiitek-badge'), html.rindex('</footer>') if '</footer>' in html else 0)

    def test_builder_pages_custom_footer_and_zip_pages_all_get_the_badge(self):
        self.assertBadge(self._get().content.decode())
        # Footer ya mteja inayojaribu kuificha: inline !important inashinda CSS yake
        self.site.custom_footer_html = '<footer>Yangu</footer><style>jamiitek-badge{display:none!important}</style>'
        self.site.save()
        self.assertBadge(self._get().content.decode())
        # Ukurasa wa ZIP (HTML kamili ya mteja) — hauna nav/footer yetu, lakini alama ipo
        from builder.models import SitePage
        SitePage.objects.create(website=self.site, slug='zip', title='Zip',
                                raw_document='<!doctype html><html><body><h1>Code yangu</h1></body></html>')
        html = self._get('/p/zip/').content.decode()
        self.assertBadge(html)
        self.assertLess(html.index('Code yangu'), html.index('<jamiitek-badge'))

    def test_non_html_and_platform_pages_untouched(self):
        self.assertNotIn(b'jamiitek-badge', self._get('/robots.txt').content)
        self.assertNotIn(b'jamiitek-badge', self._get('/sitemap.xml').content)
        self.assertNotIn(b'jamiitek-badge', Client().get('/builder/signup/').content)

    def test_studio_preview_shows_the_badge(self):
        c = Client()
        c.login(username='chapa', password='Siri#123456')
        r = c.get(f'/builder/site/{self.site.id}/studio/preview/')
        self.assertBadge(r.content.decode())


class PublishRulesTest(TestCase):
    """Kupublish kunahitaji kila hatua ya Studio iwe imehifadhiwa."""
    def setUp(self):
        self.user = User.objects.create_user('pub', password='Siri#123456')
        self.site = ClientWebsite.objects.create(owner=self.user, subdomain='pub', site_name='Pub')
        self.site.bootstrap_from_schema()
        self.c = Client()
        self.c.login(username='pub', password='Siri#123456')
        self.base = f'/builder/site/{self.site.id}/studio/'

    def _ajax(self, step, data=None):
        return self.c.post(f'{self.base}{step}/', data or {}, HTTP_X_REQUESTED_WITH='fetch')

    def test_cannot_publish_until_every_step_is_saved(self):
        r = self._ajax('publish')
        self.assertEqual(r.status_code, 400)
        self.assertIn('Business', r.json()['error'])
        # Dashboard: kitufe cha publish kinampeleka kwenye hatua inayokosekana
        r = self.c.post(f'/builder/site/{self.site.id}/publish/')
        self.assertRedirects(r, f'{self.base}business/', fetch_redirect_response=False)
        self.site.refresh_from_db()
        self.assertFalse(self.site.is_published)
        self.assertContains(self.c.get(f'/builder/site/{self.site.id}/'), 'Finish setup')

        self._ajax('business', {'site_name': 'Pub'})
        self._ajax('style', {'accent_color': '#123456', 'font': 'system'})
        self._ajax('header', {'mode': 'preset', 'preset': 'top_classic'})
        self._ajax('footer', {'mode': 'preset', 'preset': 'f_columns'})
        self.assertEqual(self._ajax('publish').status_code, 400)          # bado kurasa
        self._ajax('pages')
        r = self._ajax('publish')
        self.assertEqual(r.status_code, 200)
        self.site.refresh_from_db()
        self.assertTrue(self.site.is_published)
        # Kuunpublish kunaruhusiwa daima
        self.c.post(f'/builder/site/{self.site.id}/publish/')
        self.site.refresh_from_db()
        self.assertFalse(self.site.is_published)

    def test_zip_only_site_needs_business_and_pages_only(self):
        self.site.pages.all().update(raw_document='<!doctype html><html><body>x</body></html>')
        self._ajax('business', {'site_name': 'Pub'})
        self._ajax('pages')
        self.assertEqual(self._ajax('publish').status_code, 200)

    def test_editor_has_pro_tools_and_previews_drafts(self):
        home = self.site.pages.get(slug='home')
        r = self.c.get(f'/builder/site/{self.site.id}/pages/{home.id}/edit/')
        self.assertContains(r, f'/builder/site/{self.site.id}/studio/preview/?page=home')   # si subdomain
        self.assertNotContains(r, 'https://pub.jamiitek.com')
        for marker in ('id="page-switch"', "bm.add('jb-' + id", 'id="am"', 'componentFirst', 'appendOnClick',
                       'id="canvas-theme"', 'data-scope="sel"', 'show-hint'):
            self.assertContains(r, marker)
        self.assertContains(r, 'Hero — Centered')


class TemplateBridgeTest(TestCase):
    """Templates Marketplace → Builder, na login/usajili wa web builder."""
    def setUp(self):
        from apps.models import WebsiteTemplate
        self.tpl = WebsiteTemplate.objects.create(
            name='Savanna Luxe', category='Tourism', description='Safari site',
            preview_html='<!doctype html><html><head><style>.hero{color:gold}</style></head>'
                         '<body><section class="hero"><h1>Wild Tanzania</h1></section><script>var x=1</script></body></html>')

    def test_visitor_signs_up_then_lands_in_the_editor_with_the_template(self):
        c = Client()
        use = f'/builder/templates/{self.tpl.pk}/use/'
        r = c.get(use)
        self.assertRedirects(r, f'/builder/signup/?next={use}', fetch_redirect_response=False)
        r = c.get(f'/builder/signup/?next={use}')
        self.assertContains(r, 'Savanna Luxe')                     # "unaanza na template hii"
        self.assertNotContains(r, 'name="subdomain"')              # account tu — site inachaguliwa baadaye
        r = c.post('/builder/signup/', {'username': 'mpya', 'email': 'm@x.co', 'password1': 'Siri#123456x',
                                        'password2': 'Siri#123456x', 'next': use})
        self.assertRedirects(r, use, fetch_redirect_response=False)
        r = c.get(use)
        self.assertContains(r, 'savanna-luxe')                     # anwani inayopendekezwa
        r = c.post(use, {'target': 'new', 'site_name': 'Savanna Tours', 'subdomain': 'savannatours'})
        site = ClientWebsite.objects.get(subdomain='savannatours')
        home = site.pages.get(slug='home')
        self.assertRedirects(r, f'/builder/site/{site.id}/pages/{home.id}/edit/', fetch_redirect_response=False)
        self.assertIn('.hero{color:gold}', home.raw_document)      # <head> ya template inabaki
        self.assertIn('Wild Tanzania', home.html_cache)
        self.assertNotIn('<script', home.html_cache)               # editor inapata body bila scripts
        self.assertEqual(site.pages.count(), 1)
        self.assertEqual(site.theme_settings['source_template']['id'], self.tpl.pk)
        # Editor inafunguka, na site ya template inahitaji Business + Pages tu kupublish
        self.assertEqual(c.get(f'/builder/site/{site.id}/pages/{home.id}/edit/').status_code, 200)
        from builder.studio import required_steps
        self.assertEqual(required_steps(site), ['business', 'pages'])
        # Anwani iliyochukuliwa inakataliwa kwa ujumbe wazi
        r = c.post(use, {'target': 'new', 'site_name': 'X', 'subdomain': 'savannatours'})
        self.assertContains(r, 'already taken')

    def test_template_can_replace_home_of_an_existing_site(self):
        user = User.objects.create_user('mwenye', password='Siri#123456')
        site = ClientWebsite.objects.create(owner=user, subdomain='mwenye', site_name='Mwenye')
        site.bootstrap_from_schema()
        c = Client(); c.login(username='mwenye', password='Siri#123456')
        c.post(f'/builder/templates/{self.tpl.pk}/use/', {'target': str(site.id)})
        self.assertIn('Wild Tanzania', site.pages.get(slug='home').raw_document)
        self.assertTrue(site.pages.filter(slug='about').exists())  # kurasa nyingine hazijaguswa
        # Site ya mtu mwingine: 404
        other = ClientWebsite.objects.create(owner=User.objects.create_user('jirani2'), subdomain='jirani2', site_name='J')
        self.assertEqual(c.post(f'/builder/templates/{self.tpl.pk}/use/', {'target': str(other.id)}).status_code, 404)

    def test_builder_login_logout_and_safe_next(self):
        User.objects.create_user('ingia', email='ingia@x.co', password='Siri#123456')
        c = Client()
        r = c.get('/builder/')
        self.assertRedirects(r, '/builder/login/?next=/builder/', fetch_redirect_response=False)
        self.assertEqual(c.get('/builder/login/').status_code, 200)
        r = c.post('/builder/login/', {'username': 'ingia@x.co', 'password': 'Siri#123456', 'next': '/builder/'})
        self.assertRedirects(r, '/builder/', fetch_redirect_response=False)       # email inakubalika
        r = c.post('/builder/logout/')
        self.assertRedirects(r, '/builder/login/', fetch_redirect_response=False)
        r = c.post('/builder/login/', {'username': 'ingia', 'password': 'Siri#123456', 'next': 'https://evil.example/'})
        self.assertRedirects(r, '/builder/', fetch_redirect_response=False)       # si link ya nje

    def test_marketplace_links_every_template_to_the_builder(self):
        r = Client().get('/templates/')
        self.assertContains(r, f'/builder/templates/{self.tpl.pk}/use/')
        self.assertContains(r, 'Safari &amp; Travel website')              # jamii zote zinaonekana
        r = Client().get(f'/templates/preview/{self.tpl.pk}/')
        self.assertContains(r, f'/builder/templates/{self.tpl.pk}/use/')

    def test_jamiibot_page_shows_all_plans_and_two_phone_guide(self):
        from apps.chatbot.models import SubscriptionPlan
        for slug, name, price in (('basic', 'Starter', 5000), ('pro', 'Business', 10000), ('enterprise', 'Enterprise', 15000)):
            SubscriptionPlan.objects.update_or_create(slug=slug, defaults={'name': name, 'price_tzs': price, 'msg_limit': 0})
        r = Client().get('/bot/')
        for price in ('5,000', '10,000', '15,000'):
            self.assertContains(r, f'<div class="price-amount">{price}</div>')
        self.assertContains(r, 'id="setup-guide"')                  # link ya menyu ilielekeza kwenye sehemu isiyokuwepo
        self.assertContains(r, '2 phones')

    def test_empty_collection_hint_is_for_the_owner_only(self):
        user = User.objects.create_user('tupu2', password='Siri#123456')
        site = ClientWebsite.objects.create(owner=user, subdomain='tupu2', site_name='T', is_published=True)
        site.bootstrap_from_schema()
        html = Client().get('/', HTTP_HOST='tupu2.jamiitek.com').content.decode()
        self.assertIn('.jt-empty{display:none!important}', html)
        c = Client(); c.login(username='tupu2', password='Siri#123456')
        self.assertNotContains(c.get(f'/builder/site/{site.id}/studio/preview/'), '.jt-empty{display:none!important}')


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


class InquiryNotifyTest(TestCase):
    """Swali jipya kutoka website -> barua kwa mmiliki.

    Awali swali lilihifadhiwa tu; mmiliki aliliona pale tu alipoingia
    kwenye paneli, na wengi hawaingii kila siku.
    """

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        # Tuma "papo hapo" badala ya kwenye thread, ili barua ionekane ndani
        # ya jaribio. Tunabadilisha notify_owner PEKEE — si threading.Thread,
        # ambayo ingeathiri kila thread ya mfumo (mf. DailyTasksMiddleware).
        from builder import inquiry_notify
        run_now = mock.patch.object(inquiry_notify, 'notify_owner',
                                    side_effect=lambda inq: inquiry_notify._send(inq.pk))
        run_now.start()
        self.addCleanup(run_now.stop)
        self.owner = User.objects.create_user('mmiliki', 'owner@example.com', 'x')
        self.site = ClientWebsite.objects.create(
            owner=self.owner, subdomain='escf', site_name='ESCF Tanzania',
            website_type='ngo', is_published=True, contact_email='info@escf.or.tz')
        self.c = Client()

    def _send(self, **extra):
        data = {'name': 'Juma Hassan', 'phone': '0754 000 111', 'email': 'juma@example.com',
                'message': 'Nataka kuchangia mradi wa tembo.'}
        data.update(extra)
        return self.c.post('/inquiry/', data, HTTP_HOST='escf.localhost')

    def test_owner_gets_email_with_reply_links(self):
        from django.core import mail
        self.assertEqual(self._send().status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(sorted(m.to), ['info@escf.or.tz', 'owner@example.com'])
        self.assertEqual(m.reply_to, ['juma@example.com'])       # "Reply" inaenda kwa mgeni
        self.assertIn('Juma Hassan', m.subject)
        html = m.alternatives[0][0]
        self.assertIn('https://wa.me/255754000111', html)          # 0754… -> 255754…
        self.assertIn('Nataka kuchangia', html)
        self.assertEqual(m.extra_headers.get('X-JT-Category'), 'inquiry')

    def test_no_owner_email_still_saves(self):
        from django.core import mail
        self.site.contact_email = ''
        self.site.save()
        self.owner.email = ''
        self.owner.save()
        self._send()
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(self.site.inquiries.count(), 1)

    def test_hourly_mail_limit(self):
        from django.core import mail
        from builder.inquiry_notify import MAX_PER_HOUR
        for i in range(MAX_PER_HOUR + 3):
            self._send(name=f'Mgeni {i}')
        self.assertEqual(self.site.inquiries.count(), MAX_PER_HOUR + 3)   # maswali YOTE yamehifadhiwa
        self.assertEqual(len(mail.outbox), MAX_PER_HOUR)                  # barua zina kikomo

    def test_bad_date_does_not_crash(self):
        """Tarehe isiyosomeka ilileta Server Error na swali likapotea."""
        for bad in ('31/12/2026', 'kesho', '2026-02-31'):
            self.assertEqual(self._send(preferred_date=bad).status_code, 200)
        self.assertEqual(self.site.inquiries.count(), 3)
        self.assertTrue(all(i.preferred_date is None for i in self.site.inquiries.all()))


class InquiryFormProfileTest(SimpleTestCase):
    """Fomu inafuata aina ya website — NGO haiulizwi idadi ya watu."""

    def _form(self, kind):
        from builder.rendering import render_inquiry_form
        return render_inquiry_form(mock.Mock(website_type=kind))

    def test_ngo_has_no_booking_fields(self):
        html = self._form('ngo')
        self.assertNotIn('preferred_date', html)
        self.assertNotIn('people_count', html)
        self.assertIn('Get in touch', html)

    def test_tourism_and_restaurant_keep_booking_fields(self):
        t = self._form('tourism')
        self.assertIn('Travel date', t)
        self.assertIn('Travellers', t)
        r = self._form('restaurant')
        self.assertIn('Book a table', r)
        self.assertIn('Guests', r)

    def test_unknown_type_is_plain(self):
        html = self._form('')
        self.assertNotIn('preferred_date', html)
        self.assertIn('Send an inquiry', html)
