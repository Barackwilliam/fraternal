# JamiiTek — kusafisha na kubadilisha jina

Muhtasari wa kila kilichofanyika, ili uweze kurudia kwenye repo yako
mwenyewe badala ya kubadilisha folda nzima.

---

## 1. `ebenezeri` → `jamiitek`

```bash
git mv ebenezeri jamiitek
```

Kisha `ebenezeri` → `jamiitek` kwenye sehemu hizi tu:

| Faili | Mstari |
|---|---|
| `manage.py` | `DJANGO_SETTINGS_MODULE` |
| `jamiitek/settings.py` | `ROOT_URLCONF`, `WSGI_APPLICATION` |
| `jamiitek/wsgi.py` | settings module + docstring |
| `jamiitek/asgi.py` | settings module + docstring |
| `Procfile` | `gunicorn jamiitek.wsgi` |
| `.github/workflows/daily_emails.yml` | `DJANGO_SETTINGS_MODULE` |
| `.github/workflows/auto_suspend.yml` | `DJANGO_SETTINGS_MODULE` |
| `builder/urls.py`, `builder/README_SETUP.md` | maelezo tu |

Database, migrations na app labels **hazikuguswa** — hakuna data
iliyoathirika. `python manage.py check` inapita: 0 issues.

**Render:** badilisha start command kuwa
`gunicorn jamiitek.wsgi:application` **kabla au pamoja na** deploy hii.
Ukisahau, deploy itakufa.

---

## 2. Mabaki ya miradi mingine — yameondolewa

| Kilichoondolewa | Kilikuwa cha |
|---|---|
| `.idea/` (pamoja na `MWST.iml`) | IntelliJ config ya MWST |
| `MAREKEBISHO.md` | Notes za MWST (muslimwelfare) |
| `README.md` | "Mudandaza POS" — imeandikwa upya kwa JamiiTek |
| `render.yaml` | `name: mudandaza`, `startCommand: gunicorn core.wsgi` — imeandikwa upya |
| `.env.example` | Header ya Mudandaza — imeandikwa upya |
| `build.sh` → `compile_po` | Command ya MWST; haipo JamiiTek na hakuna `locale/` |
| `templatetags/` (mzizi) | Nakala ya `apps/templatetags/`; Django haisomi templatetags nje ya app — ilikuwa dead code |
| `__init__.py` (mzizi) | Ilifanya mzizi kuwa package bila sababu |

**Zilizobaki kwa makusudi:** `DEPLOY.md` na `INTEGRATIONS.md` (zote ni za
JamiiTek), na majina "Mudandaza"/"NyumbaChap" ndani ya `index.html`,
`seed_company_profile.py` na `rdap.py` — hayo ni **portfolio ya wateja
wako**, si mabaki.

---

## 3. Secrets — zimetolewa kwenye code

`settings.py` ilikuwa na thamani halisi kama fallback za `os.getenv()`.
Sasa zote ni tupu; environment variables pekee ndizo zinatumika:

DB password · `GROQ_API_KEY` · `WHATSAPP_MASTER_TOKEN` · Cloudinary key/secret ·
Uploadcare pub/secret · Gmail app password · namba za NMB · WhatsApp IDs

`.github/workflows/daily_emails.yml` ilikuwa na **connection string kamili
ya Supabase na nywila ya Gmail zikiwa wazi kwenye faili**. Sasa inatumia
`${{ secrets.* }}` kama `auto_suspend.yml` ilivyokuwa tayari inafanya.

`.env` na `db.sqlite3` zilikuwa **zinafuatiliwa na git** licha ya
`.gitignore`. Zimetolewa kwenye tracking (`git rm --cached`) — faili
zenyewe hazijafutwa kwenye kompyuta yako.

### Bug niliyoikuta hapa

`daily_emails.yml` ilikuwa inapitisha `DATABASE_URL`, lakini `settings.py`
ilikuwa inasoma `DB_NAME`/`DB_USER`/`DB_PASSWORD` moja moja — kwa hiyo
`DATABASE_URL` **ilikuwa inapuuzwa kabisa** na workflow ilikuwa inatumia
ile nywila iliyoandikwa kwenye code. Sasa settings inaangalia
`DATABASE_URL` kwanza, kisha `DB_*`. Kwa `DEBUG=False` bila mojawapo,
inasimama na ujumbe wazi badala ya kujaribu kuunganisha bila nywila.

---

## 4. Unachotakiwa kufanya — kwa mpangilio

1. **Rotate keys zote hapo juu sasa hivi.** Kuziondoa kwenye code
   hakuziondoi kwenye git history — bado zinasomeka na yeyote mwenye repo.
   - Supabase: Settings → Database → Reset password
   - Groq: tengeneza key mpya, futa ya zamani
   - Meta: WhatsApp Business token
   - Cloudinary na Uploadcare: regenerate
   - Gmail: futa app password, tengeneza nyingine
   - `SECRET_KEY` mpya (watumiaji watalazimika kuingia upya — ni sawa)
2. Weka zote kama environment variables kwenye Render na kama
   repository secrets kwenye GitHub.
3. Badilisha start command ya Render kuwa `gunicorn jamiitek.wsgi:application`.
4. Deploy.

