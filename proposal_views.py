"""Proposal views — builder (staff), public link (client), accept/decline, PDF, AI."""
import json
import re
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import Proposal
from .management_views import staff_member_required


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ── PUBLIC (client-facing) ──

def proposal_view(request, token):
    proposal = get_object_or_404(Proposal, token=token)
    if proposal.status in ('draft',):
        return render(request, 'proposals/proposal_unavailable.html',
                      {'proposal': proposal}, status=404)

    if proposal.status == 'sent':
        proposal.status = 'viewed'
        proposal.viewed_at = timezone.now()
        proposal.save(update_fields=['status', 'viewed_at'])

    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'sw'):
        lang = 'en'

    return render(request, 'proposals/proposal_view.html', {
        'proposal': proposal, 'lang': lang,
        'is_accepted': proposal.is_accepted,
    })


@require_POST
@csrf_protect
def proposal_accept(request, token):
    proposal = get_object_or_404(Proposal, token=token)
    if proposal.is_accepted:
        return JsonResponse({'ok': False, 'error': 'Already accepted.'}, status=400)
    if proposal.status in ('draft', 'declined', 'expired'):
        return JsonResponse({'ok': False, 'error': 'This proposal cannot be accepted.'}, status=400)

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    if len(name) < 3:
        return JsonResponse({'ok': False, 'error': 'Please type your full name.'}, status=400)

    proposal.accepted_name = name[:160]
    proposal.accepted_email = email[:254]
    proposal.accepted_at = timezone.now()
    proposal.accepted_ip = _client_ip(request)
    proposal.status = 'accepted'
    proposal.save()
    lang = request.POST.get('lang', 'en')
    return JsonResponse({'ok': True, 'redirect': f'/proposal/{token}/?accepted=1&lang={lang}'})


@require_POST
@csrf_protect
def proposal_decline(request, token):
    proposal = get_object_or_404(Proposal, token=token)
    if proposal.is_accepted:
        return JsonResponse({'ok': False, 'error': 'Already accepted.'}, status=400)
    proposal.status = 'declined'
    proposal.decline_reason = (request.POST.get('reason') or '').strip()[:300]
    proposal.save(update_fields=['status', 'decline_reason'])
    return JsonResponse({'ok': True})


def proposal_pdf(request, token):
    proposal = get_object_or_404(Proposal, token=token)
    if proposal.status == 'draft':
        return HttpResponse('Not available', status=404)
    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'sw'):
        lang = 'en'

    html = render(request, 'proposals/proposal_pdf.html', {
        'proposal': proposal, 'lang': lang,
    }).content.decode('utf-8')

    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        buffer = BytesIO()
        status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
        if status.err:
            raise Exception('PDF error')
        buffer.seek(0)
        resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        fname = f"proposal-{proposal.display_client}-{lang}.pdf".replace(' ', '_')
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp
    except Exception:
        return HttpResponse(html)


# ── BUILDER (staff) ──

@staff_member_required
def proposal_builder_list(request):
    proposals = Proposal.objects.all().select_related('client')[:200]
    sent_count = sum(1 for p in proposals if p.status in ('sent', 'viewed'))
    accepted_count = sum(1 for p in proposals if p.status == 'accepted')
    total_value = sum(p.grand_total for p in proposals if p.status == 'accepted')
    return render(request, 'proposals/builder_list.html', {
        'proposals': proposals,
        'sent_count': sent_count,
        'accepted_count': accepted_count,
        'total_value': total_value,
    })


@staff_member_required
def proposal_builder_new(request):
    proposal = Proposal.objects.create(
        title='New Project Proposal',
        provider_rep=request.user.get_full_name() or request.user.username or 'W. Chipindi',
    )
    return redirect('proposal_builder_edit', pk=proposal.pk)


