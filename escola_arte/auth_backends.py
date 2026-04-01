from django.contrib.auth.backends import ModelBackend

class AdminBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and user.is_superuser:
            return user
        return None

    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_superuser
