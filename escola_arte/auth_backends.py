from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class AdminBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return super().user_can_authenticate(user) and user.is_superuser
