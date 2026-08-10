# Marekebisho — 06 Agosti 2026

Muhtasari wa mabadiliko yaliyofanyika: picha halisi, mobile responsiveness,
na kurasa mbili mpya za kisheria.

---

## 1. Picha

| Tatizo | Suluhisho | Faili |
|---|---|---|
| Kwenye `/picha/` picha zilijaza sehemu ya juu tu, SVG ya fallback ikionekana chini | `.gallery__item img { height: 92px }` ilikuwa inashinda `.illus__img { height:100% }` kwa specificity. Imeongezwa `.illus .illus__img { height:100% }` | `static/css/mwst.css` |
| Crop ilikatia maandishi ya mabango katikati | `object-position: center 40%` kwa `.illus--card/--tall/--media/--wide` | `static/css/mwst.css` |
| `scenes/mawasiliano.jpg` haikuwepo (ilitumika mara 3) | Imetengenezwa kutoka `mkutano.jpg` — **badilisha na picha halisi ukipata** | `static/img/scenes/` |
| `hero-mosque.jpeg` nakala isiyotumika (212KB) | Imefutwa | `static/img/` |
| Picha nzito kwa mtandao wa simu | Scenes zimepunguzwa hadi 960px; matoleo ya WebP yameongezwa. **2.92 MB → 1.97 MB JPEG / 1.31 MB WebP** | `static/img/` |
| Hakuna WebP kwenye markup | `<picture>` + `<source type="image/webp">`; hero inatumia `image-set()` | `templates/components/illus.html`, `templates/public/home.html` |
| Simu ilipakua picha ya desktop | `<link rel="preload">` sasa ni `media`-scoped na inaelekeza WebP | `templates/public/home.html` |

### Ukiongeza picha mpya ya scene

1. Weka `static/img/scenes/<jina>.jpg` (upana 960px inatosha).
2. Tengeneza WebP:
   ```bash
   python -c "from PIL import Image; im=Image.open('static/img/scenes/x.jpg').convert('RGB'); im.save('static/img/scenes/x.webp','WEBP',quality=78,method=6)"
   ```
3. Picha isipokuwepo, SVG ya `components/illus.html` inaonekana badala yake — hakuna kuvunjika.

---

## 2. Mobile responsiveness

- **Hero ya nyumbani**: overlay ilikuwa `.88`/`.90` — msikiti haukuonekana kabisa.
  Sasa ni gradient ya hatua nne (`.90 → .74 → .62 → .86`).
- **`.hero__art { display:none }` kwenye ≤900px**: picha zote za hero za kurasa za ndani
  zilifichwa kwenye simu. Sasa zinaonekana chini ya maandishi (190px; 160px kwenye ≤560px).
- **Overflow kwenye `/picha/`**: `scrollWidth` 423 dhidi ya 390. Chanzo ni `.pager__nav` —
  `overflow-x:auto` haitoshi kwa sababu flex item ina `min-width:auto`. Sasa inajifunga.
- **`.chips` / `.chip` hazikuwepo kabisa kwenye CSS** — vichujio vya albamu vilionekana
  kama maandishi tu. Zimeandikwa zilingane na `.tab`.
- **`body { overflow-x: clip }`** — `clip` badala ya `hidden` kwa sababu `hidden` inavunja
  `position: sticky` ya `.pub-nav`.

Baada ya marekebisho, ukaguzi wa `scrollWidth vs clientWidth` kwenye 360px na 390px
kwa kurasa 9 hauonyeshi overflow popote.

---

## 3. Kurasa za kisheria

| Faili | Maelezo |
|---|---|
| `core/data/legal.py` | Hati zote mbili kamili, Kiswahili na Kiingereza |
| `templates/public/legal.html` | Kiolezo kimoja kinachotumika na kurasa zote mbili |
| `core/views.py` | `faragha()` na `vidakuzi()` — huchagua lugha kwa `get_language()` |
| `core/urls.py` | `/faragha/` na `/vidakuzi/` |
| `templates/public/base.html` | Viungo kwenye footer + kidirisha cha vidakuzi |
| `static/js/mwst.js` | Mantiki ya kidirisha (localStorage, mwaka mmoja) |

