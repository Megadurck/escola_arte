from django.core.management.base import BaseCommand
from inscricoes.models import Inscricao

class Command(BaseCommand):
    help = 'Remove a inscrição do Auan Vasconcelos'

    def handle(self, *args, **options):
        try:
            inscricao = Inscricao.objects.get(cpf='32165498700')
            inscricao.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    'Inscrição do Auan Vasconcelos removida com sucesso!'
                )
            )
        except Inscricao.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    'Inscrição do Auan Vasconcelos não encontrada.'
                )
            ) 