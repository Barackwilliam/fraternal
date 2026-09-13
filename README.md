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

Hakuna cron ya nje. **`apps.daily_tasks.DailyTasksMiddleware`** ndiyo
inayoendesha kila kitu kwenye thread ya nyuma — ombi la mtumiaji
halicheleweshwi, na kila kazi ina alama yake ya cache.

| Kazi | Kila |
|---|---|
| `sync_integrations` | dakika 15 |
| `process_scheduled_actions` | dakika 15 |
| `check_alerts` | dakika 30 |
| auto-suspend (`hosting_service.run_auto_suspend`) | siku |
| onyo za muda kuisha (`send_bulk_expiry_warnings`) | siku |
| `send_digest` | siku |
| `prune_snapshots` | siku 7 |
| `monthly_report --all` | siku 30 |

**`REDIS_URL` ni lazima kwenye production.** Alama za kazi zinahifadhiwa
kwenye cache. Bila Redis, kila worker wa gunicorn ana `LocMemCache` yake
na kazi zitarudiwa mara moja kwa kila worker.

Kazi za kila siku zinafanyika kwa mpangilio huu kwa makusudi: `auto_suspend`
inatangulia (ina ujumbe wa AI na maintenance mode), kisha onyo za muda
kuisha zinafuata na kushughulikia email hosting, domains, na onyo za
siku 7/3/1.

Kulazimisha kazi zikimbie sasa:

```bash
curl "https://jamiitek.com/tasks/daily/?token=$TASKS_TOKEN"
curl "https://jamiitek.com/tasks/daily/?token=$TASKS_TOKEN&dry=1"   # onyesha tu
```
