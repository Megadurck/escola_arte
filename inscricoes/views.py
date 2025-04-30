from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout
from .models import Inscricao, Curso, Funcionario, Turma, InscricaoTurma
from .forms import InscricaoForm, RegistrationForm
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.utils.timezone import now, make_aware

@login_required
def pagina_inicial(request):
    cursos = Curso.objects.all()
    return render(request, 'inscricoes/pagina_inicial.html', {'cursos': cursos})

@login_required
def inscrever(request):
    data_limite = make_aware (datetime(2025, 5, 1))
    hoje = timezone.now() # Mesmo valor usado na outra view
    if now() >= data_limite:
        return HttpResponseForbidden("As inscrições estão encerradas.")
    # Verifica se o usuário já tem uma inscrição
    inscricao_existente = Inscricao.objects.filter(usuario=request.user).exists()
    
    if inscricao_existente:
        messages.warning(request, 'Você já possui uma inscrição!')
        return redirect('inscricoes:pagina_inicial')
        
    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        
        # Processa o campo oculto com os IDs das turmas selecionadas
        turmas_ids = request.POST.get('turmas_selecionadas', '').split(',')
        turmas_ids = [int(id) for id in turmas_ids if id.isdigit()]
        
        # Verifica se pelo menos uma turma foi selecionada
        if not turmas_ids:
            messages.error(request, 'Você deve selecionar pelo menos uma turma para se inscrever.')
            return render(request, 'inscricoes/inscrever.html', {'form': form, 'inscricao_existente': inscricao_existente})
        
        # Atualiza o queryset do campo turmas com as turmas selecionadas
        form.fields['turmas'].queryset = Turma.objects.filter(id__in=turmas_ids)
        
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.usuario = request.user
            inscricao.save()
            
            try:# Cria as relações InscricaoTurma
                for turma_id in set(turmas_ids):
                    turma = Turma.objects.get(id=turma_id)
                    InscricaoTurma.objects.create(inscricao=inscricao, turma=turma)
            except ValidationError as e:
                messages.error(request, f'Erro ao inscrever em uma turma: {e}')
                inscricao.delete()  # desfaz a inscrição criada
                return render(request, 'inscricoes/inscrever.html', {'form': form})

            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('inscricoes:pagina_inicial')
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

@login_required
def get_turmas(request):
    curso_ids = request.GET.get('curso_id', '').split(',')
    curso_ids = [int(id) for id in curso_ids if id.isdigit()]
    
    turmas = Turma.objects.filter(curso_id__in=curso_ids)
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


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Agora você pode fazer login.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def pagina_inicial(request):
    cursos = Curso.objects.all()
    
    # Defina a data limite para o bloqueio das inscrições
    data_limite = make_aware(datetime(2023, 5, 1)) #Ajuste para amanhã ou a data desejada
    hoje = datetime.now()

    return render(request, 'inscricoes/pagina_inicial.html', {'cursos': cursos, 'hoje': hoje, 'data_limite': data_limite})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('accounts:login')

