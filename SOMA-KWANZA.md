# JamiiBot — Widget ya Chat kwa Website (+ Logo)

Injini ni ile ile ya WhatsApp — hakuna mfumo mpya, ni mlango mwingine tu.

## Faili (weka juu ya zilizopo, hifadhi directory ile ile)

    apps/chatbot/webchat.py             ← MPYA (handler + views + widget JS/CSS)
    apps/chatbot/urls.py                ← imebadilika (routes 2 mpya)
    apps/chatbot/views.py               ← imebadilika (parameter 1 ya hiari: handler)
    apps/static/img/jamiibot-icon.png   ← MPYA (logo ya roboti — kitufe & avatar)
    apps/static/img/jamiibot-logo.png   ← MPYA (logo kamili kwa matumizi mengine)

Hakuna migration mpya. Hakuna dependency mpya.
Kwenye build/deploy hakikisha `collectstatic` inaendeshwa (kama kawaida)
ili picha zipatikane kwenye /static/img/.

## Logo
- Kitufe kinachoelea (floating button) na avatar ya header vinatumia
  `jamiibot-icon.png`.
- Maandishi "Inaendeshwa na JamiiBot" ni LINK inayofungua
  https://www.jamiitek.com/bot/ (tab mpya).

## Kuiweka kwenye tovuti ya mteja (mstari mmoja)

    <script src="https://www.jamiitek.com/chatbot/widget/BOT_ID.js" defer></script>

## Routes

    GET  /chatbot/widget/<BOT_ID>.js   → script (kitufe + UI + logo)
    POST /chatbot/web/<BOT_ID>/        → ujumbe -> injini -> jibu

## Handoff
  1. Mmiliki: WhatsApp ya biashara NA email (bot.client.email).
  2. Mtembeleaji: namba ya mmiliki + kitufe "📞 Piga simu".
