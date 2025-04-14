from django.urls import path
from . import views

# Adicionando o app_name
app_name = 'accounts'

urlpatterns = [
    # Login, Logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
]
