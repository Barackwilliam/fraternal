# Kuunganisha JamiiTek yenyewe

Code yote ya integrations imekamilika (Awamu 1–6, angalia `INTEGRATIONS.md`).
Kilichobaki ni usanidi. Hati hii inakupitisha hatua kwa hatua kuunganisha
**jamiitek.com yenyewe** — Render, Supabase, Uploadcare.

Fuata kwa mpangilio. Hatua 1 na 2 ni lazima zikamilike kwanza.

---

## 1. Thibitisha database inalingana na models

Hili ndilo lililokuwa likizuia kila kitu kingine. Angalia mstari wa mwisho
wa `INTEGRATIONS.md`: migration history na database hazilingani.

```bash
python manage.py check_db_drift --app apps
```

**Kama inasema "Models na database zinalingana"** — nenda hatua 2.

**Kama inaonyesha nguzo zinazokosekana**, itakupa SQL. Mfano:

```sql
ALTER TABLE "apps_managedwebsite" ADD COLUMN IF NOT EXISTS "discount_3m" numeric(5, 2) DEFAULT 5 NOT NULL;
```

Nakili SQL hiyo → Supabase → **SQL Editor** → Run. Kisha endesha
`check_db_drift` tena mpaka iseme zinalingana.

### Kwa nini hii inatokea

Django inaamini kwamba kila migration iliyorekodiwa kwenye jedwali
`django_migrations` ilikamilika. Migration ikikatika katikati — mtandao
ukikatika, Supabase pooler ikichoka, au ukiiweka kwa mkono kama applied —
Django haitagundua kamwe. `showmigrations` itaonyesha `[X]`, lakini nguzo
haipo. Kosa linakuja baadaye kama `ProgrammingError: column ... does not exist`,
mara nyingi kwenye ukurasa usiohusiana kabisa.

`check_db_drift` inasoma jedwali halisi, si historia ya migrations.

---

## 2. Endesha migrations mpya

```bash
python manage.py migrate apps
```

Hii inaleta `0028` (risiti bila website). Ikishindwa, rudi hatua 1.

---

## 3. Weka environment variables

Kwenye **Render → jamiitek → Environment**:

```
FERNET_KEY=...
CRON_TOKEN=...
```

Zitengeneze hivi:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

> **FERNET_KEY ikipotea, credentials zote ulizohifadhi hazitasomeka tena
> milele.** Hakuna njia ya kuzirejesha. Ihifadhi mahali pengine pia — si
> kwenye Render pekee, si kwenye repo.

Za hiari, kwa alerts:

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Au Green API: `GREEN_API_ID`, `GREEN_API_TOKEN`, `GREEN_API_RECIPIENT`.

---

## 4. Tengeneza project ya JamiiTek

Integrations zinaambatana na `ManagedWebsite`. JamiiTek yenyewe inahitaji
rekodi yake:

**Manage → Add Website**

| Uwanja | Thamani |
|---|---|
| Name | `JamiiTek` |
| Domain | `jamiitek.com` |
| Client | tengeneza mteja `JamiiTek Digital Agency` (wewe mwenyewe) |
| Status | `Active` |

Hii haitaonekana kwa mteja yeyote — ni kwa dashboard yako.

---

## 5. Unganisha providers watatu

**Manage → Infrastructure → JamiiTek → Unganisha provider**

Kwa kila mmoja: weka credentials → mfumo unaorodhesha services zako →
chagua sahihi. Huhitaji kutafuta ID popote.

### Render

| | |
|---|---|
| Credential | API key |
| Unaipata wapi | Render → Account Settings → **API Keys** → Create |

Baada ya kuweka key, utaona orodha ya services zako zote za Render. Chagua
ile ya jamiitek.

Inatoa: hali ya deploy, region, deploy ya mwisho, tawi la git.

### Supabase

| | |
|---|---|
| Credential 1 | Personal access token — Supabase → Account → **Access Tokens** |
| Credential 2 | Database URL — Project → Settings → Database → Connection string |

Zote mbili ni za hiari, lakini **weka zote mbili**. PAT inaorodhesha
projects zako; `db_url` ndiyo inayotoa ukubwa halisi wa database na idadi
ya connections. Ukiweka PAT peke yake, hutaona ukubwa.

`db_url` ni ile ile ya `DATABASE_URL`/`DB_*` unayotumia sasa.

### Uploadcare

| | |
|---|---|
| Credential 1 | Public key |
| Credential 2 | Secret key |
| Unazipata wapi | Uploadcare → project → **API keys** |

Secret key haisafiri kwenye mtandao — inatumika kutia saini ombi pekee.

Inatoa: ukubwa wa storage uliotumika, idadi ya faili, bandwidth.

### Cloudflare (kama unaitumia kwa DNS)

| | |
|---|---|
| Credential | API token |
| Ruhusa | `Zone:Read`, `DNS:Read`, `Analytics:Read` — hakuna zaidi |

### Domain (RDAP)

Weka `jamiitek.com` tu. Hakuna key. Inavuta tarehe ya kuisha kwa domain
moja kwa moja kutoka registry.

---

## 6. Sync ya kwanza

```bash
python manage.py sync_integrations
python manage.py integration_status
```

`integration_status` inaonyesha jedwali la kila field na chanzo chake:

```
  ● live   ◐ cached   ○ manual   · haipo
Project          hosting_s  server_lo  uptime_pe  ssl_issue
JamiiTek         ●          ●          ·          ●
```

`uptime` itakuwa `·` mwanzoni — inahitaji snapshots za siku kadhaa kabla ya
kuhesabika. Hiyo ni sahihi, si kosa.

---

## 7. Weka ratiba

Endpoint moja tu inahitajika:

```
POST https://jamiitek.com/cron/sync/
Header: X-Cron-Token: <CRON_TOKEN>
```

Tumia cron-job.org (bure) kwa hiyo, kila dakika 15.

Nyingine ziko GitHub Actions au cron-job.org pia:

| Command | Mara ngapi |
|---|---|
| `sync_integrations` | dakika 15 |
| `check_alerts` | dakika 30 |
| `send_digest` | kila siku 04:00 UTC |
| `prune_snapshots` | kila wiki |
| `monthly_report --all` | tarehe 1 ya mwezi |

`prune_snapshots` si ya hiari. Sync ya dakika 15 inazalisha snapshots
~2,900 kwa integration kwa mwezi. Bila kupogoa, database itajaa.

---

## 8. Thibitisha

```bash
python manage.py integration_status
python manage.py check_alerts --dry-run
```

Kisha kwenye kivinjari:

- `/manage/infra/` — orodha ya projects
- `/manage/infra/<pk>/` — undani wa JamiiTek: storage, deploy, DNS
- Bonyeza **Ripoti ya PDF** — thibitisha hakuna neno `Render`, `Supabase`,
  wala `srv-` linaloonekana. Ripoti ni ya mteja; haipaswi kutaja vendor.

---

## Ukikwama

| Dalili | Sababu ya kawaida |
|---|---|
| `AdapterError: API key inahitajika` | credential haijahifadhiwa — angalia FERNET_KEY ipo |
| Credentials zinasomeka kama takataka | FERNET_KEY imebadilika. Futa integration, unganisha upya |
| `cron 403` | `X-Cron-Token` haifanani na `CRON_TOKEN` |
| Supabase haionyeshi ukubwa | `db_url` haijawekwa — PAT peke yake haitoshi |
| `column ... does not exist` | rudi hatua 1 |
