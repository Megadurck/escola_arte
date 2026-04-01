from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def superuser_admin_only(request):
    return request.user.is_active and request.user.is_superuser


admin.site.has_permission = superuser_admin_only

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inscricoes/', include('inscricoes.urls')),

    # Fluxo público principal
    path('', lambda request: redirect('/inscricoes/'), name='pagina_inicial'),

    # Rota legada para manter compatibilidade de links antigos
    path('login/', lambda request: redirect('/accounts/login/')),
]
