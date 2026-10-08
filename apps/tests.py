import json
import re
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings

from .models import WebsiteTemplate, WebsiteType, ProjectProposal


class NoPingMixin:
    """IndexNow isijaribu mtandao wakati wa tests (setUp pia inahifadhi templates)."""
    def setUp(self):
        p = mock.patch('apps.indexnow.ping')
        p.start()
        self.addCleanup(p.stop)
        super().setUp()


def _tpl(**kw):
    data = dict(name='Savanna Luxe', category='Tourism', description='A luxury safari website with tours and booking.',
                preview_html='<!doctype html><html><body><h1>Wild Tanzania</h1></body></html>')
    data.update(kw)
    return WebsiteTemplate.objects.create(**data)


class TemplateSeoTest(NoPingMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.tpl = _tpl()

    def test_slug_is_generated_unique_and_avoids_reserved_paths(self):
        self.assertEqual(self.tpl.slug, 'savanna-luxe')
        self.assertEqual(_tpl().slug, 'savanna-luxe-2')
        self.assertEqual(_tpl(name='Preview').slug, 'preview-template')
        self.assertEqual(self.tpl.get_absolute_url(), '/templates/savanna-luxe/')

    def test_detail_page_has_unique_meta_real_text_and_json_ld(self):
        r = self.client.get('/templates/savanna-luxe/')
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        self.assertIn('<title>Savanna Luxe — Safari &amp; Travel Website Template | JamiiTek</title>', html)
        self.assertIn('<link rel="canonical" href="https://www.jamiitek.com/templates/savanna-luxe/">', html)
        self.assertIn('<h1>Savanna Luxe', html)
        self.assertIn('Kwa Kiswahili', html)                 # maandishi ya Kiswahili pia
        self.assertIn('/builder/templates/%d/use/' % self.tpl.pk, html)
        self.assertIn('/proposals/?template=%d' % self.tpl.pk, html)
        blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        types = [b.get('@type') for b in blocks]
        for t in ('Product', 'BreadcrumbList', 'FAQPage'):
            self.assertIn(t, types)
        product = next(b for b in blocks if b.get('@type') == 'Product')
        self.assertEqual(product['offers'][0]['price'], '0')
        self.assertNotIn('aggregateRating', product)       # hakuna rating za kubuni

    def test_inactive_or_unknown_template_is_404(self):
        _tpl(name='Hidden', is_active=False)
        self.assertEqual(self.client.get('/templates/hidden/').status_code, 404)
        self.assertEqual(self.client.get('/templates/nope/').status_code, 404)

    def test_old_urls_still_work_and_point_google_to_the_new_page(self):
        r = self.client.get(f'/templates/preview/{self.tpl.pk}/')
        self.assertContains(r, '<link rel="canonical" href="https://www.jamiitek.com/templates/savanna-luxe/">', html=False)
        raw = self.client.get(f'/templates/preview/{self.tpl.pk}/raw/')
        self.assertEqual(raw['X-Robots-Tag'], 'noindex, follow')

    def test_category_page_and_crawlable_chips(self):
        _tpl(name='Mama Lishe', category='restaurant')
        r = self.client.get('/templates/c/tourism/')
        self.assertContains(r, 'Safari &amp; Travel Website Templates')
        self.assertContains(r, 'Savanna Luxe')
        self.assertNotContains(r, 'Mama Lishe</a></h3>')
        self.assertContains(r, '"@type": "ItemList"')
        self.assertEqual(self.client.get('/templates/c/unknown/').status_code, 404)
        m = self.client.get('/templates/')
        self.assertContains(m, 'href="/templates/c/restaurant/"')
        self.assertContains(m, 'href="/templates/savanna-luxe/"')

    def test_sitemap_llms_and_robots(self):
        sm = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('/templates/savanna-luxe/', sm)
        self.assertIn('/templates/c/tourism/', sm)
        self.assertIn('/templates/</loc>', sm)
        llms = self.client.get('/llms.txt').content.decode()
        self.assertIn('# JamiiTek', llms)
        self.assertIn('[Savanna Luxe — safari & travel website template](https://www.jamiitek.com/templates/savanna-luxe/)', llms)
        robots = self.client.get('/robots.txt').content.decode()
        self.assertIn('User-agent: GPTBot', robots)
        self.assertIn('llms.txt', robots)
        # Kurasa zenye noindex zisizuiwe, la sivyo Google haioni noindex
        self.assertNotIn('Disallow: /portal/', robots)
        self.assertNotIn('/raw/', robots)
        self.assertIn('Disallow: /manage/', robots)
        self.assertEqual(self.client.get('/portal/register/')['X-Robots-Tag'], 'noindex, follow')

    def test_saving_a_template_pings_indexnow(self):
        with mock.patch('apps.indexnow.ping') as ping:
            self.tpl.save()
        self.assertIn('/templates/savanna-luxe/', ping.call_args[0][0])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ProposalFlowTest(NoPingMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.tpl = _tpl()
        self.wt = WebsiteType.objects.create(name='Company Profile', description='For companies', icon='fas fa-briefcase')

    def test_step_one_links_templates_and_proposal(self):
        r = self.client.get('/proposals/')
        self.assertContains(r, 'We’ll design it for you')
        self.assertContains(r, f'/proposals/form/{self.wt.pk}/')
        self.assertContains(r, f'/proposals/?template={self.tpl.pk}')
        r = self.client.get(f'/proposals/?template={self.tpl.pk}')
        self.assertContains(r, 'Your starting design')
        self.assertContains(r, f'/proposals/form/{self.wt.pk}/?template={self.tpl.pk}')

    def test_submitting_a_proposal_emails_jamiitek_and_confirms(self):
        from .forms import DynamicProposalForm
        form = DynamicProposalForm(self.wt.name)
        data = {'reference_template': self.tpl.pk}
        for name, field in form.fields.items():
            if name == 'turnstile':
                continue
            if name == 'client_email':
                data[name] = 'asha@example.com'
            elif getattr(field, 'choices', None):
                data[name] = [str(field.choices[0][0])] if field.widget.allow_multiple_selected else str(field.choices[0][0])
            else:
                data[name] = 'Asha' if name.startswith('client_') else 'Some text'
        with mock.patch('threading.Thread') as T:
            T.side_effect = lambda target, daemon: mock.Mock(start=target)
            r = self.client.post(f'/proposals/form/{self.wt.pk}/', data)
        p = ProjectProposal.objects.get()
        self.assertRedirects(r, f'/proposals/preview/{p.pk}/?sent=1')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(f'JT-{p.pk}', mail.outbox[0].subject)
        self.assertIn('Savanna Luxe', mail.outbox[0].alternatives[0][0])
        self.assertEqual(p.requirements['reference_template']['preview_url'], '/templates/savanna-luxe/')
        self.assertContains(self.client.get(r['Location']), 'Sent to JamiiTek')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NewsletterTest(TestCase):
    """Fomu ya footer ilituma email peke yake kwenda /contact/ na kupata
    "Please fill in all fields". Sasa ina njia yake."""
    url = '/newsletter/subscribe/'

    def test_ajax_subscribe_sends_notice(self):
        r = self.client.post(self.url, {'email': 'neema@biashara.co.tz'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()['ok'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('neema@biashara.co.tz', mail.outbox[0].body)

    def test_invalid_email_rejected(self):
        r = self.client.post(self.url, {'email': 'si-email'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.json()['ok'])
        self.assertEqual(len(mail.outbox), 0)

    def test_without_js_redirects_back_with_status(self):
        r = self.client.post(self.url, {'email': 'juma@example.com'}, HTTP_REFERER='http://testserver/About/?x=1')
        self.assertRedirects(r, '/About/?subscribed=ok#site-footer', fetch_redirect_response=False)

    def test_foreign_referer_is_not_followed(self):
        r = self.client.post(self.url, {'email': 'juma@example.com'}, HTTP_REFERER='https://evil.example/')
        self.assertEqual(r['Location'], '/?subscribed=ok#site-footer')

    def test_honeypot_drops_silently(self):
        r = self.client.post(self.url, {'email': 'bot@spam.com', 'company_website': 'x'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(r.json()['ok'])
        self.assertEqual(len(mail.outbox), 0)

    def test_get_redirects_home(self):
        self.assertRedirects(self.client.get(self.url), '/', fetch_redirect_response=False)


class SpotlightTest(TestCase):
    """JamiiTek Spotlight: makala 1 kuhusu JamiiTek Jumatatu/Jumatano/Jumamosi."""

    def setUp(self):
        from datetime import datetime
        from django.utils import timezone as tz
        self.monday = tz.make_aware(datetime(2026, 10, 5, 6, 0))     # Jumatatu
        self.tuesday = tz.make_aware(datetime(2026, 10, 6, 6, 0))    # Jumanne
        self.n = 0

    def _fake_write(self, titles):
        it = iter(titles)
        def write(topic_name, facts, angle_text, previous, avoid):
            self.n += 1
            t = next(it)
            return True, {'title': t, 'slug': t.lower().replace(' ', '-'), 'excerpt': 'x', 'body': '<p>Body</p>',
                          'meta_title': t[:60], 'meta_description': 'd', 'focus_keyword': 'k', 'tags': 'a'}
        return write

    def _run(self, when, titles, **kw):
        from apps import spotlight_blog as sb
        with mock.patch.object(sb.timezone, 'localtime', return_value=when), \
             mock.patch('django.utils.timezone.now', return_value=when), \
             mock.patch.object(sb, 'write', side_effect=self._fake_write(titles)), \
             mock.patch('apps.news_blog.unsplash_cover', return_value=''):
            return sb.run(**kw)

    def test_only_on_spotlight_days(self):
        r = self._run(self.tuesday, ['Should not be written'])
        self.assertEqual(r['created'], [])
        self.assertIn('not a spotlight day', r['skipped'])
        self.assertEqual(self.n, 0)

    def test_writes_one_draft_on_monday_then_stops(self):
        r = self._run(self.monday, ['How JamiiBot Answers Customers at 2am'])
        self.assertEqual(len(r['created']), 1)
        post = r['created'][0]
        self.assertEqual(post.status, 'draft')
        self.assertEqual(post.category.slug, 'jamiitek-spotlight')
        self.assertTrue(post.source_name.startswith('spotlight:'))
        again = self._run(self.monday, ['Another One'])
        self.assertEqual(again['created'], [])
        self.assertEqual(again['skipped'], 'already wrote today')

    def test_topic_and_angle_never_repeat(self):
        from apps.models import BlogPost
        keys = set()
        heads = ['How JamiiBot Answers Customers at 2am', 'Choosing Between .co.tz and .com',
                 'Five Mistakes Shops Make With Their First Website', 'Inside Our Daily Backup Routine',
                 'What Safari Companies Need From a Booking Page', 'Mobile Money Checkout Explained Simply']
        for i in range(6):
            r = self._run(self.monday, [heads[i]], force=True)
            self.assertEqual(len(r['created']), 1, r)
            keys.add(r['created'][0].source_name)
        self.assertEqual(len(keys), 6)
        self.assertEqual(BlogPost.objects.filter(source_name__startswith='spotlight:').count(), 6)

    def test_similar_title_is_rejected_and_retried(self):
        from apps.models import BlogPost
        BlogPost.objects.create(title='Why Every Dar Shop Needs a WhatsApp Bot', slug='why-bot',
                                excerpt='x', body='<p>x</p>')
        r = self._run(self.monday, ['Why every Dar shop needs a WhatsApp bot!',
                                    'Five Questions Shop Owners Ask About Online Orders'])
        self.assertEqual(self.n, 2)
        self.assertEqual(r['created'][0].title, 'Five Questions Shop Owners Ask About Online Orders')

    def test_gives_up_without_unique_title(self):
        from apps.models import BlogPost
        BlogPost.objects.create(title='Same Title', slug='same', excerpt='x', body='<p>x</p>')
        r = self._run(self.monday, ['Same Title', 'same title', 'Same  Title.'])
        self.assertEqual(r['created'], [])
        self.assertEqual(self.n, 3)

    def test_autopublish_flag(self):
        with mock.patch.dict('os.environ', {'SPOTLIGHT_AUTOPUBLISH': '1'}):
            r = self._run(self.monday, ['A Practical Guide to .co.tz Domains'])
        self.assertEqual(r['created'][0].status, 'published')


class SiteSeoTest(NoPingMixin, TestCase):
    """SEO ya kurasa kuu: hakuna rating za kubuni, /bot/ ina canonical na schema."""

    def _ld(self, html):
        out = []
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            j = json.loads(b)
            out.extend(j if isinstance(j, list) else [j])
        return out

    def test_no_fake_ratings_anywhere(self):
        for url in ('/', '/bot/', '/service/', '/About/', '/contact/', '/get-started/'):
            html = self.client.get(url).content.decode()
            self.assertNotIn('aggregateRating', html, url)

    def test_bot_landing_has_canonical_og_and_schema(self):
        html = self.client.get('/bot/').content.decode()
        self.assertIn('<link rel="canonical" href="https://www.jamiitek.com/bot/">', html)
        self.assertIn('property="og:image"', html)
        types = [b.get('@type') for b in self._ld(html)]
        self.assertIn('SoftwareApplication', types)
        self.assertIn('BreadcrumbList', types)

    def test_key_pages_have_schema_and_tanzania_titles(self):
        for url, kind in (('/About/', 'AboutPage'), ('/contact/', 'ContactPage'), ('/get-started/', 'FAQPage')):
            html = self.client.get(url).content.decode()
            self.assertIn(kind, [b.get('@type') for b in self._ld(html)], url)
            title = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
            self.assertIn('Tanzania', title, url)

    def test_sitemap_lists_get_started_once_and_service_once(self):
        xml = self.client.get('/sitemap.xml').content.decode()
        locs = [re.sub(r'^https?://[^/]+', '', u) for u in re.findall(r'<loc>([^<]*)</loc>', xml)]
        self.assertIn('/get-started/', locs)
        self.assertEqual(locs.count('/service/'), 1)


class OneAccountTest(NoPingMixin, TestCase):
    """Akaunti moja: Web Builder ↔ Client Portal ↔ JamiiBot (apps/accounts_link.py)."""

    def setUp(self):
        super().setUp()
        from django.contrib.auth.models import User
        self.user = User.objects.create_user('neema', 'neema@example.com', 'Kilimo2026!')

    def test_builder_account_signs_in_to_client_portal(self):
        from apps.models import Client
        r = self.client.post('/portal/login/', {'username': 'neema', 'password': 'Kilimo2026!'})
        self.assertRedirects(r, '/portal/', fetch_redirect_response=False)
        c = Client.objects.get(user=self.user)
        self.assertEqual(c.email, 'neema@example.com')
        self.assertEqual(self.client.get('/portal/').status_code, 200)

    def test_portal_login_accepts_email_and_blocks_external_next(self):
        r = self.client.post('/portal/login/', {'username': 'NEEMA@example.com', 'password': 'Kilimo2026!',
                                                'next': '//evil.example/x'})
        self.assertRedirects(r, '/portal/', fetch_redirect_response=False)

    def test_builder_account_signs_in_to_jamiibot(self):
        from apps.chatbot.models import ChatbotClient
        r = self.client.post('/chatbot/login/', {'username': 'neema@example.com', 'password': 'Kilimo2026!'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(ChatbotClient.objects.filter(user=self.user).exists())

    def test_already_signed_in_goes_straight_to_bot(self):
        self.client.force_login(self.user)
        r = self.client.get('/chatbot/login/')
        self.assertRedirects(r, '/chatbot/dashboard/', fetch_redirect_response=False)

    def test_switcher_on_all_three_apps(self):
        self.client.force_login(self.user)
        for url in ('/portal/', '/builder/'):
            html = self.client.get(url).content.decode()
            self.assertIn('Switch app', html, url)
            for href in ('href="/portal/"', 'href="/chatbot/dashboard/"', 'href="/builder/"'):
                self.assertIn(href, html, url)
