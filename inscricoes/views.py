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
import time


# Função para inscrever usuário
@login_required
def inscrever(request):
    if Inscricao.objects.filter(usuario=request.user).exists():
        messages.error(request, 'Você já está inscrito!')
        return redirect('inscricoes:pagina_inicial')
    
    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        if form.is_valid():
            cursos_selecionados = form.cleaned_data.get('cursos')

            for curso in cursos_selecionados:
                if curso.inscricoes.count() >= curso.limite_inscricoes:
                    messages.error(request, f'O curso "{curso.nome}" atingiu o limite de inscrições.')
                    return redirect('inscricoes:inscrever')

            inscricao = form.save(commit=False)
            inscricao.usuario = request.user
            inscricao.save()
            form.save_m2m()  # Salva a relação ManyToMany

            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('inscricoes:pagina_inicial')
    else:
        form = InscricaoForm()

    return render(request, 'inscricoes/inscrever.html', {'form': form})





# Função para exibir dados do dashboard (somente para administradores ou usuários com permissões)
@login_required
def dashboard_data(request):
    try:
        # Verificar se o usuário tem permissão para ver o dashboard
        if not request.user.is_staff:
            return JsonResponse({'error': 'Acesso não autorizado'}, status=403)

        # Buscar dados básicos
        total_inscricoes = Inscricao.objects.count()
        
        # Buscar cursos com contagem de inscrições
        cursos = Curso.objects.annotate(
            total_inscricoes=Count('inscricoes')
        ).all()

        # Preparar dados de inscrições por curso
        inscricoes_por_curso = []
        for curso in cursos:
            inscricoes_por_curso.append({
                'curso': curso.nome,
                'total': curso.total_inscricoes,
                'porcentagem': round((curso.total_inscricoes / total_inscricoes * 100) if total_inscricoes > 0 else 0, 2)
            })

        # Buscar e preparar dados de inscrições por data
        data_inscricao = Inscricao.objects.values('data_inscricao').annotate(
            count=Count('id')
        ).order_by('data_inscricao')

        data_inscricao_list = []
        for entry in data_inscricao:
            if entry['data_inscricao']:  # Verificar se a data não é None
                data_inscricao_list.append({
                    'data_inscricao': entry['data_inscricao'].strftime('%Y-%m-%d'),
                    'count': entry['count']
                })

        # Criar resposta com headers CORS
        response = JsonResponse({
            'inscricoes_por_curso': inscricoes_por_curso,
            'total_inscricoes': total_inscricoes,
            'data_inscricao': data_inscricao_list
        })
        
        # Adicionar headers CORS
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        
        return response

    except Exception as e:
        # Log do erro para debug
        print(f"Erro no dashboard_data: {str(e)}")
        response = JsonResponse({
            'error': 'Erro ao processar dados do dashboard',
            'details': str(e)
        }, status=500)
        
        # Adicionar headers CORS mesmo para erros
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        
        return response

# Função para painel administrativo
@login_required
def dashboard_view(request):
    # Adicionar timestamp para forçar recarregamento dos arquivos estáticos
    timestamp = int(time.time())
    return render(request, 'inscricoes/dashboard.html', {'timestamp': timestamp})

# Função para página inicial (protegida por login)
@login_required
def pagina_inicial(request):
    return render(request, 'inscricoes/pagina_inicial.html')
