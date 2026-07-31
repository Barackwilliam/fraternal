"""Contract views — mteja anafikia kwa link, anachagua lugha, anasaini/anadownload."""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import Contract, Client
from .management_views import staff_member_required


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def contract_view(request, token):
    """
    Ukurasa wa umma wa mkataba (mteja anafikia kwa link).
    Mteja anachagua lugha (EN/SW) na kuchagua kusaini au kudownload.
    """
    contract = get_object_or_404(Contract, token=token)

    # Zuia kufikia drafts/cancelled
    if contract.status in ('draft', 'cancelled'):
        return render(request, 'contracts/contract_unavailable.html',
                      {'contract': contract}, status=404)

    # Weka alama 'viewed' mara ya kwanza
    if contract.status == 'sent':
        contract.status = 'viewed'
        contract.viewed_at = timezone.now()
        contract.save(update_fields=['status', 'viewed_at'])

    # Lugha: default EN, mteja anaweza kubadilisha ?lang=sw
    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'sw'):
        lang = 'en'
    # 'body' ni fallback ya jadi (kama HAKUNA sections). Usibadilishe lang
    # kwa sababu ya body tupu — sections zina lugha zao wenyewe.
    body = contract.body_sw if lang == 'sw' else contract.body_en
    if not body and not contract.sections:
        # Hakuna sections wala body ya lugha hii — jaribu nyingine (fallback ya jadi)
        body = contract.body_en or contract.body_sw

    return render(request, 'contracts/contract_view.html', {
        'contract': contract,
        'lang': lang,
        'body': body,
        'is_signed': contract.is_signed,
    })


@require_POST
@csrf_protect
def contract_sign(request, token):
    """Mteja anasaini mtandaoni: jina + makubaliano + (hiari) drawn signature."""
    contract = get_object_or_404(Contract, token=token)

    if contract.is_signed:
        return JsonResponse({'ok': False, 'error': 'This contract is already signed.'}, status=400)
    if contract.status in ('draft', 'cancelled', 'declined'):
        return JsonResponse({'ok': False, 'error': 'This contract cannot be signed.'}, status=400)

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    agreed = request.POST.get('agreed') in ('true', 'on', '1', 'yes')
    lang = request.POST.get('lang', 'en')
    sig_data = request.POST.get('signature_data', '')[:200000]  # base64 PNG (hiari)

    if len(name) < 3:
        return JsonResponse({'ok': False, 'error': 'Please type your full name.'}, status=400)
    if not agreed:
        return JsonResponse({'ok': False, 'error': 'You must agree to the terms to sign.'}, status=400)

    contract.signed_name = name[:160]
    contract.signed_email = email[:254]
    contract.agreed_to_terms = True
    contract.signed_at = timezone.now()
    contract.signed_ip = _client_ip(request)
    contract.signed_language = lang if lang in ('en', 'sw') else 'en'
    contract.signature_data = sig_data
    contract.status = 'signed'
    contract.save()

    return JsonResponse({'ok': True, 'redirect': f'/contract/{token}/?signed=1&lang={contract.signed_language}'})


@require_POST
@csrf_protect
def contract_decline(request, token):
    """Mteja anakataa mkataba."""
    contract = get_object_or_404(Contract, token=token)
    if contract.is_signed:
        return JsonResponse({'ok': False, 'error': 'Already signed.'}, status=400)
    reason = (request.POST.get('reason') or '').strip()[:300]
    contract.status = 'declined'
    contract.decline_reason = reason
    contract.save(update_fields=['status', 'decline_reason'])
    return JsonResponse({'ok': True})


def contract_pdf(request, token):
    """Download mkataba kama PDF (lugha kwa ?lang=)."""
    contract = get_object_or_404(Contract, token=token)
    if contract.status in ('draft', 'cancelled'):
        return HttpResponse('Not available', status=404)

    lang = request.GET.get('lang', 'en')
    if lang not in ('en', 'sw'):
        lang = 'en'
    body = contract.body_sw if lang == 'sw' else contract.body_en
    if not body:
        body = contract.body_en or contract.body_sw

    html = render(request, 'contracts/contract_pdf.html', {
        'contract': contract, 'lang': lang, 'body': body,
    }).content.decode('utf-8')

    # Tumia xhtml2pdf (pure Python, tayari kwenye requirements — bora kwa Render)
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
        if pisa_status.err:
            raise Exception('PDF generation error')
        buffer.seek(0)
        resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        fname = f"contract-{contract.display_client}-{lang}.pdf".replace(' ', '_')
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp
    except Exception:
        # Fallback: HTML yenye print dialog (mteja anaweza Ctrl+P → Save as PDF)
        return HttpResponse(html)


# ============================================================
# CONTRACT BUILDER — form maalum (staff only, nje ya admin)
# ============================================================

@staff_member_required
def contract_builder_list(request):
    """Orodha ya mikataba — dashboard ya staff."""
    contracts = Contract.objects.all().select_related('client')[:200]
    sent_count = sum(1 for c in contracts if c.status in ('sent', 'viewed'))
    signed_count = sum(1 for c in contracts if c.status == 'signed')
    total_value = sum(c.computed_total for c in contracts if c.status == 'signed')
    return render(request, 'contracts/builder_list.html', {
        'contracts': contracts,
        'sent_count': sent_count,
        'signed_count': signed_count,
        'total_value': total_value,
    })


