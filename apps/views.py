# app/view.py
from django.shortcuts import render
from .models import Question,Service,Team
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required


# Home Page
def home(request):
    from apps.seo.schema import (
        organization_schema, website_schema, local_business_schema,
        jamiibot_product_schema, faq_schema, render_schemas
    )
    team = Team.objects.all()

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
        'team': team,
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


# Warsha za Kiroho
def contact(request):
    # form = MyContact(request.POST)
    # ujumbe = ""


    # if request.method == 'POST':
    #     form = MyContact(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         ujumbe = "Hongera Ujumbe Wako Umetumwa Kikamilifu"
    #     else:
    #         form = MyContact()  
      
    # context = {
    #     'form':form,
    #     'ujumbe':ujumbe
    # }
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
    return render(request, 'select_website.html', {
        'website_types': website_types,
        'title': 'Select Website Type'
    })


def dynamic_form(request, website_type_id):
    website_type = get_object_or_404(WebsiteType, id=website_type_id)
    
    if request.method == 'POST':
        form = DynamicProposalForm(website_type.name, request.POST)
        if form.is_valid():
            # Create or get client
            client, created = Client.objects.get_or_create(
                email=form.cleaned_data.get('client_email'),
                defaults={
                    'name': form.cleaned_data.get('client_name'),
                    'phone': form.cleaned_data.get('client_phone'),
                    'company': form.cleaned_data.get('client_company')
                }
            )
            
            # Create proposal
            proposal = ProjectProposal.objects.create(
                client=client,
                website_type=website_type,
                requirements=form.cleaned_data
            )
            
            return redirect('proposal_preview', proposal_id=proposal.id)
    else:
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'client'):
            initial_data = {
                'client_name': request.user.client.name,
                'client_email': request.user.client.email,
                'client_phone': request.user.client.phone,
                'client_company': request.user.client.company
            }
        
        form = DynamicProposalForm(website_type.name, initial=initial_data)
    
    # Gawa fields kugawanya client na project requirements
    client_fields = []
    project_fields = []
    
    for field in form:
        if field.name.startswith('client_'):
            client_fields.append(field)
        else:
            project_fields.append(field)
    
    context = {
        'form': form,
        'website_type': website_type,
        'client_fields': client_fields,
        'project_fields': project_fields,
        'title': f'{website_type.name} Requirements'
    }
    
    return render(request, 'dynamic_form.html', context)

def proposal_preview(request, proposal_id):
    proposal = ProjectProposal.objects.get(id=proposal_id)
    return render(request, 'proposal_preview.html', {
        'proposal': proposal,
        'title': 'Proposal Preview'
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

    context = {
        'proposal': proposal,
        'requirements': requirements,
        'total_cost': total_cost
    }

    html = render_to_string(template_path, context)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse('We had some errors with PDF rendering <br>' + html)
    return result.getvalue()

def generate_pdf(request, proposal_id):
    proposal = ProjectProposal.objects.get(id=proposal_id)

    if isinstance(proposal.requirements, str):
        try:
            proposal.requirements = json.loads(proposal.requirements)
        except Exception:
            proposal.requirements = {}

    pdf_file = generate_proposal_pdf(proposal)

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="proposal_{proposal.id}.pdf"'
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
    """Injects topbar into template HTML and returns it directly — no iframe"""
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponse
    tpl = get_object_or_404(WebsiteTemplate, pk=pk, is_active=True)

    topbar = f'''
<style>
  #jt-preview-bar{{position:fixed;top:0;left:0;right:0;height:52px;z-index:2147483647;background:#1a1a2e;display:flex;align-items:center;justify-content:space-between;padding:0 16px;gap:1rem;box-shadow:0 2px 12px rgba(0,0,0,0.5);font-family:sans-serif;}}
  #jt-preview-bar a,#jt-preview-bar button{{font-size:.75rem;font-weight:700;padding:7px 14px;border-radius:8px;border:none;cursor:pointer;text-decoration:none;transition:all .2s;white-space:nowrap;}}
  .jt-logo{{font-weight:900;font-size:1rem;color:#6c63ff !important;text-decoration:none !important;}}
  .jt-sep{{color:#444;margin:0 4px;}}
  .jt-tpl-name{{font-size:.85rem;font-weight:700;color:#ddd;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
  .jt-cat{{font-size:.62rem;font-weight:700;padding:3px 9px;border-radius:10px;background:rgba(108,99,255,.2);color:#a78bfa;border:1px solid rgba(108,99,255,.3);}}
  .jt-back{{background:rgba(255,255,255,.08);color:#ccc !important;}}
  .jt-back:hover{{background:rgba(255,255,255,.15);color:#fff !important;}}
  .jt-order{{background:linear-gradient(135deg,#6c63ff,#ff6584);color:#fff !important;box-shadow:0 3px 12px rgba(108,99,255,.4);}}
  .jt-order:hover{{transform:translateY(-1px);}}
  .jt-bar-left{{display:flex;align-items:center;gap:8px;overflow:hidden;flex:1;}}
  .jt-bar-right{{display:flex;align-items:center;gap:8px;flex-shrink:0;}}
  body{{padding-top:52px !important;}}
  @media(max-width:480px){{.jt-tpl-name,.jt-cat,.jt-sep{{display:none;}}}}
</style>
<div id=jt-preview-bar>
  <div class=jt-bar-left>
    <a href=/templates/ class=jt-logo>JamiiTek</a>
    <span class=jt-sep>|</span>
    <span class=jt-tpl-name>{tpl.name}</span>
    <span class=jt-cat>{tpl.get_category_display()}</span>
  </div>
  <div class=jt-bar-right>
    <a href=/templates/ class=jt-back>← Back</a>
    <button class=jt-order onclick="(function(){{var m='Habari JamiiTek! 👋\n\nNimetazama preview ya *{tpl.name}* na ninapenda!\n\nNaomba maelezo zaidi.';window.open('https://wa.me/255629712678?text='+encodeURIComponent(m),'_blank');}})();">🛒 Get This Template</button>
  </div>
</div>
'''

    # Inject topbar right after <body> tag if exists, else prepend
    html = tpl.preview_html
    if '<body' in html.lower():
        import re
        html = re.sub(r'(<body[^>]*>)', r'' + topbar, html, count=1, flags=re.IGNORECASE)
    else:
        html = topbar + html

    return HttpResponse(html, content_type='text/html; charset=utf-8')
