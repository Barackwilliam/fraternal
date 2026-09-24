import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jamiitek.settings')
django.setup()

"""
Sajili bot ya TRYVIS INVENTORY kwenye JamiiBot.

Endesha hivi, kutoka kwenye folda ya JamiiBot:

    python manage.py shell < seed_tryvis_bot.py

HAIGUSI code ya JamiiBot hata kidogo. Inatumia models zilizopo tu
(ChatbotClient, BotConfig, BotService, BotFAQ, BotSubscription), kama
mteja mwingine yeyote anayejisajili kupitia portal.

Ni IDEMPOTENT: ukiiendesha tena, inasasisha ile ile — haitengenezi bot ya pili.
Huduma na FAQ za bot HII pekee ndizo zinazoandikwa upya. Bot za wateja
wengine hazihusiki.

Kabla ya kuendesha, badilisha sehemu ya MIPANGILIO hapa chini.
"""

# ══════════════════════════════════════════════════════════════════
# MIPANGILIO — badilisha hivi tu
# ══════════════════════════════════════════════════════════════════

USERNAME       = 'tryvis'                     # login ya mteja kwenye portal
PASSWORD       = 'Mulelo86'          # mwambie abadilishe akishaingia
EMAIL          = 'info@tryvis.co.tz'
FULL_NAME      = 'Tryvis Investments Limited'
BUSINESS_NAME  = 'Tryvis Investments Limited'
CLIENT_PHONE   = '0733331804'                           # namba ya mteja, kama unayo

BOT_NAME       = 'Msaidizi wa Tryvis '
WHATSAPP_NUMBER = ''                          # namba bot itakayoitoa kwa watumiaji.
                                              # ACHA TUPU kama huna uhakika —
                                              # bot haitatoa namba yoyote.
OWNER_WHATSAPP = '0733331804'                           # handoff inakwenda hapa (meneja wa Tryvis)
PLAN_SLUG      = 'business'                   # starter | business | enterprise
HELP_URL       = 'https://inventory.tryvis.co.tz/help/knowledge.txt'

# ══════════════════════════════════════════════════════════════════

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from apps.chatbot.models import (
    BotConfig, BotFAQ, BotService, BotSubscription, ChatbotClient,
    SubscriptionPlan,
)

# ──────────────────────────────────────────────────────────────────
# PERSONA — hii inaingia kwenye BotConfig.description, ambayo
# build_system_prompt() inaiweka chini ya "MAELEZO YAKO".
#
# JamiiBot tayari ina sheria zake za kutokubuni namba, bei na anwani.
# Hapa tunaongeza kizuizi kimoja ambacho JamiiBot haiwezi kukijua:
# bot HAIONI database ya Tryvis, kwa hiyo haitoi takwimu kamwe.
# ──────────────────────────────────────────────────────────────────

DESCRIPTION = (
    "Wewe ni msaidizi wa mfumo wa Tryvis Inventory. Mfumo huu unatumiwa na meneja "
    "na wafanyakazi wa duka wa Tryvis Investments Limited, kampuni ya vifaa vya uhandisi "
    "Dar es Salaam kama bearings, seals, cutting discs, vipuri vya mashine na karakana. "
    "Kazi yako ni kumsaidia mtu kujua jinsi ya kutumia mfumo. Usijadili mambo mengine. "
    "Jambo muhimu: huoni database ya Tryvis. Hujui stock iliyopo, madeni, invoices au faida. "
    "Mtu akiuliza taarifa hizi, mwambie huwezi kuona data yao na mwambie wapi anaweza kuiona. "
    "Mfano: 'Siwezi kuona data yenu. Nenda All items, tafuta 6204, utaona idadi kwenye In stock.' "
    "USIBUNI NAMBA AU TAARIFA ZA DATA. "
    "Majina ya kurasa na buttons ya mfumo yaache kwa Kiingereza, hata unapojibu kwa Kiswahili. "
    "Mfano: 'Bonyeza Add to store kwenye Stock received.' Usiyatafsiri. "
    "Jibu kwa kifupi, sentensi mbili au tatu. Kama kuna hatua, tumia namba. "
    "Mfumo hauwezi kufuta au kuhariri stock history, kufuta bidhaa yenye history, kutoa mzigo "
    "mara mbili kwa invoice moja, au kuruhusu stock kwenda chini ya sifuri. "
    "Ukiulizwa jinsi ya kuvunja sheria hizi, eleza sababu yake badala ya kutafuta njia ya kuipita. "
    "Mfumo hauna barcode scanner, hauna mobile app, na haujaunganishwa na website ya tryvis.co.tz. "
    f"Maelezo zaidi yapo {HELP_URL}. "
    "Kama kuna error, kitu hakifanyi kazi, wanahitaji feature mpya au wanataka ku-export data, "
    "waelekeze kwa William wa JamiiTek."
)

