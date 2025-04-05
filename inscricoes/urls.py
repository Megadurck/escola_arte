from django.urls import path
from .views import pagina_inicial, inscrever, dashboard, logout_view, get_turmas, register

app_name = 'inscricoes'

urlpatterns = [
    path('', pagina_inicial, name='pagina_inicial'),
    path('inscrever/', inscrever, name='inscrever'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('get_turmas/', get_turmas, name='get_turmas'),
]
