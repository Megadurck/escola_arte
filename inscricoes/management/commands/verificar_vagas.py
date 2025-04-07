from django.core.management.base import BaseCommand
from inscricoes.models import Turma, InscricaoTurma

class Command(BaseCommand):
    help = 'Verifica e corrige o contador de vagas para todas as turmas'

    def handle(self, *args, **options):
        # Busca todas as turmas
        turmas = Turma.objects.all()
        turmas_corrigidas = 0
        
        for turma in turmas:
            # Conta o número real de inscritos
            inscritos_count = InscricaoTurma.objects.filter(turma=turma).count()
            
            # Calcula o número correto de vagas disponíveis
            # Usa o valor original de vagas da turma
            vagas_originais = turma.vagas_originais
            vagas_disponiveis = vagas_originais - inscritos_count
            
            # Verifica se o contador de vagas está correto
            if turma.vagas != vagas_disponiveis:
                turma.vagas = vagas_disponiveis
                turma.save()
                turmas_corrigidas += 1
                
                self.stdout.write(
                    self.style.WARNING(
                        f'Turma {turma.nome} ({turma.curso.nome}): Vagas corrigidas de {turma.vagas} para {vagas_disponiveis}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Turma {turma.nome} ({turma.curso.nome}): Vagas corretas ({turma.vagas})'
                    )
                )
        
        if turmas_corrigidas > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Total de {turmas_corrigidas} turmas tiveram o contador de vagas corrigido.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Nenhuma turma precisou ter o contador de vagas corrigido.'
                )
            ) 