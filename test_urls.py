from django.contrib import admin
from django.urls import path, include
from builder import views as builder_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('builder/', include('builder.urls')),
    path('get-started/', builder_views.get_started, name='get_started'),
]
