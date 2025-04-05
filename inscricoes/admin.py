from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Inscricao, Curso, Funcionario, Turma, InscricaoTurma
from django.contrib.auth.models import User

class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 1

class InscricaoTurmaInline(admin.TabularInline):
    model = InscricaoTurma
    extra = 1

# Registrar o modelo de Inscrição no admin
@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf', 'telefone_whatsapp', 'data_inscricao']
    search_fields = ['nome_completo', 'cpf']
    list_filter = ['data_inscricao']
    inlines = [InscricaoTurmaInline]
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('usuario', 'nome_completo', 'cpf', 'data_nascimento', 'telefone_whatsapp')
        }),
        ('Endereço', {
            'fields': ('rua', 'bairro', 'numero')
        }),
    )

# Registrar o modelo de Curso no admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'valor', 'vagas_total']
    search_fields = ('nome',)
    inlines = [TurmaInline]
    list_editable = ['vagas_total']

# Registrar o modelo de Turma no admin
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'curso', 'dia_semana', 'horario_inicio', 'horario_fim', 'vagas']
    list_filter = ('curso', 'dia_semana')
    search_fields = ('nome', 'curso__nome')

# Registrar o modelo de Funcionario no admin
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'email', 'telefone']
    search_fields = ('nome', 'email')
    list_filter = ('cargo',)
    filter_horizontal = ('cursos',)

# Personalização do UserAdmin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'superuser_indicator')

    def superuser_indicator(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: green; font-weight: bold;">Superuser</span>')
        return format_html('<span style="color: red;">Usuário Comum</span>')
    
    superuser_indicator.short_description = 'Status do Superuser'

# Registra o modelo User no admin com a personalização
admin.site.unregister(User)  # Desregistra a versão padrão
admin.site.register(User, UserAdmin)  # Registra a versão personalizada


