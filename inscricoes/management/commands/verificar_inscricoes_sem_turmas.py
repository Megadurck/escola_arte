from django.core.management.base import BaseCommand
from inscricoes.models import Inscricao, InscricaoTurma

class Command(BaseCommand):
    help = 'Verifica e corrige inscrições sem turmas'

    def handle(self, *args, **options):
        # Busca todas as inscrições
        inscricoes = Inscricao.objects.all()
        inscricoes_sem_turmas = []
        
        for inscricao in inscricoes:
            # Verifica se a inscrição tem turmas associadas
            turmas_associadas = InscricaoTurma.objects.filter(inscricao=inscricao).count()
            
            if turmas_associadas == 0:
                inscricoes_sem_turmas.append(inscricao)
                self.stdout.write(
                    self.style.WARNING(
                        f'Inscrição sem turmas encontrada: {inscricao.nome_completo} (CPF: {inscricao.cpf})'
                    )
                )
        
        if inscricoes_sem_turmas:
            self.stdout.write(
                self.style.WARNING(
                    f'Total de {len(inscricoes_sem_turmas)} inscrições sem turmas encontradas.'
                )
            )
            
            # Pergunta se deseja remover as inscrições sem turmas
            resposta = input('Deseja remover as inscrições sem turmas? (s/n): ')
            
            if resposta.lower() == 's':
                for inscricao in inscricoes_sem_turmas:
                    inscricao.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Inscrição removida: {inscricao.nome_completo} (CPF: {inscricao.cpf})'
                        )
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Total de {len(inscricoes_sem_turmas)} inscrições sem turmas foram removidas.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        'Nenhuma inscrição foi removida.'
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Nenhuma inscrição sem turmas encontrada.'
                )
            ) 