Hati za kisheria **hazitumii `{% trans %}`** kwa kila sentensi — hutafsiriwa na
kupitishwa nzima, kwa hiyo matoleo mawili kamili yapo kwenye `legal.py`.
Ukibadilisha toleo moja, badilisha na jingine.

### Kidirisha cha vidakuzi
Sera inaahidi "kidirisha cha mapendeleo", kwa hiyo kipo kweli:
Kubali vyote / Vya lazima tu, hifadhi ya mwaka mmoja, na kitufe cha kubadilisha
kwenye ukurasa wa Sera ya Vidakuzi.

Uchaguzi unawekwa kwenye `document.documentElement.dataset.cookieConsent`
(`"all"` au `"essential"`). Ukiongeza analytics baadaye, iwashe pale tu thamani
ni `"all"`.

---

## 4. Tafsiri — ONYO MUHIMU

**Usiendeshe `python manage.py makemessages --no-obsolete` kwenye mradi huu.**

Filter yako ya `|tr` inaita `gettext()` kwenye maandishi yanayotoka
`core/data/*.py` (mfano `"Nyumbani"`, `"Kuhusu Sisi"`). `makemessages`
haiwezi kuyaona kwenye source code, kwa hiyo inayahesabu kama *obsolete*
na kuyafuta. Nilipojaribu, entries zilishuka **1240 → 803** (hasara ya
tafsiri 437).

Njia salama ya kuongeza tafsiri mpya:

```bash
# 1. Toa katalogi kamili kutoka .mo
msgunfmt locale/en/LC_MESSAGES/django.mo > locale/en/LC_MESSAGES/django.po

# 2. Ongeza msgid/msgstr mpya mwenyewe mwishoni mwa .po

# 3. Compile
msgfmt --check -o locale/en/LC_MESSAGES/django.mo locale/en/LC_MESSAGES/django.po
```

Sasa `.po` zote mbili zipo kwenye repo (hazikuwepo awali — `.mo` tu),
kwa hiyo hatua ya 1 haihitajiki tena. Katalogi ya Kiingereza ina
**1282 entries, zote zimetafsiriwa** (zilikuwa 1239 zenye mapengo 39).

---

## 5. Kilichobaki kufanya

### 5.1 Usalama — kipaumbele cha kwanza

`config/settings.py` mistari 92–101 ina nywila ya Supabase wazi ndani ya code,
na iko kwenye git history. Sikuibadilisha kwa sababu ingevunja deploy kama
environment variables hazijawekwa kwanza.

**Hatua:**

1. Badilisha nywila kwenye Supabase (Settings → Database → Reset password).
   Kuiondoa kwenye code hakuifanyi kuwa siri — iko kwenye history.
2. Weka `DATABASE_URL` kwenye Render (Environment → Add):
   ```
   postgresql://postgres.<ref>:<NYWILA_MPYA>@aws-0-eu-west-3.pooler.supabase.com:5432/postgres?sslmode=require
   ```
3. Badilisha `settings.py`:

```python
import os
import dj_database_url

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(
        DATABASE_URL, conn_max_age=600, ssl_require=True)}
elif DEBUG:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}
else:
    raise RuntimeError(
        "DATABASE_URL haijawekwa. Weka environment variable kabla ya kuanzisha "
        "mfumo kwenye production."
    )
```

`dj-database-url` tayari iko kwenye `requirements.txt`.

### 5.2 Taarifa zinazokinzana kwenye hati zako

Hati mbili ulizonipa zinatofautiana:

| | Sera ya Faragha | Sera ya Vidakuzi |
|---|---|---|
| Tovuti | `www.muslimwelfare.or.tz` | `www.mwst.or.tz` |
| S.L.P. | `0000` | `00000` |

