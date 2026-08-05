from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated and not request.user.is_superuser:
            logout(request)
            return redirect('/accounts/login/')
        response = self.get_response(request)
        return response

class CustomSessionMiddleware:
    """Reforça a expiração da sessão para as rotas administrativas."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return self.get_response(request)
