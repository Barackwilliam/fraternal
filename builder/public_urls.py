"""
URLconf ya websites za wateja (subdomains). SubdomainMiddleware ina-set
request.urlconf = 'builder.public_urls' — kwa hiyo subdomain HAIWEZI
kufikia dashboard, admin, wala URLs za platform.
"""
from django.urls import path
from . import public_views

urlpatterns = [
    path('', public_views.home, name='client_home'),
    path('p/<slug:slug>/', public_views.page_view, name='client_page'),
    path('c/<slug:col_slug>/', public_views.collection_list, name='client_collection'),
    path('c/<slug:col_slug>/<slug:item_slug>/', public_views.item_detail, name='client_item'),
]
