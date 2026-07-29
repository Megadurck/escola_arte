from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Inscricao, Curso, Turma, InscricaoTurma
from .forms import InscricaoForm
from django.db.models import Sum, Count, Prefetch
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.conf import settings
from django.views.decorators.cache import never_cache
import re


def _ano_letivo_atual():
    return int(getattr(settings, 'ANO_LETIVO_ATUAL'))


def _chave_turma_logica(turma):
    return (
        turma.curso_id,
        turma.ano_letivo,
        (turma.nome or '').strip().lower(),
        turma.horario_inicio,
        turma.horario_fim,
    )

@never_cache
def inscrever(request):
    inscricoes_abertas = getattr(settings, 'INSCRICOES_ABERTAS', False)
    ano_letivo_atual = _ano_letivo_atual()
    if not inscricoes_abertas:
        return HttpResponseForbidden("As inscrições estão encerradas.")
    inscricao_existente = False
        
    if request.method == 'POST':
        # Processa turmas enviadas (campo oculto e fallback para checkboxes)
        turmas_raw = request.POST.get('turmas_selecionadas', '')
        turmas_ids = [int(id) for id in turmas_raw.split(',') if id.isdigit()]

        if not turmas_ids:
            turmas_ids = [int(id) for id in request.POST.getlist('turmas') if str(id).isdigit()]

        post_data = request.POST.copy()

        # Normaliza campos mascarados antes da validação do formulário.
        if 'cpf' in post_data:
            post_data['cpf'] = re.sub(r'\D', '', post_data.get('cpf', ''))
        if 'telefone_whatsapp' in post_data:
            post_data['telefone_whatsapp'] = re.sub(r'\D', '', post_data.get('telefone_whatsapp', ''))

        # Garante consistência: se veio turma, injeta o(s) curso(s) correspondente(s).
        if turmas_ids:
            cursos_ids = list(
                Turma.objects.filter(id__in=turmas_ids, ano_letivo=ano_letivo_atual)
                .values_list('curso_id', flat=True)
                .distinct()
            )
            if cursos_ids:
                post_data.setlist('cursos', [str(curso_id) for curso_id in cursos_ids])

        cpf_normalizado = post_data.get('cpf', '')
        inscricao_existente_mesmo_ano = None
        inscricao_sem_turma = False

        if len(cpf_normalizado) == 11:
            inscricao_existente_mesmo_ano = Inscricao.objects.filter(
                cpf=cpf_normalizado,
                ano_letivo=ano_letivo_atual,
            ).first()
            inscricao_sem_turma = (
                inscricao_existente_mesmo_ano is not None
                and not inscricao_existente_mesmo_ano.inscricaoturma_set.exists()
            )

        if inscricao_sem_turma:
            form = InscricaoForm(post_data, instance=inscricao_existente_mesmo_ano)
        else:
            form = InscricaoForm(post_data)
        
        # Verifica se pelo menos uma turma foi selecionada
        if not turmas_ids:
            messages.error(request, 'Você deve selecionar pelo menos uma turma para se inscrever.')
            return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})
        
        # Atualiza o queryset do campo turmas com as turmas selecionadas
        form.fields['turmas'].queryset = Turma.objects.filter(id__in=turmas_ids, ano_letivo=ano_letivo_atual)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    inscricao = form.save(commit=False)
                    inscricao.ano_letivo = ano_letivo_atual
                    if request.user.is_authenticated:
                        inscricao.usuario = request.user
                    inscricao.save()

                    if inscricao_sem_turma:
                        InscricaoTurma.objects.filter(inscricao=inscricao).delete()

                    turmas_qs = Turma.objects.filter(
                        id__in=set(turmas_ids),
                        ano_letivo=ano_letivo_atual,
                    )
                    turmas_por_id = {turma.id: turma for turma in turmas_qs}
                    ids_invalidos = set(turmas_ids) - set(turmas_por_id.keys())

                    if ids_invalidos:
                        raise ValidationError('Uma ou mais turmas selecionadas não são mais válidas. Atualize a página e tente novamente.')

                    turmas_logicas = {}
                    for turma_id in set(turmas_ids):
                        turma = turmas_por_id[turma_id]
                        chave_logica = _chave_turma_logica(turma)
                        turma_atual = turmas_logicas.get(chave_logica)
                        if turma_atual is None or turma.id < turma_atual.id:
                            turmas_logicas[chave_logica] = turma

                    for turma in turmas_logicas.values():
                        InscricaoTurma.objects.create(inscricao=inscricao, turma=turma)
            except ValidationError as e:
                messages.error(request, f'Erro ao inscrever em uma turma: {e}')
                return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})
            except IntegrityError:
                messages.error(request, 'CPF já cadastrado para este ano letivo. Verifique seus dados.')
                return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})
            except Exception:
                messages.error(request, 'Ocorreu um erro ao processar a inscrição. Tente novamente em instantes.')
                return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})

            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('inscricoes:pagina_inicial')
        else:
            primeiro_erro = None
            for erros_campo in form.errors.values():
                if erros_campo:
                    primeiro_erro = erros_campo[0]
                    break

            messages.error(request, primeiro_erro or 'Não foi possível finalizar a inscrição. Revise os campos e tente novamente.')
    else:
        form = InscricaoForm()
    return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    ano_letivo_atual = _ano_letivo_atual()
    ano_param = request.GET.get('ano', str(ano_letivo_atual))
    try:
        ano_selecionado = int(ano_param)
    except (TypeError, ValueError):
        ano_selecionado = ano_letivo_atual

    anos_inscricoes = Inscricao.objects.values_list('ano_letivo', flat=True).distinct()
    anos_turmas = Turma.objects.values_list('ano_letivo', flat=True).distinct()
    anos_disponiveis = sorted({*anos_inscricoes, *anos_turmas, ano_letivo_atual}, reverse=True)

    turmas_do_ano = (
        Turma.objects.filter(ano_letivo=ano_selecionado)
        .select_related('curso')
        .annotate(inscritos_total=Count('inscricaoturma'))
        .order_by('curso__nome', 'nome', 'horario_inicio')
    )

    inscricoes = (
        Inscricao.objects.filter(ano_letivo=ano_selecionado)
        .prefetch_related(
            Prefetch(
                'turmas',
                queryset=Turma.objects.select_related('curso').filter(ano_letivo=ano_selecionado),
            )
        )
        .order_by('-data_inscricao')
    )

    total_inscricoes = inscricoes.count()
    total_turmas = turmas_do_ano.count()
    total_cursos = turmas_do_ano.values('curso_id').distinct().count()

    agregados_por_curso = {}
    inscricoes_unicas_por_curso = {
        item['turma__curso__nome']: item['total']
        for item in (
            InscricaoTurma.objects
            .filter(turma__ano_letivo=ano_selecionado)
            .values('turma__curso__nome')
            .annotate(total=Count('inscricao_id', distinct=True))
        )
    }
    total_vagas = 0
    for turma in turmas_do_ano:
        curso_nome = turma.curso.nome
        vagas_disponiveis = max(0, turma.vagas_originais - turma.inscritos_total)
        total_vagas += vagas_disponiveis

        if curso_nome not in agregados_por_curso:
            agregados_por_curso[curso_nome] = {
                'inscricoes': 0,
                'vagas': 0,
            }

        agregados_por_curso[curso_nome]['inscricoes'] += turma.inscritos_total
        agregados_por_curso[curso_nome]['vagas'] += vagas_disponiveis

    inscricoes_por_curso = [
        {'curso': curso_nome, 'total': inscricoes_unicas_por_curso.get(curso_nome, 0)}
        for curso_nome, dados in sorted(agregados_por_curso.items(), key=lambda item: item[0])
    ]

    vagas_por_curso = [
        {'curso': curso_nome, 'vagas': dados['vagas']}
        for curso_nome, dados in sorted(agregados_por_curso.items(), key=lambda item: item[0])
    ]

    context = {
        'inscricoes': inscricoes,
        'ano_selecionado': ano_selecionado,
        'anos_disponiveis': anos_disponiveis,
        'total_inscricoes': total_inscricoes,
        'total_vagas': total_vagas,
        'total_cursos': total_cursos,
        'total_turmas': total_turmas,
        'inscricoes_por_curso': inscricoes_por_curso,
        'vagas_por_curso': vagas_por_curso,
    }
    return render(request, 'inscricoes/dashboard.html', context)