Nimetumia `muslimwelfare.or.tz` na S.L.P. `0000` kwa zote mbili
(`ORG_SW` / `ORG_EN` kwenye `core/data/legal.py` — sehemu moja tu ya kubadilisha).
**Thibitisha ipi ni sahihi na weka namba halisi ya S.L.P.**

### 5.3 Picha

Mabango ya MWST ndani ya picha yana maandishi ya Kiingereza yaliyofungwa —
hayatafsiriki na yanarudia kichwa cha kadi kilichoandikwa chini yake.
Kwa muda mrefu, picha zisizo na mabango zingekuwa bora zaidi, hasa kwa
thumbnails ndogo (74×56, 44×38) ambapo maandishi hayasomeki.

---

## Vidokezo vya kuendesha

Folda hii **haina** `staticfiles/` — inazalishwa na
`python manage.py collectstatic` (tayari iko kwenye `buildCommand` ya `render.yaml`).


---

# Awamu ya pili — 06 Agosti 2026

## 1. Signin/Register kuonekana ukiwa umeingia

`core/context_processors.py` sasa inatoa `is_authed`, `can_join` na `is_donor`
kwenye kila ukurasa. Zimetumika kwenye:

| Faili | Kilichobadilika |
|---|---|
| `templates/public/base.html` | Header: Dashibodi + Toka badala ya "Ingia / Login". Drawer: jina, jukumu na kitufe cha kutoka. |
| `templates/public/home.html` | Paneli ya kuingia kwenye hero inakuwa "Karibu tena, [jina]". |
| `_pagehero.html`, `_cta.html`, `uanachama.html` | "Jiunge Sasa" inabadilika kuwa "Dashibodi Yangu" au "Changia Sasa". |

Sheria ya `can_join`: mhisani bado anaonyeshwa "Jiunge Sasa" (anaweza kuwa
mwanachama); wengine wote tayari wamo.

Pia "Kumbuka Mimi" sasa inafanya kazi kweli — bila hiyo,
`session.set_expiry(0)` inafanya kipindi kiishe kivinjari kikifungwa.

## 2. Ukurasa wa Vifurushi

- Sehemu 11 mpya kwenye `members.Category` (ada ya usajili, ada ya mwaka,
  muda, alama, na bendera sita za faida).
- `members/migrations/0005_package_pricing.py` inaweka thamani zote za bango
  na kuunda **Diamond** kama haipo. Haiguswi `name` wala `benefits` za
  kategoria zilizopo — hizo ni maudhui ya mteja.
- Jedwali linatoka database, si maandishi ya kuandikwa kwenye kiolezo — bango
  na tovuti havitatofautiana ukibadilisha ada.
- Menyu ya header sasa: Nyumbani, Uanachama, **Vifurushi**, **Changia**, Mawasiliano.

Kubadilisha ada baadaye: Dashibodi -> Mfumo -> Kategoria za Uanachama.
Hakuna haja ya kugusa code.

## 3. Mhisani na kuchangia bila akaunti

| Njia | Kinachofanyika |
|---|---|
| `/changia/` | Fomu ya wazi. Hakuna akaunti inayohitajika. |
| `/changia/asante/<risiti>/` | Shukrani + mwaliko wa kufungua akaunti. |
| `/mhisani/jisajili/` | Akaunti ya mhisani; mchango wa mwisho unaunganishwa. |
| `/mhisani/` | Historia ya michango, jumla, na mgawanyo kwa mfuko. |

- Jukumu jipya `Role.DONOR` na `Donor.user` (OneToOne, hiari).
- Mchango unaingia kama **`pending`** — afisa wa michango ndiye anayethibitisha.
  Hakuna kinachoingia kwenye leja mpaka hapo.
- Mwaliko wa akaunti unaonekana **baada tu ya kuchangia**, si kabla, na
  unaeleza faida nne mahususi. Hakuna kulazimisha.