@staff_member_required
def contract_builder_new(request):
    """Tengeneza mkataba mpya (fomu tupu) → peleka kwenye editor."""
    contract = Contract.objects.create(
        title='New Service Agreement',
        provider_rep=request.user.get_full_name() or request.user.username,
    )
    return redirect('contract_builder_edit', pk=contract.pk)


@staff_member_required
def contract_builder_edit(request, pk):
    """Editor kamili: client info, sections, line items, custom fields, AI kila mahali."""
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == 'POST':
        _save_builder_form(request, contract)
        return redirect('contract_builder_edit', pk=contract.pk)
    return render(request, 'contracts/builder_edit.html', {
        'contract': contract,
        'sections_json': json.dumps(contract.sections),
        'line_items_json': json.dumps(contract.line_items),
        'custom_fields_json': json.dumps(contract.custom_fields),
    })


def _save_builder_form(request, contract):
    """Hifadhi data zote kutoka builder form (POST)."""
    p = request.POST

    # Client (moja kwa moja, hakuna DB requirement)
    contract.client_name = p.get('client_name', '').strip()
    contract.client_email = p.get('client_email', '').strip()
    contract.client_company = p.get('client_company', '').strip()
    contract.client_phone = p.get('client_phone', '').strip()
    contract.client_address = p.get('client_address', '').strip()

    # Meta
    contract.title = p.get('title', contract.title).strip() or contract.title
    contract.project_name = p.get('project_name', '').strip()
    contract.provider_name = p.get('provider_name', 'JamiiTek').strip() or 'JamiiTek'
    contract.provider_rep = p.get('provider_rep', '').strip()
    contract.provider_signature = p.get('provider_signature', '').strip()
    contract.signature_block_en = p.get('signature_block_en', '')
    contract.signature_block_sw = p.get('signature_block_sw', '')
    psd = p.get('provider_signed_date', '').strip()
    if psd:
        try:
            from datetime import datetime
            contract.provider_signed_date = datetime.strptime(psd, '%Y-%m-%d').date()
        except ValueError:
            pass
    contract.accent_color = p.get('accent_color', '#25d366').strip() or '#25d366'
    contract.logo_url = p.get('logo_url', '').strip()

    # Terms summary
    amt = p.get('total_amount', '').strip()
    contract.total_amount = amt if amt else None
    contract.currency = p.get('currency', 'TZS').strip() or 'TZS'
    contract.payment_terms = p.get('payment_terms', '').strip()
    contract.timeline = p.get('timeline', '').strip()

    # Body (fallback ya jadi, hiari kama sections zinatumika)
    contract.body_en = p.get('body_en', '')
    contract.body_sw = p.get('body_sw', '')

    # Dynamic JSON (zinatumwa kama hidden input JSON strings)
    for field, default in (('sections', []), ('line_items', []), ('custom_fields', [])):
        raw = p.get(field, '')
        try:
            setattr(contract, field, json.loads(raw) if raw else default)
        except (json.JSONDecodeError, TypeError):
            pass  # acha thamani ya awali kama JSON imeharibika

    status = p.get('status')
    if status in dict(Contract.STATUS):
        if status == 'sent' and contract.status != 'sent' and not contract.sent_at:
            contract.sent_at = timezone.now()
        contract.status = status

    contract.save()


@staff_member_required
@require_POST
def contract_builder_ai_assist(request):
    """AI ndogo: pendekezo la maandishi kwa field moja (JSON endpoint)."""
    from apps import contract_ai
    field_type = request.POST.get('field_type', 'scope')
    context = request.POST.get('context', '')
    language = request.POST.get('language', 'en')

    ok, result = contract_ai.assist_field(field_type, context, language)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    return JsonResponse({'ok': True, 'text': result})


@staff_member_required
@require_POST
def contract_builder_ai_full(request, pk):
    """AI kubwa: andaa mkataba mzima (EN+SW) kutoka info ya sasa."""
    from apps import contract_ai
    contract = get_object_or_404(Contract, pk=pk)

    info = {
        'client_name': contract.display_client,
        'company': contract.display_company,
        'project_name': contract.project_name,
        'title': contract.title,
        'total_amount': contract.total_amount or contract.computed_total,
        'currency': contract.currency,
        'payment_terms': contract.payment_terms,
        'timeline': contract.timeline,
        'scope': contract.project_name or contract.title,
        'provider_rep': contract.provider_rep,
    }
    ok, result = contract_ai.generate_contract(info)
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)

    contract.title = result['title'] or contract.title
    contract.body_en = result['body_en']
    contract.body_sw = result['body_sw']
    contract.save(update_fields=['title', 'body_en', 'body_sw'])
    return JsonResponse({'ok': True, 'title': contract.title,
                          'body_en': contract.body_en, 'body_sw': contract.body_sw})
