# inscricoes/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views  # Certifique-se de que as views estão sendo importadas

app_name = 'inscricoes'  # Adicione isso para definir o namespace

urlpatterns = [
    path('', views.pagina_inicial, name='pagina_inicial'),
    path('inscrever/', views.inscrever, name='inscrever'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('get-horarios/<int:curso_id>/', views.get_horarios_curso, name='get_horarios_curso'),
    path('logout/', views.logout_view, name='logout'),
]
