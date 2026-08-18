from django.urls import path
from .views import (
    pagina_inicial,
    inscrever,
    dashboard,
    get_turmas,
    transparencia,
    documento_transparencia_preview,
    documento_transparencia_arquivo,
)

app_name = 'inscricoes'

urlpatterns = [
    path('', pagina_inicial, name='pagina_inicial'),
    path('inscrever/', inscrever, name='inscrever'),
    path('dashboard/', dashboard, name='dashboard'),
    path('get_turmas/', get_turmas, name='get_turmas'),
    path('transparencia/', transparencia, name='transparencia'),
    path('transparencia/preview/<int:pk>/', documento_transparencia_preview, name='documento_transparencia_preview'),
    path('transparencia/documento/<int:pk>/', documento_transparencia_arquivo, name='documento_transparencia_arquivo'),
]
