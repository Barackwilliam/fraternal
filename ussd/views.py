from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def respond(text):
    return HttpResponse(text, content_type='text/plain')


def is_sw(text):
    """Return True if user chose Kiswahili (first digit = 1)."""
    parts = text.split('*')
    return len(parts) > 0 and parts[0] == '1'


# ─────────────────────────────────────────────
#  MAIN VIEW
# ─────────────────────────────────────────────
@csrf_exempt
def ussd_callback(request):
    if request.method != 'POST':
        return respond("Shamba Mfukoni & AfyaPlus USSD inafanya kazi! ✅")

    text = request.POST.get('text', '').strip()

    # ══════════════════════════════════════════
    #  STEP 0 — LANGUAGE SELECTION
    # ══════════════════════════════════════════
    if text == '':
        return respond(
            "CON Welcome! / Karibu!\n"
            "Chagua lugha / Select language:\n"
            "1. Kiswahili\n"
            "2. English"
        )

    # ══════════════════════════════════════════
    #  STEP 1 — MAIN MENU  (1=SW, 2=EN)
    # ══════════════════════════════════════════
    if text == '1':
        return respond(
            "CON Karibu! Chagua huduma:\n"
            "1. Kilimo\n"
            "2. Afya\n"
            "0. Toka"
        )

    if text == '2':
        return respond(
            "CON Welcome! Choose a service:\n"
            "1. Agriculture\n"
            "2. Health\n"
            "0. Exit"
        )

    # ── Global back to language selection ─────
    # (user presses 0 at main menu)
    if text in ('1*0', '2*0'):
        return respond(
            "END Asante / Thank you!\n"
            "Shamba bora, afya bora! 🌾🏥"
        )

    sw = is_sw(text)  # True if Kiswahili branch

    # ══════════════════════════════════════════
    #  KILIMO / AGRICULTURE BRANCH
    # ══════════════════════════════════════════

    # ── Level 2 — Kilimo menu ─────────────────
    if text in ('1*1', '2*1'):
        if sw:
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
        else:
            return respond(
                "CON 🌾 AGRICULTURE - Choose:\n"
                "1. Weather Forecast\n"
                "2. Market Prices\n"
                "3. Crop Doctor\n"
                "4. Fertilizer & Pesticides\n"
                "5. Irrigation Guide\n"
                "6. Planting Calendar\n"
                "0. Back"
            )

    # ── Kilimo > Hali ya Hewa / Weather ──────
    if text in ('1*1*1', '2*1*1'):
        if sw:
            return respond(
                "CON 🌦️ Chagua mkoa:\n"
                "1. Dar es Salaam\n"
                "2. Arusha\n"
                "3. Mwanza\n"
                "4. Dodoma\n"
                "5. Mbeya\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🌦️ Select region:\n"
                "1. Dar es Salaam\n"
                "2. Arusha\n"
                "3. Mwanza\n"
                "4. Dodoma\n"
                "5. Mbeya\n"
                "0. Back"
            )

    if text in ('1*1*1*1', '2*1*1*1'):
        if sw:
            return respond(
                "END 🌦️ Dar es Salaam:\n"
                "Leo: Jua, 32°C, Unyevu 78%\n"
                "Kesho: Mvua asubuhi, 28°C\n"
                "Ushauri: Epuka kupanda mbegu wiki hii.\n"
                "Mwagilia asubuhi mapema."
            )
        else:
            return respond(
                "END 🌦️ Dar es Salaam:\n"
                "Today: Sunny, 32°C, Humidity 78%\n"
                "Tomorrow: Morning rain, 28°C\n"
                "Advice: Avoid planting seeds this week.\n"
                "Irrigate in the early morning."
            )

    if text in ('1*1*1*2', '2*1*1*2'):
        if sw:
            return respond(
                "END 🌦️ Arusha:\n"
                "Leo: Mawingu, 22°C, Unyevu 65%\n"
                "Kesho: Jua, 24°C\n"
                "Ushauri: Mazingira mazuri ya kupanda.\n"
                "Hasa mahindi na mboga za majani."
            )
        else:
            return respond(
                "END 🌦️ Arusha:\n"
                "Today: Cloudy, 22°C, Humidity 65%\n"
                "Tomorrow: Sunny, 24°C\n"
                "Advice: Good conditions for planting.\n"
                "Especially maize and leafy vegetables."
            )

    if text in ('1*1*1*3', '2*1*1*3'):
        if sw:
            return respond(
                "END 🌦️ Mwanza:\n"
                "Leo: Jua kali, 34°C, Unyevu 55%\n"
                "Kesho: Jua, 33°C\n"
                "Ushauri: Mwagilia mara mbili kwa siku.\n"
                "Tumia matandazo kulinda udongo."
            )
        else:
            return respond(
                "END 🌦️ Mwanza:\n"
                "Today: Hot sun, 34°C, Humidity 55%\n"
                "Tomorrow: Sunny, 33°C\n"
                "Advice: Irrigate twice per day.\n"
                "Use mulch to protect the soil."
            )

    if text in ('1*1*1*4', '2*1*1*4'):
        if sw:
            return respond(
                "END 🌦️ Dodoma:\n"
                "Leo: Kavu, 30°C, Unyevu 40%\n"
                "Kesho: Kavu, 31°C\n"
                "Ushauri: Msimu wa kiangazi. Tumia\n"
                "mazao yanayostahimili ukame."
            )
        else:
            return respond(
                "END 🌦️ Dodoma:\n"
                "Today: Dry, 30°C, Humidity 40%\n"
                "Tomorrow: Dry, 31°C\n"
                "Advice: Dry season. Use\n"
                "drought-resistant crops."
            )

    if text in ('1*1*1*5', '2*1*1*5'):
        if sw:
            return respond(
                "END 🌦️ Mbeya:\n"
                "Leo: Baridi, 18°C, Unyevu 80%\n"
                "Kesho: Mvua kidogo, 17°C\n"
                "Ushauri: Hali nzuri kwa chai na kahawa.\n"
                "Angalia kuoza kwa viazi."
            )
        else:
            return respond(
                "END 🌦️ Mbeya:\n"
                "Today: Cool, 18°C, Humidity 80%\n"
                "Tomorrow: Light rain, 17°C\n"
                "Advice: Good for tea and coffee.\n"
                "Watch for potato rot."
            )

    # ── Kilimo > Bei za Soko / Market Prices ──
    if text in ('1*1*2', '2*1*2'):
        if sw:
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
        else:
            return respond(
                "CON 💰 Market Prices - Select crop:\n"
                "1. Maize\n"
                "2. Beans\n"
                "3. Rice\n"
                "4. Tomatoes\n"
                "5. Bananas\n"
                "6. Cassava\n"
                "0. Back"
            )

    if text in ('1*1*2*1', '2*1*2*1'):
        if sw:
            return respond(
                "END 🌽 Bei ya Mahindi (kwa kg):\n"
                "Dar es Salaam: TZS 850\n"
                "Arusha:        TZS 780\n"
                "Mwanza:        TZS 720\n"
                "Dodoma:        TZS 700\n"
                "Mbeya:         TZS 650\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🌽 Maize Price (per kg):\n"
                "Dar es Salaam: TZS 850\n"
                "Arusha:        TZS 780\n"
                "Mwanza:        TZS 720\n"
                "Dodoma:        TZS 700\n"
                "Mbeya:         TZS 650\n"
                "Source: Kariakoo Market"
            )

    if text in ('1*1*2*2', '2*1*2*2'):
        if sw:
            return respond(
                "END 🫘 Bei ya Maharagwe (kwa kg):\n"
                "Dar es Salaam: TZS 2,600\n"
                "Arusha:        TZS 2,300\n"
                "Mwanza:        TZS 2,100\n"
                "Dodoma:        TZS 2,000\n"
                "Mbeya:         TZS 1,900\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🫘 Beans Price (per kg):\n"
                "Dar es Salaam: TZS 2,600\n"
                "Arusha:        TZS 2,300\n"
                "Mwanza:        TZS 2,100\n"
                "Dodoma:        TZS 2,000\n"
                "Mbeya:         TZS 1,900\n"
                "Source: Kariakoo Market"
            )

    if text in ('1*1*2*3', '2*1*2*3'):
        if sw:
            return respond(
                "END 🌾 Bei ya Mpunga (kwa kg):\n"
                "Dar es Salaam: TZS 1,300\n"
                "Arusha:        TZS 1,150\n"
                "Mwanza:        TZS 1,050\n"
                "Dodoma:        TZS 1,000\n"
                "Mbeya:         TZS 950\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🌾 Rice Price (per kg):\n"
                "Dar es Salaam: TZS 1,300\n"
                "Arusha:        TZS 1,150\n"
                "Mwanza:        TZS 1,050\n"
                "Dodoma:        TZS 1,000\n"
                "Mbeya:         TZS 950\n"
                "Source: Kariakoo Market"
            )

    if text in ('1*1*2*4', '2*1*2*4'):
        if sw:
            return respond(
                "END 🍅 Bei ya Nyanya (kwa kg):\n"
                "Dar es Salaam: TZS 1,800\n"
                "Arusha:        TZS 1,500\n"
                "Mwanza:        TZS 1,400\n"
                "Dodoma:        TZS 1,200\n"
                "Mbeya:         TZS 1,100\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🍅 Tomatoes Price (per kg):\n"
                "Dar es Salaam: TZS 1,800\n"
                "Arusha:        TZS 1,500\n"
                "Mwanza:        TZS 1,400\n"
                "Dodoma:        TZS 1,200\n"
                "Mbeya:         TZS 1,100\n"
                "Source: Kariakoo Market"
            )

    if text in ('1*1*2*5', '2*1*2*5'):
        if sw:
            return respond(
                "END 🍌 Bei ya Ndizi (kwa bunchi):\n"
                "Dar es Salaam: TZS 5,000\n"
                "Arusha:        TZS 4,500\n"
                "Mwanza:        TZS 4,000\n"
                "Dodoma:        TZS 3,500\n"
                "Mbeya:         TZS 3,000\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🍌 Banana Price (per bunch):\n"
                "Dar es Salaam: TZS 5,000\n"
                "Arusha:        TZS 4,500\n"
                "Mwanza:        TZS 4,000\n"
                "Dodoma:        TZS 3,500\n"
                "Mbeya:         TZS 3,000\n"
                "Source: Kariakoo Market"
            )

    if text in ('1*1*2*6', '2*1*2*6'):
        if sw:
            return respond(
                "END 🍠 Bei ya Mihogo (kwa kg):\n"
                "Dar es Salaam: TZS 600\n"
                "Arusha:        TZS 550\n"
                "Mwanza:        TZS 500\n"
                "Dodoma:        TZS 480\n"
                "Mbeya:         TZS 450\n"
                "Chanzo: Soko la Kariakoo"
            )
        else:
            return respond(
                "END 🍠 Cassava Price (per kg):\n"
                "Dar es Salaam: TZS 600\n"
                "Arusha:        TZS 550\n"
                "Mwanza:        TZS 500\n"
                "Dodoma:        TZS 480\n"
                "Mbeya:         TZS 450\n"
                "Source: Kariakoo Market"
            )

    # ── Kilimo > Daktari wa Mazao / Crop Doctor ─
    if text in ('1*1*3', '2*1*3'):
        if sw:
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
        else:
            return respond(
                "CON 🌿 Crop Doctor:\n"
                "1. Leaves turning yellow\n"
                "2. Leaves with black spots\n"
                "3. Insects on plants\n"
                "4. Plant wilting\n"
                "5. Fruits rotting\n"
                "6. Roots rotting\n"
                "0. Back"
            )

    if text in ('1*1*3*1', '2*1*3*1'):
        if sw:
            return respond(
                "END 🟡 Majani Njano:\n"
                "Sababu zinazowezekana:\n"
                "- Upungufu wa Nitrogen\n"
                "- Maji mengi sana\n"
                "- Ugonjwa wa Chlorosis\n"
                "Suluhisho: Weka Urea 50kg/ekari.\n"
                "Angalia mfumo wa maji usizidi."
            )
        else:
            return respond(
                "END 🟡 Yellow Leaves:\n"
                "Possible causes:\n"
                "- Nitrogen deficiency\n"
                "- Overwatering\n"
                "- Chlorosis disease\n"
                "Solution: Apply Urea 50kg/acre.\n"
                "Check drainage system."
            )

    if text in ('1*1*3*2', '2*1*3*2'):
        if sw:
            return respond(
                "END ⚫ Madoa Meusi:\n"
                "Sababu: Ugonjwa wa kuvu (Fungal)\n"
                "Mara nyingi: Early/Late Blight\n"
                "Suluhisho:\n"
                "- Nyunyizia Mancozeb au Ridomil\n"
                "- Ondoa majani yaliyoathirika\n"
                "- Usimwagilie jioni"
            )
        else:
            return respond(
                "END ⚫ Black Spots:\n"
                "Cause: Fungal disease\n"
                "Often: Early/Late Blight\n"
                "Solution:\n"
                "- Spray Mancozeb or Ridomil\n"
                "- Remove affected leaves\n"
                "- Do not irrigate in the evening"
            )

    if text in ('1*1*3*3', '2*1*3*3'):
        if sw:
            return respond(
                "END 🐛 Wadudu:\n"
                "Aphids: Nyunyizia Imidacloprid\n"
                "Thrips: Tumia Lambda-cyhalothrin\n"
                "Viwavi: Tumia Bt (Bacillus thuringiensis)\n"
                "Vidukari: Nyunyizia mafuta ya taa\n"
                "Omba dawa asubuhi au jioni tu."
            )
        else:
            return respond(
                "END 🐛 Insects:\n"
                "Aphids: Spray Imidacloprid\n"
                "Thrips: Use Lambda-cyhalothrin\n"
                "Caterpillars: Use Bt (Bacillus thuringiensis)\n"
                "Mites: Spray paraffin oil\n"
                "Apply pesticides morning or evening only."
            )

    if text in ('1*1*3*4', '2*1*3*4'):
        if sw:
            return respond(
                "END 🥀 Mmea Kunyauka:\n"
                "Sababu zinazowezekana:\n"
                "- Ukosefu wa maji\n"
                "- Ugonjwa wa Fusarium Wilt\n"
                "- Mizizi iliyooza\n"
                "Suluhisho: Mwagilia sasa. Kama bado\n"
                "unyauka, ng'oa na angalia mizizi."
            )
        else:
            return respond(
                "END 🥀 Plant Wilting:\n"
                "Possible causes:\n"
                "- Water shortage\n"
                "- Fusarium Wilt disease\n"
                "- Rotted roots\n"
                "Solution: Irrigate immediately. If still\n"
                "wilting, uproot and inspect roots."
            )

    if text in ('1*1*3*5', '2*1*3*5'):
        if sw:
            return respond(
                "END 🍅 Matunda Kuoza:\n"
                "Sababu: Anthracnose au Blossom End Rot\n"
                "Suluhisho:\n"
                "- Weka chokaa (Calcium) kwenye udongo\n"
                "- Nyunyizia Copper Oxychloride\n"
                "- Vuna mapema matunda yaliyoiva"
            )
        else:
            return respond(
                "END 🍅 Fruit Rotting:\n"
                "Cause: Anthracnose or Blossom End Rot\n"
                "Solution:\n"
                "- Apply lime (Calcium) to soil\n"
                "- Spray Copper Oxychloride\n"
                "- Harvest ripe fruits early"
            )

    if text in ('1*1*3*6', '2*1*3*6'):
        if sw:
            return respond(
                "END 🌱 Mizizi Kuoza:\n"
                "Sababu: Maji yasiyotoka (waterlogging)\n"
                "au ugonjwa wa Pythium\n"
                "Suluhisho:\n"
                "- Tengeneza mifereji ya maji\n"
                "- Tumia Metalaxyl kwenye udongo\n"
                "- Badilisha eneo la kupanda"
            )
        else:
            return respond(
                "END 🌱 Root Rotting:\n"
                "Cause: Waterlogging or Pythium disease\n"
                "Solution:\n"
                "- Build drainage channels\n"
                "- Apply Metalaxyl to soil\n"
                "- Change planting location"
            )

    # ── Kilimo > Mbolea & Viuatilifu / Fertilizer ─
    if text in ('1*1*4', '2*1*4'):
        if sw:
            return respond(
                "CON 🧪 Mbolea & Viuatilifu:\n"
                "1. Mbolea kwa Mahindi\n"
                "2. Mbolea kwa Mpunga\n"
                "3. Mbolea kwa Mboga\n"
                "4. Mbolea ya Asili (Organic)\n"
                "5. Tahadhari za Dawa\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🧪 Fertilizer & Pesticides:\n"
                "1. Fertilizer for Maize\n"
                "2. Fertilizer for Rice\n"
                "3. Fertilizer for Vegetables\n"
                "4. Organic Fertilizer\n"
                "5. Pesticide Safety Tips\n"
                "0. Back"
            )

    if text in ('1*1*4*1', '2*1*4*1'):
        if sw:
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
        else:
            return respond(
                "END 🌽 Fertilizer - Maize:\n"
                "At planting:\n"
                "- DAP: 50kg per acre\n"
                "3-4 weeks after planting:\n"
                "- Urea: 50kg per acre\n"
                "6-8 weeks:\n"
                "- CAN: 25kg per acre\n"
                "Place beside the plant, not on top."
            )

    if text in ('1*1*4*2', '2*1*4*2'):
        if sw:
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
        else:
            return respond(
                "END 🌾 Fertilizer - Rice:\n"
                "At planting:\n"
                "- NPK (17:17:17): 60kg/acre\n"
                "Week 3 after planting:\n"
                "- Urea: 40kg/acre\n"
                "Week 8 (panicle initiation):\n"
                "- Urea: 30kg/acre\n"
                "Apply inside the paddy water."
            )

    if text in ('1*1*4*3', '2*1*4*3'):
        if sw:
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
        else:
            return respond(
                "END 🥬 Fertilizer - Vegetables:\n"
                "Before planting:\n"
                "- Decomposed manure: 4 tins/bed\n"
                "After 2 weeks:\n"
                "- CAN or Urea: 1 teaspoon/plant\n"
                "Every 2 weeks:\n"
                "- Foliar fertilizer spray\n"
                "Irrigate immediately after applying fertilizer."
            )

    if text in ('1*1*4*4', '2*1*4*4'):
        if sw:
            return respond(
                "END ♻️ Mbolea ya Asili:\n"
                "Samadi ya ng'ombe: bora sana\n"
                "Mboji (Compost): inaboresha udongo\n"
                "Mbolea ya kijani: panda Tithonia\n"
                "Mkojo wa ng'ombe: punguza 1:10 na maji\n"
                "Faida: Bei nafuu, udongo unabaki\n"
                "na afya kwa miaka mingi."
            )
        else:
            return respond(
                "END ♻️ Organic Fertilizer:\n"
                "Cow manure: excellent choice\n"
                "Compost: improves soil structure\n"
                "Green manure: plant Tithonia\n"
                "Cow urine: dilute 1:10 with water\n"
                "Benefits: Low cost, keeps soil\n"
                "healthy for many years."
            )

    if text in ('1*1*4*5', '2*1*4*5'):
        if sw:
            return respond(
                "END ⚠️ Tahadhari za Dawa:\n"
                "- Vaa glavu na barakoa daima\n"
                "- Usinyunyizie wakati wa upepo\n"
                "- Omba asubuhi (6-9am) au jioni\n"
                "- Usiruke siku za kulinda\n"
                "- Hifadhi mbali na watoto\n"
                "- Soma maelekezo ya chupa kila wakati"
            )
        else:
            return respond(
                "END ⚠️ Pesticide Safety Tips:\n"
                "- Always wear gloves and a mask\n"
                "- Do not spray in windy conditions\n"
                "- Spray morning (6-9am) or evening\n"
                "- Do not skip protective days\n"
                "- Store away from children\n"
                "- Read bottle instructions every time"
            )

    # ── Kilimo > Umwagiliaji / Irrigation ─────
    if text in ('1*1*5', '2*1*5'):
        if sw:
            return respond(
                "CON 💧 Umwagiliaji - Chagua zao:\n"
                "1. Mahindi\n"
                "2. Nyanya\n"
                "3. Mboga za majani\n"
                "4. Ndizi\n"
                "5. Miwa\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 💧 Irrigation - Select crop:\n"
                "1. Maize\n"
                "2. Tomatoes\n"
                "3. Leafy Vegetables\n"
                "4. Bananas\n"
                "5. Sugarcane\n"
                "0. Back"
            )

    if text in ('1*1*5*1', '2*1*5*1'):
        if sw:
            return respond(
                "END 💧 Umwagiliaji - Mahindi:\n"
                "Kiasi: Lita 5-7 kwa mmea/wiki\n"
                "Wakati muhimu:\n"
                "- Kipindi cha kuota (germination)\n"
                "- Wakati wa maua (tasseling)\n"
                "- Wakati wa punje kujaa (grain fill)\n"
                "Epuka maji mengi wakati wa mavuno."
            )
        else:
            return respond(
                "END 💧 Irrigation - Maize:\n"
                "Amount: 5-7 litres per plant/week\n"
                "Critical stages:\n"
                "- Germination period\n"
                "- Tasseling stage\n"
                "- Grain filling stage\n"
                "Avoid excess water near harvest."
            )

    if text in ('1*1*5*2', '2*1*5*2'):
        if sw:
            return respond(
                "END 💧 Umwagiliaji - Nyanya:\n"
                "Kiasi: Lita 3-5 kwa mmea/siku\n"
                "Mwagilia: Kila siku asubuhi\n"
                "Epuka: Kumwagilia majani\n"
                "Tumia: Drip irrigation ikiwezekana\n"
                "Maji yasiyolingana husababisha\n"
                "matunda kupasuka."
            )
        else:
            return respond(
                "END 💧 Irrigation - Tomatoes:\n"
                "Amount: 3-5 litres per plant/day\n"
                "Irrigate: Every morning\n"
                "Avoid: Watering leaves directly\n"
                "Use: Drip irrigation if possible\n"
                "Inconsistent watering causes\n"
                "fruit cracking."
            )

    if text in ('1*1*5*3', '2*1*5*3'):
        if sw:
            return respond(
                "END 💧 Umwagiliaji - Mboga:\n"
                "Kiasi: Lita 2-3/m² kila siku\n"
                "Mwagilia: Asubuhi na jioni\n"
                "Matumizi ya kisasa:\n"
                "- Mulching hupunguza uvukizi\n"
                "- Watering can ni bora kuliko bomba\n"
                "Angalia udongo usiwe na maji mengi."
            )
        else:
            return respond(
                "END 💧 Irrigation - Vegetables:\n"
                "Amount: 2-3 litres/m² per day\n"
                "Irrigate: Morning and evening\n"
                "Modern tips:\n"
                "- Mulching reduces evaporation\n"
                "- Watering can is better than a pipe\n"
                "Ensure soil is not waterlogged."
            )

    if text in ('1*1*5*4', '2*1*5*4'):
        if sw:
            return respond(
                "END 💧 Umwagiliaji - Ndizi:\n"
                "Kiasi: Lita 10-15/mmea/wiki\n"
                "Ndizi zinahitaji maji mengi sana\n"
                "Mwagilia: Mara 2-3 kwa wiki\n"
                "Hakikisha mifereji ya maji ipo\n"
                "Maji yaliyosimama huoza mizizi."
            )
        else:
            return respond(
                "END 💧 Irrigation - Bananas:\n"
                "Amount: 10-15 litres/plant/week\n"
                "Bananas need a lot of water\n"
                "Irrigate: 2-3 times per week\n"
                "Ensure drainage channels are present\n"
                "Standing water will rot the roots."
            )

    if text in ('1*1*5*5', '2*1*5*5'):
        if sw:
            return respond(
                "END 💧 Umwagiliaji - Miwa:\n"
                "Kiasi: 1200-1500mm/msimu mzima\n"
                "Hatua muhimu:\n"
                "- Baada ya kupanda: mwagilia vizuri\n"
                "- Mwezi 1-3: mara kwa mara\n"
                "- Mwezi 4-8: punguza maji\n"
                "- Wiki 6 kabla ya kuvuna: acha maji"
            )
        else:
            return respond(
                "END 💧 Irrigation - Sugarcane:\n"
                "Amount: 1200-1500mm/full season\n"
                "Key stages:\n"
                "- After planting: irrigate well\n"
                "- Month 1-3: irrigate frequently\n"
                "- Month 4-8: reduce water\n"
                "- 6 weeks before harvest: stop watering"
            )

    # ── Kilimo > Kalenda ya Kupanda / Planting Calendar ─
    if text in ('1*1*6', '2*1*6'):
        if sw:
            return respond(
                "CON 📅 Kalenda ya Kupanda:\n"
                "1. Msimu wa Masika (Mar-Jun)\n"
                "2. Msimu wa Vuli (Oct-Dec)\n"
                "3. Kilimo cha Umwagiliaji\n"
                "4. Mazao ya Miaka Mingi\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 📅 Planting Calendar:\n"
                "1. Long Rains Season (Mar-Jun)\n"
                "2. Short Rains Season (Oct-Dec)\n"
                "3. Irrigation Farming\n"
                "4. Perennial Crops\n"
                "0. Back"
            )

    if text in ('1*1*6*1', '2*1*6*1'):
        if sw:
            return respond(
                "END 🌧️ Msimu wa Masika:\n"
                "Mar-Apr: Panda mahindi, mpunga,\n"
                "maharagwe, nyanya, vitunguu\n"
                "Apr-May: Panda mihogo, viazi,\n"
                "mboga za majani\n"
                "Jun: Vuna mazao ya mapema\n"
                "Fursa nzuri kwa Tanzania Bara."
            )
        else:
            return respond(
                "END 🌧️ Long Rains Season:\n"
                "Mar-Apr: Plant maize, rice,\n"
                "beans, tomatoes, onions\n"
                "Apr-May: Plant cassava, potatoes,\n"
                "leafy vegetables\n"
                "Jun: Harvest early crops\n"
                "Great opportunity for Mainland Tanzania."
            )

    if text in ('1*1*6*2', '2*1*6*2'):
        if sw:
            return respond(
                "END 🍂 Msimu wa Vuli:\n"
                "Oct-Nov: Panda mahindi (fupi),\n"
                "maharagwe, mboga\n"
                "Nov-Dec: Panda vitunguu saumu,\n"
                "nyanya, pilipili\n"
                "Feb-Mar: Vuna mazao ya Vuli\n"
                "Msimu mfupi - chagua aina za haraka."
            )
        else:
            return respond(
                "END 🍂 Short Rains Season:\n"
                "Oct-Nov: Plant short-season maize,\n"
                "beans, vegetables\n"
                "Nov-Dec: Plant garlic, tomatoes,\n"
                "peppers\n"
                "Feb-Mar: Harvest short-rains crops\n"
                "Short season - choose fast-maturing varieties."
            )

    if text in ('1*1*6*3', '2*1*6*3'):
        if sw:
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
        else:
            return respond(
                "END 🚿 Irrigation Farming:\n"
                "You can plant all year round!\n"
                "Best crops:\n"
                "- Vegetables (harvest 6-8 weeks)\n"
                "- Tomatoes (10-12 weeks)\n"
                "- Onions (12-16 weeks)\n"
                "- Kale/Sukuma (always)\n"
                "Requirement: Water source nearby."
            )

    if text in ('1*1*6*4', '2*1*6*4'):
        if sw:
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
        else:
            return respond(
                "END 🌳 Perennial Crops:\n"
                "Plant any time during rains:\n"
                "- Mangoes: Harvest after 3-5 years\n"
                "- Oranges: 3-4 years\n"
                "- Coffee: 3-4 years\n"
                "- Bananas: 1-2 years\n"
                "- Avocado: 3-5 years\n"
                "Long-term investment, plant today!"
            )

    # ── Back options for Kilimo sub-menus ─────
    # Going back from level-3 → level-2 (Kilimo menu)
    if text in ('1*1*1*0', '2*1*1*0'):
        if sw:
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
        else:
            return respond(
                "CON 🌾 AGRICULTURE - Choose:\n"
                "1. Weather Forecast\n"
                "2. Market Prices\n"
                "3. Crop Doctor\n"
                "4. Fertilizer & Pesticides\n"
                "5. Irrigation Guide\n"
                "6. Planting Calendar\n"
                "0. Back"
            )

    # Going back from level-2 Kilimo → main menu
    if text in ('1*1*0', '2*1*0'):
        if sw:
            return respond(
                "CON Karibu! Chagua huduma:\n"
                "1. Kilimo\n"
                "2. Afya\n"
                "0. Toka"
            )
        else:
            return respond(
                "CON Welcome! Choose a service:\n"
                "1. Agriculture\n"
                "2. Health\n"
                "0. Exit"
            )

    # ══════════════════════════════════════════
    #  AFYA / HEALTH BRANCH
    # ══════════════════════════════════════════

    # ── Level 2 — Afya menu ───────────────────
    if text in ('1*2', '2*2'):
        if sw:
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
        else:
            return respond(
                "CON 🏥 HEALTH - Choose:\n"
                "1. Disease Symptoms\n"
                "2. Mother & Child\n"
                "3. Vaccines & Prevention\n"
                "4. Nutrition & Clean Water\n"
                "5. Mental Health\n"
                "6. Common Medicines\n"
                "0. Back"
            )

    # ── Afya > Dalili za Magonjwa / Symptoms ──
    if text in ('1*2*1', '2*2*1'):
        if sw:
            return respond(
                "CON 🌡️ Dalili za Magonjwa:\n"
                "1. Homa na Baridi\n"
                "2. Kuhara na Kutapika\n"
                "3. Kikohozi na Mafua\n"
                "4. Maumivu ya Tumbo\n"
                "5. Upele wa Ngozi\n"
                "6. Maumivu ya Kichwa\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🌡️ Disease Symptoms:\n"
                "1. Fever & Chills\n"
                "2. Diarrhoea & Vomiting\n"
                "3. Cough & Cold\n"
                "4. Stomach Pain\n"
                "5. Skin Rash\n"
                "6. Headache\n"
                "0. Back"
            )

    if text in ('1*2*1*1', '2*2*1*1'):
        if sw:
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
        else:
            return respond(
                "END 🌡️ Fever & Chills:\n"
                "Could be: Malaria, Typhoid,\n"
                "Dengue or Flu\n"
                "Quick steps:\n"
                "1. Check temp - >38°C is fever\n"
                "2. Drink plenty of water\n"
                "3. Use Paracetamol to reduce fever\n"
                "⚠️ If fever >3 days: Go to hospital!"
            )

    if text in ('1*2*1*2', '2*2*1*2'):
        if sw:
            return respond(
                "END 🤢 Kuhara na Kutapika:\n"
                "Inaweza kuwa: Kipindupindu, Typhoid\n"
                "au Sumu ya chakula\n"
                "Hatua:\n"
                "1. Kunywa ORS (maji + chumvi + sukari)\n"
                "2. Epuka vyakula vya mafuta\n"
                "3. Osha mikono mara kwa mara\n"
                "⚠️ Kama kuhara >5 mara/siku: Hospitali!"
            )
        else:
            return respond(
                "END 🤢 Diarrhoea & Vomiting:\n"
                "Could be: Cholera, Typhoid\n"
                "or Food poisoning\n"
                "Steps:\n"
                "1. Drink ORS (water + salt + sugar)\n"
                "2. Avoid fatty foods\n"
                "3. Wash hands frequently\n"
                "⚠️ If diarrhoea >5 times/day: Hospital!"
            )

    if text in ('1*2*1*3', '2*2*1*3'):
        if sw:
            return respond(
                "END 😷 Kikohozi na Mafua:\n"
                "Inaweza kuwa: Flu, COVID, TB, Pumu\n"
                "Hatua:\n"
                "1. Pumzika na kunywa maji ya moto\n"
                "2. Vuta mvuke wa maji ya moto + chumvi\n"
                "3. Tumia asali na limao\n"
                "⚠️ Kikohozi >2 wiki au damu: Hospitali!"
            )
        else:
            return respond(
                "END 😷 Cough & Cold:\n"
                "Could be: Flu, COVID, TB, Asthma\n"
                "Steps:\n"
                "1. Rest and drink warm water\n"
                "2. Inhale steam of hot water + salt\n"
                "3. Use honey and lemon\n"
                "⚠️ Cough >2 weeks or blood: Hospital!"
            )

    if text in ('1*2*1*4', '2*2*1*4'):
        if sw:
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
        else:
            return respond(
                "END 🫃 Stomach Pain:\n"
                "Could be: Ulcer, Appendicitis,\n"
                "Gas or Typhoid\n"
                "Steps:\n"
                "1. Rest, avoid spicy foods\n"
                "2. Drink warm water\n"
                "3. Apply heat (hot water bottle)\n"
                "⚠️ Severe right-side pain: Hospital NOW!"
            )

    if text in ('1*2*1*5', '2*2*1*5'):
        if sw:
            return respond(
                "END 🔴 Upele wa Ngozi:\n"
                "Inaweza kuwa: Ugonjwa wa ngozi,\n"
                "Mzio, Tetekuwanga au Ukimwi\n"
                "Hatua:\n"
                "1. Usikwarue - utaeneza maambukizo\n"
                "2. Tumia sabuni ya upole\n"
                "3. Weka cream ya Calamine\n"
                "⚠️ Upele + homa + maumivu: Hospitali haraka!"
            )
        else:
            return respond(
                "END 🔴 Skin Rash:\n"
                "Could be: Skin disease, Allergy,\n"
                "Chickenpox or HIV\n"
                "Steps:\n"
                "1. Do not scratch - spreads infection\n"
                "2. Use mild soap\n"
                "3. Apply Calamine cream\n"
                "⚠️ Rash + fever + pain: Hospital fast!"
            )

    if text in ('1*2*1*6', '2*2*1*6'):
        if sw:
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
        else:
            return respond(
                "END 🤕 Headache:\n"
                "Could be: Stress, High blood pressure,\n"
                "Malaria or Meningitis\n"
                "Steps:\n"
                "1. Rest in a dark, quiet place\n"
                "2. Take Paracetamol or Ibuprofen\n"
                "3. Drink water - dehydration causes it\n"
                "⚠️ Head + stiff neck + fever: Hospital NOW!"
            )

    # ── Afya > Mama na Mtoto / Mother & Child ─
    if text in ('1*2*2', '2*2*2'):
        if sw:
            return respond(
                "CON 🤰 Mama na Mtoto:\n"
                "1. Dalili za Mimba ya Hatari\n"
                "2. Lishe ya Mama Mjamzito\n"
                "3. Chanjo za Mtoto\n"
                "4. Ukuaji wa Mtoto\n"
                "5. Kunyonyesha\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🤰 Mother & Child:\n"
                "1. Danger Signs in Pregnancy\n"
                "2. Nutrition for Pregnant Mothers\n"
                "3. Child Vaccines\n"
                "4. Child Development\n"
                "5. Breastfeeding\n"
                "0. Back"
            )

    if text in ('1*2*2*1', '2*2*2*1'):
        if sw:
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
        else:
            return respond(
                "END ⚠️ Danger Signs in Pregnancy:\n"
                "Go to hospital IMMEDIATELY if you see:\n"
                "- Vaginal bleeding at any time\n"
                "- Severe stomach pains\n"
                "- Baby moving very little\n"
                "- Sudden swelling of legs/face\n"
                "- Severe headache\n"
                "- Blurred vision\n"
                "Don't wait - call for help now!"
            )

    if text in ('1*2*2*2', '2*2*2*2'):
        if sw:
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
        else:
            return respond(
                "END 🥗 Nutrition for Pregnant Mothers:\n"
                "Eat daily:\n"
                "- Grains: ugali, rice, bread\n"
                "- Protein: meat, fish, beans\n"
                "- Vitamins: fruits and vegetables\n"
                "- Iron: liver, lentils, spinach\n"
                "- Folate: peanuts, green vegetables\n"
                "Drink 2-3 litres of water daily.\n"
                "Avoid alcohol and smoking completely."
            )

    if text in ('1*2*2*3', '2*2*2*3'):
        if sw:
            return respond(
                "END 💉 Chanjo za Mtoto (Tanzania):\n"
                "Kuzaliwa: BCG + OPV0\n"
                "Miezi 6: OPV1 + DTP + Hib + HepB\n"
                "Miezi 10: OPV2 + DTP + Hib + HepB\n"
                "Miezi 14: OPV3 + DTP + Hib + HepB\n"
                "Miezi 9: Surua + Meningitis\n"
                "Miaka 2: Kichaa cha mbwa\n"
                "Chanjo ZOTE ni BURE kliniki ya serikali!"
            )
        else:
            return respond(
                "END 💉 Child Vaccines (Tanzania):\n"
                "At birth: BCG + OPV0\n"
                "Month 6: OPV1 + DTP + Hib + HepB\n"
                "Month 10: OPV2 + DTP + Hib + HepB\n"
                "Month 14: OPV3 + DTP + Hib + HepB\n"
                "Month 9: Measles + Meningitis\n"
                "Year 2: Rabies\n"
                "ALL vaccines are FREE at govt clinics!"
            )

    if text in ('1*2*2*4', '2*2*2*4'):
        if sw:
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
        else:
            return respond(
                "END 📏 Child Development:\n"
                "Months 1-3: Sees, hears, smiles\n"
                "Months 4-6: Grasps objects, turns head\n"
                "Months 7-9: Sits alone\n"
                "Months 10-12: Takes first steps\n"
                "Years 1-2: 10-50 words\n"
                "⚠️ Child not reaching these milestones:\n"
                "Tell the doctor quickly."
            )

    if text in ('1*2*2*5', '2*2*2*5'):
        if sw:
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
        else:
            return respond(
                "END 🍼 Breastfeeding:\n"
                "Mother's milk is best of all!\n"
                "- Start breastfeeding within 1 hour of birth\n"
                "- Breastfeed exclusively for 6 months\n"
                "- Breastfeed 8-12 times per day\n"
                "- Do not give water or other foods\n"
                "- Continue until age 2\n"
                "Benefits: Disease immunity, brain, bonding."
            )

    # ── Afya > Chanjo na Kinga / Vaccines ─────
    if text in ('1*2*3', '2*2*3'):
        if sw:
            return respond(
                "CON 💉 Chanjo na Kinga:\n"
                "1. Chanjo za Watu Wazima\n"
                "2. Kuzuia Malaria\n"
                "3. Kuzuia Kipindupindu\n"
                "4. Kuzuia Typhoid\n"
                "5. Usafi wa Mazingira\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 💉 Vaccines & Prevention:\n"
                "1. Adult Vaccines\n"
                "2. Malaria Prevention\n"
                "3. Cholera Prevention\n"
                "4. Typhoid Prevention\n"
                "5. Environmental Hygiene\n"
                "0. Back"
            )

    if text in ('1*2*3*1', '2*2*3*1'):
        if sw:
            return respond(
                "END 💉 Chanjo - Watu Wazima:\n"
                "Tetanus: Kila miaka 10\n"
                "Hepatitis B: Dozi 3 kwa watu wapya\n"
                "Meningitis: Watu wanaosafiri\n"
                "Typhoid: Kila miaka 3\n"
                "COVID-19: Booster kila mwaka\n"
                "Chanjo nyingi ni BURE hospitali ya serikali."
            )
        else:
            return respond(
                "END 💉 Adult Vaccines:\n"
                "Tetanus: Every 10 years\n"
                "Hepatitis B: 3 doses for new adults\n"
                "Meningitis: For travellers\n"
                "Typhoid: Every 3 years\n"
                "COVID-19: Booster every year\n"
                "Many vaccines are FREE at govt hospitals."
            )

    if text in ('1*2*3*2', '2*2*3*2'):
        if sw:
            return respond(
                "END 🦟 Kuzuia Malaria:\n"
                "1. Lala chini ya chandarua cha dawa\n"
                "2. Weka dawa ya mbu (repellent)\n"
                "3. Vaa nguo ndefu jioni\n"
                "4. Ondoa maji yaliyosimama nyumbani\n"
                "5. Funika madumu ya maji\n"
                "6. Piga dawa nyumbani (IRS)\n"
                "Dalili: Homa, baridi, jasho, maumivu.\n"
                "Tibu mapema - malaria inaua haraka!"
            )
        else:
            return respond(
                "END 🦟 Malaria Prevention:\n"
                "1. Sleep under a treated mosquito net\n"
                "2. Use insect repellent\n"
                "3. Wear long clothes in the evening\n"
                "4. Remove standing water near home\n"
                "5. Cover water containers\n"
                "6. Indoor residual spraying (IRS)\n"
                "Symptoms: Fever, chills, sweating.\n"
                "Treat early - malaria kills fast!"
            )

    if text in ('1*2*3*3', '2*2*3*3'):
        if sw:
            return respond(
                "END 💧 Kuzuia Kipindupindu:\n"
                "1. Kunywa maji ya kuchemshwa/ya chupa\n"
                "2. Osha mikono na sabuni kila wakati\n"
                "3. Pika chakula vizuri\n"
                "4. Epuka chakula cha barabarani\n"
                "5. Tumia choo - usijisaidie nje\n"
                "6. Funika chakula dhidi ya nzi\n"
                "Dalili: Kuhara maji mengi + kutapika.\n"
                "⚠️ Inaweza kuua ndani ya masaa 24!"
            )
        else:
            return respond(
                "END 💧 Cholera Prevention:\n"
                "1. Drink boiled or bottled water\n"
                "2. Wash hands with soap always\n"
                "3. Cook food thoroughly\n"
                "4. Avoid street food\n"
                "5. Use toilets - never open defecate\n"
                "6. Cover food from flies\n"
                "Symptoms: Watery diarrhoea + vomiting.\n"
                "⚠️ Can kill within 24 hours!"
            )

    if text in ('1*2*3*4', '2*2*3*4'):
        if sw:
            return respond(
                "END 🦠 Kuzuia Typhoid:\n"
                "1. Osha mikono kabla ya kula\n"
                "2. Kunywa maji safi ya kuchemsha\n"
                "3. Epuka vyakula vibichi\n"
                "4. Piga chanjo ya Typhoid\n"
                "5. Usile matunda yasiyoosha\n"
                "Dalili: Homa inayoongezeka polepole,\n"
                "maumivu ya tumbo, upele mwilini.\n"
                "Tibu kwa Antibiotics - omba daktari."
            )
        else:
            return respond(
                "END 🦠 Typhoid Prevention:\n"
                "1. Wash hands before eating\n"
                "2. Drink clean boiled water\n"
                "3. Avoid raw/uncooked food\n"
                "4. Get Typhoid vaccine\n"
                "5. Do not eat unwashed fruits\n"
                "Symptoms: Gradually rising fever,\n"
                "stomach pain, body rash.\n"
                "Treat with Antibiotics - see a doctor."
            )

    if text in ('1*2*3*5', '2*2*3*5'):
        if sw:
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
        else:
            return respond(
                "END 🧹 Environmental Hygiene:\n"
                "At home:\n"
                "- Wash hands 5+ times per day\n"
                "- Cover food and water\n"
                "- Dispose of waste properly\n"
                "Toilet use:\n"
                "- Use indoor or outdoor toilets\n"
                "- Never defecate near rivers/wells\n"
                "- Clean toilet every day\n"
                "Hygiene = Good health for your family!"
            )

    # ── Afya > Lishe na Maji Safi / Nutrition ─
    if text in ('1*2*4', '2*2*4'):
        if sw:
            return respond(
                "CON 🥗 Lishe na Maji Safi:\n"
                "1. Lishe Bora ya Kila Siku\n"
                "2. Utapiamlo kwa Watoto\n"
                "3. Lishe kwa Wazee\n"
                "4. Maji Safi - Jinsi ya Kutayarisha\n"
                "5. Lishe kwa Magonjwa ya Sugu\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🥗 Nutrition & Clean Water:\n"
                "1. Daily Balanced Diet\n"
                "2. Malnutrition in Children\n"
                "3. Nutrition for the Elderly\n"
                "4. Clean Water Preparation\n"
                "5. Diet for Chronic Diseases\n"
                "0. Back"
            )

    if text in ('1*2*4*1', '2*2*4*1'):
        if sw:
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
        else:
            return respond(
                "END 🍽️ Daily Balanced Diet:\n"
                "Your plate should have:\n"
                "- Half: Colourful vegetables & fruits\n"
                "- Quarter: Grains (ugali/rice/bread)\n"
                "- Quarter: Protein (meat/fish/beans)\n"
                "Add:\n"
                "- Dairy products\n"
                "- Small amounts of oil (olive, coconut)\n"
                "Drink 2-3 litres of water every day."
            )

    if text in ('1*2*4*2', '2*2*4*2'):
        if sw:
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
                "- Nenda kliniki kwa ushauri"
            )
        else:
            return respond(
                "END 👶 Malnutrition - Children:\n"
                "Signs of malnutrition:\n"
                "- Slow growth\n"
                "- Yellow/falling hair\n"
                "- Swollen legs and belly\n"
                "- Fatigue and not playing\n"
                "Solutions:\n"
                "- Breastfeed until age 2\n"
                "- Increase protein foods\n"
                "- Visit clinic for advice"
            )

    if text in ('1*2*4*3', '2*2*4*3'):
        if sw:
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
        else:
            return respond(
                "END 👴 Nutrition for the Elderly:\n"
                "Elderly need more:\n"
                "- Calcium: milk, small fish\n"
                "- Vitamin D: morning sun + eggs\n"
                "- Protein: beans, meat, fish\n"
                "- Fibre: vegetables, fruits, whole grains\n"
                "Reduce: Salt, sugar, fats\n"
                "Drink water even when not thirsty.\n"
                "Eat small meals 5-6 times per day."
            )

    if text in ('1*2*4*4', '2*2*4*4'):
        if sw:
            return respond(
                "END 💧 Kutayarisha Maji Safi:\n"
                "Njia 1 - Kuchemsha:\n"
                "Chemsha kwa dakika 3 - bora zaidi\n"
                "Njia 2 - Dawa ya Maji (WaterGuard):\n"
                "Tone 1 kwa lita 1 ya maji\n"
                "Njia 3 - Kichujio (Water Filter):\n"
                "Hifadhi katika chombo safi na mfuniko\n"
                "Njia 4 - Jua (SODIS):\n"
                "Chupa ya plastiki wazi - jua masaa 6+"
            )
        else:
            return respond(
                "END 💧 Clean Water Preparation:\n"
                "Method 1 - Boiling:\n"
                "Boil for 3 minutes - best method\n"
                "Method 2 - Water treatment (WaterGuard):\n"
                "1 drop per 1 litre of water\n"
                "Method 3 - Water Filter:\n"
                "Store in a clean covered container\n"
                "Method 4 - Solar (SODIS):\n"
                "Clear plastic bottle - sun for 6+ hours"
            )

    if text in ('1*2*4*5', '2*2*4*5'):
        if sw:
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
        else:
            return respond(
                "END 🫀 Diet for Chronic Diseases:\n"
                "Diabetes:\n"
                "- Reduce sugar, excess rice, soda\n"
                "- Increase vegetables, whole grains\n"
                "High Blood Pressure:\n"
                "- Greatly reduce salt intake\n"
                "- Increase fruits, vegetables, bananas\n"
                "Heart Disease:\n"
                "- Avoid animal fats\n"
                "- Use olive oil or sunflower oil"
            )

    # ── Afya > Afya ya Akili / Mental Health ──
    if text in ('1*2*5', '2*2*5'):
        if sw:
            return respond(
                "CON 🧠 Afya ya Akili:\n"
                "1. Msongo wa Mawazo (Stress)\n"
                "2. Huzuni na Unyogovu (Depression)\n"
                "3. Usingizi Mbaya\n"
                "4. Wasiwasi (Anxiety)\n"
                "5. Msaada wa Dharura\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 🧠 Mental Health:\n"
                "1. Stress\n"
                "2. Sadness & Depression\n"
                "3. Poor Sleep\n"
                "4. Anxiety\n"
                "5. Emergency Help\n"
                "0. Back"
            )

    if text in ('1*2*5*1', '2*2*5*1'):
        if sw:
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
        else:
            return respond(
                "END 😤 Stress:\n"
                "Signs: Headache, insomnia,\n"
                "anger, loss of appetite\n"
                "Ways to relax:\n"
                "- Rest by breathing slowly\n"
                "- Talk to a friend or family\n"
                "- Exercise daily\n"
                "- Sleep well for 7-8 hours\n"
                "- Reduce phone use at night"
            )

    if text in ('1*2*5*2', '2*2*5*2'):
        if sw:
            return respond(
                "END 😔 Huzuni na Unyogovu:\n"
                "Dalili: Kukosa furaha, kujitenga,\n"
                "kuhisi huna thamani, kutolala\n"
                "Hatua:\n"
                "- Zungumza na mtu unayemwamini\n"
                "- Usijiache peke yako sana\n"
                "- Fanya shughuli unazozipenda\n"
                "⚠️ Mawazo ya kujidhuru:\n"
                "Muhimbili NHC: +255 22 215 0562"
            )
        else:
            return respond(
                "END 😔 Sadness & Depression:\n"
                "Signs: Loss of joy, isolation,\n"
                "feeling worthless, insomnia\n"
                "Steps:\n"
                "- Talk to someone you trust\n"
                "- Do not be alone too much\n"
                "- Do activities you enjoy\n"
                "⚠️ Thoughts of self-harm:\n"
                "Muhimbili NHC: +255 22 215 0562"
            )

    if text in ('1*2*5*3', '2*2*5*3'):
        if sw:
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
        else:
            return respond(
                "END 😴 Poor Sleep:\n"
                "Tips for better sleep:\n"
                "- Sleep and wake at the same time daily\n"
                "- Turn off phone/TV 1 hour before bed\n"
                "- Keep room dark and quiet\n"
                "- Avoid coffee in the evening\n"
                "- Try drinking warm milk\n"
                "- Exercise in the morning\n"
                "Good sleep = good physical and mental health."
            )

    if text in ('1*2*5*4', '2*2*5*4'):
        if sw:
            return respond(
                "END 😰 Wasiwasi (Anxiety):\n"
                "Dalili: Moyo kupiga haraka, jasho,\n"
                "kutoweza kutulia, kuogopa bila sababu\n"
                "Njia za kusaidia:\n"
                "- Pumua: Vuta pumzi 4 sek,\n"
                "  shikilia 4 sek, toa 4 sek\n"
                "- Zungumza na mshauri wa afya\n"
                "- Epuka pombe na kahawa nyingi\n"
                "- Fanya mazoezi ya yoga au kutembea"
            )
        else:
            return respond(
                "END 😰 Anxiety:\n"
                "Signs: Racing heart, sweating,\n"
                "restlessness, fear without reason\n"
                "Helpful steps:\n"
                "- Breathe: Inhale 4 sec,\n"
                "  hold 4 sec, exhale 4 sec\n"
                "- Speak to a health counsellor\n"
                "- Avoid alcohol and excess coffee\n"
                "- Try yoga or walking exercises"
            )

    if text in ('1*2*5*5', '2*2*5*5'):
        if sw:
            return respond(
                "END 🆘 Msaada wa Dharura - Afya ya Akili:\n"
                "Tanzania:\n"
                "Muhimbili NHC: +255 22 215 0562\n"
                "Wizara ya Afya: 0800 780 000 (bure)\n"
                "Muhimbili Mental Health: +255 22 215 0610\n"
                "Ukiwa katika hali ya hatari:\n"
                "- Piga simu mtu wa karibu sasa\n"
                "- Nenda hospitali ya karibu nawe\n"
                "Maisha yako yana thamani. Omba msaada!"
            )
        else:
            return respond(
                "END 🆘 Mental Health Emergency:\n"
                "Tanzania:\n"
                "Muhimbili NHC: +255 22 215 0562\n"
                "Ministry of Health: 0800 780 000 (free)\n"
                "Muhimbili Mental Health: +255 22 215 0610\n"
                "If you are in danger:\n"
                "- Call someone close to you now\n"
                "- Go to the nearest hospital\n"
                "Your life has value. Please ask for help!"
            )

    # ── Afya > Dawa za Kawaida / Common Medicines ─
    if text in ('1*2*6', '2*2*6'):
        if sw:
            return respond(
                "CON 💊 Dawa za Kawaida:\n"
                "1. Paracetamol (Tylenol)\n"
                "2. ORS - Maji ya Chumvi\n"
                "3. Metronidazole\n"
                "4. Amoxicillin\n"
                "5. Malaraquin / ALU\n"
                "0. Rudi"
            )
        else:
            return respond(
                "CON 💊 Common Medicines:\n"
                "1. Paracetamol (Tylenol)\n"
                "2. ORS - Oral Rehydration Salts\n"
                "3. Metronidazole\n"
                "4. Amoxicillin\n"
                "5. Malaraquin / ALU\n"
                "0. Back"
            )

    if text in ('1*2*6*1', '2*2*6*1'):
        if sw:
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
        else:
            return respond(
                "END 💊 Paracetamol:\n"
                "Uses: Fever, headache, body pain\n"
                "Adult dose: 500mg-1000mg\n"
                "every 4-6 hours (max 4000mg/day)\n"
                "Child dose: 15mg/kg per dose\n"
                "⚠️ Do not exceed dosage - harms liver\n"
                "⚠️ Avoid completely with alcohol"
            )

    if text in ('1*2*6*2', '2*2*6*2'):
        if sw:
            return respond(
                "END 💧 ORS - Maji ya Chumvi:\n"
                "Matumizi: Kuhara, kutapika, kupoteza maji\n"
                "Jinsi ya kutengeneza nyumbani:\n"
                "- Lita 1 ya maji safi ya kuchemsha\n"
                "- Vijiko 6 vya sukari\n"
                "- Kijiko 1/2 cha chumvi\n"
                "Kunywa glasi 1 baada ya kila kuhara\n"
                "Watoto: Kijiko 1 kila dakika 5"
            )
        else:
            return respond(
                "END 💧 ORS - Oral Rehydration Salts:\n"
                "Uses: Diarrhoea, vomiting, fluid loss\n"
                "How to prepare at home:\n"
                "- 1 litre of clean boiled water\n"
                "- 6 teaspoons of sugar\n"
                "- 1/2 teaspoon of salt\n"
                "Drink 1 glass after each episode\n"
                "Children: 1 teaspoon every 5 minutes"
            )

    if text in ('1*2*6*3', '2*2*6*3'):
        if sw:
            return respond(
                "END 💊 Metronidazole (Flagyl):\n"
                "Matumizi: Kuhara, maambukizo ya utumbo\n"
                "Dozi ya kawaida: 400mg mara 3/siku\n"
                "kwa siku 5-7\n"
                "⚠️ Lazima upate dawa kwa DAKTARI\n"
                "⚠️ Usitumie na pombe - hatari sana!\n"
                "⚠️ Usitumie wakati wa ujauzito"
            )
        else:
            return respond(
                "END 💊 Metronidazole (Flagyl):\n"
                "Uses: Diarrhoea, intestinal infections\n"
                "Standard dose: 400mg 3 times/day\n"
                "for 5-7 days\n"
                "⚠️ Must get from a DOCTOR\n"
                "⚠️ Never use with alcohol - very dangerous!\n"
                "⚠️ Do not use during pregnancy"
            )

    if text in ('1*2*6*4', '2*2*6*4'):
        if sw:
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
        else:
            return respond(
                "END 💊 Amoxicillin:\n"
                "Uses: Bacterial infections -\n"
                "throat, ear, urinary, skin\n"
                "Standard dose: 500mg 3 times/day\n"
                "for 7-10 days\n"
                "⚠️ Must get from a DOCTOR\n"
                "⚠️ Complete full dose even if you feel better\n"
                "⚠️ Watch for allergy - if rash appears: stop!"
            )

    if text in ('1*2*6*5', '2*2*6*5'):
        if sw:
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
        else:
            return respond(
                "END 💊 Malaria Medicines:\n"
                "ALU (Artemether+Lumefantrine):\n"
                "Adult: 4 tablets 2 times/day x 3 days\n"
                "Take with fatty food\n"
                "Malaraquin (Chloroquine):\n"
                "Now failing in most areas\n"
                "⚠️ Test blood first before taking medicine\n"
                "⚠️ Cerebral malaria: Hospital FAST!\n"
                "⚠️ Children: Dose is calculated by weight"
            )

    # ── Back options for Afya sub-menus ───────
    # Going back from level-3 → level-2 (Afya menu)
    if text in ('1*2*1*0', '2*2*1*0',
                '1*2*2*0', '2*2*2*0',
                '1*2*3*0', '2*2*3*0',
                '1*2*4*0', '2*2*4*0',
                '1*2*5*0', '2*2*5*0',
                '1*2*6*0', '2*2*6*0'):
        if sw:
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
        else:
            return respond(
                "CON 🏥 HEALTH - Choose:\n"
                "1. Disease Symptoms\n"
                "2. Mother & Child\n"
                "3. Vaccines & Prevention\n"
                "4. Nutrition & Clean Water\n"
                "5. Mental Health\n"
                "6. Common Medicines\n"
                "0. Back"
            )

    # Going back from level-2 Afya → main menu
    if text in ('1*2*0', '2*2*0'):
        if sw:
            return respond(
                "CON Karibu! Chagua huduma:\n"
                "1. Kilimo\n"
                "2. Afya\n"
                "0. Toka"
            )
        else:
            return respond(
                "CON Welcome! Choose a service:\n"
                "1. Agriculture\n"
                "2. Health\n"
                "0. Exit"
            )

    # ══════════════════════════════════════════
    #  GLOBAL EXIT
    # ══════════════════════════════════════════
    if text in ('1*0', '2*0'):
        if sw:
            return respond(
                "END Asante kutumia huduma yetu!\n"
                "Shamba bora, afya bora - maisha bora! 🌾🏥"
            )
        else:
            return respond(
                "END Thank you for using our service!\n"
                "Better farm, better health - better life! 🌾🏥"
            )

    # ── Catch-all ─────────────────────────────
    return respond(
        "END Samahani, chaguo hilo halipo.\n"
        "Sorry, that option is not available.\n"
        "Please start again."
    )