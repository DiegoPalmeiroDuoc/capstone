"""
URL configuration for intexta_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Páginas web
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('home/', views.home, name='home'),
    path('debug-logs/', views.debug_logs_view, name='debug_logs'),
    
    # API Endpoints
    path('api/docs/', views.api_list_docs, name='api_list_docs'),
    path('api/docs/status/', views.api_document_status, name='api_document_status'),
    path('api/docs/process/', views.api_process_document, name='api_process_document'),
    path('api/docs/search/', views.api_search_documents, name='api_search_documents'),
    path('api/processor/trigger/', views.api_trigger_processor, name='api_trigger_processor'),
    path('api/user/update-phone/', views.api_update_phone, name='api_update_phone'),
]