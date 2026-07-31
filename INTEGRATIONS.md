# JamiiTek Manage — Infrastructure Integration

**Awamu 1–6 zimekamilika.** `python manage.py check` inapita bila kosa.

Mfumo unaunganisha Render, Supabase, Uploadcare, Cloudflare na RDAP na
`ManagedWebsite` iliyokuwepo; unabadilisha data ya mkono kuwa halisi kwenye
portal ya mteja; unakupa dashboard ya kusimamia kila project bila kufungua
dashboard ya provider yeyote; na unakutumia alerts na ripoti za mwezi.

---

## Files

**Mpya (18)**

```
apps/crypto.py                      Fernet encryption
apps/integration_models.py          Integration, Snapshot, AuditLog, Resolver
apps/integration_admin.py           Admin
apps/live_config.py                 Overlay ya data halisi
apps/infra_views.py                 Dashboard ya staff + vitendo + cron + ripoti
apps/notify.py                      Telegram / Green API
apps/alerts.py                      Kanuni sita za alerts
apps/digest.py                      Muhtasari wa asubuhi (Groq)
apps/reports.py                     Ripoti ya PDF ya mwezi
apps/integrations/
    __init__.py  base.py  render.py  supabase.py
    uploadcare.py  cloudflare.py  rdap.py
apps/management/commands/
    sync_integrations.py  check_alerts.py  send_digest.py
    monthly_report.py  integration_status.py  prune_snapshots.py
apps/templates/management/infra_*.html   (6)
apps/migrations/0024_*.py  0025_*.py
```

**Zilizobadilishwa (7)** — `models.py`, `admin.py`, `urls.py`,
`client_portal_views.py`, `portal/hosting_config.html`,
`management/infra_detail.html`, `requirements.txt`.

---

## Kuanza

```bash
pip install -r requirements.txt
```

Environment variables:

```bash
FERNET_KEY=...          # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
CRON_TOKEN=...          # python -c "import secrets; print(secrets.token_urlsafe(32))"

TELEGRAM_BOT_TOKEN=...  # au GREEN_API_ID / GREEN_API_TOKEN / GREEN_API_RECIPIENT
TELEGRAM_CHAT_ID=...
GROQ_API_KEY=...        # ya hiari — digest inafanya kazi bila yo
```

**FERNET_KEY ikipotea, credentials zote hazitasomeka tena.** Ihifadhi nje
ya server.

```bash
python manage.py migrate apps
```

> Migration 0025 ni data migration inayofuta thamani za kubuni
> zilizohifadhiwa (`197.250.10.1` n.k.). Haina kurudi nyuma kwa makusudi.

Kisha `/manage/infra/` → chagua project → **Unganisha provider**.

| Provider | External id | Credentials |
|---|---|---|
| Render | `srv-xxxxx` | `api_key` |
| Supabase | project ref | `pat` na/au `db_url` |
| Uploadcare | public key | `public_key` + `secret_key` |
| Cloudflare | zone id | `api_token` (Zone:Read, DNS:Read, Analytics:Read) |
| Domain (RDAP) | jina la domain | `domain` — hakuna key |

---

## Ratiba

Tumia cron-job.org (bure) au GitHub Actions. Endpoint moja tu inahitaji
kuwa wazi:

```
POST https://jamiitek.co.tz/cron/sync/
Header: X-Cron-Token: <CRON_TOKEN>
```

Nyingine ni management commands:

| Command | Mara ngapi |
|---|---|
| `sync_integrations` | kila dakika 15 |
| `check_alerts` | kila dakika 30 |
| `send_digest` | mara moja kwa siku, 04:00 UTC |
| `prune_snapshots` | mara moja kwa wiki |
| `monthly_report --all` | tarehe 1 ya kila mwezi |
| `integration_status` | kwa mkono, unapotaka kujua hali |

---

## Awamu 5 — kusafisha

Defaults za kubuni zimeondolewa kwenye model, na data migration inafuta
zilizohifadhiwa:

| Field | Ilikuwa |
|---|---|
| `ip_address` | `197.250.10.1` |
| `server_hostname` | `srv1.jamiitek.com` |
| `ftp_host` | `ftp.jamiitek.com` |
| `db_host` | `db.jamiitek.com` |
| `server_location` | `Dar es Salaam, Tanzania` |
| `disk_used_gb` | `1.2` |
| `bandwidth_used` | `4.5` |
| `uptime_percent` | `99.97` |

Kabla ya kufuta field yoyote kabisa, endesha:

```bash
python manage.py integration_status
```

```
  ● live   ◐ cached   ○ manual   · haipo
Project          hosting_s  server_lo  uptime_pe  ssl_issue  monthly_v
Mudandaza        ●          ●          ·          ○          ●
NyumbaChap       ○          ·          ·          ○          ○
Safari Travels   ●          ●          ·          ○          ●

  Tayari kufutwa (live kwa wote, hakuna manual):
    ✓ server_location
```

**Kanuni:** field iondolewe tu ikiwa `live` kwa clients WOTE kwa angalau
wiki mbili. `python manage.py integration_status --missing` inaonyesha
projects ambazo bado hazijaunganishwa.

---

