"""
AI Assistant (Groq) — inamsaidia mteja kutengeneza content na HTML sections.
Weka GROQ_API_KEY kwenye environment variables za Render.
    pip install groq
"""
import os
import json
import logging
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import AiUsageLog, ClientWebsite

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
AI_DAILY_LIMIT = int(os.getenv('BUILDER_AI_DAILY_LIMIT', '25'))

SYSTEM_PROMPT = """You are a website content assistant for businesses in Tanzania and East Africa.

RULES:
1. If asked for a website SECTION, return CLEAN HTML ONLY (no ```html fences, no explanations).
   - Use inline styles only (no external CSS).
   - The design must be modern and responsive (max-width, flex/grid, good padding).
   - Do not use <html>, <head>, or <body> — section content only.
   - Do not use javascript.
2. If asked for TEXT only (descriptions, taglines, about us), return plain text without HTML.
3. Reply in the language the user wrote in (English or Swahili).
4. Content must match the business context provided."""


def _check_rate_limit(user):
    since = timezone.now() - timedelta(days=1)
    used = AiUsageLog.objects.filter(user=user, created_at__gte=since).count()
    return used < AI_DAILY_LIMIT, AI_DAILY_LIMIT - used


@login_required
@require_POST
def ai_assist(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    prompt = (payload.get('prompt') or '').strip()
    website_id = payload.get('website_id')
    if not prompt:
        return JsonResponse({'error': 'Please describe what you need first.'}, status=400)
    if len(prompt) > 2000:
        return JsonResponse({'error': 'Your request is too long (max 2000 characters).'}, status=400)

    ok, remaining = _check_rate_limit(request.user)
    if not ok:
        return JsonResponse(
            {'error': f'You have reached the limit of {AI_DAILY_LIMIT} requests per day. Try again tomorrow.'},
            status=429,
        )

    website = ClientWebsite.objects.filter(id=website_id, owner=request.user).first()
    context = ''
    if website:
        context = (f'\n\nBUSINESS CONTEXT: name "{website.site_name}", '
                   f'website type: {website.website_type}, '
                   f'tagline: "{website.tagline}".')

    try:
        from groq import Groq
        client = Groq(api_key=os.environ['GROQ_API_KEY'])
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT + context},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        result = completion.choices[0].message.content.strip()
        # Ondoa markdown fences kama model imeziweka
        if result.startswith('```'):
            result = result.split('\n', 1)[-1].rsplit('```', 1)[0].strip()
    except KeyError:
        return JsonResponse({'error': 'GROQ_API_KEY is not configured on the server.'}, status=500)
    except Exception:
        logger.exception('Groq API error')
        return JsonResponse({'error': 'The AI is unavailable right now. Please try again later.'}, status=502)

    AiUsageLog.objects.create(user=request.user, website=website)
    is_html = result.lstrip().startswith('<')
    return JsonResponse({'result': result, 'is_html': is_html, 'remaining': remaining - 1})
