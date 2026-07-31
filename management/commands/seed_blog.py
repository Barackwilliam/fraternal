"""
Seed makala ya kwanza ya blog (sampuli). Endesha: python manage.py seed_blog
Inaunda category + makala 1 ya SEO iliyoandaliwa vizuri, tayari kuchapishwa.
"""
from django.core.management.base import BaseCommand
from apps.models import BlogPost, BlogCategory


FIRST_POST_BODY = """
<p>Kama unamiliki biashara Tanzania na bado huna website, unapoteza wateja kila siku. Utafiti unaonyesha kuwa zaidi ya asilimia 80 ya Watanzania hutumia simu kutafuta bidhaa na huduma kabla ya kununua. Kama biashara yako haionekani mtandaoni, wateja wanaenda kwa washindani wako.</p>

<p>Habari njema ni kwamba kutengeneza website leo ni rahisi na nafuu kuliko wakati wowote. Hebu tuone hatua kwa hatua.</p>

<h2>1. Amua lengo la website yako</h2>
<p>Kabla ya kuanza, jiulize: website hii itafanya nini? Je, unataka kuonyesha bidhaa zako? Kupokea maagizo? Kujenga uaminifu? Biashara nyingi Tanzania zinahitaji website inayoonyesha huduma, bei, mahali, na njia ya kuwasiliana (hasa WhatsApp).</p>

<h2>2. Chagua njia ya kutengeneza</h2>
<p>Kuna njia kuu tatu:</p>
<ul>
<li><strong>Website builder (rahisi zaidi):</strong> Unatengeneza mwenyewe kwa kuandika maelezo. Zana kama JamiiTek Builder zinatumia AI kutengeneza website nzima kwa dakika, hata kwa Kiswahili.</li>
<li><strong>Template tayari:</strong> Unachagua muundo uliopo, unabadilisha maelezo yako. Haraka na nafuu.</li>
<li><strong>Custom (mtaalamu anajenga):</strong> Kwa biashara kubwa zinazohitaji vitu maalum.</li>
</ul>

<h2>3. Pata jina la website (domain)</h2>
<p>Jina zuri ni fupi, linalokumbukwa, na linalohusiana na biashara yako. Kwa Tanzania, unaweza kutumia .co.tz au .com. JamiiTek pia inatoa subdomain ya bure (mfano jina-lako.jamiitek.com) kuanzia.</p>

<h2>4. Ongeza maudhui muhimu</h2>
<p>Website nzuri ina: ukurasa wa mwanzo unaovutia, maelezo ya huduma/bidhaa na bei, ukurasa wa "kuhusu sisi", na njia rahisi ya kuwasiliana. Usisahau kuweka namba ya WhatsApp — Watanzania wengi wanapenda kuwasiliana kwa WhatsApp.</p>

<h2>5. Boresha kwa Google (SEO)</h2>
<p>Ili watu wakupate wanapotafuta Google, hakikisha website yako ina maneno muhimu (mfano "duka la nguo Dar es Salaam"), inapakia haraka, na inafanya kazi vizuri kwenye simu.</p>

<h2>6. Ongeza AI WhatsApp bot</h2>
<p>Hii ni siri ya biashara za kisasa: bot inayojibu wateja masaa 24 kwa siku, hata ukiwa umelala. JamiiBot inajibu maswali ya wateja kwa Kiswahili na Kiingereza, inaeleza huduma zako, na haipumziki.</p>

<h2>Hitimisho</h2>
<p>Kutengeneza website Tanzania si jambo gumu tena. Kwa zana sahihi, unaweza kuwa mtandaoni leo. Anza na website rahisi, ongeza AI bot, na ushuhudie biashara yako ikikua. Uko tayari kuanza?</p>
"""


class Command(BaseCommand):
    help = 'Seed makala ya kwanza ya blog'

    def handle(self, *args, **opts):
        cat, _ = BlogCategory.objects.get_or_create(
            slug='web-development',
            defaults={'name': 'Web Development'})

        post, created = BlogPost.objects.get_or_create(
            slug='jinsi-ya-kutengeneza-website-tanzania-2026',
            defaults={
                'title': 'Jinsi ya Kutengeneza Website Tanzania 2026: Mwongozo Kamili',
                'category': cat,
                'excerpt': 'Mwongozo kamili wa kutengeneza website kwa biashara yako Tanzania — kutoka kuchagua njia, kupata domain, hadi kuongeza AI WhatsApp bot. Kwa Kiswahili, hatua kwa hatua.',
                'body': FIRST_POST_BODY.strip(),
                'focus_keyword': 'kutengeneza website Tanzania',
                'meta_description': 'Jifunze jinsi ya kutengeneza website kwa biashara yako Tanzania 2026 — njia rahisi, nafuu, na za haraka. Mwongozo kamili kwa Kiswahili.',
                'author_name': 'JamiiTek',
                'status': 'published',
                'is_featured': True,
            })
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Makala imeundwa: {post.title}'))
        else:
            self.stdout.write('Makala tayari ipo (haijabadilishwa).')
