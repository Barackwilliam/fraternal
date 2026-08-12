# JamiiTek — Agency Platform

Django platform inayoendesha biashara nzima ya JamiiTek: tovuti ya umma,
portal ya wateja, panel ya usimamizi, website builder ya AI, na dashboard
ya infrastructure inayounganisha providers wote.

Project package: **`jamiitek/`** (settings, urls, wsgi, asgi).

## Sehemu kuu

| App | Inafanya nini |
|---|---|
| `apps/` | Tovuti ya umma, blog, client portal, management panel, proposals, contracts, invoices, receipts, infrastructure integrations |
| `builder/` | Website builder ya multi-tenant kwa subdomain, yenye AI ya design, theme na navigation |
| `apps/chatbot/` | WhatsApp Business bot (JamiiBot) |
| `ussd/` | Huduma ya USSD |
| `apps/seo/` | Zana za SEO |

## Njia kuu

| URL | Nini |
|---|---|
| `/` | Homepage |
| `/service/`, `/About/`, `/contact/` | Kurasa za umma |
| `/blog/` | Blog |
| `/templates/` | Templates marketplace |
| `/portal/` | Client portal (login ya mteja) |
| `/manage/` | Management panel (staff pekee) |
| `/manage/infra/` | Dashboard ya infrastructure |
| `/admin/` | Django admin (Jazzmin) |

## Kuanza

```bash
pip install -r requirements.txt
cp .env.example .env        # kisha jaza thamani halisi
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py runserver
```

`.env` **haitakiwi** kuingia kwenye git. Angalia `.env.example` kwa orodha
kamili ya environment variables zinazohitajika.

## Kabla ya kila deploy

```bash
python check_static.py      # inakagua picha zinazokosekana kwenye templates
python manage.py check
```

Static files zinatumia `CompressedManifestStaticFilesStorage` — faili moja
iliyokosekana inaangusha ukurasa mzima, si picha tupu.

## Deploy

Render, kwa `render.yaml` iliyomo. Start command: `gunicorn jamiitek.wsgi:application`.
Angalia `DEPLOY.md` kwa maelezo ya `DEBUG=False`, na `INTEGRATIONS.md` kwa
mfumo wa Render/Supabase/Uploadcare/Cloudflare/RDAP.

## Kazi za ratiba

| Command | Mara ngapi |
|---|---|
| `sync_integrations` | kila dakika 15 |
| `check_alerts` | kila dakika 30 |
| `send_digest` | kila siku 04:00 UTC |
| `send_expiry_emails` | kila siku (GitHub Actions) |
| `auto_suspend` | kila siku (GitHub Actions) |
| `prune_snapshots` | kila wiki |
| `monthly_report --all` | tarehe 1 ya mwezi |
