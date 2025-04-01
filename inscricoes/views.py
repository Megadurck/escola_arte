from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout
from .models import Inscricao, Curso, Funcionario, HorarioCurso
from .forms import InscricaoForm
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def pagina_inicial(request):
    cursos = Curso.objects.all()
    return render(request, 'inscricoes/pagina_inicial.html', {'cursos': cursos})

@login_required
def inscrever(request):
    # Verifica se o usuário já tem uma inscrição
    inscricao_existente = Inscricao.objects.filter(usuario=request.user).exists()
    
    if inscricao_existente:
        messages.warning(request, 'Você já possui uma inscrição!')
        return redirect('inscricoes:pagina_inicial')
        
    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.usuario = request.user
            inscricao.save()
            
            # Salva o curso selecionado
            curso_id = request.POST.get('curso')
            if curso_id:
                curso = Curso.objects.get(id=curso_id)
                inscricao.cursos.add(curso)
            
            # Salva o horário selecionado
            horario_id = request.POST.get('horario')
            if horario_id:
                horario = HorarioCurso.objects.get(id=horario_id)
                inscricao.horarios_selecionados.add(horario)
                # Atualiza o número de vagas disponíveis
                horario.vagas_disponiveis -= 1
                horario.save()
            
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
    inscricoes = Inscricao.objects.all().select_related('usuario', 'curso', 'horario')
    
    # Estatísticas gerais
    total_inscricoes = inscricoes.count()
    total_vagas = HorarioCurso.objects.aggregate(total_vagas=Sum('vagas_disponiveis'))['total_vagas'] or 0
    total_cursos = Curso.objects.count()
    total_horarios = HorarioCurso.objects.count()
    
    # Dados para o gráfico de inscrições por curso
    inscricoes_por_curso = []
    for curso in Curso.objects.all():
        num_inscritos = curso.inscricoes.count()
        inscricoes_por_curso.append({
            'curso': curso.nome,
            'total': num_inscritos
        })
    
    # Dados para o gráfico de vagas por curso
    vagas_por_curso = []
    for curso in Curso.objects.all():
        vagas = curso.horarios.aggregate(total_vagas=Sum('vagas_disponiveis'))['total_vagas'] or 0
        vagas_por_curso.append({
            'curso': curso.nome,
            'vagas': vagas
        })
    
    context = {
        'inscricoes': inscricoes,
        'total_inscricoes': total_inscricoes,
        'total_vagas': total_vagas,
        'total_cursos': total_cursos,
        'total_horarios': total_horarios,
        'inscricoes_por_curso': inscricoes_por_curso,
        'vagas_por_curso': vagas_por_curso,
    }
    return render(request, 'inscricoes/dashboard.html', context)

@login_required
def get_horarios_curso(request, curso_id):
    try:
        curso = Curso.objects.get(id=curso_id)
        horarios = HorarioCurso.objects.filter(
            curso=curso,
            vagas_disponiveis__gt=0
        ).order_by('dia_semana', 'hora_inicio')
        
        horarios_data = []
        for horario in horarios:
            horarios_data.append({
                'id': horario.id,
                'texto': f"{horario.get_dia_semana_display()} - {horario.hora_inicio.strftime('%H:%M')} às {horario.hora_fim.strftime('%H:%M')} ({horario.vagas_disponiveis} vagas)"
            })
        
        return JsonResponse({'horarios': horarios_data})
    except Curso.DoesNotExist:
        return JsonResponse({'error': 'Curso não encontrado'}, status=404)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('inscricoes:pagina_inicial')