GREETING = (
    "Karibu {name}! 👋 Mimi ni msaidizi wa *Tryvis Inventory*. "
    "Niulize kuhusu kutumia mfumo, kama kuongeza bidhaa, quotation, stock au ripoti. "
    "_Kumbuka: sioni data yenu. Ninaeleza tu jinsi ya kuiona kwenye mfumo._"
)

FALLBACK = (
    "Samahani, sijaelewa. Niambie unataka kufanya nini kwenye mfumo — "
    "mfano: 'nataka kuongeza bidhaa' au 'stock yangu haifanani na screen'."
)

HANDOFF = (
    "Nakuunganisha na timu ya JamiiTek. Kama kuna tatizo, lieleze kwa ufupi hapa "
    "na William atalipokea."
)



# ──────────────────────────────────────────────────────────────────
# MODULI ZA MFUMO — zinaingia kama BotService.
# `keywords` ni maneno yanayoifanya bot ielekeze sehemu sahihi.
# `price` tunaiacha tupu; hapa si huduma za kuuza.
# ──────────────────────────────────────────────────────────────────

SERVICES = [
    ('All items — bidhaa zote',
     'Hapa unaona bidhaa zote, stock iliyopo, alert level na bei. Hapa ndipo unaongeza bidhaa mpya kwa kutumia Add item. Code ya bidhaa hutengenezwa na mfumo. Part number ina sehemu yake na inaweza kutafutwa.',
     '', 'item, bidhaa, stock, code, part number, kuongeza bidhaa, add item'),

    ('Fix stock count — kurekebisha hesabu',
     'Tumia hapa kama umehesabu bidhaa na idadi ya dukani haifanani na screen. Chagua bidhaa, chagua kilichotokea, weka idadi na sababu. Pia unaweza kuweka starting stock ya bidhaa mpya.',
     '', 'fix stock, kurekebisha, hesabu, kuhesabu, adjustment, stock count, starting stock'),

    ('Stock history — historia ya stock',
     'Hapa unaona kila movement ya bidhaa. Hakuna kitu kinachofutwa au kuhaririwa. Kama kuna kosa, linaweza kurekebishwa kwa kuweka movement ya kinyume.',
     '', 'history, historia, movement, mwendo, ledger, nani alifanya'),

    ('Stock received — kupokea mzigo (meneja pekee)',
     'Hapa meneja anaingiza mzigo kutoka kwa supplier. Weka shipping, customs na clearing ili kupata gharama halisi ya kila bidhaa. Kwanza bonyeza Save, kisha Add to store.',
     '', 'purchase, mzigo, supplier, shipping, customs, forodha, landed cost, gharama halisi'),

    ('Quotations, Invoices, Delivery notes',
     'Mpangilio ni Quotation → Invoice → Delivery note. Quotation ni bei ya mteja, Invoice ni bili, na Delivery note ni mzigo unaotoka. Stock inapungua baada ya kuthibitisha delivery note.',
     '', 'quotation, invoice, delivery note, bili, kuuza, mteja, malipo, payment, print, pdf'),

    ('Workshop jobs — kazi za karakana',
     'Job card inaonyesha vipuri vilivyotumika, masaa ya kazi na kiasi alicholipa mteja. Hii inasaidia kujua kama kazi imeleta faida. Vipuri vinatoka store ukibonyeza "Take these parts from the store".',
     '', 'job, karakana, workshop, kazi, vipuri, job card, fundi'),

    ('Reports — ripoti (meneja pekee)',
     'Kuna ripoti za bidhaa zinazouza, bidhaa zinazokaa, thamani ya stock, faida na bidhaa zinazoisha. Running out pekee ndiyo mshika duka anaiona.',
     '', 'report, ripoti, faida, profit, thamani, value, zinazouza, running out'),

    ('People — watumiaji (meneja pekee)',
     'Hapa meneja anaweza kuongeza mtumiaji, kubadilisha role, kuweka password mpya na kuzima account. Meneja anaona gharama na faida, lakini mshika duka haoni.',
     '', 'user, mtumiaji, password, cheo, role, manager, shopkeeper, watu, people'),

    ('Dashboard na briefing',
     'Huu ni ukurasa wa kwanza. Unaonyesha taarifa muhimu za stock, bidhaa zinazohitaji kuagizwa, grafu na muhtasari wa biashara. Namba zinatoka kwenye data yao halisi.',
     '', 'dashboard, briefing, ukurasa wa kwanza, grafu, chart, muhtasari'),
]



