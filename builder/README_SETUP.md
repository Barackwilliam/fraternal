# JamiiTek Website Builder — Maelekezo ya Setup

## 1. Kilichoongezwa kwenye project

- `builder/` — app nzima (models, views, editor, public rendering, AI, schemas)
- `ebenezeri/settings.py` — `'builder'` kwenye INSTALLED_APPS, `SubdomainMiddleware` kwenye MIDDLEWARE, na `BUILDER_BASE_DOMAIN` chini
- `ebenezeri/urls.py` — `path('builder/', include('builder.urls'))`
- `requirements.txt` — `groq`

## 2. Environment Variables (Render → Environment)

| Key | Value |
|---|---|
| `GROQ_API_KEY` | API key kutoka console.groq.com (bure) |
| `UPLOADCARE_PUBLIC_KEY` | Public key kutoka uploadcare.com dashboard |
| `ALLOWED_HOSTS` | `.jamiitek.com,jamiitek.onrender.com,jamiitek.com,www.jamiitek.com` |

**MUHIMU:** dot ya mwanzo kwenye `.jamiitek.com` inaruhusu subdomains ZOTE.

## 3. Migrations

```bash
python manage.py makemigrations builder
python manage.py migrate
```

Hakikisha `build.sh` yako ya Render ina `python manage.py migrate` (hii imewahi kukusumbua kwenye Safari Travels).

## 4. DNS (kwa registrar wa jamiitek.com)

```
*.jamiitek.com   CNAME   jamiitek.onrender.com
```

## 5. Render — Wildcard Domain

Render Dashboard → service yako → Settings → Custom Domains → Add:
`*.jamiitek.com` — fuata CNAME records watakazokupa. SSL inajitengeneza yenyewe.

## 6. Testing local

```bash
python manage.py runserver
# Platform:  http://localhost:8000/builder/signup/
# Site ya mteja:  http://SUBDOMAIN.localhost:8000/
```

`*.localhost` inafanya kazi kwenye Chrome/Edge/Firefox bila kubadilisha hosts file.

## 7. Kuongeza aina mpya ya website

Unda file mpya `builder/schemas/jina.json` ukifuata muundo wa `tourism.json`:
- `pages` — pages za default na starter HTML (zinaweza kuwa na shortcodes)
- `collections` — content types na fields zake (text, textarea, number, price, date, list)

Hakuna migration inayohitajika — schema ni JSON tu.

## 8. Vipya vya toleo hili (Glass UI + Performance)

- **Panel nzima ni glassmorphism** — frosted cards, gradient mesh background, progress bar ya navigation, animations za kuingia, skeleton loaders, na mobile bottom-nav.
- **Nav styles 4 kwa websites za wateja** (Dashboard → Muonekano wa Website): Top classic, Floating Glass, **Side Navbar**, na Centered Minimal — pamoja na accent color na dark/light navbar.
- **Templates mpya za kisasa** kwa kila aina ya website: hero yenye gradient + glow, stats strip, features za glass cards, na CTA — zote zinafuata accent color ya mteja na zina scroll-reveal animations automatic.
- **Speed**: kila page ina-cache kwa saa 1 na inajipoteza PAPO HAPO mteja akibadilisha kitu (content versioning) — wageni hawapigi DB queries za collections kabisa. Lazy loading ya picha, preconnect ya CDN, na prefetching kwenye dashboard.
- Kwa production kubwa: washa Redis kwenye `CACHES` (una `redis` tayari kwenye requirements) — LocMem inatosha kuanzia.

## 9. Shortcodes (ndani ya design ya mteja)

```
[[collection:packages]]   → grid ya packages (au trips, destinations, products...)
[[site:name]] [[site:tagline]] [[site:phone]] [[site:email]]
[[site:address]] [[site:whatsapp]] [[site:logo]]
```

Editor ina blocks tayari (category "JamiiTek — Content Yako") zinazoziweka bila mteja kuandika chochote.

