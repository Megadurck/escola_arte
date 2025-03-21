from django.contrib.auth.models import Group
from django.db import models

class MyModel(models.Model):
    # Defina seus campos aqui

    @staticmethod
    def create_default_group():
        # Este método pode ser chamado quando necessário, e não no momento da inicialização
        Group.objects.get_or_create(name='Usuários Comuns')