# ──────────────────────────────────────────────────────────────────
# FAQ — 34, mafupi kwa makusudi.
#
# build_system_prompt() inaingiza FAQ ZOTE kwenye kila ujumbe. Knowledge
# base kamili ni ~4,600 tokens; ingeongeza gharama na uchelewesho kwenye
# KILA jibu. Hizi ni zile zinazoulizwa kweli. Maelezo marefu yapo
# kwenye HELP_URL, na persona inaielekeza huko.
# ──────────────────────────────────────────────────────────────────

FAQS = [
    ('Nina bearings ngapi? / Stock yangu ikoje?',
     'Sioni data yenu. Nenda *All items*, tafuta jina au part number, kisha angalia *In stock*.'),

    ('Nani ananidai? / Deni langu ni ngapi?',
     'Sioni data yenu. Fungua *Invoices*. Kwenye *Money owed to us* utaona jumla, na *Still owed* inaonyesha kila invoice.'),

    ('Nifanyeje kuongeza bidhaa mpya?',
     'Nenda *All items* → *Add item*. Weka jina, group, unit na alert level, kisha bonyeza *Save*. Code itatengenezwa na mfumo.'),

    ('Code ya bidhaa inatoka wapi?',
     'Mfumo hutengeneza code kulingana na group. Mfano TIL-BRG-001 na TIL-BRG-002. Huitengenezi mwenyewe.'),

    ('Tofauti ya code na part number ni ipi?',
     'Code ni namba ya mfumo. *Part number* ni namba iliyo kwenye kipuri, mfano 6204 au 12B-1. Ni vizuri kuiweka kwa sababu inasaidia kutafuta bidhaa.'),

    ('Kiwango cha tahadhari (alert level) ni nini?',
     'Ni kiwango ambacho bidhaa ikifikia, mfumo unaonyesha kuwa stock inakaribia kuisha. Ukiweka sifuri, mfumo hautakupa alert ya bidhaa hiyo.'),

    ('Nimehesabu rafu, idadi haiendani na screen.',
     'Nenda *Fix stock count*. Chagua bidhaa, chagua kama umeona zaidi au chini, weka tofauti na sababu.'),

    ('Naingiza bidhaa mpya ambayo tayari ina stock rafuni.',
     'Kwenye *Fix stock count*, chagua *Starting stock — first time entering this item*. Weka pia gharama ya kipande kimoja.'),

    ('Naweza kufuta au kuhariri mwendo kwenye stock history?',
     'Hapana. Historia haiwezi kufutwa au kuhaririwa. Kama kuna kosa, weka movement ya kinyume ili kulirekebisha.'),

    ('Mfumo unasema hakuna stock ya kutosha.',
     'Inaonekana unajaribu kutoa zaidi ya stock iliyopo. Kagua idadi au rekebisha kwenye *Fix stock count*. Stock haiwezi kwenda chini ya sifuri.'),

    ('Nimepokea mzigo kutoka kwa supplier, nifanyeje?',
     'Meneja pekee ndiye anayefanya hivi. Nenda *Stock received* → *Record new stock*, weka supplier, shipping, customs na bidhaa. Bonyeza *Save*, kagua, kisha *Add to store*.'),

    ('Kwa nini hatua mbili? Kwa nini isiingie moja kwa moja?',
     'Mfumo unataka ukague taarifa na gharama kwanza. Baada ya kubonyeza *Add to store*, mzigo unaingia kwenye stock na hauwezi kurudishwa nyuma.'),

    ('Shipping na customs zinafanya kazi gani hapo?',
     'Ni gharama za ziada za mzigo. Mfumo huzigawanya kwenye bidhaa ili kupata *Real cost each*, ambayo hutumika kwenye hesabu za faida.'),

    ('"Share these extra costs" ni nini?',
     'Ni njia ya kugawa shipping na customs. *By price* hugawa kulingana na bei, *By quantity* kwa idadi, na *By weight* kwa uzito.'),

    ('Nimelipa kwa dola, naandikaje?',
     'Chagua USD kwenye currency na weka exchange rate ya siku hiyo kwenye "1 of that currency = how many TZS". Bei za supplier ziandike kwa USD.'),

    ('Mfumo umekataa kuingiza mzigo store.',
     'Kagua kama kila mstari una quantity na kama mzigo haujaingizwa tayari. Ujumbe wa mfumo unaweza kukuonyesha tatizo.'),

    ('Mfuatano wa kuuza ukoje?',
     'Quotation → Invoice → Delivery note. Quotation ni bei, Invoice ni bili, na Delivery note ni mzigo unaotoka. Stock inapungua baada ya kuthibitisha delivery note.'),

    ('Mteja amekubali bei, nifanye nini?',
     'Fungua quotation na bonyeza *Convert to invoice*. Taarifa za quotation zitahamia kwenye invoice.'),

    ('Nampelekeaje mteja mzigo?',
     'Fungua invoice → *Create delivery note*. Mpelekee mteja. Akishapokea, bonyeza *Confirm the customer took the goods*. Hapo stock itapungua.'),

    ('Nimebonyeza Create delivery note mara mbili.',
     'Mfumo utakurudishia delivery note ile ile. Hautengenezi note nyingine kwa invoice hiyo baada ya kuthibitishwa, ili mzigo usitoke mara mbili.'),

    ('Mteja amelipa, naandika wapi?',
     'Fungua invoice. Weka kiasi alicholipa, tarehe na njia ya malipo. Mfumo utaonyesha kama ni *part paid* au *paid*.'),

    ('Nachapishaje invoice au delivery note?',
     'Fungua invoice au delivery note na bonyeza *Print*. Unaweza pia kutumia *PDF* kupata faili la kutuma kwa email.'),

    ('Kwa nini delivery note haina bei?',
     'Ni kwa makusudi. Delivery note inaonyesha bidhaa zilizotolewa. Bei inaonekana kwenye invoice.'),

    ('VAT inafanyaje kazi hapa?',
     'VAT ni 18%. Kama bei tayari zina VAT, weka alama kwenye *Prices already include VAT*. Kama hazina, tumia *Add VAT*.'),

    ('Job card ya karakana inafanya nini?',
     'Inaweka rekodi ya vipuri vilivyotumika, masaa ya kazi na kiasi alicholipa mteja. Hii inasaidia kujua faida ya kazi.'),

    ('Nimeorodhesha vipuri kwenye job lakini stock haijabadilika.',
     'Hiyo ni kawaida. Stock inapungua baada ya kubonyeza *Take these parts from the store* wakati vipuri vinatolewa kweli.'),

    ('Ripoti zipi zipo?',
     'Kuna *What sells, what sits*, *Value of stock*, *Profit* na *Running out*. Ripoti tatu za kwanza ni za meneja.'),

    ('Mimi ni mshika duka, ukurasa unasema siruhusiwi.',
     'Ukurasa huo ni wa meneja. Si tatizo la mfumo. Kama unahitaji taarifa yake, muulize meneja.'),

    ('Nimesahau password.',
     'Meneja ndiye anaweza kuweka password mpya. Afungue *People*, akuchague, abonyeze *Password* na aweke mpya.'),

    ('Mtu ameondoka kazini, namfuta?',
     'Usimfute. Nenda *People* → *Edit* → ondoa alama kwenye *Can sign in*. Hii inazuia login lakini historia yake inabaki.'),

    ('Naweza kufuta bidhaa?',
     'Hapana. Kama bidhaa haitumiki tena, fungua *Edit* na ondoa alama kwenye *Still in use*. Itaondoka kwenye list lakini history itabaki.'),

    ('Menyu imetoweka kwenye simu.',
     'Bonyeza kitufe cha mistari mitatu juu kushoto. Menyu itatokea pembeni. Bonyeza *X* au eneo jeusi pembeni kuifunga.'),

    ('Email ya bidhaa zinazoisha haiji.',
     'Kagua kama watu husika wamewekwa kwenye *People*, wana email, na bidhaa ina alert level zaidi ya sifuri. Kama vyote viko sawa, mwambie William.'),

    ('Faida inaonekana kubwa kupita kiasi.',
     'Kagua kama shipping na customs ziliwekwa kwenye mzigo. Kama hazikuwekwa, gharama ya bidhaa inaweza kuonekana ndogo na faida ikaonekana kubwa.')
]



