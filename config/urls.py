"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Identity APIs (Login, Auth)
    path('api/v1/auth/', include('apps.identity.urls')),
    
    # HR APIs (Dashboard, Profile)
    path('api/v1/hr/', include('apps.hr.urls')),

    # Operations APIs (Leave Management)
    path('api/v1/operations/', include('apps.operations.urls')),

    # Finance APIs (Earnings, Payments)
    path('api/v1/finance/', include('apps.finance.urls')),

    # Canteen APIs (Menu, Orders)
    path('api/v1/canteen/', include('apps.canteen.urls')),

    # Programs APIs (Internship Programs)
    path('api/v1/programs/', include('apps.programs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)