"""
JamiiTek ChatBot — Management Views (Staff Only)
William's panel to manage all bots, clients, payments, WhatsApp setup.
"""
import logging
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.conf import settings

from .models import (
    ChatbotClient, BotConfig, BotSubscription,
    SubscriptionPlan, SubscriptionPayment, Conversation, Message
)

logger = logging.getLogger('chatbot.manage')


def staff_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('/manage/login/')
        return view_func(request, *args, **kwargs)
    return wrapper


def manage_context(request):
    """Context processor — adds pending counts to all manage pages."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    try:
        pending_payments = SubscriptionPayment.objects.filter(status='pending').count()
        pending_bots = BotConfig.objects.filter(status='pending').count()
        return {
            'chatbot_pending_payments': pending_payments,
            'chatbot_pending_bots': pending_bots,
        }
    except Exception:
        return {}


# ════════════════════════════════════════════════════════
# OVERVIEW DASHBOARD
# ════════════════════════════════════════════════════════

@staff_required
def manage_chatbot_overview(request):
    """Main JamiiBot management dashboard."""
    from datetime import date, timedelta
    from django.db.models import Count

    all_bots    = BotConfig.objects.select_related('client').prefetch_related('conversations', 'subscription__plan').order_by('-created_at')
    all_clients = ChatbotClient.objects.count()
    active_bots    = all_bots.filter(status='active').count()
    pending_bots   = all_bots.filter(status='pending').count()
    suspended_bots = all_bots.filter(status='suspended').count()
    draft_bots     = all_bots.filter(status='draft').count()

    total_msgs  = Message.objects.count()
    total_convs = Conversation.objects.count()
    today_msgs  = Message.objects.filter(created_at__date=date.today()).count()

    total_revenue = SubscriptionPayment.objects.filter(
        status='verified'
    ).aggregate(t=Sum('amount'))['t'] or 0

    pending_payments = SubscriptionPayment.objects.filter(status='pending').count()

    recent_clients = ChatbotClient.objects.select_related('user').order_by('-created_at')[:8]

    bots_needing_setup = all_bots.filter(
        status='pending'
    ).select_related('client')

    # Chart data — last 30 days
    chart_data = []
    for i in range(29, -1, -1):
        day = date.today() - timedelta(days=i)
        count = Message.objects.filter(created_at__date=day).count()
        chart_data.append({'date': day.strftime('%d %b'), 'count': count})

    import json
    context = {
        'all_bots': all_bots,
        'all_clients': all_clients,
        'active_bots': active_bots,
        'pending_bots': pending_bots,
        'suspended_bots': suspended_bots,
        'draft_bots': draft_bots,
        'clients': all_clients,
        'total_msgs': total_msgs,
        'total_convs': total_convs,
        'today_msgs': today_msgs,
        'total_revenue': total_revenue,
        'pending_bot_payments': pending_payments,
        'recent_clients': recent_clients,
        'bots_needing_setup': bots_needing_setup,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'management/chatbot_overview.html', context)


# ════════════════════════════════════════════════════════
# BOT DETAIL & CONTROL
# ════════════════════════════════════════════════════════

@staff_required
def manage_bot_detail(request, bot_id):
    """Full control panel for a single bot."""
    bot  = get_object_or_404(BotConfig, id=bot_id)
    sub  = getattr(bot, 'subscription', None)
    convs = bot.conversations.order_by('-last_message_at')[:15]
    payments = sub.payments.order_by('-payment_date') if sub else []

    total_msgs  = Message.objects.filter(conversation__bot=bot).count()
    total_users = bot.conversations.values('customer_phone').distinct().count()
    today_msgs  = Message.objects.filter(
        conversation__bot=bot, created_at__date=date.today()
    ).count()

    context = {
        'bot': bot, 'sub': sub,
        'conversations': convs,
        'payments': payments,
        'total_msgs': total_msgs,
        'total_users': total_users,
        'today_msgs': today_msgs,
        'global_token_set': bool(getattr(settings, 'WHATSAPP_MASTER_TOKEN', '')),
        'services': bot.services.all(),
        'faqs': bot.faqs.all(),
    }
    return render(request, 'management/chatbot_bot_detail.html', context)


@staff_required
def manage_bot_action(request, bot_id):
    """Handle bot actions: suspend, activate, add phone ID, notes."""
    if request.method != 'POST':
        return redirect('manage_bot_detail', bot_id=bot_id)

    bot    = get_object_or_404(BotConfig, id=bot_id)
    action = request.POST.get('action')

    if action == 'suspend':
        bot.status    = 'suspended'
        bot.is_active = False
        bot.admin_suspended_reason = request.POST.get('reason', 'Admin action')
        bot.save()
        messages.success(request, f"Bot '{bot.bot_name}' imesimamishwa.")

    elif action == 'activate':
        # Only activate if phone_id is set
        if not bot.whatsapp_phone_id:
            messages.error(request, "Weka Phone Number ID kwanza kabla ya kuwasha bot.")
            return redirect('manage_bot_detail', bot_id=bot_id)
        bot.status    = 'active'
        bot.is_active = True
        bot.admin_suspended_reason = ''
        bot.save()
        messages.success(request, f"Bot '{bot.bot_name}' imewashwa! ✅")

    elif action == 'save_whatsapp':
        phone_number  = request.POST.get('whatsapp_number', '').strip()
        phone_id      = request.POST.get('whatsapp_phone_id', '').strip()
        token_override = request.POST.get('whatsapp_token', '').strip()

        bot.whatsapp_number   = phone_number
        bot.whatsapp_phone_id = phone_id
        if token_override:
            bot.whatsapp_token = token_override
        bot.save(update_fields=['whatsapp_number', 'whatsapp_phone_id', 'whatsapp_token'])

        if phone_id:
            # Auto-activate if was pending
            if bot.status == 'pending':
                bot.status    = 'active'
                bot.is_active = True
                bot.save()
            messages.success(request, f"✅ WhatsApp imeunganishwa! Bot '{bot.bot_name}' inafanya kazi.")
        else:
            messages.warning(request, "Phone Number ID haikuwekwa — bot bado haijawashwa.")

    elif action == 'admin_note':
        bot.admin_notes = request.POST.get('note', '')
        bot.save(update_fields=['admin_notes'])
        messages.success(request, "Admin notes saved.")

    elif action == 'reset_webhook':
        import secrets
        bot.webhook_verify_token = secrets.token_hex(16)
        bot.save(update_fields=['webhook_verify_token'])
        messages.success(request, "Webhook token has been reset.")

    elif action == 'save_config':
        bot.bot_name      = request.POST.get('bot_name', bot.bot_name).strip()
        bot.description   = request.POST.get('description', bot.description).strip()
        bot.language      = request.POST.get('language', bot.language)
        bot.tone          = request.POST.get('tone', bot.tone)
        bot.ai_temperature = float(request.POST.get('ai_temperature', bot.ai_temperature))
        bot.business_name = request.POST.get('business_name', bot.business_name).strip()
        bot.save(update_fields=['bot_name', 'description', 'language', 'tone', 'ai_temperature', 'business_name'])
        messages.success(request, f"✅ Bot configuration saved.")

    elif action == 'save_messages':
        bot.greeting_msg     = request.POST.get('greeting_msg', bot.greeting_msg).strip()
        bot.fallback_msg     = request.POST.get('fallback_msg', bot.fallback_msg).strip()
        bot.human_handoff_msg = request.POST.get('human_handoff_msg', bot.human_handoff_msg).strip()
        bot.collect_name     = 'collect_name' in request.POST
        bot.collect_phone    = 'collect_phone' in request.POST
        bot.save(update_fields=['greeting_msg', 'fallback_msg', 'human_handoff_msg', 'collect_name', 'collect_phone'])
        messages.success(request, "✅ Bot messages saved.")

    elif action == 'add_service':
        from .models import BotService
        name  = request.POST.get('service_name', '').strip()
        desc  = request.POST.get('service_desc', '').strip()
        price = request.POST.get('service_price', '').strip()
        if name and desc:
            BotService.objects.create(bot=bot, name=name, description=desc, price=price)
            messages.success(request, f"✅ Service '{name}' added.")
        else:
            messages.error(request, "Service name and description are required.")

    elif action == 'delete_service':
        from .models import BotService
        svc_id = request.POST.get('service_id')
        BotService.objects.filter(id=svc_id, bot=bot).delete()
        messages.success(request, "Service deleted.")

    elif action == 'add_faq':
        from .models import BotFAQ
        question = request.POST.get('faq_question', '').strip()
        answer   = request.POST.get('faq_answer', '').strip()
        if question and answer:
            BotFAQ.objects.create(bot=bot, question=question, answer=answer)
            messages.success(request, "✅ FAQ added.")
        else:
            messages.error(request, "Question and answer are required.")

    elif action == 'delete_faq':
        from .models import BotFAQ
        faq_id = request.POST.get('faq_id')
        BotFAQ.objects.filter(id=faq_id, bot=bot).delete()
        messages.success(request, "FAQ deleted.")

    elif action == 'extend_subscription':
        if sub:
            from datetime import timedelta
            days = int(request.POST.get('days', 30))
            from django.utils import timezone
            import datetime
            base = sub.end_date if sub.end_date and sub.end_date >= datetime.date.today() else datetime.date.today()
            sub.end_date = base + timedelta(days=days)
            sub.status   = 'active'
            sub.save()
            messages.success(request, f"✅ Subscription extended by {days} days.")

    return redirect('manage_bot_detail', bot_id=bot_id)


# ════════════════════════════════════════════════════════
# PAYMENTS
# ════════════════════════════════════════════════════════

@staff_required
def manage_bot_payments(request):
    """All pending & recent payments."""
    pending  = SubscriptionPayment.objects.filter(
        status='pending'
    ).select_related('subscription__bot__client').order_by('-payment_date')

    verified = SubscriptionPayment.objects.filter(
        status='verified'
    ).select_related('subscription__bot__client').order_by('-verified_at')[:30]

    rejected = SubscriptionPayment.objects.filter(
        status='rejected'
    ).select_related('subscription__bot__client').order_by('-payment_date')[:10]

    total_revenue = SubscriptionPayment.objects.filter(
        status='verified'
    ).aggregate(t=Sum('amount'))['t'] or 0

    pending_amount = pending.aggregate(t=Sum('amount'))['t'] or 0

    context = {
        'pending': pending,
        'verified': verified,
        'rejected': rejected,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
    }
    return render(request, 'management/chatbot_payments.html', context)


@staff_required
def manage_verify_payment(request, payment_id):
    """Verify a payment and extend subscription."""
    if request.method != 'POST':
        return redirect('manage_bot_payments')

    pay = get_object_or_404(SubscriptionPayment, id=payment_id)
    sub = pay.subscription
    months = int(request.POST.get('months', pay.months_covered or 1))

    pay.status      = 'verified'
    pay.verified_at = timezone.now()
    pay.verified_by = request.user
    pay.save()

    # Extend subscription
    base_date = sub.end_date if sub.end_date and sub.end_date >= date.today() else date.today()
    sub.end_date = base_date + timedelta(days=30 * months)
    sub.status   = 'active'
    sub.save()

    # Reactivate bot if it was suspended for billing
    bot = sub.bot
    if bot.status in ('suspended', 'pending'):
        if bot.whatsapp_phone_id:
            bot.status    = 'active'
            bot.is_active = True
            bot.save()

    messages.success(
        request,
        f"✅ Malipo yamethibitishwa! {bot.bot_name} — subscription hadi {sub.end_date}."
    )
    return redirect('manage_bot_payments')


@staff_required
def manage_reject_payment(request, payment_id):
    """Reject a payment."""
    if request.method != 'POST':
        return redirect('manage_bot_payments')

    pay = get_object_or_404(SubscriptionPayment, id=payment_id)
    pay.status = 'rejected'
    pay.save()
    messages.warning(request, f"Malipo #{payment_id} yamekataliwa.")
    return redirect('manage_bot_payments')


@staff_required
def manage_bulk_payment_action(request):
    """Bulk verify or reject selected payments."""
    if request.method != 'POST':
        return redirect('manage_bot_payments')

    action  = request.POST.get('bulk_action')
    pay_ids = request.POST.getlist('payment_ids')

    if not pay_ids:
        messages.warning(request, "Hakuna malipo yaliyochaguliwa.")
        return redirect('manage_bot_payments')

    pays = SubscriptionPayment.objects.filter(id__in=pay_ids, status='pending')

    if action == 'verify_all':
        for pay in pays:
            pay.status      = 'verified'
            pay.verified_at = timezone.now()
            pay.verified_by = request.user
            pay.save()
            sub = pay.subscription
            months = pay.months_covered or 1
            base = sub.end_date if sub.end_date and sub.end_date >= date.today() else date.today()
            sub.end_date = base + timedelta(days=30 * months)
            sub.status   = 'active'
            sub.save()
        messages.success(request, f"✅ Malipo {pays.count()} yamethibitishwa yote.")

    elif action == 'reject_all':
        pays.update(status='rejected')
        messages.warning(request, f"Malipo {len(pay_ids)} yamekataliwa.")

    return redirect('manage_bot_payments')


# ════════════════════════════════════════════════════════
# CLIENTS
# ════════════════════════════════════════════════════════

@staff_required
def manage_bot_clients(request):
    """All registered JamiiBot clients."""
    from datetime import date
    search = request.GET.get('q', '').strip()
    filter_status = request.GET.get('status', '').strip()

    clients = ChatbotClient.objects.select_related('user').prefetch_related(
        'bots', 'bots__subscription__plan'
    ).order_by('-created_at')

    if search:
        clients = clients.filter(
            Q(full_name__icontains=search) |
            Q(business_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    today = date.today()
    total_clients   = ChatbotClient.objects.count()
    active_bots     = ChatbotClient.objects.filter(bots__status='active').distinct().count()
    this_month      = ChatbotClient.objects.filter(
        created_at__month=today.month, created_at__year=today.year
    ).count()
    no_bot          = ChatbotClient.objects.filter(bots__isnull=True).count()

    context = {
        'clients':       clients,
        'search':        search,
        'total_clients': total_clients,
        'active_bots':   active_bots,
        'this_month':    this_month,
        'no_bot':        no_bot,
    }
    return render(request, 'management/chatbot_clients.html', context)


# ════════════════════════════════════════════════════════
# WHATSAPP SETUP PER BOT
# ════════════════════════════════════════════════════════

@staff_required
def manage_bot_whatsapp(request, bot_id):
    """William sets Phone Number ID for a specific bot."""
    bot      = get_object_or_404(BotConfig, id=bot_id)
    all_bots = BotConfig.objects.select_related('client').order_by('bot_name')
    global_token_set = bool(getattr(settings, 'WHATSAPP_MASTER_TOKEN', ''))

    if request.method == 'POST' and request.POST.get('action') == 'save_whatsapp':
        phone_number  = request.POST.get('whatsapp_number', '').strip()
        phone_id      = request.POST.get('whatsapp_phone_id', '').strip()
        token_override = request.POST.get('whatsapp_token', '').strip()

        bot.whatsapp_number   = phone_number
        bot.whatsapp_phone_id = phone_id
        if token_override:
            bot.whatsapp_token = token_override
        bot.save(update_fields=['whatsapp_number', 'whatsapp_phone_id', 'whatsapp_token'])

        if phone_id and bot.status == 'pending':
            bot.status    = 'active'
            bot.is_active = True
            bot.save()
            messages.success(request, f"✅ {bot.bot_name} imeunganishwa na imewashwa!")
        elif phone_id:
            messages.success(request, f"✅ {bot.bot_name} imeunganishwa na WhatsApp.")
        else:
            messages.warning(request, "Phone Number ID haikuwekwa.")

        return redirect('manage_bot_whatsapp', bot_id=bot_id)

    return render(request, 'management/chatbot_whatsapp.html', {
        'bot': bot,
        'all_bots': all_bots,
        'global_token_set': global_token_set,
    })


# ════════════════════════════════════════════════════════
# PUBLIC LANDING PAGE
# ════════════════════════════════════════════════════════

def jamiibot_landing(request):
    """Public marketing page for JamiiBot."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price_tzs')
    return render(request, 'chatbot_landing/jamiibot_landing.html', {'plans': plans})