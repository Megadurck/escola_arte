from django.core.management.base import BaseCommand
from inscricoes.models import Inscricao, InscricaoTurma

class Command(BaseCommand):
    help = 'Verifica as inscrições e suas turmas associadas'

    def handle(self, *args, **options):
        # Busca todas as inscrições
        inscricoes = Inscricao.objects.all()
        
        for inscricao in inscricoes:
            # Busca as turmas associadas à inscrição
            inscricoes_turma = InscricaoTurma.objects.filter(inscricao=inscricao)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Inscrição: {inscricao.nome_completo} (CPF: {inscricao.cpf})'
                )
            )
            
            if inscricoes_turma.exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Turmas associadas: {inscricoes_turma.count()}'
                    )
                )
                
                for inscricao_turma in inscricoes_turma:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    - {inscricao_turma.turma.curso.nome} - {inscricao_turma.turma.nome}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Nenhuma turma associada!'
                    )
                )
            
            # Verifica se há turmas selecionadas no formulário
            turmas_selecionadas = inscricao.turmas.all()
            if turmas_selecionadas.exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  Turmas selecionadas no formulário: {turmas_selecionadas.count()}'
                    )
                )
                
                for turma in turmas_selecionadas:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    - {turma.curso.nome} - {turma.nome}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Nenhuma turma selecionada no formulário!'
                    )
                )
            
            self.stdout.write('') 