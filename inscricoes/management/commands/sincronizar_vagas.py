from django.core.management.base import BaseCommand
from inscricoes.models import Turma

class Command(BaseCommand):
    help = 'Sincroniza o número de vagas com o número real de inscritos em cada turma'

    def handle(self, *args, **options):
        turmas = Turma.objects.all()
        count = 0
        
        for turma in turmas:
            # Força a atualização das vagas usando o método vagas_disponiveis
            vagas_disponiveis = turma.vagas_disponiveis()
            
            if turma.vagas != vagas_disponiveis:
                turma.vagas = vagas_disponiveis
                turma.save()
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Turma {turma.nome} ({turma.curso.nome}): Vagas atualizadas de {turma.vagas} para {vagas_disponiveis}')
                )
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully synchronized vagas for {count} turmas')
        ) 