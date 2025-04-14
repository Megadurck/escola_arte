from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Sua senha deve conter pelo menos 8 caracteres, incluindo letras e números.'
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Digite a mesma senha para confirmar.'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome de usuário'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu sobrenome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu e-mail'}),
        }
        help_texts = {
            'username': 'Obrigatório. 150 caracteres ou menos. Apenas letras, números e @/./+/-/_',
            'email': 'Digite um endereço de e-mail válido.',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('O nome de usuário é obrigatório.')
        if len(username) < 3:
            raise forms.ValidationError('O nome de usuário deve ter pelo menos 3 caracteres.')
        if not re.match(r'^[\w.@+-]+$', username):
            raise forms.ValidationError('O nome de usuário pode conter apenas letras, números e @/./+/-/_')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('O e-mail é obrigatório.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado em nossa base. Por favor, use outro e-mail ou recupere sua senha.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('O nome é obrigatório.')
        if len(first_name) < 2:
            raise forms.ValidationError('O nome deve ter pelo menos 2 caracteres.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('O sobrenome é obrigatório.')
        if len(last_name) < 2:
            raise forms.ValidationError('O sobrenome deve ter pelo menos 2 caracteres.')
        return last_name

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise forms.ValidationError('A senha é obrigatória.')
        try:
            validate_password(password1)
        except ValidationError as error:
            self.add_error('password1', error)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'As senhas não coincidem. Por favor, digite a mesma senha nos dois campos.')
        
        return cleaned_data
