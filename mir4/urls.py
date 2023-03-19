"""mir4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))'
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hub_api/', include('hub_api.urls', namespace='hub_api')),
    path('hub_portal/', include('hub_portal.urls', namespace='hub_portal')),
    path('ext_tnt/', include('ext_tnt.urls', namespace='ext_tnt')),
    path('accounts/', include('mirusers.urls', namespace='mirusers')),
    path('', TemplateView.as_view(template_name='hub_api/index.html'), name='main'),
    # path('', RedirectView.as_view(url='/hub_api/'))
]
