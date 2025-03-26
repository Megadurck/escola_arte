from itertools import count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscricaoForm
from .models import Curso, Inscricao
from django.contrib.auth import logout
from django.db.models import Count
from datetime import datetime


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
    """Retorna os dados do dashboard em formato JSON para o frontend."""
    total_inscricoes = Inscricao.objects.count()
    cursos = Curso.objects.annotate(total_inscricoes=Count('inscricao')).all()

    # Inscri es por curso
    inscricoes_por_curso = [
        {'curso': curso.nome, 'total': curso.total_inscricoes, 'porcentagem': round(curso.total_inscricoes / total_inscricoes * 100, 2) if total_inscricoes > 0 else 0}
        for curso in cursos
    ]

    # Inscri es por data
    data_inscricao = Inscricao.objects.values('data_inscricao').annotate(count=Count('id')).order_by('data_inscricao')

    # Preparar os dados de inscri es por data para o gr fico de linha
    datas = [entry['data_inscricao'].strftime('%Y-%m-%d') for entry in data_inscricao]
    quantidades = [entry['count'] for entry in data_inscricao]

    # Retornar os dados no formato JSON para o frontend
    return JsonResponse({
        'inscricoes_por_curso': inscricoes_por_curso,
        'total_inscricoes': total_inscricoes,
        'data_inscricao': datas,
        'quantidade_inscricao': quantidades,
    })

# Função para painel administrativo
@login_required
def dashboard_view(request):
    return render(request, 'inscricoes/dashboard.html')

# Função para página inicial (protegida por login)
@login_required
def pagina_inicial(request):
    return render(request, 'inscricoes/pagina_inicial.html')
