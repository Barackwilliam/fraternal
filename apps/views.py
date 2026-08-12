# app/view.py
from django.shortcuts import render
from .models import Question,Service,Team,BlogPost
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required


# # Home Page
# def home(request):
#     from apps.seo.schema import (
#         organization_schema, website_schema, local_business_schema,
#         jamiibot_product_schema, faq_schema, render_schemas
#     )
#     team = Team.objects.all()

#     faqs = [
#         ("Je, JamiiTek ni nini?", "JamiiTek ni kampuni ya teknolojia Tanzania inayotengeneza websites, apps, na AI WhatsApp bots kwa biashara."),
#         ("What is JamiiBot?", "JamiiBot is an AI-powered WhatsApp chatbot that responds to customer questions 24/7 in Swahili and English, starting from TZS 15,000/month."),
#         ("How much does a website cost in Tanzania?", "JamiiTek builds websites starting from TZS 150,000. Price depends on complexity, features, and design requirements."),
#         ("Je, JamiiBot inafanya kazi vipi?", "JamiiBot inajibu maswali ya wateja kupitia WhatsApp kiotomatiki, saa 24 kwa lugha ya Kiswahili na Kiingereza."),
#         ("Do you offer web hosting in Tanzania?", "Yes, JamiiTek offers reliable web hosting with 99.9% uptime, SSL certificates, and daily backups."),
#         ("How long does website development take?", "Most websites are delivered within 2-6 weeks depending on scope and content availability."),
#         ("Je, mnaunda WhatsApp bot Tanzania?", "Ndiyo! JamiiBot ni AI WhatsApp bot ya biashara Tanzania. Inajibu wateja saa 24 bila msaada wa binadamu."),
#         ("What programming languages do you use?", "We use Python/Django, JavaScript, React, and modern web technologies for all our projects."),
#     ]

#     schema_html = render_schemas(
#         organization_schema(),
#         website_schema(),
#         local_business_schema(),
#         jamiibot_product_schema(),
#         faq_schema(faqs),
#     )

#     context = {
#         'team': team,
#         'schema_markup': schema_html,
#         'latest_posts': BlogPost.objects.filter(status='published')[:3],
#         'page_title': 'JamiiTek — Web Development & AI WhatsApp Bot Tanzania',
#         'page_desc': (
#             "JamiiTek: Tanzania's leading web developer. We build websites, AI WhatsApp bots "
#             "(JamiiBot), web hosting & domains. Serving Dar es Salaam and all Tanzania. "
#             "Tunajenga website Tanzania. Bot WhatsApp Tanzania."
#         ),
#         'canonical': 'https://jamiitek.com/',
#     }
#     return render(request, 'index.html', context)





# Replacement for the `home` view in apps/views.py
#
# Only the context changes — the SEO block is untouched.

from django.shortcuts import render

from .models import Team, BlogPost, Service
from .site_content import HeroSlide, PortfolioItem, Testimonial


