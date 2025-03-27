from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_staff:
                    messages.error(request, 'Você não tem permissão para acessar esta área.')
                    return redirect('login')
                auth_login(request, user)
                messages.success(request, 'Login bem-sucedido!')
                return redirect('inscricoes:pagina_inicial')  # Redirecionar para a página inicial
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, preencha o formulário corretamente.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False  # Garante que o usuário será um usuário comum
            user.set_password(form.cleaned_data['password1'])  # Certifique-se de chamar set_password para criptografar a senha
            user.save()
            messages.success(request, 'Conta criada com sucesso! Agora você pode fazer login.')
            return redirect('accounts:login')
        else:
            print(form.errors)  # Para depuração, verifique se o formulário tem erros
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# Função para deslogar um admin
@login_required
def custom_logout(request):
    logout(request)
    return redirect('logout')