- `Donor` hatafutwi mara mbili: tunatafuta kwa simu/barua pepe kwanza.

## 4. Ukurasa mpya wa kuingia

Umejengwa kwa mujibu wa picha: nembo, "Karibu Tena!", hatua 1 (vigae vya
majukumu vyenye tiki), hatua 2 (fomu), Kumbuka Mimi, kigawanyo cha AU,
chaguo la OTP, na ujumbe wa usalama.

**MUHIMU — usalama:** jukumu unalochagua ni **mwongozo wa maonyesho tu**.
Ruhusa halisi zinatoka kwenye `user.role` ya akaunti. Nimejaribu: kuchagua
"Msimamizi" kisha kuingia kwa akaunti ya mwanachama kunampeleka
`/mwanachama/`, na `/taifa/` inamrudisha. Usibadilishe hili — kama jukumu
lililochaguliwa lingeamua ruhusa, mtu yeyote angeweza kuwa msimamizi.

## 5. Tafsiri

Katalogi ya Kiingereza: **1282 -> 1420 entries, zote zimetafsiriwa.**
Nimefuata njia ile ile salama (msingi ni katalogi kamili, si matokeo ya
`makemessages`). Nimejaribu `/vifurushi/`, `/changia/` na `/ingia/` kwa
Kiingereza — hakuna neno la Kiswahili lililobaki.

Kumbuka onyo la awali: **usiendeshe `makemessages --no-obsolete`.**

## 6. Vitu viwili vya kuamua

**Kigae cha "Kujitolea".** Picha yako ina majukumu sita; mfumo una matano —
hakuna jukumu la volunteer kwenye `Role`. Nimeweka kigae hicho na dokezo
linalosema wajitoleaji hutumia akaunti ya mwanachama. Ukitaka jukumu halisi
lenye dashibodi yake, ni kazi ya ziada.

**OTP.** Picha ina "Login with Phone Number (OTP)" lakini mfumo hauna huduma
ya SMS. Kwa sasa kitufe kinaelekeza kwenye ukurasa wa mawasiliano badala ya
kuahidi kitu kisichofanya kazi. OTP halisi inahitaji Beem au Africa's
Talking — awamu tofauti.

## 7. Bado halijafanyika

Usalama wa `config/settings.py` (nywila ya Supabase ndani ya code) — angalia
sehemu ya 5.1 hapo juu. Halijabadilika.



---

# Awamu ya tatu — 08 Agosti 2026

## 1. Kuhusu Sisi (`/kuhusu/`)

Maandishi rasmi ya MWST yameongezwa kwa lugha zote mbili kwenye
`core/data/about.py`: utangulizi wa aya tatu, Dira, Dhima, Tunu sita,
Tunachofanya (vitu 10), Kauli Mbiu na Motto.

Kama `legal.py`, hii ni hati inayotafsiriwa nzima — matoleo mawili kamili,
si `{% trans %}` kila sentensi. Ukibadilisha moja, badilisha na jingine.

## 2. Mawasiliano (`/mawasiliano/`)

Umejengwa upya kwa muundo wa bango rasmi: kadi sita (Anwani, Namba za Simu,
Barua Pepe, Saa za Kazi, Ramani, Mitandao), banner ya "Tuko hapa kukusaidia",
na ayah ya Al-Qur'an 5:2 chini.

Anwani: **Shariff PBZ House, Dodoma Mjini, Nyerere Square, Plot 4 Block M
Wing A4 — Ghorofa ya Tatu, S.L.P 450, Dodoma.**

Wakati wa kupima nilikuta bug: data ilikuwa `pages.py` lakini view inatumia
`queries.py`, kwa hiyo ukurasa ulionyesha kadi tupu. `public_mawasiliano()`
sasa inatumia data moja; FAQ bado zinatoka database.

## 3. Bei mpya za vifurushi

`members/migrations/0006_new_fees.py`:

