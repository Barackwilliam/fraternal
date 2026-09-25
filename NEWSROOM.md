# AI Newsroom + Blog SEO — JamiiTek

Kila siku AI inakagua matukio makubwa ya dunia (RSS), inachagua **5 makubwa ya
Tanzania + 5 ya kimataifa**, inaandika **rasimu** za makala za ubora wa juu
(SEO kamili), inachukua picha kutoka Unsplash, kisha **inakutumia email** ya
kukumbusha kukagua na kuthibitisha. Hakuna kinachochapishwa bila wewe kubonyeza
**Publish** kwenye admin.

## 1. Faili zilizoongezwa / kubadilishwa

**Mpya**
- `apps/news_blog.py` — pipeline (RSS → AI select → AI write → Unsplash → drafts)
- `apps/management/commands/daily_news_blog.py` — command
- `apps/seo/feeds.py` — RSS feed ya blog (`/blog/feed/`)
- `apps/templates/emails/blog_review.html` — email ya kukagua
- `apps/migrations/0035_blogpost_is_news_...py`

**Zilizoguswa**
- `apps/models.py` — BlogPost: `is_news`, `source_url`, `source_name`
- `apps/management_views.py` — endpoint `/tasks/news/`
- `apps/urls.py` — `/tasks/news/` + `/blog/feed/`
- `apps/seo/sitemaps.py` — BlogSitemap + BlogIndexSitemap
- `apps/utils/email_notifications.py` — `send_blog_review_reminder`
- `apps/templates/blog/blog_list.html`, `blog_detail.html` — SEO (breadcrumbs,
  twitter cards, article meta, RSS link, JSON-LD) + UI ya The Citizen
- `apps/admin.py` — kupakia picha (cover) kwenye blog
- `requirements.txt` — `feedparser`

## 2. Env variables (Render)

```
GROQ_API_KEY=...              # tayari unayo (AI writer)
GROQ_MODEL=llama-3.3-70b-versatile   # hiari
UNSPLASH_ACCESS_KEY=...       # bure: https://unsplash.com/developers
TASKS_TOKEN=...               # tayari unayo (kwa /tasks/daily/)
BLOG_REVIEW_EMAIL=info@jamiitek.com   # hiari (default info@jamiitek.com)
SITE_BASE_URL=https://www.jamiitek.com
```

- **UNSPLASH_ACCESS_KEY**: jisajili bure kwenye unsplash.com/developers → "New
  Application" → chukua *Access Key*. Ikikosekana, makala zinaandaliwa bila
  picha (utaweka mwenyewe wakati wa kukagua).
- **TASKS_TOKEN**: token ile ile ya `/tasks/daily/`.

## 3. Migration + deps

`build.sh` inaendesha `pip install` + `migrate` — hivyo `feedparser` na
migration 0035 zinawekwa moja kwa moja kwenye deploy.

## 4. Ratiba (cron) — endesha mara moja kwa siku

Render free tier haiendeshi commands, kwa hiyo tumia endpoint (kama
`/tasks/daily/`). Kwenye **cron-job.org** (au UptimeRobot) tengeneza job:

```
URL:      https://www.jamiitek.com/tasks/news/?token=YOUR_TASKS_TOKEN
Schedule: mara moja kwa siku (mfano 05:00 EAT)
Method:   GET
```

- Inafanya kazi **mara moja kwa siku** (hata ikipigwa mara nyingi).
- Kazi halisi (AI + RSS) inafanyika nyuma; jibu linarudi haraka.
- `?force=1` kulazimisha tena; `?dry=` haitumiki hapa.

Ukiwa na terminal: `python manage.py daily_news_blog` (au `--tz 5 --world 5`).

## 5. Mtiririko wa kila siku

1. Cron inapiga `/tasks/news/`.
2. Mfumo unakusanya vichwa vya habari (RSS: BBC, Al Jazeera, Guardian, DW,
   allAfrica TZ, Daily News, Mwananchi).
3. AI (Groq) inachagua **5 TZ + 5 kimataifa** makubwa na tofauti.
4. AI inaandika kila makala (asili, factual, inataja chanzo, SEO kamili).
5. Picha kutoka Unsplash (kama key ipo).
6. Zinahifadhiwa kama **draft** (`is_news=True`, `Tanzania News` / `World News`).
7. **Email** inakufikia yenye orodha + link za kukagua.
8. Wewe: kagua admin → hakiki dhidi ya chanzo → weka/badili picha → **Publish**.

## 6. Usalama wa maudhui

- AI inaandika **rasimu tu** — wewe unathibitisha kila makala.
- Anti-hallucination: makala zinategemea vichwa/muhtasari, zinataja chanzo,
  hazibuni nukuu/takwimu. **Hakiki ukweli kabla ya kuchapisha.**
- Dedup: tukio lililoandikwa (kwa `source_url`) au kichwa kinachofanana (siku 7)
  halirudiwi.

## 7. SEO iliyoongezwa

- Blog sasa iko kwenye **sitemap.xml** (index + kila makala, lastmod).
- **RSS feed**: `/blog/feed/` (Google Discover/News, RSS readers).
- Kila makala: **JSON-LD** (BlogPosting + BreadcrumbList), Open Graph, Twitter
  cards, `article:published_time/modified_time`, canonical, alt za picha,
  reading time.
- Blog index: JSON-LD ya `Blog`, RSS `<link rel="alternate">`.

## 8. Kuthibitisha kwa mkono (kitufe cha admin)

Admin → **Blog posts** → **📰 Run AI newsroom now**. Inaendesha newsroom sasa
hivi (nyuma, dakika 3–8). Utapokea email **kwa vyovyote**:
- **"📝 N news drafts ready for your review"** — rasimu ziko tayari (Status: Draft), au
- **"⚠️ AI newsroom: no drafts created today"** — pamoja na sababu (mf. GROQ_API_KEY
  haipo, Groq rate limit, au feeds hazipatikani).

Groq free tier ina kikomo cha tokens kwa dakika. Mfumo sasa unasubiri na kujaribu
tena kwa 429, na unahamia model mbadala kama model imeondolewa.

## 9. Maoni (comments)

Wasomaji wanaweza kuandika maoni na kujibizana (majibu ngazi moja). Ulinzi:
honeypot, Turnstile (ikiwa imewashwa), kikomo cha sekunde 20 kwa IP, na viungo
visivyozidi 2. Kila maoni mapya yanakuletea email yenye link ya kujibu au kuficha.
Ukijibu ukiwa umeingia kama staff, jibu lako linapata beji **JAMIITEK**.
Kusimamia: Admin → **Blog comments** (ficha/onyesha).
