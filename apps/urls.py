


from django.urls import path
from . import views
from .views import select_website_type, dynamic_form, proposal_preview, generate_pdf

urlpatterns = [
    path('', views.home, name='home'),
    path('service/', views.service, name='service'),
    path('About/', views.About, name='About'),
    path('contact/', views.contact, name='contact'),
    
    # Proposal System URLs
    path('proposals/', select_website_type, name='select_website'),
    path('proposals/form/<int:website_type_id>/', dynamic_form, name='dynamic_form'),
    path('proposals/preview/<int:proposal_id>/', proposal_preview, name='proposal_preview'),
    path('proposals/download/<int:proposal_id>/', generate_pdf, name='generate_pdf'),
]