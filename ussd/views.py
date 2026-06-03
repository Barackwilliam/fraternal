from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def respond(text):
    return HttpResponse(text, content_type='text/plain')


# ─────────────────────────────────────────────
#  MAIN VIEW
# ─────────────────────────────────────────────
@csrf_exempt
def ussd_callback(request):
    if request.method != 'POST':
        return respond("Shamba Mfukoni & AfyaPlus USSD inafanya kazi! ✅")

    text = request.POST.get('text', '').strip()

    # ── ROOT ──────────────────────────────────
    if text == '':
        return respond(
            "CON Karibu! Chagua huduma:\n"
            "1. Kilimo\n"
            "2. Afya\n"
            "0. Toka"
        )

    # ══════════════════════════════════════════
    #  KILIMO BRANCH  (text starts with '1')
    # ══════════════════════════════════════════

    if text == '1':
        return respond(
            "CON 🌾 KILIMO - Chagua:\n"
            "1. Hali ya Hewa\n"
            "2. Bei za Soko\n"
            "3. Daktari wa Mazao\n"
            "4. Mbolea & Viuatilifu\n"
            "5. Umwagiliaji\n"
            "6. Kalenda ya Kupanda\n"
            "0. Rudi"
        )

    # ── Kilimo > Hali ya Hewa ─────────────────
    elif text == '1*1':
        return respond(
            "CON 🌦️ Chagua mkoa:\n"
            "1. Dar es Salaam\n"
            "2. Arusha\n"
            "3. Mwanza\n"
            "4. Dodoma\n"
            "5. Mbeya\n"
            "0. Rudi"
        )

    elif text == '1*1*1':
        return respond(
            "END 🌦️ Dar es Salaam:\n"
            "Leo: Jua, 32°C, Unyevu 78%\n"
            "Kesho: Mvua asubuhi, 28°C\n"
            "Ushauri: Epuka kupanda mbegu wiki hii.\n"
            "Mwagilia asubuhi mapema."
        )

    elif text == '1*1*2':
        return respond(
            "END 🌦️ Arusha:\n"
            "Leo: Mawingu, 22°C, Unyevu 65%\n"
            "Kesho: Jua, 24°C\n"
            "Ushauri: Mazingira mazuri ya kupanda.\n"
            "Hasa mahindi na mboga za majani."
        )

    elif text == '1*1*3':
        return respond(
            "END 🌦️ Mwanza:\n"
            "Leo: Jua kali, 34°C, Unyevu 55%\n"
            "Kesho: Jua, 33°C\n"
            "Ushauri: Mwagilia mara mbili kwa siku.\n"
            "Tumia matandazo kulinda udongo."
        )

    elif text == '1*1*4':
        return respond(
            "END 🌦️ Dodoma:\n"
            "Leo: Kavu, 30°C, Unyevu 40%\n"
            "Kesho: Kavu, 31°C\n"
            "Ushauri: Msimu wa kiangazi. Tumia\n"
            "mazao yanayostahimili ukame."
        )

    elif text == '1*1*5':
        return respond(
            "END 🌦️ Mbeya:\n"
            "Leo: Baridi, 18°C, Unyevu 80%\n"
            "Kesho: Mvua kidogo, 17°C\n"
            "Ushauri: Hali nzuri kwa chai na kahawa.\n"
            "Angalia kuoza kwa viazi."
        )

    # ── Kilimo > Bei za Soko ──────────────────
    elif text == '1*2':
        return respond(
            "CON 💰 Bei za Soko - Chagua zao:\n"
            "1. Mahindi\n"
            "2. Maharagwe\n"
            "3. Mpunga\n"
            "4. Nyanya\n"
            "5. Ndizi\n"
            "6. Mihogo\n"
            "0. Rudi"
        )

    elif text == '1*2*1':
        return respond(
            "END 🌽 Bei ya Mahindi (kwa kg):\n"
            "Dar es Salaam: TZS 850\n"
            "Arusha:        TZS 780\n"
            "Mwanza:        TZS 720\n"
            "Dodoma:        TZS 700\n"
            "Mbeya:         TZS 650\n"
            "Chanzo: Soko la Kariakoo"
        )

    elif text == '1*2*2':
        return respond(
            "END 🫘 Bei ya Maharagwe (kwa kg):\n"
            "Dar es Salaam: TZS 2,600\n"
            "Arusha:        TZS 2,300\n"
            "Mwanza:        TZS 2,100\n"
            "Dodoma:        TZS 2,000\n"
            "Mbeya:         TZS 1,900\n"
            "Chanzo: Soko la Kariakoo"
        )

    elif text == '1*2*3':
        return respond(
            "END 🌾 Bei ya Mpunga (kwa kg):\n"
            "Dar es Salaam: TZS 1,300\n"
            "Arusha:        TZS 1,150\n"
            "Mwanza:        TZS 1,050\n"
            "Dodoma:        TZS 1,000\n"
            "Mbeya:         TZS 950\n"
            "Chanzo: Soko la Kariakoo"
        )

    elif text == '1*2*4':
        return respond(
            "END 🍅 Bei ya Nyanya (kwa kg):\n"
            "Dar es Salaam: TZS 1,800\n"
            "Arusha:        TZS 1,500\n"
            "Mwanza:        TZS 1,400\n"
            "Dodoma:        TZS 1,200\n"
            "Mbeya:         TZS 1,100\n"
            "Chanzo: Soko la Kariakoo"
        )

    elif text == '1*2*5':
        return respond(
            "END 🍌 Bei ya Ndizi (kwa bunchi):\n"
            "Dar es Salaam: TZS 5,000\n"
            "Arusha:        TZS 4,500\n"
            "Mwanza:        TZS 4,000\n"
            "Dodoma:        TZS 3,500\n"
            "Mbeya:         TZS 3,000\n"
            "Chanzo: Soko la Kariakoo"
        )

    elif text == '1*2*6':
        return respond(
            "END 🍠 Bei ya Mihogo (kwa kg):\n"
            "Dar es Salaam: TZS 600\n"
            "Arusha:        TZS 550\n"
            "Mwanza:        TZS 500\n"
            "Dodoma:        TZS 480\n"
            "Mbeya:         TZS 450\n"
            "Chanzo: Soko la Kariakoo"
        )

    # ── Kilimo > Daktari wa Mazao ─────────────
    elif text == '1*3':
        return respond(
            "CON 🌿 Daktari wa Mazao:\n"
            "1. Majani yanageuka njano\n"
            "2. Majani yana madoa meusi\n"
            "3. Wadudu kwenye mmea\n"
            "4. Mmea kunyauka\n"
            "5. Matunda kuoza\n"
            "6. Mizizi kuoza\n"
            "0. Rudi"
        )

    elif text == '1*3*1':
        return respond(
            "END 🟡 Majani Njano:\n"
            "Sababu zinazowezekana:\n"
            "- Upungufu wa Nitrogen\n"
            "- Maji mengi sana\n"
            "- Ugonjwa wa Chlorosis\n"
            "Suluhisho: Weka Urea 50kg/ekari.\n"
            "Angalia mfumo wa maji usizidi."
        )

    elif text == '1*3*2':
        return respond(
            "END ⚫ Madoa Meusi:\n"
            "Sababu: Ugonjwa wa kuvu (Fungal)\n"
            "Mara nyingi: Early/Late Blight\n"
            "Suluhisho:\n"
            "- Nyunyizia Mancozeb au Ridomil\n"
            "- Ondoa majani yaliyoathirika\n"
            "- Usimwagilie jioni"
        )

    elif text == '1*3*3':
        return respond(
            "END 🐛 Wadudu:\n"
            "Aphids: Nyunyizia Imidacloprid\n"
            "Thrips: Tumia Lambda-cyhalothrin\n"
            "Viwavi: Tumia Bt (Bacillus thuringiensis)\n"
            "Vidukari: Nyunyizia mafuta ya taa\n"
            "Omba dawa asubuhi au jioni tu."
        )

    elif text == '1*3*4':
        return respond(
            "END 🥀 Mmea Kunyauka:\n"
            "Sababu zinazowezekana:\n"
            "- Ukosefu wa maji\n"
            "- Ugonjwa wa Fusarium Wilt\n"
            "- Mizizi iliyooza\n"
            "Suluhisho: Mwagilia sasa. Kama bado\n"
            "unyauka, ng'oa na angalia mizizi."
        )

    elif text == '1*3*5':
        return respond(
            "END 🍅 Matunda Kuoza:\n"
            "Sababu: Ugonjwa wa Anthracnose\n"
            "au Blossom End Rot\n"
            "Suluhisho:\n"
            "- Weka chokaa (Calcium) kwenye udongo\n"
            "- Nyunyizia Copper Oxychloride\n"
            "- Vuna mapema matunda yaliyoiva"
        )

    elif text == '1*3*6':
        return respond(
            "END 🌱 Mizizi Kuoza:\n"
            "Sababu: Maji yasiyotoka (waterlogging)\n"
            "au ugonjwa wa Pythium\n"
            "Suluhisho:\n"
            "- Tengeneza mifereji ya maji\n"
            "- Tumia Metalaxyl kwenye udongo\n"
            "- Badilisha eneo la kupanda"
        )

    # ── Kilimo > Mbolea & Viuatilifu ──────────
    elif text == '1*4':
        return respond(
            "CON 🧪 Mbolea & Viuatilifu:\n"
            "1. Mbolea kwa Mahindi\n"
            "2. Mbolea kwa Mpunga\n"
            "3. Mbolea kwa Mboga\n"
            "4. Mbolea ya Asili (Organic)\n"
            "5. Tahadhari za Dawa\n"
            "0. Rudi"
        )

    elif text == '1*4*1':
        return respond(
            "END 🌽 Mbolea - Mahindi:\n"
            "Wakati wa kupanda:\n"
            "- DAP: 50kg kwa ekari moja\n"
            "Wiki 3-4 baada ya kupanda:\n"
            "- Urea: 50kg kwa ekari moja\n"
            "Wiki 6-8:\n"
            "- CAN: 25kg kwa ekari moja\n"
            "Weka pembeni ya mmea, si juu yake."
        )

    elif text == '1*4*2':
        return respond(
            "END 🌾 Mbolea - Mpunga:\n"
            "Wakati wa kupanda:\n"
            "- NPK (17:17:17): 60kg/ekari\n"
            "Wiki 3 baada ya kupanda:\n"
            "- Urea: 40kg/ekari\n"
            "Wiki 8 (panicle initiation):\n"
            "- Urea: 30kg/ekari\n"
            "Weka ndani ya maji shamba."
        )

    elif text == '1*4*3':
        return respond(
            "END 🥬 Mbolea - Mboga:\n"
            "Kabla ya kupanda:\n"
            "- Samadi iliyooza: debe 4/tuta\n"
            "Baada ya wiki 2:\n"
            "- CAN au Urea: kijiko 1/mmea\n"
            "Kila wiki 2 tena:\n"
            "- Mbolea ya majani (foliar)\n"
            "Mwagilia mara baada ya kuweka mbolea."
        )

    elif text == '1*4*4':
        return respond(
            "END ♻️ Mbolea ya Asili:\n"
            "Samadi ya ng'ombe: bora sana\n"
            "Mboji (Compost): inaboresha udongo\n"
            "Mbolea ya kijani: panda Tithonia\n"
            "Mkojo wa ng'ombe: punguza 1:10 na maji\n"
            "Faida: Bei nafuu, udongo unabaki\n"
            "na afya kwa miaka mingi."
        )

    elif text == '1*4*5':
        return respond(
            "END ⚠️ Tahadhari za Dawa:\n"
            "- Vaa glavu na barakoa daima\n"
            "- Usinyunyizie wakati wa upepo\n"
            "- Omba asubuhi (6-9am) au jioni\n"
            "- Usiruke siku za kulinda\n"
            "- Hifadhi mbali na watoto\n"
            "- Soma maelekezo ya chupa kila wakati"
        )

    # ── Kilimo > Umwagiliaji ──────────────────
    elif text == '1*5':
        return respond(
            "CON 💧 Umwagiliaji - Chagua zao:\n"
            "1. Mahindi\n"
            "2. Nyanya\n"
            "3. Mboga za majani\n"
            "4. Ndizi\n"
            "5. Miwa\n"
            "0. Rudi"
        )

    elif text == '1*5*1':
        return respond(
            "END 💧 Umwagiliaji - Mahindi:\n"
            "Kiasi: Lita 5-7 kwa mmea/wiki\n"
            "Wakati muhimu:\n"
            "- Kipindi cha kuota (germination)\n"
            "- Wakati wa maua (tasseling)\n"
            "- Wakati wa punje kujaa (grain fill)\n"
            "Epuka maji mengi wakati wa mavuno."
        )

    elif text == '1*5*2':
        return respond(
            "END 💧 Umwagiliaji - Nyanya:\n"
            "Kiasi: Lita 3-5 kwa mmea/siku\n"
            "Mwagilia: Kila siku asubuhi\n"
            "Epuka: Kumwagilia majani\n"
            "Tumia: Drip irrigation ikiwezekana\n"
            "Maji yasiyolingana husababisha\n"
            "matunda kupasuka."
        )

    elif text == '1*5*3':
        return respond(
            "END 💧 Umwagiliaji - Mboga:\n"
            "Kiasi: Lita 2-3/m² kila siku\n"
            "Mwagilia: Asubuhi na jioni\n"
            "Matumizi ya kisasa:\n"
            "- Mulching hupunguza uvukizi\n"
            "- Watering can ni bora kuliko bomba\n"
            "Angalia udongo usiwe na maji mengi."
        )

    elif text == '1*5*4':
        return respond(
            "END 💧 Umwagiliaji - Ndizi:\n"
            "Kiasi: Lita 10-15/mmea/wiki\n"
            "Ndizi zinahitaji maji mengi sana\n"
            "Mwagilia: Mara 2-3 kwa wiki\n"
            "Hakikisha mifereji ya maji ipo\n"
            "Maji yaliyosimama huoza mizizi."
        )

    elif text == '1*5*5':
        return respond(
            "END 💧 Umwagiliaji - Miwa:\n"
            "Kiasi: 1200-1500mm/msimu mzima\n"
            "Hatua muhimu:\n"
            "- Baada ya kupanda: mwagilia vizuri\n"
            "- Mwezi 1-3: mara kwa mara\n"
            "- Mwezi 4-8: punguza maji\n"
            "- Wiki 6 kabla ya kuvuna: acha maji"
        )

    # ── Kilimo > Kalenda ya Kupanda ───────────
    elif text == '1*6':
        return respond(
            "CON 📅 Kalenda ya Kupanda:\n"
            "1. Msimu wa Masika (Mar-Jun)\n"
            "2. Msimu wa Vuli (Oct-Dec)\n"
            "3. Kilimo cha Umwagiliaji\n"
            "4. Mazao ya Miaka Mingi\n"
            "0. Rudi"
        )

    elif text == '1*6*1':
        return respond(
            "END 🌧️ Msimu wa Masika:\n"
            "Mar-Apr: Panda mahindi, mpunga,\n"
            "maharagwe, nyanya, vitunguu\n"
            "Apr-May: Panda mihogo, viazi,\n"
            "mboga za majani\n"
            "Jun: Vuna mazao ya mapema\n"
            "Fursa nzuri kwa Tanzania Bara."
        )

    elif text == '1*6*2':
        return respond(
            "END 🍂 Msimu wa Vuli:\n"
            "Oct-Nov: Panda mahindi (fupi),\n"
            "maharagwe, mboga\n"
            "Nov-Dec: Panda vitunguu saumu,\n"
            "nyanya, pilipili\n"
            "Feb-Mar: Vuna mazao ya Vuli\n"
            "Msimu mfupi - chagua aina za haraka."
        )

    elif text == '1*6*3':
        return respond(
            "END 🚿 Kilimo cha Umwagiliaji:\n"
            "Unaweza kupanda mwaka mzima!\n"
            "Mazao bora:\n"
            "- Mboga (wiki 6-8 kuvuna)\n"
            "- Nyanya (wiki 10-12)\n"
            "- Vitunguu (wiki 12-16)\n"
            "- Sukuma wiki (daima)\n"
            "Mahitaji: Chanzo cha maji karibu."
        )

    elif text == '1*6*4':
        return respond(
            "END 🌳 Mazao ya Miaka Mingi:\n"
            "Panda wakati wowote wa mvua:\n"
            "- Miembe: Mavuno baada ya miaka 3-5\n"
            "- Michungwa: Miaka 3-4\n"
            "- Kahawa: Miaka 3-4\n"
            "- Ndizi: Miaka 1-2\n"
            "- Avokado: Miaka 3-5\n"
            "Faida ya muda mrefu, panda leo!"
        )

    # ══════════════════════════════════════════
    #  AFYA BRANCH  (text starts with '2')
    # ══════════════════════════════════════════

    elif text == '2':
        return respond(
            "CON 🏥 AFYA - Chagua:\n"
            "1. Dalili za Magonjwa\n"
            "2. Mama na Mtoto\n"
            "3. Chanjo na Kinga\n"
            "4. Lishe na Maji Safi\n"
            "5. Afya ya Akili\n"
            "6. Dawa za Kawaida\n"
            "0. Rudi"
        )

    # ── Afya > Dalili za Magonjwa ─────────────
    elif text == '2*1':
        return respond(
            "CON 🤒 Dalili za Magonjwa:\n"
            "1. Homa na Baridi\n"
            "2. Kuhara na Kutapika\n"
            "3. Kikohozi na Mafua\n"
            "4. Maumivu ya Tumbo\n"
            "5. Upele wa Ngozi\n"
            "6. Maumivu ya Kichwa\n"
            "0. Rudi"
        )

    elif text == '2*1*1':
        return respond(
            "END 🌡️ Homa na Baridi:\n"
            "Inaweza kuwa: Malaria, Typhoid,\n"
            "Dengue au Flu\n"
            "Hatua za haraka:\n"
            "1. Pima joto - joto >38°C ni homa\n"
            "2. Kunywa maji mengi\n"
            "3. Tumia Paracetamol kupunguza joto\n"
            "⚠️ Kama homa >3 siku: Nenda hospitali!"
        )

    elif text == '2*1*2':
        return respond(
            "END 🤢 Kuhara na Kutapika:\n"
            "Inaweza kuwa: Kipindupindu, Typhoid\n"
            "au Sumu ya chakula\n"
            "Hatua za haraka:\n"
            "1. Kunywa ORS (maji + chumvi + sukari)\n"
            "2. Epuka vyakula vya mafuta\n"
            "3. Osha mikono mara kwa mara\n"
            "⚠️ Kama kuhara >5 mara/siku: Hospitali!"
        )

    elif text == '2*1*3':
        return respond(
            "END 😷 Kikohozi na Mafua:\n"
            "Inaweza kuwa: Flu, COVID, TB, Pumu\n"
            "Hatua za haraka:\n"
            "1. Pumzika na kunywa maji ya moto\n"
            "2. Vuta mvuke wa maji ya moto + chumvi\n"
            "3. Tumia asali na limao\n"
            "⚠️ Kama kikohozi >2 wiki au damu: Hospitali!"
        )

    elif text == '2*1*4':
        return respond(
            "END 🫃 Maumivu ya Tumbo:\n"
            "Inaweza kuwa: Kidonda cha tumbo,\n"
            "Appendicitis, Gesi au Typhoid\n"
            "Hatua:\n"
            "1. Pumzika, epuka vyakula vikali\n"
            "2. Kunywa maji ya joto\n"
            "3. Tumia moto (hot water bottle)\n"
            "⚠️ Maumivu makali upande wa kulia: Hospitali SASA!"
        )

    elif text == '2*1*5':
        return respond(
            "END 🔴 Upele wa Ngozi:\n"
            "Inaweza kuwa: Ugonjwa wa ngozi,\n"
            "Mzio (Allergy), Tetekuwanga au Ukimwi\n"
            "Hatua:\n"
            "1. Usikwarue - utaeneza maambukizo\n"
            "2. Tumia sabuni ya upole\n"
            "3. Weka cream ya Calamine\n"
            "⚠️ Upele + homa + maumivu: Hospitali haraka!"
        )

    elif text == '2*1*6':
        return respond(
            "END 🤕 Maumivu ya Kichwa:\n"
            "Inaweza kuwa: Msongo, Pressure ya damu,\n"
            "Malaria au Meningitis\n"
            "Hatua:\n"
            "1. Pumzika mahali penye giza na utulivu\n"
            "2. Tumia Paracetamol au Ibuprofen\n"
            "3. Kunywa maji - dehydration husababisha\n"
            "⚠️ Kichwa + shingo ngumu + homa: Hospitali SASA!"
        )

    # ── Afya > Mama na Mtoto ──────────────────
    elif text == '2*2':
        return respond(
            "CON 🤰 Mama na Mtoto:\n"
            "1. Dalili za Mimba ya Hatari\n"
            "2. Lishe ya Mama Mjamzito\n"
            "3. Chanjo za Mtoto\n"
            "4. Ukuaji wa Mtoto\n"
            "5. Kunyonyesha\n"
            "0. Rudi"
        )

    elif text == '2*2*1':
        return respond(
            "END ⚠️ Dalili za Hatari - Mimba:\n"
            "Nenda hospitali HARAKA ukiona:\n"
            "- Kutoka damu ukeni wakati wowote\n"
            "- Maumivu makali ya tumbo\n"
            "- Mtoto kusogea kidogo sana\n"
            "- Miguu/uso kuvimba ghafla\n"
            "- Maumivu ya kichwa makali\n"
            "- Maono kufifia (blurred vision)\n"
            "Usisubiri - piga simu ya msaada!"
        )

    elif text == '2*2*2':
        return respond(
            "END 🥗 Lishe ya Mama Mjamzito:\n"
            "Kila siku ule:\n"
            "- Nafaka: ugali, wali, mkate\n"
            "- Protini: nyama, samaki, maharagwe\n"
            "- Vitamini: matunda na mboga\n"
            "- Chuma: ini, dengu, spinachi\n"
            "- Folate: karanga, mboga za kijani\n"
            "Kunywa maji lita 2-3 kwa siku.\n"
            "Epuka pombe na sigara kabisa."
        )

    elif text == '2*2*3':
        return respond(
            "END 💉 Chanjo za Mtoto (Tanzania):\n"
            "Kuzaliwa: BCG + OPV0\n"
            "Miezi 6: OPV1 + DTP + Hib + HepB\n"
            "Miezi 10: OPV2 + DTP + Hib + HepB\n"
            "Miezi 14: OPV3 + DTP + Hib + HepB\n"
            "Miezi 9: Surua (Measles) + Meningitis\n"
            "Miaka 2: Kichaa cha mbwa\n"
            "Chanjo ZOTE ni BURE kliniki ya serikali!"
        )

    elif text == '2*2*4':
        return respond(
            "END 📏 Ukuaji wa Mtoto:\n"
            "Miezi 1-3: Anaona, anasikia, anatabasamu\n"
            "Miezi 4-6: Anashika vitu, anageuza kichwa\n"
            "Miezi 7-9: Anakaa peke yake\n"
            "Miezi 10-12: Anapiga hatua za kwanza\n"
            "Miaka 1-2: Maneno 10-50\n"
            "⚠️ Mtoto asiye na maendeleo haya:\n"
            "Mwambie daktari haraka."
        )

    elif text == '2*2*5':
        return respond(
            "END 🍼 Kunyonyesha:\n"
            "Maziwa ya mama ni bora kuliko yote!\n"
            "- Anza kunyonyesha ndani ya saa 1 ya kuzaa\n"
            "- Nyonyesha peke yake miezi 6 ya kwanza\n"
            "- Nyonyesha mara 8-12 kwa siku\n"
            "- Usimpe maji wala chakula kingine\n"
            "- Endelea hadi miaka 2\n"
            "Faida: Kinga ya magonjwa, akili, uhusiano."
        )

    # ── Afya > Chanjo na Kinga ────────────────
    elif text == '2*3':
        return respond(
            "CON 💉 Chanjo na Kinga:\n"
            "1. Chanjo za Watu Wazima\n"
            "2. Kuzuia Malaria\n"
            "3. Kuzuia Kipindupindu\n"
            "4. Kuzuia Typhoid\n"
            "5. Usafi wa Mazingira\n"
            "0. Rudi"
        )

    elif text == '2*3*1':
        return respond(
            "END 💉 Chanjo - Watu Wazima:\n"
            "Tetanus: Kila miaka 10\n"
            "Hepatitis B: Dozi 3 kwa watu wapya\n"
            "Meningitis: Watu wanaosafiri\n"
            "Typhoid: Kila miaka 3\n"
            "COVID-19: Booster kila mwaka\n"
            "Chanjo nyingi ni BURE hospitali ya serikali.\n"
            "Omba kadi yako ya chanjo leo!"
        )

    elif text == '2*3*2':
        return respond(
            "END 🦟 Kuzuia Malaria:\n"
            "1. Lala chini ya chandarua cha dawa\n"
            "2. Weka dawa ya mbu (repellent)\n"
            "3. Vaa nguo ndefu jioni\n"
            "4. Ondoa maji yaliyosimama nyumbani\n"
            "5. Funika madumu ya maji\n"
            "6. Piga dawa nyumbani (IRS)\n"
            "Dalili: Homa, baridi, jasho, maumivu ya viungo.\n"
            "Tibu mapema - malaria inaua haraka!"
        )

    elif text == '2*3*3':
        return respond(
            "END 💧 Kuzuia Kipindupindu:\n"
            "1. Kunywa maji ya kuchemshwa au ya chupa\n"
            "2. Osha mikono na sabuni kila wakati\n"
            "3. Pika chakula vizuri - kisiwe kibichi\n"
            "4. Epuka chakula cha barabarani\n"
            "5. Tumia choo - usijisaidie nje\n"
            "6. Funika chakula dhidi ya nzi\n"
            "Dalili: Kuhara maji mengi + kutapika.\n"
            "⚠️ Inaweza kuua ndani ya masaa 24!"
        )

    elif text == '2*3*4':
        return respond(
            "END 🦠 Kuzuia Typhoid:\n"
            "1. Osha mikono kabla ya kula\n"
            "2. Kunywa maji safi ya kuchemsha\n"
            "3. Epuka vyakula vibichi (saladi etc)\n"
            "4. Piga chanjo ya Typhoid\n"
            "5. Usile matunda yasiyoosha\n"
            "Dalili: Homa polepole inayoongezeka,\n"
            "maumivu ya tumbo, upele mwilini.\n"
            "Tibu kwa Antibiotics - omba daktari."
        )

    elif text == '2*3*5':
        return respond(
            "END 🧹 Usafi wa Mazingira:\n"
            "Nyumbani:\n"
            "- Osha mikono mara 5+ kwa siku\n"
            "- Funika chakula na maji\n"
            "- Tupa taka mahali pazuri\n"
            "Choo:\n"
            "- Tumia choo cha ndani au la nje\n"
            "- Usijisaidie karibu na mto/kisima\n"
            "- Safisha choo kila siku\n"
            "Usafi = Afya bora kwa familia yako!"
        )

    # ── Afya > Lishe na Maji Safi ─────────────
    elif text == '2*4':
        return respond(
            "CON 🥗 Lishe na Maji Safi:\n"
            "1. Lishe Bora ya Kila Siku\n"
            "2. Utapiamlo kwa Watoto\n"
            "3. Lishe kwa Wazee\n"
            "4. Maji Safi - Jinsi ya Kutayarisha\n"
            "5. Lishe kwa Magonjwa ya Sugu\n"
            "0. Rudi"
        )

    elif text == '2*4*1':
        return respond(
            "END 🍽️ Lishe Bora ya Kila Siku:\n"
            "Sahani yako iwe na:\n"
            "- Nusu: Mboga na matunda ya rangi\n"
            "- Robo: Nafaka (ugali/wali/mkate)\n"
            "- Robo: Protini (nyama/samaki/maharagwe)\n"
            "Ongeza:\n"
            "- Maziwa au bidhaa zake\n"
            "- Mafuta kidogo (olive oil, nazi)\n"
            "Kunywa maji lita 2-3 kila siku."
        )

    elif text == '2*4*2':
        return respond(
            "END 👶 Utapiamlo - Watoto:\n"
            "Dalili za Utapiamlo:\n"
            "- Ukuaji wa polepole\n"
            "- Nywele za njano/kuanguka\n"
            "- Uvimbe wa miguu na tumbo\n"
            "- Uchovu na kutocheza\n"
            "Suluhisho:\n"
            "- Nyonyesha hadi miaka 2\n"
            "- Ongeza chakula cha protini\n"
            "- Nenda kliniki kwa ushauri wa daktari"
        )

    elif text == '2*4*3':
        return respond(
            "END 👴 Lishe kwa Wazee:\n"
            "Wazee wanahitaji zaidi:\n"
            "- Kalsiamu: maziwa, samaki wadogo\n"
            "- Vitamini D: jua asubuhi + mayai\n"
            "- Protini: maharagwe, nyama, samaki\n"
            "- Fiber: mboga, matunda, nafaka nzima\n"
            "Punguza: Chumvi, sukari, mafuta\n"
            "Kunywa maji hata usipohisi kiu.\n"
            "Kula mara ndogo 5-6 kwa siku."
        )

    elif text == '2*4*4':
        return respond(
            "END 💧 Kutayarisha Maji Safi:\n"
            "Njia 1 - Kuchemsha:\n"
            "Chemsha kwa dakika 3 - bora zaidi\n"
            "Njia 2 - Dawa ya Maji (WaterGuard):\n"
            "Tone 1 kwa lita 1 ya maji\n"
            "Njia 3 - Kichujio (Water Filter):\n"
            "Hifadhi katika chombo safi chenye mfuniko\n"
            "Njia 4 - Jua (SODIS):\n"
            "Chupa ya plastiki wazi - jua masaa 6+"
        )

    elif text == '2*4*5':
        return respond(
            "END 🫀 Lishe kwa Magonjwa ya Sugu:\n"
            "Kisukari (Diabetes):\n"
            "- Punguza sukari, wali mwingi, soda\n"
            "- Ongeza mboga, nafaka nzima\n"
            "Shinikizo la Damu:\n"
            "- Punguza chumvi sana\n"
            "- Ongeza matunda, mboga, ndizi\n"
            "Moyo:\n"
            "- Epuka mafuta ya wanyama\n"
            "- Tumia olive oil au mafuta ya alizeti"
        )

    # ── Afya > Afya ya Akili ──────────────────
    elif text == '2*5':
        return respond(
            "CON 🧠 Afya ya Akili:\n"
            "1. Msongo wa Mawazo (Stress)\n"
            "2. Huzuni na Unyogovu (Depression)\n"
            "3. Usingizi Mbaya\n"
            "4. Wasiwasi (Anxiety)\n"
            "5. Msaada wa Dharura\n"
            "0. Rudi"
        )

    elif text == '2*5*1':
        return respond(
            "END 😤 Msongo wa Mawazo:\n"
            "Dalili: Maumivu ya kichwa, usingizi,\n"
            "hasira, kukosa hamu ya kula\n"
            "Njia za kupumzika:\n"
            "- Pumzika kwa kupumua polepole\n"
            "- Ongea na rafiki au ndugu\n"
            "- Fanya mazoezi ya mwili kila siku\n"
            "- Lala vizuri masaa 7-8\n"
            "- Punguza matumizi ya simu usiku"
        )

    elif text == '2*5*2':
        return respond(
            "END 😔 Huzuni na Unyogovu:\n"
            "Dalili: Kukosa furaha, kujitenga,\n"
            "kuhisi huna thamani, kutolala\n"
            "Hatua:\n"
            "- Zungumza na mtu unayemwamini\n"
            "- Usijiache peke yako sana\n"
            "- Fanya shughuli unazozipenda\n"
            "- Nenda kanisani/msikitini/kwa mshauri\n"
            "⚠️ Mawazo ya kujidhuru: Piga simu\n"
            "Muhimbili NHC: +255 22 215 0562"
        )

    elif text == '2*5*3':
        return respond(
            "END 😴 Usingizi Mbaya:\n"
            "Njia za kulala vizuri:\n"
            "- Lala na kuamka wakati mmoja kila siku\n"
            "- Zima simu/TV saa moja kabla ya kulala\n"
            "- Chumba kiwe giza na chenye utulivu\n"
            "- Epuka kahawa jioni\n"
            "- Jaribu kunywa maziwa ya joto\n"
            "- Mazoezi ya mwili asubuhi\n"
            "Usingizi mzuri = afya nzuri ya mwili na akili."
        )

    elif text == '2*5*4':
        return respond(
            "END 😰 Wasiwasi (Anxiety):\n"
            "Dalili: Moyo kupiga haraka, jasho,\n"
            "kutoweza kutulia, kuogopa bila sababu\n"
            "Njia za kusaidia:\n"
            "- Pumua polepole: Vuta pumzi 4 sek,\n"
            "  shikilia 4 sek, toa 4 sek\n"
            "- Zungumza na mshauri wa afya\n"
            "- Epuka pombe na kahawa nyingi\n"
            "- Fanya mazoezi ya yoga au kutembea"
        )

    elif text == '2*5*5':
        return respond(
            "END 🆘 Msaada wa Dharura - Afya ya Akili:\n"
            "Tanzania:\n"
            "Muhimbili NHC: +255 22 215 0562\n"
            "Wizara ya Afya: 0800 780 000 (bure)\n"
            "Muhimbili Mental Health: +255 22 215 0610\n"
            "\n"
            "Ukiwa katika hali ya hatari:\n"
            "- Piga simu mtu wa karibu sasa\n"
            "- Nenda hospitali ya karibu nawe\n"
            "Maisha yako yana thamani. Omba msaada!"
        )

    # ── Afya > Dawa za Kawaida ────────────────
    elif text == '2*6':
        return respond(
            "CON 💊 Dawa za Kawaida:\n"
            "1. Paracetamol (Tylenol)\n"
            "2. ORS - Maji ya Chumvi\n"
            "3. Metronidazole\n"
            "4. Amoxicillin\n"
            "5. Malaraquin / ALU\n"
            "0. Rudi"
        )

    elif text == '2*6*1':
        return respond(
            "END 💊 Paracetamol:\n"
            "Matumizi: Homa, maumivu ya kichwa,\n"
            "maumivu ya mwili\n"
            "Dozi ya Mtu Mzima: 500mg-1000mg\n"
            "kila masaa 4-6 (max 4000mg/siku)\n"
            "Dozi ya Mtoto: 15mg/kg kwa kila dozi\n"
            "⚠️ Usitumie zaidi ya dozi - inadhuru ini\n"
            "⚠️ Epuka na pombe kabisa"
        )

    elif text == '2*6*2':
        return respond(
            "END 💧 ORS - Maji ya Chumvi:\n"
            "Matumizi: Kuhara, kutapika, kupoteza maji\n"
            "Jinsi ya kutengeneza nyumbani:\n"
            "- Lita 1 ya maji safi ya kuchemsha\n"
            "- Vijiko 6 vya sukari\n"
            "- Kijiko 1/2 cha chumvi\n"
            "- Changanya vizuri\n"
            "Kunywa: Glasi 1 baada ya kila kuhara\n"
            "Watoto: Kijiko 1 kila dakika 5"
        )

    elif text == '2*6*3':
        return respond(
            "END 💊 Metronidazole (Flagyl):\n"
            "Matumizi: Kuhara, maambukizo ya\n"
            "utumbo, maambukizo ya ukeni\n"
            "Dozi ya kawaida: 400mg mara 3/siku\n"
            "kwa siku 5-7\n"
            "⚠️ Lazima upate dawa kwa DAKTARI\n"
            "⚠️ Usitumie na pombe - hatari sana!\n"
            "⚠️ Usitumie wakati wa ujauzito bila ushauri"
        )

    elif text == '2*6*4':
        return respond(
            "END 💊 Amoxicillin:\n"
            "Matumizi: Maambukizo ya bakteria -\n"
            "maumivu ya koo, sikio, mkojo, ngozi\n"
            "Dozi ya kawaida: 500mg mara 3/siku\n"
            "kwa siku 7-10\n"
            "⚠️ Lazima upate dawa kwa DAKTARI\n"
            "⚠️ Kamilisha dozi yote hata ukijisikia vizuri\n"
            "⚠️ Angalia mzio - ukipata upele: simama!"
        )

    elif text == '2*6*5':
        return respond(
            "END 💊 Dawa za Malaria:\n"
            "ALU (Artemether+Lumefantrine):\n"
            "Mtu Mzima: Vidonge 4 mara 2/siku x 3 siku\n"
            "Kunywa na chakula chenye mafuta\n"
            "Malaraquin (Chloroquine):\n"
            "Sasa inashindwa katika maeneo mengi\n"
            "⚠️ Pima damu kwanza kabla ya kutumia\n"
            "⚠️ Malaria ya ubongo: Hospitali HARAKA!\n"
            "⚠️ Watoto: Dozi inahesabiwa kwa uzito"
        )

    # ══════════════════════════════════════════
    #  GLOBAL BACK / EXIT
    # ══════════════════════════════════════════

    elif text == '0':
        return respond(
            "END Asante kutumia huduma yetu!\n"
            "Shamba bora, afya bora - maisha bora! 🌾🏥\n"
            "Powered by JamiiTek"
        )

    # ── Catch-all ─────────────────────────────
    else:
        return respond("END Samahani, chaguo hilo halipo.\nTafadhali anza upya.")