import json
import uuid
import requests
from django.shortcuts import redirect, render
from django.urls import reverse
# from flask import Flask, render_template, session, request, redirect, url_for
# from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
from django.views import View

# app = Flask(__name__)
# app.config.from_object(app_config)
# Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
# from werkzeug.middleware.proxy_fix import ProxyFix
# SIGPA.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# @app.route("/")
# def index():
#     if not session.get("user"):
#         return redirect(url_for("login"))
#     return render_template('index.html', user=session["user"], version=msal.__version__)

# @app.route("/login")
# def login():
#     # Technically we could use empty list [] as scopes to do just sign in,
#     # here we choose to also collect end user consent upfront
#     session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
#     return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

# @app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
from AutenticacionAzure.views import app_config


class AutorizacionAzure(View):
    def get(self, request):
        try:
            cache = _load_cache(request)
            result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
                request.session.get("flow", {}), request.GET)
            print(result)
            if "error" in result:
                return render(request, '')
            request.session["user"] = result.get("id_token_claims")
            _save_cache(request, cache)
        except Exception as e:
            print(e)
            pass
        return redirect(reverse('index'))


class CerrarSesionAzure(View):
    def get(self, request):
        request.session.clear()
        return redirect(app_config.AUTHORITY + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" +
                        reverse('index'))


class GraphcallAzure(View):
    def get(self, request):
        token = _get_token_from_cache(request, app_config.SCOPE)
        if not token:
            return redirect(reverse('Administracion:inicio-sesion'))
        graph_data = requests.get(
            app_config.ENDPOINT,
            headers={'Authorization': 'Bearer ' + token['access_token']},
            ).json()
        return render(request, 'Autenticacion/display.html', {'result': graph_data})


def _load_cache(request):
    cache = msal.SerializableTokenCache()
    if request.session.get("token_cache"):
        cache.deserialize(request.session["token_cache"])
    return cache


def _save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri='http://localhost:8000/getAToken')


def _get_token_from_cache(request, scope=None):
    cache = _load_cache(request)  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(request, cache)
        return result

# app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template
#
# if __name__ == "__main__":
#     app.run()