# ══════════════════════════════════════════════════════════════════
# KUSAJILI
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 62)
print("  TRYVIS INVENTORY — kusajili bot kwenye JamiiBot")
print("=" * 62)

# 1. User -----------------------------------------------------------
user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={'email': EMAIL, 'first_name': 'Tryvis', 'last_name': 'Investments'},
)
if created:
    user.set_password(PASSWORD)
    user.save()
    print(f"  ✓ User mpya: {USERNAME}  (password: {PASSWORD})")
else:
    print(f"  · User ipo tayari: {USERNAME}  (password haijaguswa)")

# 2. ChatbotClient --------------------------------------------------
client, created = ChatbotClient.objects.get_or_create(
    user=user,
    defaults={
        'full_name': FULL_NAME,
        'business_name': BUSINESS_NAME,
        'email': EMAIL,
        'phone': CLIENT_PHONE,
        'is_verified': True,
        'notes': 'Msaidizi wa mfumo wa Tryvis Inventory. Imesajiliwa kwa script.',
    },
)
print(f"  {'✓ Client mpya' if created else '· Client ipo'}: {client.business_name}")

# 3. BotConfig ------------------------------------------------------
bot = BotConfig.objects.filter(client=client).first()
fields = {
    'bot_name': BOT_NAME,
    'business_name': BUSINESS_NAME,
    'description': DESCRIPTION,
    'language': 'sw+en',
    'tone': 'friendly',
    'greeting_msg': GREETING,
    'fallback_msg': FALLBACK,
    'human_handoff_msg': HANDOFF,
    'whatsapp_number': WHATSAPP_NUMBER,
    'owner_whatsapp': OWNER_WHATSAPP,
    'notify_handoff': bool(OWNER_WHATSAPP),
    'collect_name': True,
    'collect_phone': False,
    # 0.2 kwa sababu hii ni bot ya maelekezo, si ya mazungumzo ya kubuni.
    'ai_temperature': 0.2,
}