---

## 5. Vitu viwili sikuvigusa — amua mwenyewe

**`website_types/` ya mzizi dhidi ya `apps/website_types/`.** Zote mbili
zipo. Settings inatumia ya `apps/` (22 files). Ya mzizi ina 56 files —
superset, na baadhi ya JSON zinatofautiana maudhui. Ni
`scripts/seed_option_tiers.py` pekee inayoisoma. Sikufuta kwa sababu
sijui ipi ni mpya. Linganisha kisha uchague moja.

Pia kuna `.json.bak` 20 ndani ya `website_types/` — backups za mkono.

**`jamiitek_middleware.py`** ipo mzizini na haitumiwi na mradi huu — ni
snippet ya kupewa mteja aiweke kwenye Django project yake. Ni sahihi
kubaki, lakini pengine ni bora kwenye folda kama `deliverables/`.

---

# Awamu ya pili — kumaliza yaliyokuwa yamebaki

## Bug: Uploadcare ilikuwa na majina mawili

`builder/views.py` ilikuwa inasoma `UPLOADCARE_PUBLIC_KEY`, wakati
`settings.py` na `apps/uploadcare_widget.py` zinasoma `UPLOADCARE_PUB_KEY`.
Ukiweka kigezo kimoja tu, kitufe cha kupakia ndani ya builder kilikuwa
hakifanyi kazi — **bila kutoa kosa lolote**. Sasa inasoma settings kwanza,
kisha majina yote mawili.

## `.env.example` ilikuwa imepungukiwa vigezo 14

Niliiandika kwa mkono badala ya kuichambua kwenye code. Vilivyokosekana:
`RENDER_API_KEY`, `RENDER_SERVICE_ID`, `TELEGRAM_BOT_TOKEN`,
`TELEGRAM_CHAT_ID`, `GREEN_API_ID`, `GREEN_API_TOKEN`,
`GREEN_API_RECIPIENT`, `DATABASE_URL`, `GROQ_MODEL`, `REDIS_URL`,
`BUILDER_AI_DAILY_LIMIT`, `BUILDER_AI_CACHE_TTL`,
`BUILDER_AUTO_REGISTER_SUBDOMAINS`. Sasa 42 kati ya 43 zimeandikwa
(iliyobaki ni jina la zamani la Uploadcare).

## Risiti sasa inaonekana kwenye portal ya mteja

Risiti isiyo na tovuti haikuonekana kabisa portal, kwa sababu uchujaji
ulikuwa `website__client` pekee. Nimeongeza FK ya `client` moja kwa moja
(migration `0029`), na uchujaji sasa ni `website__client` **AU** `client`.
Fomu ina chaguo la "Existing client".

Imejaribiwa: risiti bila tovuti inaonekana kwenye orodha ya portal, PDF
inapakuliwa, ukurasa wa kusaini unafunguka.

## Invoice PDF sasa ni ukurasa mmoja

Mabadiliko mawili:

1. **Footer ni frame ya kudumu** (`@frame` ya xhtml2pdf) badala ya
   maudhui yanayotiririka. Inarudisha ~2.5 cm, na footer inaonekana chini
   ya kila ukurasa — si ukurasa wa mwisho pekee.
2. **Safu ya Subtotal inafichwa** pale hakuna VAT wala punguzo. Ilikuwa
   inaonyesha namba ile ile ya Total, mara mbili mfululizo.

Invoice ya kawaida sasa inaingia ukurasa mmoja. Note ya sentensi tano
bado inavuja — weka nne au chini.

## Google Fonts zimehamia kwenye server yetu

`index.html` ilikuwa inapakia Sora (uzito 5) na Inter (uzito 4) kutoka
`fonts.googleapis.com`. Hiyo ni DNS lookup mpya, TLS handshake mpya,
kisha CSS inayoagiza faili nyingine tena — hatua nne kabla maandishi
hayajaonekana sawa. Kwenye 3G ni sekunde kadhaa.

Sasa ni woff2 nane kwenye `apps/static/fonts/` (jumla 156 KB),
zinatolewa na Whitenoise kwenye domain ile ile, na zinahifadhiwa mwaka
mzima. Sora 800 na Inter 400 zina `preload`.

## `assets/` (15 MB) imehamishwa `_archive/`

Ilikuwa STATIC_ROOT ya zamani. `STATICFILES_DIRS` imezimwa, kwa hiyo
`collectstatic` haikuwa inaisoma kabisa — nimethibitisha: faili 301
kabla, 301 baada. `vendor/adminlte` ya 11 MB ndani yake ni nakala; ile
inayotumika inatoka kwenye package ya jazzmin.

Mradi umepungua kutoka 24 MB hadi **9.2 MB**.

## Vifungu vya mkataba

`docs/vifungu-vya-mkataba.md` — vifungu nane vya kunakili, kwa Kiswahili
na Kiingereza, kila kimoja na maelezo ya kwa nini kipo. Kifungu cha 1 na
2 ndivyo vinavyokulinda kwenye mradi wa Africanberty (app stores na
malipo ndani ya app).

## Baada ya kufungua

```bash
python manage.py migrate
python manage.py collectstatic --no-input
```
