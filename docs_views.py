"""Company Profile + Invoice: public views, PDF, staff builders, AI endpoints."""
import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import CompanyProfile, Invoice
from .management_views import staff_member_required


def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _lang(request):
    lang = request.GET.get('lang', 'en')
    return lang if lang in ('en', 'sw') else 'en'


def _render_pdf(request, template, ctx, filename):
    html = render(request, template, ctx).content.decode('utf-8')
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        buf = BytesIO()
        status = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
        if status.err:
            raise Exception('PDF error')
        buf.seek(0)
        resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp
    except Exception:
        return HttpResponse(html)


# ============================================================
# COMPANY PROFILE
# ============================================================

def company_profile_view(request):
    """Ukurasa wa umma wa company profile."""
    profile = CompanyProfile.objects.filter(is_active=True).first()
    if profile is None:
        raise Http404('No active company profile')
    return render(request, 'docs/profile_view.html',
                  {'profile': profile, 'lang': _lang(request)})


def company_profile_pdf(request):
    profile = CompanyProfile.objects.filter(is_active=True).first()
    if profile is None:
        raise Http404('No active company profile')
    lang = _lang(request)
    fname = f'{profile.short_name}-company-profile-{lang}.pdf'.replace(' ', '_')
    return _render_pdf(request, 'docs/profile_pdf.html',
                       {'profile': profile, 'lang': lang}, fname)


@staff_member_required
def profile_builder(request):
    """Editor ya company profile (staff)."""
    profile = CompanyProfile.objects.filter(is_active=True).first()
    if profile is None:
        profile = CompanyProfile.objects.create()
    if request.method == 'POST':
        _save_profile_form(request, profile)
        return redirect('profile_builder')
    return render(request, 'docs/profile_edit.html', {
        'profile': profile,
        'services_json': json.dumps(profile.services),
        'why_json': json.dumps(profile.why_us),
        'projects_json': json.dumps(profile.projects),
        'facts_json': json.dumps(profile.facts),
        'sections_json': json.dumps(profile.sections),
    })


def _save_profile_form(request, p):
    d = request.POST
    for f in ('company_name', 'short_name', 'tagline_en', 'tagline_sw',
              'subtitle_en', 'subtitle_sw', 'period', 'about_en', 'about_sw',
              'mission_en', 'mission_sw', 'vision_en', 'vision_sw',
              'pricing_note_en', 'pricing_note_sw', 'email', 'phone',
              'website', 'address', 'logo_url'):
        if f in d:
            setattr(p, f, d.get(f, '').strip())
    for field, default in (('services', []), ('why_us', []), ('projects', []),
                           ('facts', []), ('sections', [])):
        raw = d.get(field, '')
        try:
            setattr(p, field, json.loads(raw) if raw else default)
        except (json.JSONDecodeError, TypeError):
            pass
    p.is_active = True
    p.save()


@staff_member_required
@require_POST
def profile_ai_assist(request):
    from apps import docs_ai
    ok, result = docs_ai.assist_field(
        request.POST.get('field_type', 'about'),
        request.POST.get('context', ''),
        request.POST.get('language', 'en'),
        kind='profile')
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    return JsonResponse({'ok': True, 'text': result})


@staff_member_required
@require_POST
def profile_ai_full(request):
    from apps import docs_ai
    profile = CompanyProfile.objects.filter(is_active=True).first()
    if profile is None:
        return JsonResponse({'ok': False, 'error': 'No profile'}, status=404)
    ok, result = docs_ai.generate_profile({
        'company_name': profile.company_name,
        'tagline': profile.tagline_en,
        'address': profile.address,
    })
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    for k, v in result.items():
        setattr(profile, k, v)
    profile.save()
    return JsonResponse({'ok': True, **result})


# ============================================================
# INVOICES
# ============================================================

def invoice_view(request, token):
    invoice = get_object_or_404(Invoice, token=token)
    if invoice.status in ('draft', 'cancelled'):
        return render(request, 'docs/invoice_unavailable.html',
                      {'invoice': invoice}, status=404)
    if invoice.status == 'sent':
        invoice.status = 'viewed'
        invoice.viewed_at = timezone.now()
        invoice.save(update_fields=['status', 'viewed_at'])
    return render(request, 'docs/invoice_view.html', {
        'invoice': invoice, 'lang': _lang(request),
    })


