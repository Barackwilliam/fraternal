
## Anti-spam kwa fomu ya Contact (bots wa "Robertmeads")
Fomu ya /contact/ ilikuwa HAINA ulinzi wa server-side (Turnstile middleware
haikuwa kwenye MIDDLEWARE, na /contact/ ilikuwa imecomment-out). Sasa:
  - apps/templates/contact.html : honeypot field iliyofichwa (company_website).
  - apps/views.py               : ikijazwa honeypot -> email haitumwi (spam inadondoshwa kimya).
  - jamiitek/settings.py        : TurnstileMiddleware imewekwa kwenye MIDDLEWARE.
  - apps/turnstile_middleware.py: /contact/ imewezeshwa kwenye PROTECTED_PATHS.
Honeypot inazuia spam MARA MOJA bila keys. Ukiweka Turnstile keys,
middleware itaongeza ulinzi wa CAPTCHA pia.

## Demo seed data (Zawadi Electronics)
Jaza demo account kwa mbonyezo mmoja (Render free tier haiendeshi commands):
  apps/chatbot/demo_seed.py                 : seed_demo_bot(bot) — logic
  apps/management/commands/seed_demo.py      : `python manage.py seed_demo --email ...` (local/dev)
  apps/chatbot/views.py + urls.py            : URL /chatbot/seed-demo/ (staff au mmiliki wa bot)

JINSI YA KUTUMIA (production):
  1. Ingia kwenye demo account (mmiliki wa bot) AU staff.
  2. Fungua: https://www.jamiitek.com/chatbot/seed-demo/
  3. Bonyeza "Jaza demo sasa".
Inaweka: bidhaa 8, FAQ 7, mazungumzo 5, analytics za siku 7, na inaweka
utambulisho wa bot kuwa "Zawadi Electronics". Idempotent (kubonyeza tena
hakurudufishi). ONYO: inafuta huduma/FAQ/mazungumzo yaliyopo kwenye bot hiyo.


## Demo = JamiiBot inayojiuza yenyewe
demo_seed sasa inaweka bot inayoELEZA na kuSHAWISHI watu kutumia JamiiBot:
faida, bei (5k/10k/15k), setup, kuwa ni product ya JamiiTek, huduma za
JamiiTek (website, mobile app, system, chatbot, hosting), jinsi ya kuipata,
na tips za kuifanya bot ielewe biashara. Namba ya JamiiTek imewekwa
(+255 750 910 158). Bot ikiunganishwa itajibu kama muuzaji wa JamiiBot.

## Namba + ukurasa /bot/
- Demo bot number (watu wachati na demo) = 0768146230. Iko kwenye CTA za "Try the Live Demo".
- Handoff ya demo bot inaenda 0750910158 (demo_seed: owner_whatsapp).
- /bot/ (jamiibot_landing.html) imesasishwa: bei 5k/10k/15k, logo mpya, website widget,
  QR setup (Meta imeondolewa), M-Pesa/mobile money, handoff feature, plan slugs
  (basic/pro/enterprise). Claude-AI claim imeondolewa (mnatumia Groq).
- index.html: bei ya JamiiBot 15,000 -> 5,000 (JamiiBot pekee; hosting/domain hazikuguswa).
