from django.core.management.base import BaseCommand
from inscricoes.models import Turma

class Command(BaseCommand):
    help = 'Reseta o número de vagas para todas as turmas para o valor padrão (30)'

    def handle(self, *args, **options):
        turmas = Turma.objects.all()
        count = 0
        
        for turma in turmas:
            turma.vagas = 30
            turma.save()
            count += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully reset vagas for {count} turmas')
        ) 