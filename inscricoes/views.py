from itertools import count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscricaoForm
from .models import Curso, Inscricao
from django.contrib.auth import logout
from django.db.models import Count

# Função para inscrever usuário
@login_required
def inscrever(request):
    if Inscricao.objects.filter(usuario=request.user).exists():
        messages.error(request, 'Você já está inscrito!')
        return redirect('inscricoes:pagina_inicial')
    
    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.usuario = request.user
            inscricao.save()
            form.save_m2m()

            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('inscricoes:inscrever')
    else:
        form = InscricaoForm()

    return render(request, 'inscricoes/inscrever.html', {'form': form})

# Função para exibir dados do dashboard (somente para administradores ou usuários com permissões)
@login_required
def dashboard_data(request):
    total_inscricoes = Inscricao.objects.count()
    cursos = Curso.objects.annotate(total_inscricoes=Count('inscricao')).all()

    inscricoes_por_curso = [
        {
            'curso': curso.nome,
            'total': curso.total_inscricoes,
            'porcentagem': (curso.total_inscricoes / total_inscricoes * 100) if total_inscricoes > 0 else 0
        }
        for curso in cursos
    ]

    return JsonResponse({
        'inscricoes_por_curso': inscricoes_por_curso,
        'total_inscricoes': total_inscricoes
    })

# Função para painel administrativo
@login_required
def dashboard_view(request):
    return render(request, 'inscricoes/dashboard.html')

# Função para página inicial (protegida por login)
@login_required
def pagina_inicial(request):
    return render(request, 'inscricoes/pagina_inicial.html')
