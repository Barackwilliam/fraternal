from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import USSDConfig

# ============================================================
# DATA
# ============================================================

REGIONS = {
    '1': {
        'name': 'Kagera',
        'districts': {
            '1': 'Bukoba', '2': 'Muleba', '3': 'Karagwe',
            '4': 'Ngara', '5': 'Misenyi', '6': 'Kyerwa',
        }
    },
    '2': {
        'name': 'Kilimanjaro',
        'districts': {
            '1': 'Moshi', '2': 'Hai', '3': 'Mwanga',
            '4': 'Same', '5': 'Rombo', '6': 'Siha',
        }
    },
    '3': {
        'name': 'Arusha',
        'districts': {
            '1': 'Arusha', '2': 'Meru', '3': 'Monduli',
            '4': 'Ngorongoro', '5': 'Longido', '6': 'Karatu',
        }
    },
    '4': {
        'name': 'Mbeya',
        'districts': {
            '1': 'Mbeya', '2': 'Rungwe', '3': 'Chunya',
            '4': 'Kyela', '5': 'Momba', '6': 'Songwe',
        }
    },
    '5': {
        'name': 'Iringa',
        'districts': {
            '1': 'Iringa', '2': 'Kilolo', '3': 'Mufindi',
            '4': 'Ludewa', '5': 'Makete',
        }
    },
    '6': {
        'name': 'Morogoro',
        'districts': {
            '1': 'Morogoro', '2': 'Kilosa', '3': 'Mvomero',
            '4': 'Gairo', '5': 'Kilombero', '6': 'Ulanga',
        }
    },
    '7': {
        'name': 'Dar es Salaam',
        'districts': {
            '1': 'Ilala', '2': 'Kinondoni', '3': 'Temeke',
            '4': 'Ubungo', '5': 'Kigamboni',
        }
    },
    '8': {
        'name': 'Mwanza',
        'districts': {
            '1': 'Ilemela', '2': 'Nyamagana', '3': 'Misungwi',
            '4': 'Magu', '5': 'Sengerema', '6': 'Kwimba',
        }
    },
    '9': {
        'name': 'Dodoma',
        'districts': {
            '1': 'Dodoma', '2': 'Bahi', '3': 'Chamwino',
            '4': 'Kondoa', '5': 'Mpwapwa',
        }
    },
    '10': {
        'name': 'Tanga',
        'districts': {
            '1': 'Tanga', '2': 'Lushoto', '3': 'Korogwe',
            '4': 'Muheza', '5': 'Pangani', '6': 'Handeni',
        }
    },
}

CROPS = {
    '1': 'Maharagwe',
    '2': 'Kahawa',
    '3': 'Mahindi',
    '4': 'Parachichi',
    '5': 'Ndizi',
}

