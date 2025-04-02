from django.urls import path
from .views import pagina_inicial, inscrever, dashboard, get_horarios_curso, logout_view

app_name = 'inscricoes'

urlpatterns = [
    path('', pagina_inicial, name='pagina_inicial'),
    path('inscrever/', inscrever, name='inscrever'),
    path('dashboard/', dashboard, name='dashboard'),
    path('get-horarios-curso/', get_horarios_curso, name='get_horarios_curso'),
    path('logout/', logout_view, name='logout'),
]
