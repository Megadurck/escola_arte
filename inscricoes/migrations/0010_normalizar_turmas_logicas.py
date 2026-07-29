from django.db import migrations


def normalizar_turmas_logicas(apps, schema_editor):
    Turma = apps.get_model('inscricoes', 'Turma')
    InscricaoTurma = apps.get_model('inscricoes', 'InscricaoTurma')
    EncontroTurma = apps.get_model('inscricoes', 'EncontroTurma')

    turmas = list(
        Turma.objects.all().order_by('curso_id', 'ano_letivo', 'nome', 'horario_inicio', 'id')
    )

    grupos = {}
    for turma in turmas:
        chave = (
            turma.curso_id,
            turma.ano_letivo,
            (turma.nome or '').strip().lower(),
            turma.horario_inicio,
            turma.horario_fim,
        )
        grupos.setdefault(chave, []).append(turma.id)

    for ids_grupo in grupos.values():
        if len(ids_grupo) <= 1:
            continue

        ids_grupo = sorted(ids_grupo)
        principal_id = ids_grupo[0]
        secundarios_ids = ids_grupo[1:]

        turmas_grupo = list(Turma.objects.filter(id__in=ids_grupo))

        for turma_origem in turmas_grupo:
            EncontroTurma.objects.get_or_create(
                turma_id=principal_id,
                dia_semana=turma_origem.dia_semana,
                horario_inicio=turma_origem.horario_inicio,
                horario_fim=turma_origem.horario_fim,
            )

        inscritos_principal = set(
            InscricaoTurma.objects.filter(turma_id=principal_id)
            .values_list('inscricao_id', flat=True)
        )

        relacoes_secundarias = list(
            InscricaoTurma.objects.filter(turma_id__in=secundarios_ids).order_by('id')
        )
        for rel in relacoes_secundarias:
            if rel.inscricao_id not in inscritos_principal:
                InscricaoTurma.objects.create(
                    inscricao_id=rel.inscricao_id,
                    turma_id=principal_id,
                )
                inscritos_principal.add(rel.inscricao_id)
            rel.delete()

        principal = Turma.objects.get(id=principal_id)
        vagas_originais_grupo = max(t.vagas_originais for t in turmas_grupo)
        principal.vagas_originais = vagas_originais_grupo
        inscritos_count = InscricaoTurma.objects.filter(turma_id=principal_id).count()
        principal.vagas = max(0, vagas_originais_grupo - inscritos_count)
        principal.save(update_fields=['vagas_originais', 'vagas'])

        Turma.objects.filter(id__in=secundarios_ids).delete()

    # Garante que toda turma restante tenha ao menos um encontro registrado.
    for turma in Turma.objects.all().iterator():
        if not EncontroTurma.objects.filter(turma_id=turma.id).exists():
            EncontroTurma.objects.create(
                turma_id=turma.id,
                dia_semana=turma.dia_semana,
                horario_inicio=turma.horario_inicio,
                horario_fim=turma.horario_fim,
            )

    # Recalcula o contador de vagas de todas as turmas.
    for turma in Turma.objects.all().iterator():
        inscritos = InscricaoTurma.objects.filter(turma_id=turma.id).count()
        vagas_disponiveis = max(0, turma.vagas_originais - inscritos)
        if turma.vagas != vagas_disponiveis:
            turma.vagas = vagas_disponiveis
            turma.save(update_fields=['vagas'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('inscricoes', '0009_encontroturma'),
    ]

    operations = [
        migrations.RunPython(normalizar_turmas_logicas, noop_reverse),
    ]