| Daraja | Ada ya usajili | Ada ya mwezi |
|---|---|---|
| Bronze | 10,000 | 10,000 |
| Silver | 20,000 | 20,000 |
| **Gold** | **5,000** | **5,000** |
| Platinum | 100,000 | 100,000 |
| Tanzanite | 1,000,000 | 200,000 |

- **Diamond imestaafishwa** — haijafutwa (kumbukumbu zinabaki) bali
  imeondolewa kwenye ukurasa wa vifurushi (`is_selectable=False`,
  `registration_fee=0`).
- **Tanzanite** sasa ni daraja linaloweza kuchaguliwa, si la heshima tu,
  kwa sababu limepewa ada.
- Kigezo cha ukurasa wa vifurushi kimebadilika kutoka `annual_fee__gt=0`
  kwenda `registration_fee__gt=0`, ili madaraja ya urithi (mfano Founder)
  yasionekane.
- Ada ya mwaka haikutolewa safari hii, kwa hiyo imewekwa 0 na **safu yake
  inajificha yenyewe** hadi itakapotolewa.

### ONYO: ada ya Gold

Gold ni **5,000** — ndogo kuliko Bronze (10,000) na Silver (20,000).
Hivyo ndivyo ulivyoagiza, na nimetekeleza kama ulivyosema. Lakini
inamaanisha daraja la kati ndilo la bei ya chini kabisa kwenye jedwali la
umma — mtu anaweza kuchagua Gold kwa 5,000 badala ya Bronze kwa 10,000.

Kama ilikuwa **50,000**, badilisha thamani mbili za `"G"` kwenye
`0006_new_fees.py` kisha uendeshe migration mpya. Ni sehemu moja tu.

## 4. Hali ya majaribio ya malipo

`PAYMENTS_DEMO` kwenye `config/settings.py` (chaguo-msingi `True`).
Ikiwa `True`:

- Kidokezo cha njano kinaonekana kwenye fomu ya kuchangia: *"Malipo bado
  hayajaunganishwa ... HAKUNA pesa halisi itakayotolewa."*
- Kitufe kinasoma "Tuma Mchango (Demo)".
- Ukurasa wa shukrani unaonyesha ujumbe wa kijani: *"Imefanikiwa — lakini ni
  majaribio tu"*, pamoja na risiti halisi ili uone mtiririko mzima.

Ukiunganisha mtoa huduma, weka `PAYMENTS_DEMO=False` kwenye environment ya
Render. Hakuna kitu kingine cha kubadilisha.

## 5. Kadi za benki — hazikusanywi

Mockup zilizonipa zilikuwa na `Card Number`, `CVV` na "Save card". **Sikuweka
sehemu hizo popote**, na sitaziweka. Nimethibitisha kwa kupima: hakuna input
yenye jina la card/cvv/expiry kwenye mfumo mzima.

Sababu: kukusanya namba za kadi kwenye seva yako kunakuweka chini ya PCI-DSS
kamili — ukaguzi wa gharama kubwa kila mwaka, na dhima yote ikitokea uvujaji.
Njia sahihi ni **hosted fields** au **redirect ya gateway** (Selcom, DPO,
Flutterwave, Stripe), ambapo namba inaenda moja kwa moja kwa mtoa huduma na
haigusi seva zetu kabisa. UI inaweza kuonekana ile ile — tofauti ni pale
namba inapoingia.

## 6. Tafsiri

Katalogi ya Kiingereza: 1420 -> **1451, zote zimetafsiriwa.**
Njia ile ile salama. Kumbuka: **usiendeshe `makemessages --no-obsolete`.**

## 7. Bado halijafanyika

- Ukurasa wa Uanachama (kuondoa tiers na how-to-join, kuweka muundo wa
  infographic ya MEMBERSHIP).
- Kurasa kamili za malipo (Lipa Ada / Michango) kwa muundo wa mockup.
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili.
- Usalama wa `config/settings.py` — angalia sehemu 5.1.



