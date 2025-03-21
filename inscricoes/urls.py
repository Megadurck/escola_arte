# inscricoes/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views  # Certifique-se de que as views estão sendo importadas

app_name = 'inscricoes'  # Adicione isso para definir o namespace

urlpatterns = [
    path('pagina-inicial/', views.pagina_inicial, name='pagina_inicial'),
    path('inscrever/', views.inscrever, name='inscrever'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
]
