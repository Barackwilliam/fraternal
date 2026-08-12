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
