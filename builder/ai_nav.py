"""
AI Navbar/Footer Generator — inatengeneza custom nav/footer HTML kutoka maneno.

Mteja anaandika 'nataka navbar ya kisasa yenye logo katikati na button ya
WhatsApp' → AI ina-generate HTML kamili + <style>, ikitumia placeholders za
mfumo ({{logo}}, {{nav_links}}, n.k.) ili links za pages zibaki dynamic.

Output ni HTML SAFI (bila markdown), tayari kuhifadhiwa kama custom_nav_html.
"""
import os
import logging

logger = logging.getLogger(__name__)

MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
TIMEOUT = 40


def _client():
    key = os.getenv('GROQ_API_KEY')
    if not key:
        return None
    try:
        from groq import Groq
    except ImportError:
        return None
    return Groq(api_key=key)


NAV_SYSTEM = """You are an expert front-end developer who builds beautiful,
responsive website navigation bars. You will receive a description of the
navbar a business owner wants. Produce ONE complete <nav> block followed by
a <style> block that styles it.

STRICT RULES:
1. Output ONLY the HTML: a <nav>...</nav> then a <style>...</style>. No markdown,
   no ```html fences, no explanations.
2. You MUST use these placeholders (they get filled automatically by the system):
   {{logo}}       - renders the logo <img> (may be empty, that's fine)
   {{site_name}}  - the business name text
   {{nav_links}}  - renders all the page links as <a> tags
   {{whatsapp}}   - a wa.me link (use for a contact/CTA button if wanted)
   {{phone}}      - phone number text
   Do NOT invent your own page links — always use {{nav_links}} for the menu.
3. Wrap the menu links container with id="jt-links" so the mobile menu works,
   and include a hamburger button: <button class="jt-burger-x" onclick="jtMenu(true)">☰</button>
   and a close button inside the menu: <button onclick="jtMenu(false)">×</button>
4. Scope ALL your CSS classes with a unique prefix to avoid clashes.
5. Use var(--accent) for the brand color, var(--nav-ink) for text where sensible.
6. Make it fully responsive: on mobile (max-width:820px) the menu should hide
   and show via the hamburger (position it as a slide-in or dropdown).
7. Keep it clean and modern. 30-70 lines of CSS max.

The result must be production-quality and look intentional."""


FOOTER_SYSTEM = """You are an expert front-end developer who builds beautiful,
responsive website footers. You will receive a description of the footer a
business owner wants. Produce ONE complete <footer> block followed by a
<style> block.

STRICT RULES:
1. Output ONLY the HTML: a <footer>...</footer> then <style>...</style>. No
   markdown, no fences, no explanations.
2. Use these placeholders (filled automatically):
   {{site_name}}   - business name
   {{tagline_line}}- renders tagline in a <div> (may be empty)
   {{nav_links}}   - all page links as <a> tags
   {{phone_line}}  - phone in a <div> (may be empty)
   {{email_line}}  - email in a <div> (may be empty)
   {{whatsapp_line}}- whatsapp link in a <div> (may be empty)
   {{year}}        - current year
   Always end with a credit line: Built with JamiiTek (link to https://jamiitek.com).
3. Scope ALL CSS classes with a unique prefix.
4. Use var(--accent) for accents.
5. Fully responsive: columns should stack on mobile (max-width:720px).
6. Clean and modern. 30-70 lines of CSS max.

Production-quality, intentional design."""


def _generate(system, site, brief, extra_ctx=''):
    client = _client()
    if client is None:
        return False, 'AI is not configured on the server.'
    if len(brief) > 800:
        return False, 'Description is too long (max 800 characters).'

    user = (
        f'Business: "{site.site_name}" (type: {site.website_type})\n'
        f'Brand/accent color: {site.accent_color}\n'
        f'{extra_ctx}'
        f'The owner wants: "{brief.strip()}"\n\n'
        f'Build it now. Remember: raw HTML + <style> only, use the placeholders.'
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL, temperature=0.7, max_tokens=1800,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            timeout=TIMEOUT,
        )
        html = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception('AI nav/footer generation failed')
        return False, f'AI is temporarily unavailable ({type(e).__name__}).'

    # Safisha fences
    if html.startswith('```'):
        lines = html.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
        html = '\n'.join(lines).strip()

    if not html or '<' not in html:
        return False, 'AI did not return valid HTML — please try again.'
    return True, html[:40000]


def generate_navbar(site, brief):
    """Rudisha (ok, html_or_error)."""
    return _generate(NAV_SYSTEM, site, brief,
                     extra_ctx='This is for the site NAVBAR.\n')


def generate_footer(site, brief):
    """Rudisha (ok, html_or_error)."""
    return _generate(FOOTER_SYSTEM, site, brief,
                     extra_ctx='This is for the site FOOTER.\n')