def home(request):
    from apps.seo.schema import (
        organization_schema, website_schema, local_business_schema,
        jamiibot_product_schema, faq_schema, render_schemas
    )

    faqs = [
        ("Je, JamiiTek ni nini?", "JamiiTek ni kampuni ya teknolojia Tanzania inayotengeneza websites, apps, na AI WhatsApp bots kwa biashara."),
        ("What is JamiiBot?", "JamiiBot is an AI-powered WhatsApp chatbot that responds to customer questions 24/7 in Swahili and English, starting from TZS 15,000/month."),
        ("How much does a website cost in Tanzania?", "JamiiTek builds websites starting from TZS 150,000. Price depends on complexity, features, and design requirements."),
        ("Je, JamiiBot inafanya kazi vipi?", "JamiiBot inajibu maswali ya wateja kupitia WhatsApp kiotomatiki, saa 24 kwa lugha ya Kiswahili na Kiingereza."),
        ("Do you offer web hosting in Tanzania?", "Yes, JamiiTek offers reliable web hosting with 99.9% uptime, SSL certificates, and daily backups."),
        ("How long does website development take?", "Most websites are delivered within 2-6 weeks depending on scope and content availability."),
        ("Je, mnaunda WhatsApp bot Tanzania?", "Ndiyo! JamiiBot ni AI WhatsApp bot ya biashara Tanzania. Inajibu wateja saa 24 bila msaada wa binadamu."),
        ("What programming languages do you use?", "We use Python/Django, JavaScript, React, and modern web technologies for all our projects."),
    ]

    schema_html = render_schemas(
        organization_schema(),
        website_schema(),
        local_business_schema(),
        jamiibot_product_schema(),
        faq_schema(faqs),
    )

    context = {
        # ── slider content (all admin-managed) ──────────────────
        'hero_slides':  HeroSlide.objects.filter(is_active=True).exclude(image=''),
        'portfolio':    PortfolioItem.objects.filter(is_featured=True).exclude(image='')[:12],
        'testimonials': Testimonial.objects.filter(is_active=True)[:9],
        'services':     Service.objects.all()[:8],
        'team':         Team.objects.all(),
        'latest_posts': BlogPost.objects.filter(status='published')[:3],

        # ── SEO (unchanged) ─────────────────────────────────────
        'schema_markup': schema_html,
        'page_title': 'JamiiTek — Web Development & AI WhatsApp Bot Tanzania',
        'page_desc': (
            "JamiiTek: Tanzania's leading web developer. We build websites, AI WhatsApp bots "
            "(JamiiBot), web hosting & domains. Serving Dar es Salaam and all Tanzania. "
            "Tunajenga website Tanzania. Bot WhatsApp Tanzania."
        ),
        'canonical': 'https://jamiitek.com/',
    }
    return render(request, 'index.html', context)

# Elimu ya Ufahamu
def service(request):
    from apps.seo.schema import (
        organization_schema, faq_schema, render_schemas, breadcrumb_schema
    )
    services = Service.objects.all()
    questions = Question.objects.all()

    # Build FAQ from DB questions
    faqs_data = [(q.question, q.answer) for q in questions] if questions else [
        ("What web services does JamiiTek offer?", "JamiiTek offers website development, mobile app development, AI WhatsApp bots, web hosting, domain registration, UI/UX design, and system integration."),
        ("How much does website development cost in Tanzania?", "Websites start from TZS 150,000 for basic sites up to TZS 5,000,000+ for complex web applications."),
        ("Je, mnatengeneza website Tanzania?", "Ndiyo, JamiiTek inatengeneza websites za hali ya juu Tanzania kwa bei nafuu."),
        ("Do you build mobile apps?", "Yes, we develop Android and iOS apps using modern frameworks."),
    ]

    schema_html = render_schemas(
        organization_schema(),
        breadcrumb_schema([("Home", "/"), ("Services", "/service/")]),
        faq_schema(faqs_data),
    )

    context = {
        'services': services,
        'questions': questions,
        'schema_markup': schema_html,
        'page_title': 'Our Services — Web Development, AI Bots & Hosting | JamiiTek Tanzania',
        'page_desc': 'JamiiTek services: website development, AI WhatsApp bots, web hosting, domain registration, mobile apps, UI/UX design. Best web developer in Tanzania.',
        'canonical': 'https://jamiitek.com/service/',
        'page_keywords': 'web development services Tanzania, AI WhatsApp bot, website design Tanzania, web hosting Tanzania, domain registration Tanzania, mobile app Tanzania',
    }
    return render(request, 'service.html', context)

# Warsha za Kiroho
def contact(request):
    return render(request, 'contact.html')

# Ushuhuda wa Wateja
def About(request):
    return render(request, 'about.html')

