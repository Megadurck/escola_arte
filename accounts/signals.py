from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib.auth import logout

@receiver(user_logged_out)
def handle_logout(sender, request, user, **kwargs):
    # Verifique se o usuário é admin e faça logout
    if request.user.is_superuser:
        # Marcar a sessão de admin com uma chave específica
        request.session['admin_logged_out'] = True
