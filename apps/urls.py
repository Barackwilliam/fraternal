# app/urls.py

from django.urls import path
from . import views
from .views import select_website_type, dynamic_form, proposal_preview, generate_pdf
from . import management_views

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

    # ── MANAGEMENT LOGIN / LOGOUT ─────────────────────────────
    path('manage/login/', management_views.management_login, name='management_login'),
    path('manage/logout/', management_views.management_logout, name='management_logout'),

    # ── WEBSITE MANAGEMENT PANEL ──────────────────────────
    path('manage/', management_views.management_dashboard, name='management_dashboard'),
    path('manage/websites/', management_views.website_list, name='website_list'),
    path('manage/websites/add/', management_views.website_add, name='website_add'),
    path('manage/websites/<int:pk>/', management_views.website_detail, name='website_detail'),

    # Status Actions
    path('manage/websites/<int:pk>/suspend/', management_views.suspend_website, name='suspend_website'),
    path('manage/websites/<int:pk>/restore/', management_views.restore_website, name='restore_website'),
    path('manage/websites/<int:pk>/maintenance/', management_views.set_maintenance, name='set_maintenance'),

    # Features
    path('manage/websites/<int:pk>/features/<int:feature_pk>/toggle/', management_views.toggle_feature, name='toggle_feature'),
    path('manage/websites/<int:pk>/features/add/', management_views.add_feature, name='add_feature'),

    # Payments
    path('manage/websites/<int:pk>/payments/add/', management_views.add_payment, name='add_payment'),

    # Notifications
    path('manage/websites/<int:pk>/notify/', management_views.send_notification, name='send_notification'),

    # Scheduled Actions
    path('manage/websites/<int:pk>/schedule/', management_views.schedule_action, name='schedule_action'),
    path('manage/actions/<int:action_pk>/cancel/', management_views.cancel_scheduled_action, name='cancel_scheduled_action'),

    # ── API ENDPOINTS (kwa client websites) ───────────────
    path('api/site-status/<str:api_key>/', management_views.site_status_api, name='site_status_api'),
    path('api/js/<str:api_key>/', management_views.get_js_snippet, name='get_js_snippet'),
]
