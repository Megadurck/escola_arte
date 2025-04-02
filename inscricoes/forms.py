from django import forms
from .models import Inscricao, Curso, HorarioCurso
from django.core.exceptions import ValidationError
import re
import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InscricaoForm(forms.ModelForm):
    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        label='Cursos',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    horarios_selecionados = forms.ModelMultipleChoiceField(
        queryset=HorarioCurso.objects.all(),
        label='Horários',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Inscricao
        fields = ['nome_completo', 'cpf', 'rua', 'bairro', 'numero', 'telefone_whatsapp', 'data_nascimento', 'cursos', 'horarios_selecionados']
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
        self.fields['horarios_selecionados'].widget.attrs['disabled'] = True

    def clean_horarios_selecionados(self):
        horarios = self.cleaned_data.get('horarios_selecionados', [])
        cursos_selecionados = self.cleaned_data.get('cursos', [])
        
        # Verifica se os horários pertencem aos cursos selecionados
        for horario in horarios:
            if horario.curso not in cursos_selecionados:
                raise forms.ValidationError(f'O horário {horario} não pertence aos cursos selecionados.')
            
            # Verifica se há vagas disponíveis
            if horario.vagas_disponiveis <= 0:
                raise forms.ValidationError(f'Não há mais vagas disponíveis para o horário {horario}.')
        
        return horarios

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
            # Primeiro salvamos a inscrição
            inscricao.save()
            
            # Agora salvamos os relacionamentos
            self.save_m2m()
            inscricao.cursos.set(self.cleaned_data['cursos'])
            inscricao.horarios_selecionados.set(self.cleaned_data['horarios_selecionados'])
            
        return inscricao


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