def contact(request):
    """
    Contact form view with Turnstile protection
    
    Flow:
    1. GET — render form kwa TURNSTILE_SITEKEY
    2. POST — frontend sends cf-turnstile-response token
    3. Mixin au middleware validates token
    4. Form cleaned (kama valid)
    5. Email sent to admin
    """
    
    if request.method == 'POST':
        # Pata data kutoka POST
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Token verification ni automatic via middleware (kama enabled)
        # Kama hapo na error, middleware itarudi 403 na request hautafikia hapa
        
        # Validate required fields
        if not all([full_name, email, subject, message]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'contact.html')
        
        # Email validation (kama inataka zaidi)
        try:
            validate_email = email.endswith('.com') or email.endswith('.co.tz') or '@' in email
            if not validate_email:
                messages.error(request, "Invalid email address.")
                return render(request, 'contact.html')
        except:
            messages.error(request, "Invalid email address.")
            return render(request, 'contact.html')
        
        # Send email to admin
        try:
            admin_email = 'info@jamiitek.com'
            send_mail(
                subject=f"New Contact Form: {subject}",
                message=f"""
From: {full_name} <{email}>
Subject: {subject}
 
Message:
{message}
 
---
Contact form message from JamiiTek website
                """,
                from_email='info@jamiitek.com',
                recipient_list=[admin_email],
                fail_silently=False,
            )
            
            # Optional: Send confirmation email to customer
            send_mail(
                subject="We received your message — JamiiTek",
                message=f"""
Hi {full_name},
 
Thank you for reaching out. We've received your message and will respond within 24 hours.
 
Subject: {subject}
 
Best regards,
JamiiTek Team
                """,
                from_email='info@jamiitek.com',
                recipient_list=[email],
                fail_silently=True,
            )
            
            ujumbe = "✓ Your message has been sent successfully! We'll respond within 24 hours."
            messages.success(request, ujumbe)
            
        except Exception as e:
            ujumbe = f"✗ Error sending email: {str(e)}"
            messages.error(request, ujumbe)
            return render(request, 'contact.html', {'ujumbe': ujumbe})
    
    return render(request, 'contact.html')



import os
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import WebsiteType, Client, ProjectProposal
from .forms import DynamicProposalForm
from .utils.pdf_generator import generate_proposal_pdf

def select_website_type(request):
    website_types = WebsiteType.objects.all()
    # "Order This" kutoka /templates/preview/<pk>/ inabeba ?template=<pk>
    ref_template = None
    tpl_id = request.GET.get('template')
    if tpl_id:
        ref_template = WebsiteTemplate.objects.filter(
            pk=tpl_id, is_active=True).first()
    return render(request, 'select_website.html', {
        'website_types': website_types,
        'ref_template': ref_template,
        'title': 'Select Website Type'
    })


# ═══════════════════════════════════════════════════════════════════
# apps/views.py — REPLACEMENT kwa `dynamic_form`
#
# Badilisha function nzima ya `dynamic_form` (ilianzia mstari 200)
# na hii. Hakuna kingine kwenye file kinachohitaji kubadilishwa.
#
# Ongeza import hizi juu ya file kama hazipo:
#     import logging
#     logger = logging.getLogger(__name__)
# ═══════════════════════════════════════════════════════════════════

import logging

logger = logging.getLogger(__name__)


def _resolve_client(cleaned):
    """
    Pata Client anayelingana na email, au tengeneza mpya.

    KWA NINI SI get_or_create:
    `Client.email` HAINA unique=True (models.py:112), lakini get_or_create
    inaita .get() ndani yake — hivyo inavunjika na MultipleObjectsReturned
    mara tu duplicates zinapoingia. Duplicates zinatokea kwa sababu sehemu
    tatu tofauti zinatengeneza Client: portal register, chatbot fallback
    (client_portal_views.py:49), na form hii.

    .first() haiwezi kuvunjika hata kama kuna duplicates kumi.
    order_by('pk') inahakikisha tunachukua rekodi ileile kila mara,
    si ya nasibu — muhimu ili proposals za mteja zisitawanyike.
    """
    email = (cleaned.get('client_email') or '').strip().lower()

    # iexact: 'Willy@x.com' na 'willy@x.com' ni mtu mmoja
    matches = Client.objects.filter(email__iexact=email).order_by('pk')
    client = matches.first()

    if client is None:
        return Client.objects.create(
            email=email,
            name=(cleaned.get('client_name') or '').strip(),
            phone=(cleaned.get('client_phone') or '').strip(),
            company=(cleaned.get('client_company') or '').strip(),
        )

    count = matches.count()
    if count > 1:
        logger.warning(
            "Client duplicates kwa %s: %s rekodi (pk: %s). Natumia pk=%s.",
            email, count, list(matches.values_list('pk', flat=True)), client.pk,
        )

    # Jaza sehemu tupu TU. Mteja anaweza kuwa alijaza jina kamili kwenye
    # portal; proposal form isilifute kwa jina fupi alilotumia hapa.
    updated = []
    for field, value in (
        ('name',    cleaned.get('client_name')),
        ('phone',   cleaned.get('client_phone')),
        ('company', cleaned.get('client_company')),
    ):
        value = (value or '').strip()
        if value and not getattr(client, field):
            setattr(client, field, value)
            updated.append(field)

    if updated:
        client.save(update_fields=updated)

    return client


