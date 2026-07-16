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
