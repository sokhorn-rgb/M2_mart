"""
URL configuration for posdb project.

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
# posdb/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # /admin/  → ផ្ទាំង Django admin
    path('sales/', include('sales.urls')),    # /sales/  → បញ្ជូនទៅ sales/urls.py
    path('accounts/', include('django.contrib.auth.urls')),  # login, logout, password change

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ឧទាហរណ៍លំហូរ URL:
# Request: GET /sales/products/3/
# ផ្គូផ្គង: path('sales/', ...) → កាត់ 'sales/' ហើយបញ្ជូន 'products/3/' ទៅ sales/urls.py
# ផ្គូផ្គង: path('products/<int:pk>/', ...) → ហៅ product_detail(request, pk=3)

# URL map:
# /                  → redirect to /accounts/login/
# /accounts/login/   → login page
# /accounts/logout/  → logs the user out
# /sales/products/   → product catalogue  (requires login)
# /sales/orders/     → orders list        (requires login)
# /admin/            → Django admin panel