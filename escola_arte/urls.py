from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inscricoes/', include('inscricoes.urls')),

    # Redireciona a raiz para o login com next apontando para a página inicial
    path('', lambda request: redirect('/accounts/login/?next=/inscricoes/'), name='pagina_inicial'),

    # Rota legada para manter compatibilidade de links antigos
    path('login/', lambda request: redirect('/accounts/login/')),
]