## Awamu 6 — alerts, digest, ripoti

### Kanuni sita

| Kanuni | Kiwango | Inagusa lini |
|---|---|---|
| Site iko chini | critical | deploy ya mwisho imeshindwa |
| Service imesimamishwa | critical | hosting suspended ingawa bili hai |
| Domain imeisha / inakaribia | critical / warning | siku 45, na `auto_renew` ni false |
| SSL inakaribia kuisha | critical / warning | siku 14 |
| Sync imekufa | warning | saa 6+ bila mafanikio |
| Storage inakaribia kikomo | warning / critical | 85% / 95% |
| Hosting inaisha | info | siku 7 |

Dedup inatumia `IntegrationAuditLog` — critical inarudiwa baada ya saa 6,
warning baada ya siku, info baada ya wiki. Hakuna table mpya.

Jaribio: alerts 4 zilikutwa na kutumwa; kuendesha tena mara moja → 0.

### Digest

Code inakusanya ukweli, Groq inaupanga. **Groq ikizimika, muhtasari wa
kawaida unatumwa** — hakuna kinachopotea. Inatuma deltas pekee:

```
JamiiTek — 30/07/2026

🔴 Hatua sasa
  • Safari Travels — Site iko chini

🟡 Angalia
  • Safari Travels — Domain inakaribia kuisha
  • Safari Travels — Sync imekufa — cloudflare

Mabadiliko
  • Safari Travels: online → failed
```

### Ripoti ya PDF

Namba tatu kubwa juu — **Uptime · Incidents · Visitors** — kisha jedwali
la huduma, muhtasari kwa lugha ya kawaida, na hali ya bili.

Uptime inatoka snapshots halisi. Bila data ya kutosha, ripoti inasema
monitoring imeanza hivi karibuni badala ya kubuni namba.

Mteja anajipakulia mwenyewe: **Hosting Panel → Download PDF**.
Wewe: **Infrastructure → project → Ripoti ya PDF**.

Jaribio: `Render`, `Supabase`, `Cloudflare`, `srv-` — hakuna hata moja
kwenye PDF.

### Prune

Sync ya dakika 15 inazalisha snapshots ~2,900 kwa integration kwa mwezi.

```
siku 7 za mwisho  → zote
siku 8–90         → moja kwa saa
zaidi ya siku 90  → futa
```

Uptime ya siku 30 haiathiriki.

---

## Usalama

| Kanuni | Utekelezaji |
|---|---|
| Credentials hazikai wazi | Fernet; key iko env pekee |
| Client portal ni read-only | `run_action` haipo kwenye code path ya mteja |
| Vitendo vinathibitishwa | `key not in adapter.actions()` → 400 |
| Kila kitendo kinarekodiwa | `IntegrationAuditLog` na IP |
| Vitendo vya kuharibu | Havipo — hakuna drop/delete database |
| API haiitwi ndani ya request | Sync ni cron; UI inasoma `cached_summary` |
| Errors hazivuji kwa mteja | `AdapterError` inanaswa |

Majaribio:

```
anon  → /manage/infra/            302
anon  → action deploy             302
staff → kitendo kisichoruhusiwa   400
cron  bila token / token mbaya    403
cron  token sahihi                200
```

---

## Kilichorekebishwa kwenye portal

**Badge ya ONLINE ilikuwa inasema uongo.** Ilikuwa `website.status ==
'active'` — hiyo ni hali ya *malipo*. Site iliyokuwa chini kabisa ilionyesha
kijani mradi mteja amelipa. Sasa inatoka Render.

**Uptime** ilikuwa `99.97` ya mkono. Sasa inahesabiwa; bila data inasema
"Collecting…".

**`server_location`** ilikuwa inadai data iko Tanzania wakati iko Render.
Sasa inatoka region halisi: `Europe (Frankfurt)`.

Kanuni ya white-label: inaficha **vendor**, si **hali**. Site ikiwa chini,
mteja anaona nyekundu.

---

## Muhimu kufanya leo

`.env` na `db.sqlite3` zilikuwa **zimeingia kwenye git**. `GROQ_API_KEY`
ilikuwa humo.

```bash
# 1. Badilisha key kwenye Groq console — sasa hivi
# 2. Zitoe kwenye tracking
git rm --cached .env db.sqlite3
git commit -m "Remove secrets from tracking"
```

Kubadilisha `.gitignore` peke yake **hakuondoi** kilichokwisha ingia.

Vilevile: migration history na database hazilingani (`facebook_link`
inajirudia, `discount_3m` haipo). Tatua kabla ya 0024/0025. Angalia
`python manage.py showmigrations apps`.

---

## Kuongeza provider mpya

Class moja + mstari mmoja. Hakuna migration, template, wala view.

```python
class MyAdapter(BaseAdapter):
    provider = 'myprovider'
    label = 'My Provider'
    client_label = 'Storage'
    credential_fields = [{'key': 'token', 'label': 'Token', 'secret': True}]

    @classmethod
    def discover(cls, creds): ...
    def summary(self): return {base.DB_SIZE_BYTES: ...}
```

```python
ADAPTERS = {..., MyAdapter.provider: MyAdapter}
```
