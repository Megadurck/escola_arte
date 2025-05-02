from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inscricoes/', include('inscricoes.urls')),

    # Redireciona a raiz para o login com next apontando para a página inicial
    path('', lambda request: redirect('/login/?next=/inscricoes/'), name='pagina_inicial'),

    # Login padrão com template personalizado
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
]