PRICES = {
    # Kagera
    'Bukoba':    {'Maharagwe': '2,800', 'Kahawa': '5,500', 'Mahindi': '850',   'Parachichi': '1,200', 'Ndizi': '600'},
    'Muleba':    {'Maharagwe': '2,600', 'Kahawa': '5,200', 'Mahindi': '800',   'Parachichi': '1,100', 'Ndizi': '550'},
    'Karagwe':   {'Maharagwe': '2,700', 'Kahawa': '5,300', 'Mahindi': '820',   'Parachichi': '1,150', 'Ndizi': '580'},
    'Ngara':     {'Maharagwe': '2,500', 'Kahawa': '5,000', 'Mahindi': '780',   'Parachichi': '1,050', 'Ndizi': '520'},
    'Misenyi':   {'Maharagwe': '2,650', 'Kahawa': '5,100', 'Mahindi': '810',   'Parachichi': '1,080', 'Ndizi': '560'},
    'Kyerwa':    {'Maharagwe': '2,550', 'Kahawa': '5,050', 'Mahindi': '790',   'Parachichi': '1,060', 'Ndizi': '530'},
    # Kilimanjaro
    'Moshi':     {'Maharagwe': '3,000', 'Kahawa': '6,500', 'Mahindi': '900',   'Parachichi': '1,500', 'Ndizi': '700'},
    'Hai':       {'Maharagwe': '2,900', 'Kahawa': '6,200', 'Mahindi': '880',   'Parachichi': '1,400', 'Ndizi': '680'},
    'Mwanga':    {'Maharagwe': '2,800', 'Kahawa': '6,000', 'Mahindi': '860',   'Parachichi': '1,350', 'Ndizi': '660'},
    'Same':      {'Maharagwe': '2,750', 'Kahawa': '5,800', 'Mahindi': '840',   'Parachichi': '1,300', 'Ndizi': '640'},
    'Rombo':     {'Maharagwe': '2,950', 'Kahawa': '6,300', 'Mahindi': '890',   'Parachichi': '1,450', 'Ndizi': '690'},
    'Siha':      {'Maharagwe': '2,850', 'Kahawa': '6,100', 'Mahindi': '870',   'Parachichi': '1,380', 'Ndizi': '670'},
    # Arusha
    'Arusha':    {'Maharagwe': '3,200', 'Kahawa': '7,000', 'Mahindi': '950',   'Parachichi': '1,800', 'Ndizi': '750'},
    'Meru':      {'Maharagwe': '3,100', 'Kahawa': '6,800', 'Mahindi': '930',   'Parachichi': '1,700', 'Ndizi': '730'},
    'Monduli':   {'Maharagwe': '2,900', 'Kahawa': '6,500', 'Mahindi': '900',   'Parachichi': '1,600', 'Ndizi': '710'},
    'Ngorongoro':{'Maharagwe': '2,800', 'Kahawa': '6,200', 'Mahindi': '880',   'Parachichi': '1,550', 'Ndizi': '700'},
    'Longido':   {'Maharagwe': '2,700', 'Kahawa': '6,000', 'Mahindi': '860',   'Parachichi': '1,500', 'Ndizi': '690'},
    'Karatu':    {'Maharagwe': '3,000', 'Kahawa': '6,600', 'Mahindi': '910',   'Parachichi': '1,650', 'Ndizi': '720'},
    # Mbeya
    'Mbeya':     {'Maharagwe': '2,600', 'Kahawa': '5,500', 'Mahindi': '820',   'Parachichi': '1,300', 'Ndizi': '650'},
    'Rungwe':    {'Maharagwe': '2,500', 'Kahawa': '5,300', 'Mahindi': '800',   'Parachichi': '1,250', 'Ndizi': '630'},
    'Chunya':    {'Maharagwe': '2,400', 'Kahawa': '5,000', 'Mahindi': '780',   'Parachichi': '1,200', 'Ndizi': '610'},
    'Kyela':     {'Maharagwe': '2,550', 'Kahawa': '5,200', 'Mahindi': '810',   'Parachichi': '1,270', 'Ndizi': '640'},
    'Momba':     {'Maharagwe': '2,450', 'Kahawa': '5,100', 'Mahindi': '790',   'Parachichi': '1,220', 'Ndizi': '620'},
    'Songwe':    {'Maharagwe': '2,480', 'Kahawa': '5,150', 'Mahindi': '795',   'Parachichi': '1,240', 'Ndizi': '625'},
    # Iringa
    'Iringa':    {'Maharagwe': '2,700', 'Kahawa': '5,800', 'Mahindi': '850',   'Parachichi': '1,400', 'Ndizi': '680'},
    'Kilolo':    {'Maharagwe': '2,600', 'Kahawa': '5,600', 'Mahindi': '830',   'Parachichi': '1,350', 'Ndizi': '660'},
    'Mufindi':   {'Maharagwe': '2,650', 'Kahawa': '5,700', 'Mahindi': '840',   'Parachichi': '1,370', 'Ndizi': '670'},
    'Ludewa':    {'Maharagwe': '2,550', 'Kahawa': '5,500', 'Mahindi': '820',   'Parachichi': '1,320', 'Ndizi': '650'},
    'Makete':    {'Maharagwe': '2,500', 'Kahawa': '5,400', 'Mahindi': '810',   'Parachichi': '1,300', 'Ndizi': '640'},
    # Morogoro
    'Morogoro':  {'Maharagwe': '2,800', 'Kahawa': '5,500', 'Mahindi': '870',   'Parachichi': '1,400', 'Ndizi': '700'},
    'Kilosa':    {'Maharagwe': '2,700', 'Kahawa': '5,300', 'Mahindi': '850',   'Parachichi': '1,350', 'Ndizi': '680'},
    'Mvomero':   {'Maharagwe': '2,650', 'Kahawa': '5,200', 'Mahindi': '840',   'Parachichi': '1,320', 'Ndizi': '660'},
    'Gairo':     {'Maharagwe': '2,600', 'Kahawa': '5,100', 'Mahindi': '830',   'Parachichi': '1,300', 'Ndizi': '650'},
    'Kilombero': {'Maharagwe': '2,750', 'Kahawa': '5,400', 'Mahindi': '860',   'Parachichi': '1,370', 'Ndizi': '690'},
    'Ulanga':    {'Maharagwe': '2,680', 'Kahawa': '5,250', 'Mahindi': '845',   'Parachichi': '1,340', 'Ndizi': '670'},
    # Dar es Salaam
    'Ilala':     {'Maharagwe': '3,500', 'Kahawa': '8,000', 'Mahindi': '1,100', 'Parachichi': '2,000', 'Ndizi': '900'},
    'Kinondoni': {'Maharagwe': '3,600', 'Kahawa': '8,200', 'Mahindi': '1,150', 'Parachichi': '2,100', 'Ndizi': '950'},
    'Temeke':    {'Maharagwe': '3,400', 'Kahawa': '7,800', 'Mahindi': '1,080', 'Parachichi': '1,950', 'Ndizi': '880'},
    'Ubungo':    {'Maharagwe': '3,550', 'Kahawa': '8,100', 'Mahindi': '1,120', 'Parachichi': '2,050', 'Ndizi': '920'},
    'Kigamboni': {'Maharagwe': '3,450', 'Kahawa': '7,900', 'Mahindi': '1,090', 'Parachichi': '1,980', 'Ndizi': '900'},
    # Mwanza
    'Ilemela':   {'Maharagwe': '2,900', 'Kahawa': '5,800', 'Mahindi': '900',   'Parachichi': '1,500', 'Ndizi': '750'},
    'Nyamagana': {'Maharagwe': '2,950', 'Kahawa': '5,900', 'Mahindi': '910',   'Parachichi': '1,520', 'Ndizi': '760'},
    'Misungwi':  {'Maharagwe': '2,800', 'Kahawa': '5,600', 'Mahindi': '880',   'Parachichi': '1,450', 'Ndizi': '730'},
    'Magu':      {'Maharagwe': '2,750', 'Kahawa': '5,500', 'Mahindi': '870',   'Parachichi': '1,420', 'Ndizi': '720'},
    'Sengerema': {'Maharagwe': '2,820', 'Kahawa': '5,650', 'Mahindi': '885',   'Parachichi': '1,460', 'Ndizi': '735'},
    'Kwimba':    {'Maharagwe': '2,780', 'Kahawa': '5,580', 'Mahindi': '875',   'Parachichi': '1,440', 'Ndizi': '725'},
    # Dodoma
    'Dodoma':    {'Maharagwe': '2,600', 'Kahawa': '5,200', 'Mahindi': '820',   'Parachichi': '1,300', 'Ndizi': '650'},
    'Bahi':      {'Maharagwe': '2,500', 'Kahawa': '5,000', 'Mahindi': '800',   'Parachichi': '1,250', 'Ndizi': '630'},
    'Chamwino':  {'Maharagwe': '2,550', 'Kahawa': '5,100', 'Mahindi': '810',   'Parachichi': '1,270', 'Ndizi': '640'},
    'Kondoa':    {'Maharagwe': '2,520', 'Kahawa': '5,050', 'Mahindi': '805',   'Parachichi': '1,260', 'Ndizi': '635'},
    'Mpwapwa':   {'Maharagwe': '2,480', 'Kahawa': '4,950', 'Mahindi': '795',   'Parachichi': '1,240', 'Ndizi': '625'},
    # Tanga
    'Tanga':     {'Maharagwe': '2,900', 'Kahawa': '6,000', 'Mahindi': '900',   'Parachichi': '1,500', 'Ndizi': '750'},
    'Lushoto':   {'Maharagwe': '2,800', 'Kahawa': '5,800', 'Mahindi': '880',   'Parachichi': '1,450', 'Ndizi': '730'},
    'Korogwe':   {'Maharagwe': '2,750', 'Kahawa': '5,700', 'Mahindi': '870',   'Parachichi': '1,420', 'Ndizi': '720'},
    'Muheza':    {'Maharagwe': '2,700', 'Kahawa': '5,600', 'Mahindi': '860',   'Parachichi': '1,400', 'Ndizi': '710'},
    'Pangani':   {'Maharagwe': '2,850', 'Kahawa': '5,900', 'Mahindi': '890',   'Parachichi': '1,470', 'Ndizi': '740'},
    'Handeni':   {'Maharagwe': '2,680', 'Kahawa': '5,550', 'Mahindi': '850',   'Parachichi': '1,380', 'Ndizi': '700'},
}