def dynamic_form(request, website_type_id):
    website_type = get_object_or_404(WebsiteType, id=website_type_id)

    # DynamicProposalForm inakubali request= tu kama TurnstileFormMixin
    # imeongezwa. Hii inaruhusu view kufanya kazi kabla NA baada ya mixin,
    # bila TypeError.
    form_kwargs = {}
    try:
        from apps.turnstile import TurnstileFormMixin
        if issubclass(DynamicProposalForm, TurnstileFormMixin):
            form_kwargs['request'] = request
    except ImportError:
        pass

    if request.method == 'POST':
        form = DynamicProposalForm(website_type.name, request.POST, **form_kwargs)

        if form.is_valid():
            client = _resolve_client(form.cleaned_data)

            requirements = dict(form.cleaned_data)
            # Token ya Turnstile ni ya matumizi ya mara moja — isihifadhiwe
            # kwenye JSON wala isionekane kwenye proposal ya mteja.
            requirements.pop('turnstile', None)

            tpl_id = request.POST.get('reference_template')
            if tpl_id:
                ref = WebsiteTemplate.objects.filter(
                    pk=tpl_id, is_active=True).first()
                if ref:
                    requirements['reference_template'] = {
                        'id': ref.pk,
                        'name': ref.name,
                        'category': ref.get_category_display(),
                        'preview_url': f'/templates/preview/{ref.pk}/',
                    }

            proposal = ProjectProposal.objects.create(
                client=client,
                website_type=website_type,
                requirements=requirements,
            )

            return redirect('proposal_preview', proposal_id=proposal.id)

    else:
        initial_data = {}
        if request.user.is_authenticated:
            profile = Client.objects.filter(user=request.user).first()
            if profile:
                initial_data = {
                    'client_name':    profile.name,
                    'client_email':   profile.email,
                    'client_phone':   profile.phone,
                    'client_company': profile.company,
                }

        form = DynamicProposalForm(
            website_type.name, initial=initial_data, **form_kwargs)

    # Gawa fields: client details dhidi ya project requirements
    client_fields = []
    project_fields = []
    for field in form:
        if field.name == 'turnstile':
            continue          # inarendwa peke yake kwenye template
        if field.name.startswith('client_'):
            client_fields.append(field)
        else:
            project_fields.append(field)

    ref_template = None
    tpl_id = request.GET.get('template') or request.POST.get('reference_template')
    if tpl_id:
        ref_template = WebsiteTemplate.objects.filter(
            pk=tpl_id, is_active=True).first()

    context = {
        'form': form,
        'website_type': website_type,
        'client_fields': client_fields,
        'project_fields': project_fields,
        'ref_template': ref_template,
        'title': f'{website_type.name} Requirements',
    }

    return render(request, 'dynamic_form.html', context)

# ═══════════════════════════════════════════════════════════════════
# PATCH kwa apps/views.py
# Badilisha function ya `proposal_preview` (ilikuwa mstari ~275)
# ═══════════════════════════════════════════════════════════════════

from django.shortcuts import get_object_or_404


# ── Helper: gawa "Feature Name | 250000" kuwa (jina, bei) ──────────
def _parse_choice(raw):
    """
    Values za checkbox zinahifadhiwa kama 'Online Payments | 250000'.
    Rudisha (name, price_int). Kama hakuna '|', bei ni 0.
    """
    text = str(raw)
    if '|' not in text:
        return text.strip(), 0

    name, _, price_part = text.rpartition('|')
    digits = ''.join(ch for ch in price_part if ch.isdigit())
    try:
        price = int(digits) if digits else 0
    except ValueError:
        price = 0
    return name.strip(), price


