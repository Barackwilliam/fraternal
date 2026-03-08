# apps/urls.py

from django.urls import path
from . import views
from .views import select_website_type, dynamic_form, proposal_preview, generate_pdf
from . import management_views
from . import client_portal_views as portal

urlpatterns = [
    # ── PUBLIC SITE ───────────────────────────────────────
    path('', views.home, name='home'),
    path('service/', views.service, name='service'),
    path('About/', views.About, name='About'),
    path('contact/', views.contact, name='contact'),

    # Proposal System
    path('proposals/', select_website_type, name='select_website'),
    path('proposals/form/<int:website_type_id>/', dynamic_form, name='dynamic_form'),
    path('proposals/preview/<int:proposal_id>/', proposal_preview, name='proposal_preview'),
    path('proposals/download/<int:proposal_id>/', generate_pdf, name='generate_pdf'),

    # ── MANAGEMENT PANEL ──────────────────────────────────
    path('manage/login/', management_views.management_login, name='management_login'),
    path('manage/logout/', management_views.management_logout, name='management_logout'),
    path('manage/', management_views.management_dashboard, name='management_dashboard'),
    path('manage/websites/', management_views.website_list, name='website_list'),
    path('manage/websites/add/', management_views.website_add, name='website_add'),
    path('manage/websites/<int:pk>/', management_views.website_detail, name='website_detail'),
    path('manage/websites/<int:pk>/edit/', management_views.website_edit, name='website_edit'),
    path('manage/websites/<int:pk>/suspend/', management_views.suspend_website, name='suspend_website'),
    path('manage/websites/<int:pk>/restore/', management_views.restore_website, name='restore_website'),
    path('manage/websites/<int:pk>/maintenance/', management_views.set_maintenance, name='set_maintenance'),
    path('manage/websites/<int:pk>/features/<int:feature_pk>/toggle/', management_views.toggle_feature, name='toggle_feature'),
    path('manage/websites/<int:pk>/features/add/', management_views.add_feature, name='add_feature'),
    path('manage/websites/<int:pk>/payments/add/', management_views.add_payment, name='add_payment'),
    path('manage/websites/<int:pk>/notify/', management_views.send_notification, name='send_notification'),
    path('manage/websites/<int:pk>/schedule/', management_views.schedule_action, name='schedule_action'),
    path('manage/websites/<int:pk>/api-key/regenerate/', management_views.regenerate_api_key, name='regenerate_api_key'),
    path('manage/actions/<int:action_pk>/cancel/', management_views.cancel_scheduled_action, name='cancel_scheduled_action'),
    path('manage/clients/', management_views.client_list, name='client_list'),
    path('manage/clients/<int:pk>/', management_views.client_detail_admin, name='client_detail_admin'),

    # ── DOMAIN MANAGEMENT ─────────────────────────────────
    path('manage/domains/', management_views.domain_list, name='domain_list'),
    path('manage/domains/add/', management_views.domain_add, name='domain_add'),
    path('manage/domains/<int:pk>/', management_views.domain_detail, name='domain_detail'),
    path('manage/domains/<int:pk>/renew/', management_views.domain_renew, name='domain_renew'),
    path('manage/domains/<int:pk>/status/', management_views.domain_update_status, name='domain_update_status'),

    # ── EMAIL HOSTING MANAGEMENT ──────────────────────────
    path('manage/email/', management_views.email_hosting_list, name='email_hosting_list'),
    path('manage/email/add/', management_views.email_hosting_add, name='email_hosting_add'),
    path('manage/email/<int:pk>/', management_views.email_hosting_detail, name='email_hosting_detail'),
    path('manage/email/<int:pk>/payment/', management_views.email_hosting_payment, name='email_hosting_payment'),
    path('manage/email/<int:pk>/suspend/', management_views.email_hosting_suspend, name='email_hosting_suspend'),
    path('manage/email/<int:pk>/restore/', management_views.email_hosting_restore, name='email_hosting_restore'),

    # ── CLIENT PORTAL ─────────────────────────────────────
    path('portal/', portal.portal_dashboard, name='portal_dashboard'),
    path('portal/login/', portal.portal_login, name='portal_login'),
    path('portal/logout/', portal.portal_logout, name='portal_logout'),
    path('portal/register/', portal.portal_register, name='portal_register'),
    path('portal/websites/', portal.portal_website_list, name='portal_website_list'),
    path('portal/websites/<int:pk>/', portal.portal_website_detail, name='portal_website_detail'),
    path('portal/billing/', portal.portal_billing, name='portal_billing'),
    path('portal/billing/submit/', portal.portal_submit_payment, name='portal_submit_payment'),
    path('portal/notifications/', portal.portal_notifications, name='portal_notifications'),
    path('portal/profile/', portal.portal_profile, name='portal_profile'),
    path('portal/support/', portal.portal_support, name='portal_support'),
    path('portal/domains/', portal.portal_domains, name='portal_domains'),
    path('portal/email/', portal.portal_email_hosting, name='portal_email_hosting'),

    # ── PUBLIC API ─────────────────────────────────────────
    path('api/site-status/<str:api_key>/', management_views.site_status_api, name='site_status_api'),
    path('api/js/<str:api_key>/', management_views.get_js_snippet, name='get_js_snippet'),

    # ── CRON ENDPOINT ──────────────────────────────────────
    path('cron/emails/<str:secret>/', views.run_email_cron, name='run_email_cron'),
]