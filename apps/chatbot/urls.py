from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──
    path('register/',  views.chatbot_register, name='chatbot_register'),
    path('login/',     views.chatbot_login,    name='chatbot_login'),
    path('logout/',    views.chatbot_logout,   name='chatbot_logout'),

    # ── Setup Wizard ──
    path('setup/', views.chatbot_setup_wizard, name='chatbot_setup_wizard'),

    # ── Portal ──
    path('dashboard/',                          views.chatbot_dashboard,           name='chatbot_dashboard'),
    path('config/',                             views.chatbot_config,              name='chatbot_config'),
    path('conversations/',                      views.chatbot_conversations,       name='chatbot_conversations'),
    path('conversations/<int:conv_id>/',        views.chatbot_conversation_detail, name='chatbot_conversation_detail'),
    path('billing/',                            views.chatbot_billing,             name='chatbot_billing'),

    # ── Webhook — ONE global URL for ALL bots ──
    path('webhook/', views.whatsapp_webhook_global, name='whatsapp_webhook_global'),

    # ── Legacy per-bot webhook ──
    path('webhook/<uuid:bot_id>/', views.whatsapp_webhook, name='whatsapp_webhook'),

    # ── Simulate / Test (staff only) ──
    path('simulate/<uuid:bot_id>/', views.simulate_message, name='chatbot_simulate'),
]