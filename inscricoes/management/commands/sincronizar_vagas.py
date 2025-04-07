from django.core.management.base import BaseCommand
from inscricoes.models import Turma

class Command(BaseCommand):
    help = 'Sincroniza o número de vagas com o número real de inscritos em cada turma'

    def handle(self, *args, **options):
        turmas = Turma.objects.all()
        count = 0
        
        for turma in turmas:
            inscritos_count = turma.inscricaoturma_set.count()
            vagas_originais = 30  # Valor padrão de vagas
            vagas_disponiveis = vagas_originais - inscritos_count
            
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