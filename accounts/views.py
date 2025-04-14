from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def user_login(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)

                if user:
                    if user.is_staff:
                        messages.error(request, 'Você não tem permissão para acessar esta área.')
                        return redirect('accounts:login')
                    auth_login(request, user)
                    messages.success(request, 'Login bem-sucedido!')
                    return redirect('inscricoes:pagina_inicial')
                else:
                    messages.error(request, 'Usuário ou senha inválidos.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        else:
            form = AuthenticationForm()
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {str(e)}')
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    try:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_staff = False
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(request, 'Conta criada com sucesso! Agora você pode fazer login.')
                return redirect('accounts:login')
            else:
                # Verifica erros específicos e mostra mensagens apropriadas
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        else:
            form = CustomUserCreationForm()
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {str(e)}')
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('accounts:login')

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso!')
    return redirect('accounts:login')

