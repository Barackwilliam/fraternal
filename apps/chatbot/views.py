"""
JamiiTek ChatBot SaaS — Views
NEW APPROACH: William manages ONE Meta account.
- Client provides WhatsApp number only
- William adds Phone Number ID via manage panel
- ONE global webhook URL routes by phone_number_id
"""
import json
import logging
import re
import secrets
import threading

import requests
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Count
from django.conf import settings

from .models import (
    ChatbotClient, BotConfig, BotService, BotFAQ,
    BotSubscription, SubscriptionPlan, SubscriptionPayment,
    Conversation, Message, BotAnalytics
)
from .ai_engine import BotAIEngine
from .whatsapp import build_services_menu
from .bridge import BaileysHandler
from . import handoff
from . import knowledge
from . import ratelimit

logger = logging.getLogger('chatbot.views')


# ════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════

def _get_or_create_client(user):
    """
    Return the ChatbotClient for this user, creating one if needed.
    Handles users who logged in via the main portal (not chatbot_login).
    """
    client = ChatbotClient.objects.filter(user=user).first()
    if client:
        return client
    full_name     = user.get_full_name() or user.username
    business_name = user.username
    email         = user.email or f"{user.username}@jamiitek.com"
    phone         = ''
    try:
        from apps.models import Client as PortalClient
        pc = PortalClient.objects.get(user=user)
        full_name     = pc.name or full_name
        business_name = pc.company or pc.name or business_name
        phone         = pc.phone or ''
    except Exception:
        pass
    return ChatbotClient.objects.create(
        user=user, full_name=full_name,
        business_name=business_name, email=email, phone=phone,
    )


def _notify_william(bot):
    """
    Notify William via WhatsApp that a new bot needs setup.
    Sends to WILLIAM_WHATSAPP from settings using master token.
    """
    try:
        master_token = getattr(settings, 'WHATSAPP_MASTER_TOKEN', '')
        william_phone = getattr(settings, 'WILLIAM_WHATSAPP', '')
        william_phone_id = getattr(settings, 'WILLIAM_PHONE_NUMBER_ID', '')

        if not all([master_token, william_phone, william_phone_id]):
            logger.warning("William notification skipped — WILLIAM_WHATSAPP or WILLIAM_PHONE_NUMBER_ID not set")
            return

        msg = (
            f"🤖 *BOT MPYA — INAHITAJI SETUP*\n\n"
            f"👤 Mteja: {bot.client.full_name}\n"
            f"🏢 Biashara: {bot.client.business_name}\n"
            f"📱 WhatsApp: {bot.whatsapp_number}\n"
            f"🤖 Bot: {bot.bot_name}\n\n"
            f"➡️ Hatua: Ingia Meta → Ongeza nambari → Weka Phone ID\n"
            f"🔗 /manage/chatbot/bots/{bot.id}/whatsapp/"
        )

        url = f"https://graph.facebook.com/v19.0/{william_phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": william_phone,
            "type": "text",
            "text": {"body": msg}
        }
        headers = {
            "Authorization": f"Bearer {master_token}",
            "Content-Type": "application/json"
        }
        requests.post(url, json=payload, headers=headers, timeout=10)
        logger.info(f"William notified about new bot: {bot.bot_name}")
    except Exception as e:
        logger.error(f"Failed to notify William: {e}")


# ════════════════════════════════════════════════════════
# AUTHENTICATION
# ════════════════════════════════════════════════════════

def chatbot_register(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)

    if request.method == 'POST':
        data = request.POST
        errors = []

        username  = data.get('username', '').strip().lower()
        password  = data.get('password', '')
        password2 = data.get('password2', '')
        email     = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        business  = data.get('business_name', '').strip()
        phone     = data.get('phone', '').strip()

        if not all([username, password, email, full_name, business]):
            errors.append("Tafadhali jaza sehemu zote zinazohitajika.")
        if User.objects.filter(username=username).exists():
            errors.append("Jina hilo la mtumiaji linatumiwa tayari.")
        if User.objects.filter(email=email).exists():
            errors.append("Barua pepe hiyo imesajiliwa tayari.")
        if password != password2:
            errors.append("Nywila hazifanani.")
        if len(password) < 8:
            errors.append("Nywila lazima iwe na herufi 8 au zaidi.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'chatbot/portal/register.html', {'plans': plans})

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, password=password, email=email,
                    first_name=full_name.split()[0] if full_name else ''
                )
                ChatbotClient.objects.create(
                    user=user, full_name=full_name, business_name=business,
                    email=email, phone=phone
                )
                login(request, user)
                messages.success(request, f"Karibu {full_name}! Sasa unda bot yako ya kwanza.")
                return redirect('chatbot_setup_wizard')
        except Exception as e:
            logger.exception(f"Registration error: {e}")
            messages.error(request, "Tatizo la kiufundi. Jaribu tena.")

    return render(request, 'chatbot/portal/register.html', {'plans': plans})