def _build_requirement_rows(requirements):
    """
    Geuza requirements dict kuwa rows tayari kwa template, na uhesabu jumla.

    MUHIMU: bei zinatokana TU na sehemu iliyo baada ya '|' kwenye chaguo
    zilizochaguliwa. Hesabu ya zamani ilikuwa inakusanya KILA tarakimu
    kwenye table — ikiwemo namba ya simu ya mteja — hivyo jumla ilikuwa
    inaweza kuwa mabilioni. Hii ndiyo sababu ya kuhesabu upande wa server.
    """
    rows = []
    total = 0

    for key, value in requirements.items():
        if key == 'reference_template' or key.startswith('client_'):
            continue
        if key in ('turnstile', 'csrfmiddlewaretoken'):
            continue

        label = key.replace('_', ' ').strip().title()

        # Chaguo nyingi (checkbox) → list
        if isinstance(value, (list, tuple)):
            items = []
            for raw in value:
                name, price = _parse_choice(raw)
                total += price
                items.append({'name': name, 'price': price or None})
            if items:
                rows.append({'label': label, 'items': items, 'text': None})

        # Jibu la maandishi
        else:
            text = str(value).strip() if value not in (None, '') else ''
            rows.append({'label': label, 'items': None, 'text': text})

    return rows, total


def proposal_preview(request, proposal_id):
    proposal = get_object_or_404(ProjectProposal, id=proposal_id)

    requirements = proposal.requirements
    if isinstance(requirements, str):
        import json
        try:
            requirements = json.loads(requirements)
        except Exception:
            requirements = {}
    if not isinstance(requirements, dict):
        requirements = {}

    rows, total_cost = _build_requirement_rows(requirements)

    return render(request, 'proposal_preview.html', {
        'proposal': proposal,
        'requirement_rows': rows,
        'total_cost': total_cost,
        'title': 'Proposal Preview',
    })



import json
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .models import ProjectProposal

