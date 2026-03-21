"""
URL configuration for mocon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# SITE_MODE controls which site's URLs are served at root '/'
# Set SITE_MODE=construction in Azure App Settings for missouriconstruction.com
# Set SITE_MODE=springfield (or omit) for seekingspringfield.com
# Set SITE_MODE=washington for seekingwashington.com (future)
SITE_MODE = os.getenv('SITE_MODE', 'springfield')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('allauth.urls')),  # Social auth: /accounts/google/login/, etc.
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if SITE_MODE == 'construction':
    urlpatterns += [path('', include('construction.urls', namespace='construction'))]
else:
    # Default: seekingspringfield.com (springfield or washington modes)
    urlpatterns += [path('', include('core.urls'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
