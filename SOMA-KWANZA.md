# JamiiBot — Website Widget (dark, flexible) + fixes

## Files (overwrite existing, keep same paths)

    apps/chatbot/webchat.py                                        NEW  widget engine + JS/CSS (dark)
    apps/chatbot/urls.py                                           EDIT routes
    apps/chatbot/views.py                                          EDIT handler param, chatbot_website, LID fix
    apps/chatbot/models.py                                         EDIT AI rules (clarify + language + one greeting)
    apps/chatbot/templates/chatbot/portal/website.html            NEW  "Add to Website" page (English)
    apps/chatbot/templates/chatbot/portal/base.html               EDIT sidebar link
    apps/chatbot/templates/chatbot/portal/conversation_detail.html EDIT Open in WhatsApp / LID (English)
    apps/static/img/jamiibot-icon.png                             NEW  logo
    apps/static/img/jamiibot-logo.png                             NEW  logo

No migrations. No new dependencies. Run collectstatic as usual.

## What changed this round
1. Widget UI is now DARK (WhatsApp dark theme) and fully flexible:
   on mobile it resizes to the visible area when the keyboard opens
   (visualViewport), so text no longer hides or jumps.
2. Greeting shows ONCE (served on open) — no more double greeting.
3. AI understanding: added rules — if the bot doesn't understand, it
   asks the customer to rephrase; it replies in the customer's language;
   it doesn't restart the long greeting mid-chat.
4. Client-facing pages converted to English (Add to Website page,
   conversation LID notice, sidebar label). Customer-facing chat stays
   Swahili/English (the customer's language); placeholders stay Swahili.

## LID note (Open in WhatsApp)
WhatsApp identifies many customers by an internal ID (LID), not a phone.
wa.me/<LID> is invalid. The chat page now: uses the real number when
available (or the number the customer typed via collect_phone), else
shows guidance instead of a broken button. Turn on "collect_phone" to
capture real numbers.