## 10. Usalama uliojengwa ndani

- Subdomain za wateja zinapata URLs za public TU (`builder/public_urls.py`) — haziwezi kufikia /admin wala /builder
- Kila view ya panel ina-check ownership (`owner=request.user`)
- Reserved subdomains (admin, api, www...) zinakataliwa
- AI ina rate limit (default 25/siku kwa mteja — badilisha kwa `BUILDER_AI_DAILY_LIMIT`)
- Admin wa JamiiTek anaweza ku-suspend site yoyote kutoka Django admin

## ⚠️ TAHADHARI TOFAUTI (si ya builder)

`ebenezeri/settings.py` yako ina Supabase DB password na SECRET_KEY zikiwa
hardcoded kama defaults. Zibadilishe Supabase kisha ziondoe kwenye code —
zibaki env variables tu.


## Toleo la 3 (JamiiTek Dark Tech + Tutorial System)

- **UI ya panel nzima ni style ya JamiiTek** (dark navy + neon green + mono) badala ya glass — inaendana na jamiitek.com.
- **Mobile-first kabisa**: bottom navigation bar kwenye simu, touch targets 44px+, tables zinazo-scroll, forms za full-width — mtu anaweza kuunda na ku-manage website nzima kwa simu.
- **Tutorial system**: `/builder/tutorial/` — mwongozo wa hatua 6, mwongozo maalum kwa kila aina ya website (tabs), mafunzo ya editor, na FAQ.
- **Onboarding checklist** kwenye dashboard — hatua 4 zenye progress bar zinazo-tick automatic (contact → content → design → publish).
- **Editor mpya (dark tech, cyan/violet)**: GrapesJS panels zote zime-theme, device switcher (Desktop/Tablet/Simu), na **guided tour ya hatua 5** inayojianzisha kwa mgeni wa kwanza (🎓 button inairudisha).
- **Code viewer ya kisasa (</> button)**: window ya macOS dots, dark editor, syntax highlighting, JetBrains Mono.
- **Homepage ya jamiitek.com**: sliding ads strip (matangazo 5 yanayojibadilisha + dots) na CTA button "🚀 Unda Website Yako" inayoenda `/builder/signup/` moja kwa moja.


## Toleo la 5 (Full Release — kila kitu)

### 📥 Booking / Inquiry System
- Kila item page (package, product, dish...) ina **booking form** built-in — jina, simu, email, tarehe, idadi ya watu, ujumbe.
- Block mpya kwenye editor: **"📥 Inquiry / Booking Form"** — mteja anaiweka page yoyote (shortcode `[[form:inquiry]]`).
- Submissions zote zinaenda **Dashboard → 📥 Inquiries**: status flow (New → Contacted → Closed), button ya "Reply on WhatsApp" yenye ujumbe tayari, na filter tabs.
- Kinga: honeypot ya bots + rate limit ya inquiries 30/saa kwa site.

### 🏫 Schemas mpya 3
- **School & Education** (programs, news/events, staff, admissions form)
- **Real Estate** (properties zenye bedrooms/bathrooms/location/features)
- **NGO & Charity** (projects, events, volunteer form)

### 🌐 Custom Domains (Premium)
- Field mpya: `is_premium` + `custom_domain` kwenye ClientWebsite (admin ana-mark premium kutoka Django admin).
- Mteja premium anaweka domain yake Dashboard → Website Appearance → Custom Domain.
- Middleware ina-route custom domain (na/bila www) kwenda site yake.
- **Hatua za admin (wewe)** kwa kila custom domain: (1) mteja aweke CNAME → jamiitek.onrender.com, (2) ongeza domain yake Render → Custom Domains (SSL automatic), (3) ongeza domain kwenye `ALLOWED_HOSTS` env var Render (comma-separated).

