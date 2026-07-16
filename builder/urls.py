"""URLs za dashboard (zinaingia kwenye ebenezeri/urls.py kama /builder/)."""
from django.urls import path
from . import views, ai

app_name = 'builder'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.my_sites, name='my_sites'),
    path('new/', views.create_site, name='create_site'),
    path('tutorial/', views.tutorial, name='tutorial'),

    path('site/<int:site_id>/', views.site_dashboard, name='site_dashboard'),
    path('site/<int:site_id>/settings/', views.site_settings_save, name='site_settings_save'),
    path('site/<int:site_id>/publish/', views.toggle_publish, name='toggle_publish'),
    path('site/<int:site_id>/template/', views.change_template, name='change_template'),

    path('site/<int:site_id>/pages/new/', views.page_create, name='page_create'),
    path('site/<int:site_id>/pages/<int:page_id>/edit/', views.page_editor, name='page_editor'),
    path('site/<int:site_id>/pages/<int:page_id>/delete/', views.page_delete, name='page_delete'),
    path('site/<int:site_id>/pages/<int:page_id>/load/', views.page_load, name='page_load'),
    path('site/<int:site_id>/pages/<int:page_id>/save/', views.page_save, name='page_save'),

    path('site/<int:site_id>/collections/<int:collection_id>/', views.collection_items, name='collection_items'),
    path('site/<int:site_id>/collections/<int:collection_id>/new/', views.item_form, name='item_new'),
    path('site/<int:site_id>/collections/<int:collection_id>/<int:item_id>/', views.item_form, name='item_edit'),
    path('site/<int:site_id>/collections/<int:collection_id>/<int:item_id>/delete/', views.item_delete, name='item_delete'),

    path('site/<int:site_id>/inquiries/', views.inquiries_list, name='inquiries_list'),
    path('site/<int:site_id>/inquiries/<int:inquiry_id>/status/', views.inquiry_status, name='inquiry_status'),

    path('site/<int:site_id>/assets/save/', views.asset_save, name='asset_save'),
    path('site/<int:site_id>/assets/', views.asset_list, name='asset_list'),

    path('ai/assist/', ai.ai_assist, name='ai_assist'),
]
