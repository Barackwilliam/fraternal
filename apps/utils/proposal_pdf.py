# apps/utils/proposal_pdf.py
"""
Mjenzi wa Pendekezo la Mradi (PDF) — toleo la vifurushi vitatu.

MUUNDO:
  Vipengele vyote vya aina ya website vimegawanywa katika madaraja
  matatu (A, B, C) ndani ya website_types/*.json:

      "SEO Setup | 150000 | B"

  Vifurushi ni CUMULATIVE:
      Kifurushi A  =  vipengele vya daraja A
      Kifurushi B  =  A + B
      Kifurushi C  =  A + B + C

  Mteja anapojaza fomu na kuchagua vipengele, tunatafuta daraja la juu
  kabisa alilochagua. Kifurushi hicho ndicho tunachopendekeza — hivyo
  pendekezo linaonyesha vifurushi vitatu na kile kinacholingana naye
  kimewekwa alama "TUNAPENDEKEZA".

  Hii ndiyo mbinu ya pendekezo la Africanberty: mteja anaona chaguo,
  si bei moja tu, na kinachopendekezwa kinatokana na alichoeleza.

MAANDIKO YOTE yako kwenye vigezo hapa chini.
"""

import json
import os
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from xhtml2pdf import pisa


# ══════════════════════════════════════════════════════════════════
# VIGEZO
# ══════════════════════════════════════════════════════════════════

COMPANY = {
    'name':     'JamiiTek Digital Agency',
    'tagline':  'Your Trusted Digital Partner in Tanzania',
    'address':  'Kizota, Dodoma',
    'whatsapp': '+255 750 910 158',
    'email':    'info@jamiitek.com',
    'website':  'www.jamiitek.com',
}

VALIDITY_DAYS = 14

# Vifurushi — jina, maelezo mafupi, muda
PACKAGES = {
    'A': {
        'name':    'KIFURUSHI A — MSINGI',
        'blurb':   'Kwa mwanzo wa haraka',
        'timeline': 'Wiki 2 – 3',
    },
    'B': {
        'name':    'KIFURUSHI B — BIASHARA',
        'blurb':   'Kwa biashara inayokua',
        'timeline': 'Wiki 4 – 5',
    },
    'C': {
        'name':    'KIFURUSHI C — PREMIUM',
        'blurb':   'Kwa ukuaji wa muda mrefu',
        'timeline': 'Wiki 6 – 8',
    },
}
TIER_ORDER = ['A', 'B', 'C']

PAYMENT_SPLIT = [
    ('60%', 'Unapokubali pendekezo na kusaini mkataba — kazi inaanza siku hiyo hiyo'),
    ('40%', 'Kabla ya kukabidhiwa mfumo kamili'),
]
PAYMENT_NOTE = ('Malipo yanafanyika kwa akaunti rasmi ya JamiiTek na risiti '
                'hutolewa kwa kila malipo.')

CLIENT_INPUTS = [
    'Jina rasmi la mradi na maudhui utakayotaka yaonekane',
    'Logo — kama huna, tunaweza kukutengenezea',
    'Email rasmi na namba ya simu ya biashara',
    'Picha na taarifa za bidhaa au huduma zako',
    'Nyaraka za usajili kama mradi unahitaji malipo mtandaoni (BRELA, TIN, akaunti ya benki)',
]

GUARANTEES = [
    'Msimbo (source code) wote unakuwa mali yako baada ya malipo kukamilika',
    'Miezi 6 ya usimamizi na kurekebisha makosa bila malipo',
    'Mafunzo ya matumizi ya mfumo — kikao kimoja, mtandaoni au ana kwa ana',
    'Kusaidiwa kupakia mfumo na kuunganisha domain yako',
    'Mawasiliano ya moja kwa moja na timu yetu wakati wote wa mradi',
]

TERMS = [
    ('Upeo wa kazi',
     'Pendekezo hili linahusu vipengele vya kifurushi utakachochagua pekee. Kazi ya '
     'ziada itakadiriwa na kukubaliwa kwa maandishi kabla haijaanza.'),
    ('Uhalali',
     f'Pendekezo hili ni halali kwa siku {VALIDITY_DAYS} tangu tarehe lilipotolewa. '
     'Bei zinaweza kubadilika baada ya muda huo.'),
    ('Muda wa kazi',
     'Ratiba inakubaliwa kwa maandishi mara malipo ya awali yanapopokelewa. Kuchelewa '
     'kwa maudhui au majibu kutoka kwa mteja kunasogeza ratiba mbele.'),
    ('Umiliki',
     'Baada ya malipo kukamilika, mteja anamiliki mfumo, muundo na maudhui yaliyokabidhiwa. '
     'Leseni za watu wa tatu, hosting na domain zinafuata masharti yao.'),
    ('Usiri',
     'Pande zote mbili zinakubaliana kutunza siri taarifa za kibiashara na kiufundi '
     'zitakazoshirikiwa wakati wa mradi.'),
    ('Sheria',
     'Pendekezo hili na mkataba wowote utakaotokana nalo vinaongozwa na sheria za '
     'Jamhuri ya Muungano wa Tanzania. Migogoro itatatuliwa kwa mazungumzo, na '
     'ikishindikana, kwa usuluhishi Dodoma.'),
]

