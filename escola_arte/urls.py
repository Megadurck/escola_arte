from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adicione o namespace 'escola_arte' na URL de 'accounts'
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('inscricoes/', include('inscricoes.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Incluindo as URLs padrão de auth

]
