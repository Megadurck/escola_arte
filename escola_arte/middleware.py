from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated and not request.user.is_staff:
            logout(request)
            return redirect('/accounts/login/')
        response = self.get_response(request)
        return response

class CustomSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            request.session.set_expiry(0)  # Expira a sessão quando o navegador é fechado
            request.session[settings.SESSION_COOKIE_NAME] = settings.ADMIN_SESSION_COOKIE_NAME
            request.META['CSRF_COOKIE'] = settings.ADMIN_CSRF_COOKIE_NAME
        else:
            request.session[settings.SESSION_COOKIE_NAME] = settings.SESSION_COOKIE_NAME
            request.META['CSRF_COOKIE'] = settings.CSRF_COOKIE_NAME
        response = self.get_response(request)
        return response
