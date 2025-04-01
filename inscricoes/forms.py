from django import forms
from .models import Inscricao, Curso, HorarioCurso
from django.core.exceptions import ValidationError
import re
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InscricaoForm(forms.ModelForm):
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all(),
        label='Curso',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'curso-select'})
    )
    
    horario = forms.ModelChoiceField(
        queryset=HorarioCurso.objects.none(),  # Inicializa vazio
        label='Horário',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'horario-select'})
    )
    
    class Meta:
        model = Inscricao
        fields = ['nome_completo', 'cpf', 'rua', 'bairro', 'numero', 'telefone_whatsapp', 'data_nascimento', 'curso', 'horario']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Desabilita o campo de horário inicialmente
        self.fields['horario'].widget.attrs['disabled'] = True

    def clean_telefone_whatsapp(self):
        telefone = self.cleaned_data.get('telefone_whatsapp', '')
        # Remove todos os caracteres não numéricos
        telefone = ''.join(filter(str.isdigit, telefone))
        return telefone

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        # Remove todos os caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se o CPF já está cadastrado
        if Inscricao.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
            
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')
            
        return cpf

    def save(self, commit=True):
        inscricao = super().save(commit=False)
        if commit:
            inscricao.save()
            # Adiciona o curso e horário selecionados
            inscricao.cursos.add(self.cleaned_data['curso'])
            # Atualiza as vagas disponíveis
            horario = self.cleaned_data['horario']
            horario.vagas_disponiveis -= 1
            horario.save()
        return inscricao


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
