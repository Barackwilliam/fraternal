"""
JamiiTek ChatBot — AI Engine (Google Gemini)
Uses Google Gemini API (FREE tier) instead of Anthropic Claude.
Free limits: 1,500 requests/day, 15 requests/minute — enough to start.
"""
import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger('chatbot.ai')

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


class BotAIEngine:

    def __init__(self, bot_config):
        self.bot = bot_config
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '')

    def build_gemini_contents(self, conversation, new_user_message: str) -> list:
        contents = []
        limit = getattr(self.bot, 'max_context_msgs', 10)
        recent = list(conversation.messages.order_by('-created_at')[:limit * 2])
        recent.reverse()
        for msg in recent:
            if msg.role == 'user':
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == 'assistant':
                contents.append({"role": "model", "parts": [{"text": msg.content}]})
        contents.append({"role": "user", "parts": [{"text": new_user_message}]})
        return contents

    def get_response(self, conversation, user_message: str) -> dict:
        start_time = time.time()

        if not self.bot.is_active or self.bot.status != 'active':
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'Bot not active'}

        try:
            sub = self.bot.subscription
            if not sub.is_active:
                return {'success': False, 'content': "Huduma hii imesimamishwa. Wasiliana na kampuni moja kwa moja.", 'tokens': 0, 'latency_ms': 0, 'error': 'Subscription inactive'}
            if sub.messages_remaining <= 0 and not sub.plan.is_unlimited:
                return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'Message limit reached'}
        except Exception:
            pass

        handoff_triggers = ['binadamu', 'mtu halisi', 'human', 'agent', 'speak to someone', 'mwambie mtu', 'operator', 'call me']
        if any(kw in user_message.lower() for kw in handoff_triggers):
            return {'success': True, 'content': self.bot.human_handoff_msg, 'tokens': 0, 'latency_ms': 0, 'is_handoff': True}

        if not self.api_key:
            logger.error("GEMINI_API_KEY not set in settings.py")
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'GEMINI_API_KEY not configured'}

        try:
            system_prompt = self.bot.build_system_prompt()
            contents = self.build_gemini_contents(conversation, user_message)

            payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": contents,
                "generationConfig": {
                    "temperature": float(getattr(self.bot, 'ai_temperature', 0.7)),
                    "maxOutputTokens": 500,
                    "topP": 0.9,
                }
            }

            response = requests.post(
                f"{GEMINI_API_URL}?key={self.api_key}",
                json=payload, timeout=30,
                headers={"Content-Type": "application/json"}
            )

            latency = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"Gemini API error {response.status_code}: {error_msg}")
                return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': latency, 'error': error_msg}

            data = response.json()
            content = (data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', self.bot.fallback_msg))
            tokens = data.get('usageMetadata', {}).get('totalTokenCount', 0)

            return {'success': True, 'content': content, 'tokens': tokens, 'latency_ms': latency, 'model': 'gemini-1.5-flash', 'is_handoff': False}

        except requests.Timeout:
            latency = int((time.time() - start_time) * 1000)
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': latency, 'error': 'Request timeout'}
        except Exception as e:
            logger.exception(f"Unexpected AI error for bot {self.bot.id}: {e}")
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': str(e)}

    def get_greeting(self, customer_name: str = "") -> str:
        if customer_name:
            return self.bot.greeting_msg.replace('{name}', customer_name)
        return self.bot.greeting_msg