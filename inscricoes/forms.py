from django import forms
from .models import Inscricao, Curso, Turma
from django.core.exceptions import ValidationError
import re
import datetime
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class InscricaoForm(forms.ModelForm):
    cpf = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    data_nascimento = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'dd/mm/aaaa',
                'inputmode': 'numeric',
                'maxlength': '10',
                'autocomplete': 'bday',
            }
        ),
    )

    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        label='Cursos',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    turmas = forms.ModelMultipleChoiceField(
        queryset=Turma.objects.none(),  # Será preenchido via JavaScript
        label='Turmas',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Inscricao
        fields = ['nome_completo', 'cpf', 'rua', 'bairro', 'numero', 'telefone_whatsapp', 'data_nascimento']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'rua': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone_whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ano_letivo_atual = int(getattr(settings, 'ANO_LETIVO_ATUAL', datetime.date.today().year))
        # Desabilita o campo de turmas inicialmente
        self.fields['turmas'].widget.attrs['disabled'] = True

    def clean_turmas(self):
        turmas = self.cleaned_data.get('turmas', [])
        cursos_selecionados = self.cleaned_data.get('cursos', [])
        
        # Verifica se as turmas pertencem aos cursos selecionados
        for turma in turmas:
            if turma.curso not in cursos_selecionados:
                raise forms.ValidationError(f'A turma {turma} não pertence aos cursos selecionados.')

            if turma.ano_letivo != self.ano_letivo_atual:
                raise forms.ValidationError('As turmas selecionadas não pertencem ao ano letivo ativo.')
            
            # Verifica se há vagas disponíveis usando o método correto
            vagas_disponiveis = turma.vagas_disponiveis()
            if vagas_disponiveis <= 0:
                raise forms.ValidationError(f'Não há mais vagas disponíveis para a turma {turma}.')
        
        return turmas

    def clean_telefone_whatsapp(self):
        telefone = self.cleaned_data.get('telefone_whatsapp', '')
        # Remove todos os caracteres não numéricos
        telefone = ''.join(filter(str.isdigit, telefone))
        return telefone

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        # Remove todos os caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se o CPF já está cadastrado no ano letivo atual
        if Inscricao.objects.filter(cpf=cpf, ano_letivo=self.ano_letivo_atual).exists():
            raise forms.ValidationError('Este CPF já está cadastrado para o ano letivo atual.')
            
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')
            
        return cpf

    def save(self, commit=True):
        inscricao = super().save(commit=False)
        inscricao.ano_letivo = self.ano_letivo_atual
        if commit:
            inscricao.save()
        return inscricao


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