def get_turmas(request):
    ano_letivo_atual = _ano_letivo_atual()
    curso_ids = request.GET.get('curso_id', '').split(',')
    curso_ids = [int(id) for id in curso_ids if id.isdigit()]

    if not curso_ids:
        return JsonResponse({'turmas': []})

    turmas = (
        Turma.objects
        .filter(curso_id__in=curso_ids, ano_letivo=ano_letivo_atual)
        .select_related('curso')
        .prefetch_related('encontros')
        .only(
            'id',
            'curso_id',
            'nome',
            'dia_semana',
            'horario_inicio',
            'horario_fim',
            'vagas_originais',
            'curso__nome',
        )
        .annotate(inscritos_count=Count('inscricaoturma'))
        .order_by('curso__nome', 'nome', 'horario_inicio', 'horario_fim', 'dia_semana')
    )
    turmas_agrupadas = {}
    ordem_dias = {
        'Segunda-feira': 1,
        'Terça-feira': 2,
        'Quarta-feira': 3,
        'Quinta-feira': 4,
        'Sexta-feira': 5,
        'Sábado': 6,
        'Domingo': 7,
    }

    for turma in turmas:
        vagas_disponiveis = max(0, turma.vagas_originais - turma.inscritos_count)
        if vagas_disponiveis <= 0:
            continue

        encontros = list(turma.encontros.all())
        dias_turma = [encontro.dia_semana for encontro in encontros] if encontros else [turma.dia_semana]

        chave = (turma.curso_id, turma.nome, turma.horario_inicio, turma.horario_fim)
        if chave not in turmas_agrupadas:
            turmas_agrupadas[chave] = {
                'id': turma.id,
                'ids': [turma.id],
                'nome': turma.nome,
                'dias': list(dias_turma),
                'horario_inicio': turma.horario_inicio.strftime('%H:%M'),
                'horario_fim': turma.horario_fim.strftime('%H:%M'),
                'vagas_disponiveis': vagas_disponiveis,
                'curso_id': turma.curso_id,
                'curso_nome': turma.curso.nome,
            }
        else:
            grupo = turmas_agrupadas[chave]
            grupo['ids'].append(turma.id)
            grupo['dias'].extend(dias_turma)
            grupo['vagas_disponiveis'] = min(grupo['vagas_disponiveis'], vagas_disponiveis)

    turmas_data = []
    for grupo in turmas_agrupadas.values():
        dias_ordenados = sorted(
            set(grupo['dias']),
            key=lambda dia: ordem_dias.get(dia, 99)
        )

        curso_normalizado = (grupo['curso_nome'] or '').lower()
        if (
            'ballet' in curso_normalizado
            or 'bale' in curso_normalizado
            or 'balé' in curso_normalizado
        ):
            dias_ordenados = ['Terça-feira', 'Quarta-feira']

        turmas_data.append({
            'id': grupo['id'],
            'ids': grupo['ids'],
            'nome': grupo['nome'],
            'dia_semana': ', '.join(dias_ordenados),
            'horario_inicio': grupo['horario_inicio'],
            'horario_fim': grupo['horario_fim'],
            'vagas_disponiveis': grupo['vagas_disponiveis'],
            'curso_id': grupo['curso_id'],
            'curso_nome': grupo['curso_nome'],
        })

    turmas_data.sort(
        key=lambda turma: (
            turma['curso_nome'],
            turma['nome'],
            turma['horario_inicio'],
            turma['horario_fim'],
        )
    )

    return JsonResponse({'turmas': turmas_data})


@never_cache
def pagina_inicial(request):
    cursos = Curso.objects.all()
    inscricoes_abertas = getattr(settings, 'INSCRICOES_ABERTAS', False)

    return render(request, 'inscricoes/pagina_inicial.html', {'cursos': cursos, 'inscricoes_abertas': inscricoes_abertas})

