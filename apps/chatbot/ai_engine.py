"""
JamiiTek ChatBot — AI Engine (Groq)
Uses Groq API (FREE tier) — 14,400 requests/day, responds in under 1 second.
Get your free key at: https://console.groq.com
Model: llama-3.3-70b-versatile
"""
import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger('chatbot.ai')

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


class BotAIEngine:

    def __init__(self, bot_config):
        self.bot     = bot_config
        self.api_key = getattr(settings, 'GROQ_API_KEY', '')

    def build_messages(self, conversation, new_user_message: str) -> list:
        messages = []
        messages.append({
            "role":    "system",
            "content": self.bot.build_system_prompt()
        })
        limit  = getattr(self.bot, 'max_context_msgs', 10)
        recent = list(conversation.messages.order_by('-created_at')[:limit * 2])
        recent.reverse()
        for msg in recent:
            if msg.role == 'user':
                messages.append({"role": "user",      "content": msg.content})
            elif msg.role == 'assistant':
                messages.append({"role": "assistant", "content": msg.content})
        messages.append({"role": "user", "content": new_user_message})
        return messages

    def get_response(self, conversation, user_message: str) -> dict:
        start_time = time.time()

        if not self.bot.is_active or self.bot.status != 'active':
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'Bot not active'}

        try:
            sub = self.bot.subscription
            if not sub.is_active:
                return {'success': False, 'content': "This service has been suspended. Please contact the business directly.", 'tokens': 0, 'latency_ms': 0, 'error': 'Subscription inactive'}
            if sub.messages_remaining <= 0 and not sub.plan.is_unlimited:
                return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'Message limit reached'}
        except Exception:
            pass

        handoff_triggers = ['binadamu', 'mtu halisi', 'human', 'agent', 'speak to someone', 'mwambie mtu', 'operator', 'call me']
        if any(kw in user_message.lower() for kw in handoff_triggers):
            return {'success': True, 'content': self.bot.human_handoff_msg, 'tokens': 0, 'latency_ms': 0, 'is_handoff': True}

        if not self.api_key:
            logger.error("GROQ_API_KEY not set in settings.py")
            return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': 0, 'error': 'GROQ_API_KEY not configured'}

        try:
            messages = self.build_messages(conversation, user_message)

            payload = {
                "model":       GROQ_MODEL,
                "messages":    messages,
                "temperature": float(getattr(self.bot, 'ai_temperature', 0.7)),
                "max_tokens":  500,
                "top_p":       0.9,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type":  "application/json",
            }

            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)

            latency = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                logger.error(f"Groq API error {response.status_code}: {error_msg}")
                return {'success': False, 'content': self.bot.fallback_msg, 'tokens': 0, 'latency_ms': latency, 'error': error_msg}

            data    = response.json()
            content = data['choices'][0]['message']['content'].strip()
            tokens  = data.get('usage', {}).get('total_tokens', 0)

            return {'success': True, 'content': content, 'tokens': tokens, 'latency_ms': latency, 'model': GROQ_MODEL, 'is_handoff': False}

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