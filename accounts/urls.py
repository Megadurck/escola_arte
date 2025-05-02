from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

# Adicionando o app_name
# app_name = 'accounts'

urlpatterns = [
    # Login, Logout
    path('login/', views.user_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    
     # URLs para o processo de reset de senha
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    
    # Corrigido: define explicitamente o template do usuário comum
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