---

# Awamu ya nne — 08 Agosti 2026

## 1. Bei — Gold imerekebishwa

`0006_new_fees.py` sasa ina bei sahihi kwa **kila sehemu ya mfumo**:

| Daraja | Ada ya usajili | Ada ya mwezi |
|---|---|---|
| Bronze | 10,000 | 10,000 |
| Silver | 20,000 | 20,000 |
| Gold | **50,000** | **50,000** |
| Platinum | 100,000 | 100,000 |
| Tanzanite | 1,000,000 | 200,000 |

Sehemu zilizosasishwa:
- `members/migrations/0006_new_fees.py` — chanzo halisi (database).
- `core/data/pages.py` — thamani za akiba zinazotumika na `/jiunge/`.
- `core/management/commands/seed.py` — usakinishaji mpya unaanza na bei sahihi.

Ukurasa wa `/vifurushi/`, `/uanachama/`, `/jiunge/` na dashibodi ya mwanachama
zote zinasoma kutoka `members.Category`, kwa hiyo hazihitaji kugusa tena.

## 2. Kichagua lugha — sasa ni droplist

`templates/components/langpick.html` (kipya) kinatumika na tovuti ya umma
(`public/base.html`) na dashibodi (`base/topbar.html`).

- Ni `<select>` halisi — lugha inabadilika mara tu unapochagua, hakuna kubonyeza.
- Majina yanaonyeshwa kwa lugha yenyewe (`name_local`): **Kiswahili / English**,
  si yaliyotafsiriwa. Awali "English" ilikuwa inaonyeshwa kama "Kiingereza".
- `<noscript>` ina kitufe cha "Nenda" ili ifanye kazi hata JavaScript ikizimwa.

## 3. Ukurasa wa Uanachama umejengwa upya

Vifurushi na hatua za zamani vimeondolewa. Sasa una muundo wa bango la
MEMBERSHIP: Kuhusu Uanachama (pamoja na hadith), Jinsi ya Kujiunga (hatua 5),
Aina za Uanachama (5), Manufaa (16), Wajibu wa Mwanachama (8), Jinsi Uanachama
Unavyokoma (8 + onyo), na Kwa Nini Kujiunga.

Maudhui yapo `core/data/membership.py` kwa lugha zote mbili.
**Bei hazipo hapo** — kuna kiungo kinachoelekeza `/vifurushi/`, ili kuwe na
chanzo kimoja tu cha bei.

## 4. Bug ya `hide-xs`

Nilipoweka droplist, header ilianza kuvuja 15px kwenye simu. Chanzo halisi:
class `hide-xs` ilitumika kwenye `base.html` **lakini haikuwahi kufafanuliwa
kwenye CSS**, kwa hiyo maandishi "Ingia / Login" yalikuwa yanaonekana daima
na kubana header. Ilikuwa ipo tangu awali — droplist ndiyo iliifichua tu.

Imefafanuliwa sasa. Nimejaribu 320px, 360px, 390px na 430px kwa kurasa nane:
hakuna overflow popote.

## 5. Tafsiri

Katalogi ya Kiingereza: **1457, zote zimetafsiriwa.**
Nimejaribu `/uanachama/` kwa lugha zote mbili — sehemu zote zinabadilika
("KUHUSU UANACHAMA" -> "ABOUT MEMBERSHIP" n.k.), hakuna Kiswahili
kilichobaki kwenye toleo la Kiingereza.

## 6. Bado halijafanyika

- Kurasa kamili za malipo kwa muundo wa mockup (Lipa Ada / Michango yenye
  hatua nne, uteuzi wa mtoa huduma, aina za michango kama Zakat, Sadaqah,
  Waqf n.k.). Hali ya demo ipo tayari na inafanya kazi kwenye `/changia/`.
- Jedwali la michango ya kila mwezi/mwaka la bango la Kiswahili.
- Usalama wa `config/settings.py` — angalia sehemu 5.1.