WEATHER = {
    'Kagera':        'Mvua nyingi, 22-27C. Unyevu wa juu. Mazao yanastawi vizuri.',
    'Kilimanjaro':   'Baridi asubuhi, jua mchana, 15-25C. Hewa nzuri kwa kahawa.',
    'Arusha':        'Hewa nzuri, 18-26C. Mvua inatarajiwa wiki hii.',
    'Mbeya':         'Baridi, 14-22C. Mvua ndogo. Mazingira mazuri kwa mazao.',
    'Iringa':        'Baridi usiku, 12-24C. Jua mchana. Hewa safi.',
    'Morogoro':      'Joto la wastani, 24-32C. Unyevu wa juu. Angalia wadudu.',
    'Dar es Salaam': 'Jua kali, 28-34C. Unyevu mwingi. Mvua usiku.',
    'Mwanza':        'Jua, 24-30C. Upepo wa ziwa. Mvua kidogo mchana.',
    'Dodoma':        'Joto kali, 26-35C. Hewa kavu. Mvua haipo.',
    'Tanga':         'Joto la pwani, 26-32C. Unyevu mwingi. Mvua inatarajiwa.',
}

DAKTARI = {
    '1': {
        'tatizo': 'Majani yanageuka njano',
        'sababu': 'Upungufu wa Nitrogen au CBSD',
        'suluhisho': 'Weka Urea 50kg/eka. Angalia mizizi kwa ugonjwa.',
    },
    '2': {
        'tatizo': 'Wadudu kwenye mmea',
        'sababu': 'Aphids, Thrips au Nzige',
        'suluhisho': 'Nyunyizia Lambda au Imidacloprid asubuhi na jioni.',
    },
    '3': {
        'tatizo': 'Mmea kunyauka',
        'sababu': 'Ukosefu wa maji au Fusarium Wilt',
        'suluhisho': 'Mwagilia mara kwa mara. Ng\'oa mmea mgonjwa haraka.',
    },
    '4': {
        'tatizo': 'Matunda kuoza',
        'sababu': 'Anthracnose au unyevu mwingi',
        'suluhisho': 'Nyunyizia Mancozeb. Punguza umwagiliaji.',
    },
    '5': {
        'tatizo': 'Mizizi iliooza',
        'sababu': 'Maji mengi au Pythium Root Rot',
        'suluhisho': 'Boresha mifereji ya maji. Tumia dawa ya Metalaxyl.',
    },
    '6': {
        'tatizo': 'Madoa meupe kwenye majani',
        'sababu': 'Powdery Mildew',
        'suluhisho': 'Nyunyizia Sulphur au Trifloxystrobin. Punguza unyevu.',
    },
    '7': {
        'tatizo': 'Mashina kuoza chini',
        'sababu': 'Damping Off - unyevu wa udongo mwingi',
        'suluhisho': 'Panda udongo wenye mifereji. Tumia dawa ya Captan.',
    },
    '8': {
        'tatizo': 'Rangi ya kahawia kwenye majani',
        'sababu': 'Coffee Leaf Rust (kahawa)',
        'suluhisho': 'Nyunyizia Copper Oxychloride. Kata matawi yaliyoathirika.',
    },
}

