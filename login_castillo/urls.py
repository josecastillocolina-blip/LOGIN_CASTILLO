"""
URL configuration for login_castillo project.

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
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from app_usuarios.views import google_verificacion


urlpatterns = [
    path("admin/", admin.site.urls),
    path("usuarios/", include("app_usuarios.urls")),

    # 👇 Redirección: raíz (/) → login
    path("", lambda request: redirect("login")),
    path("google59c38f56bef2f608.html", google_verificacion, name="google_verificacion"),

   
]



