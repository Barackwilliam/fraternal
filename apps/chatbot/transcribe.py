"""
Kutafsiri sauti kuwa maandishi — Groq Whisper.

KWA NINI

Wateja wa Tanzania wanatuma voice note nyingi kuliko maandishi.
Bila hii, ujumbe wa sauti ulikuwa unakuwa "[Sauti]" na AI ikijibu
kwamba haielewi — mteja anaona bot haifanyi kazi.

GHARAMA

`whisper-large-v3-turbo` ni $0.04 kwa saa ya sauti. Voice note ya
dakika moja ni sehemu ndogo ya senti. Kwenye plan ya bure ya Groq,
inahesabiwa kwenye rate limit ile ile.

MPAKA

Sauti ndefu kuliko dakika 10 inakataliwa. Si kwa gharama — ni kwa
sababu mteja anayetuma dakika 15 za sauti hataki jibu la bot,
anahitaji binadamu.
"""
import base64
import io
import logging
import os

import requests
from django.conf import settings

logger = logging.getLogger('chatbot.audio')

GROQ_URL = 'https://api.groq.com/openai/v1/audio/transcriptions'
MODEL = os.getenv('GROQ_WHISPER_MODEL', 'whisper-large-v3-turbo')

MAX_SECONDS = 600          # dakika 10
MAX_BYTES = 5 * 1024 * 1024

# WhatsApp inatuma ogg/opus; Whisper inaikubali
EXT = {
    'audio/ogg':  'ogg',
    'audio/opus': 'ogg',
    'audio/mpeg': 'mp3',
    'audio/mp4':  'm4a',
    'audio/aac':  'm4a',
    'audio/wav':  'wav',
    'audio/webm': 'webm',
}


def is_available():
    return bool(getattr(settings, 'GROQ_API_KEY', ''))


def transcribe(audio_b64, mime='audio/ogg', seconds=0, language=None):
    """
    Inarudisha maandishi, au tupu ikishindwa.

    Kamwe haitupi exception — ujumbe wa mteja usivunjike kwa sababu
    ya kutafsiri.
    """
    try:
        return _transcribe(audio_b64, mime, seconds, language)
    except Exception:
        logger.exception('kutafsiri sauti kumeshindwa')
        return ''


def _transcribe(audio_b64, mime, seconds, language):
    key = getattr(settings, 'GROQ_API_KEY', '')
    if not key or not audio_b64:
        return ''

    if seconds and seconds > MAX_SECONDS:
        logger.info('sauti ndefu mno (%ss) — imerukwa', seconds)
        return ''

    try:
        raw = base64.b64decode(audio_b64)
    except Exception:
        logger.warning('base64 ya sauti si sahihi')
        return ''

    if not raw or len(raw) > MAX_BYTES:
        return ''

    ext = EXT.get((mime or '').split(';')[0].strip().lower(), 'ogg')

    resp = requests.post(
        GROQ_URL,
        headers={'Authorization': f'Bearer {key}'},
        files={'file': (f'sauti.{ext}', io.BytesIO(raw), mime or 'audio/ogg')},
        data={
            'model': MODEL,
            'response_format': 'text',
            # Bila `language`, Whisper inagundua yenyewe. Hiyo ni bora
            # kwa Tanzania — mteja mmoja anaweza kuchanganya Kiswahili
            # na Kiingereza kwenye sentensi moja.
            **({'language': language} if language else {}),
        },
        timeout=60,
    )

    if resp.status_code != 200:
        logger.error('Whisper %s: %s', resp.status_code, resp.text[:200])
        return ''

    text = (resp.text or '').strip()
    if len(text) > 2000:
        text = text[:2000]
    logger.info('sauti imetafsiriwa: %s', text[:80])
    return text
