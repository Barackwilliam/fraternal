from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from io import BytesIO
from xhtml2pdf import pisa

def generate_proposal_pdf(proposal):
    # Tengeneza HTML
    html = render_to_string("proposal_pdf.html", {
        'proposal': proposal
    })
    
    # Tengeneza PDF
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    
    # Hifadhi kwenye model
    proposal.pdf_file.save(f'proposal_{proposal.id}.pdf', ContentFile(pdf.getvalue()))
    return pdf.getvalue()