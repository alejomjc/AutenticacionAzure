"""AutenticacionAzure URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from AutenticacionAzure.views import app, app_config, views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('iniciar-sesion', views.InicioSesionView.as_view(), name='inicio-sesion'),
    path('cerrar-sesion', views.CierreSesion.as_view(), name='cierre-sesion'),
    path(app_config.REDIRECT_PATH, app.AutorizacionAzure.as_view(), name='autorizacion-azure'),
]
