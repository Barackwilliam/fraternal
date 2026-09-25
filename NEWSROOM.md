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

## 10. Kasi + SEO ya blog

**Kasi**
- Wageni wanapata ukurasa wa blog kutoka cache (Redis) kwa dakika 5. Makala au maoni
  yakibadilika, cache inafutwa papo hapo. Header `X-Blog-Cache: HIT/MISS` inaonyesha hali.
- Orodha hazipakii maandishi kamili ya makala, na ukurasa wa mbele unajengwa kutoka
  makala 60 za karibuni tu (hata zikiwa maelfu).
- Picha za Unsplash zinaletwa kwa ukubwa unaohitajika (WebP/AVIF). Picha kuu inaanza
  kupakuliwa mapema (preload).
- Picha unazopakia kwenye admin zinapunguzwa kwenye browser kabla ya kupakiwa
  (≤1600px, WebP). Picha za zamani: chagua posts → action
  **⚡ Optimize cover images**.
- Fonts hazizuii ukurasa kuonekana, na Turnstile haipakiwi kwenye orodha ya blog.
- **Render free tier inalala baada ya dakika 15 bila wageni** (kuamka ni sekunde 30-60).
  Weka job kwenye cron-job.org: `GET https://jamiitek.com/blog/` **kila dakika 10**.

**SEO**
- `/news-sitemap.xml`: Google News sitemap (makala za siku 2). Iko kwenye robots.txt.
  Iongeze pia kwenye Google Search Console → Sitemaps.
- IndexNow: makala ikichapishwa, Bing, Yandex, ChatGPT search na DuckDuckGo zinajulishwa
  papo hapo. Funguo iko `/indexnow.txt` na haihitaji env yoyote.
- Canonical moja (`https://jamiitek.com`) kwa kila makala. Ukitaka domain nyingine,
  weka env `CANONICAL_BASE_URL`.
- JSON-LD: Organization, WebSite + SearchAction, ItemList, NewsArticle (picha 3 za
  uwiano, wordCount, keywords, isBasedOn). Pia news_keywords na article:tag.
- Kurasa za category na za pagination zina title, description na canonical zake.
- `Crawl-delay` imeondolewa kwenye robots.txt, kwa hiyo Bing inaweza ku-crawl bila kuchelewa.

## 11. Google Discover: waandishi, sera ya uhariri, dawati la Tech & Business

**Newsroom mpya (default):** rasimu **3 kwa siku** za *Tech & Business*
(TechCabal, Techpoint, Disrupt Africa, allAfrica TZ, Daily News, BBC Tech/Business),
kwa kuipa Tanzania na Afrika Mashariki kipaumbele. Idadi inabadilishwa kwa env
`NEWSROOM_DAILY`. Mtindo wa zamani bado unapatikana: `daily_news_blog --tz 5 --world 5`.

**Uchambuzi wa mhariri ni lazima:** kila rasimu ina sehemu
"What this means for Tanzanian businesses" yenye alama `[[EDITOR-INSIGHT]]` na
maswali 2-3 ya kukuongoza. Makala **haiwezi kuchapishwa** mpaka uandike uchambuzi
wako na kufuta alama hiyo. Kwenye admin, safu ya **Insight** inaonyesha ✍️ Needed.

**Waandishi (E-E-A-T):**
1. Admin → **Blog authors** → Add: jina, role, picha halisi, bio, LinkedIn/X, na
   uunganishe **User** (account yako ya admin).
2. Kila makala unayohifadhi bila Author inapewa jina lako moja kwa moja.
3. Makala inaonyesha jina lako lenye link, kisanduku "About the author", na
   JSON-LD `Person`. Ukurasa wako ni `/blog/author/<slug>/`.

**Sera ya uhariri:** `/blog/editorial-policy/` inaeleza jinsi mnavyoripoti, matumizi
ya AI, marekebisho (corrections), picha na uhuru wa uhariri. Ina link kutoka kila
makala na kutoka chini ya kila ukurasa wa blog, na iko kwenye sitemap.

**Picha:** ukipakia picha ya cover yenye upana chini ya 1200px, admin inakuonya
(Google Discover inahitaji ≥1200px).