if bot:
    for key, value in fields.items():
        setattr(bot, key, value)
    bot.save()
    print(f"  · Bot ipo, imesasishwa: {bot.bot_name}")
else:
    bot = BotConfig.objects.create(client=client, status='draft', **fields)
    print(f"  ✓ Bot mpya: {bot.bot_name}")

print(f"    session_name : {bot.session_name}")
print(f"    id           : {bot.id}")

# 4. Subscription ---------------------------------------------------
plan = (SubscriptionPlan.objects.filter(slug=PLAN_SLUG).first()
        or SubscriptionPlan.objects.order_by('sort_order').first())
if plan:
    sub, created = BotSubscription.objects.get_or_create(
        bot=bot,
        defaults={
            'plan': plan,
            'status': 'trial',
            'trial_ends': timezone.now().date() + timedelta(days=7),
            'end_date': timezone.now().date() + timedelta(days=7),
        },
    )
    print(f"  {'✓ Trial siku 7' if created else '· Subscription ipo'}: {sub.plan.name} ({sub.status})")
else:
    print("  ! Hakuna SubscriptionPlan kwenye database — ruka hatua hii.")

# 5. Huduma na FAQ za bot HII pekee ---------------------------------
removed_services = bot.services.all().delete()[0]
removed_faqs = bot.faqs.all().delete()[0]
if removed_services or removed_faqs:
    print(f"  · Nimeondoa za zamani za bot hii: {removed_services} huduma, {removed_faqs} FAQ")

BotService.objects.bulk_create([
    BotService(bot=bot, name=name, description=desc, price=price,
               keywords=keywords, sort_order=index)
    for index, (name, desc, price, keywords) in enumerate(SERVICES)
])
BotFAQ.objects.bulk_create([
    BotFAQ(bot=bot, question=question, answer=answer, sort_order=index)
    for index, (question, answer) in enumerate(FAQS)
])
print(f"  ✓ Moduli {len(SERVICES)}, FAQ {len(FAQS)}")

# 6. Ukubwa wa system prompt ----------------------------------------
prompt = bot.build_system_prompt()
print(f"  · System prompt: {len(prompt):,} chars ≈ {len(prompt)//4:,} tokens kwa kila ujumbe")

print("=" * 62)
print("""
  HATUA ZINAZOFUATA

  1. Ingia kwenye portal kama '%s' uangalie bot.
  2. Unganisha WhatsApp kwa QR (session: %s).
  3. Weka bot kuwa active pale utakapokuwa tayari.
  4. Jaribu maswali haya kabla hujampa mteja:

       "Nina bearings ngapi?"          -> LAZIMA ikatae kukisia
       "Nifanyeje kuongeza bidhaa?"    -> itaje Add item
       "How do I record a payment?"    -> ijibu kwa Kiingereza
       "Mfumo umegoma kufungua"        -> ikuelekeze kwako

  Lile la kwanza ndilo muhimu zaidi. Ikikisia namba, usiipe mteja.
""" % (USERNAME, bot.session_name))