### ⚡ Redis Cache (production)
- Weka `REDIS_URL` kwenye Render env (Render ina Redis add-on, au tumia Upstash free tier) — mfumo unaanza kutumia Redis automatic. Bila hiyo, LocMem inaendelea (sawa kwa dev).

### Migration
`python manage.py migrate` — inaleta 0004 (custom_domain, is_premium, SiteInquiry).


## Toleo la 5.1 — Auto Custom Domains (bila Render dashboard)

Sasa custom domain ya mteja premium inasajiliwa Render **automatic** wakati
anapoihifadhi kwenye dashboard yake. Hatua za mkono zimebaki MOJA tu
(CNAME ya mteja kwa registrar wake).

### Setup ya mara moja (wewe, Render → Environment):
| Key | Value |
|---|---|
| `RENDER_API_KEY` | Render → Account Settings → API Keys → Create |
| `RENDER_SERVICE_ID` | ID ya service (srv-...) — ipo kwenye URL ya dashboard |
| `ALLOWED_HOSTS` | `*` — sasa ni SALAMA: middleware ndiyo whitelist halisi; host yoyote isiyosajiliwa inapata 404, si platform |

### Flow ya mteja premium:
1. Dashboard → Website Appearance → Custom Domain → anaandika domain → Save
2. Mfumo: unaisajili Render kupitia API (SSL automatic), una-remove ya zamani
   kama alibadilisha, na una-run **DNS check** — anaambiwa papo hapo kama
   CNAME yake tayari inaelekea kwetu au bado
3. Mteja anaweka CNAME → jamiitek.onrender.com kwa registrar — DAKIKA chache
   baadaye domain iko live na SSL

Bila API keys, kila kitu kingine kinaendelea (routing, database) — unapata
message ya kuongeza domain kwa mkono.


## Toleo la 6 — AI One-Shot Website Generator ✨

Kutoka sentensi moja ya biashara → website nzima tayari kwa sekunde 30.

### Flow ya mteja
1. Anafungua `/builder/ai/` (au anachagua kadi mpya kwenye Get Started)
2. Anaandika sentensi 1-3 kuhusu biashara yake — English au Swahili
3. Mfumo unafanya:
   - **Pass 1**: AI ina-generate JSON kamili (jina, tagline, About Us, items 4-6 zenye descriptions na bei, Why Choose Us, hero copy, accent color, nav layout)
   - **Pass 2**: AI nyingine kama senior editor ina-review Pass 1 na kuiboresha kuwa international quality
   - Total: **API calls 2 tu kwa website nzima**
4. Ana-signup (kama ni mgeni) — banner ya AI inaonyesha jina la biashara pre-filled
5. Baada ya signup, apply ina-sogeza content yote kwenye ClientWebsite + primary collection (packages/products/menu...)
6. Anafika dashboard yenye website tayari ~90% — anapaki maelezo machache na Publish

### Files mpya
- `builder/ai_oneshot.py` — generator + self-critique logic
- `builder/templates/builder/ai_generator.html` — page ya mtumiaji
- Views: `ai_generator`, `ai_generate_website`, `ai_apply`, `_apply_ai_plan`
- URLs: `/builder/ai/`, `/builder/ai/generate/`, `/builder/ai/apply/`

### UI updates
- **Get Started**: kadi mpya "🪄 Let AI Build It for You" juu kabisa (grid-column: 1/-1)
- **Signup**: banner ya violet inaonyesha kama flow imeanzia AI, na jina la biashara pre-filled
- **Homepage**: slide mpya ya AI kwenye sliding ads


## Toleo la 6.1 — AI Magic Buttons (Level 2) ✨

Kila field muhimu sasa ina button ya ✨ AI inayojaza field hiyo kwa content
ya kiwango cha juu — kwa muktadha kamili wa biashara.

### Jinsi inavyofanya kazi
1. Mtu anabonyeza ✨ karibu na field (mfano "Package Description")
2. JS inasoma FORM NZIMA (title, price, fields nyingine) kama context
3. POST /builder/ai/field/ na field_type + site_id + context + hint
   (hint = alichokiandika tayari — AI inaboresha kutoka pale)
