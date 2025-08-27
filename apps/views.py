from django.shortcuts import render
from .models import Question,Service,Team
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
# from .forms import MyContact


# Home Page
def home(request):
    team = Team.objects.all()

    context = {
        'team':team
    }
    return render(request, 'index.html',context)

# Elimu ya Ufahamu
def service(request):
    services = Service.objects.all()
    questions = Question.objects.all()

    context = {
        'services':services,
        'questions':questions

    }

    return render(request, 'service.html',context)

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
