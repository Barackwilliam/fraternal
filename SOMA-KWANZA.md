# JamiiBot — Widget ya Chat kwa Website (kamili)

Injini ni ile ile ya WhatsApp. Mteja anajiwekea mwenyewe bila msaada:
anaingia portal → "Weka kwenye Website" → ananakili code → anabandika.

## Faili (weka juu ya zilizopo, hifadhi njia ile ile)

    apps/chatbot/webchat.py                                   ← MPYA (widget engine)
    apps/chatbot/urls.py                                      ← imebadilika (routes 3 mpya)
    apps/chatbot/views.py                                     ← imebadilika (handler param + chatbot_website)
    apps/chatbot/templates/chatbot/portal/website.html       ← MPYA (ukurasa wa maelekezo)
    apps/chatbot/templates/chatbot/portal/base.html          ← imebadilika (link ya sidebar)
    apps/static/img/jamiibot-icon.png                         ← MPYA (logo — kitufe & avatar)
    apps/static/img/jamiibot-logo.png                         ← MPYA (logo kamili)

Hakuna migration mpya. Hakuna dependency mpya.
Hakikisha `collectstatic` inaendeshwa kwenye build (kama kawaida).

## Mteja anavyojiwekea (ndani ya portal yake)

  1. Anaingia JamiiBot portal.
  2. Sidebar → **"Weka kwenye Website"**.
  3. Anabonyeza **"Nakili code"** — anapata mstari wake mwenyewe:

         <script src="https://www.jamiitek.com/chatbot/widget/BOT_ID.js" defer></script>

     (BOT_ID yake imejaa tayari — kila mteja ana yake.)
  4. Anabandika kabla ya </body> kwenye tovuti yake, anahifadhi.
  5. Kitufe cha chat chenye logo ya JamiiBot kinaonekana chini kulia.

  Ukurasa pia una kitufe cha **"Jaribu sasa"** — anaona chat papo hapo.

## Routes zilizoongezwa
    GET  /chatbot/website/             → ukurasa wa maelekezo (portal, login)
    GET  /chatbot/widget/<BOT_ID>.js   → script (kitufe + UI + logo)
    POST /chatbot/web/<BOT_ID>/        → ujumbe -> injini -> jibu

## Handoff
  1. Mmiliki: WhatsApp ya biashara NA email (bot.client.email).
  2. Mtembeleaji: namba ya mmiliki + kitufe "📞 Piga simu".
