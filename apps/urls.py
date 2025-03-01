
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('service/', views.service, name='service'),
    path('About/', views.About, name='About'),
    path('contact/', views.contact, name='contact'),
    path('About/', views.About, name='About'),
   
]