def invoice_pdf(request, token):
    invoice = get_object_or_404(Invoice, token=token)
    if invoice.status == 'draft':
        return HttpResponse('Not available', status=404)
    lang = _lang(request)
    fname = f'{invoice.invoice_number or "invoice"}-{lang}.pdf'.replace(' ', '_')
    return _render_pdf(request, 'docs/invoice_pdf.html',
                       {'invoice': invoice, 'lang': lang}, fname)


@staff_member_required
def invoice_list(request):
    invoices = Invoice.objects.all().select_related('client')[:200]
    unpaid = sum(1 for i in invoices if not i.is_paid and i.status not in ('draft', 'cancelled'))
    paid_count = sum(1 for i in invoices if i.is_paid)
    outstanding = sum(i.balance_due for i in invoices
                      if not i.is_paid and i.status not in ('draft', 'cancelled'))
    collected = sum(float(i.amount_paid or 0) for i in invoices)
    return render(request, 'docs/invoice_list.html', {
        'invoices': invoices, 'unpaid': unpaid, 'paid_count': paid_count,
        'outstanding': outstanding, 'collected': collected,
    })


@staff_member_required
def invoice_new(request):
    inv = Invoice.objects.create(
        title='Invoice',
        issue_date=timezone.now().date(),
        provider_rep=request.user.get_full_name() or request.user.username or 'W. Chipindi',
        payment_methods=[
            {'method': 'M-Pesa', 'details': ''},
            {'method': 'Bank Transfer', 'details': ''},
        ],
    )
    return redirect('invoice_edit', pk=inv.pk)


@staff_member_required
def invoice_edit(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        _save_invoice_form(request, inv)
        return redirect('invoice_edit', pk=inv.pk)
    return render(request, 'docs/invoice_edit.html', {
        'invoice': inv,
        'items_json': json.dumps(inv.line_items),
        'methods_json': json.dumps(inv.payment_methods),
    })


def _save_invoice_form(request, inv):
    d = request.POST
    for f in ('client_name', 'client_email', 'client_company', 'client_phone',
              'client_address', 'title', 'project_name', 'payment_terms',
              'notes_en', 'notes_sw', 'provider_name', 'provider_rep',
              'logo_url', 'paid_reference', 'invoice_number'):
        if f in d:
            setattr(inv, f, d.get(f, '').strip())

    inv.currency = d.get('currency', 'TZS').strip() or 'TZS'
    itype = d.get('invoice_type')
    if itype in dict(Invoice.TYPES):
        inv.invoice_type = itype

    for f in ('tax_percent', 'discount_amount', 'amount_paid'):
        val = d.get(f, '').strip()
        setattr(inv, f, val if val else None)

    for f in ('issue_date', 'due_date'):
        val = d.get(f, '').strip()
        if val:
            try:
                setattr(inv, f, datetime.strptime(val, '%Y-%m-%d').date())
            except ValueError:
                pass

    for field in ('line_items', 'payment_methods'):
        raw = d.get(field, '')
        try:
            setattr(inv, field, json.loads(raw) if raw else [])
        except (json.JSONDecodeError, TypeError):
            pass

    status = d.get('status')
    if status in dict(Invoice.STATUS):
        if status == 'sent' and not inv.sent_at:
            inv.sent_at = timezone.now()
        if status == 'paid' and not inv.paid_at:
            inv.paid_at = timezone.now()
        inv.status = status

    inv.save()


@staff_member_required
@require_POST
def invoice_mark_paid(request, pk):
    """Weka alama ya kulipwa (kamili au sehemu)."""
    inv = get_object_or_404(Invoice, pk=pk)
    amount = request.POST.get('amount', '').strip()
    ref = request.POST.get('reference', '').strip()
    if amount:
        try:
            inv.amount_paid = float(amount)
        except ValueError:
            return JsonResponse({'ok': False, 'error': 'Invalid amount'}, status=400)
    else:
        inv.amount_paid = inv.grand_total
    if ref:
        inv.paid_reference = ref[:120]
    if inv.balance_due <= 0:
        inv.status = 'paid'
        inv.paid_at = timezone.now()
    else:
        inv.status = 'partial'
    inv.save()
    return JsonResponse({'ok': True, 'status': inv.status,
                         'balance_due': inv.balance_due})


@staff_member_required
@require_POST
def invoice_ai_assist(request):
    from apps import docs_ai
    ok, result = docs_ai.assist_field(
        request.POST.get('field_type', 'notes'),
        request.POST.get('context', ''),
        request.POST.get('language', 'en'),
        kind='invoice')
    if not ok:
        return JsonResponse({'ok': False, 'error': result}, status=400)
    return JsonResponse({'ok': True, 'text': result})