def generate_proposal_pdf(proposal):
    template_path = 'proposal_pdf.html'

    requirements = proposal.requirements.copy()
    total_cost = 0

    for key, value in requirements.items():
        if 'cost' in key.lower() or 'price' in key.lower():
            try:
                cost = float(value)
                requirements[key] = cost
                total_cost += cost
            except (ValueError, TypeError):
                continue

    # Reference design (kama proposal ilianzia /templates/preview/) — itolewe
    # kwenye requirements loop na ionekane kama section yake kwenye PDF
    ref_template = requirements.pop('reference_template', None)

    context = {
        'proposal': proposal,
        'requirements': requirements,
        'total_cost': total_cost,
        'ref_template': ref_template,
    }

    html = render_to_string(template_path, context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse('We had some errors with PDF rendering <br>' + html)
    return result.getvalue()

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
 
from apps.utils.proposal_pdf import generate_proposal_pdf
 
 
def generate_pdf(request, proposal_id):
    proposal = get_object_or_404(ProjectProposal, id=proposal_id)
 
    pdf_bytes = generate_proposal_pdf(proposal)
 
    if not pdf_bytes:
        # Ya zamani ilirudisha HTML mbichi ndani ya response ya PDF —
        # browser ilipakua faili bovu. Sasa mteja anarudi kwenye preview
        # na ujumbe unaoeleweka.
        messages.error(
            request,
            'We could not build the PDF just now. Please try again, '
            'or contact us and we will send it to you directly.'
        )
        return redirect('proposal_preview', proposal_id=proposal.id)
 
    filename = f'JamiiTek-Quotation-JT-{proposal.id}.pdf'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# import json
# from django.http import HttpResponse
# from django.template.loader import render_to_string
# from xhtml2pdf import pisa
# from io import BytesIO
# from pyuploadcare import Uploadcare
# from .models import ProjectProposal

# # Initialize Uploadcare client
# uc = Uploadcare(public_key='76122001cca4add87f02', secret_key='f00801b9b65172d50de5')

# def generate_proposal_pdf(proposal):
#     template_path = 'proposal_pdf.html'

#     requirements = proposal.requirements.copy()
#     total_cost = 0

#     # Hesabu total cost
#     for key, value in requirements.items():
#         if 'cost' in key.lower() or 'price' in key.lower():
#             try:
#                 cost = float(value)
#                 requirements[key] = cost
#                 total_cost += cost
#             except (ValueError, TypeError):
#                 continue

#     context = {
#         'proposal': proposal,
#         'requirements': requirements,
#         'total_cost': total_cost
#     }

#     html = render_to_string(template_path, context)
#     result = BytesIO()
#     pisa_status = pisa.CreatePDF(html, dest=result)

#     if pisa_status.err:
#         return HttpResponse('We had some errors with PDF rendering <br>' + html)
#     result.seek(0)  # Read from beginning
#     return result

# def generate_pdf(request, proposal_id):
#     proposal = ProjectProposal.objects.get(id=proposal_id)

#     # Ensure requirements is a dict
#     if isinstance(proposal.requirements, str):
#         try:
#             proposal.requirements = json.loads(proposal.requirements)
#         except Exception:
#             proposal.requirements = {}

#     pdf_buffer = generate_proposal_pdf(proposal)

#     # Uploadcare: tumia from_bytes (pyuploadcare 6.x inatumia this method)
#     if pdf_buffer:
#         pdf_buffer.seek(0)
#         upload = uc.upload_from_bytes(pdf_buffer.read(), filename=f"proposal_{proposal.id}.pdf")
#         proposal.pdf_file = upload.cdn_url  # Hii inahifadhi URL kwenye database
#         proposal.save()
#         pdf_buffer.seek(0)  # Kurudi mwanzo ili kurudisha HTTP response

#     response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="proposal_{proposal.id}.pdf"'
#     return response


# ══════════════════════════════════════════════════════════════════
# CRON ENDPOINT — Called by cron-job.org daily to send emails
# URL: /cron/emails/jamiitek-cron-2025/
# ══════════════════════════════════════════════════════════════════

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def run_email_cron(request, secret):
    if secret != 'jamiitek-cron-2025':
        from django.http import JsonResponse
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    from apps.utils.email_notifications import send_bulk_expiry_warnings
    from django.http import JsonResponse
    result = send_bulk_expiry_warnings()
    return JsonResponse(result)

# ============================================================
# WEBSITE TEMPLATES MARKETPLACE
# ============================================================
from .models import WebsiteTemplate
from django.utils.safestring import mark_safe

def templates_marketplace(request):
    """Page inayoonyesha templates zote zilizowekwa na admin"""
    category = request.GET.get('category', 'all')
    templates = WebsiteTemplate.objects.filter(is_active=True)
    if category != 'all':
        templates = templates.filter(category=category)
    
    all_templates = WebsiteTemplate.objects.filter(is_active=True)
    categories_used = all_templates.values_list('category', flat=True).distinct()

    return render(request, 'templates_marketplace.html', {
        'templates': templates,
        'selected_category': category,
        'total_count': all_templates.count(),
        'filtered_count': templates.count(),
        'categories_used': list(categories_used),
    })


def template_preview(request, pk):
    """Wrapper page — preview bar + device toggle + iframe"""
    from django.shortcuts import get_object_or_404
    tpl = get_object_or_404(WebsiteTemplate, pk=pk, is_active=True)
    return render(request, 'template_preview.html', {'template': tpl})


from django.views.decorators.clickjacking import xframe_options_exempt

@xframe_options_exempt
def template_preview_raw(request, pk):
    """Serves the raw template HTML inside the iframe — exempt from X-Frame-Options"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    tpl = get_object_or_404(WebsiteTemplate, pk=pk, is_active=True)
    if not tpl.preview_html or not tpl.preview_html.strip():
        return HttpResponse('<p style="font-family:sans-serif;padding:2rem;color:#999">Hakuna HTML iliyowekwa kwa template hii.</p>', content_type='text/html; charset=utf-8')
    return HttpResponse(tpl.preview_html, content_type='text/html; charset=utf-8')