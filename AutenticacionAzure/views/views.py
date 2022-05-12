from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.contrib import messages

from AutenticacionAzure.views import app_config
from AutenticacionAzure.views.app import _build_auth_code_flow


class AuthAbsView(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.session.get("user"):
            return redirect(reverse('inicio-sesion'))
        if not self.request.user.is_authenticated:
            validar_autenticacion_local(self.request)
        return super(AuthAbsView, self).dispatch(*args, **kwargs)


class IndexView(AuthAbsView):
    def get(self, request):
        return render(request, 'Plantilla/index.html')


class InicioSesionView(View):
    def get(self, request):
        validar_autenticacion_local(self.request)
        request.session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
        return render(request, 'Plantilla/inicio_sesion.html',
                      {'auth_url': request.session["flow"]["auth_uri"]})


class CierreSesion(View):
    def get(self, request):
        logout(request)
        request.session.clear()
        messages.success(request, 'Se ha cerrado la sesión')
        return redirect(app_config.AUTHORITY + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" +
                        'http://127.0.0.1:8000')


def crear_usuario(usuario):
    usr = usuario['preferred_username'].split('@')[0]
    nombre_completo = usuario['name'].split(' ')
    if len(nombre_completo) == 3:
        nombre = nombre_completo[0]
        apellido = '{0} {1}'.format(nombre_completo[1], nombre_completo[2])

    elif len(nombre_completo) == 2:
        nombre = nombre_completo[0]
        apellido = nombre_completo[1]
    else:
        nombre = '{0} {1}'.format(nombre_completo[0], nombre_completo[1])
        apellido = '{0} {1}'.format(nombre_completo[2], nombre_completo[3])

    return User.objects.create_user(username=usr, password='PssWrd.2019*', first_name=nombre, last_name=apellido,
                                    email=usuario['preferred_username'])


def autenticar_usuario(request, usuario):
    user = authenticate(username=usuario, password="PssWrd.2019*")
    if user is not None:
        login(request, user)
    return user


def validar_autenticacion_local(request):
    usuario = request.session.get("user")
    if not request.user.is_authenticated and usuario:
        if User.objects.filter(email=usuario['preferred_username']):
            autenticar_usuario(request, usuario['preferred_username'].split('@')[0])
        else:
            usr = crear_usuario(usuario)
            autenticar_usuario(request, usr)
