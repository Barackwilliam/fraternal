
## Anti-spam kwa fomu ya Contact (bots wa "Robertmeads")
Fomu ya /contact/ ilikuwa HAINA ulinzi wa server-side (Turnstile middleware
haikuwa kwenye MIDDLEWARE, na /contact/ ilikuwa imecomment-out). Sasa:
  - apps/templates/contact.html : honeypot field iliyofichwa (company_website).
  - apps/views.py               : ikijazwa honeypot -> email haitumwi (spam inadondoshwa kimya).
  - jamiitek/settings.py        : TurnstileMiddleware imewekwa kwenye MIDDLEWARE.
  - apps/turnstile_middleware.py: /contact/ imewezeshwa kwenye PROTECTED_PATHS.
Honeypot inazuia spam MARA MOJA bila keys. Ukiweka Turnstile keys,
middleware itaongeza ulinzi wa CAPTCHA pia.
