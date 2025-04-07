from django.core.management.base import BaseCommand
from inscricoes.models import Inscricao, Turma, InscricaoTurma
from django.db.models import Count

class Command(BaseCommand):
    help = 'Verifica e corrige as relações entre inscrições e turmas'

    def handle(self, *args, **options):
        # Verifica se há inscrições sem turmas
        inscricoes_sem_turmas = Inscricao.objects.filter(turmas__isnull=True)
        if inscricoes_sem_turmas.exists():
            self.stdout.write(
                self.style.WARNING(f'Encontradas {inscricoes_sem_turmas.count()} inscrições sem turmas')
            )
        
        # Verifica se há turmas sem inscritos
        turmas_sem_inscritos = Turma.objects.filter(inscricaoturma__isnull=True)
        if turmas_sem_inscritos.exists():
            self.stdout.write(
                self.style.WARNING(f'Encontradas {turmas_sem_inscritos.count()} turmas sem inscritos')
            )
        
        # Verifica se há inscrições com turmas duplicadas
        inscricoes_duplicadas = InscricaoTurma.objects.values('inscricao', 'turma').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if inscricoes_duplicadas.exists():
            self.stdout.write(
                self.style.WARNING(f'Encontradas {inscricoes_duplicadas.count()} relações duplicadas entre inscrições e turmas')
            )
            
            # Corrige as relações duplicadas
            for relacao in inscricoes_duplicadas:
                inscricao_id = relacao['inscricao']
                turma_id = relacao['turma']
                
                # Mantém apenas uma relação
                inscricoes_turma = InscricaoTurma.objects.filter(
                    inscricao_id=inscricao_id,
                    turma_id=turma_id
                ).order_by('data_inscricao')
                
                # Mantém a primeira relação e remove as demais
                primeira_relacao = inscricoes_turma.first()
                inscricoes_turma.exclude(id=primeira_relacao.id).delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Corrigida relação duplicada: Inscrição {inscricao_id} - Turma {turma_id}')
                )
        
        # Verifica se o contador de vagas está correto
        turmas = Turma.objects.all()
        count = 0
        
        for turma in turmas:
            # Conta o número real de inscritos
            inscritos_count = InscricaoTurma.objects.filter(turma=turma).count()
            
            # Calcula o número correto de vagas disponíveis
            vagas_originais = 30  # Valor padrão de vagas
            vagas_disponiveis = vagas_originais - inscritos_count
            
            # Verifica se o número de vagas está correto
            if turma.vagas != vagas_disponiveis:
                self.stdout.write(
                    self.style.WARNING(f'Turma {turma.nome} ({turma.curso.nome}): Vagas incorretas. Atual: {turma.vagas}, Correto: {vagas_disponiveis}')
                )
                
                # Corrige o número de vagas
                turma.vagas = vagas_disponiveis
                turma.save()
                count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Turma {turma.nome} ({turma.curso.nome}): Vagas corrigidas para {vagas_disponiveis}')
                )
            
        self.stdout.write(
            self.style.SUCCESS(f'Verificação concluída. {count} turmas foram corrigidas.')
        ) 