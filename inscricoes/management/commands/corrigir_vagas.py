from django.core.management.base import BaseCommand
from inscricoes.models import Turma, InscricaoTurma

class Command(BaseCommand):
    help = 'Corrige o contador de vagas para todas as turmas'

    def handle(self, *args, **options):
        turmas = Turma.objects.all()
        count = 0
        
        for turma in turmas:
            # Conta o número real de inscritos
            inscritos_count = InscricaoTurma.objects.filter(turma=turma).count()
            
            # Calcula o número correto de vagas disponíveis
            vagas_originais = 30  # Valor padrão de vagas
            vagas_disponiveis = vagas_originais - inscritos_count
            
            # Atualiza o número de vagas
            turma.vagas = vagas_disponiveis
            turma.save()
            count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Turma {turma.nome} ({turma.curso.nome}): Vagas atualizadas para {vagas_disponiveis}')
            )
            
        self.stdout.write(
            self.style.SUCCESS(f'Correção concluída. {count} turmas foram atualizadas.')
        ) 