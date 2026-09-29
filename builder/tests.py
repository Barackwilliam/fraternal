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
