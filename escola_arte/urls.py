from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),  # Personalize suas URLs de autenticação aqui
    path('inscricoes/', include('inscricoes.urls')),
]