T = {
    'doc_kind':     'PENDEKEZO LA MRADI',
    'prepared_for': 'Kwa',
    'project':      'Mradi',
    'prepared_by':  'Imeandaliwa na',
    'date':         'Tarehe',
    'number':       'Namba',
    'validity':     'Uhalali',
    'days':         'Siku',
    'greeting_h':   'Asante kwa kutupa nafasi ya kufanya kazi na wewe',
    'greeting_p':   ('Tumefurahi kupokea ombi lako. Pendekezo hili linaeleza '
                     'tutakachokujengea, vifurushi vilivyopo, gharama zake, na '
                     'masharti ya kazi. Tupo tayari kuanza mara tu utakapokuwa tayari.'),
    's1':           'Uelewa wetu wa mahitaji yako',
    's1_intro':     'Kutokana na taarifa ulizotupa, tumeelewa unahitaji:',
    's2':           'Vifurushi na gharama',
    's2_intro':     ('Tumeandaa vifurushi vitatu ili uchague kinachoendana na bajeti yako '
                     'na hatua uliyopo sasa.'),
    's3':           'Maelezo ya ziada uliyotoa',
    's4':           'Masharti ya malipo',
    's5':           'Tunachohitaji kutoka kwako',
    's6':           'Tunachokuhakikishia',
    's7':           'Masharti ya jumla',
    'next_h':       'Hatua inayofuata',
    'next_p':       ('Chagua kifurushi unachotaka, kisha tutakutumia mkataba rasmi na '
                     'invoice ya malipo ya awali. Kazi inaanza mara tu malipo '
                     'yanapothibitishwa.'),
    'next_cta':     'Karibu ofisini kwetu Kizota, Dodoma, au tuwasiliane kwa WhatsApp',
    'recommended':  'TUNAPENDEKEZA',
    'rec_why':      'Kinaendana na mahitaji uliyoeleza',
    'plus_prev':    'Kila kitu cha kifurushi kilichotangulia, pamoja na:',
    'timeline':     'Muda',
    'included':     'Kimejumuishwa',
    'no_items':     ('Hakuna vipengele vyenye bei vilivyopatikana kwa aina hii ya mradi. '
                     'Timu yetu itawasiliana nawe ili kukadiria mradi moja kwa moja.'),
    'ref_design':   'Muundo wa kuigwa',
    'sign_us':      'Kwa niaba ya JamiiTek',
    'sign_client':  'Mteja',
    'sign_cap':     'Jina / Sahihi / Tarehe',
    'page':         'Ukurasa',
    'of':           'kati ya',
    'price_note':   ('Bei zilizoonyeshwa ni makadirio. Bei ya mwisho inathibitishwa kwa '
                     'maandishi kabla kazi haijaanza. Gharama za hosting, domain na leseni '
                     'za watu wa tatu zinalipwa tofauti.'),
}


# ══════════════════════════════════════════════════════════════════
# KUSOMA NA KUGAWA
# ══════════════════════════════════════════════════════════════════

def parse_option(raw):
    """'SEO Setup | 150000 | B' -> ('SEO Setup', 150000, 'B')."""
    parts = [p.strip() for p in str(raw).split('|')]

    if len(parts) >= 3 and parts[-1].upper() in ('A', 'B', 'C'):
        tier = parts[-1].upper()
        price_part = parts[-2]
        name = '|'.join(parts[:-2]).strip()
    elif len(parts) >= 2:
        tier = 'A'
        price_part = parts[-1]
        name = '|'.join(parts[:-1]).strip()
    else:
        return parts[0], 0, 'A'

    digits = ''.join(ch for ch in price_part if ch.isdigit())
    price = int(digits) if digits else 0
    return name, price, tier


