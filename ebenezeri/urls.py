from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from apps.chatbot.manage_views import (
    manage_chatbot_overview, manage_bot_detail, manage_bot_action,
    manage_bot_payments, manage_verify_payment, manage_reject_payment,
    manage_bulk_payment_action, manage_bot_clients, manage_bot_whatsapp,
    jamiibot_landing
)
from apps.seo.sitemaps import sitemaps
from apps.seo.views import robots_txt
from apps.seo.manifest import web_manifest

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path('chatbot/', include('apps.chatbot.urls')),

    # ── SEO ──────────────────────────────────────────────
    path('robots.txt',  robots_txt,  name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('manifest.json', web_manifest, name='web_manifest'),

    # JamiiBot Landing Page
    path('bot/', jamiibot_landing, name='jamiibot_landing'),

    # Manage ChatBot Section
    path('manage/chatbot/', manage_chatbot_overview, name='manage_chatbot'),
    path('manage/chatbot/bots/<uuid:bot_id>/', manage_bot_detail, name='manage_bot_detail'),
    path('manage/chatbot/bots/<uuid:bot_id>/action/', manage_bot_action, name='manage_bot_action'),
    path('manage/chatbot/payments/', manage_bot_payments, name='manage_bot_payments'),
    path('manage/chatbot/payments/<int:payment_id>/verify/', manage_verify_payment, name='manage_verify_payment'),
    path('manage/chatbot/payments/<int:payment_id>/reject/', manage_reject_payment, name='manage_reject_payment'),
    path('manage/chatbot/payments/bulk-action/', manage_bulk_payment_action, name='manage_bulk_payment_action'),
    path('manage/chatbot/clients/', manage_bot_clients, name='manage_bot_clients'),
    path('manage/chatbot/bots/<uuid:bot_id>/whatsapp/', manage_bot_whatsapp, name='manage_bot_whatsapp'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)