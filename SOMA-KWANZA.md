# JamiiBot — Website widget + mobile-responsive portal

## Files (overwrite existing, keep same paths). No migrations, no new deps. Run collectstatic.

CODE
    apps/chatbot/webchat.py       NEW  website chat widget (dark, keyboard-flexible)
    apps/chatbot/urls.py          EDIT routes
    apps/chatbot/views.py         EDIT handler param, chatbot_website, LID fix
    apps/chatbot/models.py        EDIT AI rules (clarify + language + single greeting)

TEMPLATES (apps/chatbot/templates/chatbot/portal/)
    website.html               NEW  "Add to Website" page (English)
    base.html                  EDIT sidebar link
    conversation_detail.html   EDIT mobile responsive + LID (English)
    conversations.html         EDIT mobile responsive
    billing.html               EDIT mobile responsive
    config.html                EDIT mobile responsive
    connect.html               EDIT mobile responsive (small screens)

IMAGES
    apps/static/img/jamiibot-icon.png   NEW
    apps/static/img/jamiibot-logo.png   NEW

## Mobile fixes this round
- Conversation page: the 260px sidebar used to crush the chat on phones.
  Now the layout stacks vertically (chat on top, customer details below),
  chat height uses dvh, bubbles widen. Fixed at <=820px and <=420px.
- Conversations list: 4-col stats -> 2-col (<=768) -> 1-col (<=400);
  message preview capped to 52vw; time/count hidden on very small screens;
  handoff "resume" button goes full width.
- Billing: 3 plan columns stack to 1 on phones.
- Config: tabs tighten, item cards wrap.
- Connect: QR box scales to width on very small screens.
Pages that were already responsive (dashboard, register, login, wizard)
were left unchanged. All 8 portal pages verified returning 200.