MAIN_MENU = "CON Karibu Shamba Mfukoni!\n1. Hali ya Hewa\n2. Bei za Soko\n3. Daktari wa Mazao\n0. Toka"

def build_region_menu(prefix):
    r = f"CON {prefix}:\n"
    for key, val in REGIONS.items():
        r += f"{key}. {val['name']}\n"
    r += "0. Rudi"
    return r


# ============================================================
# VIEW
# ============================================================

@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        config = USSDConfig.objects.first()
        if not config or not config.is_active:
            msg = config.message_imezimwa if config else 'Huduma haipo kwa sasa.'
            return HttpResponse(f"END {msg}", content_type='text/plain; charset=utf-8')

        text = request.POST.get('text', '')
        parts = text.split('*') if text else []

        # ── MAIN MENU ──
        if text == '':
            response = MAIN_MENU

        elif text == '0':
            response = "END Asante kutumia Shamba Mfukoni!\nShamba bora, maisha bora!"

        # ══════════════════════════════════
        # 1. HALI YA HEWA
        # ══════════════════════════════════
        elif text == '1':
            response = build_region_menu("Hali ya Hewa - Chagua Mkoa")

        elif len(parts) == 2 and parts[0] == '1':
            rk = parts[1]
            if rk == '0':
                response = MAIN_MENU
            elif rk in REGIONS:
                rname = REGIONS[rk]['name']
                weather = WEATHER.get(rname, 'Taarifa haipatikani.')
                response = f"END Hali ya Hewa - {rname}:\n{weather}"
            else:
                response = "END Chaguo hilo halipo."

        # ══════════════════════════════════
        # 2. BEI ZA SOKO
        # ══════════════════════════════════
        elif text == '2':
            response = build_region_menu("Bei za Soko - Chagua Mkoa")

        elif len(parts) == 2 and parts[0] == '2':
            rk = parts[1]
            if rk == '0':
                response = MAIN_MENU
            elif rk in REGIONS:
                region = REGIONS[rk]
                response = f"CON Bei - {region['name']}\nChagua Wilaya:\n"
                for k, d in region['districts'].items():
                    response += f"{k}. {d}\n"
                response += "0. Rudi"
            else:
                response = "END Chaguo hilo halipo."

        elif len(parts) == 3 and parts[0] == '2':
            rk, dk = parts[1], parts[2]
            if dk == '0':
                response = build_region_menu("Bei za Soko - Chagua Mkoa")
            elif rk in REGIONS and dk in REGIONS[rk]['districts']:
                dname = REGIONS[rk]['districts'][dk]
                response = f"CON Bei - {dname}\nChagua Zao:\n"
                for k, crop in CROPS.items():
                    response += f"{k}. {crop}\n"
                response += "0. Rudi"
            else:
                response = "END Chaguo hilo halipo."

        elif len(parts) == 4 and parts[0] == '2':
            rk, dk, ck = parts[1], parts[2], parts[3]
            if ck == '0':
                region = REGIONS[rk]
                response = f"CON Bei - {region['name']}\nChagua Wilaya:\n"
                for k, d in region['districts'].items():
                    response += f"{k}. {d}\n"
                response += "0. Rudi"
            elif rk in REGIONS and dk in REGIONS[rk]['districts'] and ck in CROPS:
                dname = REGIONS[rk]['districts'][dk]
                cname = CROPS[ck]
                price = PRICES.get(dname, {}).get(cname, 'Haijulikani')
                response = f"END Bei ya {cname}\nWilaya: {dname}\nTZS {price}/kg\n\nAsante - Shamba Mfukoni!"
            else:
                response = "END Chaguo hilo halipo."

        # ══════════════════════════════════
        # 3. DAKTARI WA MAZAO
        # ══════════════════════════════════
        elif text == '3':
            response = "CON Daktari wa Mazao:\nChagua tatizo:\n"
            for k, v in DAKTARI.items():
                response += f"{k}. {v['tatizo']}\n"
            response += "0. Rudi"

        elif len(parts) == 2 and parts[0] == '3':
            pk = parts[1]
            if pk == '0':
                response = MAIN_MENU
            elif pk in DAKTARI:
                d = DAKTARI[pk]
                response = f"END {d['tatizo']}\nSababu: {d['sababu']}\nSuluhisho: {d['suluhisho']}"
            else:
                response = "END Chaguo hilo halipo."

        else:
            response = "END Samahani, chaguo hilo halipo."

        return HttpResponse(response, content_type='text/plain; charset=utf-8')

    return HttpResponse("Shamba Mfukoni USSD inafanya kazi!", content_type='text/plain; charset=utf-8')