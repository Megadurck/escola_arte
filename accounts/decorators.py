from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Acesso negado. Você precisa ser um administrador.')
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view