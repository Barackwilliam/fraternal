"""Contract views — mteja anafikia kwa link, anachagua lugha, anasaini/anadownload."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import Contract


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
    body = contract.body_sw if lang == 'sw' else contract.body_en
    # Kama lugha moja haipo, tumia nyingine
    if not body:
        body = contract.body_en or contract.body_sw
        lang = 'en' if contract.body_en else 'sw'

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
        fname = f"contract-{contract.client.name}-{lang}.pdf".replace(' ', '_')
        resp['Content-Disposition'] = f'attachment; filename="{fname}"'
        return resp
    except Exception:
        # Fallback: HTML yenye print dialog (mteja anaweza Ctrl+P → Save as PDF)
        return HttpResponse(html)