@staff_member_required
def proposal_builder_edit(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    if request.method == 'POST':
        _save_proposal_form(request, proposal)
        return redirect('proposal_builder_edit', pk=proposal.pk)
    return render(request, 'proposals/builder_edit.html', {
        'proposal': proposal,
        'sections_json': json.dumps(proposal.sections),
        'line_items_json': json.dumps(proposal.line_items),
        'timeline_json': json.dumps(proposal.timeline_items),
    })


def _save_proposal_form(request, p):
    d = request.POST
    p.client_name = d.get('client_name', '').strip()
    p.client_email = d.get('client_email', '').strip()
    p.client_company = d.get('client_company', '').strip()
    p.client_phone = d.get('client_phone', '').strip()

    p.title = d.get('title', p.title).strip() or p.title
    p.project_name = d.get('project_name', '').strip()
    p.currency = d.get('currency', 'TZS').strip() or 'TZS'
    p.payment_terms = d.get('payment_terms', '').strip()
    p.pricing_note = d.get('pricing_note', '').strip()
    p.provider_name = d.get('provider_name', 'JamiiTek').strip() or 'JamiiTek'
    p.provider_rep = d.get('provider_rep', '').strip()
    p.accent_color = d.get('accent_color', '#00d4ff').strip() or '#00d4ff'
    p.logo_url = d.get('logo_url', '').strip()

    p.summary_en = d.get('summary_en', '')
    p.summary_sw = d.get('summary_sw', '')
    p.scope_en = d.get('scope_en', '')
    p.scope_sw = d.get('scope_sw', '')
    p.about_en = d.get('about_en', '')
    p.about_sw = d.get('about_sw', '')

    disc = d.get('discount_amount', '').strip()
    p.discount_amount = disc if disc else None

    vu = d.get('valid_until', '').strip()
    if vu:
        try:
            p.valid_until = datetime.strptime(vu, '%Y-%m-%d').date()
        except ValueError:
            pass

    for field, default in (('sections', []), ('line_items', []), ('timeline_items', [])):
        raw = d.get(field, '')
        try:
            setattr(p, field, json.loads(raw) if raw else default)
        except (json.JSONDecodeError, TypeError):
            pass

    status = d.get('status')
    if status in dict(Proposal.STATUS):
        if status == 'sent' and not p.sent_at:
            p.sent_at = timezone.now()
        p.status = status

    p.save()


@staff_member_required
@require_POST
def proposal_ai_assist(request):
    from apps import proposal_ai
    field_type = request.POST.get('field_type', 'summary')
    context = request.POST.get('context', '')
    language = request.POST.get('language', 'en')
    ok, result = proposal_ai.assist_field(field_type, context, language)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    return JsonResponse({'ok': True, 'text': result})


@staff_member_required
@require_POST
def proposal_ai_full(request, pk):
    from apps import proposal_ai
    proposal = get_object_or_404(Proposal, pk=pk)
    info = {
        'client_name': proposal.display_client,
        'company': proposal.display_company,
        'project_name': proposal.project_name,
        'title': proposal.title,
        'currency': proposal.currency,
    }
    ok, result = proposal_ai.generate_proposal(info)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    for k, v in result.items():
        setattr(proposal, k, v)
    proposal.save()
    return JsonResponse({'ok': True, **result})


# ── CONVERT LEAD → PREMIUM PROPOSAL ──

# Maneno yanayoashiria bei kwenye requirements za lead
_PRICE_HINTS = ('cost', 'price', 'bei', 'budget', 'bajeti')
# Fields zisizo za mradi (za mteja au za ndani)
_SKIP_KEYS = ('client_name', 'client_email', 'client_phone', 'client_company',
              'reference_template')


def _humanize_key(key):
    """budget_range -> Budget Range"""
    return key.replace('_', ' ').strip().title()


@staff_member_required
def proposal_from_lead(request, lead_id):
    """
    Chukua lead ya zamani (ProjectProposal kutoka form ya mteja) na tengeneza
    Proposal mpya ya premium yenye taarifa zote zilizojazwa tayari.
    """
    from .models import ProjectProposal
    lead = get_object_or_404(ProjectProposal, pk=lead_id)

    req = lead.requirements
    if isinstance(req, str):
        try:
            req = json.loads(req)
        except (json.JSONDecodeError, TypeError):
            req = {}
    if not isinstance(req, dict):
        req = {}

    wtype = getattr(lead.website_type, 'name', '') or 'Website'

    proposal = Proposal(
        client=lead.client,
        client_name=req.get('client_name') or getattr(lead.client, 'name', '') or '',
        client_email=req.get('client_email') or getattr(lead.client, 'email', '') or '',
        client_phone=req.get('client_phone') or getattr(lead.client, 'phone', '') or '',
        client_company=req.get('client_company') or getattr(lead.client, 'company', '') or '',
        title=f'{wtype} Proposal',
        project_name=wtype,
        provider_rep=request.user.get_full_name() or request.user.username or 'W. Chipindi',
    )

    # Requirements zenye bei -> line items; nyingine -> section ya "Requirements"
    line_items = []
    other_lines = []
    for key, value in req.items():
        if key in _SKIP_KEYS or value in (None, '', [], {}):
            continue
        label = _humanize_key(key)
        if any(h in key.lower() for h in _PRICE_HINTS):
            try:
                amount = float(value)
            except (ValueError, TypeError):
                other_lines.append(f'{label}: {value}')
                continue
            line_items.append({'desc': label, 'qty': 1,
                               'unit_price': amount, 'amount': amount})
        else:
            if isinstance(value, (list, tuple)):
                value = ', '.join(str(v) for v in value)
            other_lines.append(f'{label}: {value}')

    # Reference template aliyochagua mteja
    ref = req.get('reference_template')
    if isinstance(ref, dict) and ref.get('name'):
        other_lines.append(f"Reference design: {ref['name']}")

    proposal.line_items = line_items
    if other_lines:
        body = '\n'.join(other_lines)
        proposal.sections = [{
            'heading_en': 'Your Requirements',
            'heading_sw': 'Mahitaji Yako',
            'body_en': body,
            'body_sw': '',
        }]
    proposal.save()
    return redirect('proposal_builder_edit', pk=proposal.pk)


def _wa_link(phone):
    """
    Tengeneza wa.me link kutoka namba ya Tanzania.
    0750910158 -> 255750910158 ; +255750... -> 255750... ; 255... -> 255...
    Rudisha '' kama namba haifai.
    """
    if not phone:
        return ''
    digits = re.sub(r'\D', '', str(phone))
    if not digits:
        return ''
    if digits.startswith('255'):
        pass
    elif digits.startswith('0'):
        digits = '255' + digits[1:]
    elif len(digits) == 9:          # 750910158
        digits = '255' + digits
    if len(digits) < 11:            # si namba kamili — usitengeneze link
        return ''
    return f'https://wa.me/{digits}'


# ── LEADS (wateja waliojaza form ya "Start Your Project") ──

@staff_member_required
def lead_list(request):
    """
    Orodha ya leads — wateja waliojaza form ya umma (/proposals/).
    Kila lead ina button ya kubadilisha kuwa Premium Proposal.
    """
    from .models import ProjectProposal
    leads = (ProjectProposal.objects
             .select_related('client', 'website_type')
             .order_by('-created_at')[:200])

    # Ni lead zipi tayari zimebadilishwa kuwa proposal?
    converted_emails = set(
        Proposal.objects.exclude(client_email='')
        .values_list('client_email', flat=True)
    )

    rows = []
    for lead in leads:
        req = lead.requirements
        if isinstance(req, str):
            try:
                req = json.loads(req)
            except (json.JSONDecodeError, TypeError):
                req = {}
        if not isinstance(req, dict):
            req = {}

        email = (req.get('client_email') or
                 getattr(lead.client, 'email', '') or '')

        details = []
        for key, value in req.items():
            if key in _SKIP_KEYS or value in (None, '', [], {}):
                continue
            if isinstance(value, (list, tuple)):
                value = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value = value.get('name') or str(value)
            details.append({'label': _humanize_key(key), 'value': value})

        # Reference design aliyochagua mteja (iko kwenye _SKIP_KEYS, lakini ni muhimu hapa)
        ref = req.get('reference_template')
        if isinstance(ref, dict) and ref.get('name'):
            details.append({'label': 'Reference Design', 'value': ref['name']})
        elif isinstance(ref, str) and ref.strip():
            details.append({'label': 'Reference Design', 'value': ref})

        phone = (req.get('client_phone') or
                 getattr(lead.client, 'phone', '') or '')

        rows.append({
            'lead': lead,
            'name': req.get('client_name') or getattr(lead.client, 'name', '') or '—',
            'email': email,
            'phone': phone,
            'wa': _wa_link(phone),
            'company': req.get('client_company') or getattr(lead.client, 'company', '') or '',
            'website_type': getattr(lead.website_type, 'name', '—'),
            'details': details,
            'converted': bool(email) and email in converted_emails,
        })

    return render(request, 'proposals/lead_list.html', {
        'rows': rows,
        'total': len(rows),
        'converted_count': sum(1 for r in rows if r['converted']),
        'new_count': sum(1 for r in rows if not r['converted']),
    })