4. AI ina-generate kwa prompt maalum ya field hiyo + self-check ndani ya prompt
5. Text ina-type polepole kwenye field (typing animation) + toast ya feedback

### Field types zinazopatikana (builder/ai_field.py)
site_name, tagline, about_us, hero_headline, hero_subline,
description, features_list, why_choose_us

### Zimewekwa wapi
- Item forms (packages, products, menu...): description + list fields
- Dashboard → Website Details: tagline
- Create site: tagline
- Kuongeza field mpya popote: weka tu `data-ai="field_type"` kwenye
  input/textarea na u-include `builder/_ai_magic.html` — button inajitokeza yenyewe

### Rate limiting
Inashare limit ile ile ya AI (BUILDER_AI_DAILY_LIMIT, default 25/siku)
na kila matumizi yanalogwa AiUsageLog.


## Toleo la 6.2 — AI Coach + AI Suggest + Caching (Levels 4 & 5) 💡

### AI Coach (dashboard)
Card mpya ya "💡 AI Coach" kwenye dashboard — ushauri 1-3 wenye maana ZAIDI
kwa hali halisi ya website, kila mmoja na action button ya moja kwa moja:
- Inquiries mpya zinasubiri → Reply now (P1)
- Website haiko hewani → Publish (P1/P2)
- Hakuna mawasiliano → Add contact (P1)
- Content chache → ✨ AI Suggest (P2)
- Hakuna tagline/logo, items bila picha, design haijaguswa (P3-P4)
Rule-based — HAKUNA API calls, bure na instant. (builder/insights.py)

### ✨ AI Suggest (bulk items)
Button kwenye kila collection: AI ina-generate items 5 mpya kwa muktadha
wa biashara + zilizopo (haizirudi), zinaingia kama **HIDDEN drafts** —
mtu ana-review, anaweka picha, kisha ana-tick "Visible" kwa anazozipenda.

### Caching ya AI (Level 5)
Field responses zina-cache dakika 30 (Redis/LocMem) — maombi yanayofanana
hayarudii API. Env: BUILDER_AI_CACHE_TTL (sekunde, default 1800).


## Toleo la 7 — SEO za Client Sites + Super-Admin Dashboard 🛡️

### SEO (kila website ya mteja, automatic)
- **Meta tags kamili kila page**: title ("Item · Site Name"), description
  (kutoka tagline/content ya page/item, HTML na shortcodes zimeondolewa), canonical URL
- **Open Graph + Twitter Cards**: mtu aki-share link WhatsApp/Facebook inaonekana
  na picha — item pages zinatumia PICHA YA ITEM yenyewe kama og:image (1200px)
- **JSON-LD LocalBusiness**: jina, simu, anwani, logo — Google inaielewa biashara
- **sitemap.xml** kwa kila site: home + pages + collections + items zote visible
- **robots.txt**: site iliyo live = Allow + sitemap link; DRAFT = Disallow (Google
  haioni kabla mteja haja-publish); sitemap ya draft inarudisha 404
- Custom domain za premium zinatumika kwenye URLs zote za SEO automatic

### Super-Admin Dashboard (/builder/superadmin/ — staff only)
- **Stats za platform**: total sites, live, premium, users, ukuaji (7d/30d),
  inquiries za wiki, AI calls za wiki, suspended
- **Search**: subdomain, jina, owner, custom domain
- **Filters**: All / Live / Draft / Premium / Suspended
- **Actions kwa click moja**: ⭐ Premium ON/OFF (inafungua custom domains kwa
  mteja), 🚫 Suspend/Reactivate (public inaonyesha 403 mara moja), Open dashboard
  ya mteja
- Link ya "🛡️ Super Admin" inaonekana sidenav kwa STAFF TU
- Kuwa staff: Django admin → Users → tick "Staff status"
