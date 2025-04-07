from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Inscricao, InscricaoTurma

# Sinais para atualizar o contador de vagas
@receiver(post_save, sender=InscricaoTurma)
def atualizar_vagas_apos_salvar(sender, instance, created, **kwargs):
    if created:  # Se for uma nova inscrição
        turma = instance.turma
        turma.vagas = turma.vagas - 1
        turma.save()
        print(f"Vagas atualizadas após salvar: {turma.vagas}")

@receiver(post_delete, sender=InscricaoTurma)
def atualizar_vagas_apos_deletar(sender, instance, **kwargs):
    turma = instance.turma
    turma.vagas = turma.vagas + 1
    turma.save()
    print(f"Vagas atualizadas após deletar: {turma.vagas}")

# Sinal para atualizar o contador de vagas quando uma inscrição é deletada
@receiver(post_delete, sender=Inscricao)
def atualizar_vagas_apos_deletar_inscricao(sender, instance, **kwargs):
    # Obtém todas as turmas associadas à inscrição
    inscricoes_turma = InscricaoTurma.objects.filter(inscricao=instance)
    
    # Atualiza o contador de vagas para cada turma
    for inscricao_turma in inscricoes_turma:
        turma = inscricao_turma.turma
        turma.vagas = turma.vagas + 1
        turma.save()
        print(f"Vagas atualizadas após deletar inscrição: {turma.vagas}") 