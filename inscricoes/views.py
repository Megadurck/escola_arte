from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Inscricao, Curso, Turma, InscricaoTurma
from .forms import InscricaoForm
from django.db.models import Sum
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.conf import settings
import re


def _ano_letivo_atual():
    return int(getattr(settings, 'ANO_LETIVO_ATUAL'))

def inscrever(request):
    inscricoes_abertas = getattr(settings, 'INSCRICOES_ABERTAS', False)
    ano_letivo_atual = _ano_letivo_atual()
    if not inscricoes_abertas:
        return HttpResponseForbidden("As inscrições estão encerradas.")
    # Mantém a regra atual para usuários autenticados, sem exigir login no fluxo público
    inscricao_existente = False
    if request.user.is_authenticated:
        inscricao_existente = Inscricao.objects.filter(usuario=request.user, ano_letivo=ano_letivo_atual).exists()
    
    if inscricao_existente:
        messages.warning(request, 'Você já possui uma inscrição!')
        return redirect('inscricoes:pagina_inicial')
        
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

                    turmas_qs = Turma.objects.filter(
                        id__in=set(turmas_ids),
                        ano_letivo=ano_letivo_atual,
                    )
                    turmas_por_id = {turma.id: turma for turma in turmas_qs}
                    ids_invalidos = set(turmas_ids) - set(turmas_por_id.keys())

                    if ids_invalidos:
                        raise ValidationError('Uma ou mais turmas selecionadas não são mais válidas. Atualize a página e tente novamente.')

                    for turma_id in set(turmas_ids):
                        InscricaoTurma.objects.create(inscricao=inscricao, turma=turmas_por_id[turma_id])
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
    # Obtém todas as inscrições para administradores
    inscricoes = Inscricao.objects.all().prefetch_related('usuario', 'turmas')
    
    # Estatísticas gerais
    total_inscricoes = inscricoes.count()
    total_vagas = Turma.objects.aggregate(total_vagas=Sum('vagas'))['total_vagas'] or 0
    total_cursos = Curso.objects.count()
    total_turmas = Turma.objects.count()
    
    # Dados para o gráfico de inscrições por curso
    inscricoes_por_curso = []
    for curso in Curso.objects.all():
        num_inscritos = curso.turmas.filter(inscricao__isnull=False).count()
        inscricoes_por_curso.append({
            'curso': curso.nome,
            'total': num_inscritos
        })
    
    # Dados para o gráfico de vagas por curso
    vagas_por_curso = []
    for curso in Curso.objects.all():
        vagas = curso.turmas.aggregate(total_vagas=Sum('vagas'))['total_vagas'] or 0
        vagas_por_curso.append({
            'curso': curso.nome,
            'vagas': vagas
        })
    
    context = {
        'inscricoes': inscricoes,
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
    
    turmas = Turma.objects.filter(curso_id__in=curso_ids, ano_letivo=ano_letivo_atual)
    turmas_data = []

    for turma in turmas:
        vagas_disponiveis = turma.vagas_disponiveis()
        if vagas_disponiveis > 0:
            turmas_data.append({
                'id': turma.id,
                'nome': turma.nome,
                'dia_semana': turma.dia_semana,
                'horario_inicio': turma.horario_inicio.strftime('%H:%M'),
                'horario_fim': turma.horario_fim.strftime('%H:%M'),
                'vagas_disponiveis': vagas_disponiveis,
                'curso_id': turma.curso_id,
                'curso_nome': turma.curso.nome
            })
    
    return JsonResponse({'turmas': turmas_data})


def pagina_inicial(request):
    cursos = Curso.objects.all()
    inscricoes_abertas = getattr(settings, 'INSCRICOES_ABERTAS', False)

    return render(request, 'inscricoes/pagina_inicial.html', {'cursos': cursos, 'inscricoes_abertas': inscricoes_abertas})