def load_type_schema(website_type_name):
    """Soma website_types/<jina>.json kwa mtindo uleule wa forms.py."""
    base = Path(settings.BASE_DIR)
    safe = str(website_type_name).lower().replace(' ', '').replace('-', '')
    path = base / 'website_types' / f'{safe}.json'

    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def build_packages(schema):
    """
    Rudisha list ya vifurushi vitatu, kila kimoja na vipengele vyake
    NA jumla ya cumulative.
    """
    by_tier = {'A': [], 'B': [], 'C': []}

    for key, field in schema.items():
        if not isinstance(field, dict) or field.get('type') != 'checkbox':
            continue
        label = key.replace('_', ' ').strip().title()

        for raw in field.get('options', []) or []:
            name, price, tier = parse_option(raw)
            if tier not in by_tier:
                tier = 'A'
            by_tier[tier].append({
                'group': label,
                'name':  name,
                'price': price,
                'price_display': f'{price:,}' if price else T['included'],
            })

    packages, running_total = [], 0
    for i, tier in enumerate(TIER_ORDER):
        items = by_tier[tier]
        running_total += sum(it['price'] for it in items)

        packages.append({
            'tier':          tier,
            'name':          PACKAGES[tier]['name'],
            'blurb':         PACKAGES[tier]['blurb'],
            'timeline':      PACKAGES[tier]['timeline'],
            'items':         items,
            'is_cumulative': i > 0,
            'total':         running_total,
            'total_display': f'{running_total:,}',
        })

    return packages


def read_selection(requirements):
    """
    Rudisha (summary, notes, recommended_tier) kutoka alichochagua mteja.

    recommended_tier = daraja la juu kabisa alilochagua. Kwa kuwa vifurushi
    ni cumulative, kifurushi hicho kinajumuisha kila alichotaka.
    """
    summary, notes = [], []
    highest = 'A'

    if not isinstance(requirements, dict):
        return [], [], 'A'

    for key, value in requirements.items():
        if key in ('reference_template', 'turnstile', 'csrfmiddlewaretoken'):
            continue
        if key.startswith('client_'):
            continue

        label = key.replace('_', ' ').strip().title()

        if isinstance(value, (list, tuple)):
            for raw in value:
                name, _price, tier = parse_option(raw)
                summary.append(name)
                if TIER_ORDER.index(tier) > TIER_ORDER.index(highest):
                    highest = tier
        else:
            text = str(value).strip() if value not in (None, '') else ''
            if text:
                notes.append({'label': label, 'text': text})

    return summary, notes, highest


# ══════════════════════════════════════════════════════════════════
# STATIC
# ══════════════════════════════════════════════════════════════════

def link_callback(uri, rel):
    """xhtml2pdf haijui URLs za Django — geuza /static/... kuwa path ya diski."""
    if uri.startswith('http://') or uri.startswith('https://'):
        return uri

    if uri.startswith(settings.STATIC_URL):
        path = uri.replace(settings.STATIC_URL, '', 1)
        found = finders.find(path)
        if found:
            return found if isinstance(found, str) else found[0]
        if getattr(settings, 'STATIC_ROOT', None):
            candidate = os.path.join(settings.STATIC_ROOT, path)
            if os.path.isfile(candidate):
                return candidate

    media_url = getattr(settings, 'MEDIA_URL', None)
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_url and media_root and uri.startswith(media_url):
        candidate = os.path.join(media_root, uri.replace(media_url, '', 1))
        if os.path.isfile(candidate):
            return candidate

    return uri


# ══════════════════════════════════════════════════════════════════
# MJENZI
# ══════════════════════════════════════════════════════════════════

def generate_proposal_pdf(proposal):
    """Rudisha bytes za PDF, au None kama rendering imeshindwa."""
    requirements = proposal.requirements
    if isinstance(requirements, str):
        try:
            requirements = json.loads(requirements)
        except Exception:
            requirements = {}
    if not isinstance(requirements, dict):
        requirements = {}

    schema = load_type_schema(proposal.website_type.name)
    packages = build_packages(schema)
    summary, notes, recommended = read_selection(requirements)

    for pkg in packages:
        pkg['recommended'] = (pkg['tier'] == recommended)

    context = {
        'proposal':      proposal,
        'company':       COMPANY,
        't':             T,
        'packages':      packages,
        'summary':       summary,
        'notes':         notes,
        'ref_template':  requirements.get('reference_template'),
        'doc_number':    f'JT/{proposal.id:04d}/{proposal.created_at.strftime("%Y")}',
        'validity_days': VALIDITY_DAYS,
        'payment_split': PAYMENT_SPLIT,
        'payment_note':  PAYMENT_NOTE,
        'client_inputs': CLIENT_INPUTS,
        'guarantees':    GUARANTEES,
        'terms':         TERMS,
    }

    html = render_to_string('proposal_pdf.html', context)
    result = BytesIO()
    status = pisa.CreatePDF(html, dest=result, link_callback=link_callback)

    if status.err:
        return None
    return result.getvalue()