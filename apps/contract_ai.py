"""
AI Contract Writer — inaandaa rasimu za mikataba ya kitaalamu (EN + SW).

Falsafa: AI inaandaa RASIMU. Mmiliki (JamiiTek) anaboresha kabla ya kutuma
kwa mteja. AI haisaini chochote — signing ni ya mteja pekee.

Inaandaa mkataba kwa lugha ZOTE mbili (Kiingereza + Kiswahili) ili mteja
achague. Mkataba unafuata muundo wa kimataifa: parties, scope, deliverables,
payment, timeline, IP rights, warranties, termination, governing law.
"""
import os
import re
import json
import logging

logger = logging.getLogger(__name__)

MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
TIMEOUT = 90


def _client():
    key = os.getenv('GROQ_API_KEY')
    if not key:
        return None
    try:
        from groq import Groq
    except ImportError:
        return None
    return Groq(api_key=key)


SYSTEM = """You are a professional contract writer for JamiiTek, a web
development company in Tanzania. You draft clear, professional service
agreements that meet international standards while being appropriate for
the Tanzanian business context.

You will draft the SAME contract in BOTH English and Swahili.

STRICT RULES:
1. Output ONLY valid JSON, no markdown, no preamble. Schema:
   {"title": "...", "body_en": "...", "body_sw": "..."}
2. "body_en" and "body_sw" are the full contract in clean HTML using ONLY:
   <h2>, <h3>, <p>, <ul>, <li>, <strong>, <ol>. NO styles, scripts, or tables.
3. The contract MUST include these numbered sections (adapt to the project):
   1. Parties (JamiiTek as "the Provider" and the client as "the Client")
   2. Scope of Work / Services (what will be delivered)
   3. Deliverables
   4. Timeline / Delivery Schedule
   5. Payment Terms (amount, currency, schedule)
   6. Client Responsibilities (providing content, feedback, access)
   7. Revisions and Changes
   8. Intellectual Property (ownership transfers on final payment)
   9. Confidentiality
   10. Warranties and Support
   11. Termination
   12. Limitation of Liability
   13. Governing Law (laws of the United Republic of Tanzania)
   14. Entire Agreement / Signatures
4. Be professional, clear, and fair to both parties. Use real contract
   language, not casual text. Avoid making up specific facts not provided —
   use clear placeholders like [describe deliverable] only if truly needed,
   but prefer to write complete, sensible clauses based on the project info.
5. The Swahili version must be natural, professional Tanzanian Swahili — a
   proper legal-business register, not a rough translation.
6. Do NOT include a title heading inside the body (the title is separate).
   Start body with <h2>1. Parties</h2> style sections.
7. Reference the payment amount, currency, timeline, and payment terms given.
8. End each version with a signature section stating both parties will sign,
   with lines for names, dates (the actual signing is handled by the app).
"""


def generate_contract(project_info):
    """
    project_info: dict yenye {client_name, company, project_name, title,
                              total_amount, currency, payment_terms, timeline,
                              scope, provider_rep}
    Rudisha (ok, dict_or_error) — dict: {title, body_en, body_sw}
    """
    client = _client()
    if client is None:
        return False, 'AI is not configured (GROQ_API_KEY missing).'

    info = project_info
    amount_line = ''
    if info.get('total_amount'):
        amount_line = f"Total amount: {info.get('currency', 'TZS')} {info['total_amount']}\n"

    user = (
        f"Draft a professional service agreement for the following project.\n\n"
        f"Provider: JamiiTek (web development company, Dar es Salaam, Tanzania)\n"
        f"Provider representative: {info.get('provider_rep') or 'JamiiTek Management'}\n"
        f"Client name: {info.get('client_name', '')}\n"
        f"Client company: {info.get('company', '')}\n"
        f"Project: {info.get('project_name') or info.get('title', 'Website Development')}\n"
        f"{amount_line}"
        f"Payment terms: {info.get('payment_terms', 'To be agreed')}\n"
        f"Timeline: {info.get('timeline', 'To be agreed')}\n"
        f"Scope / description: {info.get('scope', 'Design and development of a website.')}\n\n"
        f"Draft the full contract in BOTH English and Swahili now. Return ONLY the JSON."
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0.4,   # chini — mkataba unahitaji usahihi, si ubunifu
            max_tokens=4000,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user},
            ],
            timeout=TIMEOUT,
        )
        raw = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception('AI contract generation failed')
        return False, f'AI error ({type(e).__name__})'

    if raw.startswith('```'):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return False, 'AI did not return valid JSON'
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return False, 'AI returned malformed JSON'

    body_en = _clean_html(data.get('body_en', ''))
    body_sw = _clean_html(data.get('body_sw', ''))
    if not body_en or not body_sw:
        return False, 'AI response missing English or Swahili body'

    return True, {
        'title': (data.get('title') or info.get('title') or 'Service Agreement').strip()[:200],
        'body_en': body_en,
        'body_sw': body_sw,
    }


def _clean_html(html):
    """Ruhusu tags salama tu."""
    html = re.sub(r'<(script|style|iframe|head|html|body)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.I)
    html = re.sub(r'</?(?:html|head|body|script|style|iframe)[^>]*>', '', html, flags=re.I)
    html = re.sub(r'\son\w+="[^"]*"', '', html, flags=re.I)
    html = re.sub(r'\sstyle="[^"]*"', '', html, flags=re.I)
    return html.strip()
