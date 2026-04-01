from django.urls import path
from .views import pagina_inicial, inscrever, dashboard, get_turmas

app_name = 'inscricoes'

urlpatterns = [
    path('', pagina_inicial, name='pagina_inicial'),
    path('inscrever/', inscrever, name='inscrever'),
    path('dashboard/', dashboard, name='dashboard'),
    path('get_turmas/', get_turmas, name='get_turmas'),
]
