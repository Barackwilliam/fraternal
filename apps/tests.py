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
