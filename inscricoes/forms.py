from django import forms
from .models import Inscricao, Curso
from django.core.exceptions import ValidationError
import re
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InscricaoForm(forms.ModelForm):
    
    cursos = forms.ModelMultipleChoiceField(queryset=Curso.objects.all())  # Múltiplos cursos podem ser selecionados

    class Meta:
        model = Inscricao
        fields = ['nome_completo', 'cpf', 'rua', 'bairro', 'numero', 'telefone_whatsapp', 'data_nascimento', 'cursos']

    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Cursos',
        required=True
    )

    # Usando o widget 'date' do HTML5 mas garantindo a conversão correta
    data_nascimento = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],  # Aceita ambos os formatos
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})  # Formato esperado para o HTML5
    )

    def clean_telefone_whatsapp(self):
        telefone = self.cleaned_data.get('telefone_whatsapp')
        # Remove qualquer caractere não numérico
        telefone = re.sub(r'\D', '', telefone)
        return telefone

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        cpf = re.sub(r'\D', '', cpf)  # Remove tudo que não for número
        
        # Verificar se o CPF já existe
        if Inscricao.objects.filter(cpf=cpf).exists():
            raise ValidationError('Este CPF já está cadastrado.')
        
        # Verificar o tamanho do CPF
        if len(cpf) != 11:
            raise ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.")
        
        return cpf

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')

        # Se for uma string, tenta converter
        if isinstance(data_nascimento, str):
            try:
                # Converte a data do formato DD/MM/YYYY para o formato datetime
                data_formatada = datetime.strptime(data_nascimento, '%d/%m/%Y')
                return data_formatada.date()
            except ValueError:
                raise ValidationError("Data inválida. Use o formato DD/MM/YYYY.")
        
        return data_nascimento  # Se já for um objeto de data, retorna diretamente


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