def chatbot_login(request):
    # Already logged in with chatbot account → go to dashboard
    if request.user.is_authenticated:
        if hasattr(request.user, 'chatbot_profile'):
            return redirect('chatbot_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user and not user.is_staff:
            # Ensure ChatbotClient exists for this user
            # Works for BOTH chatbot-registered users AND portal-registered users
            if not hasattr(user, 'chatbot_profile'):
                from apps.chatbot.models import ChatbotClient
                # Try to get info from portal Client profile
                full_name     = user.get_full_name() or user.username
                business_name = user.username
                email         = user.email or f"{user.username}@jamiitek.com"
                phone         = ''
                try:
                    from apps.models import Client as PortalClient
                    pc = PortalClient.objects.get(user=user)
                    full_name     = pc.name or full_name
                    business_name = pc.company or pc.name or business_name
                    phone         = pc.phone or ''
                except Exception:
                    pass
                ChatbotClient.objects.create(
                    user=user,
                    full_name=full_name,
                    business_name=business_name,
                    email=email,
                    phone=phone,
                )

            login(request, user)
            return redirect('chatbot_dashboard')

        elif user and user.is_staff:
            # Staff/admin — just log in and go to dashboard
            login(request, user)
            return redirect('chatbot_dashboard')

        messages.error(request, "Invalid username or password.")

    return render(request, 'chatbot/portal/login.html')


def chatbot_logout(request):
    logout(request)
    return redirect('chatbot_login')


# ════════════════════════════════════════════════════════
# SETUP WIZARD
# ════════════════════════════════════════════════════════

@login_required(login_url='chatbot_login')
def chatbot_setup_wizard(request):
    client = _get_or_create_client(request.user)
    step   = int(request.GET.get('step', 1))
    bot    = client.bots.first()

    # Bot already deployed (pending or active) — go to dashboard unless editing
    if bot and bot.status in ('active', 'pending') and not request.GET.get('edit') and request.method == 'GET':
        if step == 1:
            return redirect('chatbot_dashboard')

    services = bot.services.all() if bot else []
    faqs     = bot.faqs.all() if bot else []
    plans    = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')

    context = {
        'client': client, 'step': step, 'bot': bot,
        'services': services, 'faqs': faqs, 'plans': plans,
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        # ══════════════════════════════════════════════════════
        # WIZARD: HATUA 3, SI 6
        # ══════════════════════════════════════════════════════
        # Zamani: biashara, jumbe, huduma, FAQs, namba, mpango.
        #
        # Mbili kati ya hizo zilimtaka mmiliki ABASHIRI kabla hajaona
        # bot yake ikifanya kazi:
        #
        #   Jumbe  — greeting, fallback, handoff. Chaguo-msingi
        #            zinafanya kazi mara moja; mmiliki anaziboresha
        #            baada ya kuona bot ikijibu.
        #   FAQs   — kubashiri maswali ambayo wateja HAWAJAULIZA.
        #            Mfumo wa maarifa sasa unayajifunza kutoka maswali
        #            HALISI — kuuliza mbele ni kuuliza abuni.
        #
        # Zote mbili zimehamia /chatbot/config/ baada ya kuanza.
        #
        # Namba ya WhatsApp imeungana na hatua ya 1 — ni taarifa ya
        # biashara, si hatua yake mwenyewe.

        # ── HATUA 1: Biashara ──
        if action == 'save_step1':
            import re as _re
            bot_name    = request.POST.get('bot_name', '').strip()
            business    = request.POST.get('business_name', '').strip()
            description = request.POST.get('description', '').strip()
            wa_number   = request.POST.get('whatsapp_number', '').strip()
            language    = request.POST.get('language', 'sw+en')
            tone        = request.POST.get('tone', 'friendly')

            if not all([bot_name, business, description]):
                messages.error(request, "Jaza jina la bot, biashara na maelezo.")
                return render(request, 'chatbot/portal/wizard.html', context)

            digits = _re.sub(r'\D', '', wa_number)
            if wa_number and not (7 <= len(digits) <= 15):
                messages.error(request, "Namba ya WhatsApp si sahihi.")
                context.update({'bot': bot, 'step': 1})
                return render(request, 'chatbot/portal/wizard.html', context)

            if bot:
                bot.bot_name = bot_name; bot.business_name = business
                bot.description = description; bot.language = language
                bot.tone = tone
                if wa_number: bot.whatsapp_number = wa_number
                bot.save()
            else:
                bot = BotConfig.objects.create(
                    client=client, bot_name=bot_name, business_name=business,
                    description=description, language=language, tone=tone,
                    whatsapp_number=wa_number,
                    greeting_msg=f"Karibu {{name}}! Mimi ni {bot_name} wa {business}. Nitakusaidiaje?",
                )
            return redirect('/chatbot/setup/?step=2')

        # ── Jumbe: sasa ziko /chatbot/config/, si kwenye wizard ──
        elif action == 'save_step2':
            if not bot: return redirect('/chatbot/setup/?step=1')
            bot.greeting_msg      = request.POST.get('greeting_msg', bot.greeting_msg)
            bot.fallback_msg      = request.POST.get('fallback_msg', bot.fallback_msg)
            bot.human_handoff_msg = request.POST.get('human_handoff_msg', bot.human_handoff_msg)
            bot.collect_name      = request.POST.get('collect_name') == 'on'
            bot.collect_phone     = request.POST.get('collect_phone') == 'on'
            bot.save()
            return redirect('/chatbot/config/')

        # ── HATUA 2: Huduma ──
        elif action == 'add_service':
            if bot:
                name  = request.POST.get('service_name', '').strip()
                desc  = request.POST.get('service_desc', '').strip()
                price = request.POST.get('service_price', '').strip()
                if name and desc:
                    BotService.objects.create(bot=bot, name=name, description=desc, price=price)
            return redirect('/chatbot/setup/?step=2')

        elif action == 'delete_service':
            if bot:
                BotService.objects.filter(id=request.POST.get('service_id'), bot=bot).delete()
            return redirect('/chatbot/setup/?step=2')

        elif action == 'next_step2':
            _notify_william(bot)
            return redirect('/chatbot/setup/?step=3')

        # ── FAQs: sasa ziko /chatbot/config/ na /chatbot/knowledge/ ──
        # Kuuliza FAQs kabla mteja hajaanza ni kumtaka abashiri maswali
        # ambayo wateja HAWAJAULIZA. Mfumo wa maarifa sasa unayajifunza
        # kutoka maswali halisi — bot ikishindwa, swali linaingia kwenye
        # orodha na mmiliki analijibu mara moja.
        elif action == 'add_faq':
            if bot:
                q = request.POST.get('faq_question', '').strip()
                a = request.POST.get('faq_answer', '').strip()
                if q and a:
                    BotFAQ.objects.create(bot=bot, question=q, answer=a)
            return redirect(request.POST.get('next') or '/chatbot/config/')

        elif action == 'delete_faq':
            if bot:
                BotFAQ.objects.filter(id=request.POST.get('faq_id'), bot=bot).delete()
            return redirect(request.POST.get('next') or '/chatbot/config/')

        # ── HATUA 3: Mpango + kuanza ──
        elif action == 'deploy':
            if not bot:
                messages.error(request, "Tafadhali anza kutoka hatua ya kwanza.")
                return redirect('/chatbot/setup/?step=1')

            # Safely resolve plan — never pass '' to filter(id=...)
            plan_id = request.POST.get('plan_id', '').strip()
            plan = None
            if plan_id and plan_id.isdigit():
                plan = SubscriptionPlan.objects.filter(id=int(plan_id), is_active=True).first()
            if not plan:
                plan = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order').first()
            if not plan:
                messages.error(request, "Hakuna mpango uliowekwa. Wasiliana na timu yetu.")
                context.update({'step': 6})
                return render(request, 'chatbot/portal/wizard.html', context)

            sub, created = BotSubscription.objects.get_or_create(
                bot=bot,
                defaults={
                    'plan':       plan,
                    'status':     'trial',
                    'trial_ends': date.today() + timedelta(days=7),
                    'end_date':   date.today() + timedelta(days=7),
                }
            )
            if not created:
                sub.plan = plan
                sub.save(update_fields=['plan'])

            # Zamani bot ilikaa 'pending' hadi William aweke Meta phone ID
            # kwa mkono — mteja alisubiri saa 24. Kwa Baileys hakuna cha
            # kusubiri: trial inaanza, QR inafunguka, mteja anascan mwenyewe.
            #
            # Lango la malipo halijaondoka — limehamia kwenye subscription.
            # `_process_message` inakagua `sub.is_active`, ambayo ni kweli
            # kwa 'trial' na 'active' pekee. Trial ikiisha bila malipo,
            # bot inanyamaza yenyewe.
            bot.status      = 'active'
            bot.is_active   = True
            bot.deployed_at = timezone.now()
            bot.save()

            # Anzisha session ili QR iwe tayari mteja anapofika ukurasa
            try:
                from apps.chatbot import bridge
                if bridge.is_configured():
                    bridge.start_session(bot.session_name)
            except Exception:
                logger.warning('Haikuweza kuanzisha session %s', bot.session_name)

            messages.success(request, f"🎉 Bot yako '{bot.bot_name}' iko tayari! Iunganishe na WhatsApp sasa.")
            return redirect('chatbot_connect')

    # Refresh services/faqs after any POST changes
    if bot:
        context['services'] = bot.services.all()
        context['faqs']     = bot.faqs.all()
        context['bot']      = bot

    return render(request, 'chatbot/portal/wizard.html', context)


# ════════════════════════════════════════════════════════
# CLIENT PORTAL
# ════════════════════════════════════════════════════════

@login_required(login_url='chatbot_login')
def chatbot_dashboard(request):
    client = _get_or_create_client(request.user)
    bot    = client.bots.first()
    if not bot:
        return redirect('chatbot_setup_wizard')

    total_convs  = bot.conversations.count()
    total_msgs   = Message.objects.filter(conversation__bot=bot).count()
    today_msgs   = Message.objects.filter(conversation__bot=bot, created_at__date=date.today()).count()
    unique_users = bot.conversations.values('customer_phone').distinct().count()

    analytics_7d = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        analytics_7d.append({
            'date': d.strftime('%d %b'),
            'count': Message.objects.filter(conversation__bot=bot, created_at__date=d, role='user').count()
        })

    context = {
        'client': client, 'bot': bot,
        'sub': getattr(bot, 'subscription', None),
        'total_convs': total_convs, 'total_msgs': total_msgs,
        'today_msgs': today_msgs, 'unique_users': unique_users,
        'analytics_7d': json.dumps(analytics_7d),
        'recent_convs': bot.conversations.order_by('-last_message_at')[:8],
    }
    return render(request, 'chatbot/portal/dashboard.html', context)


@login_required(login_url='chatbot_login')
def chatbot_config(request):
    client = _get_or_create_client(request.user)
    bot    = client.bots.first()
    if not bot:
        messages.warning(request, "Please complete your bot setup first.")
        return redirect('chatbot_setup_wizard')

    if request.method == 'POST':
        section = request.POST.get('section')

        if section == 'basic':
            bot.bot_name    = request.POST.get('bot_name', bot.bot_name)
            bot.description = request.POST.get('description', bot.description)
            bot.language    = request.POST.get('language', bot.language)
            bot.tone        = request.POST.get('tone', bot.tone)
            bot.save(); messages.success(request, "Taarifa za msingi zimehifadhiwa.")

        elif section == 'messages':
            bot.greeting_msg      = request.POST.get('greeting_msg', bot.greeting_msg)
            bot.fallback_msg      = request.POST.get('fallback_msg', bot.fallback_msg)
            bot.human_handoff_msg = request.POST.get('human_handoff_msg', bot.human_handoff_msg)
            bot.save(); messages.success(request, "Ujumbe wa bot umehifadhiwa.")

        elif section == 'add_service':
            name = request.POST.get('service_name', '').strip()
            desc = request.POST.get('service_desc', '').strip()
            if name and desc:
                BotService.objects.create(bot=bot, name=name, description=desc,
                    price=request.POST.get('service_price', '').strip())
                messages.success(request, f"Huduma '{name}' imeongezwa.")

        elif section == 'delete_service':
            BotService.objects.filter(id=request.POST.get('service_id'), bot=bot).delete()
            messages.success(request, "Huduma imefutwa.")

        elif section == 'add_faq':
            q = request.POST.get('faq_question', '').strip()
            a = request.POST.get('faq_answer', '').strip()
            if q and a:
                BotFAQ.objects.create(bot=bot, question=q, answer=a)
                messages.success(request, "FAQ imeongezwa.")

        elif section == 'delete_faq':
            BotFAQ.objects.filter(id=request.POST.get('faq_id'), bot=bot).delete()
            messages.success(request, "FAQ imefutwa.")

        return redirect('chatbot_config')

    return render(request, 'chatbot/portal/config.html', {
        'client': client, 'bot': bot,
        'services': bot.services.all(), 'faqs': bot.faqs.all(),
    })


@login_required(login_url='chatbot_login')
def chatbot_conversations(request):
    client = _get_or_create_client(request.user)
    bot    = client.bots.first()
    if not bot:
        messages.warning(request, "Complete your bot setup to view conversations.")
        return redirect('chatbot_setup_wizard')
    convs  = bot.conversations.order_by('-last_message_at')

    total_convs   = convs.count()
    total_msgs    = Message.objects.filter(conversation__bot=bot).count()
    unique_customers = convs.values('customer_phone').distinct().count()
    today_convs   = convs.filter(started_at__date=date.today()).count()

    # Wanaosubiri binadamu wanatangulia — hao ndio wanaoweza kuondoka
    waiting = convs.filter(is_human_handoff=True).order_by('handoff_at')

    return render(request, 'chatbot/portal/conversations.html', {
        'client': client, 'bot': bot, 'conversations': convs,
        'total_convs': total_convs, 'total_msgs': total_msgs,
        'unique_customers': unique_customers, 'today_convs': today_convs,
        'waiting': waiting, 'waiting_count': waiting.count(),
    })


@login_required(login_url='chatbot_login')
def chatbot_conversation_detail(request, conv_id):
    client = _get_or_create_client(request.user)
    bot    = client.bots.first()
    if not bot:
        return redirect('chatbot_setup_wizard')
    conv   = get_object_or_404(Conversation, id=conv_id, bot=bot)
    return render(request, 'chatbot/portal/conversation_detail.html', {
        'client': client, 'bot': bot, 'conv': conv,
        'messages': conv.messages.order_by('created_at'),
    })


@login_required(login_url='chatbot_login')
def chatbot_billing(request):
    client   = _get_or_create_client(request.user)
    bot      = client.bots.first()

    if not bot:
        messages.warning(request, "Please complete your bot setup first.")
        return redirect('chatbot_setup_wizard')

    # Allow billing even if bot is pending/draft — client needs to pay
    sub      = getattr(bot, 'subscription', None)
    plans    = SubscriptionPlan.objects.filter(is_active=True)
    payments = sub.payments.order_by('-payment_date') if sub else []

    if request.method == 'POST':
        ref    = request.POST.get('transaction_ref', '').strip()
        amount = request.POST.get('amount', '0')
        months = request.POST.get('months', 1)
        method = request.POST.get('payment_method', 'NMB Bank')
        plan_id = request.POST.get('plan_id')

        if not ref:
            messages.error(request, "Tafadhali weka namba ya transaction.")
        elif sub:
            SubscriptionPayment.objects.create(
                subscription=sub, amount=amount, months_covered=months,
                payment_method=method, transaction_ref=ref
            )
            messages.success(request, "✅ Malipo yametumwa! Tutahakikisha ndani ya masaa 24.")
        else:
            messages.error(request, "Hakuna subscription. Wasiliana na usaidizi.")

    return render(request, 'chatbot/portal/billing.html', {
        'client': client, 'bot': bot, 'sub': sub,
        'plans': plans, 'payments': payments,
    })


# ════════════════════════════════════════════════════════
# WHATSAPP WEBHOOK — GLOBAL (routes by phone_number_id)
# ════════════════════════════════════════════════════════

@csrf_exempt
def whatsapp_webhook_global(request):
    """
    SINGLE global webhook for ALL bots.
    Meta sends all messages here — we route to the correct bot
    by matching phone_number_id in the payload.

    Setup in Meta: Webhook URL = https://jamiitek.com/chatbot/webhook/
    """

    # ── GET: Verification ──
    if request.method == 'GET':
        mode      = request.GET.get('hub.mode')
        token     = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        master_verify = getattr(settings, 'WHATSAPP_WEBHOOK_VERIFY_TOKEN', '')
        if mode == 'subscribe' and token == master_verify:
            logger.info("Global webhook verified")
            return HttpResponse(challenge, content_type='text/plain')
        return HttpResponse('Forbidden', status=403)

    # ── POST: Messages ──
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Bad Request', status=400)

        try:
            entries = data.get('entry', [])
            for entry in entries:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    phone_number_id = value.get('metadata', {}).get('phone_number_id', '')

                    if not phone_number_id:
                        continue

                    # Find which bot owns this phone number
                    try:
                        bot = BotConfig.objects.get(
                            whatsapp_phone_id=phone_number_id,
                            is_active=True,
                            status='active'
                        )
                    except BotConfig.DoesNotExist:
                        logger.warning(f"No active bot for phone_id: {phone_number_id}")
                        continue

                    # Process all messages in this change
                    for msg_raw in value.get('messages', []):
                        try:
                            msg_data = _parse_message(msg_raw, value)
                            if msg_data:
                                _process_message(bot, msg_data)
                        except Exception as e:
                            logger.exception(f"Error processing message for bot {bot.id}: {e}")

        except Exception as e:
            logger.exception(f"Webhook processing error: {e}")

        # Always return 200 to Meta (otherwise Meta will retry)
        return HttpResponse('OK', status=200)

    return HttpResponse('Method not allowed', status=405)


# Keep per-bot webhook for backwards compatibility
@csrf_exempt
def whatsapp_webhook(request, bot_id):
    """Legacy per-bot webhook — kept for existing bots."""
    try:
        bot = BotConfig.objects.get(id=bot_id, is_active=True, status='active')
    except BotConfig.DoesNotExist:
        return HttpResponse("Bot not found", status=404)

    if request.method == 'GET':
        mode      = request.GET.get('hub.mode')
        token     = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if mode == 'subscribe' and token == bot.webhook_verify_token:
            return HttpResponse(challenge, content_type='text/plain')
        return HttpResponse('Forbidden', status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponse('Bad Request', status=400)

        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                for msg_raw in value.get('messages', []):
                    msg_data = _parse_message(msg_raw, value)
                    if msg_data:
                        try:
                            _process_message(bot, msg_data)
                        except Exception as e:
                            logger.exception(f"Error: {e}")

        return HttpResponse('OK', status=200)

    return HttpResponse('Method not allowed', status=405)


def _parse_message(msg_raw: dict, value: dict) -> dict | None:
    """
    Parse raw WhatsApp webhook payload into a clean dict.

    Supported message types:
      text        — plain text
      image       — photo with optional caption
      document    — file attachment (PDF, DOCX, …)
      audio       — voice note or audio clip
      video       — video clip
      sticker     — WhatsApp sticker
      location    — GPS coordinates
      interactive — list_reply or button_reply (user tapped a button)
      unsupported — anything else (reaction, poll, etc.)
    """
    contacts     = value.get('contacts', [{}])
    contact_name = contacts[0].get('profile', {}).get('name', '') if contacts else ''
    msg_type     = msg_raw.get('type', 'text')

    base = {
        'from':         msg_raw.get('from', ''),
        'message_id':   msg_raw.get('id', ''),
        'timestamp':    msg_raw.get('timestamp', ''),
        'contact_name': contact_name,
        'msg_type':     msg_type,
        'text':         '',          # filled below per type
        'media_id':     None,        # set for image/audio/video/document
        'media_caption': '',
        'filename':     '',
        'mime_type':    '',
        'location':     None,        # set for location
    }

    if msg_type == 'text':
        base['text'] = msg_raw.get('text', {}).get('body', '')

    elif msg_type == 'image':
        img = msg_raw.get('image', {})
        base['media_id']      = img.get('id', '')
        base['mime_type']     = img.get('mime_type', 'image/jpeg')
        base['media_caption'] = img.get('caption', '')
        base['text']          = f"[Picha]{': ' + img['caption'] if img.get('caption') else ''}"

    elif msg_type == 'document':
        doc = msg_raw.get('document', {})
        base['media_id']      = doc.get('id', '')
        base['mime_type']     = doc.get('mime_type', 'application/octet-stream')
        base['filename']      = doc.get('filename', 'document')
        base['media_caption'] = doc.get('caption', '')
        base['text']          = f"[Faili: {base['filename']}]{': ' + doc['caption'] if doc.get('caption') else ''}"

    elif msg_type == 'audio':
        audio = msg_raw.get('audio', {})
        base['media_id']  = audio.get('id', '')
        base['mime_type'] = audio.get('mime_type', 'audio/ogg')
        base['text']      = "[Ujumbe wa sauti]"

    elif msg_type == 'video':
        vid = msg_raw.get('video', {})
        base['media_id']      = vid.get('id', '')
        base['mime_type']     = vid.get('mime_type', 'video/mp4')
        base['media_caption'] = vid.get('caption', '')
        base['text']          = f"[Video]{': ' + vid['caption'] if vid.get('caption') else ''}"

    elif msg_type == 'sticker':
        base['text'] = "[Sticker]"

    elif msg_type == 'location':
        loc = msg_raw.get('location', {})
        lat  = loc.get('latitude', '')
        lng  = loc.get('longitude', '')
        name = loc.get('name', '')
        addr = loc.get('address', '')
        label = name or addr or f"{lat},{lng}"
        base['location'] = {'latitude': lat, 'longitude': lng, 'name': name, 'address': addr}
        base['text']     = f"[Mahali: {label}]"

    elif msg_type == 'interactive':
        # User tapped a list item or quick-reply button
        inter = msg_raw.get('interactive', {})
        itype = inter.get('type', '')  # 'list_reply' or 'button_reply'
        if itype == 'list_reply':
            reply      = inter.get('list_reply', {})
            base['text'] = reply.get('title', reply.get('id', '[List reply]'))
            base['interactive_id']    = reply.get('id', '')
            base['interactive_title'] = reply.get('title', '')
        elif itype == 'button_reply':
            reply      = inter.get('button_reply', {})
            base['text'] = reply.get('title', reply.get('id', '[Button reply]'))
            base['interactive_id']    = reply.get('id', '')
            base['interactive_title'] = reply.get('title', '')
        else:
            base['text'] = '[Interactive message]'

    else:
        # reactions, polls, contacts, etc.
        base['text'] = f"[{msg_type.capitalize()} message]"

    return base


def _get_conv_state(conv) -> str:
    """
    Return the current conversation state from metadata.

    States:
      'greeting'      — just started, greeting sent, waiting for any reply
      'collect_name'  — waiting for customer to send their name
      'collect_phone' — waiting for customer to send their phone number
      'chat'          — normal AI-powered conversation
    """
    return conv.metadata.get('state', 'greeting')


def _set_conv_state(conv, state: str):
    """Persist conversation state."""
    conv.metadata['state'] = state
    conv.save(update_fields=['metadata'])


def _send_and_save(wa, conv, phone: str, text: str, role='assistant', jid=None):
    """
    Send a WhatsApp message and save it to Message table.

    `jid` ni ya mazungumzo haya. WhatsApp inatumia LID kwa wateja
    wengi, na LID haiwezi kujengwa upya kutoka tarakimu — inaishia
    `@lid`, si `@s.whatsapp.net`. Kwa hiyo tunapitisha jid halisi.
    """
    res = wa.send_text(phone, text, jid=jid or getattr(wa, 'jid', None))
    if not res.get('success'):
        logger.error('[%s] ujumbe haukufika kwa %s: %s',
                     conv.bot.session_name, phone, res.get('error'))
    Message.objects.create(conversation=conv, role=role, content=text)


def _process_message(bot: BotConfig, msg_data: dict, handler=None):
    """
    Core message processing pipeline with greeting flow state machine.

    `handler` ni ya hiari. Ikiachwa, tunatumia `BaileysHandler` (WhatsApp).
    Kituo kingine chochote — chat ya website, simulation — kinaweza
    kupitisha handler yake yenye interface ile ile (`send_text`,
    `mark_as_read`, `send_interactive_list`), na injini nzima inabaki
    ile ile. Hii ndiyo sababu chat ya website si mfumo mpya — ni
    mlango mwingine tu wa injini hii.

    Conversation states:
      greeting      → send greeting; if collect_name → move to collect_name
                      else if collect_phone → move to collect_phone
                      else → move to chat
      collect_name  → save name; if collect_phone → move to collect_phone
                      else → move to chat + send welcome
      collect_phone → save phone; move to chat + send welcome
      chat          → AI response
    """
    from_phone   = msg_data['from']
    text         = msg_data['text'].strip()
    contact      = msg_data.get('contact_name', '')   # WhatsApp profile name
    msg_id       = msg_data.get('message_id', '')
    msg_type     = msg_data.get('msg_type', 'text')
    media_id     = msg_data.get('media_id')
    media_caption = msg_data.get('media_caption', '')

    # For media messages: use caption as text if available,
    # otherwise use the auto-generated label e.g. "[Picha]"
    if msg_type != 'text' and not text:
        return   # empty message — nothing to process

    # If media has a caption, prefer caption as the conversational text
    if media_caption and msg_type in ('image', 'document', 'video'):
        text = media_caption

    # Skip duplicates
    if msg_id and Message.objects.filter(wa_message_id=msg_id).exists():
        return

    # Baileys: `jid` inahitajika kwa mark_as_read (Meta ilihitaji id tu)
    wa = handler or BaileysHandler(bot, jid=msg_data.get('jid'))

    # Get or create conversation
    conv, is_new = Conversation.objects.get_or_create(
        bot=bot,
        customer_phone=from_phone,
        defaults={
            'wa_contact_name': contact,
            'customer_name':   contact,
            'metadata':        {'state': 'greeting'},
        }
    )

    # Update timestamps and WA profile name
    conv.last_message_at = timezone.now()
    conv.message_count  += 1
    if contact and not conv.wa_contact_name:
        conv.wa_contact_name = contact
    conv.save(update_fields=['last_message_at', 'message_count', 'wa_contact_name'])

    if msg_id:
        wa.mark_as_read(msg_id)

    # JID ihifadhiwe. Kazi za ratiba (`check_handoffs`) zinatuma jumbe
    # nje ya mazungumzo haya, na LID haiwezi kujengwa upya kutoka
    # tarakimu — inaishia `@lid`, si `@s.whatsapp.net`.
    incoming_jid = msg_data.get('jid') or ''
    if incoming_jid and conv.metadata.get('jid') != incoming_jid:
        conv.metadata['jid'] = incoming_jid
        conv.save(update_fields=['metadata'])

    # Save incoming message
    Message.objects.create(
        conversation=conv, role='user', content=text, wa_message_id=msg_id
    )

    # ── AMRI ZA MMILIKI ────────────────────────────────────────────
    # Mmiliki anazungumza na bot kupitia WhatsApp ya biashara yake.
    # Hii inakaguliwa KABLA ya kila kitu kingine, lakini ujumbe usio
    # amri unapita kama kawaida — mmiliki anaweza kuwa mteja wa bot
    # yake mwenyewe anapoijaribu.
    # `is_owner` inalinganisha namba NA LID. WhatsApp inatumia LID kwa
    # wateja wengi, kwa hiyo kulinganisha namba peke yake kulishindwa
    # kabisa — amri `orodha` na `endelea` hazikufanya kazi.
    if bot.owner_digits and not bot.owner_lid and msg_data.get('is_lid'):
        # Jaribio moja la kutafsiri, mara ya kwanza tunapoona LID
        try:
            from . import bridge as _br
            _br.resolve_owner_lid(bot)
        except Exception:
            logger.warning('[%s] kutafsiri LID ya mmiliki kumeshindwa', bot.session_name)

    if bot.is_owner(from_phone):
        if handoff.handle_owner_command(bot, wa, from_phone, text):
            return

    # ── BOT IMESIMAMA ──────────────────────────────────────────────
    # Mteja ameambiwa "nakuunganisha na mtu halisi". Kuandika chochote
    # baada ya hapo kungefanya ahadi ile kuwa uongo.
    #
    # Ujumbe wake umeshahifadhiwa hapo juu, kwa hiyo mmiliki
    # ataiona kila kitu alichoandika akiwa anasubiri. Bot inanyamaza
    # tu — haisemi "bado unasubiri", haikumbushi, haifanyi kitu.
    if conv.is_human_handoff:
        # Mkumbushe mmiliki kama mteja anaendelea kuandika bila kujibiwa
        handoff.remind_owner_if_stale(bot, wa, conv, text)
        return

    # ── ANAHITAJI BINADAMU? ────────────────────────────────────────
    # Hii iko HAPA, kabla ya state machine, si ndani ya hali ya 'chat'.
    #
    # Ilikuwa chini kwenye 'chat' pekee, kwa hiyo mteja mpya
    # aliyeandika "nataka kuongea na mtu halisi" kama ujumbe wake wa
    # KWANZA alipata salamu tu — ombi lake likapotea kimyakimya. Na
    # huo ndio wakati unaowezekana zaidi kwa mtu kuomba binadamu.
    #
    # Pia inashika mtu anayeomba akiwa katikati ya kuulizwa jina.
    needs_human, why = handoff.detect(text)
    if needs_human:
        handoff.trigger(bot, wa, conv, from_phone, by='customer', reason=why)
        return

    # ── State: GREETING (brand new conversation) ───────────────────
    if is_new:
        # Replace {name} placeholder if we already know the WA profile name.
        # Bila jina, "Karibu {name}!" ilikuwa inatoa "Karibu !" — .strip()
        # inaondoa pembeni tu, si nafasi iliyo katikati. Tunaisafisha.
        display_name = contact or ''
        greeting     = bot.greeting_msg.replace('{name}', display_name)
        if not display_name:
            greeting = re.sub(r'\s+([!?.,])', r'\1', greeting)
            greeting = re.sub(r'\s{2,}', ' ', greeting)
        greeting = greeting.strip()
        _send_and_save(wa, conv, from_phone, greeting)

        if bot.collect_name and not conv.customer_name:
            # Ask for name
            ask_name_msg = "Karibu! Niambie jina lako ili nikusaidie vizuri zaidi. 😊"
            _send_and_save(wa, conv, from_phone, ask_name_msg)
            _set_conv_state(conv, 'collect_name')
        elif bot.collect_phone and not conv.metadata.get('phone_collected'):
            ask_phone_msg = "Tafadhali nipe namba yako ya simu ili tuweze kuwasiliana nawe. 📱"
            _send_and_save(wa, conv, from_phone, ask_phone_msg)
            _set_conv_state(conv, 'collect_phone')
        else:
            _set_conv_state(conv, 'chat')
        return

    # ── State: COLLECT_NAME ────────────────────────────────────────
    state = _get_conv_state(conv)

    if state == 'collect_name':
        # Accept anything as a name (1–60 chars)
        name = text.strip()[:60]
        conv.customer_name = name
        conv.save(update_fields=['customer_name'])

        if bot.collect_phone and not conv.metadata.get('phone_collected'):
            ack = f"Asante, {name}! 😊 Sasa nipe namba yako ya simu. 📱"
            _send_and_save(wa, conv, from_phone, ack)
            _set_conv_state(conv, 'collect_phone')
        else:
            welcome = f"Karibu sana, {name}! Ninaweza kukusaidiaje leo? 🙏"
            _send_and_save(wa, conv, from_phone, welcome)
            _set_conv_state(conv, 'chat')
        return

    # ── State: COLLECT_PHONE ───────────────────────────────────────
    if state == 'collect_phone':
        # Basic validation — accept digits, spaces, +, -, ()
        # (`re` sasa imeimportwa juu ya faili — import ya ndani hapa
        #  ilikuwa inafanya `re` kuwa local kwa function NZIMA)
        digits = re.sub(r'[^\d+\-\s()]', '', text).strip()
        if len(re.sub(r'\D', '', digits)) < 7:
            # Doesn't look like a phone number — ask again
            retry_msg = "Samahani, simu hiyo si sahihi. Tafadhali ingiza namba yako ya simu (mfano: +255712345678). 📱"
            _send_and_save(wa, conv, from_phone, retry_msg)
            return

        # Save phone in metadata (avoid overwriting the customer's WA from_phone)
        meta = conv.metadata
        meta['provided_phone']  = digits
        meta['phone_collected'] = True
        conv.metadata = meta
        conv.save(update_fields=['metadata'])

        name    = conv.customer_name or 'rafiki'
        welcome = f"Asante, {name}! Tumepokea namba yako. Ninaweza kukusaidiaje leo? 🙏"
        _send_and_save(wa, conv, from_phone, welcome)
        _set_conv_state(conv, 'chat')
        return

    # ── State: CHAT (normal AI flow) ──────────────────────────────

    # Check subscription
    sub = getattr(bot, 'subscription', None)
    if sub:
        # Kipindi kipya kikifika, hesabu inarudi sifuri. Bila hii,
        # plan ya kila mwezi ilikuwa inahesabu maisha yote.
        sub.roll_period_if_due()
    if sub and not sub.is_active:
        _send_and_save(wa, conv, from_phone,
                       "Samahani, huduma hii imesimamishwa. Wasiliana na kampuni moja kwa moja.")
        return

    # ── Media-aware pre-processing ─────────────────────────────────
    # For non-text messages without a caption, acknowledge receipt and
    # optionally ask the user to describe what they need.
    if msg_type == 'image' and not media_caption:
        ack = "Nimepokea picha yako. 📷 Tafadhali nieleze zaidi unachohitaji ili nikusaidie vizuri."
        _send_and_save(wa, conv, from_phone, ack)
        # Still pass "[Picha]" to AI context so it's aware
        ai_text = "[Mteja alituma picha bila maelezo]"
    elif msg_type == 'document' and not media_caption:
        fname = msg_data.get('filename', 'faili')
        ack   = f"Nimepokea faili: *{fname}* 📄 Je, ungependa nikusaidie nini kuhusu faili hili?"
        _send_and_save(wa, conv, from_phone, ack)
        ai_text = f"[Mteja alituma faili: {fname}]"
    elif msg_type == 'audio':
        # Tunafika hapa sauti ikishindwa kutafsiriwa tu — ndefu mno,
        # kubwa mno, au Whisper imeshindwa. Sauti ya kawaida
        # inabadilishwa kuwa maandishi kwenye `_baileys_to_msg_data`.
        ack = ("Nimepokea ujumbe wako wa sauti 🎙️ lakini sikuweza kuusikia vizuri. "
               "Tafadhali uandike kwa maandishi, au tuma sauti fupi zaidi.")
        _send_and_save(wa, conv, from_phone, ack)
        # Save and stop — no AI call for voice without transcription
        Message.objects.create(conversation=conv, role='assistant', content=ack)
        return
    elif msg_type == 'location':
        loc   = msg_data.get('location', {})
        label = loc.get('name') or loc.get('address') or f"{loc.get('latitude')},{loc.get('longitude')}"
        ai_text = f"Mteja alituma mahali: {label} (lat={loc.get('latitude')}, lng={loc.get('longitude')})"
        text  = ai_text   # override text for AI
    elif msg_type == 'sticker':
        _send_and_save(wa, conv, from_phone, "😊 Asante kwa sticker! Ninaweza kukusaidiaje?")
        return
    else:
        ai_text = text   # normal text or media with caption

    # Use ai_text if set by media handling above, else use original text
    final_text = locals().get('ai_text', text)

    # ── Services menu trigger ──────────────────────────────────────
    # Mteja akiomba orodha ya huduma, tunatuma orodha badala ya jibu
    # la AI.
    #
    # `bei`, `price`, `gharama` na `cost` ZILIONDOLEWA.
    #
    # Zilikuwa zinafanya KILA swali la bei kupata orodha ya huduma
    # badala ya jibu. "bei ya saruji?" — swali mahususi lenye jibu
    # mahususi — lilikuwa linarudisha menyu ya huduma zote. Mteja
    # anauliza kitu kimoja na anapewa kila kitu.
    #
    # AI tayari inajua bei zote (`build_system_prompt` inaziweka
    # pamoja na kila huduma), kwa hiyo inaweza kujibu moja kwa moja.
    #
    # Neno la bei peke yake — "bei?" bila kitu kingine — bado
    # linaleta orodha, kwa sababu hapo mteja hajataja huduma.
    menu_keywords = [
        'menu', 'huduma', 'services', 'orodha', 'chaguo', 'options',
        'nini mnafanya', 'mnafanya nini', 'what do you offer', 'what can you do',
    ]
    text_lower = final_text.lower()

    # "bei?" / "bei zenu?" — swali pana bila huduma mahususi
    bare_price = text_lower.strip(' ?.!').strip() in (
        'bei', 'bei?', 'bei zenu', 'bei gani', 'price', 'prices', 'gharama', 'cost',
    )

    if bare_price or any(kw in text_lower for kw in menu_keywords):
        menu = build_services_menu(bot)
        if menu:
            sent = wa.send_interactive_list(
                to=from_phone,
                header=menu['header'],
                body=menu['body'],
                button_text=menu['button_text'],
                sections=menu['sections'],
            )
            if sent.get('success'):
                Message.objects.create(
                    conversation=conv, role='assistant',
                    content=f"[Orodha ya huduma ilitumwa — {len(menu['sections'][0]['rows'])} huduma]"
                )
                if sub:
                    sub.messages_used += 1
                    sub.save(update_fields=['messages_used'])
                return
            # If interactive fails (e.g. bot not WhatsApp-connected), fall through to AI

    # ── Kikomo cha matumizi ────────────────────────────────────────
    # Groq ya bure inatoa tokens 6,000/dakika kwa AKAUNTI NZIMA.
    # Mteja mmoja akituma jumbe kumi mfululizo, bot ZOTE zinanyamaza.
    #
    # Hii iko HAPA, si mwanzoni: salamu, majina, na orodha ya huduma
    # hazitumii AI, kwa hiyo hazipaswi kuhesabiwa.
    allowed, why = ratelimit.check(bot, from_phone)
    if not allowed:
        # Onyo linatumwa MARA MOJA kwa dirisha. Mteja anayebonyeza
        # mara ishirini asipate onyo mara ishirini.
        if not ratelimit.already_warned(bot, from_phone, why):
            _send_and_save(wa, conv, from_phone,
                           ratelimit.message_for(why, bot),
                           jid=msg_data.get('jid'))
        return

    # AI response
    ai     = BotAIEngine(bot)
    result = ai.get_response(conv, final_text)
    reply  = result['content']

    Message.objects.create(
        conversation=conv, role='assistant', content=reply,
        tokens_used=result.get('tokens', 0),
        ai_model=result.get('model', ''),
        latency_ms=result.get('latency_ms', 0),
    )

    if sub and result.get('success'):
        sub.messages_used += 1
        sub.save(update_fields=['messages_used'])

    # Jibu la bridge LAZIMA likaguliwe. Zamani `wa.send_text(...)`
    # iliitwa bila kuangalia matokeo: bridge ikisema `success: false`,
    # Django iliendelea kana kwamba imetuma, na dashboard ilionyesha
    # bot imejibu wakati mteja hakupokea kitu.
    sent = wa.send_text(from_phone, reply, jid=msg_data.get('jid'))
    if not sent.get('success'):
        logger.error('[%s] jibu halikufika kwa %s: %s',
                     bot.session_name, from_phone, sent.get('error'))

    if result.get('is_handoff'):
        # Hii ilikuwa inaweka bendera pekee — mmiliki hakuarifiwa, na bot
        # iliendelea kujibu. Sasa inapita njia ile ile ya handoff.trigger.
        handoff.trigger(bot, wa, conv, from_phone, by='ai',
                        reason='Bot iliomba binadamu')

    elif handoff.promised_handoff(reply):
        # AI imeahidi kumuunganisha mteja kwa maneno yake, bila neno
        # lolote la TRIGGERS kulingana. Bila hii, bot inaahidi kisha
        # inaendelea kuongea — na mteja anasubiri mtu ambaye hajaitwa.
        #
        # Ujumbe wa ahadi tayari umetumwa, kwa hiyo hatutumi mwingine;
        # tunasimamisha bot na kumjulisha mmiliki.
        if conv.start_handoff(by='ai', reason='Bot iliahidi kuunganisha'):
            handoff.notify_owner(bot, wa, conv, 'Bot iliahidi kuunganisha na binadamu')
            logger.info('[%s] handoff kutoka ahadi ya bot: %s',
                        bot.session_name, from_phone)

    # ── Bot imeshindwa? Hifadhi swali ili mmiliki alijibu ──────────
    knowledge.watch(bot, conv, final_text, reply, result)

    # ── Kumbukumbu ya mteja (kila baada ya jumbe kadhaa) ───────────
    knowledge.maybe_update_memory(bot, conv)

    _update_analytics(bot, result)


def _update_analytics(bot, ai_result):
    try:
        analytics, _ = BotAnalytics.objects.get_or_create(bot=bot, date=date.today())
        analytics.messages_in  += 1
        analytics.messages_out += 1
        analytics.tokens_used  += ai_result.get('tokens', 0)
        if not ai_result.get('success'):
            analytics.errors += 1
        if ai_result.get('is_handoff'):
            analytics.handoffs += 1
        analytics.save()
    except Exception as e:
        logger.error(f"Analytics update failed: {e}")

# ════════════════════════════════════════════════════════
# SIMULATE / TEST ENDPOINT (staff only)
# ════════════════════════════════════════════════════════

@login_required
@csrf_exempt
def simulate_message(request, bot_id):
    """
    Simulate a WhatsApp message without actually going through Meta.
    Only accessible to staff (William) for testing and debugging.

    POST JSON: {"phone": "+255700000001", "message": "Habari", "contact_name": "Test User"}
    GET: renders the test UI
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    try:
        bot = BotConfig.objects.get(id=bot_id)
    except BotConfig.DoesNotExist:
        return JsonResponse({'error': 'Bot not found'}, status=404)

    if request.method == 'GET':
        # Render simple test UI
        conversations = bot.conversations.order_by('-last_message_at')[:10]
        return render(request, 'chatbot/admin/simulate.html', {
            'bot':           bot,
            'conversations': conversations,
        })

    # POST — simulate a message
    try:
        data         = json.loads(request.body)
        phone        = data.get('phone', '+255700000001').strip()
        text         = data.get('message', '').strip()
        contact_name = data.get('contact_name', 'Test User').strip()
        reset_conv   = data.get('reset', False)
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not text:
        return JsonResponse({'error': 'message is required'}, status=400)

    # Optionally reset conversation (start fresh)
    if reset_conv:
        bot.conversations.filter(customer_phone=phone).delete()

    # Build a fake msg_data and run through the pipeline
    # Tunanasa jumbe zinazotoka kwa kubadilisha BaileysHandler.send_text
    # kwa muda. Hakuna kinachotoka kwenda WhatsApp wakati wa simulation.
    sent_messages = []

    from .bridge import BaileysHandler as _BH

    original_send_text = _BH.send_text
    def fake_send_text(self, to, message):
        sent_messages.append(message)
        return {'success': True, 'message_id': 'sim_' + str(len(sent_messages))}
    _BH.send_text = fake_send_text

    original_mark_read = _BH.mark_as_read
    _BH.mark_as_read = lambda self, msg_id: {'success': True}

    # `send_interactive_list` inaita `send_text` ndani yake, kwa hiyo
    # orodha ya huduma nayo inanaswa bila kubadilisha kitu kingine.

    try:
        msg_data = {
            'from':         phone,
            'text':         text,
            'message_id':   f'sim_{timezone.now().timestamp()}',
            'contact_name': contact_name,
        }
        _process_message(bot, msg_data)

        # Get conversation state after processing
        conv = bot.conversations.filter(customer_phone=phone).first()
        state    = conv.metadata.get('state', 'unknown') if conv else 'unknown'
        cust_name = conv.customer_name if conv else ''
        cust_phone = conv.metadata.get('provided_phone', '') if conv else ''

    except Exception as e:
        logger.exception(f"Simulate error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        _BH.send_text     = original_send_text
        _BH.mark_as_read  = original_mark_read

    return JsonResponse({
        'success':       True,
        'bot_responses': sent_messages,
        'conv_state':    state,
        'customer_name': cust_name,
        'customer_phone_collected': cust_phone,
        'phone':         phone,
    })

# ════════════════════════════════════════════════════════
# LEGAL PAGES
# ════════════════════════════════════════════════════════

def privacy_policy(request):
    """Public privacy policy page — required by Meta App Review."""
    return render(request, 'chatbot/privacy_policy.html')

# ════════════════════════════════════════════════════════
# BAILEYS BRIDGE
# ════════════════════════════════════════════════════════
# Bridge inatuma ujumbe hapa; tunajibu 200 MARA MOJA kisha
# tunashughulikia nyuma.
#
# Sababu si kasi peke yake. `_process_message` inatuma jumbe MBILI
# mteja anapoanza (salamu, kisha "niambie jina lako"), na inaweza
# kuchukua sekunde 20 kusubiri AI. Kama bridge ingesubiri jibu
# kwenye HTTP response, mkulima wa tano angesubiri wanne wamalize
# — na tungeweza kurudisha ujumbe mmoja tu.

def _bridge_authorized(request):
    given = request.headers.get('X-Bridge-Key', '')
    expected = getattr(settings, 'BRIDGE_API_KEY', '')
    if not expected:
        logger.error('BRIDGE_API_KEY haijawekwa — webhook imezimwa')
        return False
    return secrets.compare_digest(str(given), str(expected))


def _baileys_to_msg_data(payload: dict) -> dict:
    """
    Bridge inatuma payload iliyokwisha chambuliwa. Hapa tunaibadilisha
    iwe na maumbo yale yale ambayo `_process_message` inategemea, ili
    state machine isibadilike hata kidogo.
    """
    msg_type = payload.get('msg_type', 'text')
    text = (payload.get('text') or '').strip()

    data = {
        'from':         payload.get('phone', ''),
        'text':         text,
        'message_id':   payload.get('message_id', ''),
        'contact_name': payload.get('contact_name', ''),
        'msg_type':     msg_type,
        'media_id':     None,
        'media_caption': text if msg_type in ('image', 'video', 'document') else '',
        'filename':     payload.get('filename', ''),
        'jid':          payload.get('jid', ''),
        'is_lid':       bool(payload.get('is_lid')),
    }

    if payload.get('location'):
        data['location'] = payload['location']

    # ── Sauti -> maandishi ────────────────────────────────────────
    # Bila hii, voice note ilikuwa inakuwa "[Sauti]" na AI ikijibu
    # kwamba haielewi. Wateja wa Tanzania wanatuma sauti nyingi
    # kuliko maandishi, kwa hiyo bot ilikuwa inashindwa kwa sehemu
    # kubwa ya mazungumzo.
    if msg_type == 'audio' and payload.get('audio_base64'):
        from . import transcribe as _tr
        spoken = _tr.transcribe(
            payload['audio_base64'],
            mime=payload.get('audio_mime', 'audio/ogg'),
            seconds=payload.get('audio_seconds', 0),
        )
        if spoken:
            data['text'] = spoken
            data['from_voice'] = True
            # MUHIMU: msg_type inakuwa 'text'.
            #
            # `_process_message` ina tawi la `msg_type == 'audio'`
            # linalokata mara moja na kutuma "siwezi kusikia sauti",
            # bila kuangalia kama maandishi yapo. Bila mstari huu,
            # kutafsiri kunafanyika kisha kunatupwa.
            data['msg_type'] = 'text'
            return data

    # Jumbe zisizo na maandishi zinahitaji lebo ili `_process_message`
    # isiziruke kama tupu (inakagua `if msg_type != 'text' and not text`)
    if not text and msg_type != 'text':
        data['text'] = {
            'image':    '[Picha]',
            'video':    '[Video]',
            'audio':    '[Ujumbe wa sauti — sikuweza kuusikia]',
            'document': '[Faili]',
            'sticker':  '[Sticker]',
            'location': '[Mahali]',
        }.get(msg_type, f'[{msg_type}]')

    return data


@csrf_exempt
def baileys_webhook(request):
    """Bridge -> Django. Inajibu mara moja, inashughulikia nyuma."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST pekee'}, status=405)

    if not _bridge_authorized(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON si sahihi'}, status=400)

    session = payload.get('session', '')
    if not session:
        return JsonResponse({'success': False, 'error': 'session inahitajika'}, status=400)

    bot = BotConfig.objects.filter(session_name=session).first()
    if not bot:
        logger.warning('Hakuna bot yenye session: %s', session)
        return JsonResponse({'success': False, 'error': 'Session haijulikani'}, status=404)

    # Hali ya bot inagusa mteja — ikiwa imezimwa, bridge haihitaji kujua
    if not bot.is_active or bot.status != 'active':
        return JsonResponse({'success': True, 'skipped': 'bot haijawashwa'})

    msg_data = _baileys_to_msg_data(payload)

    def _work():
        try:
            _process_message(bot, msg_data)
        except Exception:
            logger.exception('Baileys: kushughulikia ujumbe kumeshindwa (session %s)', session)
        finally:
            # Thread hii ina muunganisho wake wa database — lazima ufungwe
            try:
                from django.db import connection as _conn
                _conn.close()
            except Exception:
                pass

    threading.Thread(target=_work, name=f'baileys-{session}', daemon=True).start()

    return JsonResponse({'success': True})


@csrf_exempt
def bridge_session_list(request):
    """
    Bridge inauliza hii ikianza: 'ni sessions zipi ninazopaswa
    kuziinua?' Session zenyewe ziko Supabase, kwa hiyo hakuna
    kuscan QR upya — zinarudi zilipoishia.
    """
    if not _bridge_authorized(request):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)

    names = list(
        BotConfig.objects
        .filter(is_active=True, status='active', autostart=True)
        .exclude(session_name='')
        .values_list('session_name', flat=True)
    )
    return JsonResponse({'success': True, 'sessions': names})


# ════════════════════════════════════════════════════════
# PORTAL: MTEJA ANAJIUNGANISHA MWENYEWE
# ════════════════════════════════════════════════════════
# Bot inapatikana kupitia `client.bots` PEKEE — kamwe kwa id
# inayotoka kwenye URL. Mteja hawezi kufikia session ya mwenzake
# hata akijaribu.

def _own_bot(request):
    """Bot ya mtumiaji aliyeingia, au None."""
    client = _get_or_create_client(request.user)
    return client.bots.first()


@login_required(login_url='/chatbot/login/')
def chatbot_connect(request):
    """Ukurasa wa kuunganisha WhatsApp — QR au hali ya muunganisho."""
    bot = _own_bot(request)
    if not bot:
        return redirect('chatbot_setup_wizard')

    sub = getattr(bot, 'subscription', None)

    # Lango: QR inafunguka baada ya trial (au subscription) kuanza.
    if not sub or not sub.is_active:
        return render(request, 'chatbot/portal/connect.html', {
            'bot': bot, 'sub': sub, 'locked': True,
        })

    from apps.chatbot import bridge
    return render(request, 'chatbot/portal/connect.html', {
        'bot': bot,
        'sub': sub,
        'locked': False,
        'bridge_ok': bridge.is_configured(),
        'trial_days': sub.days_remaining if sub.status == 'trial' else None,
    })


@login_required(login_url='/chatbot/login/')
def chatbot_website(request):
    """
    Ukurasa unaomwonyesha mteja jinsi ya kuweka bot kwenye tovuti yake
    mwenyewe — link kamili (yenye BOT_ID yake), kitufe cha kunakili, na
    maelekezo hatua kwa hatua. Mteja anafanya haya bila msaada.
    """
    bot = _own_bot(request)
    if not bot:
        return redirect('chatbot_setup_wizard')

    sub = getattr(bot, 'subscription', None)
    origin = request.build_absolute_uri('/').rstrip('/')
    widget_src = f"{origin}/chatbot/widget/{bot.id}.js"
    snippet = f'<script src="{widget_src}" defer></script>'

    return render(request, 'chatbot/portal/website.html', {
        'bot':        bot,
        'sub':        sub,
        'active':     bool(sub and sub.is_active) and bot.is_active and bot.status == 'active',
        'origin':     origin,
        'widget_src': widget_src,
        'snippet':    snippet,
        'bot_page':   f"{origin}/bot/",
    })


@login_required(login_url='/chatbot/login/')
def chatbot_connect_qr(request):
    """
    JSON kwa ukurasa unaopiga kila sekunde 5. QR ya WhatsApp inaisha
    baada ya ~60s, kwa hiyo lazima ionekane mpya bila kurefresh.
    """
    bot = _own_bot(request)
    if not bot:
        return JsonResponse({'success': False, 'error': 'Hakuna bot'}, status=404)

    sub = getattr(bot, 'subscription', None)
    if not sub or not sub.is_active:
        return JsonResponse({'success': False, 'error': 'Mpango wako haujaanza'}, status=403)

    from apps.chatbot import bridge
    data = bridge.session_qr(bot.session_name)

    # Session bado haijaanzishwa kwenye bridge (bridge ilirestart, n.k.)
    if not data.get('success') and 'haipo' in str(data.get('error', '')):
        bridge.start_session(bot.session_name)
        data = bridge.session_qr(bot.session_name)

    _apply_session_status(bot, data)

    # Onyo la namba: aliyoiandika hatua ya 5 dhidi ya aliyoiscan
    connected = (data.get('number') or '').lstrip('0')
    declared  = re.sub(r'\D', '', bot.whatsapp_number or '').lstrip('0')
    if connected and declared and not (connected.endswith(declared) or declared.endswith(connected)):
        data['number_mismatch'] = bot.whatsapp_number

    return JsonResponse(data)


@login_required(login_url='/chatbot/login/')
def chatbot_connect_action(request):
    """restart | disconnect — kwa bot ya mtumiaji mwenyewe pekee."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST pekee'}, status=405)

    bot = _own_bot(request)
    if not bot:
        return JsonResponse({'success': False, 'error': 'Hakuna bot'}, status=404)

    sub = getattr(bot, 'subscription', None)
    if not sub or not sub.is_active:
        return JsonResponse({'success': False, 'error': 'Mpango wako haujaanza'}, status=403)

    from apps.chatbot import bridge
    action = request.POST.get('action', '')

    if action == 'restart':
        data = bridge.restart_session(bot.session_name)
    elif action == 'disconnect':
        # Kufuta session kunamlazimisha kuscan upya. Anaandika jina la
        # biashara yake kwanza — kama GitHub inavyodai jina la repo.
        typed = (request.POST.get('confirm') or '').strip().lower()
        if typed != (bot.business_name or '').strip().lower():
            return JsonResponse({
                'success': False,
                'error': 'Andika jina la biashara yako kwa usahihi.',
            }, status=400)
        data = bridge.logout_session(bot.session_name)
    else:
        return JsonResponse({'success': False, 'error': 'Kitendo hakijulikani'}, status=400)

    _apply_session_status(bot, data)
    return JsonResponse(data)


def _apply_session_status(bot, data):
    """Hifadhi hali kutoka bridge kwenye BotConfig."""
    if not data.get('success'):
        return
    fields = []
    status = data.get('status')
    if status and status != bot.connection_status:
        bot.connection_status = status
        fields.append('connection_status')
    number = data.get('number') or ''
    if number != bot.connected_number:
        bot.connected_number = number
        fields.append('connected_number')
    if status == 'connected':
        bot.last_seen_at = timezone.now()
        fields.append('last_seen_at')
    if fields:
        bot.save(update_fields=fields)


@login_required(login_url='/chatbot/login/')
def chatbot_resume(request, conv_id):
    """
    Kitufe cha 'Bot irudi' kwenye portal.

    Ni njia ile ile ya `endelea` ya WhatsApp — mmiliki mwingine
    anapendelea kubonyeza. Conversation inapatikana kupitia bot yake
    mwenyewe pekee.
    """
    if request.method != 'POST':
        return redirect('chatbot_conversations')

    bot = _own_bot(request)
    if not bot:
        return redirect('chatbot_setup_wizard')

    conv = get_object_or_404(Conversation, id=conv_id, bot=bot)
    if conv.resume_bot():
        who = conv.customer_name or conv.customer_phone
        messages.success(request, f"Bot imerudi kwa {who}.")
    else:
        messages.info(request, "Mazungumzo haya hayakuwa yamesimama.")
    return redirect('chatbot_conversations')


# ════════════════════════════════════════════════════════
# PORTAL: MAARIFA YA BOT
# ════════════════════════════════════════════════════════

@login_required(login_url='/chatbot/login/')
def chatbot_knowledge(request):
    """
    Maswali bot iliyoshindwa kuyajibu, na rasimu za majibu.

    Hapa ndipo mmiliki anapofundisha bot yake. Hakuna kitu
    kinachoingia kwenye maarifa ya bot bila yeye kubonyeza.
    """
    from .models import KnowledgeGap

    bot = _own_bot(request)
    if not bot:
        return redirect('chatbot_setup_wizard')

    gaps = bot.knowledge_gaps.exclude(status='dismissed')
    return render(request, 'chatbot/portal/knowledge.html', {
        'bot': bot,
        'open_gaps':   gaps.filter(status__in=['open', 'drafted']),
        'answered':    gaps.filter(status='answered')[:20],
        'open_count':  gaps.filter(status__in=['open', 'drafted']).count(),
        'answered_count': gaps.filter(status='answered').count(),
    })


@login_required(login_url='/chatbot/login/')
def chatbot_knowledge_action(request, gap_id):
    """draft | approve | dismiss"""
    from .models import KnowledgeGap
    from . import knowledge

    if request.method != 'POST':
        return redirect('chatbot_knowledge')

    bot = _own_bot(request)
    if not bot:
        return redirect('chatbot_setup_wizard')

    gap = get_object_or_404(KnowledgeGap, id=gap_id, bot=bot)
    action = request.POST.get('action', '')

    if action == 'draft':
        text = knowledge.draft_answer(bot, gap)
        if text:
            gap.suggested_answer = text
            gap.status = 'drafted'
            gap.save(update_fields=['suggested_answer', 'status'])
            return JsonResponse({'success': True, 'answer': text})
        return JsonResponse({'success': False, 'error': 'Haikuweza kuandika rasimu'}, status=502)

    if action == 'approve':
        answer = request.POST.get('answer', '').strip()
        if not answer:
            messages.error(request, "Jibu haliwezi kuwa tupu.")
            return redirect('chatbot_knowledge')
        knowledge.approve(gap, answer)
        messages.success(request, "Bot sasa inajua jibu hili.")
        return redirect('chatbot_knowledge')

    if action == 'dismiss':
        gap.status = 'dismissed'
        gap.save(update_fields=['status'])
        messages.info(request, "Swali limeondolewa kwenye orodha.")
        return redirect('chatbot_knowledge')

    return redirect('chatbot_knowledge')
